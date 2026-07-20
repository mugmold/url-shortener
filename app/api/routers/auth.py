from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.models.user import User
from app.schemas.user import UserCreate, UserCreateResponse
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    hashed_password = get_password_hash(user_in.password)

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=hashed_password
    )

    await new_user.insert()

    return new_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), status_code=status.HTTP_200_OK):
    user = await User.find_one(
        {
            "$or": [
                {
                    "username": form_data.username
                },
                {
                    "email": form_data.username
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

    return {"access_token": access_token, "token_type": "bearer"}
