from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import math

from src.database import get_db
from src.crud import RefreshTokenCRUD
from src.schemas import (
    RefreshTokenCreateRequest, RefreshTokenResponse, 
    RefreshTokenRevokeRequest, SuccessResponse,
    TokenCleanupResponse
)

router = APIRouter()

@router.post("/", response_model=RefreshTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_token(
    token_data: RefreshTokenCreateRequest,
    db: Session = Depends(get_db)
):
    """Создать новый refresh токен"""
    try:
        token = RefreshTokenCRUD.create_refresh_token(
            db, 
            token_data.token_hash, 
            token_data.user_id, 
            token_data.expires_at
        )
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания токена: {str(e)}"
        )

@router.get("/verify/{token_hash}", response_model=RefreshTokenResponse)
async def verify_token(
    token_hash: str,
    db: Session = Depends(get_db)
):
    """Проверить и получить refresh токен по хешу"""
    token = RefreshTokenCRUD.get_refresh_token_by_hash(db, token_hash)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Токен не найден, отозван или истек"
        )
    return token

@router.get("/user/{user_id}", response_model=List[RefreshTokenResponse])
async def get_user_tokens(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить все токены пользователя"""
    tokens = RefreshTokenCRUD.get_user_tokens(db, user_id)
    return tokens

@router.post("/revoke", response_model=SuccessResponse)
async def revoke_token(
    revoke_data: RefreshTokenRevokeRequest,
    db: Session = Depends(get_db)
):
    """Отозвать refresh токен"""
    success = RefreshTokenCRUD.revoke_refresh_token(db, revoke_data.token_hash)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Токен не найден"
        )
    
    return SuccessResponse(message="Токен успешно отозван")

@router.post("/revoke-user/{user_id}", response_model=SuccessResponse)
async def revoke_user_tokens(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Отозвать все токены пользователя"""
    count = RefreshTokenCRUD.revoke_all_user_tokens(db, user_id)
    return SuccessResponse(message=f"Отозвано токенов: {count}")

@router.post("/cleanup", response_model=TokenCleanupResponse)
async def cleanup_expired_tokens(
    db: Session = Depends(get_db)
):
    """Очистить просроченные токены"""
    deleted_count = RefreshTokenCRUD.cleanup_expired_tokens(db)
    return TokenCleanupResponse(
        deleted_count=deleted_count,
        message=f"Удалено просроченных токенов: {deleted_count}"
    )

@router.get("/", response_model=List[RefreshTokenResponse])
async def get_tokens(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    user_id: Optional[int] = Query(None, description="Фильтр по ID пользователя"),
    is_revoked: Optional[bool] = Query(None, description="Фильтр по статусу отзыва"),
    db: Session = Depends(get_db)
):
    """Получить список токенов с пагинацией и фильтрами"""
    tokens, total = RefreshTokenCRUD.get_tokens_paginated(
        db, page, limit, user_id, is_revoked
    )
    return tokens 