from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, func, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Session, sessionmaker, declarative_base, relationship
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
import os


# Создание экземпляра FastAPI
app = FastAPI()

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений переменных окружения
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
dbname = os.getenv("POSTGRES_DB")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")

# Строка подключения к базе данных
DATABASE_URL = (f"postgresql://{user}:{password}@"
                f"{host}:{port}/{dbname}")
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
    product_dealer_keys = relationship("ProductDealerKey", back_populates="product")

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

# API-маршруты

# Получение всех записей
@app.get("/products/", response_model=List[Product])
def get_all_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

# Получение статистики
@app.get("/statistics/")
def get_statistics(db: Session = Depends(get_db)):
    # Получение общего количества размеченных товаров
    total_markup_count = db.query(func.count()).select_from(ProductDealerKey).scalar()

    # Получение количества товаров, у которых есть сопоставление
    matched_products_count = (
        db.query(func.count())
        .select_from(ProductDealerKey)
        .filter(ProductDealerKey.key.isnot(None))
        .scalar()
    )

    # Расчет процента сопоставленных товаров
    if total_markup_count > 0:
        matching_percentage = (matched_products_count / total_markup_count) * 100
    else:
        matching_percentage = 0

    return {
        "total_markup_count": total_markup_count,
        "matched_products_count": matched_products_count,
        "matching_percentage": matching_percentage,
    }

# Переход в режим разметки товаров
@app.post("/markup/")
def start_markup(db: Session = Depends(get_db)):
    # Реализация логики начала разметки
    # Например, можно выбрать первый товар, который еще не был размечен, и начать с него
    unmarked_product = db.query(Product).filter(~Product.product_dealer_keys.any()).first()

    if not unmarked_product:
        raise HTTPException(status_code=404, detail="No unmarked products found")

    # Здесь можно добавить дополнительную логику для начала разметки
    # Например, установка флага начала разметки в базе данных

    return {"message": "Markup started", "product_id": unmarked_product.id}

# Предоставление вариантов соответствия товаров
@app.get("/matching-options/{product_id}", response_model=List[int])
def get_matching_options(product_id: int, db: Session = Depends(get_db)):
    # Реализация логики предоставления вариантов соответствия для товара
    # Например, можно использовать ML-модель для предсказания соответствия
    # Здесь возможные варианты соответствия - это целые числа
    
    return [1, 2, 3]  # Можно заменить на нужные варианты соответствия

# Разметка товара
@app.post("/markup/{product_id}")
def markup_product(product_id: int, markup_request: MarkupRequest, db: Session = Depends(get_db)):
    # Реализация логики разметки конкретного товара
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Добавление сопоставления в базу данных
    db_markup = ProductDealerKey(key=markup_request.key, product_id=product_id)
    db.add(db_markup)
    db.commit()
    db.refresh(db_markup)

    return {"message": f"Markup for product {product_id} completed", "markup_id": db_markup.id}

# Просмотр всех записей
@app.get("/markup/", response_model=List[Product])
def view_markup(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Реализация логики просмотра разметки
    marked_products = db.query(Product).filter(Product.product_dealer_keys.any()).offset(skip).limit(limit).all()
    return marked_products
