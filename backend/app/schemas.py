import re
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class ProfileUpdate(BaseModel):
    # `plan` is intentionally absent: entitlements are server-controlled.
    full_name: str | None = Field(default=None, max_length=120)
    timezone: str | None = None
    min_hourly_pay: float | None = Field(default=None, ge=0)
    prefer_remote: bool | None = None
    min_block_minutes: int | None = Field(default=None, ge=15, le=480)
    buffer_minutes: int | None = Field(default=None, ge=0, le=120)

    @field_validator("timezone")
    @classmethod
    def valid_tz(cls, v):
        if v is None:
            return v
        from zoneinfo import ZoneInfo
        try:
            ZoneInfo(v)
        except Exception:
            raise ValueError("Unknown timezone")
        return v


class RoutineBlock(BaseModel):
    weekday: int = Field(ge=0, le=6)  # 0 = Monday
    start_time: str
    end_time: str
    block_type: Literal["class", "work", "commute", "sleep", "personal", "unavailable"]

    @model_validator(mode="after")
    def check_times(self):
        if not (HHMM.match(self.start_time) and HHMM.match(self.end_time)):
            raise ValueError("Times must be HH:MM (24h)")
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time (split overnight blocks in two)")
        return self


class RoutineSave(BaseModel):
    blocks: list[RoutineBlock] = Field(max_length=200)


class ApplicationCreate(BaseModel):
    job_id: str


class TailorRequest(BaseModel):
    job_id: str
    resume_text: str | None = Field(default=None, max_length=20000)  # omitted = reuse latest saved resume


class DigestPreviewRequest(BaseModel):
    pass