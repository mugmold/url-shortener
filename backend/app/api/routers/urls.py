from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks

from app.models.url import URL
from pymongo.errors import DuplicateKeyError
from app.schemas.url import URLCreateRequest, URLCreateResponse, URLUpdateRequest, URLUpdateResponse
from app.api.dependencies import get_current_user_id, TokenUser

from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

from app.core.limiter import limiter, get_remote_ip

from app.core.redis import redis_client

router = APIRouter(tags=["URLs"])


@router.post("/urls", response_model=URLCreateResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_url(
    url_in: URLCreateRequest,
    request: Request,
    current_user: TokenUser = Depends(get_current_user_id)
):
    if url_in.custom_alias:
        existing_url = await URL.find_one({"short_code": url_in.custom_alias})
        if existing_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom alias already in use"
            )
        short_code = url_in.custom_alias

        # bridge between SQL user id and MongoDB document
        new_url = URL(
            short_code=short_code,
            original_url=str(url_in.original_url),
            owner_id=current_user.id,
            expired_at=url_in.expired_at
        )
        await new_url.insert()

        # proactively prune the KGS queue in case this alias was generated
        await redis_client.lrem("available_short_codes", 0, short_code)

    else:
        # try up to 5 times to find an unused hash
        max_retries = 5
        for _ in range(max_retries):
            # pop a pre-made key from Redis (already a string)
            short_code = await redis_client.lpop("available_short_codes")

            if not short_code:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Generation queue is empty. Please try again later."
                )

            new_url = URL(
                short_code=short_code,
                original_url=str(url_in.original_url),
                owner_id=current_user.id,
                expired_at=url_in.expired_at
            )

            try:
                await new_url.insert()
                break  # successfully claimed
            except DuplicateKeyError:
                pass   # collision detected, loop continues to try next key
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="System collision error, Please try again"
            )

    base_url = str(request.base_url).rstrip("/")

    return URLCreateResponse(
        shortened_url=f"{base_url}/{short_code}",
        created_at=new_url.created_at
    )


@router.patch("/urls/{short_code}", response_model=URLUpdateResponse, status_code=status.HTTP_200_OK)
@limiter.limit("30/minute")
async def update_url(
    short_code: str,
    update_data: URLUpdateRequest,
    request: Request,
    current_user: TokenUser = Depends(get_current_user_id)
):
    url_doc = await URL.find_one({"short_code": short_code, "owner_id": current_user.id})

    if not url_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found or you don't have permission to edit it"
        )

    final_short_code = url_doc.short_code

    # convert to a dictionary to handle the specific case where the user explicitly sends "expired_at": null
    update_dict = update_data.model_dump(exclude_unset=True)

    if "new_custom_alias" in update_dict:
        existing_alias = await URL.find_one({"short_code": update_dict["new_custom_alias"]})
        if existing_alias and existing_alias.id != url_doc.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom alias is already taken by someone else"
            )
        url_doc.short_code = update_dict["new_custom_alias"]
        final_short_code = update_dict["new_custom_alias"]

    if "new_url" in update_dict:
        url_doc.original_url = str(update_dict["new_url"])

    # even if the user sends null, this condition is still fulfilled
    if "expired_at" in update_dict:
        url_doc.expired_at = update_dict["expired_at"]

    await url_doc.save()

    # invalidate the old cache (if exists)
    await redis_client.delete(f"url_cache:{short_code}")

    # if they changed the custom alias, also delete the new key just to be safe
    if final_short_code != short_code:
        await redis_client.delete(f"url_cache:{final_short_code}")

    base_url = str(request.base_url).rstrip("/")

    return URLUpdateResponse(
        new_shortened_url=f"{base_url}/{final_short_code}"
    )


@router.delete("/urls/{short_code}", status_code=status.HTTP_200_OK)
@limiter.limit("30/minute")
async def delete_url(
    request: Request,
    short_code: str,
    current_user: TokenUser = Depends(get_current_user_id)
):
    url_doc = await URL.find_one({"short_code": short_code, "owner_id": current_user.id})

    if not url_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found or you don't have permission to delete it"
        )

    await url_doc.delete()

    # invalidate the old cache (if exists)
    await redis_client.delete(f"url_cache:{short_code}")

    return {"detail": f"URL with short code '{short_code}' has been successfully deleted"}


async def track_click_in_redis(short_code: str):
    await redis_client.hincrby("url_clicks_buffer", short_code, 1)


@router.get("/{short_code}")
@limiter.limit("1000/minute", key_func=get_remote_ip)
async def redirect_to_original(
    request: Request,
    short_code: str,
    background_tasks: BackgroundTasks
):
    cache_key = f"url_cache:{short_code}"

    # check Redis first
    cached_url = await redis_client.get(cache_key)

    if cached_url:
        if cached_url == "NOT_FOUND":
            return RedirectResponse(
                url="/not-found",
                status_code=status.HTTP_302_FOUND
            )

        # track click and redirect instantly
        background_tasks.add_task(track_click_in_redis, short_code)
        return RedirectResponse(
            url=cached_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    # cache miss
    url_doc = await URL.find_one({"short_code": short_code})

    if not url_doc:
        # cache the 404 for 10 minutes to prevent bot spam
        await redis_client.setex(cache_key, 600, "NOT_FOUND")
        return RedirectResponse(
            url="/not-found",
            status_code=status.HTTP_302_FOUND
        )

    ttl_seconds = 3600  # 1 hour

    if url_doc.expired_at:
        expired_time = url_doc.expired_at
        if expired_time.tzinfo is None:
            expired_time = expired_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        if expired_time < now:
            # expired, cache as NOT_FOUND and redirect
            await redis_client.setex(cache_key, 600, "NOT_FOUND")
            return RedirectResponse(
                url="/not-found",
                status_code=status.HTTP_302_FOUND
            )

        # if it expires in less than 1 hour, shrink the Redis timer so it drops exactly when it expires
        remaining_seconds = int((expired_time - now).total_seconds())
        ttl_seconds = min(ttl_seconds, remaining_seconds)

    # cache the successful result
    await redis_client.setex(cache_key, ttl_seconds, url_doc.original_url)

    # track click and redirect
    background_tasks.add_task(track_click_in_redis, short_code)

    return RedirectResponse(
        url=url_doc.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
