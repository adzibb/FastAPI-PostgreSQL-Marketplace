from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Annotated

import models
from database import engine
from routers.users import get_db, get_current_active_user
from schemas.product import ProductCreate, ProductInDB, Product
from schemas.user import User

models.Base.metadata.create_all(bind=engine)

router = APIRouter()


def create_product(db: Session, new_product: ProductCreate):
    new = models.Product(
        name=new_product.name,
        description=new_product.description,
        quantity=new_product.quantity,
        price=new_product.price,
    )
    db.add(new)
    db.commit()
    db.refresh(new)

    return new


# read by name only [others later]
def read_product_by_name(prod_name: str, db: Session):
    product = db.query(models.Product).filter(models.Product.name == prod_name).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with name {prod_name} not found.")
    return product


# update by name only [others later]
def update_product():
    pass


def remove_product(name: str, db: Session):
    product = read_product_by_name(prod_name=name, db=db)
    db.delete(product)
    db.commit()
    return {"message": f"product with name {name} deleted successfully"}


@router.post("/create-product", response_model=ProductInDB)
async def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_pro = create_product(db=db, new_product=product)
    return new_pro


@router.get("/products/{name}", response_model=Product)
async def get_product_by_name(name: str, db: Session = Depends(get_db)):
    prod = read_product_by_name(prod_name=name, db=db)
    return prod


@router.get("/product_list", response_model=list[Product])
async def product_list(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    items = db.query(models.Product).offset(skip).limit(limit).all()
#     there could be no product. rare.
    return items


@router.delete("/delete/{name}")
async def remove_product_name(name: str, db: Session = Depends(get_db)):
    prod = remove_product(name=name, db=db)
    return prod


@router.put("/update/{name}", response_model=Product)
async def update_product(name: str, product: Product, db: Session = Depends(get_db)):
    prod = read_product_by_name(prod_name=name, db=db)

    update_prod = jsonable_encoder(product)
    for field in update_prod:
        setattr(prod, field, update_prod[field])

    # Commit the changes to the database
    db.commit()

    return prod
