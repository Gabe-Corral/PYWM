from Xlib import X
from pywm.x11.connection import DISPLAY, ROOT, SCREEN
from pywm.ui import theme
from pywm.core import cursor
from pywm.core import tags

from dataclasses import dataclass

BAR = None

BUTTONS = []

@dataclass
class Button:
    x: int
    y: int
    w: int
    h: int
    tag: int


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
        cursor=cursor.CURSOR,
        event_mask=(
            X.ExposureMask |
            X.StructureNotifyMask |
            X.ButtonPressMask |
            X.PointerMotionMask
        )
    )
    BAR.map()
    DISPLAY.sync()
    return BAR


# def draw(text):
#     if BAR is None:
#         return

#     BAR.clear_area()
#     gc = BAR.create_gc(foreground=theme.BAR_FG)
#     BAR.draw_text(gc, 8, theme.BAR_TEXT_BASELINE, text)
#     DISPLAY.flush()


def draw(text):
    global BUTTONS
    if BAR is None:
        return

    BUTTONS = []
    BAR.clear_area()

    gc = BAR.create_gc(foreground=theme.BAR_FG)
    agc = BAR.create_gc(foreground=theme.BAR_ACTIVE_TAG)

    pad = 0
    x = pad
    y = 0
    h = theme.BAR_HEIGHT

    btn_w = 28
    btn_h = h

    for i in range(tags.NUM_TAGS):
        mask = 1 << i

        if tags.CURRENT_TAG & mask:
            BAR.rectangle(agc, x, 0, btn_w - 1, btn_h - 1)
        else:
            BAR.rectangle(gc, x, 0, btn_w - 1, btn_h - 1)

        BAR.draw_text(gc, x + 10, theme.BAR_TEXT_BASELINE, str(i + 1))

        BUTTONS.append(Button(x=x, y=y, w=btn_w, h=btn_h, tag=mask))

        x += btn_w

    BAR.draw_text(gc, x + 12, theme.BAR_TEXT_BASELINE, text)

DISPLAY.flush()


def check_tag_pressed(event):
    if BAR is None or event.window.id != BAR.id:
        return None

    for b in BUTTONS:
        if b.x <= event.event_x < b.x + b.w and b.y <= event.event_y < b.y + b.h:
            return b.tag

    return tags.CURRENT_TAG
