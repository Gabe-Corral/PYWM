from Xlib import X
from Xlib.error import BadAccess

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pywm.x11.connection import ROOT, DISPLAY
from pywm.core.manager import WindowManager
from pywm.core.keys import KeyHandler
from pywm.core.process import setup_signal_handlers
from pywm.core import cursor
from pywm.ui import statusbar


def main():
    setup_signal_handlers()
    window_manager = WindowManager()
    key_handler = KeyHandler(window_manager)
    key_handler.init_keybindings()
    window_manager.prepare_manager()

    try:
        ROOT.change_attributes(
            event_mask=(
                X.SubstructureRedirectMask |
                X.SubstructureNotifyMask   |
                X.ButtonPressMask          |
                X.PointerMotionMask        |
                X.EnterWindowMask          |
                X.LeaveWindowMask          |
                X.KeyPressMask
            ),
            cursor=cursor.CURSOR
        )
        DISPLAY.sync()
    except BadAccess:
        raise SystemExit("Another window manager already owns SubstructureRedirect on this DISPLAY.")

    while True:
        event = DISPLAY.next_event()

        if event.type == X.MapRequest:
            # print("MAP REQUEST")
            window_manager.handle_map_request(event)
        elif event.type == X.EnterNotify:
            # print("ENTER NOTIFY")
            window_manager.handle_enter_notify(event)
        elif event.type == X.LeaveNotify:
            pass
            # print("LEAVE")
        elif event.type == X.KeyPress:
            key_handler.handle_key(event)
        elif event.type == X.KeyRelease:
            pass
            # print("RELEASE")
            # handle_key(event)
        elif event.type == X.DestroyNotify:
            # print("DESTORY")
            window_manager.handle_destroy_notify(event)
        elif event.type == X.ButtonPress:
            window_manager.handle_button_press(event)
        elif event.type == X.UnmapNotify:
            window_manager.handle_unmap_notify(event)


if __name__=="__main__":
    main()
