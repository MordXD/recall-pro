import httpx
import os
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class DatabaseClient:
    """HTTP клиент для взаимодействия с Database Service"""
    
    def __init__(self):
        self.base_url = os.getenv("DATABASE_SERVICE_URL", "http://database-service:8002")
        self.timeout = 30.0
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[Any, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[Any, Any]:
        """Выполнить HTTP запрос к Database Service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, params=params)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, params=params)
                else:
                    raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database Service недоступен (timeout)"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Не удается подключиться к Database Service"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                error_detail = e.response.json().get("detail", "Ошибка валидации данных")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_detail
                )
            elif e.response.status_code == 500:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Внутренняя ошибка Database Service"
                )
            else:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Ошибка Database Service: {e.response.text}"
                )
    
    # Методы для работы с пользователями
    async def create_user(self, username: str, email: str, password_hash: str) -> Optional[Dict[Any, Any]]:
        """Создать пользователя"""
        data = {
            "username": username,
            "email": email,
            "password_hash": password_hash
        }
        return await self._make_request("POST", "/api/v1/users/", data)
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[Any, Any]]:
        """Получить пользователя по ID"""
        return await self._make_request("GET", f"/api/v1/users/{user_id}")
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[Any, Any]]:
        """Получить пользователя по имени пользователя"""
        return await self._make_request("GET", f"/api/v1/users/search/by-username/{username}")
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[Any, Any]]:
        """Получить пользователя по email"""
        return await self._make_request("GET", f"/api/v1/users/search/by-email/{email}")
    
    async def update_user(self, user_id: int, **kwargs) -> Optional[Dict[Any, Any]]:
        """Обновить пользователя"""
        data = {k: v for k, v in kwargs.items() if v is not None}
        if not data:
            return None
        return await self._make_request("PUT", f"/api/v1/users/{user_id}", data)
    
    async def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        result = await self._make_request("DELETE", f"/api/v1/users/{user_id}")
        return result is not None
    
    # Методы для работы с токенами
    async def create_refresh_token(
        self, 
        token_hash: str, 
        user_id: int, 
        expires_at: datetime
    ) -> Optional[Dict[Any, Any]]:
        """Создать refresh токен"""
        data = {
            "token_hash": token_hash,
            "user_id": user_id,
            "expires_at": expires_at.isoformat()
        }
        return await self._make_request("POST", "/api/v1/tokens/", data)
    
    async def verify_refresh_token(self, token_hash: str) -> Optional[Dict[Any, Any]]:
        """Проверить refresh токен"""
        return await self._make_request("GET", f"/api/v1/tokens/verify/{token_hash}")
    
    async def revoke_refresh_token(self, token_hash: str) -> bool:
        """Отозвать refresh токен"""
        data = {"token_hash": token_hash}
        result = await self._make_request("POST", "/api/v1/tokens/revoke", data)
        return result is not None
    
    async def revoke_user_tokens(self, user_id: int) -> bool:
        """Отозвать все токены пользователя"""
        result = await self._make_request("POST", f"/api/v1/tokens/revoke-user/{user_id}")
        return result is not None
    
    async def cleanup_expired_tokens(self) -> Dict[Any, Any]:
        """Очистить просроченные токены"""
        return await self._make_request("POST", "/api/v1/tokens/cleanup")


# Singleton instance
database_client = DatabaseClient()

def get_database_client() -> DatabaseClient:
    """Dependency для получения клиента базы данных"""
    return database_client 