import asyncio
from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from beanie import init_beanie
import redis.exceptions

from app.models.url import URL
from app.models.counter import Counter
from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis import redis_client
from app.api.routers import auth, urls, users

from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded


async def sync_clicks_to_mongodb():
    """background worker that flushes Redis clicks to MongoDB every 5 seconds."""
    while True:
        await asyncio.sleep(5)
        try:
            # atomically rename the key so incoming clicks write to a fresh buffer
            # this prevents losing clicks that happen during the flush process
            await redis_client.rename("url_clicks_buffer", "url_clicks_processing")

            # grab all the clicks we isolated
            buffered_clicks = await redis_client.hgetall("url_clicks_processing")

            if buffered_clicks:
                # flush them to MongoDB in the background
                for short_code, count in buffered_clicks.items():
                    url_doc = await URL.find_one({"short_code": short_code})
                    if url_doc:
                        await url_doc.update({"$inc": {"clicks_count": int(count)}})

                # delete the processing buffer now that we are done
                await redis_client.delete("url_clicks_processing")

        except redis.exceptions.ResponseError:
            # this happens if "url_clicks_buffer" doesn't exist yet (no clicks in the last 5 seconds)
            pass
        except Exception as e:
            print(f"Error syncing clicks: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("PostgreSQL connected!")

    client = AsyncMongoClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB_NAME]
    await init_beanie(database=db, document_models=[URL, Counter])
    await Counter.init_counter("url_counter")
    print("MongoDB connected!")

    # start the background sync loop
    sync_task = asyncio.create_task(sync_clicks_to_mongodb())

    yield

    # cleanup
    sync_task.cancel()
    await redis_client.close()
    client.close()
    await engine.dispose()

    print("Database & Cache connections closed!")

app = FastAPI(
    lifespan=lifespan,
    title="URL Shortener API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests. Please try again later"}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # grab the very first error from the Pydantic array
    error = exc.errors()[0]

    # "loc" tells us which field failed (e.g., ["body", "custom_alias"])
    field = str(error.get("loc", ["unknown"])[-1])
    error_type = error.get("type", "")

    if field in ["custom_alias", "new_custom_alias"]:
        if "too_short" in error_type:
            detail = "Your custom alias must be at least 5 characters long"
        elif "too_long" in error_type:
            detail = "Your custom alias cannot exceed 20 characters"
        else:
            detail = "Custom alias can only contain letters and numbers"

    elif field == "username":
        if "too_short" in error_type:
            detail = "Your username must be at least 3 characters long"
        elif "too_long" in error_type:
            detail = "Your username cannot exceed 20 characters"
        else:
            detail = "Invalid username format"

    elif field in ["original_url", "new_url"] and "url" in error_type:
        detail = "Please enter a valid URL (e.g., https://example.com)"

    elif field == "password" and "too_short" in error_type:
        detail = "Your password must be at least 8 characters long"

    else:
        detail = error.get("msg", "Invalid input")

        if detail.startswith("Value error, "):
            detail = detail.replace("Value error, ", "")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detail}
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(urls.router)
