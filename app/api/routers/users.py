from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.api.dependencies import get_current_user
from app.core.security import get_password_hash
from typing import List
from app.models.url import URL
from app.schemas.url import URLListResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged in user profile
    """
    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    if user_update.username:
        existing_username = await User.find_one({"username": user_update.username})
        if existing_username and existing_username.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    if user_update.email:
        existing_email = await User.find_one({"email": user_update.email})
        if existing_email and existing_email.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    if user_update.password:
        current_user.password = get_password_hash(user_update.password)

    await current_user.save()

    return current_user


@router.get("/me/urls", response_model=List[URLListResponse], status_code=status.HTTP_200_OK)
async def get_my_urls(current_user: User = Depends(get_current_user)):
    urls = await URL.find({"owner.$id": current_user.id}).to_list()
    return urls
