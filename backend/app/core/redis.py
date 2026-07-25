import redis.asyncio as aioredis
from app.core.config import settings

# decode responses ensures we get strings back instead of raw bytes
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
