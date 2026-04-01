from pywm.ui.theme import theme


def apply_tiling_layout(clients, monitor):
    clients = list(clients.values())
    if not clients:
        return

    outer = theme.gap # gap at screen edges
    inner = theme.gap # gap between windows
    bw = theme.border_width

    sw = monitor.width
    sh = monitor.height - theme.bar_height

    # usable area inside the OUTER gap
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

    if len(clients) == 1:
        place(clients[0], ux, uy, uw, uh)
        return

    master = clients[0]
    stack = clients[1:]
    n = len(stack)

    # horizontal split with an innger gap between master and stack
    master_ratio = monitor.tags.get_master_ratio()
    uw2 = uw - inner
    master_w = int(uw2 * master_ratio)
    stack_w = uw2 - master_w

    master_x = ux
    stack_x = ux + master_w + inner

    place(master, master_x, uy, master_w, uh)

    # vertical stack with inner gaps between stacked windows
    total_inner_gaps = (n - 1) * inner
    tile_h = (uh - total_inner_gaps) // n

    for i, c in enumerate(stack):
        cy = uy + i * (tile_h + inner)
        place(c, stack_x, cy, stack_w, tile_h)
