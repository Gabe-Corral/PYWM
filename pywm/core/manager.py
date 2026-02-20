from Xlib import X
from Xlib import X, protocol
from Xlib.error import BadWindow

from pywm.x11.connection import ROOT, DISPLAY, SCREEN
from pywm.ui import theme
from pywm.core.window import Client, Frame
from pywm.core.layout.tile import apply_tiling_layout
from pywm.x11.atoms import WM_DELETE_WINDOW, WM_PROTOCOLS
from pywm.ui import statusbar


CLIENTS = {}
FRAMES = {}
FOCUSED_FRAME = None
DESTROY_FRAME = None

def prepare_manager():
    statusbar.create_bar()
    statusbar.draw("PYWM")


def apply_layout():
    # NOTE: fix the ugly args for screen geometry
    apply_tiling_layout(CLIENTS)
    DISPLAY.sync()


def get_child_of_frame(frame):
    tree = frame.query_tree()
    if tree.children:
        return tree.children[0]
    return None


def unfocus():
    ROOT.set_input_focus(
        X.RevertToPointerRoot,
        X.CurrentTime
    )
    DISPLAY.sync()


def focus(window):
    try:
        if window.get_attributes().map_state != X.IsViewable:
            return
        window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
        statusbar.draw(get_window_name(window))
        DISPLAY.flush()
    except BadWindow:
        return
    # DISPLAY.sync()


def get_window_name(window):
    NET_WM_NAME = DISPLAY.intern_atom('_NET_WM_NAME')
    UTF8_STRING = DISPLAY.intern_atom('UTF8_STRING')

    prop = window.get_full_property(NET_WM_NAME, UTF8_STRING)
    if prop and prop.value:
        try:
            return prop.value.decode('utf-8', errors='replace')
        except Exception:
            return str(prop.value)

    WM_NAME = DISPLAY.intern_atom('WM_NAME')
    prop = window.get_full_property(WM_NAME, X.AnyPropertyType)
    if prop and prop.value:
        if isinstance(prop.value, bytes):
            return prop.value.decode('latin1', errors='replace')
        return str(prop.value)

    return None


def manage_client(client_window):
    # NOTE: this needs to change
    global FOCUSED_FRAME

    attrs = client_window.get_attributes()
    if attrs.override_redirect:
        client_window.map()
        DISPLAY.sync()
        return

    geometry = client_window.get_geometry()

    frame_window = ROOT.create_window(
        geometry.x, geometry.y,
        geometry.width, geometry.height,
        theme.BORDER_WIDTH,
        DISPLAY.screen().root_depth,
        X.InputOutput,
        X.CopyFromParent,
        override_redirect=True,
        background_pixel=DISPLAY.screen().black_pixel,
        border_pixel=theme.COLOR_FOCUSED,
        event_mask=(X.EnterWindowMask | X.ButtonPressMask)
    )

    client_window.reparent(frame_window, 0, 0)
    frame_window.map()
    client_window.map()
    DISPLAY.sync()

    client = Client(client_window)
    frame = Frame(frame_window, client)
    client.frame = frame
    frame.client = client

    # NOTE: this needs to change
    # FOCUSED_FRAME = frame

    CLIENTS[client_window.id] = client
    FRAMES[frame_window.id] = frame

    apply_layout()

    return client


def handle_map_request(event):
    window = event.window
    window.configure(x=0, y=0, width=500, height=500, border_width=2)
    window.map()
    DISPLAY.sync()
    manage_client(window)


def handle_enter_notify(event):
    global FOCUSED_FRAME

    if event.detail == X.NotifyInferior:
        return

    frame = FRAMES.get(event.window.id)
    if frame:
        FOCUSED_FRAME = frame
        focus(frame.client.window)


def close_window():
    global FOCUSED_FRAME, DESTROY_FRAME
    DESTROY_FRAME = FOCUSED_FRAME

    if not DESTROY_FRAME:
        return

    client = DESTROY_FRAME.client
    if not client:
        return

    w = client.window

    try:
        protocols = w.get_wm_protocols()
    except BadWindow:
        # already gone
        return

    try:
        if protocols and WM_DELETE_WINDOW in protocols:
            msg = protocol.event.ClientMessage(
                window=w,
                client_type=WM_PROTOCOLS,
                data=(32, [WM_DELETE_WINDOW, X.CurrentTime, 0, 0, 0])
            )
            w.send_event(msg, event_mask=X.NoEventMask)
        else:
            w.destroy()

        DISPLAY.flush()
    except BadWindow:
        # window disappeared between calls
        return


def handle_destroy_notify(event):
    global DESTROY_FRAME

    if not DESTROY_FRAME:
        statusbar.draw("PYWM")
        return

    frame = DESTROY_FRAME
    DESTROY_FRAME = None

    frame.window.destroy()

    frame_id = frame.window.id
    client_id = frame.client.window.id

    # NOTE: add some protection here
    FRAMES.pop(frame_id, None)
    CLIENTS.pop(client_id, None)

    if len(FRAMES):
        apply_layout()
