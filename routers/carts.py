from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

import models
from routers.users import get_db, get_current_active_user
from schemas.cart import Item
from schemas.user import User

router = APIRouter()


# 404 exception
def not_found_404(details: str = "not found"):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{details}"
    )


# add new product to cart
def add_to_cart(cart_id: int, product_id: int, quantity: int, db: Session):
    new_item = models.CartItem(
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


# use cart id or username to fetch user id OR use authentication
def view_contents(cart_id: int, db: Session):
    items = db.query(models.CartItem).filter(models.CartItem.cart_id == cart_id).all()
    if not items:
        raise not_found_404(details="No item have been added to your cart")
    return items


# remove a product from cart
def remove_from_cart(prod_id: int, db: Session):
    item = db.query(models.CartItem).filter(models.CartItem.product_id == prod_id).first()
    if not item:
        raise not_found_404(details="Product does not exist in cart")
    db.delete(item)
    db.commit()
    return {"message": "Product deleted successfully"}


def update_prod_quantity():
    pass


@router.post("/new-cart", description="Create new empty cart")
async def create_cart(current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    # check if user exists in db
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise not_found_404(details="User does not exist")

    # check if user has cart already
    user_cart = db.query(models.Cart).filter(models.Cart.user == user).first()
    if user_cart:
        return {"message": "You already have a cart. You can add products to your cart."}

    # create new cart with for user and save to db
    cart = models.Cart(user_id=user.user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)

    return {"message": "Cart is empty. Add products to your cart"}


@router.get("/view-items", description="View all the products in your cart")
async def view_cart_content(
        current_user: Annotated[User, Depends(get_current_active_user)],
        db: Session = Depends(get_db)
):
    # check if user exists in db
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise not_found_404(details="User does not exist")

    # get user cart
    cart = db.query(models.Cart).filter(models.Cart.user == user).first()
    if not cart:
        raise not_found_404(details="User cart does not exist")

    # get all items in cart
    cart_items = view_contents(cart_id=cart.cart_id, db=db)

    content = []
    for item in cart_items:
        prod = item.product
        content.append(
            {
                "product_name": prod.name,
                "quantity": item.quantity,
                "price": item.quantity * prod.price
            }
        )

    return content


@router.post("/add-item", description="Add a product to your cart")
async def add_new_product(
        current_user: Annotated[User, Depends(get_current_active_user)],
        new_product: Item, db: Session = Depends(get_db)
):
    # check if the user exists
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise not_found_404(details="User does not exist")

    # get user cart
    cart = db.query(models.Cart).filter(models.Cart.user == user).first()
    if not cart:
        raise not_found_404(details="User cart does not exist")

    # quantity of new product
    quantity = new_product.quantity

    # check if product exists
    db_prod = db.query(models.Product).filter(models.Product.name == new_product.product_name).first()
    if not db_prod:
        raise not_found_404(details=new_product.product_name)

    # quantity of product in db
    db_quantity = db_prod.quantity

    # if the quantity requested is more than existing, raise not acceptable error
    if quantity > db_quantity:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Not much product at the moment, {db_quantity} left"
        )

    # check if product exist in cart
    # prod_cart = db.query(models.CartItem).filter(models.CartItem.product == db_prod).first()
    prod_cart = db.query(models.CartItem).filter(
        models.CartItem.cart == cart,
        models.CartItem.product == db_prod
    ).first()

    # if product exists in the cart, update the quantity
    if prod_cart:
        prod_cart.quantity += quantity
        db_prod.quantity -= quantity
        # new_quantity = prod_cart.quantity + quantity
        # new_quantity_db = db_quantity - quantity
        # setattr(prod_cart, "quantity", new_quantity)
        # setattr(db_prod, "quantity", new_quantity_db)
        db.commit()
        return {"message": "product update successfully"}
    else:
        # add new product to cart
        user_cart = add_to_cart(cart_id=cart.cart_id, product_id=db_prod.product_id, quantity=quantity, db=db)

        db_prod.quantity -= quantity
        db.commit()
        return {"message": "product added successfully"}

    # return {"message": "could not add product"}


@router.delete("/remove-product", description="remove a product from your cart")
async def remove_product(
        current_user: Annotated[User, Depends(get_current_active_user)],
        product_name: str, db: Session = Depends(get_db)
):
    # check if user exists
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise not_found_404(details="User does not exist")

    # check if user has cart
    cart = db.query(models.Cart).filter(models.Cart.user == user).first()
    if not cart:
        raise not_found_404("User cart does not exist")

    # check if product exists
    db_prod = db.query(models.Product).filter(models.Product.name == product_name).first()
    if not db_prod:
        raise not_found_404(details=product_name)

    # check if product exists in cart
    prod_cart = db.query(models.CartItem).filter(
        models.CartItem.cart == cart,
        models.CartItem.product == db_prod
    ).first()

    # remove the product
    remova = remove_from_cart(prod_cart.product_id, db)

    if remova:
        db_prod.quantity += prod_cart.quantity
    db.commit()

    return remova


@router.delete("/delete-cart", description="remove a cart associated with a user")
async def delete_cart(current_user: Annotated[User, Depends(get_current_active_user)], db: Session = Depends(get_db)):
    # check if user exists
    user = db.query(models.User).filter(models.User.username == current_user.username).first()
    if not user:
        raise not_found_404(details="User does not exist")

    # check if user has cart
    cart = db.query(models.Cart).filter(models.Cart.user == user).first()
    if not cart:
        raise not_found_404("User cart does not exist")

    db.delete(cart)
    db.commit()

    return {"message": "User cart deleted"}
