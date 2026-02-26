
NUM_TAGS = 5

# bitmask for tags
CURRENT_TAG = 1 << 0

MASTER_RATIO = 0.6
MASTER_RATIO_BY_TAG = {CURRENT_TAG: MASTER_RATIO}


def get_master_ratio():
    return MASTER_RATIO_BY_TAG.get(CURRENT_TAG, MASTER_RATIO)


def set_master_ratio(ratio):
    ratio = max(0.1, min(0.9, ratio))
    MASTER_RATIO_BY_TAG[CURRENT_TAG] = ratio


def is_visible(client):
    return client.tags & CURRENT_TAG


def view(index):
    global CURRENT_TAG
    CURRENT_TAG = 1 << index
    MASTER_RATIO_BY_TAG.setdefault(CURRENT_TAG, MASTER_RATIO)


def toggle_view(index):
    global CURRENT_TAG
    CURRENT_TAG ^= (1 << index)


def move_client(client, index):
    client.tags ^= (1 << index)


def set_tag(mask):
    global CURRENT_TAG
    CURRENT_TAG = mask
