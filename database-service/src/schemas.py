from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Базовые схемы для пользователя
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: str = Field(..., description="Email адрес")


# Схемы для создания пользователя через Database Service
class UserCreateRequest(UserBase):
    password_hash: str = Field(..., description="Хешированный пароль")


class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None)
    password_hash: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)


# Схема для ответа с данными пользователя
class UserResponse(UserBase):
    id: int
    password_hash: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True


# Схемы для поиска пользователей
class UserSearchRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    user_id: Optional[int] = None


# Схемы для токенов
class RefreshTokenCreateRequest(BaseModel):
    token_hash: str = Field(..., description="Хеш токена")
    user_id: int = Field(..., description="ID пользователя")
    expires_at: datetime = Field(..., description="Время истечения токена")


class RefreshTokenResponse(BaseModel):
    id: int
    token_hash: str
    user_id: int
    expires_at: datetime
    created_at: datetime
    is_revoked: bool
    
    class Config:
        from_attributes = True


class RefreshTokenSearchRequest(BaseModel):
    token_hash: Optional[str] = None
    user_id: Optional[int] = None
    is_revoked: Optional[bool] = None


class RefreshTokenRevokeRequest(BaseModel):
    token_hash: str = Field(..., description="Хеш токена для отзыва")


# Схемы для пагинации
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Номер страницы")
    limit: int = Field(10, ge=1, le=100, description="Количество элементов на странице")


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Общие схемы ответов
class SuccessResponse(BaseModel):
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    detail: str
    error_code: Optional[str] = None


# Схема для очистки токенов
class TokenCleanupResponse(BaseModel):
    deleted_count: int
    message: str 