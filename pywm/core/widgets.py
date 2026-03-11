import time
from datetime import datetime
import psutil

class Widget:
    interval = 1.0

    def __init__(self):
        self.last_update = 0
        self._text = ""

    def should_update(self):
        now = time.time()
        if now - self.last_update >= self.interval:
            self.update()
            self.last_update = now

    def update(self):
        pass

    def text(self):
        return self._text


class ClockWidget(Widget):
    interval = 1.0

    def __init__(self):
        super().__init__()
        self.update()
        self.last_update = time.time()

    def update(self):
        self._text = datetime.now().strftime("%H:%M")


class CPUWidget(Widget):
    interval = 1.0

    def __init__(self):
        super().__init__()
        self.update()
        self.last_update = time.time()

    def update(self):
        percent = psutil.cpu_percent(interval=None)
        self._text = f"CPU {percent}%"


class MemoryWidget(Widget):
    interval = 1.0

    def __init__(self):
        super().__init__()
        self.update()
        self.last_update = time.time()

    def update(self):
        memory = psutil.virtual_memory()
        memory = memory.percent
        self._text = f"MEM {memory}%"
