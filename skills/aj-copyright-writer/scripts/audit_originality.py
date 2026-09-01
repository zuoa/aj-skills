#!/usr/bin/env python3
"""Audit copyright identification materials for template-heavy content.

The thresholds in this module are internal quality heuristics.  They are not
published review thresholds of a registration authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


LOW_VALUE_PATTERNS = [
    re.compile(r"^\s*(?:import|package|using|require\s*\(|from\s+\S+\s+import)\b"),
    re.compile(r"^\s*(?:@(?:Data|Getter|Setter|NoArgsConstructor|AllArgsConstructor)|#include\s*[<\"])") ,
    re.compile(r"^\s*(?:public|private|protected)?\s*[\w<>?,.\[\]]+\s+(?:get|set|is)[A-Z]\w*\s*\([^)]*\)\s*[{;]"),
]
PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:TODO|FIXME|NotImplementedException|UnsupportedOperationException)\b|待实现|占位(?:符|代码)",
    re.IGNORECASE,
)
EMPTY_IMPLEMENTATION_PATTERN = re.compile(r"(?:\)|=>|\b(?:class|function)\b[^{}]*)\s*\{\s*\}")
MULTILINE_EMPTY_IMPLEMENTATION_PATTERNS = [
    re.compile(r"\)\s*\{\s*(?:return\s+null\s*;)?\s*\}", re.MULTILINE),
    re.compile(r"^\s*(?:async\s+)?def\s+\w+\s*\([^)]*\)\s*:\s*\n\s+pass\s*$", re.MULTILINE),
    re.compile(r"=>\s*(?:null|<></>)\s*;"),
]
GENERATED_OR_THIRD_PARTY_PATTERN = re.compile(
    r"auto[- ]generated|generated code|do not edit|@Generated\b|node_modules[/\\]|vendor[/\\]|third[- ]party",
    re.IGNORECASE,
)
GENERIC_MODULE_PATTERN = re.compile(
    r"^(?:首页|(?:用户|角色|权限|数据字典|操作日志|系统设置|帮助)(?:管理|中心|配置)?|数据管理|信息维护|统计分析)$"
)
CODE_SUFFIXES = {".txt", ".java", ".kt", ".js", ".jsx", ".ts", ".tsx", ".py", ".cs", ".cpp", ".c", ".go", ".rs", ".swift", ".dart"}
DOCUMENT_SUFFIXES = {".md", ".txt"}


def normalized_line(line: str, structural: bool = False) -> str:
    value = re.sub(r"(['\"]).*?\1", "STR", line)
    value = re.sub(r"\b\d+(?:\.\d+)?\b", "NUM", value)
    value = re.sub(r"\s+", " ", value.strip())
    if structural:
        keywords = {
            "if", "else", "for", "while", "switch", "case", "return", "throw", "new", "class", "interface",
            "public", "private", "protected", "static", "final", "const", "let", "var", "async", "await", "try",
            "catch", "finally", "true", "false", "null", "def", "in", "and", "or", "not", "with", "from", "import",
        }

        def replace_identifier(match: re.Match[str]) -> str:
            token = match.group(0)
            return token if token in keywords else "ID"

        value = re.sub(r"\b[A-Za-z_$][A-Za-z0-9_$]*\b", replace_identifier, value)
    return value


def is_low_value(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped in {"{", "}", "};", ");"}:
        return True
    return any(pattern.search(line) for pattern in LOW_VALUE_PATTERNS)


def repeated_window_coverage(files: dict[str, list[str]], window: int = 8, structural: bool = False) -> float:
    occurrences: dict[str, list[tuple[str, int]]] = defaultdict(list)
    total_lines = sum(len(lines) for lines in files.values())
    if total_lines == 0:
        return 0.0
    for name, lines in files.items():
        normalized = [normalized_line(line, structural=structural) for line in lines]
        for index in range(max(0, len(normalized) - window + 1)):
            block = normalized[index : index + window]
            if sum(bool(line) and not is_low_value(line) for line in block) < window // 2:
                continue
            digest = hashlib.sha256("\n".join(block).encode("utf-8")).hexdigest()
            occurrences[digest].append((name, index))
    covered: dict[str, set[int]] = defaultdict(set)
    for positions in occurrences.values():
        if len(positions) < 2:
            continue
        distinct = {(name, index) for name, index in positions}
        if len({name for name, _ in distinct}) < 2:
            continue
        for name, index in distinct:
            covered[name].update(range(index, index + window))
    return sum(len(indexes) for indexes in covered.values()) / total_lines


def read_modules(module_dir: Path | None) -> list[dict[str, str]]:
    if module_dir is None or not module_dir.exists():
        return []
    modules = []
    for path in sorted(module_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        heading = re.search(r"^#\s+(?:(\d{2})[.、\s-]+)?(.+?)\s*$", text, flags=re.MULTILINE)
        if heading:
            modules.append({"id": heading.group(1) or path.stem[:2], "name": heading.group(2).strip(), "path": path.name})
    return modules


def detect_languages(text: str) -> list[str]:
    checks = {
        "Java": bool(re.search(r"@(?:RestController|Service|Repository)\b|\bpublic\s+(?:final\s+)?class\s+\w+", text)),
        "JavaScript/TypeScript": bool(re.search(r"\b(?:const|let)\s+\w+\s*=|\bexport\s+(?:default|const|function|class)|\bfunction\s+\w+\s*\(", text)),
        "Python": bool(re.search(r"^\s*(?:async\s+)?def\s+\w+\s*\([^)]*\)\s*:", text, flags=re.MULTILINE) or "from fastapi" in text),
        "C#": bool(re.search(r"^\s*using\s+System(?:\.|;)|\bnamespace\s+\w+[.\w]*\s*\{", text, flags=re.MULTILINE)),
        "C/C++": bool(re.search(r"^\s*#include\s*[<\"]|\bstd::|\bconstexpr\b", text, flags=re.MULTILINE)),
        "Go": bool(re.search(r"^\s*package\s+\w+\s*$", text, flags=re.MULTILINE) and re.search(r"^\s*func\s+(?:\([^)]*\)\s*)?\w+\s*\(", text, flags=re.MULTILINE)),
        "Kotlin": bool(re.search(r"\b(?:suspend\s+)?fun\s+\w+\s*\(|\bdata\s+class\s+\w+", text)),
        "Rust": bool(re.search(r"\b(?:pub\s+)?fn\s+\w+\s*\(|\bimpl(?:<[^>]+>)?\s+\w+", text)),
        "Swift": bool(re.search(r"^\s*import\s+(?:SwiftUI|Foundation)\s*$", text, flags=re.MULTILINE) and re.search(r"\bfunc\s+\w+\s*\(", text)),
        "Dart": "package:flutter" in text or bool(re.search(r"\bWidget\s+build\s*\(", text)),
    }
    return [language for language, matched in checks.items() if matched]


def detect_core_methods(text: str) -> list[str]:
    names = re.findall(r"\b(?:def|function|func|fun|fn)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(", text)
    names.extend(re.findall(r"\b([A-Za-z_$][A-Za-z0-9_$]*)\s*\([^;{}]*\)\s*\{", text))
    names.extend(re.findall(r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", text))
    names.extend(re.findall(r"\b([A-Za-z_$][A-Za-z0-9_$]*)\s*\([^;{}]*\)\s*=>", text))
    ignored = {"if", "for", "while", "switch", "catch", "class"}
    return list(dict.fromkeys(name for name in names if name not in ignored))[:20]


def make_manifest(code_dir: Path, modules: list[dict[str, str]]) -> dict:
    module_by_id = {item["id"]: item["name"] for item in modules}
    entries = []
    for order, path in enumerate(sorted(code_dir.glob("*.txt")), 1):
        text = path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if line.strip()]
        module_id = path.name[:2] if re.match(r"^\d{2}-", path.name) else ""
        low_value_count = sum(is_low_value(line) for line in lines)
        entries.append(
            {
                "order": order,
                "path": path.name,
                "module_id": module_id,
                "module_name": module_by_id.get(module_id, path.stem[3:] if module_id else path.stem),
                "languages": detect_languages(text),
                "core_methods": detect_core_methods(text),
                "nonempty_lines": len(lines),
                "low_value_lines": low_value_count,
                "low_value_ratio": round(low_value_count / len(lines), 4) if lines else 1.0,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "selection_reason": (
                    f"选取{module_by_id.get(module_id, path.stem[3:] if module_id else path.stem)}的"
                    f"{('、'.join(detect_core_methods(text)[:3]) or '核心业务处理')}实现"
                ),
            }
        )
    technology_stack = list(dict.fromkeys(language for entry in entries for language in entry["languages"]))
    return {
        "version": 1,
        "code_dir": str(code_dir),
        "technology_stack": technology_stack,
        "business_terms": [item["name"] for item in modules],
        "files": entries,
    }


def document_paragraphs(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    paragraphs = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
        text = re.sub(r"^#+\s+", "", block.strip())
        if text.startswith("![") or len(text) < 40:
            continue
        paragraphs.append(re.sub(r"\s+", "", text))
    return paragraphs


def paragraph_template_duplicates(paragraphs: list[str], business_terms: list[str] | None = None) -> list[dict[str, object]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, paragraph in enumerate(paragraphs, 1):
        skeleton = re.sub(r"「[^」]+」", "「TERM」", paragraph)
        for term in sorted(business_terms or [], key=len, reverse=True):
            skeleton = skeleton.replace(term, "TERM")
        skeleton = re.sub(r"\d+(?:\.\d+)?", "NUM", skeleton)
        skeleton = re.sub(r"[A-Za-z_][A-Za-z0-9_-]*", "ID", skeleton)
        groups[skeleton].append(index)
    return [
        {"paragraphs": indexes, "preview": skeleton[:120]}
        for skeleton, indexes in groups.items()
        if len(indexes) > 1 and len(skeleton) >= 20
    ]


def shingles(text: str, size: int = 8, limit: int = 50000) -> set[str]:
    tokens = re.findall(r"[\u4e00-\u9fff]|[A-Za-z_$][A-Za-z0-9_$]*|\d+|\S", text)
    values = {" ".join(tokens[index : index + size]) for index in range(max(0, len(tokens) - size + 1))}
    if len(values) <= limit:
        return values
    return set(sorted(values)[:limit])


def corpus_similarity(
    current_text: str,
    corpus: Path | None,
    suffixes: set[str],
    excluded_paths: set[Path] | None = None,
) -> dict | None:
    if corpus is None or not corpus.exists():
        return None
    current = shingles(current_text)
    best = {"score": 0.0, "path": None}
    for path in corpus.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if path.resolve() in (excluded_paths or set()):
            continue
        try:
            candidate = shingles(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue
        union = current | candidate
        score = len(current & candidate) / len(union) if union else 0.0
        if score > best["score"]:
            best = {"score": round(score, 4), "path": str(path)}
    return best


def code_corpus_similarity(
    code_files: dict[str, list[str]],
    corpus: Path | None,
    excluded_paths: set[Path] | None = None,
) -> dict | None:
    if corpus is None or not corpus.exists():
        return None
    candidates = []
    for path in corpus.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in CODE_SUFFIXES:
            continue
        if path.resolve() in (excluded_paths or set()):
            continue
        try:
            candidates.append((path, shingles(path.read_text(encoding="utf-8"))))
        except (UnicodeDecodeError, OSError):
            continue
    best = {"score": 0.0, "current_path": None, "corpus_path": None}
    for current_name, lines in code_files.items():
        current = shingles("\n".join(lines))
        for candidate_path, candidate in candidates:
            union = current | candidate
            score = len(current & candidate) / len(union) if union else 0.0
            if score > best["score"]:
                best = {"score": round(score, 4), "current_path": current_name, "corpus_path": str(candidate_path)}
    return best


def add_issue(issues: list[dict[str, object]], severity: str, code: str, message: str, evidence: object) -> None:
    issues.append({"severity": severity, "code": code, "message": message, "evidence": evidence})


def audit(
    code_dir: Path,
    module_dir: Path | None,
    document: Path | None,
    comparison_corpus: Path | None,
    document_type: str | None = None,
    document_selection_reason: str | None = None,
) -> tuple[dict, dict]:
    modules = read_modules(module_dir)
    manifest = make_manifest(code_dir, modules)
    code_files = {entry["path"]: (code_dir / entry["path"]).read_text(encoding="utf-8").splitlines() for entry in manifest["files"]}
    code_text = "\n".join("\n".join(lines) for lines in code_files.values())
    issues: list[dict[str, object]] = []
    if not code_dir.is_dir():
        add_issue(issues, "error", "source-directory", "源码目录不存在或不是目录", str(code_dir))
    if module_dir is not None and not module_dir.is_dir():
        add_issue(issues, "error", "module-directory", "模块目录不存在或不是目录", str(module_dir))
    elif module_dir is not None:
        module_files = sorted(path.name for path in module_dir.glob("*.md") if path.is_file())
        expected_module_files = [f"{index:02d}.md" for index in range(1, 11)]
        if module_files != expected_module_files:
            add_issue(issues, "error", "module-file-set", "模块目录必须恰好包含 01.md 到 10.md", module_files)
    if document is not None and not document.is_file():
        add_issue(issues, "error", "selected-document", "指定的鉴别文档不存在", str(document))
    if comparison_corpus is not None and not comparison_corpus.is_dir():
        add_issue(issues, "error", "comparison-corpus", "指定的历史材料目录不存在或不是目录", str(comparison_corpus))
    invalid_names = [name for name in code_files if not re.match(r"^(?:0[1-9]|10)-.+\.txt$", name)]
    if len(code_files) != 10:
        add_issue(issues, "error", "source-file-count", "源码目录必须恰好包含 10 个编号代码文件", len(code_files))
    if invalid_names:
        add_issue(issues, "error", "source-file-names", "源码文件名必须使用 01-模块名称.txt 到 10-模块名称.txt", invalid_names)
    source_line_total = sum(entry["nonempty_lines"] for entry in manifest["files"])
    if source_line_total < 3000:
        add_issue(issues, "error", "source-line-total", "源码非空行总数不足 3000 行", source_line_total)

    placeholders = [
        f"{name}:{index}"
        for name, lines in code_files.items()
        for index, line in enumerate(lines, 1)
        if PLACEHOLDER_PATTERN.search(line)
    ]
    empty_implementations = [
        f"{name}:{index}"
        for name, lines in code_files.items()
        for index, line in enumerate(lines, 1)
        if EMPTY_IMPLEMENTATION_PATTERN.search(line)
    ]
    for name, lines in code_files.items():
        text = "\n".join(lines)
        for pattern in MULTILINE_EMPTY_IMPLEMENTATION_PATTERNS:
            for match in pattern.finditer(text):
                empty_implementations.append(f"{name}:{text.count(chr(10), 0, match.start()) + 1}")
    empty_implementations = sorted(set(empty_implementations))
    generated_markers = [
        f"{name}:{index}"
        for name, lines in code_files.items()
        for index, line in enumerate(lines, 1)
        if GENERATED_OR_THIRD_PARTY_PATTERN.search(line)
    ]
    low_value_files = [entry for entry in manifest["files"] if entry["nonempty_lines"] >= 40 and entry["low_value_ratio"] > 0.60]
    exact_repeat = repeated_window_coverage(code_files, structural=False)
    structural_repeat = repeated_window_coverage(code_files, structural=True)
    if placeholders:
        add_issue(issues, "error", "placeholder-code", "源码包含明确的占位或未实现逻辑", placeholders[:30])
    if empty_implementations:
        add_issue(issues, "error", "empty-implementation", "源码包含空方法、空函数或空组件实现", empty_implementations[:30])
    if generated_markers:
        add_issue(issues, "error", "generated-or-third-party", "源码包含自动生成或第三方代码标记", generated_markers[:30])
    if low_value_files:
        add_issue(issues, "error", "low-value-file", "部分代码文件主要由导入、访问器或结构符号组成", low_value_files)
    if exact_repeat > 0.20:
        add_issue(issues, "error", "exact-code-repetition", "跨文件重复代码块覆盖率过高", round(exact_repeat, 4))
    elif exact_repeat > 0.12:
        add_issue(issues, "warning", "exact-code-repetition", "跨文件存在较多重复代码块", round(exact_repeat, 4))
    if structural_repeat > 0.60:
        add_issue(issues, "error", "structural-repetition", "替换标识符后仍存在过高的同构代码比例", round(structural_repeat, 4))
    elif structural_repeat > 0.45:
        add_issue(issues, "warning", "structural-repetition", "替换标识符后仍存在较高的同构代码比例", round(structural_repeat, 4))

    generic_modules = [item["name"] for item in modules if GENERIC_MODULE_PATTERN.fullmatch(item["name"])]
    if len(generic_modules) > 2:
        add_issue(issues, "error", "generic-modules", "通用支撑模块超过两个", generic_modules)

    paragraphs = document_paragraphs(document)
    business_terms = [item["name"] for item in modules]
    duplicate_paragraphs = paragraph_template_duplicates(paragraphs, business_terms)
    duplicate_paragraph_instances = sum(len(group["paragraphs"]) - 1 for group in duplicate_paragraphs)
    if duplicate_paragraph_instances >= 3:
        add_issue(issues, "error", "document-template-repetition", "文档中存在多组仅替换术语的重复段落", duplicate_paragraphs[:20])
    elif duplicate_paragraphs:
        add_issue(issues, "warning", "document-template-repetition", "文档中存在重复段落骨架", duplicate_paragraphs[:20])

    if document and document.exists() and modules:
        document_text = document.read_text(encoding="utf-8")
        missing_modules = [item["name"] for item in modules if item["name"] not in document_text]
        if missing_modules:
            add_issue(issues, "error", "document-module-consistency", "鉴别文档未覆盖全部核心模块", missing_modules)

    filename_mismatches = [
        {"path": entry["path"], "expected_module_name": entry["module_name"]}
        for entry in manifest["files"]
        if entry["module_id"] and Path(entry["path"]).stem[3:] != entry["module_name"]
    ]
    if filename_mismatches:
        add_issue(issues, "error", "code-module-consistency", "代码文件名与同编号模块名称不一致", filename_mismatches)
    no_core_methods = [entry["path"] for entry in manifest["files"] if not entry["core_methods"]]
    if no_core_methods:
        add_issue(issues, "error", "core-method-visibility", "部分文件未识别到明确的核心方法", no_core_methods)
    no_languages = [entry["path"] for entry in manifest["files"] if not entry["languages"]]
    if no_languages:
        add_issue(issues, "error", "source-language-detection", "部分文件无法识别出明确的编程语言", no_languages)
    code_term_hits = sum(
        1
        for term in business_terms
        if any(term in "\n".join(lines) for lines in code_files.values())
    )
    business_term_code_coverage = round(code_term_hits / len(business_terms), 4) if business_terms else None
    if business_term_code_coverage is not None and business_term_code_coverage < 0.5:
        add_issue(issues, "warning", "business-term-code-coverage", "源码正文中的核心业务术语覆盖率偏低", business_term_code_coverage)

    current_code_paths = {(code_dir / name).resolve() for name in code_files}
    code_similarity = code_corpus_similarity(code_files, comparison_corpus, current_code_paths)
    document_similarity = (
        corpus_similarity(
            document.read_text(encoding="utf-8"),
            comparison_corpus,
            DOCUMENT_SUFFIXES,
            {document.resolve()},
        )
        if document and document.exists()
        else None
    )
    if code_similarity and code_similarity["score"] >= 0.45:
        add_issue(issues, "error", "code-corpus-similarity", "源码与历史材料高度相似", code_similarity)
    if document_similarity and document_similarity["score"] >= 0.55:
        add_issue(issues, "error", "document-corpus-similarity", "文档与历史材料高度相似", document_similarity)

    if document_type is None and document is not None:
        document_type = "operation-manual" if "操作手册" in document.name else "design-specification"
    report = {
        "version": 1,
        "status": "fail" if any(issue["severity"] == "error" for issue in issues) else "pass",
        "disclaimer": "本报告中的阈值为材料内部质量控制指标，不是登记机关公布的审查阈值。",
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "document_type": document_type,
        "document_selection_reason": document_selection_reason,
        "metrics": {
            "code_files": len(code_files),
            "code_nonempty_lines": sum(entry["nonempty_lines"] for entry in manifest["files"]),
            "exact_repeated_window_coverage": round(exact_repeat, 4),
            "structural_repeated_window_coverage": round(structural_repeat, 4),
            "generic_module_count": len(generic_modules),
            "document_paragraphs": len(paragraphs),
            "document_duplicate_skeleton_groups": len(duplicate_paragraphs),
            "business_term_code_coverage": business_term_code_coverage,
            "code_corpus_similarity": code_similarity,
            "document_corpus_similarity": document_similarity,
        },
        "source_files": [
            {"path": entry["path"], "sha256": entry["sha256"]}
            for entry in manifest["files"]
        ],
        "issues": issues,
    }
    return manifest, report


def write_markdown_report(report: dict, path: Path) -> None:
    lines = ["# 独创性与模板化风险审计", "", f"审计结果：{'通过' if report['status'] == 'pass' else '未通过'}", "", report["disclaimer"], "", "## 指标", ""]
    for key, value in report["metrics"].items():
        lines.append(f"- {key}: {json.dumps(value, ensure_ascii=False)}")
    lines.extend(["", "## 问题", ""])
    if not report["issues"]:
        lines.append("未发现阻断交付的问题。")
    else:
        for issue in report["issues"]:
            lines.append(f"- [{issue['severity']}] {issue['message']}（{issue['code']}）")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-dir", required=True, type=Path)
    parser.add_argument("--module-dir", required=True, type=Path)
    parser.add_argument("--document", required=True, type=Path)
    parser.add_argument("--comparison-corpus", type=Path)
    parser.add_argument("--document-type", required=True, choices=("operation-manual", "design-specification"))
    parser.add_argument("--document-selection-reason", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--allow-high-risk", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest, report = audit(
        args.code_dir,
        args.module_dir,
        args.document,
        args.comparison_corpus,
        args.document_type,
        args.document_selection_reason,
    )
    (args.output_dir / "source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "originality-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(report, args.output_dir / "originality-report.md")
    print(f"Audit status: {report['status']}")
    return 0 if report["status"] == "pass" or args.allow_high_risk else 1


if __name__ == "__main__":
    raise SystemExit(main())
