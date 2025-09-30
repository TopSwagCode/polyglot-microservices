from fastapi import HTTPException, status, Request
from fastapi import Depends
import structlog

logger = structlog.get_logger()


async def get_current_user_from_headers(request: Request) -> dict:
    """Get current user from headers set by API Gateway"""
    user_id = request.headers.get("X-User-Id")
    username = request.headers.get("X-Username")
    role = request.headers.get("X-User-Role", "User")
    
    if not user_id or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user information in headers. Requests must come through API Gateway."
        )
    
    return {
        "user_id": int(user_id),
        "username": username,
        "role": role
    }


async def get_admin_user(request: Request) -> dict:
    """Get current admin user (requires Admin role) - trusts API Gateway"""
    user = await get_current_user_from_headers(request)
    
    # if user.get("role") != "Admin": TODO: Uncomment if admin-only access is needed
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Forbidden: Admin role required"
    #     )
    
    return user