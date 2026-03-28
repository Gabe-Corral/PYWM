from pywm.x11.connection import alloc_color, SCREEN

from dataclasses import dataclass


@dataclass
class ThemeConfig:
    border_width: int = 4
    gap: int = 8

    color_focused: int = alloc_color("#bd93f9")
    color_unfocused: int = alloc_color("gray20")
    background_color: int = alloc_color("black")

    bar_height: int = 24
    bar_bg: int = alloc_color("#282a36")
    bar_fg: int = alloc_color("#f8f8f2")

    bar_active_tag: int = alloc_color("#bd93f9")

    bar_text_baseline: int = 16


theme = ThemeConfig()
