from beanie import Document, Indexed
from datetime import datetime, timezone
from typing import Optional, Annotated
from pydantic import Field


class URL(Document):
    short_code: Annotated[str, Indexed(unique=True)]
    original_url: str
    owner_id: Annotated[Optional[str], Indexed()] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expired_at: Optional[datetime] = None
    clicks_count: int = 0

    class Settings:
        name = 'urls'
