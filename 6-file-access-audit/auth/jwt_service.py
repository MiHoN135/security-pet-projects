"""Выпуск и проверка JWT-токенов (stateless-аутентификация)."""
import os
from datetime import datetime, timedelta, timezone

import jwt

# В курсовой ключ был захардкожен; здесь берём из окружения, иначе тестовый
SECRET_KEY = os.environ.get("JWT_SECRET", "dev-only-secret-key-change-me-32bytes!")
ALGORITHM = "HS256"


def create_token(username: str, role: str, expires_sec: int = 3600) -> str:
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_sec),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {e}")
