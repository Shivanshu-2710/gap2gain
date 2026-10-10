from fastapi import APIRouter, Depends, HTTPException
from app.config import get_settings
from app.deps import CurrentUser, current_user, get_db, get_profile
from app.schemas import ApplicationCreate

router = APIRouter(tags=["applications"])


@router.post("/applications")
def create_application(body: ApplicationCreate, user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    """Quota is enforced in Postgres (reserve_auto_apply), atomically. Nothing is sent to an
    external platform in the MVP: the application is only queued inside Gap2Gain."""
    profile = get_profile(db, user.id)
    limit = None if profile["plan"] == "premium" else get_settings().free_daily_auto_applies
    res = db.rpc("reserve_auto_apply", {
        "p_user": user.id, "p_job": body.job_id, "p_timezone": profile["timezone"], "p_limit": limit,
    }).execute().data
    status = res["status"]
    if status == "limit_reached":
        raise HTTPException(429, {"code": "daily_limit_reached",
                                  "message": f"Daily free limit of {limit} auto-apply actions reached."})
    if status == "job_unavailable":
        raise HTTPException(404, {"code": "job_unavailable", "message": "This job is no longer open."})
    return {**res, "mode": "queued_in_app",
            "note": "Queued inside Gap2Gain. Not yet submitted to an external platform."}


@router.get("/applications")
def list_applications(user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    rows = (db.table("applications").select("*, jobs(title, source, external_url)")
            .eq("user_id", user.id).order("applied_at", desc=True).execute().data)
    return {"applications": rows}