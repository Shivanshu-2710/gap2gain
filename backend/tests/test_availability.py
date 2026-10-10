from app.services.availability import compute_free_intervals, to_hhmm


def blk(s, e, t="class"):
    return {"start_time": s, "end_time": e, "block_type": t, "weekday": 0}


def test_doc_example_two_hour_gap():
    blocks = [blk("09:00", "15:00"), blk("15:00", "16:00", "commute"), blk("18:00", "19:00", "personal")]
    free = compute_free_intervals(blocks, min_block_minutes=60)
    spans = [(to_hhmm(f.start), to_hhmm(f.end)) for f in free]
    assert ("16:00", "18:00") in spans


def test_overlaps_are_merged():
    blocks = [blk("09:00", "12:00"), blk("11:00", "14:00")]
    free = compute_free_intervals(blocks, min_block_minutes=30)
    assert all(not (f.start < 14 * 60 and f.end > 9 * 60) for f in free)


def test_buffer_shrinks_gap_and_short_gaps_dropped():
    blocks = [blk("09:00", "15:00"), blk("17:00", "18:00")]
    assert any(f.duration == 120 for f in compute_free_intervals(blocks, buffer_minutes=0, min_block_minutes=30))
    assert not any(f.start == 15 * 60 for f in compute_free_intervals(blocks, buffer_minutes=60, min_block_minutes=30))


def test_empty_day_uses_day_window():
    free = compute_free_intervals([], min_block_minutes=30)
    assert len(free) == 1 and free[0].duration == 17 * 60