from Xlib import X
from Xlib import X, protocol
from Xlib.error import BadWindow

from pywm.x11.connection import ROOT, DISPLAY, SCREEN
from pywm.ui import theme
from pywm.core.window import Client, Frame
from pywm.core.layout import tile
from pywm.x11.atoms import WM_DELETE_WINDOW, WM_PROTOCOLS, NET_WM_NAME, UTF8_STRING
from pywm.ui.statusbar import StatusBar
from pywm.core.tags import Tags


class WindowManager:
    def __init__(self):
        self.clients = {}
        self.frames = {}
        self.focused_frame = None
        self.destroy_frame = None
        self.tags = Tags()
        self.statusbar = None

    def prepare_manager(self):
        sw = SCREEN.width_in_pixels
        sh = SCREEN.height_in_pixels

        self.statusbar = StatusBar(
            0,
            sh - theme.BAR_HEIGHT,
            sw,
            theme.BAR_HEIGHT,
            self.tags,
        )

        self.statusbar.draw("PYWM")

    def apply_layout(self):
        visible_clients = {}

        for id, c in self.clients.items():
            if self.tags.is_visible(c):
                visible_clients[id] = c
                c.frame.window.map()
            else:
                c.frame.window.unmap()

        tile.apply_tiling_layout(visible_clients, self.tags)
        DISPLAY.sync()

    def get_child_of_frame(self, frame):
        tree = frame.query_tree()
        if tree.children:
            return tree.children[0]
        return None

    def unfocus(self):
        ROOT.set_input_focus(
            X.RevertToPointerRoot,
            X.CurrentTime
        )
        DISPLAY.sync()

    def focus(self, window):
        try:
            if window.get_attributes().map_state != X.IsViewable:
                return
            window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
            if self.statusbar:
                self.statusbar.draw(self.get_window_name(window))
            DISPLAY.flush()
        except BadWindow:
            return

    def get_window_name(self, window):
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

    def manage_client(self, client_window):
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

        client = Client(client_window, tags=self.tags.current_tag)
        frame = Frame(frame_window, client)
        client.frame = frame  # type: ignore[attr-defined]
        frame.client = client

        self.clients[client_window.id] = client
        self.frames[frame_window.id] = frame

        return client

    def handle_map_request(self, event):
        window = event.window
        window.configure(x=0, y=0, width=500, height=500, border_width=2)
        window.map()
        DISPLAY.sync()
        self.manage_client(window)
        self.apply_layout()

    def handle_enter_notify(self, event):
        if event.detail == X.NotifyInferior:
            return

        frame = self.frames.get(event.window.id)
        if frame:
            self.focused_frame = frame
            self.focus(frame.client.window)

    def close_window(self):
        self.destroy_frame = self.focused_frame

        if not self.destroy_frame:
            return

        client = self.destroy_frame.client
        if not client:
            return

        w = client.window

        try:
            protocols = w.get_wm_protocols()
        except BadWindow:
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
            return

    def handle_destroy_notify(self, event):
        if not self.destroy_frame:
            if self.statusbar:
                self.statusbar.draw("PYWM")
            return

        frame = self.destroy_frame
        self.destroy_frame = None

        frame.window.destroy()

        frame_id = frame.window.id
        client_id = frame.client.window.id

        self.frames.pop(frame_id, None)
        self.clients.pop(client_id, None)

        if len(self.frames):
            self.apply_layout()

    def handle_button_press(self, event):
        tag = None
        if self.statusbar:
            tag = self.statusbar.check_tag_pressed(event)

        if tag:
            self.tags.set_tag(tag)
            if self.statusbar:
                self.statusbar.draw("PYWM")
            self.apply_layout()

    def resize_left(self):
        self.tags.set_master_ratio(self.tags.get_master_ratio() - 0.05)

        if len(self.frames) > 1:
            self.apply_layout()

    def resize_right(self):
        self.tags.set_master_ratio(self.tags.get_master_ratio() + 0.05)

        if len(self.frames) > 1:
            self.apply_layout()
