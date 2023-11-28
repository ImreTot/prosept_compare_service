import os

from typing import List
from pydantic import BaseModel
from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        create_engine)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config import DATABASE_URL

# Получение значений переменных окружения
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

engine = create_engine(DATABASE_URL)

# Создание экземпляра declarative_base
Base = declarative_base()


# Модели данных для SQLAlchemy
class DealerPrice(Base):
    """
    Модель данных для таблицы 'marketing_dealerprice'.
    """

    __tablename__ = "marketing_dealerprice"

    id = Column(Integer, primary_key=True, index=True)
    product_key = Column(String)
    price = Column(Float)
    product_url = Column(String)
    product_name = Column(String)
    date = Column(DateTime)
    dealer_id = Column(Integer, ForeignKey("dealers.id"))
    dealer = relationship("Dealer", back_populates="marketing_dealerprice")


class ProductDealerKey(Base):
    """
    Модель данных для таблицы 'marketing_productdealerkey'.
    """

    __tablename__ = "marketing_productdealerkey"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String)
    dealer_id = Column(Integer, ForeignKey("dealers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    dealer = relationship("Dealer",
                          back_populates="marketing_productdealerkey")
    product = relationship("Product",
                           back_populates="marketing_productdealerkey")


class Dealer(Base):
    """
    Модель данных для таблицы 'marketing_dealer'.
    """

    __tablename__ = "marketing_dealer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dealer_prices = relationship("DealerPrice", back_populates="dealer")
    product_dealer_keys = relationship("ProductDealerKey",
                                       back_populates="dealer")


class Product(Base):
    """
    Модель данных для таблицы 'marketing_product'.
    """

    __tablename__ = "marketing_product"

    row_number = Column(Integer)
    id = Column(Integer, primary_key=True, index=True)
    article = Column(String)
    ean_13 = Column(String)
    name = Column(String)
    cost = Column(Float)
    recommended_price = Column(Float)
    category_id = Column(Integer)
    ozon_name = Column(String)
    name_1c = Column(String)
    wb_name = Column(String)
    ozon_article = Column(String)
    wb_article = Column(String)
    ym_article = Column(String)
    wb_article_td = Column(String)
    product_dealer_keys = relationship("ProductDealerKey",
                                       back_populates="product")


# Создание фабрики сессий SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Модель для запроса разметки товара
class MarkupRequest(BaseModel):
    matching_option: int


class Recommendation(BaseModel):
    product_id: int
    recommended_ids: List[int]
