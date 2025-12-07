from fastapi import APIRouter
from src.models.item import Item
from src.services.item_service import ItemService

router = APIRouter()
service = ItemService()

@router.get("/items")
def get_items():
    return service.get_all()

@router.post("/items")
def add_item(item: Item):
    return service.add_item(item)
