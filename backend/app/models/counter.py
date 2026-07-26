from beanie import Document, Indexed
from typing import Annotated
from pydantic import Field


class Counter(Document):
    name: Annotated[str, Indexed(
        unique=True)
    ] = Field(..., description="counter name")
    seq: int = 0

    class Settings:
        name = "counters"

    @classmethod
    async def init_counter(cls, counter_name: str):
        exists = await cls.find_one({"name": counter_name})
        if not exists:
            try:
                await cls(name=counter_name, seq=0).insert()
            except Exception:
                pass
