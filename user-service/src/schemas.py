from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Базовые схемы для пользователя
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: str = Field(..., description="Email адрес")


# Схемы для создания пользователя
class UserCreateRequest(UserBase):
    password: str = Field(..., min_length=6, description="Пароль (минимум 6 символов)")


class UserCreateResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Схемы для входа в систему
class UserLoginRequest(BaseModel):
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# Схемы для обновления пользователя
class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None)
    password: Optional[str] = Field(None, min_length=6)


# Схема для ответа с данными пользователя
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Схемы для токенов
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh токен")


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh токен")


# Схемы для ошибок
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# Схема для успешного ответа
class SuccessResponse(BaseModel):
    message: str
    success: bool = True


# Схемы для пагинации
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Номер страницы")
    limit: int = Field(10, ge=1, le=100, description="Количество элементов на странице")


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Схема для выхода из системы
class UserLogoutResponse(BaseModel):
    message: str = "Успешный выход из системы"
    success: bool = True



