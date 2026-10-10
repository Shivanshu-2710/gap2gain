from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import applications, jobs, me, routine

app = FastAPI(title="Gap2Gain API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",")],
    allow_methods=["*"], allow_headers=["*"],
)

for r in (me, routine, jobs, applications):
    app.include_router(r.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"ok": True}