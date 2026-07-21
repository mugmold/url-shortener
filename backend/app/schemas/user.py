from pydantic import BaseModel, model_validator, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)

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
