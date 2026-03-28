from Xlib import X
from Xlib import X, protocol
from Xlib.error import BadWindow
from Xlib.ext import randr

from pywm.x11.connection import ROOT, DISPLAY, SCREEN
from pywm.ui.theme import theme
from pywm.core.window import Client, Frame
from pywm.core.layout import tile
from pywm.x11.atoms import (
    WM_DELETE_WINDOW,
    WM_PROTOCOLS,
    NET_WM_NAME,
    UTF8_STRING,
    WM_NAME,
)
from pywm.ui.status_bar import StatusBar
from pywm.core.monitor import Monitor
from pywm.core.tags import Tags
from pywm.core.widgets import ClockWidget, CPUWidget, MemoryWidget


class WindowManager:
    def __init__(self):
        self.clients = {}
        self.frames = {}
        self.focused_frame = None
        self.tags = Tags()
        self.monitors = []
        self.current_monitor = None

    def prepare_manager(self):
        resources = randr.get_screen_resources(ROOT)
        self.monitors = []

        randr.select_input(
            ROOT,
            randr.RRScreenChangeNotifyMask        )

        for output in resources.outputs:
            output_info = randr.get_output_info(ROOT, output, X.CurrentTime)

            # Skip disconnected outputs
            if output_info.crtc == 0:
                continue

            crtc = randr.get_crtc_info(ROOT, output_info.crtc, X.CurrentTime)

            x = crtc.x
            y = crtc.y
            width = crtc.width
            height = crtc.height

            tags = Tags()

            monitor = Monitor(x, y, width, height, tags)

            widgets = [CPUWidget(), MemoryWidget(), ClockWidget()]

            monitor.statusbar = StatusBar(
                monitor.x,
                monitor.y + monitor.height - theme.bar_height,
                monitor.width,
                theme.bar_height,
                monitor.tags,
                widgets
            )

            monitor.statusbar.draw("PYWM")

            self.monitors.append(monitor)

        if not self.monitors:
            sw = SCREEN.width_in_pixels
            sh = SCREEN.height_in_pixels

            monitor = Monitor(0, 0, sw, sh, Tags())

            monitor.statusbar = StatusBar(
                0,
                sh - theme.bar_height,
                sw,
                theme.bar_height,
                monitor.tags,
            )

            monitor.statusbar.draw("PYWM")

            self.monitors = [monitor]

        self.current_monitor = self.monitors[0]

    def apply_layout(self):
        # NOTE: pass monitor and apply only to specific monitor.
        for monitor in self.monitors:
            visible_clients = {}

            for id, c in self.clients.items():
                if getattr(c, "monitor", None) != monitor:
                    continue

                if monitor.tags.is_visible(c):
                    visible_clients[id] = c
                    c.frame.window.map()
                else:
                    c.frame.window.unmap()

            tile.apply_tiling_layout(visible_clients, monitor)

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
            monitor = self.current_monitor
            if monitor and monitor.statusbar:
                monitor.statusbar.draw(self.get_window_name(window))
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

        prop = window.get_full_property(WM_NAME, X.AnyPropertyType)
        if prop and prop.value:
            if isinstance(prop.value, bytes):
                return prop.value.decode('latin1', errors='replace')
            return str(prop.value)

        return None

    def manage_client(self, client_window):
        if client_window.id in self.clients:
            return

        client_window.change_attributes(
            event_mask=X.SubstructureNotifyMask
        )

        attrs = client_window.get_attributes()
        if attrs.override_redirect:
            client_window.map()
            return

        geometry = client_window.get_geometry()

        cx = geometry.x + geometry.width // 2
        cy = geometry.y + geometry.height // 2

        monitor = self.get_monitor_for_point(cx, cy)

        frame_window = ROOT.create_window(
            geometry.x, geometry.y,
            geometry.width, geometry.height,
            theme.border_width,
            DISPLAY.screen().root_depth,
            X.InputOutput,
            X.CopyFromParent,
            override_redirect=True,
            background_pixel=DISPLAY.screen().black_pixel,
            border_pixel=theme.color_focused,
            event_mask=(X.EnterWindowMask | X.ButtonPressMask | X.SubstructureNotifyMask)
        )

        client_window.reparent(frame_window, 0, 0)
        frame_window.map()
        client_window.map()
        DISPLAY.sync()

        client = Client(client_window, tags=monitor.tags.current_tag)
        frame = Frame(frame_window, client)
        client.frame = frame  # type: ignore[attr-defined]
        frame.client = client

        client.monitor = monitor  # type: ignore[attr-defined]

        self.clients[client_window.id] = client
        self.frames[frame_window.id] = frame

        return client

    def handle_map_request(self, event):
        # NOTE: potential errors here
        window = event.window
        self.manage_client(window)
        self.apply_layout()

    def handle_enter_notify(self, event):
        if event.detail == X.NotifyInferior:
            return

        frame = self.frames.get(event.window.id)
        if frame:
            self.focused_frame = frame
            monitor = getattr(frame.client, "monitor", None)
            if monitor:
                self.current_monitor = monitor
                monitor.focused_client = frame.client
            self.focus(frame.client.window)

    def close_window(self):
        frame = self.focused_frame
        if not frame:
            return

        client = frame.client
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
                    data=(32, [WM_DELETE_WINDOW, X.CurrentTime, 0, 0, 0]),
                )
                w.send_event(msg, event_mask=X.NoEventMask)
            else:
                w.destroy()

            DISPLAY.flush()
        except BadWindow:
            return

    def handle_destroy_notify(self, event):
        window_id = event.window.id
        client = self.clients.pop(window_id, None)
        if not client:
            return

        frame = client.frame
        monitor = client.monitor

        self.frames.pop(frame.window.id)

        frame.window.destroy()

        if monitor.focused_client == client:
            monitor.focused_client = None

        if len(self.frames):
            self.apply_layout()

    def handle_button_press(self, event):
        tag = None
        for monitor in self.monitors:
            if monitor.statusbar:
                tag = monitor.statusbar.check_tag_pressed(event)
                if tag:
                    self.current_monitor = monitor
                    break

        if tag:
            self.current_monitor.tags.set_tag(tag)
            if self.current_monitor.statusbar:
                self.current_monitor.statusbar.draw("PYWM")
            self.apply_layout()

    def should_resize_frames(self):
        # NOTE: this probably isn't ideal
        # should consider reimplementing client/frames and monitor class
        # in a way that will make this sencerios easier and more readable
        client_count = 0
        for c in self.clients.values():
            client_tag = c.tags
            monitor_tag = self.current_monitor.tags.current_tag

            if client_tag == monitor_tag:
                client_count += 1

        if client_count > 1:
            return True

        return False

    def resize_left(self):
        if not self.should_resize_frames():
            return

        tags = self.current_monitor.tags
        tags.set_master_ratio(tags.get_master_ratio() - 0.05)

        if len(self.frames) > 1:
            self.apply_layout()

    def resize_right(self):
        if not self.should_resize_frames():
            return

        tags = self.current_monitor.tags
        tags.set_master_ratio(tags.get_master_ratio() + 0.05)

        if len(self.frames) > 1:
            self.apply_layout()

    def get_monitor_for_point(self, x, y):
        for m in self.monitors:
            if m.contains(x, y):
                return m
        return self.current_monitor

    def handle_unmap_notify(self, event):
        print("unmap")

    def move_stack_left(self):
        monitor = self.current_monitor
        # if len(monitor.frames) < 1:
        #     return

        if not monitor or not monitor.focused_client:
            return

        focused = monitor.focused_client

        ordered = list(self.clients.items())
        indices = [
            i for i, (cid, c) in enumerate(ordered)
            if getattr(c, "monitor", None) == monitor
            and monitor.tags.is_visible(c)
        ]

        visible_clients = [ordered[i][1] for i in indices]

        if focused not in visible_clients:
            return

        idx = visible_clients.index(focused)

        if idx <= 0:
            # Already far left, move to end
            client = visible_clients.pop(idx)
            visible_clients.append(client)
        else:
            # Swap with previous
            visible_clients[idx - 1], visible_clients[idx] = (
                visible_clients[idx],
                visible_clients[idx - 1],
            )

        # Rebuild ordered list preserving non-visible positions
        for pos, client in zip(indices, visible_clients):
            ordered[pos] = (client.window.id, client)

        # Rebuild clients dict with new order
        self.clients = {cid: c for cid, c in ordered}

        self.apply_layout()

    def move_stack_right(self):
        monitor = self.current_monitor
        # if len(monitor.frames) < 1:
        #     return

        if not monitor or not monitor.focused_client:
            return

        focused = monitor.focused_client

        ordered = list(self.clients.items())
        indices = [
            i for i, (cid, c) in enumerate(ordered)
            if getattr(c, "monitor", None) == monitor
            and monitor.tags.is_visible(c)
        ]

        visible_clients = [ordered[i][1] for i in indices]

        if focused not in visible_clients:
            return

        idx = visible_clients.index(focused)

        if idx >= len(visible_clients) - 1:
            # Already far right, move to front
            client = visible_clients.pop(idx)
            visible_clients.insert(0, client)
        else:
            # Swap with next
            visible_clients[idx], visible_clients[idx + 1] = (
                visible_clients[idx + 1],
                visible_clients[idx],
            )

        for pos, client in zip(indices, visible_clients):
            ordered[pos] = (client.window.id, client)

        self.clients = {cid: c for cid, c in ordered}

        self.apply_layout()

    def handle_tick(self):
        for monitor in self.monitors:
            widgets = monitor.statusbar.widgets
            for widegt in widgets:
                widegt.should_update()
                # widegt.update()

            monitor.statusbar.draw()

    def handle_screen_change(self):
        resources = randr.get_screen_resources(ROOT)

        new_geometries = []

        for output in resources.outputs:
            output_info = randr.get_output_info(ROOT, output, X.CurrentTime)

            if output_info.crtc == 0:
                continue

            crtc = randr.get_crtc_info(ROOT, output_info.crtc, X.CurrentTime)
            new_geometries.append((crtc.x, crtc.y, crtc.width, crtc.height))

        if not new_geometries:
            return

        if len(new_geometries) != len(self.monitors):
            self.prepare_manager()
            self.apply_layout()
            return

        for monitor, (x, y, width, height) in zip(self.monitors, new_geometries):
            monitor.x = x
            monitor.y = y
            monitor.width = width
            monitor.height = height

            if monitor.statusbar and monitor.statusbar.window:
                monitor.statusbar.window.configure(
                    x=monitor.x,
                    y=monitor.y + monitor.height - theme.bar_height,
                    width=monitor.width,
                    height=theme.bar_height,
                )

        self.apply_layout()
