from pydantic import BaseModel, HttpUrl, Field, model_validator
from typing import Optional
from datetime import datetime


class URLCreateRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(None, min_length=5, max_length=20)
    expired_at: Optional[datetime] = None


class URLCreateResponse(BaseModel):
    shortened_url: HttpUrl
    created_at: datetime


class URLUpdateRequest(BaseModel):
    new_url: Optional[HttpUrl] = None
    new_custom_alias: Optional[str] = Field(None, min_length=5, max_length=20)
    expired_at: Optional[datetime] = None

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not (self.new_url or self.new_custom_alias or self.expired_at is not None):
            raise ValueError("At least one field must be updated")
        return self


class URLUpdateResponse(BaseModel):
    new_shortened_url: HttpUrl


class URLInspectResponse(BaseModel):
    original_url: HttpUrl


class URLListResponse(BaseModel):
    short_code: str
    original_url: HttpUrl
    clicks_count: int
    created_at: datetime
