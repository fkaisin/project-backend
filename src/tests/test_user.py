import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.db.models import User
from src.tests.conftest import TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME
from src.utils.security import verify_password


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )

    data = response.json()

    assert response.status_code == 201
    assert data['username'] == TEST_USERNAME
    assert verify_password(TEST_PASSWORD, data['hashed_password'])
    assert data['hashed_password'] != TEST_PASSWORD
    assert data['email'] == TEST_EMAIL
    assert isinstance(uuid.UUID(data['uid']), uuid.UUID)
    assert isinstance(datetime.fromisoformat(data['created_at']), datetime)
    assert isinstance(datetime.fromisoformat(data['updated_at']), datetime)


@pytest.mark.asyncio
async def test_create_user_with_existing_username(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )
    response = await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': 'another@mail.com',
            'password': TEST_PASSWORD,
        },
    )

    data = response.json()

    assert response.status_code == 403
    assert data['detail'] == 'Username already exists.'


@pytest.mark.asyncio
async def test_create_user_with_existing_email(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )
    response = await client.post(
        '/users/',
        json={
            'username': 'AnotherUserName',
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )

    data = response.json()

    assert response.status_code == 403
    assert data['detail'] == 'Email already exists.'


@pytest.mark.asyncio
async def test_get_all_users_empty(client: AsyncClient):
    response = await client.get('/users/')

    data = response.json()

    assert response.status_code == 200
    assert data == []


@pytest.mark.asyncio
async def test_get_all_users_success(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME + 'X',
            'email': 'X' + TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )

    response = await client.get('/users/')

    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_user_success(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )
    response = await client.get(f'/users/{TEST_USERNAME}')

    data = response.json()

    assert response.status_code == 200
    assert data['username'] == TEST_USERNAME


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    response = await client.get(f'/users/{TEST_USERNAME}')

    data = response.json()

    assert response.status_code == 404
    assert data['detail'] == 'User not found.'


@pytest.mark.asyncio
async def test_delete_user_success(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )
    response = await client.delete(f'/users/{TEST_USERNAME}')

    data = response.json()

    assert response.status_code == 200
    assert data['detail'] == f'User {TEST_USERNAME} deleted successfully.'


@pytest.mark.asyncio
async def test_delete_user_not_found(client: AsyncClient):
    response = await client.delete(f'/users/{TEST_USERNAME}')

    data = response.json()

    assert response.status_code == 404
    assert data['detail'] == 'User not found.'


@pytest.mark.asyncio
async def test_update_user_success(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )

    response = await client.patch(
        f'/users/{TEST_USERNAME}',
        json={
            'username': 'AnotherUserName',
            'email': 'AnotherEmail',
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data['username'] == 'AnotherUserName'
    assert data['email'] == 'AnotherEmail'


@pytest.mark.asyncio
async def test_update_user_password_success(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )

    response = await client.patch(
        f'/users/{TEST_USERNAME}',
        json={
            'password': 'AnotherPassword',
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data['username'] == TEST_USERNAME
    assert data['email'] == TEST_EMAIL
    assert verify_password('AnotherPassword', data['hashed_password'])


@pytest.mark.asyncio
async def test_update_user_not_found(client: AsyncClient):
    response = await client.patch(
        f'/users/{TEST_USERNAME}',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )

    data = response.json()

    assert response.status_code == 404
    assert data['detail'] == 'User not found.'


@pytest.mark.asyncio
async def test_update_user_existing_username(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )
    await client.post(
        '/users/',
        json={
            'username': 'NewUser',
            'email': 'NewEmail',
            'password': TEST_PASSWORD,
        },
    )

    response = await client.patch(
        f'/users/{TEST_USERNAME}',
        json={
            'username': 'NewUser',
        },
    )

    data = response.json()

    assert response.status_code == 403
    assert data['detail'] == 'Username already exists.'


@pytest.mark.asyncio
async def test_update_user_existing_email(client: AsyncClient):
    await client.post(
        '/users/',
        json={
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD,
        },
    )
    await client.post(
        '/users/',
        json={
            'username': 'NewUser',
            'email': 'NewEmail',
            'password': TEST_PASSWORD,
        },
    )

    response = await client.patch(
        f'/users/{TEST_USERNAME}',
        json={
            'email': 'NewEmail',
        },
    )

    data = response.json()

    assert response.status_code == 403
    assert data['detail'] == 'Email already exists.'
