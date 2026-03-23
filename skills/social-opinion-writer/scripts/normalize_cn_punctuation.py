#!/usr/bin/env python3
"""Normalize common Chinese punctuation in markdown prose."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

CJK = r"\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"
PUNCT_LEFT_CONTEXT = CJK + r"》）】”"
INLINE_CODE_OR_FENCE = re.compile(r"(```[\s\S]*?```|`[^`\n]+`)")


def normalize_markdown_text(text: str) -> str:
    parts: list[str] = []
    last = 0
    for match in INLINE_CODE_OR_FENCE.finditer(text):
        parts.append(_normalize_prose(text[last : match.start()]))
        parts.append(match.group(0))
        last = match.end()
    parts.append(_normalize_prose(text[last:]))
    return "".join(parts)


def _normalize_prose(text: str) -> str:
    text = _replace_paired_quotes(text)
    text = re.sub(rf"\(([^()\n]*[{CJK}][^()\n]*)\)", r"（\1）", text)

    replacements = {
        ",": "，",
        ":": "：",
        ";": "；",
        "?": "？",
        "!": "！",
    }
    for ascii_punct, cn_punct in replacements.items():
        text = re.sub(
            rf"(?<=[{PUNCT_LEFT_CONTEXT}]){re.escape(ascii_punct)}",
            cn_punct,
            text,
        )
    text = re.sub(rf"(?<=[{PUNCT_LEFT_CONTEXT}])\.", "。", text)
    return text


def _replace_paired_quotes(text: str) -> str:
    result: list[str] = []
    open_quote = True
    for char in text:
        if char == '"':
            result.append("“" if open_quote else "”")
            open_quote = not open_quote
        else:
            result.append(char)
    return "".join(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to the markdown file")
    parser.add_argument("--output", help="Path to write the normalized markdown")
    parser.add_argument("--in-place", action="store_true", help="Rewrite the input file")
    args = parser.parse_args()

    if args.output and args.in_place:
        raise SystemExit("--output and --in-place cannot be used together.")

    input_path = Path(args.input)
    text = input_path.read_text(encoding="utf-8")
    normalized = normalize_markdown_text(text)

    if args.in_place:
        output_path = input_path
    else:
        output_path = Path(args.output) if args.output else input_path.with_name(f"{input_path.stem}-normalized{input_path.suffix}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(normalized, encoding="utf-8")
    print(f"Normalized punctuation written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
