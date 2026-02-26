from pywm.x11.connection import SCREEN
from pywm.ui import theme
from pywm.core import tags

# def apply_tiling_layout(clients, master_ratio=0.6):
#     clients = [i for i in clients.values()]

#     screen_width = SCREEN.width_in_pixels - 2*theme.BORDER_WIDTH
#     screen_height = SCREEN.height_in_pixels - 2*theme.BORDER_WIDTH - theme.BAR_HEIGHT


#     if len(clients) == 1:
#         clients[0].window.configure(
#             x=0,
#             y=0,
#             width=screen_width,
#             height=screen_height
#         )
#         frame = clients[0].frame.window
#         frame.configure(
#             x=0,
#             y=0,
#             width=screen_width,
#             height=screen_height
#         )
#         return

#     master_width = int(screen_width * master_ratio)
#     stack_width = screen_width - master_width

#     master = clients[0]
#     stack = clients[1:]

#     master.frame.window.configure(
#         x=0,
#         y=0,
#         width=master_width,
#         height=screen_height
#     )

#     stack_height = screen_height // len(stack)

#     for i, client in enumerate(stack):
#         client.frame.window.configure(
#             x=master_width,
#             y=i * stack_height,
#             width=stack_width,
#             height=stack_height
#         )
#         client.window.configure(
#             x=0,
#             y=0,
#             width=stack_width,
#             height=stack_height
#         )


def apply_tiling_layout(clients):
    clients = list(clients.values())
    if not clients:
        return

    outer = theme.GAP          # gap at screen edges
    inner = theme.GAP          # gap between windows (you can make this different)
    bw = theme.BORDER_WIDTH

    sw = SCREEN.width_in_pixels
    sh = SCREEN.height_in_pixels - theme.BAR_HEIGHT

    # Usable area inside the OUTER gap
    ux = outer
    uy = outer
    uw = sw - 2 * outer
    uh = sh - 2 * outer

    def place(client, x, y, w, h):
        """
        x,y,w,h are the OUTER rectangle we want the window+border to fit in.
        Because X11 border is outside the configured size, shrink by 2*bw.
        """
        fw = max(1, w - 2 * bw)
        fh = max(1, h - 2 * bw)

        client.frame.window.configure(x=x, y=y, width=fw, height=fh)
        client.window.configure(x=0, y=0, width=fw, height=fh)

    # 1 window: fill usable area (no inner gaps needed)
    if len(clients) == 1:
        place(clients[0], ux, uy, uw, uh)
        return

    master = clients[0]
    stack = clients[1:]
    n = len(stack)

    # Horizontal split with an INNER gap between master and stack
    master_ratio = tags.get_master_ratio()
    uw2 = uw - inner
    master_w = int(uw2 * master_ratio)
    stack_w = uw2 - master_w

    master_x = ux
    stack_x = ux + master_w + inner

    place(master, master_x, uy, master_w, uh)

    # Vertical stack with INNER gaps between stacked windows
    total_inner_gaps = (n - 1) * inner
    tile_h = (uh - total_inner_gaps) // n

    for i, c in enumerate(stack):
        cy = uy + i * (tile_h + inner)
        place(c, stack_x, cy, stack_w, tile_h)
