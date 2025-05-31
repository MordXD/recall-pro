import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://recall_user:recall_password@localhost:5432/recall_pro")

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения сессии базы данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Создание всех таблиц в базе данных
    """
    Base.metadata.create_all(bind=engine) 