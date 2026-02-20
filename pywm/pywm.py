from Xlib import X
from Xlib.error import BadAccess
from pywm.x11.connection import ROOT, DISPLAY
from pywm.core import manager
from pywm.core.keys import init_keybindings, handle_key
from pywm.core.process import setup_signal_handlers


def run():
    # NOTE: move this
    init_keybindings()
    setup_signal_handlers()
    manager.prepare_manager()

    try:
        ROOT.change_attributes(event_mask=(
            X.SubstructureRedirectMask |
            X.SubstructureNotifyMask   |
            X.ButtonPressMask          |
            X.PointerMotionMask        |
            X.EnterWindowMask          |
            X.LeaveWindowMask          |
            X.KeyPressMask
        ))
        DISPLAY.sync()
    except BadAccess:
        raise SystemExit("Another window manager already owns SubstructureRedirect on this DISPLAY.")

    while True:
        event = DISPLAY.next_event()

        if event.type == X.MapRequest:
            # print("MAP REQUEST")
            manager.handle_map_request(event)
        elif event.type == X.EnterNotify:
            # print("ENTER NOTIFY")
            manager.handle_enter_notify(event)
        elif event.type == X.LeaveNotify:
            pass
            # print("LEAVE")
        elif event.type == X.KeyPress:
            handle_key(event)
            pass
        elif event.type == X.KeyRelease:
            pass
            # print("RELEASE")
            # handle_key(event)
        elif event.type == X.DestroyNotify:
            # print("DESTORY")
            manager.handle_destroy_notify(event)


if __name__=="__main__":
    run()
