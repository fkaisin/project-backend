from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db.main import init_db
from src.routes.auth import router as auth_router
from src.routes.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('=' * 50, ' Starting up... ', '=' * 50)
    await init_db()
    yield
    print('=' * 50, ' Shutting down... ', '=' * 50)


app = FastAPI(
    title='FastAPI Example',
    description='A simple FastAPI example with lifespan context manager',
    version='0.1.0',
    lifespan=lifespan,
)


app.include_router(user_router)
app.include_router(auth_router)
