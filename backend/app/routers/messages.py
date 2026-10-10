from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.config import get_settings
from app.deps import CurrentUser, current_user, get_db
from app.services.context import load_context
from app.services.digest import next_delivery, summarize_messages

router = APIRouter(tags=["inbox"])


@router.get("/messages")
def list_messages(user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    rows = (db.table("messages").select("*").eq("user_id", user.id)
            .order("received_at", desc=True).limit(100).execute().data)
    return {"messages": rows}


@router.post("/digests/preview")
def digest_preview(user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    """Preview only: no background worker in the MVP. Real delivery needs a persistent
    scheduler/queue (an in-memory timer would be lost on restart)."""
    unread = (db.table("messages").select("*").eq("user_id", user.id).eq("is_read", False)
              .order("received_at", desc=True).execute().data)
    prefs = db.table("digest_preferences").select("*").eq("user_id", user.id).limit(1).execute().data[0]
    ctx = load_context(db, user.id)
    when, reason = next_delivery(datetime.now(timezone.utc), prefs["timezone"], prefs["delivery_time"],
                                 ctx.weekly_free, get_settings().digest_max_delay_hours)
    db.table("digest_logs").insert({"user_id": user.id, "scheduled_for": when.isoformat(), "status": "previewed"}).execute()
    return {"enabled": prefs["enabled"], "scheduled_for": when.isoformat(), "scheduling_reason": reason,
            "unread_count": len(unread), "items": summarize_messages(unread)}
