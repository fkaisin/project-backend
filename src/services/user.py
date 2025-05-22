from fastapi import HTTPException, status
from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import User
from src.schemes.user import UserUpdate
from src.utils.dbcheck import (
    check_username_or_email_exists,
)
from src.utils.security import hash_password


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(self):
        statement = select(User)
        result = await self.session.exec(statement)
        return result.all()

    async def create_user(self, user):
        user_check = await check_username_or_email_exists(
            username=user.username, email=user.email, session=self.session
        )
        if user_check:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=user_check,
            )

        hashed_password = hash_password(user.password)
        extra_data = {'hashed_password': hashed_password}
        db_user = User.model_validate(user, update=extra_data)
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_user(self, username: str):
        user = await self.session.get(User, username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found.',
            )
        return user

    async def update_user(self, username: str, user: UserUpdate):
        db_user = await self.session.get(User, username)

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found.',
            )

        user_data = user.model_dump(exclude_unset=True)

        if user_data.get('username') or user_data.get('email'):
            user_check = await check_username_or_email_exists(
                username=user_data.get('username'),
                email=user_data.get('email'),
                session=self.session,
            )
            if user_check:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=user_check,
                )

        if user_data.get('password'):
            user_data['hashed_password'] = hash_password(user_data['password'])
            del user_data['password']
        db_user.sqlmodel_update(user_data)

        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def delete_user(self, username: str):
        user = await self.session.get(User, username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found.',
            )
        await self.session.delete(user)
        await self.session.commit()
