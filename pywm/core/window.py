from dataclasses import dataclass
from Xlib.xobject.drawable import Window


@dataclass
class Client:
    window: Window
    # frame: Frame


@dataclass
class Frame:
    window: Window
    client: Client
