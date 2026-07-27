#!/usr/bin/env python3
"""Extract readable Markdown and embedded media from OOXML Office files.

Supports .docx, .pptx and .ppsx with Python's standard library. The converter
does not execute macros, external links or embedded objects. Its output is an
internal evidence-scanning aid rather than a layout-faithful document renderer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable
from xml.etree import ElementTree as ET


SUPPORTED_SUFFIXES = {".docx", ".pptx", ".ppsx"}
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
MAX_MEMBER_BYTES = 64 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert .docx/.pptx/.ppsx files to Markdown for evidence scanning"
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Office files to convert")
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory for Markdown and extracted media",
    )
    parser.add_argument("--manifest", type=Path, help="Optional JSON manifest path")
    parser.add_argument(
        "--max-uncompressed-mb",
        type=int,
        default=256,
        help="Reject archives exceeding this total uncompressed size",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def natural_number(path: str) -> tuple[int, str]:
    match = re.search(r"(\d+)(?=\.xml$)", path)
    return (int(match.group(1)) if match else 10**9, path)


def read_member(archive: zipfile.ZipFile, name: str) -> bytes:
    info = archive.getinfo(name)
    if info.file_size > MAX_MEMBER_BYTES:
        raise ValueError(f"archive member is too large: {name}")
    return archive.read(name)


def validate_archive(archive: zipfile.ZipFile, max_uncompressed_mb: int) -> None:
    limit = max_uncompressed_mb * 1024 * 1024
    total = sum(item.file_size for item in archive.infolist())
    if total > limit:
        raise ValueError(
            f"uncompressed archive size {total} exceeds configured limit {limit}"
        )


def text_from_element(element: ET.Element, text_namespace: str) -> str:
    parts: list[str] = []
    for node in element.iter():
        name = local_name(node.tag)
        if node.tag == f"{{{text_namespace}}}t" and node.text:
            parts.append(node.text)
        elif name == "tab":
            parts.append("\t")
        elif name in {"br", "cr"}:
            parts.append("\n")
    return "".join(parts).strip()


def docx_markdown(archive: zipfile.ZipFile, source_name: str) -> list[str]:
    xml = read_member(archive, "word/document.xml")
    root = ET.fromstring(xml)
    body = root.find(f".//{{{WORD_NS}}}body")
    lines = [
        f"# {Path(source_name).stem}",
        "",
        f"> 扫描来源：`{Path(source_name).name}`；此转换稿用于证据定位，不保证版式还原。",
        "",
    ]
    if body is None:
        return lines + ["（未提取到正文）", ""]

    for child in body:
        name = local_name(child.tag)
        if name == "p":
            value = text_from_element(child, WORD_NS)
            if value:
                style = child.find(f".//{{{WORD_NS}}}pStyle")
                style_value = ""
                if style is not None:
                    style_value = style.attrib.get(f"{{{WORD_NS}}}val", "")
                heading_match = re.search(r"(?:Heading|标题)\s*([1-6])", style_value, re.I)
                if heading_match:
                    lines.append("#" * int(heading_match.group(1)) + " " + value)
                else:
                    lines.append(value)
                lines.append("")
        elif name == "tbl":
            rows: list[list[str]] = []
            for row in child.findall(f".//{{{WORD_NS}}}tr"):
                cells = [
                    text_from_element(cell, WORD_NS).replace("|", "\\|")
                    for cell in row.findall(f"./{{{WORD_NS}}}tc")
                ]
                if cells:
                    rows.append(cells)
            if rows:
                width = max(len(row) for row in rows)
                normalized = [row + [""] * (width - len(row)) for row in rows]
                lines.append("| " + " | ".join(normalized[0]) + " |")
                lines.append("| " + " | ".join(["---"] * width) + " |")
                for row in normalized[1:]:
                    lines.append("| " + " | ".join(row) + " |")
                lines.append("")
    return lines


def pptx_markdown(archive: zipfile.ZipFile, source_name: str) -> list[str]:
    slide_names = sorted(
        (
            name
            for name in archive.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        ),
        key=natural_number,
    )
    note_names = sorted(
        (
            name
            for name in archive.namelist()
            if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)
        ),
        key=natural_number,
    )
    lines = [
        f"# {Path(source_name).stem}",
        "",
        f"> 扫描来源：`{Path(source_name).name}`；此转换稿用于证据定位，不保证版式还原。",
        "",
    ]
    for index, slide_name in enumerate(slide_names, start=1):
        lines.extend([f"## 幻灯片 {index}", ""])
        root = ET.fromstring(read_member(archive, slide_name))
        values = [
            (node.text or "").strip()
            for node in root.iter(f"{{{DRAWING_NS}}}t")
            if (node.text or "").strip()
        ]
        if values:
            lines.extend(f"- {value}" for value in values)
        else:
            lines.append("（未提取到文本）")
        lines.append("")
        if index <= len(note_names):
            note_root = ET.fromstring(read_member(archive, note_names[index - 1]))
            note_values = [
                (node.text or "").strip()
                for node in note_root.iter(f"{{{DRAWING_NS}}}t")
                if (node.text or "").strip()
            ]
            note_values = [
                value
                for value in note_values
                if value.lower() not in {"slide image", "text placeholder"}
            ]
            if note_values:
                lines.extend(["### 备注", "", " ".join(note_values), ""])
    return lines


def unique_output_path(output_dir: Path, stem: str, suffix: str) -> Path:
    candidate = output_dir / f"{stem}{suffix}"
    index = 2
    while candidate.exists():
        candidate = output_dir / f"{stem}_{index}{suffix}"
        index += 1
    return candidate


def extract_media(
    archive: zipfile.ZipFile, prefix: str, output_dir: Path
) -> list[dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for name in sorted(archive.namelist()):
        if not name.startswith(prefix) or name.endswith("/"):
            continue
        basename = PurePosixPath(name).name
        if not basename:
            continue
        data = read_member(archive, name)
        destination = unique_output_path(output_dir, Path(basename).stem, Path(basename).suffix)
        destination.write_bytes(data)
        rows.append(
            {
                "archive_path": name,
                "output": str(destination),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return rows


def convert_one(
    input_path: Path, output_dir: Path, max_uncompressed_mb: int
) -> dict[str, object]:
    source = input_path.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"input file does not exist: {source}")
    suffix = source.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"unsupported file type: {source.suffix}")

    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = unique_output_path(output_dir, source.stem, ".md")
    media_dir = output_dir / f"{markdown_path.stem}_media"
    with zipfile.ZipFile(source) as archive:
        validate_archive(archive, max_uncompressed_mb)
        if suffix == ".docx":
            lines = docx_markdown(archive, source.name)
            media = extract_media(archive, "word/media/", media_dir)
        else:
            lines = pptx_markdown(archive, source.name)
            media = extract_media(archive, "ppt/media/", media_dir)

    if media:
        lines.extend(["## 嵌入媒体", ""])
        for item in media:
            media_path = Path(str(item["output"]))
            rel = media_path.relative_to(markdown_path.parent).as_posix()
            lines.append(f"- [{media_path.name}]({rel})")
        lines.append("")

    markdown_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "input": str(source),
        "input_sha256": sha256_file(source),
        "type": suffix.lstrip("."),
        "markdown": str(markdown_path),
        "media": media,
    }


def write_manifest(path: Path, converted: Iterable[dict[str, object]]) -> None:
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "converter": "office_to_markdown.py",
        "files": list(converted),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    converted: list[dict[str, object]] = []
    failures: list[str] = []
    for input_path in args.inputs:
        try:
            result = convert_one(input_path, args.output_dir, args.max_uncompressed_mb)
            converted.append(result)
            print(f"Converted: {result['markdown']}")
        except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
            failures.append(f"{input_path}: {exc}")
            print(f"ERROR: {input_path}: {exc}", file=sys.stderr)
    if args.manifest:
        write_manifest(args.manifest, converted)
        print(f"Manifest: {args.manifest}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
