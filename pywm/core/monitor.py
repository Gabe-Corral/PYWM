

class Monitor:
    def __init__(self, x, y, width, height, tags):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.tags = tags
        self.statusbar = None
        self.focused_client = None
        self.widgets = []

    def contains(self, px, py):
        return (
            self.x <= px < self.x + self.width
            and self.y <= py < self.y + self.height
        )
