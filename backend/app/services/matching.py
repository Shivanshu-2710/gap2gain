"""Transparent rule-based matching:  S = 0.40*T + 0.35*K + 0.15*P + 0.10*R  (each 0-100).
Weights are initial product assumptions, to be tuned with real users.
Hard requirements are checked separately and never hidden inside the score."""

WEIGHTS = {"T": 0.40, "K": 0.35, "P": 0.15, "R": 0.10}


def score_job(job: dict, user_skill_ids: set, weekly_free: dict, profile: dict) -> dict:
    reasons: list[str] = []
    blocking: list[str] = []

    # T: time compatibility
    need = job["duration_minutes"] + (job.get("setup_minutes") or 0)
    fits = sum(1 for ivs in weekly_free.values() for iv in ivs if iv.duration >= need)
    if fits == 0:
        T = 0.0
        blocking.append(f"No free block of {need} min in your weekly schedule")
    else:
        T = float(min(100, 40 + 20 * fits))
        reasons.append(f"Fits {fits} free block(s) per week ({need} min needed)")

    # K: skill compatibility (importance-weighted)
    skills = job.get("job_skills") or []
    total = sum(s["importance"] for s in skills)
    matched = sum(s["importance"] for s in skills if s["skill_id"] in user_skill_ids)
    K = 100.0 * matched / total if total else 50.0
    missing = [(s.get("skills") or {}).get("name", "?") for s in skills
               if s["importance"] >= 3 and s["skill_id"] not in user_skill_ids]
    if missing:
        blocking.append("Missing required skill: " + ", ".join(missing))
    have = [(s.get("skills") or {}).get("name", "?") for s in skills if s["skill_id"] in user_skill_ids]
    if have:
        reasons.append("Matches your skills: " + ", ".join(have))

    # P: pay compatibility (hourly)
    pay, min_pay = job.get("pay_amount"), profile.get("min_hourly_pay")
    if pay is None:
        P = 50.0
        reasons.append("Pay not listed")
    else:
        hourly = float(pay) / (job["duration_minutes"] / 60)
        P = 100.0 if not min_pay else min(100.0, 100.0 * hourly / float(min_pay))
        reasons.append(f"About {hourly:.0f}/hour" + ("" if job.get("pay_verified") else " (pay unverified)"))

    # R: remote preference
    pref = profile.get("prefer_remote")
    R = 100.0 if pref is None or pref == job.get("remote") else 30.0

    score = round(WEIGHTS["T"] * T + WEIGHTS["K"] * K + WEIGHTS["P"] * P + WEIGHTS["R"] * R, 1)
    return {
        "job_id": job["id"], "title": job["title"], "source": job["source"],
        "external_url": job.get("external_url"), "duration_minutes": job["duration_minutes"],
        "pay_amount": pay, "pay_verified": job.get("pay_verified", False), "remote": job.get("remote"),
        "flagged": job.get("flagged", False), "flag_reason": job.get("flag_reason"),
        "score": score, "eligible": not blocking and not job.get("flagged", False),
        "components": {"T": T, "K": round(K, 1), "P": round(P, 1), "R": R},
        "reasons": reasons, "blocking": blocking,
    }