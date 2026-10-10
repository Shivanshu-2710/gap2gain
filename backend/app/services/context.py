from dataclasses import dataclass
from supabase import Client
from app.deps import get_profile
from app.services.availability import Interval, weekly_availability


@dataclass
class UserContext:
    profile: dict
    weekly_free: dict[int, list[Interval]]
    min_block: int
    buffer: int


def load_context(db: Client, user_id: str, min_block: int | None = None, buffer: int | None = None) -> UserContext:
    profile = get_profile(db, user_id)
    min_block = min_block or profile["min_block_minutes"]
    buffer = profile["buffer_minutes"] if buffer is None else buffer
    blocks = db.table("routine_blocks").select("*").eq("user_id", user_id).execute().data
    free = weekly_availability(blocks, buffer_minutes=buffer, min_block_minutes=min_block)
    return UserContext(profile, free, min_block, buffer)