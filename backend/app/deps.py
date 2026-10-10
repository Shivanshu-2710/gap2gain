from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends, Header, HTTPException
from supabase import Client, create_client

from app.config import get_settings


@lru_cache
def get_db() -> Client:
    """Service-role client. It bypasses RLS, so every query MUST filter by user_id."""
    s = get_settings()
    return create_client(s.supabase_url, s.supabase_service_role_key)


@dataclass
class CurrentUser:
    id: str
    email: str | None


def current_user(authorization: str | None = Header(default=None), db: Client = Depends(get_db)) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        user = db.auth.get_user(token).user
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return CurrentUser(id=user.id, email=user.email)


def get_profile(db: Client, user_id: str) -> dict:
    res = db.table("profiles").select("*").eq("id", user_id).limit(1).execute()
    if not res.data:
        raise HTTPException(404, "Profile not found")
    return res.data[0]


def require_premium(user: CurrentUser = Depends(current_user), db: Client = Depends(get_db)) -> CurrentUser:
    if get_profile(db, user.id)["plan"] != "premium":
        raise HTTPException(403, {"code": "premium_required", "message": "This feature needs the Premium plan."})
    return user