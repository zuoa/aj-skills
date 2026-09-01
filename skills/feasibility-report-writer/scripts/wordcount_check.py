#!/usr/bin/env python3
"""Check each chapter of the feasibility report against its word-count hard limit.

Counting rule (matches references/report-template.md): per chapter, count
Chinese characters (CJK Unified Ideographs) + Arabic digits. Markdown markup,
punctuation, whitespace and latin letters are excluded.

Inputs (auto-detected):
  - a single assembled Markdown file: chapters are split by headings
    matching `^#{0,6}\\s*([一二三四五六])、`.
  - a directory of per-chapter files named `0N_*.md`: 01->一, 02->二, ...

Exit code 1 if any chapter exceeds its limit; 0 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Chapter numeral -> (display name, limit)
CHAPTERS = {
    "一": ("一　背景意义", 800),
    "二": ("二　国内外现状", 500),
    "三": ("三　工作基础", 1000),
    "四": ("四　关键技术与创新", 1000),
    "五": ("五　实施方案·技术路线·进度", 2000),
    "六": ("六　预期目标", 1000),
}
ORDER = ["一", "二", "三", "四", "五", "六"]
PREFIX_TO_NUMERAL = {"01": "一", "02": "二", "03": "三", "04": "四", "05": "五", "06": "六"}

# A chapter heading line: optional markdown hashes, then a Chinese numeral + 、
CHAPTER_HEADING_RE = re.compile(r"^\s*#{0,6}\s*([一二三四五六])、")
# A heading that ends the last chapter's accumulation (appendices).
TERMINATOR_RE = re.compile(r"^\s*#{1,6}\s*(参考文献|信源清单|页脚|附录)")
CJK_RE = re.compile(r"[一-鿿]")
DIGIT_RE = re.compile(r"[0-9]")


def count_chars(text: str) -> int:
    return len(CJK_RE.findall(text)) + len(DIGIT_RE.findall(text))


def strip_markup(line: str) -> str:
    # Remove markdown emphasis/heading markers/link URLs so they aren't counted.
    s = re.sub(r"^[#>\-\*\+\d\.\s]+", "", line)          # leading markers
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)        # links -> label
    s = re.sub(r"[`*_~]", "", s)                           # emphasis
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)            # images
    return s


def parse_file(path: Path) -> dict[str, int]:
    """Return {numeral: count} for chapters found in an assembled markdown file."""
    counts: dict[str, int] = {n: 0 for n in ORDER}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if TERMINATOR_RE.match(raw):
            current = None
            continue
        m = CHAPTER_HEADING_RE.match(raw)
        if m:
            current = m.group(1)
            continue
        if current is None:
            continue
        counts[current] += count_chars(strip_markup(raw))
    return counts


def parse_dir(path: Path) -> dict[str, int]:
    """Return {numeral: count} from per-chapter files 0N_*.md in a directory."""
    counts: dict[str, int] = {n: 0 for n in ORDER}
    for f in sorted(path.glob("*.md")):
        prefix = f.stem.split("_", 1)[0]
        numeral = PREFIX_TO_NUMERAL.get(prefix)
        if not numeral:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        counts[numeral] += count_chars(" ".join(strip_markup(l) for l in text.splitlines()))
    return counts


def main() -> int:
    p = argparse.ArgumentParser(description="Check chapter word counts against hard limits")
    p.add_argument("--input", required=True, type=Path,
                   help="Assembled report .md file, or a directory of 0N_*.md chapter files")
    p.add_argument("--report", type=Path,
                   help="Optional path to write/merge a quality_report.json wordcount block")
    args = p.parse_args()

    src = args.input.resolve()
    if src.is_dir():
        counts = parse_dir(src)
        source_label = f"dir:{src}"
    elif src.is_file():
        counts = parse_file(src)
        source_label = f"file:{src}"
    else:
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    rows = []
    over = 0
    for n in ORDER:
        name, limit = CHAPTERS[n]
        actual = counts.get(n, 0)
        ok = actual <= limit
        if not ok:
            over += 1
        rows.append((name, actual, limit, "pass" if ok else "OVER"))

    width_name = max(len(r[0]) for r in rows)
    print(f"字数校验　来源：{source_label}")
    print("-" * 52)
    print(f"{'章节'.ljust(width_name)}  {'实际':>6}  {'上限':>6}   结果")
    print("-" * 52)
    for name, actual, limit, res in rows:
        print(f"{name.ljust(width_name)}  {actual:>6}  {limit:>6}   {res}")
    print("-" * 52)
    print("结论：" + ("全部达标 ✓" if over == 0 else f"{over} 章超限 ✗"))

    if args.report:
        block = {
            "source": source_label,
            "chapters": {
                CHAPTERS[n][0]: {"actual": counts.get(n, 0), "limit": CHAPTERS[n][1],
                                 "pass": counts.get(n, 0) <= CHAPTERS[n][1]}
                for n in ORDER
            },
            "pass": over == 0,
        }
        existing = {}
        if args.report.exists():
            try:
                existing = json.loads(args.report.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                existing = {}
        existing["wordcount"] = block
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"已写入字数校验结果：{args.report}")

    return 1 if over else 0


if __name__ == "__main__":
    raise SystemExit(main())
