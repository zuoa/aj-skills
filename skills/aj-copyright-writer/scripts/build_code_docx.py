#!/usr/bin/env python3
"""Build a source-code docx from numbered 05.code/*.txt files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_outputs import ValidationError, validate_code_files, validate_file_exists


def import_docx():
    try:
        from docx import Document
        from docx.enum.style import WD_STYLE_TYPE
        from docx.shared import Pt
    except ImportError as exc:
        raise SystemExit("Missing dependency: pip install python-docx") from exc
    return Document, WD_STYLE_TYPE, Pt


def resolve_template(template: str | None, cwd: Path) -> Path | None:
    if template:
        path = Path(template).expanduser()
        if path.exists():
            return path
    names = ["代码文档模版.docx", "代码文档模板.docx", "操作手册模版.docx", "操作手册模板.docx"]
    roots = [
        cwd / "reference",
        cwd / "refence",
        cwd / "refrence",
        Path.home() / "aj-skills" / "reference",
        Path.home() / "aj-skills" / "refence",
        Path.home() / "aj-skills" / "refrence",
    ]
    for root in roots:
        for name in names:
            candidate = root / name
            if candidate.exists():
                return candidate
    return None


def ensure_code_style(document, style_type, pt):
    styles = document.styles
    try:
        style = styles["AJ Code"]
    except KeyError:
        style = styles.add_style("AJ Code", style_type.PARAGRAPH)
    style.font.name = "Consolas"
    style.font.size = pt(8.5)
    return style


def module_title(path: Path, text: str) -> str:
    for line in text.splitlines()[:10]:
        stripped = line.strip()
        if stripped.startswith("// 模块:"):
            return stripped.replace("// 模块:", "").strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    if "-" in path.stem:
        return path.stem.split("-", 1)[1]
    return path.stem


def add_code_lines(document, text: str, style_name: str, line_numbers: bool) -> None:
    for number, line in enumerate(text.splitlines(), start=1):
        paragraph = document.add_paragraph(style=style_name)
        if line_numbers:
            paragraph.add_run(f"{number:04d}  ")
        paragraph.add_run(line if line else " ")


def code_files(code_dir: Path) -> list[Path]:
    return validate_code_files(code_dir)


def infer_software_name(output_path: Path) -> str:
    stem = output_path.stem
    if stem.endswith("_代码"):
        return stem[: -len("_代码")]
    return stem


def build_docx(
    code_dir: Path,
    output_path: Path,
    template_path: Path | None,
    line_numbers: bool,
    software_name: str | None,
) -> None:
    Document, style_type, pt = import_docx()
    document = Document(str(template_path)) if template_path else Document()
    if template_path and any(p.text.strip() for p in document.paragraphs):
        document.add_page_break()

    ensure_code_style(document, style_type, pt)
    document.add_heading(software_name or infer_software_name(output_path), level=1)

    for path in code_files(code_dir):
        text = path.read_text(encoding="utf-8")
        document.add_page_break()
        clean_title = re.sub(r"\s+", " ", module_title(path, text))
        document.add_heading(f"{path.stem}. {clean_title}", level=2)
        add_code_lines(document, text, "AJ Code", line_numbers)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))
    validate_file_exists(output_path, "code docx")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--template")
    parser.add_argument("--software-name")
    parser.add_argument("--line-numbers", action="store_true")
    args = parser.parse_args()

    template_path = resolve_template(args.template, Path.cwd())
    if template_path:
        print(f"Using template: {template_path}")
    else:
        print("Template not found; generating code docx without template.")
    try:
        build_docx(args.code_dir, args.output, template_path, args.line_numbers, args.software_name)
    except ValidationError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
