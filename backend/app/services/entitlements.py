FREE = {"plan": "free", "auto_apply_daily_limit": 5, "resume_tailoring": False}
PREMIUM = {"plan": "premium", "auto_apply_daily_limit": None, "resume_tailoring": True}  # None = unlimited


def entitlements_for(plan: str, free_limit: int) -> dict:
    if plan == "premium":
        return dict(PREMIUM)
    return {**FREE, "auto_apply_daily_limit": free_limit}