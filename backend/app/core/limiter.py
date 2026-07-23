from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def get_remote_ip(request: Request) -> str:
    """
    extracts the real client IP address behind the NGINX reverse proxy
    used for unauthenticated/public endpoints (login, register, redirects)
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


def get_user_or_ip(request: Request) -> str:
    """
    keys by authorization token for authenticated users, falling back to IP
    used for protected endpoints so users behind a corporate NAT don't share limits
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return f"user:{auth_header}"

    return f"ip:{get_remote_ip(request)}"


# default limiter keys by authenticated user token (falling back to IP)
limiter = Limiter(key_func=get_user_or_ip)
