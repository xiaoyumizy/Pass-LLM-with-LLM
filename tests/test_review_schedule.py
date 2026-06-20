"""Tests for review_schedule.py — ReviewItem, parser, scheduler, due status."""

from datetime import date
from exam_memory.review_schedule import (
    ReviewItem,
    parse_review_queue,
    dump_review_queue,
    is_due,
    schedule_next_review,
)


SAMPLE_QUEUE = """\
### RQ-20260617-001

```yaml
source_type: mistake
source_path: targets/pdd-algo/mistake_log.md
topic: sliding-window
root_cause: boundary
priority: P0
status: due
created_at: 2026-06-17
last_reviewed_at: null
next_review_at: 2026-06-18
interval_days: 1
ease: 2.5
reviews: 0
```

Prompt: Re-solve the original problem without looking at the prior code.
Success rule: AC within 25 minutes and explain the invariant in one sentence.

### RQ-20260617-002

```yaml
source_type: topic_coverage
source_path: targets/pdd-algo/topic_checklist.md
topic: binary-search
priority: P1
status: due
created_at: 2026-06-17
last_reviewed_at: null
next_review_at: 2026-06-17
interval_days: 1
ease: 2.5
reviews: 0
```

Prompt: Practice 3 binary search problems from medium difficulty.
Success rule: AC all 3 within 30 minutes.
"""


# ── Task 1: Parser / Serializer / Due ─────────────────────


class TestParseReviewQueue:
    def test_parses_two_items(self):
        items = parse_review_queue(SAMPLE_QUEUE)
        assert len(items) == 2

    def test_first_item_fields(self):
        items = parse_review_queue(SAMPLE_QUEUE)
        item = items[0]
        assert item.review_id == "RQ-20260617-001"
        assert item.topic == "sliding-window"
        assert item.priority == "P0"
        assert item.interval_days == 1

    def test_second_item_source_type(self):
        items = parse_review_queue(SAMPLE_QUEUE)
        assert items[1].source_type == "topic_coverage"
        assert items[1].next_review_at == date(2026, 6, 17)

    def test_parses_prompt_and_success_rule(self):
        items = parse_review_queue(SAMPLE_QUEUE)
        assert "original problem" in items[0].prompt
        assert "invariant" in items[0].success_rule

    def test_empty_text_returns_empty_list(self):
        assert parse_review_queue("") == []

    def test_no_yaml_blocks_returns_empty_list(self):
        assert parse_review_queue("Just plain text") == []


class TestDumpReviewQueue:
    def test_roundtrip_preserves_all_fields(self):
        items = parse_review_queue(SAMPLE_QUEUE)
        dumped = dump_review_queue(items)
        reparsed = parse_review_queue(dumped)
        assert len(reparsed) == 2
        for orig, rep in zip(items, reparsed):
            assert orig.review_id == rep.review_id
            assert orig.topic == rep.topic
            assert orig.priority == rep.priority
            assert orig.interval_days == rep.interval_days

    def test_dump_handles_empty_list(self):
        assert dump_review_queue([]).strip() == ""

    def test_dump_includes_prompt_block(self):
        items = parse_review_queue(SAMPLE_QUEUE)
        dumped = dump_review_queue(items)
        assert "### RQ-20260617-001" in dumped
        assert "```yaml" in dumped


class TestIsDue:
    def test_due_when_next_review_before_today(self):
        item = ReviewItem(review_id="T1", next_review_at=date(2026, 6, 16))
        assert is_due(item, date(2026, 6, 17))

    def test_due_when_next_review_is_today(self):
        item = ReviewItem(review_id="T1", next_review_at=date(2026, 6, 17))
        assert is_due(item, date(2026, 6, 17))

    def test_not_due_when_next_review_in_future(self):
        item = ReviewItem(review_id="T1", next_review_at=date(2026, 6, 18))
        assert not is_due(item, date(2026, 6, 17))

    def test_due_when_next_review_is_none(self):
        item = ReviewItem(review_id="T1", next_review_at=None)
        assert is_due(item, date(2026, 6, 17))


# ── Task 2: Scheduling Logic ──────────────────────────────


def _make_item(
    review_id="RQ-T1",
    interval_days=1,
    ease=2.5,
    reviews=0,
    next_review_at=None,
    created_at=None,
) -> ReviewItem:
    today = date(2026, 6, 17)
    return ReviewItem(
        review_id=review_id,
        interval_days=interval_days,
        ease=ease,
        reviews=reviews,
        next_review_at=next_review_at or today,
        created_at=created_at or today,
    )


class TestScheduleAgain:
    def test_again_resets_interval_to_1(self):
        item = _make_item(interval_days=4, reviews=3)
        updated = schedule_next_review(item, "again", date(2026, 6, 17))
        assert updated.interval_days == 1
        assert updated.reviews == 4

    def test_again_sets_ease_minus_20(self):
        item = _make_item(ease=2.5)
        updated = schedule_next_review(item, "again", date(2026, 6, 17))
        assert updated.ease == 2.3

    def test_again_ease_floor_is_1_3(self):
        item = _make_item(ease=1.4)
        updated = schedule_next_review(item, "again", date(2026, 6, 17))
        assert updated.ease == 1.3

    def test_again_schedules_tomorrow(self):
        item = _make_item()
        updated = schedule_next_review(item, "again", date(2026, 6, 17))
        assert updated.next_review_at == date(2026, 6, 18)


class TestScheduleHard:
    def test_hard_schedules_2_days(self):
        item = _make_item(interval_days=4, reviews=3)
        updated = schedule_next_review(item, "hard", date(2026, 6, 17))
        assert updated.interval_days == 2
        assert updated.next_review_at == date(2026, 6, 19)

    def test_hard_ease_minus_15(self):
        item = _make_item(ease=2.5)
        updated = schedule_next_review(item, "hard", date(2026, 6, 17))
        assert updated.ease == 2.35


class TestScheduleGood:
    def test_good_doubles_interval(self):
        item = _make_item(interval_days=4, reviews=3)
        updated = schedule_next_review(item, "good", date(2026, 6, 17))
        assert updated.interval_days == 8
        assert updated.next_review_at == date(2026, 6, 25)

    def test_good_first_review_interval_1(self):
        item = _make_item(interval_days=1, reviews=0)
        updated = schedule_next_review(item, "good", date(2026, 6, 17))
        assert updated.interval_days == 1
        assert updated.next_review_at == date(2026, 6, 18)


class TestScheduleEasy:
    def test_easy_triples_interval(self):
        item = _make_item(interval_days=4, reviews=3)
        updated = schedule_next_review(item, "easy", date(2026, 6, 17))
        assert updated.interval_days == 12
        assert updated.next_review_at == date(2026, 6, 29)

    def test_easy_ease_plus_15(self):
        item = _make_item(ease=2.5)
        updated = schedule_next_review(item, "easy", date(2026, 6, 17))
        assert updated.ease == 2.65


class TestExamCap:
    def test_interval_capped_by_exam_date(self):
        item = _make_item(interval_days=14, reviews=3)
        exam_date = date(2026, 6, 22)
        updated = schedule_next_review(item, "good", date(2026, 6, 17), exam_date=exam_date)
        assert updated.interval_days == 5
        assert updated.next_review_at == exam_date

    def test_no_exam_date_no_cap(self):
        item = _make_item(interval_days=4, reviews=3)
        updated = schedule_next_review(item, "good", date(2026, 6, 17), exam_date=None)
        assert updated.interval_days == 8

    def test_cap_ignored_when_interval_below_exam(self):
        item = _make_item(interval_days=2, reviews=3)
        exam_date = date(2026, 6, 22)
        updated = schedule_next_review(item, "good", date(2026, 6, 17), exam_date=exam_date)
        assert updated.interval_days == 4
        assert updated.next_review_at == date(2026, 6, 21)


class TestInvalidOutcome:
    def test_unknown_outcome_raises(self):
        item = _make_item()
        try:
            schedule_next_review(item, "unknown", date(2026, 6, 17))
            assert False
        except ValueError:
            pass
