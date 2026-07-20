from fastapi import FastAPI
from app.models.url import URL
from app.models.user import User
from app.models.counter import Counter
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from beanie import init_beanie
from app.core.config import settings
from app.api.routers import auth, urls, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncMongoClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB_NAME]

    await init_beanie(database=db, document_models=[User, URL, Counter])

    print("database connected!")
    yield

    client.close()

    print("database connection closed!")

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(users.router)


@app.get('/')
async def root():
    return {
        'message': 'Hello World!'
    }
