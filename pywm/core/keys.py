from Xlib import X, XK
from pywm.x11.connection import DISPLAY, ROOT
from pywm.core.actions import spawn_application
from pywm.core import manager

MOD = X.Mod4Mask  # Super key
# MOD = X.ControlMask
RETURN = XK.string_to_keysym("Return")
C = XK.string_to_keysym("c")
W = XK.string_to_keysym("w")
Q = XK.string_to_keysym("q")

# PRESSED = set()

def init_keybindings():
    grab_key(RETURN, MOD)
    grab_key(C, MOD)
    grab_key(W, MOD)
    grab_key(Q, MOD)


def grab_key(keysym, modmask):
    keycode = DISPLAY.keysym_to_keycode(keysym)

    extra_mods = [0, X.LockMask, X.Mod2Mask, X.LockMask | X.Mod2Mask]

    for em in extra_mods:
        ROOT.grab_key(
            keycode,
            modmask | em,
            False,  # deliver to WM even when a client is focused
            X.GrabModeAsync,
            X.GrabModeAsync
        )

    DISPLAY.sync()


def handle_key(event):
    keysym = DISPLAY.keycode_to_keysym(event.detail, 0)

    if not (event.state & MOD):
        return

    # keyname = XK.keysym_to_string(keysym)

    if keysym == RETURN:
        spawn_application("alacritty")
    elif keysym == Q:
        print("Super+Q pressed")
    elif keysym == C:
        manager.close_window()
    elif keysym == W:
        spawn_application("thunar")
