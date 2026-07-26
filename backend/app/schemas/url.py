from pydantic import BaseModel, HttpUrl, Field, model_validator, field_validator
from typing import Optional, List
from datetime import datetime

CUSTOM_ALIAS_REGEX = r"^[a-zA-Z0-9]+$"

RESTRICTED_ALIASES = {
    "login", "register", "dashboard", "settings",
    "api", "docs", "openapi", "auth", "users", "urls"
}


class URLCreateRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(
        None,
        min_length=5,
        max_length=20,
        pattern=CUSTOM_ALIAS_REGEX,
        description="Custom alias can only contain letters and numbers"
    )
    expired_at: Optional[datetime] = None

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() in RESTRICTED_ALIASES:
            raise ValueError(
                "This alias is a reserved system word and cannot be used"
            )
        return v


class URLCreateResponse(BaseModel):
    shortened_url: HttpUrl
    created_at: datetime


class URLUpdateRequest(BaseModel):
    new_url: Optional[HttpUrl] = None
    new_custom_alias: Optional[str] = Field(
        None,
        min_length=5,
        max_length=20,
        pattern=CUSTOM_ALIAS_REGEX,
        description="Custom alias can only contain letters and numbers"
    )
    expired_at: Optional[datetime] = None

    @field_validator("new_custom_alias")
    @classmethod
    def validate_new_custom_alias(cls, v: Optional[str]) -> Optional[str]:
        if v and v.lower() in RESTRICTED_ALIASES:
            raise ValueError(
                "This alias is a reserved system word and cannot be used"
            )
        return v

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
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
    expired_at: Optional[datetime] = None


class PaginatedURLResponse(BaseModel):
    items: List[URLListResponse]
    total: int
    skip: int
    limit: int
