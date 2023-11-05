from fastapi import FastAPI
from routers import users, products, carts, transactions

app = FastAPI()


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(carts.router, prefix="/carts", tags=["carts"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
