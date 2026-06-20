"""Tests for rebuild_index CLI source selection."""

from __future__ import annotations

import sys

from exam_memory.fts_store import FTSStore
from exam_memory import fts_store, vector_store
from exam_memory import rebuild_index


def _write_entry(path, q_type="算法", knowledge="哈希表", body="hash table content"):
    path.write_text(
        f"---\ntype: {q_type}\nknowledge: {knowledge}\ntitle: {knowledge}\n---\n\n## {knowledge}\n\n{body}\n",
        encoding="utf-8",
    )


def _prepare_base(tmp_path, monkeypatch):
    base = tmp_path / "exam_memory"
    (base / "experiences").mkdir(parents=True)
    (base / "bank").mkdir()
    (base / "vectorstore").mkdir()
    db_path = base / "vectorstore" / "fts.sqlite"
    monkeypatch.setattr(vector_store, "BASE_DIR", base)
    monkeypatch.setattr(fts_store, "DB_PATH", db_path)
    return base, db_path


def _run_rebuild(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["rebuild_index", *args])
    return rebuild_index.main()


def test_rebuild_default_indexes_experiences_and_bank(tmp_path, monkeypatch):
    base, db_path = _prepare_base(tmp_path, monkeypatch)
    _write_entry(base / "experiences" / "exp.md", knowledge="经验", body="experience token")
    _write_entry(base / "bank" / "bank.md", knowledge="题库", body="bank token")
    (base / "bank" / "README.md").write_text("# index\n", encoding="utf-8")

    assert _run_rebuild(monkeypatch, "--fts-only", "--force") == 0

    store = FTSStore(db_path=db_path)
    try:
        assert store.count() == 2
        assert store.search("experience")[0]["canonical_key"] == "experiences/exp.md"
        assert store.search("bank")[0]["canonical_key"] == "bank/bank.md"
    finally:
        store.close()


def test_rebuild_bank_only_indexes_bank_entries(tmp_path, monkeypatch):
    base, db_path = _prepare_base(tmp_path, monkeypatch)
    _write_entry(base / "experiences" / "exp.md", knowledge="经验", body="experience token")
    _write_entry(base / "bank" / "bank.md", knowledge="题库", body="bank token")

    assert _run_rebuild(monkeypatch, "--fts-only", "--force", "--bank-only") == 0

    store = FTSStore(db_path=db_path)
    try:
        assert store.count() == 1
        assert store.search("experience") == []
        assert store.search("bank")[0]["canonical_key"] == "bank/bank.md"
    finally:
        store.close()


def test_rebuild_type_filter_applies_to_all_sources(tmp_path, monkeypatch):
    base, db_path = _prepare_base(tmp_path, monkeypatch)
    _write_entry(base / "experiences" / "algo.md", q_type="算法", knowledge="算法", body="algo token")
    _write_entry(base / "bank" / "choice.md", q_type="单选题", knowledge="选择", body="choice token")

    assert _run_rebuild(monkeypatch, "--fts-only", "--force", "--type", "单选题") == 0

    store = FTSStore(db_path=db_path)
    try:
        assert store.count() == 1
        hit = store.search("choice")[0]
        assert hit["canonical_key"] == "bank/choice.md"
        assert hit["type"] == "单选题"
    finally:
        store.close()
