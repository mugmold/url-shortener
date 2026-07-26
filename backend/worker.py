import asyncio
import logging
from hashids import Hashids
from pymongo import AsyncMongoClient
from beanie import init_beanie, UpdateResponse
import redis.exceptions

from app.core.config import settings
from app.core.redis import redis_client
from app.models.url import URL
from app.models.counter import Counter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Background-Worker")

hashids = Hashids(salt=settings.SECRET_KEY, min_length=5)

MIN_KEYS = 2000
BATCH_SIZE = 5000


async def init_mongo():
    client = AsyncMongoClient(settings.MONGO_URL)
    await init_beanie(
        database=client[settings.MONGO_DB_NAME],
        document_models=[URL, Counter]
    )
    logger.info("MongoDB connection established successfully.")
    await Counter.init_counter("url_counter")


async def sync_clicks_to_mongodb():
    """background worker that flushes Redis clicks to MongoDB every 5 seconds."""
    logger.info("Click Sync Worker started...")
    while True:
        await asyncio.sleep(5)
        try:
            # atomically rename the key so incoming clicks write to a fresh buffer
            # this prevents losing clicks that happen during the flush process
            await redis_client.rename("url_clicks_buffer", "url_clicks_processing")

            # grab all the clicks we isolated
            buffered_clicks = await redis_client.hgetall("url_clicks_processing")

            if buffered_clicks:
                # flush them to MongoDB in the background
                for short_code, count in buffered_clicks.items():
                    url_doc = await URL.find_one({"short_code": short_code})
                    if url_doc:
                        await url_doc.update({"$inc": {"clicks_count": int(count)}})

                # delete the processing buffer now that we are done
                await redis_client.delete("url_clicks_processing")
                logger.info(
                    f"Successfully synced click data for {len(buffered_clicks)} URLs to MongoDB."
                )

        except redis.exceptions.ResponseError:
            # this happens if "url_clicks_buffer" doesn't exist yet (no clicks in the last 5 seconds)
            pass
        except Exception as e:
            logger.error(f"Failed to sync click analytics: {e}")


async def refill_keys():
    """background loop that pre-generates Hashids."""
    logger.info("KGS Worker started. Monitoring Redis queue...")
    while True:
        try:
            available_keys = await redis_client.llen("available_short_codes")

            if available_keys < MIN_KEYS:
                logger.info(
                    f"Key pool running low ({available_keys} keys remaining). Generating batch of {BATCH_SIZE} new keys..."
                )

                doc = await Counter.find_one({"name": "url_counter"}).update(
                    {"$inc": {"seq": BATCH_SIZE}},
                    response_type=UpdateResponse.NEW_DOCUMENT
                )

                highest_val = doc.seq
                start_val = highest_val - BATCH_SIZE + 1

                # generate the hashes in memory
                new_keys = [
                    hashids.encode(i)
                    for i
                    in range(start_val, highest_val + 1)
                ]

                # check if any of these were taken
                taken_docs = await URL.find({"short_code": {"$in": new_keys}}).to_list()
                taken_keys = {doc.short_code for doc in taken_docs}

                # clean the batch
                clean_keys = [key for key in new_keys if key not in taken_keys]

                # push guaranteed-clean keys to Redis
                if clean_keys:
                    await redis_client.rpush("available_short_codes", *clean_keys)
                    logger.info(
                        f"Successfully added {len(clean_keys)} new keys to the Redis pool."
                    )

            # wait 5 secs before checking again
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"KGS encountered an error: {e}")
            await asyncio.sleep(5)


async def main():
    await init_mongo()

    # run both loops concurrently
    await asyncio.gather(
        refill_keys(),
        sync_clicks_to_mongodb()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Background Worker shutting down...")
