import os
from typing import List

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import MarkupRequest, Product, ProductDealerKey, get_db

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


# API-маршруты

# Получение всех записей
@app.get("/products/", response_model=List[Product])
def get_all_products(skip: int = 0,
                     limit: int = 10,
                     db: Session = Depends(get_db)):
    return db.query(Product).offset(skip).limit(limit).all()


# Получение статистики
@app.get("/statistics/")
def get_statistics(db: Session = Depends(get_db)):
    # Получение общего количества размеченных товаров
    total_markup_count = db.query(
        func.count()).select_from(ProductDealerKey).scalar()

    # Получение количества товаров, у которых есть сопоставление
    matched_products_count = (
        db.query(func.count())
        .select_from(ProductDealerKey)
        .filter(ProductDealerKey.key.isnot(None))
        .scalar()
    )

    # Расчет процента сопоставленных товаров
    if total_markup_count > 0:
        matching_percentage = (
                (matched_products_count / total_markup_count) * 100
        )
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
    # Например, можно выбрать первый товар,
    # который еще не был размечен, и начать с него
    unmarked_product = db.query(Product).filter(
        ~Product.product_dealer_keys.any()).first()

    if not unmarked_product:
        raise HTTPException(status_code=404,
                            detail="No unmarked products found")

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
def markup_product(product_id: int,
                   markup_request: MarkupRequest,
                   db: Session = Depends(get_db)):
    # Реализация логики разметки конкретного товара
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Добавление сопоставления в базу данных
    db_markup = ProductDealerKey(key=markup_request.key, product_id=product_id)
    db.add(db_markup)
    db.commit()
    db.refresh(db_markup)

    return {"message": f"Markup for product {product_id} completed",
            "markup_id": db_markup.id}


# Просмотр всех записей
@app.get("/markup/", response_model=List[Product])
def view_markup(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Реализация логики просмотра разметки
    return db.query(Product).filter(
        Product.product_dealer_keys.any()).offset(skip).limit(limit).all()
