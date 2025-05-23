import uuid
from datetime import UTC, datetime, timedelta, timezone

import jwt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import settings
from src.db.models import User
from src.tests.conftest import TEST_EMAIL, TEST_PASSWORD, TEST_USERNAME
from src.utils.security import create_access_token, create_refresh_token, verify_password


@pytest.mark.asyncio
async def test_login_successful(client: AsyncClient, initial_user):
	response = await client.post(
		'/auth/login',
		data={
			'username': TEST_USERNAME,
			'password': TEST_PASSWORD,
		},
	)

	data = response.json()
	at_payload = jwt.decode(
		data['access_token'], key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
	)
	refresh_token = response.cookies.get('refresh_token')
	rt_payload = jwt.decode(
		refresh_token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
	)

	# On récupère le uid dans la DB
	user = await client.get(f'users/{TEST_USERNAME}')
	user_uid_db = user.json()['uid']

	assert response.status_code == 202
	assert data['access_token'] is not None
	assert data['token_type'] == 'bearer'
	assert refresh_token is not None
	assert at_payload.get('sub') == user_uid_db
	assert rt_payload.get('sub') == user_uid_db


@pytest.mark.asyncio
async def test_login_wrong_user(client: AsyncClient, initial_user):
	response = await client.post(
		'/auth/login',
		data={
			'username': 'AnotherUser',
			'password': TEST_PASSWORD,
		},
	)

	data = response.json()

	assert response.status_code == 401
	assert data['detail'] == 'Invalid username or password.'


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, initial_user):
	response = await client.post(
		'/auth/login',
		data={
			'username': TEST_USERNAME,
			'password': 'WrongPassword',
		},
	)

	data = response.json()

	assert response.status_code == 401
	assert data['detail'] == 'Invalid username or password.'


@pytest.mark.asyncio
async def test_access_protected_route_with_valid_token(client: AsyncClient, initial_user):
	# 1. Login
	response = await client.post(
		'/auth/login',
		data={
			'username': TEST_USERNAME,
			'password': TEST_PASSWORD,
		},
	)
	assert response.status_code == 202
	access_token = response.json()['access_token']

	# 2. Construire les headers avec Authorization
	headers = {'Authorization': f'Bearer {access_token}'}

	# 3. Appel à une route protégée
	protected_response = await client.get('/auth/me', headers=headers)

	# 4. Vérifications
	assert protected_response.status_code == 202
	assert protected_response.json()['username'] == TEST_USERNAME


@pytest.mark.asyncio
async def test_access_protected_route_with_not_valid_token(client: AsyncClient, initial_user):
	headers = {'Authorization': 'Bearer random0access0token'}
	protected_response = await client.get('/auth/me', headers=headers)

	assert protected_response.status_code == 401
	assert protected_response.json()['detail'] == 'Invalid token.'
	assert protected_response.headers['WWW-Authenticate'] == 'Bearer'


@pytest.mark.asyncio
async def test_access_protected_route_with_expired_token(client: AsyncClient, initial_user):
	# 1. On récupère le uid dans la DB
	user = await client.get(f'users/{TEST_USERNAME}')
	user_uid_db = user.json()['uid']

	# 2. On crée un access_token expiré
	expired_access_token = create_access_token(
		data={'sub': user_uid_db}, expires_delta=timedelta(seconds=-1)
	)

	# 2. Construire les headers avec Authorization
	headers = {'Authorization': f'Bearer {expired_access_token}'}

	# 3. Appel à une route protégée
	protected_response = await client.get('/auth/me', headers=headers)

	# 4. Vérifications
	assert protected_response.status_code == 401
	assert protected_response.json()['detail'] == 'Token expired.'
	assert protected_response.headers['WWW-Authenticate'] == 'Bearer'


@pytest.mark.asyncio
async def test_access_protected_route_with_no_token(client: AsyncClient, initial_user):
	protected_response = await client.get('/auth/me')

	assert protected_response.status_code == 401
	assert protected_response.json()['detail'] == 'Not authenticated'
	assert protected_response.headers['WWW-Authenticate'] == 'Bearer'


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, initial_user):
	# Premièrement, on récupère un refresh token en se loguant
	login_response = await client.post(
		'/auth/login',
		data={'username': TEST_USERNAME, 'password': TEST_PASSWORD},
	)
	assert login_response.status_code == 202
	refresh_token = login_response.cookies.get('refresh_token')
	assert refresh_token is not None

	# Ensuite, on appelle /auth/refresh avec le cookie refresh_token
	client.cookies.set('refresh_token', refresh_token)
	refresh_response = await client.post('/auth/refresh')

	assert refresh_response.status_code == 200
	data = refresh_response.json()
	assert 'access_token' in data
	assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_refresh_token_missing_cookie(client: AsyncClient):
	# Appel sans cookie refresh_token
	response = await client.post('/auth/refresh')

	assert response.status_code == 404
	assert response.json()['detail'] == 'Refresh token not found.'


@pytest.mark.asyncio
async def test_refresh_token_invalid_cookie(client: AsyncClient):
	# Envoi d'un cookie invalide
	client.cookies.set('refresh_token', 'invalidToken')
	response = await client.post('/auth/refresh')

	assert response.status_code == 401
	assert response.json()['detail'] == 'Invalid token signature. Please login.'


@pytest.mark.asyncio
async def test_refresh_token_expired_cookie(client: AsyncClient, initial_user):
	# 1. On récupère le uid dans la DB
	user = await client.get(f'users/{TEST_USERNAME}')
	user_uid_db = user.json()['uid']

	# 2. On crée un refresh_token expiré
	expired_refresh_token = create_refresh_token(
		data={'sub': user_uid_db}, expires_delta=timedelta(seconds=-1)
	)
	# Envoi d'un cookie expiré
	client.cookies.set('refresh_token', expired_refresh_token)
	response = await client.post('/auth/refresh')

	assert response.status_code == 401
	assert response.json()['detail'] == 'Expired token signature. Please login.'


@pytest.mark.asyncio
async def test_refresh_token_user_not_found(client: AsyncClient, initial_user):
	invalid_refresh_token = create_refresh_token(data={'sub': str(uuid.uuid4())})
	client.cookies.set('refresh_token', invalid_refresh_token)
	response = await client.post('/auth/refresh')

	assert response.status_code == 404
	assert response.json()['detail'] == 'Refresh token user ID not found.'


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient):
	response = await client.post('/auth/logout')
	assert response.status_code == 200
	assert response.json()['detail'] == 'Logged out successfully.'
