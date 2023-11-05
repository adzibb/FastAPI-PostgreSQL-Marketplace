from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    quantity: int


class ProductInDB(ProductBase):
    product_id: int


class ProductCreate(ProductBase):
    model_config = ConfigDict(from_attributes=True)


class Product(ProductBase):
    pass




