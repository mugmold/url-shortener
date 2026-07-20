from beanie import Document, Indexed
from typing import Annotated
from pydantic import Field
from pymongo import ReturnDocument


class Counter(Document):
    name: Annotated[str, Indexed(
        unique=True)
    ] = Field(..., description="counter name")
    seq: int = 0

    class Settings:
        name = "counters"

    @classmethod
    async def get_next_sequence(cls, counter_name: str) -> int:
        doc = await cls.get_motor_collection().find_one_and_update(
            {
                "name": counter_name
            },
            {
                "$inc": {
                    "seq": 1
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        return doc["seq"]
