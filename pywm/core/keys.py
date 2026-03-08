from Xlib import X, XK
from pywm.x11.connection import DISPLAY, ROOT
from pywm.core.actions import spawn_application


class KeyHandler:
    MOD = X.Mod4Mask  # Super key

    def __init__(self, window_manager):
        self.wm = window_manager

        self.RETURN = XK.string_to_keysym("Return")
        self.C = XK.string_to_keysym("c")
        self.W = XK.string_to_keysym("w")
        self.Q = XK.string_to_keysym("q")
        self.H = XK.string_to_keysym("h")
        self.L = XK.string_to_keysym("l")
        self.J = XK.string_to_keysym("j")
        self.K = XK.string_to_keysym("k")

    def init_keybindings(self):
        self._grab_key(self.RETURN, self.MOD)
        self._grab_key(self.C, self.MOD)
        self._grab_key(self.W, self.MOD)
        self._grab_key(self.Q, self.MOD)
        self._grab_key(self.H, self.MOD)
        self._grab_key(self.L, self.MOD)
        self._grab_key(self.J, self.MOD)
        self._grab_key(self.K, self.MOD)

    def _grab_key(self, keysym, modmask):
        keycode = DISPLAY.keysym_to_keycode(keysym)

        extra_mods = [0, X.LockMask, X.Mod2Mask, X.LockMask | X.Mod2Mask]

        for em in extra_mods:
            ROOT.grab_key(
                keycode,
                modmask | em,
                False,
                X.GrabModeAsync,
                X.GrabModeAsync,
            )

        DISPLAY.sync()

    def handle_key(self, event):
        keysym = DISPLAY.keycode_to_keysym(event.detail, 0)

        if not (event.state & self.MOD):
            return

        if keysym == self.RETURN:
            spawn_application("alacritty")
        elif keysym == self.Q:
            print("Super+Q pressed")
        elif keysym == self.C:
            self.wm.close_window()
        elif keysym == self.W:
            spawn_application("thunar")
        elif keysym == self.H:
            self.wm.resize_left()
        elif keysym == self.L:
            self.wm.resize_right()
        elif keysym == self.J:
            self.wm.move_stack_left()
        elif keysym == self.K:
            self.wm.move_stack_right()
