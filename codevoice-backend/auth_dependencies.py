"""
Authentication dependencies for FastAPI routes.
Simple header-based user verification using MongoDB/Beanie User model.
Expect header: X-User-Id with a valid user id.
"""

from fastapi import Depends, Header, HTTPException
from typing import Optional
from models.user_models import User


async def get_current_user_id(x_user_id: Optional[str] = Header(default=None, alias="X-User-Id")) -> str:
    """Get current user id from X-User-Id header, or raise 401."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    return x_user_id


async def get_current_user(user_id: str = Depends(get_current_user_id)) -> User:
    """Load the current user from database, or raise 401 if not found/inactive."""
    user = await User.get(user_id)
    if not user or not getattr(user, "is_active", True):
        raise HTTPException(status_code=401, detail="Invalid or inactive user")
    return user
