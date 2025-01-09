from sqlalchemy import String, Integer, Text, Float, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import date


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    usersurname: Mapped[str] = mapped_column(String(100), nullable=False)
    userphone: Mapped[str] = mapped_column(String(100))
    telegram_id: Mapped[str] = mapped_column(String(100))


class Admins(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    telegram_id: Mapped[str] = mapped_column(String(100))


class Products(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[int] = mapped_column(Integer)
    images: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    status_product: Mapped[int] = mapped_column(Integer)


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))


class Basket(Base):
    __tablename__ = "basket"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_telegram_id: Mapped[str] = mapped_column(String(100))
    product: Mapped[int] = mapped_column(Integer)
    product_quantity: Mapped[int] = mapped_column(Integer)
    product_sum: Mapped[float] = mapped_column(Float)


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[date] = mapped_column(Date, default=date.today)
    sum_order: Mapped[float] = mapped_column(Float)
    order_product: Mapped[str] = mapped_column(Text)
    order_quantity: Mapped[int] = mapped_column(Integer)
    user_telegram_id: Mapped[str] = mapped_column(String(100))
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_surname: Mapped[str] = mapped_column(String(100))
    user_phone: Mapped[str] = mapped_column(String(100))
    order_status: Mapped[int] = mapped_column(Integer)

class Language(Base):
    __tablename__ = "language"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[str] = mapped_column(String(100))
    user_language: Mapped[str] = mapped_column(String(2))
