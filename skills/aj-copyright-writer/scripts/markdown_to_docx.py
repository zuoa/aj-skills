#!/usr/bin/env python3
"""Convert a Markdown operation manual to docx, optionally using a template."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def import_docx():
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt
    except ImportError as exc:
        raise SystemExit("Missing dependency: pip install python-docx") from exc
    return Document, Inches, Pt, WD_ALIGN_PARAGRAPH


def resolve_template(template: str | None, cwd: Path) -> Path | None:
    candidates: list[Path] = []
    if template:
        candidates.append(Path(template).expanduser())
    names = ["操作手册模版.docx", "操作手册模板.docx"]
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
            candidates.append(root / name)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def add_table(document, lines: list[str]) -> None:
    rows = [split_table_row(line) for line in lines]
    rows = [row for row in rows if not is_separator_row(row)]
    if not rows:
        return
    cols = max(len(row) for row in rows)
    table = document.add_table(rows=0, cols=cols)
    table.style = "Table Grid"
    for row_cells in rows:
        row = table.add_row().cells
        for idx in range(cols):
            if idx < len(row_cells):
                add_inline_markdown(row[idx].paragraphs[0], row_cells[idx])


def add_image(document, markdown_image: re.Match[str], base_dir: Path, Inches) -> bool:
    alt = markdown_image.group(1).strip()
    raw_path = markdown_image.group(2).strip().strip("<>").strip('"').strip("'")
    image_path = Path(raw_path)
    if not image_path.is_absolute():
        image_path = (base_dir / image_path).resolve()
    if not image_path.exists():
        document.add_paragraph(f"[图片缺失: {alt} - {raw_path}]")
        return False
    document.add_picture(str(image_path), width=Inches(6.3))
    if alt:
        caption = document.add_paragraph()
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = caption.add_run(alt)
        run.font.size = Pt(10)
    return True


def add_code_block(document, code_lines: list[str]) -> None:
    for line in code_lines:
        paragraph = document.add_paragraph()
        run = paragraph.add_run(line if line else " ")
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)


def add_inline_markdown(paragraph, text: str) -> None:
    """Render a small subset of inline Markdown into docx runs."""
    pattern = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`)")
    pos = 0
    for match in pattern.finditer(text):
        if match.start() > pos:
            paragraph.add_run(text[pos : match.start()])
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
        pos = match.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def add_paragraph_with_inline(document, text: str, style: str | None = None):
    paragraph = document.add_paragraph(style=style) if style else document.add_paragraph()
    add_inline_markdown(paragraph, text)
    return paragraph


def convert_markdown(markdown_path: Path, output_path: Path, template_path: Path | None, auto_lists: bool = False) -> None:
    Document, Inches, imported_pt, imported_align = import_docx()
    global Pt, WD_ALIGN_PARAGRAPH
    Pt = imported_pt
    WD_ALIGN_PARAGRAPH = imported_align

    document = Document(str(template_path)) if template_path else Document()
    if template_path and any(p.text.strip() for p in document.paragraphs):
        document.add_page_break()

    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    i = 0
    in_code = False
    code_buffer: list[str] = []
    image_re = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                add_code_block(document, code_buffer)
                code_buffer = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buffer.append(line)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if is_table_line(line):
            table_lines = []
            while i < len(lines) and is_table_line(lines[i]):
                table_lines.append(lines[i])
                i += 1
            add_table(document, table_lines)
            continue

        image_match = image_re.fullmatch(stripped)
        if image_match:
            add_image(document, image_match, markdown_path.parent, Inches)
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            level = min(len(heading.group(1)), 4)
            document.add_heading(heading.group(2).strip(), level=level)
            i += 1
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        if bullet:
            if auto_lists:
                add_paragraph_with_inline(document, bullet.group(1), style="List Bullet")
            else:
                add_paragraph_with_inline(document, f"• {bullet.group(1)}")
            i += 1
            continue

        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if ordered:
            if auto_lists:
                add_paragraph_with_inline(document, ordered.group(1), style="List Number")
            else:
                add_paragraph_with_inline(document, stripped)
            i += 1
            continue

        add_paragraph_with_inline(document, stripped)
        i += 1

    if code_buffer:
        add_code_block(document, code_buffer)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--template")
    parser.add_argument(
        "--auto-lists",
        action="store_true",
        help="Use Word automatic bullet/numbered list styles. Default renders list markers as plain text for cleaner manuals.",
    )
    args = parser.parse_args()

    markdown_path = args.input
    template_path = resolve_template(args.template, Path.cwd())
    if template_path:
        print(f"Using template: {template_path}")
    else:
        print("Template not found; generating docx without template.")
    convert_markdown(markdown_path, args.output, template_path, args.auto_lists)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
