from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User
from src.schemes.user import UserPublic, UserUpdate
from src.services.user import UserService

router = APIRouter(
    prefix='/users',
    tags=['User'],
)


@router.get('/', response_model=list[UserPublic])
async def read_users(session: Annotated[AsyncSession, Depends(get_session)]):
    return await UserService(session).get_all_users()


@router.get('/{username}', status_code=status.HTTP_200_OK, response_model=UserPublic)
async def read_user(
    username: str, session: Annotated[AsyncSession, Depends(get_session)]
):
    return await UserService(session).get_user(username)


@router.patch('/{username}', status_code=status.HTTP_200_OK, response_model=UserPublic)
async def update_user(
    username: str,
    user: UserUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await UserService(session).update_user(username, user)


@router.delete('/{username}', status_code=status.HTTP_200_OK)
async def delete_user(
    username: str, session: Annotated[AsyncSession, Depends(get_session)]
):
    await UserService(session).delete_user(username)
    return {'detail': f'User {username} deleted successfully.'}
