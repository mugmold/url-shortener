from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.api.dependencies import get_current_user
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    if user_update.username:
        existing_username = await User.find_one({"username": user_update.username})
        if existing_username and existing_username.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
        current_user.username = user_update.username

    if user_update.email:
        existing_email = await User.find_one({"email": user_update.email})
        if existing_email and existing_email.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        current_user.email = user_update.email

    if user_update.password:
        current_user.password = get_password_hash(user_update.password)

    await current_user.save()

    return current_user
