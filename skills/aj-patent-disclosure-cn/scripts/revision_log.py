#!/usr/bin/env python3
"""Append immutable Markdown and JSONL records for disclosure revisions."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


KINDS = ("supplement", "correction", "strategy", "format")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a patent disclosure revision record")
    parser.add_argument("--case-dir", required=True, type=Path)
    parser.add_argument("--kind", required=True, choices=KINDS)
    parser.add_argument("--base", type=Path, help="Previous disclosure file")
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        type=Path,
        help="New artifact; repeat for multiple files",
    )
    parser.add_argument("--changed-section", action="append", default=[])
    parser.add_argument("--summary", required=True)
    parser.add_argument("--search-impact", default="未说明")
    parser.add_argument("--claim-impact", default="未说明")
    parser.add_argument("--figure-impact", default="未说明")
    parser.add_argument("--redaction-impact", default="未说明")
    parser.add_argument("--log-name", default="revision_history.md")
    parser.add_argument("--jsonl-name", default="revision_history.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path | None, case_dir: Path) -> dict[str, Any] | None:
    if path is None:
        return None
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise ValueError(f"file does not exist: {resolved}")
    try:
        display = str(resolved.relative_to(case_dir))
    except ValueError:
        display = str(resolved)
    return {
        "path": display,
        "sha256": sha256_file(resolved),
        "size": resolved.stat().st_size,
    }


def build_record(args: argparse.Namespace, case_dir: Path) -> dict[str, Any]:
    now_local = datetime.now().astimezone()
    now_utc = datetime.now(timezone.utc)
    base = file_record(args.base, case_dir)
    artifacts = [file_record(path, case_dir) for path in args.artifact]
    return {
        "revision_id": now_utc.strftime("rev-%Y%m%dT%H%M%S.%fZ"),
        "time_local": now_local.isoformat(),
        "time_utc": now_utc.isoformat(),
        "kind": args.kind,
        "base": base,
        "artifacts": artifacts,
        "changed_sections": [item.strip() for item in args.changed_section if item.strip()],
        "summary": args.summary.strip(),
        "impacts": {
            "search": args.search_impact.strip(),
            "claims": args.claim_impact.strip(),
            "figures": args.figure_impact.strip(),
            "redaction": args.redaction_impact.strip(),
        },
    }


def markdown_record(record: dict[str, Any]) -> str:
    base = record["base"]
    base_line = (
        f"`{base['path']}` · SHA-256 `{base['sha256']}`" if base else "（无基线文件）"
    )
    artifact_lines = (
        "\n".join(
            f"- `{item['path']}` · SHA-256 `{item['sha256']}`"
            for item in record["artifacts"]
            if item
        )
        or "- （未登记交付物）"
    )
    sections = "、".join(record["changed_sections"]) or "未列明"
    impacts = record["impacts"]
    return f"""## {record['revision_id']}

- 本地时间：{record['time_local']}
- UTC：{record['time_utc']}
- 类型：{record['kind']}
- 基线：{base_line}
- 修改章节：{sections}

**修改摘要**

{record['summary']}

**影响检查**

- 检索：{impacts['search']}
- 拟保护主题：{impacts['claims']}
- 附图：{impacts['figures']}
- 脱敏：{impacts['redaction']}

**本轮交付物**

{artifact_lines}

---

"""


def append_record(case_dir: Path, args: argparse.Namespace, record: dict[str, Any]) -> None:
    markdown_path = case_dir / args.log_name
    jsonl_path = case_dir / args.jsonl_name
    header = "# 技术交底书修订历史\n\n"
    if not markdown_path.exists():
        markdown_path.write_text(header, encoding="utf-8")
    with markdown_path.open("a", encoding="utf-8") as handle:
        handle.write(markdown_record(record))
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"Markdown log: {markdown_path}")
    print(f"JSONL log: {jsonl_path}")


def main() -> int:
    args = parse_args()
    case_dir = args.case_dir.expanduser().resolve()
    if not case_dir.is_dir():
        print(f"ERROR: case directory does not exist: {case_dir}", file=sys.stderr)
        return 2
    try:
        record = build_record(args, case_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.dry_run:
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0
    append_record(case_dir, args, record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
