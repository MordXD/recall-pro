from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from src.schemas import (
    UserCreateRequest, UserCreateResponse, 
    UserLoginRequest, UserLoginResponse, 
    UserLogoutResponse, RefreshTokenRequest, TokenResponse
)
from src.auth_service import AuthService, get_auth_service

router = APIRouter()
security = HTTPBearer()

@router.post("/signup", response_model=UserCreateResponse)
async def signup(
    user_data: UserCreateRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    try:
        return await auth_service.signup(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.post("/login", response_model=UserLoginResponse)
async def login(
    user_data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Авторизация пользователя"""
    try:
        return await auth_service.login(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.post("/logout", response_model=UserLogoutResponse)
async def logout(
    refresh_token: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Выход из системы"""
    try:
        return await auth_service.logout(refresh_token.refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление access токена"""
    try:
        return await auth_service.refresh_access_token(refresh_token.refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")

@router.get("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Проверка валидности токена"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return {"valid": True, "payload": payload}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")