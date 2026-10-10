from fastapi import APIRouter, Depends, Query
from app.deps import CurrentUser, current_user, get_db
from app.services.context import load_context
from app.services.matching import score_job

router = APIRouter(tags=["jobs"])
JOB_SELECT = "*, job_skills(importance, skill_id, skills(name))"


@router.get("/jobs")
def list_jobs(q: str | None = None, remote: bool | None = None, max_minutes: int | None = None,
              user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    query = db.table("jobs").select(JOB_SELECT).eq("status", "open")
    if remote is not None:
        query = query.eq("remote", remote)
    if max_minutes:
        query = query.lte("duration_minutes", max_minutes)
    if q:
        query = query.ilike("title", f"%{q}%")
    return {"jobs": query.order("created_at", desc=True).execute().data}


@router.get("/matches")
def matches(include_ineligible: bool = False, limit: int = Query(20, le=100),
            user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    ctx = load_context(db, user.id)
    jobs = db.table("jobs").select(JOB_SELECT).eq("status", "open").execute().data
    mine = {r["skill_id"] for r in db.table("user_skills").select("skill_id").eq("user_id", user.id).execute().data}
    results = [score_job(j, mine, ctx.weekly_free, ctx.profile) for j in jobs]
    results.sort(key=lambda r: (not r["eligible"], -r["score"]))
    eligible = [r for r in results if r["eligible"]]
    if eligible:  # cache explanations
        db.table("job_matches").upsert(
            [{"user_id": user.id, "job_id": r["job_id"], "score": r["score"], "reasons": r["reasons"]} for r in eligible],
            on_conflict="user_id,job_id").execute()
    out = results if include_ineligible else eligible
    return {"matches": out[:limit], "hidden_ineligible": len(results) - len(eligible)}