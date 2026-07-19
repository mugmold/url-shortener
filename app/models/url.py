from beanie import Document, Indexed, Link
from datetime import datetime, timezone
from typing import Optional, Annotated
from pydantic import Field
from app.models.user import User


class URL(Document):
    short_code: Annotated[str, Indexed(unique=True)]
    original_url: str
    owner: Optional[Link[User]] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expired_at: Optional[datetime] = None
    clicks_count: int = 0

    class Settings:
        name = 'urls'

        # define additional indexes based on owner (User) id
        indexes = [
            'owner.$id'
        ]
