from pydantic import BaseModel
from datetime import datetime


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
    category: str
    tags: list[str]


class Cart(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int


class OrderHistory(BaseModel):
    id: int
    user_id: int
    product_id: int
    order_datetime: datetime
    status: str  # e.g., 'pending', 'shipped', 'delivered'
    payment_info: str
    shipping_address: str
