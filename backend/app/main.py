from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pymongo import AsyncMongoClient
from beanie import init_beanie

from app.models.url import URL
from app.models.user import User
from app.models.counter import Counter
from app.core.config import settings
from app.api.routers import auth, urls, users

from app.core.limiter import limiter
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
