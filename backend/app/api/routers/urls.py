from fastapi import APIRouter, Depends, HTTPException, status, Request
from hashids import Hashids

from app.models.url import URL
from app.models.counter import Counter
from app.models.user import User
from app.schemas.url import URLCreateRequest, URLCreateResponse, URLUpdateRequest, URLUpdateResponse
from app.api.dependencies import get_current_user
from app.core.config import settings

from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

from app.core.limiter import limiter, get_remote_ip

router = APIRouter(tags=["URLs"])

hashids = Hashids(salt=settings.SECRET_KEY, min_length=5)


@router.post("/urls", response_model=URLCreateResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_url(
    url_in: URLCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    if url_in.custom_alias:
        existing_url = await URL.find_one({"short_code": url_in.custom_alias})
        if existing_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom alias already in use"
            )
        short_code = url_in.custom_alias

    else:
        # try up to 10 times to find an unused hash
        max_retries = 10
        for _ in range(max_retries):
            seq_id = await Counter.get_next_sequence("url_counter")
            short_code = hashids.encode(seq_id)

            existing_url = await URL.find_one({"short_code": short_code})
            if not existing_url:
                break  # found a free one
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="System collision error, Please try again"
            )

    new_url = URL(
        short_code=short_code,
        original_url=str(url_in.original_url),
        owner=current_user,
        expired_at=url_in.expired_at
    )
    await new_url.insert()

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
    current_user: User = Depends(get_current_user)
):
    url_doc = await URL.find_one({"short_code": short_code, "owner.$id": current_user.id})

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

    base_url = str(request.base_url).rstrip("/")

    return URLUpdateResponse(
        new_shortened_url=f"{base_url}/{final_short_code}"
    )


@router.delete("/urls/{short_code}", status_code=status.HTTP_200_OK)
@limiter.limit("30/minute")
async def delete_url(
    request: Request,
    short_code: str,
    current_user: User = Depends(get_current_user)
):
    url_doc = await URL.find_one({"short_code": short_code, "owner.$id": current_user.id})

    if not url_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found or you don't have permission to delete it"
        )

    await url_doc.delete()

    return {"detail": f"URL with short code '{short_code}' has been successfully deleted"}


@router.get("/{short_code}")
@limiter.limit("1000/minute", key_func=get_remote_ip)
async def redirect_to_original(request: Request, short_code: str):
    url_doc = await URL.find_one({"short_code": short_code})

    if not url_doc:
        return RedirectResponse(
            url="/not-found",
            status_code=status.HTTP_302_FOUND
        )

    if url_doc.expired_at:
        expired_time = url_doc.expired_at
        if expired_time.tzinfo is None:
            expired_time = expired_time.replace(tzinfo=timezone.utc)

        if expired_time < datetime.now(timezone.utc):
            return RedirectResponse(
                url="/not-found",
                status_code=status.HTTP_302_FOUND
            )

    await url_doc.update({"$inc": {"clicks_count": 1}})

    return RedirectResponse(
        url=url_doc.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
