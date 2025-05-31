from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import math

from database import get_db
from crud import UserCRUD
from schemas import (
    UserCreateRequest, UserResponse, UserUpdateRequest,
    UserSearchRequest, UserListResponse, SuccessResponse,
    PaginationParams
)

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """Создать нового пользователя"""
    try:
        # Проверяем уникальность username и email
        existing_user = UserCRUD.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )
        
        existing_email = UserCRUD.get_user_by_email(db, user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        user = UserCRUD.create_user(db, user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания пользователя: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получить пользователя по ID"""
    user = UserCRUD.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.get("/search/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    db: Session = Depends(get_db)
):
    """Получить пользователя по имени пользователя"""
    user = UserCRUD.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.get("/search/by-email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """Получить пользователя по email"""
    user = UserCRUD.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    search: Optional[str] = Query(None, description="Поиск по имени пользователя или email"),
    db: Session = Depends(get_db)
):
    """Получить список пользователей с пагинацией"""
    users, total = UserCRUD.get_users_paginated(db, page, limit, search)
    total_pages = math.ceil(total / limit)
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    db: Session = Depends(get_db)
):
    """Обновить пользователя"""
    user = UserCRUD.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Удалить пользователя"""
    success = UserCRUD.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return SuccessResponse(message="Пользователь успешно удален") 