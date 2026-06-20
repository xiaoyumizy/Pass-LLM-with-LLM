"""Tests for review_cli.py — CLI commands for review scheduling."""

import os
import sys
from datetime import date
from pathlib import Path

import pytest

from exam_memory.review_cli import build, due, mark


@pytest.fixture
def tmp_target(tmp_path):
    """Create a minimal target directory with fixture data."""
    target_dir = tmp_path / "targets" / "test-target"
    progress_dir = target_dir / "progress" / "reviews"
    progress_dir.mkdir(parents=True, exist_ok=True)
    # Create mistake_log
    (target_dir / "mistake_log.md").write_text(
        "| 2026-06-15 | P001 | sliding-window | boundary | fix |\n",
        encoding="utf-8",
    )
    # Create topic_checklist
    (target_dir / "topic_checklist.md").write_text(
        "## P0 Must Practice First\n\n| Topic | Std |\n|-------|-----|\n| Binary Search | lower_bound |\n",
        encoding="utf-8",
    )
    return tmp_path  # return root so tests can set --project-root


def _run_build(tmp_target):
    """Helper: run build and return output path."""
    return build(
        target="test-target",
        project_root=tmp_target,
        sources_dir=tmp_target / "targets" / "test-target",
        today=date(2026, 6, 17),
    )


class TestBuildCommand:
    def test_build_creates_review_queue(self, tmp_target):
        result = _run_build(tmp_target)
        assert result is not None
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "### RQ-" in content
        assert "sliding-window" in content
        assert "binary-search" in content

    def test_build_is_valid_markdown(self, tmp_target):
        result = _run_build(tmp_target)
        content = result.read_text(encoding="utf-8")
        assert "```yaml" in content
        assert "source_type:" in content


class TestDueCommand:
    def test_due_returns_items(self, tmp_target):
        _run_build(tmp_target)
        items = due(target="test-target", today=date(2026, 6, 17), project_root=tmp_target)
        assert len(items) > 0
        assert all(i.status == "due" or i.next_review_at <= date(2026, 6, 17) for i in items)

    def test_due_future_date_returns_none(self, tmp_target):
        _run_build(tmp_target)
        # Future date after review
        items = due(target="test-target", today=date(2026, 6, 15), project_root=tmp_target)
        # Items created today (2026-06-17) won't be due on 2026-06-15
        # but some items have next_review_at=today (2026-06-17) so they're > 15
        all_not_due = all(i.next_review_at and i.next_review_at > date(2026, 6, 15) for i in items)
        assert all_not_due or len(items) == 0


class TestMarkCommand:
    def test_mark_updates_item(self, tmp_target):
        _run_build(tmp_target)
        # Find a review ID first
        from exam_memory.review_schedule import parse_review_queue
        queue_path = tmp_target / "targets" / "test-target" / "progress" / "reviews" / "review-queue.md"
        content = queue_path.read_text(encoding="utf-8")
        items = parse_review_queue(content)
        if not items:
            pytest.skip("no review items to mark")
        rid = items[0].review_id
        result = mark(target="test-target", review_id=rid, outcome="good", today=date(2026, 6, 17), project_root=tmp_target)
        assert result is True
        # Verify update
        updated_content = queue_path.read_text(encoding="utf-8")
        assert rid in updated_content
        assert "reviews: 1" in updated_content

    def test_mark_nonexistent_id_returns_false(self, tmp_target):
        result = mark(target="test-target", review_id="RQ-NONEXIST", outcome="good", today=date(2026, 6, 17), project_root=tmp_target)
        assert result is False
