from pydantic import BaseModel, model_validator, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not (self.username or self.email or self.password):
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
