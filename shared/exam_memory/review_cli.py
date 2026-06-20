"""review_cli.py — CLI entry points for review scheduling.

Commands:
  build --target <name> [--project-root <path>]
  due   --target <name> [--date YYYY-MM-DD] [--project-root <path>]
  mark  --target <name> --id <RQ-ID> --outcome <again|hard|good|easy> [--date YYYY-MM-DD] [--project-root <path>]
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Sequence

from exam_memory.review_builder import (
    build_review_items_from_choice_rounds,
    build_review_items_from_mistakes,
    build_review_items_from_topic_checklist,
    dedupe_review_items,
)
from exam_memory.review_schedule import (
    ReviewItem,
    dump_review_queue,
    is_due,
    parse_review_queue,
    schedule_next_review,
)


def _parse_date(s: str | None) -> "date | None":
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        print(f"错误: 日期格式无效 '{s}'，请使用 YYYY-MM-DD", file=sys.stderr)
        sys.exit(1)


def _resolve_target(
    target: str,
    project_root: Path | None,
) -> tuple[Path, Path]:
    """Return (target_dir, reviews_dir)."""
    root = (project_root or Path.cwd()).resolve()
    target_dir = root / "targets" / target
    if ".." in target or "/" in target or "\\" in target:
        raise ValueError(f"非法 target 名称: {target}")
    if not target_dir.is_relative_to(root / "targets"):
        raise ValueError(f"target 超出范围: {target}")
    reviews_dir = target_dir / "progress" / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    return target_dir, reviews_dir


_DEFAULT_SOURCES = [
    ("mistake_log.md", build_review_items_from_mistakes),
    ("topic_checklist.md", build_review_items_from_topic_checklist),
]


def build(
    target: str,
    project_root: Path | None = None,
    sources_dir: Path | None = None,
    today: date | None = None,
) -> Path | None:
    """Build review queue from harness data sources.

    Args:
        target: Target name (e.g., "pdd-algo").
        project_root: Project root path. Defaults to cwd.
        sources_dir: Optional pre-resolved source directory. Overrides target resolution.
        today: Optional build date used for created_at, next_review_at, and review IDs.

    Returns:
        Path to the generated queue file, or None on failure.
    """
    if sources_dir:
        target_dir = sources_dir.resolve()
        reviews_dir = target_dir / "progress" / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir, reviews_dir = _resolve_target(target, project_root)

    review_date = today or date.today()

    # Collect items from all sources
    all_items: list[ReviewItem] = []
    sources = list(_DEFAULT_SOURCES)

    # Also read choice rounds if they exist
    choice_dir = target_dir / "progress" / "choice-questions"
    if choice_dir.is_dir():
        sources.append(("progress/choice-questions/", None))

    for filename, parser in sources:
        if parser is None:
            # Directory of choice rounds
            for fpath in sorted(choice_dir.glob("round*.md")):
                text = fpath.read_text(encoding="utf-8")
                all_items.extend(build_review_items_from_choice_rounds(text, today=review_date))
            continue
        fpath = target_dir / filename
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        all_items.extend(parser(text, today=review_date))

    if not all_items:
        return None

    deduped = dedupe_review_items(all_items)
    queue_path = reviews_dir / "review-queue.md"
    queue_path.write_text(dump_review_queue(deduped), encoding="utf-8")
    return queue_path


def due(
    target: str,
    today: date | None = None,
    project_root: Path | None = None,
) -> list[ReviewItem]:
    """Return due review items for the given target."""
    _, reviews_dir = _resolve_target(target, project_root)
    queue_path = reviews_dir / "review-queue.md"
    if not queue_path.exists():
        return []
    today = today or date.today()
    items = parse_review_queue(queue_path.read_text(encoding="utf-8"))
    return [i for i in items if is_due(i, today)]


def mark(
    target: str,
    review_id: str,
    outcome: str,
    today: date | None = None,
    project_root: Path | None = None,
) -> bool:
    """Mark a review item with an outcome, update its schedule.

    Returns True if updated, False if not found.
    """
    _, reviews_dir = _resolve_target(target, project_root)
    queue_path = reviews_dir / "review-queue.md"
    if not queue_path.exists():
        return False
    today = today or date.today()
    items = parse_review_queue(queue_path.read_text(encoding="utf-8"))
    found = False
    for i, item in enumerate(items):
        if item.review_id == review_id:
            items[i] = schedule_next_review(item, outcome, today)
            found = True
            break
    if not found:
        return False
    queue_path.write_text(dump_review_queue(items), encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Review scheduling CLI")
    parser.add_argument("--project-root", type=str, default=None, help="Project root path")
    sub = parser.add_subparsers(dest="command", required=True)

    build_p = sub.add_parser("build", help="Build review queue from harness data")
    build_p.add_argument("--target", required=True, help="Target name (e.g., pdd-algo)")
    build_p.add_argument("--date", type=str, default=None, help="YYYY-MM-DD")

    due_p = sub.add_parser("due", help="List due review items")
    due_p.add_argument("--target", required=True)
    due_p.add_argument("--date", type=str, default=None, help="YYYY-MM-DD")

    mark_p = sub.add_parser("mark", help="Mark a review result")
    mark_p.add_argument("--target", required=True)
    mark_p.add_argument("--id", required=True, dest="review_id")
    mark_p.add_argument("--outcome", required=True, choices=["again", "hard", "good", "easy"])
    mark_p.add_argument("--date", type=str, default=None)

    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve() if args.project_root else None

    if args.command == "build":
        d = _parse_date(args.date) or date.today()
        path = build(target=args.target, project_root=root, today=d)
        if path:
            print(f"Review queue written to {path}")
        else:
            print("No review items generated (check sources)")
        return 0

    if args.command == "due":
        d = _parse_date(args.date) or date.today()
        items = due(target=args.target, today=d, project_root=root)
        if not items:
            print("No due review items.")
        else:
            for item in items:
                print(f"  {item.review_id} [{item.priority}] {item.topic} — {item.prompt}")
        return 0

    if args.command == "mark":
        d = _parse_date(args.date) or date.today()
        ok = mark(target=args.target, review_id=args.review_id, outcome=args.outcome, today=d, project_root=root)
        print(f"Review {args.review_id}: {'updated' if ok else 'not found'}")
        return 0 if ok else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
