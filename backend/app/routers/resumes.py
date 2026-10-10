from fastapi import APIRouter, Depends, HTTPException
from app.config import get_settings
from app.deps import CurrentUser, get_db, require_premium
from app.schemas import TailorRequest
from app.services.resume import tailor_resume

router = APIRouter(tags=["resumes"])


@router.post("/resumes/tailor")
def tailor(body: TailorRequest, user: CurrentUser = Depends(require_premium), db=Depends(get_db)):
    jobs = db.table("jobs").select("*, job_skills(skills(name))").eq("id", body.job_id).limit(1).execute().data
    if not jobs:
        raise HTTPException(404, "Job not found")
    job = jobs[0]

    if body.resume_text:
        resume = db.table("resumes").insert({"user_id": user.id, "original_text": body.resume_text}).execute().data[0]
    else:
        rows = (db.table("resumes").select("*").eq("user_id", user.id)
                .order("created_at", desc=True).limit(1).execute().data)
        if not rows:
            raise HTTPException(400, "No resume on file. Paste your resume text.")
        resume = rows[0]

    names = [js["skills"]["name"] for js in job["job_skills"] if js.get("skills")]
    s = get_settings()
    result = tailor_resume(resume["original_text"], job, names, s.anthropic_api_key, s.anthropic_model)

    version = db.table("resume_versions").insert({
        "resume_id": resume["id"], "job_id": job["id"],
        "tailored_text": result["tailored_text"], "changes_summary": result["changes_summary"],
    }).execute().data[0]
    return {"version_id": version["id"], "original_text": resume["original_text"], **result}