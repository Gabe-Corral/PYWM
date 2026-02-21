from Xlib import X
from Xlib import Xcursorfont

from pywm.x11.connection import DISPLAY, ROOT



font = DISPLAY.open_font('cursor')
shape = Xcursorfont.left_ptr
CURSOR = font.create_glyph_cursor(
    font,
    shape,
    shape + 1,
    (65535, 65535, 65535),  # fg: white
    (0, 0, 0)               # bg: black
)
