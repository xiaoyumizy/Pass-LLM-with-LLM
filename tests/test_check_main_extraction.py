"""Tests for the main-extraction denylist gate."""

from types import SimpleNamespace

from scripts import check_main_extraction
from scripts.check_main_extraction import _git_staged, _matches_denylist


def test_target_wildcards_do_not_match_unrelated_target_files():
    allowed = [
        "targets/exam_config_template.md",
        "targets/ai-lab/exam_config.md",
        "targets/ai-lab/cheatsheets/math_fundamentals.md",
        "shared/exam_memory/server.py",
        "README.md",
    ]

    for path in allowed:
        assert _matches_denylist(path) is None


def test_target_file_wildcards_match_exact_single_target_segment():
    assert _matches_denylist("targets/ai-lab/mistake_log.md") == "targets/*/mistake_log.md"
    assert _matches_denylist(r"targets\ai-lab\mock_exam_log.md") == "targets/*/mock_exam_log.md"
    assert _matches_denylist("targets/foo/bar/mistake_log.md") is None


def test_target_directory_wildcards_match_directory_and_children():
    assert _matches_denylist("targets/ai-lab/progress") == "targets/*/progress/"
    assert _matches_denylist("targets/ai-lab/progress/rounds/r1.md") == "targets/*/progress/"
    assert _matches_denylist("targets/foo/bar/progress/r1.md") is None


def test_plain_directory_denylist_matches_nested_children():
    assert _matches_denylist("docs") == "docs/"
    assert _matches_denylist("docs/archive/dev-branch-review.md") == "docs/"


def test_git_staged_ignores_deletions(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(stdout="README.md\n")

    monkeypatch.setattr(check_main_extraction.subprocess, "run", fake_run)

    assert _git_staged() == ["README.md"]
    assert "--diff-filter=ACMRTUXB" in calls[0]
