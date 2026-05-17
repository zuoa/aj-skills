#!/usr/bin/env python3
"""Validate numbered copyright material outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


EXPECTED_IDS = [f"{index:02d}" for index in range(1, 11)]
MIN_PROTOTYPE_FUNCTION_COVERAGE = 0.4
MAX_PROTOTYPE_FUNCTION_COVERAGE = 0.6
CODE_MIN_LINES = 120
CODE_MAX_LINES = 260
MAX_MANUAL_BODY_LIST_MARKERS = 35
ALLOWED_PROTOTYPE_STYLES = {
    "custom-command-system",
    "gov-service-light",
    "enterprise-data-station",
    "industrial-iot-cockpit",
    "medical-research-clean",
    "education-campus-portal",
    "finance-risk-terminal",
    "mobile-business-console",
}
INTERNAL_DOCUMENT_LABEL_PATTERNS = [
    re.compile(r"模块\s*(?:0?[1-9]|10)(?=\s*[：:、，,。\s\)\]）\-]|$)"),
    re.compile(r"(?:第\s*)?(?:0?[1-9]|10)\s*号?模块"),
    re.compile(r"功能点\s*(?:0?[1-9]|10)(?=\s*[：:、，,。\s\)\]）\-]|$)"),
    re.compile(r"(?:第\s*)?(?:0?[1-9]|10)\s*号?功能点"),
]
RIGID_MANUAL_LABEL_PATTERNS = [
    re.compile(r"^\s*(页面内容说明|页面区域说明|功能说明|操作前提|字段说明|按钮说明|操作步骤|操作过程|预期结果|异常提示)\s*[：:]"),
]
MANUAL_BODY_LIST_MARKER_PATTERN = re.compile(r"^\s*(?:[-*]\s+|\d+[.)、]\s+|[a-zA-Z]）、|[一二三四五六七八九十]+[、.)]\s*)")


class ValidationError(ValueError):
    pass


def validate_numbered_files(directory: Path, suffix: str, label: str, expected_ids: list[str] | None = None) -> list[Path]:
    expected_ids = expected_ids or EXPECTED_IDS
    if not directory.exists():
        raise ValidationError(f"{label}: directory does not exist: {directory}")
    if not directory.is_dir():
        raise ValidationError(f"{label}: path is not a directory: {directory}")

    files = sorted((path for path in directory.iterdir() if path.is_file() and path.suffix == suffix), key=lambda p: p.name)
    expected_names = [f"{file_id}{suffix}" for file_id in expected_ids]
    actual_names = [path.name for path in files]

    missing = [name for name in expected_names if name not in actual_names]
    extra = [name for name in actual_names if name not in expected_names]
    errors: list[str] = []
    if missing:
        errors.append(f"missing {', '.join(missing)}")
    if extra:
        errors.append(f"unexpected {', '.join(extra)}")
    if len(actual_names) != len(expected_names):
        errors.append(f"expected {len(expected_names)} files, found {len(actual_names)}")
    if errors:
        raise ValidationError(f"{label}: " + "; ".join(errors))
    return files


def module_function_counts(module_dir: Path) -> dict[str, int]:
    files = validate_numbered_files(module_dir, ".md", "modules")
    counts: dict[str, int] = {}
    for path in files:
        count = count_module_function_points(path.read_text(encoding="utf-8"))
        if count is None:
            raise ValidationError(f"modules function points: {path.name}: missing ## 功能点清单")
        counts[path.stem] = count
    return counts


def parse_prototype_id(file_id: str) -> tuple[str, str | None]:
    if file_id == "00-login":
        return "login", None
    if re.fullmatch(r"\d{2}", file_id):
        return file_id, None
    match = re.fullmatch(r"(\d{2})-(\d{2})", file_id)
    if match:
        return match.group(1), match.group(2)
    raise ValidationError(f"invalid prototype id {file_id!r}; expected 00-login, 01, or 01-01")


def expected_prototype_range(module_dir: Path | None) -> tuple[int, int, dict[str, int]]:
    if module_dir is None:
        return 11, 31, {}
    counts = module_function_counts(module_dir)
    total_function_points = sum(counts.values())
    min_count = 1 + len(EXPECTED_IDS) + max(1, int(total_function_points * MIN_PROTOTYPE_FUNCTION_COVERAGE + 0.9999))
    max_count = 1 + len(EXPECTED_IDS) + max(1, int(total_function_points * MAX_PROTOTYPE_FUNCTION_COVERAGE))
    return min_count, max_count, counts


def validate_prototype_files(directory: Path, suffix: str, label: str, module_dir: Path | None = None) -> list[Path]:
    if not directory.exists():
        raise ValidationError(f"{label}: directory does not exist: {directory}")
    if not directory.is_dir():
        raise ValidationError(f"{label}: path is not a directory: {directory}")

    files = sorted((path for path in directory.iterdir() if path.is_file() and path.suffix == suffix), key=lambda p: p.name)
    ids = [path.stem for path in files]
    errors: list[str] = []
    if "00-login" not in ids:
        errors.append(f"missing 00-login{suffix}")
    for module_id in EXPECTED_IDS:
        if module_id not in ids:
            errors.append(f"missing module overview {module_id}{suffix}")

    min_count, max_count, function_counts = expected_prototype_range(module_dir)
    if len(files) < min_count or len(files) > max_count:
        errors.append(f"expected {min_count}-{max_count} prototype files, found {len(files)}")

    covered_function_points: set[tuple[str, str]] = set()
    seen_ids: set[str] = set()
    for file_id in ids:
        if file_id in seen_ids:
            errors.append(f"duplicate id {file_id}")
        seen_ids.add(file_id)
        try:
            module_id, function_id = parse_prototype_id(file_id)
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        if module_id == "login":
            continue
        if module_id not in EXPECTED_IDS:
            errors.append(f"{file_id}: module id must be 01-10")
            continue
        if function_id is not None:
            function_count = function_counts.get(module_id)
            if function_count is not None:
                max_function_id = f"{function_count:02d}"
                if function_id < "01" or function_id > max_function_id:
                    errors.append(f"{file_id}: function id must be 01-{max_function_id} for module {module_id}")
            covered_function_points.add((module_id, function_id))

    if function_counts:
        total_function_points = sum(function_counts.values())
        min_covered = max(1, int(total_function_points * MIN_PROTOTYPE_FUNCTION_COVERAGE + 0.9999))
        max_covered = max(1, int(total_function_points * MAX_PROTOTYPE_FUNCTION_COVERAGE))
        covered_count = len(covered_function_points)
        if covered_count < min_covered or covered_count > max_covered:
            errors.append(f"expected function-point screenshot coverage {min_covered}-{max_covered}, found {covered_count}")

    if errors:
        raise ValidationError(f"{label}: " + "; ".join(errors))
    return files


def validate_html_prototypes(
    directory: Path,
    module_dir: Path | None = None,
    style_selection: Path | None = None,
) -> list[Path]:
    files = validate_prototype_files(directory, ".html", "prototype html", module_dir)
    expected_style = validate_style_selection(style_selection) if style_selection else None
    errors: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        style_match = re.search(
            r"<meta\s+name=[\"']prototype-style[\"']\s+content=[\"']([^\"']+)[\"']\s*/?>",
            text,
            flags=re.IGNORECASE,
        )
        if not style_match:
            errors.append(f"{path.name}: missing <meta name=\"prototype-style\" content=\"...\">")
        elif style_match.group(1) not in ALLOWED_PROTOTYPE_STYLES:
            errors.append(
                f"{path.name}: unsupported prototype style {style_match.group(1)!r}; "
                f"expected one of {', '.join(sorted(ALLOWED_PROTOTYPE_STYLES))}"
            )
        elif expected_style and style_match.group(1) != expected_style:
            errors.append(f"{path.name}: prototype style {style_match.group(1)!r} does not match confirmed style {expected_style!r}")
        if path.stem == "00-login":
            if not re.search(r"<meta\s+name=[\"']module[\"']\s+content=[\"']login[\"']\s*/?>", text, flags=re.IGNORECASE):
                errors.append(f"{path.name}: login page must use <meta name=\"module\" content=\"login\">")
        else:
            module_id, _ = parse_prototype_id(path.stem)
            if not re.search(
                rf"<meta\s+name=[\"']module[\"']\s+content=[\"']02\.modules/{module_id}\.md[\"']\s*/?>",
                text,
                flags=re.IGNORECASE,
            ):
                errors.append(f"{path.name}: module meta must point to 02.modules/{module_id}.md")
        lowered = text.lower()
        forbidden = ["cdn.jsdelivr", "unpkg.com", "bootstrap", "ant-design", "antd", "element-plus"]
        found = [token for token in forbidden if token in lowered]
        if found:
            errors.append(f"{path.name}: forbidden generic/external UI dependency markers: {', '.join(found)}")
    if errors:
        raise ValidationError("prototype html style: " + "; ".join(errors))
    return files


def validate_style_selection(path: Path) -> str:
    validate_file_exists(path, "prototype style selection")
    text = path.read_text(encoding="utf-8", errors="ignore")
    confirmed_lines = [
        line for line in text.splitlines() if re.search(r"用户确认|confirmed|confirmed_style|confirmed style", line, flags=re.IGNORECASE)
    ]
    if not confirmed_lines:
        raise ValidationError("prototype style selection: should record the user-confirmed style")
    for line in confirmed_lines:
        for style in sorted(ALLOWED_PROTOTYPE_STYLES):
            if style in line:
                return style
    found = [style for style in sorted(ALLOWED_PROTOTYPE_STYLES) if style in text]
    if found:
        raise ValidationError("prototype style selection: confirmed style line does not contain a valid style id")
    else:
        raise ValidationError(
            "prototype style selection: missing confirmed style id; "
            f"expected one of {', '.join(sorted(ALLOWED_PROTOTYPE_STYLES))}"
        )


def code_file_id(path: Path) -> str | None:
    match = re.match(r"^(\d{2})-.+\.txt$", path.name)
    if not match:
        return None
    return match.group(1)


def validate_code_files(directory: Path, min_lines: int = CODE_MIN_LINES, max_lines: int = CODE_MAX_LINES) -> list[Path]:
    if not directory.exists():
        raise ValidationError(f"code files: directory does not exist: {directory}")
    if not directory.is_dir():
        raise ValidationError(f"code files: path is not a directory: {directory}")

    files = sorted((path for path in directory.iterdir() if path.is_file() and path.suffix == ".txt"), key=lambda p: p.name)
    by_id: dict[str, list[Path]] = {}
    errors: list[str] = []
    for path in files:
        file_id = code_file_id(path)
        if file_id is None:
            errors.append(f"{path.name}: expected filename like 01-模块名称.txt")
            continue
        by_id.setdefault(file_id, []).append(path)

    missing = [file_id for file_id in EXPECTED_IDS if file_id not in by_id]
    extra = [file_id for file_id in by_id if file_id not in EXPECTED_IDS]
    if missing:
        errors.append(f"missing ids {', '.join(missing)}")
    if extra:
        errors.append(f"unexpected ids {', '.join(extra)}")
    for file_id, paths in sorted(by_id.items()):
        if len(paths) > 1:
            errors.append(f"{file_id}: duplicate code files {', '.join(path.name for path in paths)}")
    if len(files) != len(EXPECTED_IDS):
        errors.append(f"expected {len(EXPECTED_IDS)} code files, found {len(files)}")

    valid_files = [paths[0] for file_id, paths in sorted(by_id.items()) if file_id in EXPECTED_IDS and len(paths) == 1]
    for path in valid_files:
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count < min_lines or line_count > max_lines:
            errors.append(f"{path.name}: expected {min_lines}-{max_lines} lines, found {line_count}")

    if errors:
        raise ValidationError("code files: " + "; ".join(errors))
    return valid_files


def count_module_function_points(text: str) -> int | None:
    match = re.search(r"^##\s+功能点清单\s*$", text, flags=re.MULTILINE)
    if not match:
        return None
    section = text[match.end() :]
    next_heading = re.search(r"^##\s+", section, flags=re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    return len(re.findall(r"^\s*\d+[.)、]\s+\S+", section, flags=re.MULTILINE))


def validate_module_function_points(module_dir: Path) -> None:
    files = validate_numbered_files(module_dir, ".md", "modules")
    errors: list[str] = []
    for path in files:
        count = count_module_function_points(path.read_text(encoding="utf-8"))
        if count is None:
            errors.append(f"{path.name}: missing ## 功能点清单")
        elif count < 3 or count > 5:
            errors.append(f"{path.name}: expected 3-5 function points, found {count}")
    if errors:
        raise ValidationError("modules function points: " + "; ".join(errors))


def validate_file_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise ValidationError(f"{label}: file does not exist: {path}")
    if not path.is_file():
        raise ValidationError(f"{label}: path is not a file: {path}")
    if path.stat().st_size <= 0:
        raise ValidationError(f"{label}: file is empty: {path}")


def find_internal_document_labels(text: str) -> list[str]:
    findings: list[str] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for pattern in INTERNAL_DOCUMENT_LABEL_PATTERNS:
            for match in pattern.finditer(line):
                snippet = line.strip()
                if len(snippet) > 120:
                    snippet = snippet[:117] + "..."
                findings.append(f"line {line_number}: {match.group(0)!r} in {snippet!r}")
    return findings


def validate_no_internal_document_labels(text: str, label: str) -> None:
    findings = find_internal_document_labels(text)
    if findings:
        preview = "; ".join(findings[:10])
        if len(findings) > 10:
            preview += f"; ... and {len(findings) - 10} more"
        raise ValidationError(
            f"{label}: found internal module/function labels. Use real module/function names instead of labels like 模块01. {preview}"
        )


def validate_no_rigid_manual_labels(text: str, label: str) -> None:
    findings: list[str] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for pattern in RIGID_MANUAL_LABEL_PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(f"line {line_number}: {match.group(1)!r}")
    if findings:
        preview = "; ".join(findings[:10])
        if len(findings) > 10:
            preview += f"; ... and {len(findings) - 10} more"
        raise ValidationError(
            f"{label}: found rigid manual labels. Fold page content, operation process, expected results and exceptions into natural paragraphs. {preview}"
        )


def validate_manual_list_density(text: str, label: str, max_markers: int = MAX_MANUAL_BODY_LIST_MARKERS) -> None:
    findings: list[str] = []
    in_code = False
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped or stripped.startswith("#") or stripped.startswith("!["):
            continue
        if MANUAL_BODY_LIST_MARKER_PATTERN.match(stripped):
            findings.append(f"line {line_number}: {stripped[:80]!r}")
    if len(findings) > max_markers:
        preview = "; ".join(findings[:10])
        raise ValidationError(
            f"{label}: too many body list/number markers ({len(findings)}, max {max_markers}). "
            f"Keep numbering mainly in headings and rewrite operation details as paragraphs. {preview}"
        )


def validate_deliverable_markdown(path: Path, label: str) -> None:
    validate_file_exists(path, label)
    validate_no_internal_document_labels(path.read_text(encoding="utf-8", errors="ignore"), label)


def validate_manual_markdown(path: Path, label: str) -> None:
    validate_file_exists(path, label)
    text = path.read_text(encoding="utf-8", errors="ignore")
    validate_no_internal_document_labels(text, label)
    validate_no_rigid_manual_labels(text, label)
    validate_manual_list_density(text, label)


def extract_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            xml_names = [
                name
                for name in archive.namelist()
                if name.startswith("word/")
                and name.endswith(".xml")
                and (
                    name == "word/document.xml"
                    or name.startswith("word/header")
                    or name.startswith("word/footer")
                    or name.startswith("word/footnotes")
                    or name.startswith("word/endnotes")
                )
            ]
            parts: list[str] = []
            for name in xml_names:
                root = ET.fromstring(archive.read(name))
                for paragraph in root.iter():
                    if not paragraph.tag.endswith("}p"):
                        continue
                    paragraph_text = "".join(node.text or "" for node in paragraph.iter() if node.tag.endswith("}t"))
                    if paragraph_text:
                        parts.append(paragraph_text)
            return "\n".join(parts)
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        raise ValidationError(f"docx text: unable to read {path}: {exc}") from exc


def validate_deliverable_docx(path: Path, label: str) -> None:
    validate_file_exists(path, label)
    validate_no_internal_document_labels(extract_docx_text(path), label)


def validate_manual_docx(path: Path, label: str) -> None:
    validate_file_exists(path, label)
    text = extract_docx_text(path)
    validate_no_internal_document_labels(text, label)
    validate_no_rigid_manual_labels(text, label)


def extract_protected_manual_terms(text: str) -> list[str]:
    terms: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            terms.append(stripped)
        if stripped.startswith("!["):
            terms.append(stripped)
        for match in re.finditer(r"「[^」]{1,80}」", stripped):
            terms.append(match.group(0))
        for match in re.finditer(r"`[^`]{1,120}`", stripped):
            terms.append(match.group(0))

    seen: set[str] = set()
    unique_terms: list[str] = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            unique_terms.append(term)
    return unique_terms


def validate_manual_preserved_terms(draft_path: Path, final_path: Path) -> None:
    validate_file_exists(draft_path, "manual draft markdown")
    validate_file_exists(final_path, "manual markdown")
    draft_text = draft_path.read_text(encoding="utf-8", errors="ignore")
    final_text = final_path.read_text(encoding="utf-8", errors="ignore")
    missing = [term for term in extract_protected_manual_terms(draft_text) if term not in final_text]
    if missing:
        preview = "; ".join(repr(term) for term in missing[:15])
        if len(missing) > 15:
            preview += f"; ... and {len(missing) - 15} more"
        raise ValidationError(
            "manual protected terms: final manual changed or removed protected headings, UI labels, image references or code spans. "
            f"Missing from final: {preview}"
        )


def validate_batch_manifest(path: Path, require_success: bool = True, module_dir: Path | None = None) -> None:
    validate_file_exists(path, "batch manifest")
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not isinstance(items, list):
        raise ValidationError("batch manifest: items must be a list")
    ids = [str(item.get("id", "")) for item in items]
    errors: list[str] = []
    try:
        min_count, max_count, function_counts = expected_prototype_range(module_dir)
    except ValidationError as exc:
        errors.append(str(exc))
        min_count, max_count, function_counts = 11, 31, {}
    if len(items) < min_count or len(items) > max_count:
        errors.append(f"expected {min_count}-{max_count} items, found {len(items)}")
    if "00-login" not in ids:
        errors.append("missing id 00-login")
    for module_id in EXPECTED_IDS:
        if module_id not in ids:
            errors.append(f"missing module overview id {module_id}")

    covered_function_points: set[tuple[str, str]] = set()
    required_fields = {"id", "module", "output", "retry", "status"}
    for item in items:
        item_id = str(item.get("id", "?"))
        try:
            module_id, function_id = parse_prototype_id(item_id)
            if function_id is not None:
                covered_function_points.add((module_id, function_id))
        except ValidationError as exc:
            errors.append(str(exc))
        absent = sorted(required_fields - set(item))
        if absent:
            errors.append(f"{item_id}: missing fields {', '.join(absent)}")
        if "prompt" not in item and "html" not in item:
            errors.append(f"{item_id}: missing prompt/html field")
        if not isinstance(item.get("retry"), dict):
            errors.append(f"{item_id}: retry must be an object")
        if require_success and item.get("status") != "success":
            errors.append(f"{item_id}: status is {item.get('status')!r}, expected 'success'")
    if function_counts:
        total_function_points = sum(function_counts.values())
        min_covered = max(1, int(total_function_points * MIN_PROTOTYPE_FUNCTION_COVERAGE + 0.9999))
        max_covered = max(1, int(total_function_points * MAX_PROTOTYPE_FUNCTION_COVERAGE))
        covered_count = len(covered_function_points)
        if covered_count < min_covered or covered_count > max_covered:
            errors.append(f"expected function-point manifest coverage {min_covered}-{max_covered}, found {covered_count}")
    if errors:
        raise ValidationError("batch manifest: " + "; ".join(errors))


def infer_standard_dirs(root: Path, args: argparse.Namespace) -> None:
    if args.spec_md is None:
        args.spec_md = root / "01.spec" / "spec.md"
    if args.module_dir is None:
        args.module_dir = root / "02.modules"
    if args.prototype_mode in {"image", "both"} and args.prompt_dir is None:
        args.prompt_dir = root / "03.prototype.prompt"
    if args.prototype_mode in {"html", "both"} and args.html_dir is None:
        args.html_dir = root / "03.prototype.html"
    if args.style_selection is None:
        args.style_selection = root / "03.prototype.style" / "selection.md"
    if args.prototype_dir is None:
        args.prototype_dir = root / "04.prototype"
    if args.code_dir is None:
        args.code_dir = root / "05.code"
    if args.code_docx is None:
        if args.software_name:
            args.code_docx = root / "07.code.full" / f"{args.software_name}_代码.docx"
        else:
            raise ValidationError("--root validation requires --software-name to infer 07.code.full/{SOFTWARE_NAME}_代码.docx")
    if args.batch_file is None:
        args.batch_file = root / "04.prototype" / "batch.json"


def run_validation(args: argparse.Namespace) -> list[str]:
    if args.root:
        try:
            infer_standard_dirs(args.root, args)
        except ValidationError as exc:
            return [str(exc)]

    checks: list[tuple[str, callable]] = []
    if args.module_dir:
        if args.skip_module_function_points:
            checks.append(("modules", lambda: validate_numbered_files(args.module_dir, ".md", "modules")))
        else:
            checks.append(("modules", lambda: validate_module_function_points(args.module_dir)))
    if args.prompt_dir:
        checks.append(("prototype prompts", lambda: validate_prototype_files(args.prompt_dir, ".md", "prototype prompts", args.module_dir)))
    if args.html_dir:
        checks.append(("prototype html", lambda: validate_html_prototypes(args.html_dir, args.module_dir, args.style_selection)))
    if args.style_selection:
        checks.append(("prototype style selection", lambda: validate_style_selection(args.style_selection)))
    if args.prototype_dir:
        checks.append(("prototype images", lambda: validate_prototype_files(args.prototype_dir, ".jpg", "prototype images", args.module_dir)))
    if args.batch_file:
        checks.append(("batch manifest", lambda: validate_batch_manifest(args.batch_file, not args.allow_incomplete_batch, args.module_dir)))
    if args.code_dir:
        checks.append(("code files", lambda: validate_code_files(args.code_dir, args.code_min_lines, args.code_max_lines)))
    if args.spec_md:
        checks.append(("spec markdown", lambda: validate_deliverable_markdown(args.spec_md, "spec markdown")))
    if args.manual_draft_md:
        checks.append(("manual draft markdown", lambda: validate_file_exists(args.manual_draft_md, "manual draft markdown")))
    if args.manual_md:
        checks.append(("manual markdown", lambda: validate_manual_markdown(args.manual_md, "manual markdown")))
    if args.manual_draft_md and args.manual_md:
        checks.append(("manual protected terms", lambda: validate_manual_preserved_terms(args.manual_draft_md, args.manual_md)))
    if args.manual_docx:
        checks.append(("manual docx", lambda: validate_manual_docx(args.manual_docx, "manual docx")))
    if args.code_docx:
        checks.append(("code docx", lambda: validate_file_exists(args.code_docx, "code docx")))

    errors: list[str] = []
    for label, check in checks:
        try:
            check()
            print(f"OK {label}")
        except ValidationError as exc:
            errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, help="Output root containing 01.spec, 02.modules, ...")
    parser.add_argument("--prototype-mode", choices=("html", "image", "both"), default="html")
    parser.add_argument("--module-dir", type=Path)
    parser.add_argument("--prompt-dir", type=Path)
    parser.add_argument("--html-dir", type=Path)
    parser.add_argument("--style-selection", type=Path)
    parser.add_argument("--prototype-dir", type=Path)
    parser.add_argument("--batch-file", type=Path)
    parser.add_argument("--code-dir", type=Path)
    parser.add_argument("--spec-md", type=Path)
    parser.add_argument("--manual-draft-md", type=Path)
    parser.add_argument("--manual-md", type=Path)
    parser.add_argument("--manual-docx", type=Path)
    parser.add_argument("--code-docx", type=Path)
    parser.add_argument("--software-name")
    parser.add_argument("--code-min-lines", default=CODE_MIN_LINES, type=int)
    parser.add_argument("--code-max-lines", default=CODE_MAX_LINES, type=int)
    parser.add_argument("--allow-incomplete-batch", action="store_true")
    parser.add_argument("--skip-module-function-points", action="store_true")
    args = parser.parse_args()

    errors = run_validation(args)
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
