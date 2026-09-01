#!/usr/bin/env python3
"""Validate numbered copyright material outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


EXPECTED_IDS = [f"{index:02d}" for index in range(1, 11)]
MIN_PROTOTYPE_FUNCTION_COVERAGE = 0.4
MAX_PROTOTYPE_FUNCTION_COVERAGE = 0.6
CODE_MIN_LINES = 0
CODE_MAX_LINES = 0
CODE_MIN_TOTAL_NONEMPTY_LINES = 3000
CODE_MIN_COMMENT_RATIO = 0.0
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
APPLICATION_INFO_FIELD_LIMITS = {
    "开发的硬件环境": 50,
    "运行的硬件环境": 50,
    "操作系统": 50,
    "软件开发环境 / 开发工具": 50,
    "该软件的运行平台 / 操作系统": 50,
    "软件运行支撑环境 / 支持软件": 50,
    "开发目的": 50,
    "面向领域 / 行业": 50,
    "软件的主要功能": 200,
}
APPLICATION_INFO_FIELD_ALIASES = {
    "开发的硬件环境": ("开发的硬件环境",),
    "运行的硬件环境": ("运行的硬件环境",),
    "操作系统": ("操作系统",),
    "软件开发环境 / 开发工具": ("软件开发环境 / 开发工具", "软件开发环境/开发工具"),
    "该软件的运行平台 / 操作系统": ("该软件的运行平台 / 操作系统", "该软件的运行平台/操作系统"),
    "软件运行支撑环境 / 支持软件": ("软件运行支撑环境 / 支持软件", "软件运行支撑环境/支持软件"),
    "编程语言": ("编程语言",),
    "开发目的": ("开发目的",),
    "面向领域 / 行业": ("面向领域 / 行业", "面向领域/行业", "行业"),
    "软件的主要功能": ("软件的主要功能",),
    "软件的技术特点": ("软件的技术特点",),
}
APPLICATION_INFO_SOFTWARE_TYPES = {
    "APP",
    "游戏软件",
    "教育软件",
    "金融软件",
    "医疗软件",
    "地理信息软件",
    "云计算软件",
    "信息安全软件",
    "大数据软件",
    "人工智能软件",
    "VR软件",
    "5G软件",
    "小程序",
    "物联网软件",
    "智慧城市软件",
}
APPLICATION_INFO_FORBIDDEN_TEMPLATE_MARKERS = [
    "限50个字符",
    "限200个字",
    "限200字",
    "限100个字",
    "限100字",
    "指开发登记软件",
    "指运行登记软件",
    "登记软件的创作目的",
    "面向领域 / 行业，限",
    "请选择该软件属于以下哪一种",
]
FORMAL_PROCESS_PATTERNS = [
    re.compile(r"(?:本文|本材料|本说明书|本手册).{0,8}草案|(?:材料|文档|说明书|操作手册)草案|草案版本"),
    re.compile(r"扩展设定"),
    re.compile(r"待申请人(?:核验|确认)"),
    re.compile(r"(?:本文|本材料|该文档).{0,8}AI\s*(?:生成|编写|辅助)"),
    re.compile(r"独创性(?:与模板化风险)?审计"),
    re.compile(r"模板化风险"),
    re.compile(r"生成过程说明"),
]
DESIGN_IMPLEMENTATION_LEAK_PATTERNS = [
    re.compile(r"本节(?:设计)?由.{0,100}落地"),
    re.compile(r"对应源程序文件"),
    re.compile(r"本(?:节|模块|功能).{0,24}(?:代码)?实现于"),
    re.compile(r"(?:^|[\s（(])(?:0[1-9]|10)-[^\s，。；：:]{1,80}\.(?:txt|py|java|kt|js|jsx|ts|tsx|cs|cpp|c|h|hpp|go|rs|swift|dart)\b", re.IGNORECASE),
    re.compile(r"(?:^|\s)(?:0[1-9]|10)?\.?05\.code(?:[/\\]|\b)", re.IGNORECASE),
]
DESIGN_AI_STYLE_PATTERNS = [
    re.compile(r"本系统(?:旨在|致力于)"),
    re.compile(r"(?:全面|显著|有效)(?:提升|提高|增强|保障)"),
    re.compile(r"(?:赋能|打造)"),
    re.compile(r"(?:形成|构建)(?:了|起)?(?:一套|完整|完善)?[^。；\n]{0,16}(?:闭环|体系)"),
    re.compile(r"(?:提供|奠定)[^。；\n]{0,12}(?:有力支撑|坚实基础|可靠保障)"),
    re.compile(r"具备良好的(?:可扩展性|可维护性|稳定性|兼容性)"),
    re.compile(r"不仅[^。；\n]{0,40}而且"),
]
DESIGN_STOCK_OPENING_PATTERN = re.compile(r"^\s*(?:本系统|系统通过|通过[^。；]{0,20}实现)")
GENERIC_SUPPORT_MODULE_PATTERN = re.compile(
    r"^(?:首页|(?:用户|角色|权限|数据字典|操作日志|系统设置|帮助)(?:管理|中心|配置)?|数据管理|信息维护|统计分析)$"
)


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


def expected_prototype_range(module_dir: Path | None, require_login: bool = True) -> tuple[int, int, dict[str, int]]:
    base_count = 1 if require_login else 0
    if module_dir is None:
        return base_count + 10, base_count + 30, {}
    counts = module_function_counts(module_dir)
    total_function_points = sum(counts.values())
    min_count = base_count + len(EXPECTED_IDS) + max(1, int(total_function_points * MIN_PROTOTYPE_FUNCTION_COVERAGE + 0.9999))
    max_count = base_count + len(EXPECTED_IDS) + max(1, int(total_function_points * MAX_PROTOTYPE_FUNCTION_COVERAGE))
    return min_count, max_count, counts


def validate_prototype_files(
    directory: Path,
    suffix: str,
    label: str,
    module_dir: Path | None = None,
    require_login: bool = True,
) -> list[Path]:
    if not directory.exists():
        raise ValidationError(f"{label}: directory does not exist: {directory}")
    if not directory.is_dir():
        raise ValidationError(f"{label}: path is not a directory: {directory}")

    files = sorted((path for path in directory.iterdir() if path.is_file() and path.suffix == suffix), key=lambda p: p.name)
    ids = [path.stem for path in files]
    errors: list[str] = []
    if require_login and "00-login" not in ids:
        errors.append(f"missing 00-login{suffix}")
    for module_id in EXPECTED_IDS:
        if module_id not in ids:
            errors.append(f"missing module overview {module_id}{suffix}")

    min_count, max_count, function_counts = expected_prototype_range(module_dir, require_login)
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
    require_login: bool = True,
) -> list[Path]:
    files = validate_prototype_files(directory, ".html", "prototype html", module_dir, require_login)
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


def source_code_stats(files: list[Path]) -> dict:
    """Count mixed-language text sources without assuming every file is JavaScript."""
    stats: dict[str, dict[str, int]] = {}
    total_comment = 0
    total_code = 0
    total_blank = 0
    for path in files:
        comment = 0
        code = 0
        blank = 0
        in_block_comment = False
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                blank += 1
                continue
            if in_block_comment:
                comment += 1
                if "*/" in line:
                    in_block_comment = False
                continue
            if line.startswith("/*"):
                comment += 1
                in_block_comment = "*/" not in line[2:]
            elif line.startswith("//") or (line.startswith("#") and not line.startswith(("#!", "#include", "#define", "#pragma"))):
                comment += 1
            else:
                code += 1
        stats[str(path)] = {"comment": comment, "code": code, "blank": blank}
        total_comment += comment
        total_code += code
        total_blank += blank
    stats["SUM"] = {"comment": total_comment, "code": total_code, "blank": total_blank}
    return stats


def source_stats_entry_for_path(stats: dict, path: Path) -> dict:
    for key in (str(path), str(path.resolve()), path.name):
        entry = stats.get(key)
        if isinstance(entry, dict):
            return entry

    for key, entry in stats.items():
        if key in {"header", "SUM"} or not isinstance(entry, dict):
            continue
        if Path(key).name == path.name:
            return entry

    raise ValidationError(f"code files: source statistics did not report {path.name}")


def validate_code_files(
    directory: Path,
    min_lines: int = CODE_MIN_LINES,
    max_lines: int = CODE_MAX_LINES,
    min_total_nonempty_lines: int = CODE_MIN_TOTAL_NONEMPTY_LINES,
    min_comment_ratio: float = CODE_MIN_COMMENT_RATIO,
    source_manifest: Path | None = None,
) -> list[Path]:
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
    if source_manifest is not None and valid_files:
        manifest_order = validate_source_manifest(source_manifest, directory)
        valid_by_name = {path.name: path for path in valid_files}
        valid_files = [valid_by_name[name] for name in manifest_order if name in valid_by_name]
    stats = source_code_stats(valid_files) if valid_files else {"SUM": {"comment": 0, "code": 0}}
    total_comment_lines = 0
    total_code_lines = 0
    for path in valid_files:
        text = path.read_text(encoding="utf-8")
        copyright_matches = [index for index, line in enumerate(text.splitlines(), 1) if "copyright" in line.lower()]
        if copyright_matches:
            preview = ", ".join(str(index) for index in copyright_matches[:10])
            if len(copyright_matches) > 10:
                preview += f", ... and {len(copyright_matches) - 10} more"
            errors.append(f"{path.name}: source code must not contain copyright ({preview})")
        entry = source_stats_entry_for_path(stats, path)
        comment_lines = int(entry.get("comment", 0))
        code_lines = int(entry.get("code", 0))
        nonempty_line_count = comment_lines + code_lines
        total_comment_lines += comment_lines
        total_code_lines += code_lines
        if min_lines and nonempty_line_count < min_lines:
            errors.append(f"{path.name}: expected at least {min_lines} non-empty source lines, found {nonempty_line_count}")
        if max_lines and nonempty_line_count > max_lines:
            errors.append(f"{path.name}: expected at most {max_lines} non-empty source lines, found {nonempty_line_count}")
    total_nonempty_lines = total_comment_lines + total_code_lines
    if total_nonempty_lines < min_total_nonempty_lines:
        errors.append(
                f"expected at least {min_total_nonempty_lines} total non-empty source lines, found {total_nonempty_lines}"
        )
    if total_nonempty_lines:
        comment_ratio = total_comment_lines / total_nonempty_lines
        if comment_ratio < min_comment_ratio:
            errors.append(
                f"expected at least {min_comment_ratio:.0%} source comment ratio, found {comment_ratio:.1%}"
            )

    if errors:
        raise ValidationError("code files: " + "; ".join(errors))
    return valid_files


def validate_source_manifest(path: Path, code_dir: Path | None = None) -> list[str]:
    validate_file_exists(path, "source manifest")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError("source manifest: invalid JSON") from exc
    if not isinstance(data, dict):
        raise ValidationError("source manifest: root must be an object")
    entries = data.get("files")
    if not isinstance(entries, list) or not entries:
        raise ValidationError("source manifest: files must be a non-empty array")
    errors: list[str] = []
    if data.get("version") != 1:
        errors.append("version must be 1")
    if not isinstance(data.get("technology_stack"), list) or not data.get("technology_stack"):
        errors.append("technology_stack must be a non-empty array")
    if not isinstance(data.get("business_terms"), list):
        errors.append("business_terms must be an array")
    if len(entries) != len(EXPECTED_IDS):
        errors.append(f"expected {len(EXPECTED_IDS)} files, found {len(entries)}")
    ordered_paths: list[str] = []
    seen: set[str] = set()
    for expected_order, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            errors.append(f"entry {expected_order}: expected object")
            continue
        required_fields = {
            "order", "path", "module_id", "module_name", "languages", "core_methods",
            "nonempty_lines", "low_value_lines", "low_value_ratio", "sha256", "selection_reason",
        }
        missing_fields = sorted(required_fields - set(entry))
        if missing_fields:
            errors.append(f"entry {expected_order}: missing fields {', '.join(missing_fields)}")
        relative = str(entry.get("path", ""))
        if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append(f"entry {expected_order}: invalid relative path {relative!r}")
            continue
        if entry.get("order") != expected_order:
            errors.append(f"{relative}: expected order {expected_order}, found {entry.get('order')!r}")
        module_id = entry.get("module_id")
        if module_id is not None and str(module_id) != relative[:2]:
            errors.append(f"{relative}: module_id {module_id!r} does not match filename prefix")
        if not isinstance(entry.get("languages"), list) or not entry.get("languages"):
            errors.append(f"{relative}: languages must be a non-empty array")
        if not isinstance(entry.get("core_methods"), list) or not entry.get("core_methods"):
            errors.append(f"{relative}: core_methods must be a non-empty array")
        if not str(entry.get("selection_reason", "")).strip():
            errors.append(f"{relative}: selection_reason must be non-empty")
        if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
            errors.append(f"{relative}: sha256 must be a lowercase SHA-256 digest")
        if relative in seen:
            errors.append(f"{relative}: duplicate manifest entry")
        seen.add(relative)
        ordered_paths.append(relative)
        if code_dir is not None:
            source = code_dir / relative
            try:
                source.resolve().relative_to(code_dir.resolve())
            except ValueError:
                errors.append(f"{relative}: resolves outside {code_dir}")
                continue
            if not source.is_file():
                errors.append(f"{relative}: file does not exist under {code_dir}")
            else:
                actual_hash = hashlib.sha256(source.read_bytes()).hexdigest()
                if entry.get("sha256") is not None and entry.get("sha256") != actual_hash:
                    errors.append(f"{relative}: sha256 does not match current source")
                actual_nonempty = sum(bool(line.strip()) for line in source.read_text(encoding="utf-8").splitlines())
                if entry.get("nonempty_lines") is not None and entry.get("nonempty_lines") != actual_nonempty:
                    errors.append(f"{relative}: nonempty_lines does not match current source")
    if code_dir is not None:
        actual = {item.name for item in code_dir.glob("*.txt") if item.is_file()}
        if set(ordered_paths) != actual:
            errors.append("manifest paths must match all 05.code/*.txt files exactly")
    if errors:
        raise ValidationError("source manifest: " + "; ".join(errors))
    return ordered_paths


def validate_originality_report(
    path: Path,
    code_dir: Path | None = None,
    source_manifest: Path | None = None,
) -> None:
    validate_file_exists(path, "originality report")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError("originality report: invalid JSON") from exc
    if not isinstance(data, dict):
        raise ValidationError("originality report: root must be an object")
    if data.get("version") != 1:
        raise ValidationError("originality report: version must be 1")
    raw_issues = data.get("issues")
    if not isinstance(raw_issues, list):
        raise ValidationError("originality report: issues must be an array")
    report_errors = [
        issue.get("message", issue.get("code", "unknown"))
        for issue in raw_issues
        if isinstance(issue, dict) and issue.get("severity") == "error"
    ]
    if data.get("status") != "pass":
        detail = "; ".join(str(item) for item in report_errors[:10]) or "report status is not pass"
        raise ValidationError(f"originality report: {detail}")
    if report_errors:
        raise ValidationError("originality report: pass status conflicts with error findings")
    if source_manifest is not None:
        validate_file_exists(source_manifest, "source manifest")
        try:
            manifest_data = json.loads(source_manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValidationError("source manifest: invalid JSON") from exc
        if not isinstance(manifest_data, dict):
            raise ValidationError("source manifest: root must be an object")
        manifest_hash = hashlib.sha256(
            json.dumps(manifest_data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if data.get("source_manifest_sha256") != manifest_hash:
            raise ValidationError("originality report: source manifest changed after audit")
    if code_dir is not None:
        reported = data.get("source_files")
        if not isinstance(reported, list) or not reported:
            raise ValidationError("originality report: missing source file fingerprints")
        errors: list[str] = []
        reported_paths: set[str] = set()
        for entry in reported:
            if isinstance(entry, dict):
                reported_paths.add(str(entry.get("path", "")))
            else:
                errors.append("source fingerprint entry must be an object")
        actual_paths = {path.name for path in code_dir.glob("*.txt") if path.is_file()}
        if len(reported) != len(reported_paths):
            errors.append("source fingerprint entries contain duplicates or invalid paths")
        if reported_paths != actual_paths:
            errors.append("audited source set does not match current 05.code files")
        for entry in reported:
            if not isinstance(entry, dict):
                continue
            relative = str(entry.get("path", ""))
            if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
                errors.append(f"invalid audited source path: {relative!r}")
                continue
            source = code_dir / relative
            if not source.is_file():
                errors.append(f"missing audited source {relative}")
                continue
            actual = hashlib.sha256(source.read_bytes()).hexdigest()
            if actual != entry.get("sha256"):
                errors.append(f"source changed after audit: {relative}")
        if errors:
            raise ValidationError("originality report: " + "; ".join(errors))


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
    generic_names: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        count = count_module_function_points(text)
        if count is None:
            errors.append(f"{path.name}: missing ## 功能点清单")
        elif count < 3 or count > 5:
            errors.append(f"{path.name}: expected 3-5 function points, found {count}")
        heading = re.search(r"^#\s+(?:\d{2}[.、\s-]+)?(.+?)\s*$", text, flags=re.MULTILINE)
        if heading and GENERIC_SUPPORT_MODULE_PATTERN.fullmatch(heading.group(1).strip()):
            generic_names.append(heading.group(1).strip())
    if len(generic_names) > 2:
        errors.append(f"expected at least 8 domain-specific modules; generic support modules: {', '.join(generic_names)}")
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


def validate_no_formal_process_markers(text: str, label: str) -> None:
    findings: list[str] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for pattern in FORMAL_PROCESS_PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(f"line {line_number}: {match.group(0)!r}")
    if findings:
        preview = "; ".join(findings[:10])
        raise ValidationError(f"{label}: contains generation or internal quality-control wording. {preview}")


def validate_no_design_implementation_leaks(text: str, label: str) -> None:
    findings: list[str] = []
    in_code = False
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for pattern in DESIGN_IMPLEMENTATION_LEAK_PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(f"line {line_number}: {match.group(0)!r}")
    if findings:
        preview = "; ".join(findings[:10])
        raise ValidationError(
            f"{label}: exposes delivery-package filenames or generated source-mapping wording. "
            f"Use one design—implementation traceability appendix with logical components and verified symbols instead. {preview}"
        )


def validate_design_language(text: str, label: str) -> None:
    findings: list[str] = []
    stock_openings: list[str] = []
    in_code = False
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped or stripped.startswith(("#", "|", "![")):
            continue
        for pattern in DESIGN_AI_STYLE_PATTERNS:
            for match in pattern.finditer(line):
                findings.append(f"line {line_number}: {match.group(0)!r}")
        if DESIGN_STOCK_OPENING_PATTERN.search(line):
            stock_openings.append(f"line {line_number}: {stripped[:50]!r}")

    errors: list[str] = []
    if len(findings) >= 4:
        errors.append(f"stock benefit claims ({len(findings)}): " + "; ".join(findings[:6]))
    if len(stock_openings) >= 4:
        errors.append(f"repeated stock paragraph openings ({len(stock_openings)}): " + "; ".join(stock_openings[:6]))
    if errors:
        raise ValidationError(
            f"{label}: writing is too abstract or repetitive. Replace claims with business objects, conditions, actions and results. "
            + " | ".join(errors)
        )


def validate_deliverable_markdown(path: Path, label: str) -> None:
    validate_file_exists(path, label)
    text = path.read_text(encoding="utf-8", errors="ignore")
    validate_no_internal_document_labels(text, label)
    validate_no_formal_process_markers(text, label)


def validate_design_markdown(path: Path, label: str) -> None:
    validate_deliverable_markdown(path, label)
    text = path.read_text(encoding="utf-8", errors="ignore")
    validate_no_design_implementation_leaks(text, label)
    validate_design_language(text, label)


def validate_manual_markdown(path: Path, label: str) -> None:
    validate_file_exists(path, label)
    text = path.read_text(encoding="utf-8", errors="ignore")
    validate_no_internal_document_labels(text, label)
    validate_no_rigid_manual_labels(text, label)
    validate_manual_list_density(text, label)
    validate_no_formal_process_markers(text, label)


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
    text = extract_docx_text(path)
    validate_no_internal_document_labels(text, label)
    validate_no_formal_process_markers(text, label)


def validate_design_docx(path: Path, label: str) -> None:
    validate_deliverable_docx(path, label)
    text = extract_docx_text(path)
    validate_no_design_implementation_leaks(text, label)
    validate_design_language(text, label)


def validate_manual_docx(path: Path, label: str) -> None:
    validate_file_exists(path, label)
    text = extract_docx_text(path)
    validate_no_internal_document_labels(text, label)
    validate_no_rigid_manual_labels(text, label)
    validate_no_formal_process_markers(text, label)


def count_docx_page_breaks(path: Path) -> int:
    try:
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        raise ValidationError(f"code docx: unable to read document XML: {exc}") from exc
    word_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    page_breaks = 0
    for element in root.iter():
        if element.tag.endswith("}br") and element.get(f"{{{word_ns}}}type") == "page":
            page_breaks += 1
    return page_breaks


def validate_code_docx(path: Path, label: str, software_name: str | None = None, software_version: str | None = None) -> None:
    validate_file_exists(path, label)
    text = extract_docx_text(path)
    if "copyright" in text.lower():
        raise ValidationError(f"{label}: source-code document must not contain copyright")
    if software_name and software_name not in text:
        raise ValidationError(f"{label}: header should contain software name {software_name!r}")
    if software_version and software_version not in text:
        raise ValidationError(f"{label}: header should contain software version {software_version!r}")
    page_breaks = count_docx_page_breaks(path)
    if page_breaks != 59:
        raise ValidationError(f"{label}: expected 59 explicit page breaks for 60 code pages, found {page_breaks}")


def normalize_application_info_char(char: str) -> str:
    if char in {"／", "/"}:
        return "/"
    return char


def consume_application_info_label(line: str, label: str) -> str | None:
    label_chars = [normalize_application_info_char(char) for char in label if not char.isspace()]
    if not label_chars:
        return None

    label_index = 0
    for index, char in enumerate(line):
        if char.isspace():
            continue
        if label_index >= len(label_chars):
            return line[index:]
        if normalize_application_info_char(char) != label_chars[label_index]:
            return None
        label_index += 1
        if label_index == len(label_chars):
            return line[index + 1 :]
    return "" if label_index == len(label_chars) else None


def strip_application_info_value_prefix(value: str) -> str:
    return value.strip().lstrip("\t ：:").strip()


def application_info_char_count(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def is_application_info_label_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    labels = ["开发该软件的"]
    for aliases in APPLICATION_INFO_FIELD_ALIASES.values():
        labels.extend(aliases)
    return any(consume_application_info_label(stripped, label) is not None for label in labels)


def extract_application_info_value(lines: list[str], label: str) -> str:
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        for alias in APPLICATION_INFO_FIELD_ALIASES[label]:
            remainder = consume_application_info_label(stripped, alias)
            if remainder is None:
                continue
            value = strip_application_info_value_prefix(remainder)
            if value:
                return value
            for next_line in lines[index + 1 :]:
                candidate = next_line.strip()
                if not candidate:
                    continue
                if is_application_info_label_line(candidate):
                    return ""
                return candidate
            return ""
    return ""


def validate_application_info_txt(path: Path) -> None:
    validate_file_exists(path, "application info txt")
    text = path.read_text(encoding="utf-8", errors="ignore")
    validate_no_formal_process_markers(text, "application info txt")
    lines = text.splitlines()
    errors: list[str] = []

    for marker in APPLICATION_INFO_FORBIDDEN_TEMPLATE_MARKERS:
        if marker in text:
            errors.append(f"should not keep template prompt marker {marker!r}")

    for label, limit in APPLICATION_INFO_FIELD_LIMITS.items():
        value = extract_application_info_value(lines, label)
        if not value:
            errors.append(f"missing value for {label}")
            continue
        char_count = application_info_char_count(value)
        if char_count > limit:
            errors.append(f"{label}: expected <= {limit} characters, found {char_count}")

    language_value = extract_application_info_value(lines, "编程语言")
    if not language_value:
        errors.append("missing value for 编程语言")
    else:
        for token in ("语言", "版本", "源程序量", "行"):
            if token not in language_value:
                errors.append(f"编程语言: missing {token!r}")
        if not re.search(r"源程序量\s*[：:\t ]*\d+\s*行", language_value):
            errors.append("编程语言: 源程序量 should be a numeric line count like 源程序量 3000 行")

    tech_value = extract_application_info_value(lines, "软件的技术特点")
    if not tech_value:
        errors.append("missing value for 软件的技术特点")
    else:
        found_types = [software_type for software_type in sorted(APPLICATION_INFO_SOFTWARE_TYPES, key=len, reverse=True) if software_type in tech_value]
        if not found_types:
            errors.append("软件的技术特点: should include one software type from the configured list")
        elif len(set(found_types)) > 1:
            errors.append(f"软件的技术特点: choose one software type, found {', '.join(found_types)}")
        else:
            description = re.sub(r"^\s*类型\s*[：:]\s*", "", tech_value)
            description = description.replace(found_types[0], "", 1).lstrip("。；;:：，,、 ")
            if not description:
                errors.append("软件的技术特点: missing technical description after software type")
            elif application_info_char_count(description) > 100:
                errors.append(
                    f"软件的技术特点: technical description expected <= 100 characters, "
                    f"found {application_info_char_count(description)}"
                )

    if errors:
        raise ValidationError("application info txt: " + "; ".join(errors))


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


def validate_batch_manifest(
    path: Path,
    require_success: bool = True,
    module_dir: Path | None = None,
    require_login: bool = True,
) -> None:
    validate_file_exists(path, "batch manifest")
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not isinstance(items, list):
        raise ValidationError("batch manifest: items must be a list")
    ids = [str(item.get("id", "")) for item in items]
    errors: list[str] = []
    try:
        min_count, max_count, function_counts = expected_prototype_range(module_dir, require_login)
    except ValidationError as exc:
        errors.append(str(exc))
        min_count, max_count, function_counts = (11, 31, {}) if require_login else (10, 30, {})
    if len(items) < min_count or len(items) > max_count:
        errors.append(f"expected {min_count}-{max_count} items, found {len(items)}")
    if require_login and "00-login" not in ids:
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
    if args.source_manifest is None:
        args.source_manifest = root / "09.originality-audit" / "source-manifest.json"
    if args.originality_report is None:
        args.originality_report = root / "09.originality-audit" / "originality-report.json"
    if args.document_md is None or args.document_docx is None:
        candidates = []
        for directory in (root / "06.document", root / "06.manual"):
            if directory.exists():
                candidates.extend(directory.iterdir())
        if args.document_md is None:
            markdown = sorted(
                path
                for path in candidates
                if path.is_file()
                and path.suffix == ".md"
                and not path.name.endswith((".working.md", ".draft.md"))
            )
            if len(markdown) != 1:
                raise ValidationError(f"--root validation requires exactly one final selected-document markdown, found {len(markdown)}")
            args.document_md = markdown[0]
        if args.document_docx is None:
            documents = sorted(path for path in candidates if path.is_file() and path.suffix == ".docx")
            if len(documents) != 1:
                raise ValidationError(f"--root validation requires exactly one final selected-document docx, found {len(documents)}")
            args.document_docx = documents[0]
    if args.code_docx is None:
        if args.software_name:
            args.code_docx = root / "07.code.full" / f"{args.software_name}_代码.docx"
        else:
            raise ValidationError("--root validation requires --software-name to infer 07.code.full/{SOFTWARE_NAME}_代码.docx")
    if args.application_info_txt is None:
        if args.software_name:
            args.application_info_txt = root / "08.application-info" / f"{args.software_name}_软著申请表信息.txt"
        else:
            raise ValidationError("--root validation requires --software-name to infer 08.application-info/{SOFTWARE_NAME}_软著申请表信息.txt")
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
        checks.append(("prototype prompts", lambda: validate_prototype_files(args.prompt_dir, ".md", "prototype prompts", args.module_dir, not args.no_login)))
    if args.html_dir:
        checks.append(("prototype html", lambda: validate_html_prototypes(args.html_dir, args.module_dir, args.style_selection, not args.no_login)))
    if args.style_selection:
        checks.append(("prototype style selection", lambda: validate_style_selection(args.style_selection)))
    if args.prototype_dir:
        checks.append(("prototype images", lambda: validate_prototype_files(args.prototype_dir, ".jpg", "prototype images", args.module_dir, not args.no_login)))
    if args.batch_file:
        checks.append(("batch manifest", lambda: validate_batch_manifest(args.batch_file, not args.allow_incomplete_batch, args.module_dir, not args.no_login)))
    if args.code_dir:
        checks.append((
            "code files",
            lambda: validate_code_files(
                args.code_dir,
                args.code_min_lines,
                args.code_max_lines,
                args.code_min_total_nonempty_lines,
                args.code_min_comment_ratio,
                args.source_manifest,
            ),
        ))
    if args.source_manifest:
        checks.append(("source manifest", lambda: validate_source_manifest(args.source_manifest, args.code_dir)))
    if args.originality_report:
        checks.append(("originality report", lambda: validate_originality_report(args.originality_report, args.code_dir, args.source_manifest)))
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
    if args.document_md:
        if "操作手册" in args.document_md.name:
            checks.append(("selected document markdown", lambda: validate_manual_markdown(args.document_md, "selected document markdown")))
        elif "软件设计说明书" in args.document_md.name:
            checks.append(("selected document markdown", lambda: validate_design_markdown(args.document_md, "selected document markdown")))
        else:
            checks.append(("selected document markdown", lambda: validate_deliverable_markdown(args.document_md, "selected document markdown")))
    if args.document_docx:
        if "操作手册" in args.document_docx.name:
            checks.append(("selected document docx", lambda: validate_manual_docx(args.document_docx, "selected document docx")))
        elif "软件设计说明书" in args.document_docx.name:
            checks.append(("selected document docx", lambda: validate_design_docx(args.document_docx, "selected document docx")))
        else:
            checks.append(("selected document docx", lambda: validate_deliverable_docx(args.document_docx, "selected document docx")))
    if args.code_docx:
        checks.append(("code docx", lambda: validate_code_docx(args.code_docx, "code docx", args.software_name, args.software_version)))
    if args.application_info_txt:
        checks.append(("application info txt", lambda: validate_application_info_txt(args.application_info_txt)))

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
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--originality-report", type=Path)
    parser.add_argument("--spec-md", type=Path)
    parser.add_argument("--manual-draft-md", type=Path)
    parser.add_argument("--manual-md", type=Path)
    parser.add_argument("--manual-docx", type=Path)
    parser.add_argument("--document-md", type=Path)
    parser.add_argument("--document-docx", type=Path)
    parser.add_argument("--code-docx", type=Path)
    parser.add_argument("--application-info-txt", type=Path)
    parser.add_argument("--software-name")
    parser.add_argument("--software-version", default="V1.0")
    parser.add_argument("--code-min-lines", default=CODE_MIN_LINES, type=int)
    parser.add_argument("--code-max-lines", default=CODE_MAX_LINES, type=int)
    parser.add_argument("--code-min-total-nonempty-lines", default=CODE_MIN_TOTAL_NONEMPTY_LINES, type=int)
    parser.add_argument("--code-min-comment-ratio", default=CODE_MIN_COMMENT_RATIO, type=float)
    parser.add_argument("--allow-incomplete-batch", action="store_true")
    parser.add_argument("--no-login", action="store_true", help="Do not require a login prototype when the software has no login flow")
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
