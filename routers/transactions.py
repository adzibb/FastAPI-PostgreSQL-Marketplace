from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

import models
from routers.carts import not_found_404
from routers.users import get_db

router = APIRouter()


@router.get("/checkout", description="Checkout the total price of your products")
async def checkout_product(username: str, db: Session = Depends(get_db)):
    # check if the user exists
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise not_found_404(details="User does not exist")

    # get user cart
    cart = db.query(models.Cart).filter(models.Cart.user == user).first()
    if not cart:
        raise not_found_404(details="User cart does not exist")

    # get products from user cart
    prod_cart = db.query(models.CartItem).filter(models.CartItem.cart == cart,).all()
    if not prod_cart:
        raise not_found_404(details="No product has been added to cart")

    # return the total price of the products
    content = []
    total_price = 0
    for item in prod_cart:
        prod = item.product
        total_price += item.quantity * prod.price
        content.append(
            {
                "product_name": prod.name,
                "quantity": item.quantity,
                "price": item.quantity * prod.price
            }
        )

    content.append({"total amount": total_price})
    return content
