from pywm.core.manager import FRAMES


def get_client_from_event(event):
    frame = FRAMES.get(event.window.id)
    if frame:
        return frame.client
    return None
