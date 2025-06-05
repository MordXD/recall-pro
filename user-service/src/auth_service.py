from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from schemas import (
    UserCreateRequest, UserCreateResponse, 
    UserLoginRequest, UserLoginResponse,
    UserLogoutResponse, UserResponse
)
from database_client import DatabaseClient, get_database_client
import hashlib
from datetime import timezone
import os

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Сервис аутентификации и авторизации пользователей"""
    
    def __init__(self, db_client: DatabaseClient = None):
        self.pwd_context = pwd_context
        self.db_client = db_client or get_database_client()
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создание access токена"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def _create_refresh_token(self, data: dict) -> str:
        """Создание refresh токена"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def _hash_token(self, token: str) -> str:
        """Хеширование токена для безопасного хранения"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def signup(self, user_data: UserCreateRequest) -> UserCreateResponse:
        """Регистрация нового пользователя"""
        
        # Проверяем, не существует ли уже пользователь
        existing_user = await self.db_client.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )
        
        existing_email = await self.db_client.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создаем нового пользователя
        hashed_password = self._hash_password(user_data.password)
        new_user = await self.db_client.create_user(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка создания пользователя"
            )
        
        # Возвращаем данные пользователя (без пароля)
        return UserCreateResponse(
            id=new_user["id"],
            username=new_user["username"],
            email=new_user["email"],
            created_at=datetime.fromisoformat(new_user["created_at"].replace('Z', '+00:00'))
        )
    
    async def login(self, user_data: UserLoginRequest) -> UserLoginResponse:
        """Авторизация пользователя"""
        
        # Находим пользователя
        user = await self.db_client.get_user_by_username(user_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль"
            )
        
        # Проверяем активность пользователя
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Аккаунт деактивирован"
            )
        
        # Проверяем пароль
        if not self._verify_password(user_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль"
            )
        
        # Создаем токены
        access_token = self._create_access_token(
            data={"sub": user["username"], "user_id": user["id"]}
        )
        refresh_token = self._create_refresh_token(
            data={"sub": user["username"], "user_id": user["id"]}
        )
        
        # Сохраняем refresh токен в базе данных
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        token_hash = self._hash_token(refresh_token)
        
        await self.db_client.create_refresh_token(
            token_hash=token_hash,
            user_id=user["id"],
            expires_at=expires_at
        )
        
        # Создаем объект пользователя для ответа
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            created_at=datetime.fromisoformat(user["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(user["updated_at"].replace('Z', '+00:00')) if user.get("updated_at") else None
        )
        
        return UserLoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_response
        )
    
    async def logout(self, refresh_token: str) -> UserLogoutResponse:
        """Выход из системы"""
        
        # Хешируем токен и отзываем его
        token_hash = self._hash_token(refresh_token)
        await self.db_client.revoke_refresh_token(token_hash)
        
        return UserLogoutResponse()
    
    def verify_token(self, token: str) -> dict:
        """Проверка валидности токена"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невалидный токен"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен"
            )
    
    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Обновление access токена с помощью refresh токена"""
        
        # Проверяем refresh токен
        token_hash = self._hash_token(refresh_token)
        token_record = await self.db_client.verify_refresh_token(token_hash)
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный или просроченный refresh токен"
            )
        
        # Получаем пользователя
        user = await self.db_client.get_user_by_id(token_record["user_id"])
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или деактивирован"
            )
        
        # Создаем новый access токен
        access_token = self._create_access_token(
            data={"sub": user["username"], "user_id": user["id"]}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

# Singleton instance
auth_service = AuthService()

def get_auth_service() -> AuthService:
    """Dependency для получения сервиса аутентификации"""
    return auth_service 