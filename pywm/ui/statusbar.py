from Xlib import X
from pywm.x11.connection import DISPLAY, ROOT, SCREEN
from pywm.ui import theme

BAR = None


def create_bar():
    global BAR
    sw = SCREEN.width_in_pixels
    sh = SCREEN.height_in_pixels

    BAR = ROOT.create_window(
        0, sh - theme.BAR_HEIGHT,
        sw, theme.BAR_HEIGHT,
        0,
        SCREEN.root_depth,
        X.InputOutput,
        X.CopyFromParent,
        override_redirect=True,
        background_pixel=theme.BAR_BG,
        event_mask=(X.ExposureMask | X.StructureNotifyMask)
    )
    BAR.map()
    DISPLAY.sync()
    return BAR


def draw(text: str):
    if BAR is None:
        return

    BAR.clear_area()
    gc = BAR.create_gc(foreground=theme.BAR_FG)
    BAR.draw_text(gc, 8, theme.BAR_TEXT_BASELINE, text)
    DISPLAY.flush()
