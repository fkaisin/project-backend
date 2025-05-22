import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import settings
from src.db.main import get_session
from src.db.models import User
from src.schemes.auth import TokenResponse
from src.utils.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def login(self, form_data: OAuth2PasswordRequestForm):
        user_db = await self.session.get(User, form_data.username)

        if not user_db or not verify_password(
            form_data.password, user_db.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid username or password.',
            )

        access_token = create_access_token(data={'sub': str(user_db.uid)})
        refresh_token = create_refresh_token(data={'sub': str(user_db.uid)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
        )


# Dépendance utilisée dans les routes protégées
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid token.',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        # Transforme le token type str en type UUID
        user_uid = uuid.UUID(payload.get('sub'))

        if user_uid is None:
            raise invalid_token_exception

        statement = select(User).where(User.uid == user_uid)
        result = await session.exec(statement)
        user_db = result.first()

        if not user_db:
            raise invalid_token_exception

        return user_db

    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired.',
            headers={'WWW-Authenticate': 'Bearer'},
        ) from exc
    except InvalidTokenError as exc:
        raise invalid_token_exception from exc
