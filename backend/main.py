from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Session, sessionmaker, declarative_base, relationship
from typing import List

DATABASE_URL = "URL_To_PostgreSQL.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()


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

    dealer = relationship("Dealer", back_populates="marketing_productdealerkey")
    product = relationship("Product", back_populates="marketing_productdealerkey")


class Dealer(Base):
    """
    Модель данных для таблицы 'marketing_dealer'.
    """

    __tablename__ = "marketing_dealer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    dealer_prices = relationship("DealerPrice", back_populates="dealer")
    product_dealer_keys = relationship("ProductDealerKey", back_populates="dealer")


class Product(Base):
    """
    Модель данных для таблицы 'marketing_product'.
    """

    __tablename__ = "marketing_product"

    id = Column(Integer, primary_key=True, index=True)
    article = Column(String)
    ean_13 = Column(String)
    name = Column(String)
    cost = Column(Float)
    min_recommended_price = Column(Float)
    recommended_price = Column(Float)
    category_id = Column(Integer)
    ozon_name = Column(String)
    name_1c = Column(String)
    wb_name = Column(String)
    ozon_article = Column(String)
    wb_article = Column(String)
    ym_article = Column(String)

    product_dealer_keys = relationship("ProductDealerKey", back_populates="product")

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Обработчики эндпоинтов для CRUD-операций

@app.get("/dealers/{dealer_id}", response_model=Dealer)
def read_dealer(dealer_id: int, db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")
    return dealer

@app.get("/dealers/", response_model=List[Dealer])
def read_dealers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    dealers = db.query(Dealer).offset(skip).limit(limit).all()
    return dealers
