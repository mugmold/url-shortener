from pydantic import BaseModel, model_validator, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=20)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    confirm_password: Optional[str] = None

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
