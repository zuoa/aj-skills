#!/usr/bin/env python3
"""Extract readable Markdown from Office files for the feasibility-report skill.

Supports:
  - .docx / .pptx / .ppsx : OOXML, parsed with the standard library (zipfile + ET),
    including embedded media extraction.
  - .doc (legacy binary)  : converted via macOS `textutil` to .txt, then wrapped as
    Markdown. Media is not extracted for legacy .doc. If `textutil` is unavailable,
    a clear error is raised so the caller can fall back (e.g. LibreOffice).

Output is an evidence-scanning aid, not a layout-faithful renderer.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable
from xml.etree import ElementTree as ET

OOXML_SUFFIXES = {".docx", ".pptx", ".ppsx"}
LEGACY_SUFFIXES = {".doc", ".ppt"}
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
MAX_MEMBER_BYTES = 64 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Convert .doc/.docx/.ppt/.pptx files to Markdown for evidence scanning"
    )
    p.add_argument("inputs", nargs="+", type=Path, help="Office files to convert")
    p.add_argument("--output-dir", required=True, type=Path, help="Output directory")
    p.add_argument("--manifest", type=Path, help="Optional JSON manifest path")
    p.add_argument(
        "--max-uncompressed-mb", type=int, default=256,
        help="Reject OOXML archives exceeding this total uncompressed size",
    )
    return p.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as h:
        for chunk in iter(lambda: h.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def natural_number(path: str) -> tuple[int, str]:
    m = re.search(r"(\d+)(?=\.xml$)", path)
    return (int(m.group(1)) if m else 10 ** 9, path)


def read_member(archive: zipfile.ZipFile, name: str) -> bytes:
    info = archive.getinfo(name)
    if info.file_size > MAX_MEMBER_BYTES:
        raise ValueError(f"archive member too large: {name}")
    return archive.read(name)


def validate_archive(archive: zipfile.ZipFile, max_uncompressed_mb: int) -> None:
    limit = max_uncompressed_mb * 1024 * 1024
    total = sum(it.file_size for it in archive.infolist())
    if total > limit:
        raise ValueError(f"uncompressed size {total} exceeds limit {limit}")


def text_from_element(element: ET.Element, ns: str) -> str:
    parts: list[str] = []
    for node in element.iter():
        name = local_name(node.tag)
        if node.tag == f"{{{ns}}}t" and node.text:
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
                sv = style.attrib.get(f"{{{WORD_NS}}}val", "") if style is not None else ""
                hm = re.search(r"(?:Heading|标题)\s*([1-6])", sv, re.I)
                if hm:
                    lines.append("#" * int(hm.group(1)) + " " + value)
                else:
                    lines.append(value)
                lines.append("")
        elif name == "tbl":
            rows: list[list[str]] = []
            for row in child.findall(f".//{{{WORD_NS}}}tr"):
                cells = [
                    text_from_element(c, WORD_NS).replace("|", "\\|")
                    for c in row.findall(f"./{{{WORD_NS}}}tc")
                ]
                if cells:
                    rows.append(cells)
            if rows:
                width = max(len(r) for r in rows)
                norm = [r + [""] * (width - len(r)) for r in rows]
                lines.append("| " + " | ".join(norm[0]) + " |")
                lines.append("| " + " | ".join(["---"] * width) + " |")
                for r in norm[1:]:
                    lines.append("| " + " | ".join(r) + " |")
                lines.append("")
    return lines


def pptx_markdown(archive: zipfile.ZipFile, source_name: str) -> list[str]:
    slide_names = sorted(
        (n for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
        key=natural_number,
    )
    note_names = sorted(
        (n for n in archive.namelist() if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)),
        key=natural_number,
    )
    lines = [
        f"# {Path(source_name).stem}",
        "",
        f"> 扫描来源：`{Path(source_name).name}`；此转换稿用于证据定位，不保证版式还原。",
        "",
    ]
    for idx, slide_name in enumerate(slide_names, start=1):
        lines.extend([f"## 幻灯片 {idx}", ""])
        root = ET.fromstring(read_member(archive, slide_name))
        values = [
            (n.text or "").strip()
            for n in root.iter(f"{{{DRAWING_NS}}}t")
            if (n.text or "").strip()
        ]
        lines.extend((f"- {v}" for v in values) if values else ["（未提取到文本）"])
        lines.append("")
        if idx <= len(note_names):
            nr = ET.fromstring(read_member(archive, note_names[idx - 1]))
            nv = [
                (n.text or "").strip()
                for n in nr.iter(f"{{{DRAWING_NS}}}t")
                if (n.text or "").strip()
                and (n.text or "").strip().lower() not in {"slide image", "text placeholder"}
            ]
            if nv:
                lines.extend(["### 备注", "", " ".join(nv), ""])
    return lines


def unique_output_path(output_dir: Path, stem: str, suffix: str) -> Path:
    candidate = output_dir / f"{stem}{suffix}"
    i = 2
    while candidate.exists():
        candidate = output_dir / f"{stem}_{i}{suffix}"
        i += 1
    return candidate


def extract_media(archive: zipfile.ZipFile, prefix: str, output_dir: Path) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for name in sorted(archive.namelist()):
        if not name.startswith(prefix) or name.endswith("/"):
            continue
        base = PurePosixPath(name).name
        if not base:
            continue
        data = read_member(archive, name)
        dest = unique_output_path(output_dir, Path(base).stem, Path(base).suffix)
        dest.write_bytes(data)
        rows.append({
            "archive_path": name, "output": str(dest),
            "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        })
    return rows


def convert_legacy(source: Path, output_dir: Path) -> dict:
    """Convert legacy .doc/.ppt via macOS textutil to plain text, wrap as markdown."""
    if shutil.which("textutil") is None:
        raise ValueError(
            "legacy .doc/.ppt conversion needs macOS `textutil` (not found). "
            "Convert to .docx first (e.g. LibreOffice: `soffice --convert-to docx`)."
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp_txt = Path(td) / (source.stem + ".txt")
        subprocess.run(
            ["textutil", "-convert", "txt", "-encoding", "UTF-8",
             "-output", str(tmp_txt), str(source)],
            check=True, capture_output=True,
        )
        text = tmp_txt.read_text(encoding="utf-8", errors="replace") if tmp_txt.exists() else ""

    md_path = unique_output_path(output_dir, source.stem, ".md")
    lines = [
        f"# {source.stem}",
        "",
        f"> 扫描来源：`{source.name}`（legacy {source.suffix}，经 textutil 转 txt）；用于证据定位，不保证版式还原。",
        "",
        text.strip(),
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "input": str(source), "input_sha256": sha256_file(source),
        "type": source.suffix.lstrip("."), "markdown": str(md_path), "media": [],
    }


def convert_one(input_path: Path, output_dir: Path, max_uncompressed_mb: int) -> dict:
    source = input_path.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"input file does not exist: {source}")
    suffix = source.suffix.lower()

    if suffix in LEGACY_SUFFIXES:
        return convert_legacy(source, output_dir)
    if suffix not in OOXML_SUFFIXES:
        raise ValueError(f"unsupported file type: {source.suffix}")

    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = unique_output_path(output_dir, source.stem, ".md")
    media_dir = output_dir / f"{md_path.stem}_media"
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
            mp = Path(str(item["output"]))
            rel = mp.relative_to(md_path.parent).as_posix()
            lines.append(f"- [{mp.name}]({rel})")
        lines.append("")

    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {
        "input": str(source), "input_sha256": sha256_file(source),
        "type": suffix.lstrip("."), "markdown": str(md_path), "media": media,
    }


def write_manifest(path: Path, converted: Iterable[dict]) -> None:
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "converter": "office_to_markdown.py",
        "files": list(converted),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    converted: list[dict] = []
    failures: list[str] = []
    for input_path in args.inputs:
        try:
            result = convert_one(input_path, args.output_dir, args.max_uncompressed_mb)
            converted.append(result)
            print(f"Converted: {result['markdown']}")
        except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError, subprocess.CalledProcessError) as exc:
            failures.append(f"{input_path}: {exc}")
            print(f"ERROR: {input_path}: {exc}", file=sys.stderr)
    if args.manifest:
        write_manifest(args.manifest, converted)
        print(f"Manifest: {args.manifest}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
