import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER', 'POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD',
                              'POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'POSTGRES_DB')
DB_HOST = os.getenv('DB_HOST', 'DB_HOST')
DB_PORT = os.getenv('DB_PORT', 'DB_PORT')

DATABASE_URL = (f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
                f"{DB_HOST}:{DB_PORT}/{POSTGRES_DB}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# проверка соединения с базой данных в контейнере
if __name__ == '__main__':
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(result.scalar())
