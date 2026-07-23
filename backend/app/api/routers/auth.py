from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt

from app.models.user import User
from app.schemas.user import UserCreate, UserCreateResponse
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.limiter import limiter
from beanie import PydanticObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(request: Request, user_in: UserCreate):
    if user_in.password != user_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    existing_user = await User.find_one(
        {
            "$or": [
                {
                    "username": user_in.username
                },
                {
                    "email": user_in.email
                }
            ]
        }
    )

    if existing_user:
        if existing_user.username == user_in.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    hashed_password = get_password_hash(user_in.password)

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=hashed_password
    )

    await new_user.insert()

    return new_user


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    login_identifier = form_data.username.lower()

    user = await User.find_one(
        {
            "$or": [
                {
                    "username": login_identifier
                },
                {
                    "email": login_identifier
                }
            ]
        }
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def refresh_token(request: Request, body: RefreshTokenRequest):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            body.refresh_token, settings.SECRET_KEY, algorithms=[
                settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        # verify it is actually a refresh token
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type, please provide a valid refresh token"
            )

        if user_id is None:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    # verify user still exists in database
    user = await User.get(PydanticObjectId(user_id))
    if not user:
        raise credentials_exception

    # refresh both "refresh token" and "access token"
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
