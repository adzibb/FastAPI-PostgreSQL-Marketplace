from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CartBase(BaseModel):
    user_id: int


class CartInDB(CartBase):
    cart_id: int
    created_at: datetime


class CreateCart(CartBase):
    model_config = ConfigDict(from_attributes=True)


# cart item models
class ItemBase(BaseModel):
    cart_id: int
    product_id: int
    quantity: int


class ItemAdd(ItemBase):
    pass

    model_config = ConfigDict(from_attributes=True)


class Item(BaseModel):
    product_name: str
    quantity: int
