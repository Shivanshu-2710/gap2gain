"""Create the preloaded demo account so judges can click 'Try demo'.
Run from backend/:  python -m scripts.create_demo_user   (after running the SQL migrations + seed)."""
from app.config import get_settings
from app.deps import get_db

SAMPLE_RESUME = """Aarav Demo
B.Com student, Delhi University

EXPERIENCE
Math tutor (part-time), 2023-2024: taught 5 school students algebra and geometry.
Cleaned and organised student records in Excel for a college society.
Wrote weekly articles for the college magazine.

SKILLS
Excel, Math, Tutoring, Content Writing
"""


def main():
    s, db = get_settings(), get_db()
    try:
        user = db.auth.admin.create_user({
            "email": s.demo_email, "password": s.demo_password, "email_confirm": True,
            "user_metadata": {"full_name": "Aarav Demo"},
        }).user
    except Exception:
        user = next(u for u in db.auth.admin.list_users() if u.email == s.demo_email)
    uid = user.id

    db.table("profiles").update({"full_name": "Aarav Demo", "min_hourly_pay": 250, "plan": "free",
                                 "buffer_minutes": 10, "min_block_minutes": 45}).eq("id", uid).execute()

    names = ["Excel", "Math", "Tutoring", "Content Writing", "Data Entry"]
    skills = db.table("skills").select("id,name").in_("name", names).execute().data
    db.table("user_skills").upsert([{"user_id": uid, "skill_id": k["id"], "level": 4} for k in skills]).execute()

    blocks = []
    for d in range(5):  # Mon-Fri
        blocks += [
            {"weekday": d, "start_time": "09:00", "end_time": "15:00", "block_type": "class"},
            {"weekday": d, "start_time": "15:00", "end_time": "16:00", "block_type": "commute"},
            {"weekday": d, "start_time": "19:00", "end_time": "20:00", "block_type": "personal"},
        ]
    db.rpc("replace_routine", {"p_user": uid, "p_blocks": blocks}).execute()

    if not db.table("resumes").select("id").eq("user_id", uid).execute().data:
        db.table("resumes").insert({"user_id": uid, "original_text": SAMPLE_RESUME}).execute()

    if not db.table("messages").select("id").eq("user_id", uid).execute().data:
        db.table("messages").insert([
            {"user_id": uid, "sender": "Priya (Cafe Mocha) [sample]", "subject": "Re: Instagram captions",
             "body": "Thanks for applying! Could you share two sample captions by Friday? This is a sample message."},
            {"user_id": uid, "sender": "EduBridge Tutors [sample]", "subject": "Math tutor slot",
             "body": "We'd like to schedule a 15-minute intro call. Are weekday evenings OK? This is a sample message."},
        ]).execute()
    print("Demo user ready:", s.demo_email)


if __name__ == "__main__":
    main()
