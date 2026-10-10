from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException
from app.config import get_settings
from app.deps import CurrentUser, current_user, get_db, get_profile
from app.services.entitlements import entitlements_for

router = APIRouter(tags=["account"])


@router.get("/usage")
def usage(user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    profile = get_profile(db, user.id)
    today = datetime.now(ZoneInfo(profile["timezone"])).date().isoformat()
    row = (db.table("daily_usage").select("auto_apply_count").eq("user_id", user.id)
           .eq("usage_date", today).limit(1).execute().data)
    used = row[0]["auto_apply_count"] if row else 0
    limit = entitlements_for(profile["plan"], get_settings().free_daily_auto_applies)["auto_apply_daily_limit"]
    return {"date": today, "used": used, "limit": limit,
            "remaining": None if limit is None else max(0, limit - used)}


@router.get("/subscription")
def subscription(user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    profile = get_profile(db, user.id)
    sub = (db.table("subscriptions").select("*").eq("user_id", user.id)
           .order("expires_at", desc=True).limit(1).execute().data)
    return {"plan": profile["plan"], "subscription": sub[0] if sub else None,
            "entitlements": entitlements_for(profile["plan"], get_settings().free_daily_auto_applies)}


@router.post("/subscription/demo-upgrade")
def demo_upgrade(user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    """Simulated upgrade for the demo ONLY. Real billing/payment reconciliation is deferred."""
    if not get_settings().demo_mode:
        raise HTTPException(404, "Not found")
    db.table("profiles").update({"plan": "premium"}).eq("id", user.id).execute()
    db.table("subscriptions").insert({"user_id": user.id, "plan": "premium", "status": "demo"}).execute()
    return {"plan": "premium", "status": "demo"}