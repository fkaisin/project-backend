from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db.main import init_db
from src.routes.auth import router as auth_router
from src.routes.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('=' * 50, ' Starting up... ', '=' * 50)
    await init_db()
    yield
    print('=' * 50, ' Shutting down... ', '=' * 50)


app = FastAPI(lifespan=lifespan)

origins = [
    'http://localhost:5174',
    # Add more origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(user_router)
app.include_router(auth_router)
