from app.services.availability import Interval
from app.services.matching import score_job

JOB = {"id": "j1", "title": "T", "source": "s", "duration_minutes": 60, "setup_minutes": 0, "pay_amount": 500,
       "pay_verified": True, "remote": True,
       "job_skills": [{"importance": 3, "skill_id": "py", "skills": {"name": "Python"}},
                      {"importance": 1, "skill_id": "xl", "skills": {"name": "Excel"}}]}
FREE = {0: [Interval(960, 1080)], 1: [Interval(960, 1080)], 2: [Interval(960, 1080)]}


def test_good_match_is_high_and_eligible():
    r = score_job(JOB, {"py", "xl"}, FREE, {"min_hourly_pay": 300, "prefer_remote": True})
    assert r["eligible"] and r["score"] >= 95


def test_missing_required_skill_is_hard_block():
    r = score_job(JOB, {"xl"}, FREE, {})
    assert not r["eligible"] and r["blocking"]


def test_no_fitting_block_is_hard_block():
    r = score_job({**JOB, "duration_minutes": 300}, {"py"}, FREE, {})
    assert not r["eligible"]


def test_flagged_job_never_eligible():
    r = score_job({**JOB, "flagged": True, "flag_reason": "scam"}, {"py"}, FREE, {})
    assert not r["eligible"]