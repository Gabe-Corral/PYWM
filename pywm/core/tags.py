
NUM_TAGS = 5

# bitmask for tags
CURRENT_TAG = 1 << 0


def is_visible(client):
    return client.tags & CURRENT_TAG


def view(index):
    global CURRENT_TAG
    CURRENT_TAG = 1 << index


def toggle_view(index):
    global CURRENT_TAG
    CURRENT_TAG ^= (1 << index)


def move_client(client, index):
    client.tags ^= (1 << index)


def set_tag(mask):
    global CURRENT_TAG
    CURRENT_TAG = mask
