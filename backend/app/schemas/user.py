from pydantic import BaseModel, model_validator, field_validator, EmailStr, Field
from typing import Optional
from datetime import datetime

USERNAME_PATTERN = r"^[a-zA-Z0-9_]+$"


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=USERNAME_PATTERN,
        description="Only letters, numbers, and underscores are allowed."
    )
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("username", "email")
    @classmethod
    def to_lowercase(cls, v: str) -> str:
        if isinstance(v, str):
            return v.lower()
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=20,
        pattern=USERNAME_PATTERN
    )
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    confirm_password: Optional[str] = None

    @field_validator("username", "email")
    @classmethod
    def to_lowercase(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return v.lower()
        return v

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not (self.username or self.email or self.password or self.confirm_password):
            raise ValueError("At least one field must be updated")
        return self


class UserResponse(BaseModel):
    username: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }


class UserCreateResponse(UserResponse):
    created_at: datetime
