from Xlib import X
from dataclasses import dataclass

from pywm.x11.connection import DISPLAY, ROOT
from pywm.ui.theme import theme
from pywm.core import cursor


@dataclass
class Button:
    x: int
    y: int
    w: int
    h: int
    tag: int


class StatusBar:
    def __init__(self, x, y, width, height, tags, widgets):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tags = tags

        self.window = None
        self.buttons = []
        self.widgets = widgets

        self._create_window()

    def _create_window(self):
        self.window = ROOT.create_window(
            self.x,
            self.y,
            self.width,
            self.height,
            0,
            DISPLAY.screen().root_depth,
            X.InputOutput,
            X.CopyFromParent,
            override_redirect=True,
            background_pixel=theme.bar_bg,
            cursor=cursor.CURSOR,
            event_mask=(
                X.ExposureMask
                | X.StructureNotifyMask
                | X.ButtonPressMask
                | X.PointerMotionMask
            ),
        )

        self.window.map()
        DISPLAY.sync()

    def draw(self, text=None):
        # NOTE: fix the slop in this method please
        if self.window is None:
            return

        self.buttons = []
        self.window.clear_area()

        gc = self.window.create_gc(foreground=theme.bar_fg)
        agc = self.window.create_gc(foreground=theme.bar_active_tag)

        x = 0
        btn_w = 28
        btn_h = self.height

        # ---- LEFT: TAG BUTTONS ----
        for i in range(self.tags.num_tags):
            mask = 1 << i

            if self.tags.current_tag & mask:
                self.window.rectangle(agc, x, 0, btn_w - 1, btn_h - 1)
            else:
                self.window.rectangle(gc, x, 0, btn_w - 1, btn_h - 1)

            self.window.draw_text(
                gc,
                x + 10,
                theme.bar_text_baseline,
                str(i + 1),
            )

            self.buttons.append(
                Button(x=x, y=0, w=btn_w, h=btn_h, tag=mask)
            )

            x += btn_w

        # ---- BASE TEXT (TITLE) — KEEP ORIGINAL LEFT POSITION ----
        base_text = text or getattr(self, "title_text", "") or ""

        approx_char_width = 7

        text_x = x + 12

        self.window.draw_text(
            gc,
            text_x,
            theme.bar_text_baseline,
            base_text,
        )

        # ---- RIGHT: WIDGETS ----
        # monitor = getattr(self, "monitor", None)
        # print(monitor)
        # widgets = []
        # if monitor and hasattr(monitor, "widgets"):
        #     print("HERT")
        #     widgets = monitor.widgets

        right_text = "  ".join(w.text() for w in self.widgets)
        # right_text = "10:00pm"

        if right_text:
            right_width = len(right_text) * approx_char_width
            right_x = self.width - right_width

            self.window.draw_text(
                gc,
                right_x,
                theme.bar_text_baseline,
                right_text,
            )

        DISPLAY.flush()

    def check_tag_pressed(self, event):
        if self.window is None or event.window.id != self.window.id:
            return None

        for b in self.buttons:
            if (
                b.x <= event.event_x < b.x + b.w
                and b.y <= event.event_y < b.y + b.h
            ):
                return b.tag

        return None
