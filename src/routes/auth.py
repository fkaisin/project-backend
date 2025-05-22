from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.schemes.auth import TokenResponse
from src.schemes.user import UserCreate, UserPublic
from src.services.auth import AuthService, get_current_user
from src.services.user import UserService

router = APIRouter(
    prefix='/auth',
    tags=['Authentication'],
)


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic,
)
async def create_user(
    user: UserCreate, session: Annotated[AsyncSession, Depends(get_session)]
):
    return await UserService(session).create_user(user)


@router.post(
    '/login', status_code=status.HTTP_202_ACCEPTED, response_model=TokenResponse
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    token = await AuthService(session).login(form_data)
    return token


@router.get('/me')
async def read_user_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
