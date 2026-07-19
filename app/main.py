from fastapi import FastAPI
from app.models.url import URL
from app.models.user import User
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from beanie import init_beanie
from dotenv import load_dotenv
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

    client = AsyncMongoClient(MONGO_URL)
    db = client.my_database

    await init_beanie(database=db, document_models=[User, URL])

    print("database connected!")
    yield

    client.close()

    print("database connection closed!")

app = FastAPI(lifespan=lifespan)


@app.get('/')
async def root():
    return {
        'message': 'Hello World!'
    }
