"""review_schedule.py — ReviewItem dataclass + parser/serializer + due status.

Part of the file-based SM-2 inspired spaced review system.

一个 review queue 文件（targets/{target}/progress/reviews/review-queue.md）
包含多个 review item block，每个 block 是一个 Markdown heading + YAML frontmatter + prompt。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import yaml

from exam_memory.frontmatter import parse_frontmatter


@dataclass
class ReviewItem:
    """一条复习项。"""

    review_id: str
    source_type: str = "mistake"
    source_path: str = ""
    topic: str = ""
    root_cause: str = ""
    priority: str = "P1"
    status: str = "due"
    created_at: date | None = None
    last_reviewed_at: date | None = None
    next_review_at: date | None = None
    interval_days: int = 1
    ease: float = 2.5
    reviews: int = 0
    prompt: str = ""
    success_rule: str = ""
    _extra: dict[str, Any] = field(default_factory=dict)


_HEADER_RE = re.compile(r"^###\s+(?P<id>RQ-\d{8}-\d{3})\s*$", re.MULTILINE)


def _yaml_block(text: str, start: int) -> tuple[str, int]:
    """从 start 位置开始，提取 ```yaml ... ``` 块的内容和结束位置。"""
    rest = text[start:]
    m = re.match(r"\s*```", rest)
    if not m:
        return "", start
    lang_end = m.end()
    # skip optional "yaml" language tag
    if rest[lang_end:lang_end + 4] == "yaml":
        lang_end += 4
    block_start = start + lang_end
    end_marker = text.find("\n```", block_start)
    if end_marker == -1:
        return "", start
    return text[block_start:end_marker].strip(), end_marker + 4


def parse_review_queue(text: str) -> list[ReviewItem]:
    """解析 review queue Markdown，返回 ReviewItem 列表。"""
    items: list[ReviewItem] = []
    pos = 0
    while True:
        m = _HEADER_RE.search(text, pos)
        if not m:
            break
        review_id = m.group("id")
        block_start = m.end()
        yaml_text, yaml_end = _yaml_block(text, block_start)
        if not yaml_text:
            pos = block_start
            continue
        try:
            data = yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError:
            data = {}
        prompt = ""
        success_rule = ""
        # 提取 prompt 和 success_rule 在 yaml 块之后的内容
        after_yaml = text[yaml_end:].strip()
        if after_yaml.startswith("Prompt:"):
            # 提取直到下一个 ### 或文件结尾
            prompt_end = after_yaml.find("\n### ")
            prompt_content = after_yaml[7:prompt_end] if prompt_end > 7 else after_yaml[7:]
            if prompt_end == -1:
                prompt = prompt_content.strip()
                pos = len(text)
            else:
                prompt = prompt_content.strip()
                pos = after_yaml.find("\n### ", yaml_end) + yaml_end
            # 提取 success_rule
            if "Success rule:" in prompt:
                spl = prompt.rsplit("Success rule:", 1)
                prompt = spl[0].strip()
                success_rule = spl[1].strip()
        else:
            pos = block_start

        def _d(v: str | None) -> date | None:
            if not v:
                return None
            try:
                parts = str(v).split("-")
                return date(int(parts[0]), int(parts[1]), int(parts[2]))
            except (ValueError, IndexError):
                return None

        def _i(v: Any, default: int = 0) -> int:
            try:
                return int(v)
            except (TypeError, ValueError):
                return default

        def _f(v: Any, default: float = 2.5) -> float:
            try:
                return float(v)
            except (TypeError, ValueError):
                return default

        item = ReviewItem(
            review_id=review_id,
            source_type=str(data.get("source_type", "mistake")),
            source_path=str(data.get("source_path", "")),
            topic=str(data.get("topic", "")),
            root_cause=str(data.get("root_cause", "")),
            priority=str(data.get("priority", "P1")),
            status=str(data.get("status", "due")),
            created_at=_d(data.get("created_at")),
            last_reviewed_at=_d(data.get("last_reviewed_at")),
            next_review_at=_d(data.get("next_review_at")),
            interval_days=_i(data.get("interval_days"), 1),
            ease=_f(data.get("ease"), 2.5),
            reviews=_i(data.get("reviews"), 0),
            prompt=prompt,
            success_rule=success_rule,
        )
        items.append(item)
    return items


def dump_review_queue(items: list[ReviewItem]) -> str:
    """将 ReviewItem 列表序列化为 review queue Markdown。"""
    if not items:
        return ""
    blocks: list[str] = []
    for item in items:
        data: dict[str, Any] = {
            "source_type": item.source_type,
            "source_path": item.source_path,
            "topic": item.topic,
            "root_cause": item.root_cause,
            "priority": item.priority,
            "status": item.status,
            "created_at": str(item.created_at) if item.created_at else None,
            "last_reviewed_at": str(item.last_reviewed_at) if item.last_reviewed_at else None,
            "next_review_at": str(item.next_review_at) if item.next_review_at else None,
            "interval_days": item.interval_days,
            "ease": item.ease,
            "reviews": item.reviews,
        }
        yaml_text = yaml.dump(data, default_flow_style=False, allow_unicode=True).strip()
        block = f"### {item.review_id}\n\n```yaml\n{yaml_text}\n```\n\nPrompt: {item.prompt}"
        if item.success_rule:
            block += f"\nSuccess rule: {item.success_rule}"
        blocks.append(block)
    return "\n\n".join(blocks) + "\n"


def is_due(item: ReviewItem, today: date) -> bool:
    """判断复习项是否到期（next_review_at <= today 或 None）。"""
    if item.next_review_at is None:
        return True
    if item.status == "completed":
        return False
    return item.next_review_at <= today


def schedule_next_review(
    item: ReviewItem,
    outcome: str,
    today: date,
    exam_date: date | None = None,
) -> ReviewItem:
    """根据 SM-2 简化规则计算下一次复习计划。

    Outcomes: again (1d), hard (2d), good (*2), easy (*3)
    """
    outcome = outcome.lower()
    if outcome == "again":
        new_interval = 1
        new_ease = max(1.3, item.ease - 0.2)
    elif outcome == "hard":
        new_interval = 2
        new_ease = max(1.3, item.ease - 0.15)
    elif outcome == "good":
        if item.reviews == 0:
            new_interval = 1
        else:
            new_interval = item.interval_days * 2
        new_ease = item.ease
    elif outcome == "easy":
        new_interval = item.interval_days * 3
        new_ease = item.ease + 0.15
    else:
        raise ValueError(f"未知复习结果: {outcome!r}，可选: again, hard, good, easy")

    # 用考试日期做上限
    if exam_date is not None:
        days_to_exam = (exam_date - today).days
        if days_to_exam > 0:
            new_interval = min(new_interval, days_to_exam)

    next_date = today.replace()  # copy
    try:
        from datetime import timedelta
        next_date = today + timedelta(days=new_interval)
    except OverflowError:
        next_date = today

    return ReviewItem(
        review_id=item.review_id,
        source_type=item.source_type,
        source_path=item.source_path,
        topic=item.topic,
        root_cause=item.root_cause,
        priority=item.priority,
        status="due" if new_interval <= 1 else "scheduled",
        created_at=item.created_at,
        last_reviewed_at=today,
        next_review_at=next_date,
        interval_days=new_interval,
        ease=round(new_ease, 2),
        reviews=item.reviews + 1,
        prompt=item.prompt,
        success_rule=item.success_rule,
    )
