from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.services.availability import Interval, to_minutes


def summarize_messages(messages: list[dict]) -> list[dict]:
    """Extractive summary (no AI): keeps a link back to each original message."""
    return [
        {"message_id": m["id"], "sender": m["sender"], "subject": m["subject"],
         "snippet": (m["body"][:140] + "…") if len(m["body"]) > 140 else m["body"],
         "received_at": m["received_at"]}
        for m in messages
    ]


def next_delivery(now_utc: datetime, tz: str, delivery_time: str, weekly_free: dict[int, list[Interval]],
                  max_delay_hours: int = 6) -> tuple[datetime, str]:
    """Next digest time in the user's timezone.
    If the preferred time falls in a busy period, move to the next free block the same day,
    but never delay more than `max_delay_hours` (configurable fallback so messages aren't held back forever)."""
    local_now = now_utc.astimezone(ZoneInfo(tz))
    h, m = (int(x) for x in str(delivery_time).split(":")[:2])
    candidate = local_now.replace(hour=h, minute=m, second=0, microsecond=0)
    if candidate <= local_now:
        candidate += timedelta(days=1)
    minute = candidate.hour * 60 + candidate.minute
    free = weekly_free.get(candidate.weekday(), [])
    if any(iv.start <= minute < iv.end for iv in free):
        return candidate, "preferred_time"
    later = [iv for iv in free if iv.start > minute]
    if later:
        shifted = candidate.replace(hour=later[0].start // 60, minute=later[0].start % 60)
        if shifted - candidate <= timedelta(hours=max_delay_hours):
            return shifted, "moved_to_next_free_block"
    return candidate, "fallback_preferred_time"