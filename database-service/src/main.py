from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from src.routers import users, tokens
from src.database import create_tables

# Создание FastAPI приложения
app = FastAPI(
    title="Recall Pro - Database Service",
    description="Сервис для работы с базой данных",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tokens.router, prefix="/api/v1/tokens", tags=["tokens"])

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    # Создание таблиц в базе данных
    create_tables()
    print("Database Service: База данных инициализирована")

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Recall Pro Database Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "database"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8002"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port,
        reload=debug
    ) 