"""Free-time calculation. Pure functions, no I/O: easy to test."""
from dataclasses import dataclass

# Sleep is already an unavailable window, so no travel/buffer padding is added around it.
UNBUFFERED_TYPES = {"sleep"}
DAY_START = 6 * 60    # earliest usable minute (06:00)
DAY_END = 23 * 60     # latest usable minute (23:00)


@dataclass(frozen=True)
class Interval:
    start: int  # minutes from midnight
    end: int

    @property
    def duration(self) -> int:
        return self.end - self.start


def to_minutes(t) -> int:
    parts = str(t).split(":")
    return int(parts[0]) * 60 + int(parts[1])


def to_hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def merge(intervals: list[Interval]) -> list[Interval]:
    """Merge overlapping or touching intervals."""
    out: list[Interval] = []
    for iv in sorted(intervals, key=lambda i: (i.start, i.end)):
        if out and iv.start <= out[-1].end:
            out[-1] = Interval(out[-1].start, max(out[-1].end, iv.end))
        else:
            out.append(iv)
    return out


def compute_free_intervals(
    blocks: list[dict],
    *,
    buffer_minutes: int = 0,
    min_block_minutes: int = 30,
    day_start: int = DAY_START,
    day_end: int = DAY_END,
) -> list[Interval]:
    """Free gaps in ONE day, after merging commitments, adding buffers and dropping short gaps."""
    busy = [Interval(0, day_start), Interval(day_end, 1440)]
    for b in blocks:
        pad = 0 if b["block_type"] in UNBUFFERED_TYPES else buffer_minutes
        busy.append(Interval(max(0, to_minutes(b["start_time"]) - pad),
                             min(1440, to_minutes(b["end_time"]) + pad)))
    free, cursor = [], 0
    for iv in merge(busy):
        if iv.start > cursor:
            free.append(Interval(cursor, iv.start))
        cursor = max(cursor, iv.end)
    if cursor < 1440:
        free.append(Interval(cursor, 1440))
    return [f for f in free if f.duration >= min_block_minutes]


def weekly_availability(blocks: list[dict], **kwargs) -> dict[int, list[Interval]]:
    return {
        d: compute_free_intervals([b for b in blocks if b["weekday"] == d], **kwargs)
        for d in range(7)
    }