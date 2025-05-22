from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.config import settings


def hash_password(password: str) -> str:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=settings.JWT_ACCESS_EXPIRATION_IN_MIN),
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp': expire})
    return jwt.encode(
        payload=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    data: dict,
    expires_delta: timedelta = timedelta(days=settings.JWT_REFRESH_EXPIRATION_IN_DAYS),
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp': expire})
    return jwt.encode(
        payload=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
