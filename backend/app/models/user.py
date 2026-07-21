from beanie import Document, Indexed
from datetime import datetime, timezone
from typing import Annotated
from pydantic import Field


class User(Document):
    username: Annotated[str, Indexed(unique=True)]
    email: Annotated[str, Indexed(unique=True)]
    password: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "users"
