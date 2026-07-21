from fastapi import FastAPI
from app.models.url import URL
from app.models.user import User
from app.models.counter import Counter
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from beanie import init_beanie
from app.core.config import settings
from app.api.routers import auth, urls, users
from fastapi.middleware.cors import CORSMiddleware

from app.core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncMongoClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB_NAME]

    await init_beanie(database=db, document_models=[User, URL, Counter])
    await Counter.init_counter("url_counter")

    print("database connected!")
    yield

    client.close()

    print("database connection closed!")

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(urls.router)
