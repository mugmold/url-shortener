from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.models.user import User
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class TokenUser(BaseModel):
    id: str


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> TokenUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

        return TokenUser(id=user_id)

    except jwt.PyJWTError:
        raise credentials_exception


async def get_current_user(
    token_user: TokenUser = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> User:
    result = await db.execute(select(User).where(User.id == token_user.id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
