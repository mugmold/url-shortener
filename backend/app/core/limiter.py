from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def get_identifier(request: Request) -> str:
    # check if the user is logged in via token
    auth_header = request.headers.get("Authorization")
    if auth_header:
        return auth_header

    # check for reverse proxy headers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # the first one is the real client ip
        return forwarded.split(",")[0].strip()

    # fallback to the direct socket connection ip
    return get_remote_address(request)


# initialize the limiter
limiter = Limiter(key_func=get_identifier)
