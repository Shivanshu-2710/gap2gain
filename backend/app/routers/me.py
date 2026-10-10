from fastapi import APIRouter, Depends
from app.deps import CurrentUser, current_user, get_db, get_profile
from app.schemas import ProfileUpdate

router = APIRouter(tags=["profile"])


@router.get("/me")
def read_me(user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    return {**get_profile(db, user.id), "email": user.email}


@router.put("/me")
def update_me(body: ProfileUpdate, user: CurrentUser = Depends(current_user), db=Depends(get_db)):
    changes = body.model_dump(exclude_unset=True)
    if changes:
        db.table("profiles").update(changes).eq("id", user.id).execute()
    return {**get_profile(db, user.id), "email": user.email}