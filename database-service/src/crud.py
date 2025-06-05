from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from src.models import User, RefreshToken
from src.schemas import UserCreateRequest, UserUpdateRequest

class UserCRUD:
    """CRUD операции для пользователей"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Получить пользователя по имени пользователя"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreateRequest) -> User:
        """Создать нового пользователя"""
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=user_data.password_hash
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdateRequest) -> Optional[User]:
        """Обновить пользователя"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Удалить пользователя"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def get_users_paginated(
        db: Session, 
        page: int = 1, 
        limit: int = 10,
        search_term: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """Получить пользователей с пагинацией"""
        query = db.query(User)
        
        if search_term:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search_term}%"),
                    User.email.ilike(f"%{search_term}%")
                )
            )
        
        total = query.count()
        users = query.offset((page - 1) * limit).limit(limit).all()
        
        return users, total

class RefreshTokenCRUD:
    """CRUD операции для refresh токенов"""
    
    @staticmethod
    def create_refresh_token(
        db: Session, 
        token_hash: str, 
        user_id: int, 
        expires_at: datetime
    ) -> RefreshToken:
        """Создать новый refresh токен"""
        db_token = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    
    @staticmethod
    def get_refresh_token_by_hash(db: Session, token_hash: str) -> Optional[RefreshToken]:
        """Получить refresh токен по хешу"""
        return db.query(RefreshToken).filter(
            and_(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        ).first()
    
    @staticmethod
    def get_user_tokens(db: Session, user_id: int) -> List[RefreshToken]:
        """Получить все токены пользователя"""
        return db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()
    
    @staticmethod
    def revoke_refresh_token(db: Session, token_hash: str) -> bool:
        """Отозвать refresh токен"""
        token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        if not token:
            return False
        
        token.is_revoked = True
        db.commit()
        return True
    
    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int) -> int:
        """Отозвать все токены пользователя"""
        count = db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        ).update({"is_revoked": True})
        db.commit()
        return count
    
    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Удалить просроченные токены"""
        count = db.query(RefreshToken).filter(
            RefreshToken.expires_at <= datetime.now(timezone.utc)
        ).delete()
        db.commit()
        return count
    
    @staticmethod
    def get_tokens_paginated(
        db: Session, 
        page: int = 1, 
        limit: int = 10,
        user_id: Optional[int] = None,
        is_revoked: Optional[bool] = None
    ) -> Tuple[List[RefreshToken], int]:
        """Получить токены с пагинацией"""
        query = db.query(RefreshToken)
        
        if user_id is not None:
            query = query.filter(RefreshToken.user_id == user_id)
        
        if is_revoked is not None:
            query = query.filter(RefreshToken.is_revoked == is_revoked)
        
        total = query.count()
        tokens = query.offset((page - 1) * limit).limit(limit).all()
        
        return tokens, total 