from .connection import DISPLAY


_atoms = {}


def atom(name: str):
    if name not in _atoms:
        _atoms[name] = DISPLAY.intern_atom(name)
    return _atoms[name]


WM_DELETE_WINDOW = atom("WM_DELETE_WINDOW")
WM_PROTOCOLS = atom("WM_PROTOCOLS")
NET_WM_NAME = atom("_NET_WM_NAME")
UTF8_STRING = atom("UTF8_STRING")
