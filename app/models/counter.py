from beanie import Document, Indexed, UpdateResponse
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

    @classmethod
    async def get_next_sequence(cls, counter_name: str) -> int:
        doc = await cls.find_one({"name": counter_name}).update(
            {"$inc": {"seq": 1}},
            response_type=UpdateResponse.NEW_DOCUMENT
        )
        return doc.seq
