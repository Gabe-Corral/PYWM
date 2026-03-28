from Xlib import display


DISPLAY = display.Display()
SCREEN = DISPLAY.screen()
ROOT = SCREEN.root


def sync():
    DISPLAY.sync()


def alloc_color(name):
    return SCREEN.default_colormap.alloc_named_color(name).pixel
