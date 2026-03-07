
class Tags:
    def __init__(self, num_tags=5):
        self.num_tags = num_tags
        self.current_tag = 1 << 0
        self.master_ratio = 0.6
        self.master_ratio_by_tag = {
            self.current_tag: self.master_ratio
        }

    def get_master_ratio(self):
        return self.master_ratio_by_tag.get(self.current_tag, self.master_ratio)

    def set_master_ratio(self, ratio):
        ratio = max(0.1, min(0.9, ratio))
        self.master_ratio_by_tag[self.current_tag] = ratio

    def is_visible(self, client):
        return client.tags & self.current_tag

    def view(self, index):
        self.current_tag = 1 << index
        self.master_ratio_by_tag.setdefault(self.current_tag, self.master_ratio)

    def toggle_view(self, index):
        self.current_tag ^= (1 << index)

    def move_client(self, client, index):
        client.tags ^= (1 << index)

    def set_tag(self, mask):
        self.current_tag = mask
