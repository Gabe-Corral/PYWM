from Xlib import X
from Xlib.error import BadAccess

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pywm.x11.connection import ROOT, DISPLAY
from pywm.core.window_manager import WindowManager
from pywm.core.process import setup_signal_handlers
from pywm.core import cursor

def configure_root():
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


def main():
    setup_signal_handlers()
    window_manager = WindowManager()
    # NOTE: I don't like this being here
    # find a better way to initialize
    window_manager.prepare_manager()
    configure_root()

    last_tick = time.time()
    while True:
        event = DISPLAY.next_event()

        handler = window_manager.event_handlers.get(event.type)
        if handler:
            handler(event)

        # NOTE: figure out why we have to do this and do it correctly
        # NOTE: also this needs to skip on startup
        if event.__class__.__name__ == "ScreenChangeNotify":
            window_manager.handle_screen_change()

        now = time.time()
        if now - last_tick >= 1.0:
            window_manager.handle_tick()
            last_tick = now


if __name__=="__main__":
    main()
