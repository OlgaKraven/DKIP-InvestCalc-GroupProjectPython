from src.storage.json_storage import JsonStorage
from src.models.item import Item


class ItemService:
    def __init__(self):
        self.storage = JsonStorage("data/items.json")

    def get_all(self):
        return self.storage.load()

    def add_item(self, item: Item):
        data = self.storage.load()
        data.append(item.model_dump())
        self.storage.save(data)
        return item
