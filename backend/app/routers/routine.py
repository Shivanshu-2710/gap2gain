from fastapi import APIRouter, Depends
from app.deps import CurrentUser, current_user, get_db
from app.schemas import RoutineSave
from app.services.availability import to_hhmm
from app.services.context import load_context

router = APIRouter(tags=["routine"])


def _blocks(db, user_id):
    return (db.table("routine_blocks").select("*").eq("user_id", user_id)
            .order("weekday").order("start_time").execute().data)


@router.get("/routine")
def get_routine(user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    return {"blocks": _blocks(db, user.id)}


@router.put("/routine")
def save_routine(body: RoutineSave, user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    db.rpc("replace_routine", {"p_user": user.id, "p_blocks": [b.model_dump() for b in body.blocks]}).execute()
    return {"blocks": _blocks(db, user.id)}


@router.get("/availability")
def availability(min_block_minutes: int | None = None, buffer_minutes: int | None = None,
                 user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    ctx = load_context(db, user.id, min_block_minutes, buffer_minutes)
    weekly = {
        str(d): [{"start": to_hhmm(i.start), "end": to_hhmm(i.end), "minutes": i.duration} for i in ivs]
        for d, ivs in ctx.weekly_free.items()
    }
    total = sum(i.duration for ivs in ctx.weekly_free.values() for i in ivs)
    return {"min_block_minutes": ctx.min_block, "buffer_minutes": ctx.buffer,
            "weekly": weekly, "total_free_minutes": total}