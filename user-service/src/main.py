from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from routers.auth import router as auth_router

# Создание FastAPI приложения
app = FastAPI(
    title="Recall Pro - User Service",
    description="Сервис аутентификации и управления пользователями",
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
app.include_router(auth_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    print("User Service запущен")

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Recall Pro User Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "user"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port,
        reload=debug
    )