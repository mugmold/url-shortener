from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.api.dependencies import get_current_user
from app.core.security import get_password_hash
from app.models.url import URL
from app.schemas.url import PaginatedURLResponse

from app.core.limiter import limiter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    """
    get current logged in user profile
    """
    return current_user


@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def update_profile(
    request: Request,
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


@router.get("/me/urls", response_model=PaginatedURLResponse, status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def get_my_urls(
    request: Request,
    skip: int = Query(default=0, ge=0, description="how many records to skip"),
    limit: int = Query(
        default=10, ge=1, le=100, description="how many records to return (max 100)"
    ),
    current_user: User = Depends(get_current_user)
):
    # count total urls for the frontend to calculate total pages
    total = await URL.find({"owner.$id": current_user.id}).count()

    # fetch the specific chunk of data
    urls = await URL.find({"owner.$id": current_user.id}).skip(skip).limit(limit).to_list()

    return PaginatedURLResponse(
        items=urls,
        total=total,
        skip=skip,
        limit=limit
    )
