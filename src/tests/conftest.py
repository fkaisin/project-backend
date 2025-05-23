import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.pool import StaticPool

from src import app
from src.db.main import get_session
from src.db.models import User
from src.schemes.user import UserCreate, UserPublic, UserUpdate

TEST_USERNAME = 'testUser'
TEST_EMAIL = 'test@mail.com'
TEST_PASSWORD = 'testPassword'


@pytest_asyncio.fixture(name='session')
async def session_fixture():
	engine = create_async_engine(
		'sqlite+aiosqlite://',
		connect_args={'check_same_thread': False},
		poolclass=StaticPool,
	)
	async with engine.begin() as conn:
		await conn.run_sync(SQLModel.metadata.create_all)
	async_session = AsyncSession(engine)
	yield async_session
	await async_session.close()


@pytest_asyncio.fixture(name='client')
async def client_fixture(session: Session):
	def get_session_override():
		return session

	app.dependency_overrides[get_session] = get_session_override

	async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
		yield client

	app.dependency_overrides.clear()


@pytest_asyncio.fixture(name='initial_user')
async def initial_user_fixture(client: AsyncClient):
	await client.post(
		'/auth/register',
		json={
			'username': TEST_USERNAME,
			'email': TEST_EMAIL,
			'password': TEST_PASSWORD,
		},
	)
	yield
