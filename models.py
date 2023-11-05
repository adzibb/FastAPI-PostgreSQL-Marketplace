from sqlalchemy import Column, Integer, String, Float, ForeignKey, func, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    email = Column(String(100), unique=True)
    full_name = Column(String)
    password_hash = Column(String(100))

    # Add other user-related fields here

    user_profiles = relationship("UserProfile", back_populates="user")
    carts = relationship("Cart", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)

    # Add user profile fields here

    user = relationship("User", back_populates="user_profiles")


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String)
    price = Column(Float(precision=2))
    quantity = Column(Integer)

    # Add other product-related fields here

    cart_items = relationship("CartItem", back_populates="product")


class Cart(Base):
    __tablename__ = 'carts'

    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="carts")
    cart_items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = 'cart_items'

    cart_item_id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey('carts.cart_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    quantity = Column(Integer)

    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    status = Column(String(20))

    # Add other transaction-related fields here

    user = relationship("User", back_populates="transactions")
