"""rebuild_index.py — CLI 全量重建向量索引 + FTS 词法索引。

用法:
    python -m exam_memory.rebuild_index                # 全量重建
    python -m exam_memory.rebuild_index --type 算法    # 只重建指定类型
    python -m exam_memory.rebuild_index --force        # 强制覆盖已有索引
    python -m exam_memory.rebuild_index --fts-only     # 仅重建 FTS
    python -m exam_memory.rebuild_index --vec-only     # 仅重建向量
    python -m exam_memory.rebuild_index --dry-run      # 预览不写入
"""
from __future__ import annotations

import argparse
import glob
import sys
from datetime import datetime, timezone
from pathlib import Path


def _parse_fp(fp: str, source_dir: str):
    text = Path(fp).read_text(encoding="utf-8")
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        try:
            import yaml
            meta = yaml.safe_load(parts[1]) or {}
        except Exception:
            pass
        body = parts[2].strip() if len(parts) >= 3 else ""
    name = Path(fp).name
    meta["file_name"] = name
    meta["source_dir"] = source_dir
    meta["canonical_key"] = f"{source_dir}/{name}"
    meta.setdefault("id", name)
    return meta, body


def _iter_entry_files(base_dir: Path, source_dirs: list[str], type_filter: str | None):
    """Yield parsed entries from allowed data directories."""
    for source_dir in source_dirs:
        data_dir = base_dir / source_dir
        for fp in glob.glob(str(data_dir / "*.md")):
            path = Path(fp)
            if path.name.upper() == "README.MD":
                continue
            meta, body = _parse_fp(fp, source_dir)
            if not meta.get("type"):
                continue
            if type_filter and meta.get("type") != type_filter:
                continue
            yield path, meta, body


def main() -> int:
    ap = argparse.ArgumentParser(
        description="exam-memory 索引全量重建"
    )
    ap.add_argument("--type", choices=["单选题", "多选题", "算法"],
                    help="仅重建指定类型")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--fts-only", action="store_true")
    ap.add_argument("--vec-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-bank", action="store_true",
                    help="兼容旧调用；默认已包含 bank/")
    ap.add_argument("--bank-only", action="store_true",
                    help="仅重建 bank/ 题库索引")
    args = ap.parse_args()

    from exam_memory.vector_store import BASE_DIR, NumpyVectorStore
    from exam_memory.fts_store import FTSStore
    from exam_memory.embedding import is_available, encode

    type_filter = args.type
    source_dirs = ["bank"] if args.bank_only else ["experiences", "bank"]

    entries = list(_iter_entry_files(BASE_DIR, source_dirs, type_filter))
    files = [path for path, _, _ in entries]

    if not files:
        label = "bank/" if args.bank_only else "experiences/ + bank/"
        print(f"[rebuild] {label} 无可索引条目，无需重建")
        return 0

    docs = [(m, b) for _, m, b in entries]
    metas = [m for m, _ in docs]
    bodies = [b for _, b in docs]
    total_size = sum(len(b) for b in bodies)
    latest = max(path.stat().st_mtime for path in files)
    latest_str = datetime.fromtimestamp(latest, tz=timezone.utc).isoformat()
    source_label = "bank/" if args.bank_only else "experiences/ + bank/"

    print(f"[rebuild] 扫描到 {len(files)} 条条目（{source_label}，{type_filter or '全部'}）")
    print(f"[rebuild] 签名: count={len(files)}, size={total_size}, mtime={latest_str}")

    if args.dry_run:
        print("[rebuild] dry-run，不写入")
        return 0

    do_vec = not args.fts_only
    if do_vec:
        if not is_available():
            print("[rebuild] embedding 不可用，跳过向量（pip install '.[embed]'）",
                  file=sys.stderr)
        else:
            store = NumpyVectorStore()
            skip = not args.force and store.is_available and not args.vec_only
            if skip:
                print(f"[rebuild] 向量索引已存在（{store.count} 条），加 --force 覆盖")
            else:
                print(f"[rebuild] 编码 {len(bodies)} 条...")
                embs = encode(bodies)
                if embs is not None:
                    store._embs = embs.astype("float32")
                    store._meta = []
                    for i, m in enumerate(metas):
                        m.setdefault("signature", {})["file_count"] = len(files)
                        m.setdefault("signature", {})["total_size"] = total_size
                        m.setdefault("signature", {})["latest_mtime"] = latest_str
                        m["index_version"] = 1
                        store._meta.append(m)
                    store.save()
                    print(f"[rebuild] 向量完成: {len(metas)} 条, {store._embs.shape}")
                else:
                    print("[rebuild] 编码失败", file=sys.stderr)
                    return 1

    do_fts = not args.vec_only
    if do_fts:
        fts = FTSStore()
        n = fts.count()
        if n > 0 and not args.force:
            print(f"[rebuild] FTS 已存在（{n} 条），加 --force 覆盖")
        else:
            fts.clear()
            docs2 = [{"canonical_key": m.get("canonical_key", m.get("file_name", m.get("id", ""))),
                      "title": m.get("title", m.get("knowledge", "")),
                      "knowledge": m.get("knowledge", ""),
                      "content": b, "type": m.get("type", "")}
                     for m, b in docs]
            fts.upsert_many(docs2)
            print(f"[rebuild] FTS 完成: {len(docs2)} 条")
        fts.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
