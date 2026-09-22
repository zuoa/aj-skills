#!/usr/bin/env python3
"""
Deterministic patent disclosure docx generator (Markdown -> DOCX via pypandoc).

Usage:
  python scripts/generate_docx.py --input disclosure.json \
    --output outputs/交底书_xxx_v1.0.docx --with-markdown
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

DEFAULT_REFERENCE_DOC = Path(__file__).resolve().parents[1] / "assets/templates/技术交底书模板.docx"
GENERATOR_VERSION = "7"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate patent disclosure docx from structured JSON")
    p.add_argument("--input", required=True, help="Path to JSON input file")
    p.add_argument("--output", required=True, help="Path to output .docx file")
    p.add_argument("--overwrite", action="store_true", help="Force regenerate output")
    p.add_argument("--workflow-case", type=Path, help="Verify confirmed stage versions before exporting this case")
    p.add_argument("--validation-report", type=Path, help="Write final machine validation report after successful export")
    p.add_argument(
        "--no-strict-cnipa",
        action="store_true",
        help="Disable disclosure reference styling (legacy flag name; not a statutory CNIPA form)",
    )
    p.add_argument(
        "--word-only",
        action="store_true",
        help="Require .docx output only; fail if conversion toolchain unavailable",
    )
    p.add_argument(
        "--with-markdown",
        action="store_true",
        help="Also write a diff-friendly .md file next to the .docx",
    )
    return p.parse_args()


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def stable_hash(payload: Dict[str, Any], strict_cnipa: bool) -> str:
    data = {
        "payload": payload,
        "strict_cnipa": strict_cnipa,
        "reference_doc_sha256": _file_sha256(DEFAULT_REFERENCE_DOC) if strict_cnipa else "",
        "generator_version": GENERATOR_VERSION,
    }
    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def hash_sidecar_path(output: Path) -> Path:
    return output.with_suffix(output.suffix + ".sha256")


def should_skip(output: Path, input_hash: str) -> bool:
    sidecar = hash_sidecar_path(output)
    if not output.exists() or not sidecar.exists():
        return False
    old_hash = sidecar.read_text(encoding="utf-8").strip()
    return old_hash == input_hash


def write_hash(output: Path, input_hash: str) -> None:
    sidecar = hash_sidecar_path(output)
    sidecar.write_text(input_hash + "\n", encoding="utf-8")


def validate_strict_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required_text_fields = ["title", "technical_field", "background"]
    for key in required_text_fields:
        if not str(payload.get(key, "")).strip():
            errors.append(f"missing required field: {key}")

    invention = payload.get("invention", {})
    if not isinstance(invention, dict):
        errors.append("invention must be an object")
        invention = {}

    for key in ("technical_problem", "purpose"):
        value = invention.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"missing required text field: invention.{key}")

    if not str(invention.get("solution", "")).strip() and not invention.get("solution_steps"):
        errors.append("missing required field: invention.solution or invention.solution_steps")

    effects = invention.get("effects")
    if effects is None or (isinstance(effects, str) and not effects.strip()) or (
        isinstance(effects, list) and not effects
    ):
        errors.append("missing required field: invention.effects")

    embodiments = payload.get("embodiments", [])
    if not isinstance(embodiments, list) or not embodiments:
        errors.append("strict mode requires at least 1 end-to-end embodiment")

    return errors


def _to_text(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def _as_list(v: Any) -> List[Any]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _to_markdown_list(items: List[Any], ordered: bool = False) -> List[str]:
    out: List[str] = []
    for i, item in enumerate(items, start=1):
        prefix = f"{i}. " if ordered else "- "
        out.append(prefix + _to_text(item))
    return out


def _sanitize_title(text: str) -> str:
    t = _to_text(text)
    # Remove heading/list/code markers from title to avoid raw markdown in H1.
    t = t.lstrip("#").strip()
    t = t.replace("**", "").replace("*", "").replace("`", "")
    if t.startswith("- "):
        t = t[2:].strip()
    return t or "发明专利技术交底书"


def _normalize_markdown_block(text: Any) -> str:
    """Normalize user-provided markdown fragments for stable pandoc parsing."""
    s = _to_text(text)
    if not s:
        return ""

    lines = s.splitlines()
    # Remove outer fenced code block if the whole fragment is wrapped.
    if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip().startswith("```"):
        lines = lines[1:-1]

    out: List[str] = []
    for line in lines:
        stripped = line.strip()
        is_bold_heading = bool(re.match(r"^\*\*.+\*\*$", stripped))
        is_list = bool(re.match(r"^([-*+]|\d+\.)\s+", stripped))
        if is_bold_heading and out and out[-1].strip() != "":
            out.append("")
        if is_bold_heading:
            out.append(line.rstrip())
            out.append("")
            continue
        # Ensure blank line before list blocks so markdown parser won't treat list
        # markers as plain text continuation.
        if is_list and out and out[-1].strip() != "":
            out.append("")
        out.append(line.rstrip())
    return "\n".join(out).strip()


FIELD_LABELS = {
    "status": "状态",
    "source": "来源",
    "basis": "依据",
    "evidence": "证据",
    "evidence_status": "证据状态",
    "test_conditions": "测试条件",
    "comparison_baseline": "对比基线",
    "input": "输入",
    "inputs": "输入",
    "action": "处理",
    "processing": "处理",
    "output": "输出",
    "outputs": "输出",
    "technical_effect": "技术作用/效果",
    "parameters": "参数",
    "conditions": "条件",
    "description_support": "发明内容支撑",
    "embodiment_support": "实施例支撑",
    "figure_support": "附图支撑",
    "risk": "风险",
    "source_url": "来源链接",
    "publication_no": "公开号",
    "publication_date": "公开日",
    "priority_date": "优先权日",
    "applicant": "申请人",
    "relevant_passages": "相关位置",
    "relevance": "相关性",
    "definition": "定义",
    "name": "名称",
    "value": "取值",
    "feature": "技术特征",
}


def _inline_value(value: Any) -> str:
    if isinstance(value, list):
        return "；".join(_inline_value(item) for item in value if _inline_value(item))
    if isinstance(value, dict):
        return "；".join(
            f"{FIELD_LABELS.get(str(key), str(key))}={_inline_value(item)}"
            for key, item in value.items()
            if _inline_value(item)
        )
    return _to_text(value)


def _dict_primary(item: Dict[str, Any]) -> Tuple[str, str]:
    for key in (
        "description",
        "effect",
        "feature",
        "action",
        "text",
        "title",
        "term",
        "document_id",
        "publication_no",
    ):
        value = _inline_value(item.get(key))
        if value:
            return key, value
    return "", ""


def _append_items(lines: List[str], value: Any, ordered: bool = False) -> None:
    items = _as_list(value)
    if not items:
        lines.append("- 无")
        return

    for index, item in enumerate(items, start=1):
        prefix = f"{index}. " if ordered else "- "
        if not isinstance(item, dict):
            lines.append(prefix + _normalize_markdown_block(item))
            continue

        primary_key, primary = _dict_primary(item)
        lines.append(prefix + (primary or "记录"))
        nested_indent = "    " if ordered else "  "
        for key, detail in item.items():
            if key in {primary_key, "id", "num", "title", "status", "evidence_status", "source", "risk"}:
                continue
            rendered = _inline_value(detail)
            if rendered:
                lines.append(f"{nested_indent}- **{FIELD_LABELS.get(str(key), str(key))}：**{rendered}")


def _append_named_block(lines: List[str], heading: str, value: Any) -> None:
    if value is None or value == "" or value == []:
        return
    lines.extend(["", heading, ""])
    if isinstance(value, (list, dict)):
        if isinstance(value, dict):
            _append_items(lines, [value])
        else:
            _append_items(lines, value)
    else:
        lines.append(_normalize_markdown_block(value))


def _append_solution_steps(lines: List[str], steps: Any) -> None:
    for index, step in enumerate(_as_list(steps), start=1):
        if not isinstance(step, dict):
            lines.append(f"{index}. {_normalize_markdown_block(step)}")
            continue
        step_id = _to_text(step.get("id")) or f"S{index}"
        action = _to_text(step.get("action")) or _to_text(step.get("description"))
        lines.append(f"#### {step_id} {action}".rstrip())
        lines.append("")
        for key in (
            "input",
            "inputs",
            "conditions",
            "processing",
            "output",
            "outputs",
            "parameters",
            "technical_effect",
        ):
            rendered = _inline_value(step.get(key))
            if rendered:
                lines.append(f"- **{FIELD_LABELS.get(key, key)}：**{rendered}")
        lines.append("")


def render_markdown(payload: Dict[str, Any], strict_cnipa: bool = False) -> str:
    title = _sanitize_title(_to_text(payload.get("title")))
    date_text = _to_text(payload.get("date")) or dt.date.today().isoformat()
    inventors = payload.get("inventors", [])
    applicant = _to_text(payload.get("applicant"))

    invention = payload.get("invention", {})
    if not isinstance(invention, dict):
        invention = {}
    effects = _as_list(invention.get("effects"))

    figures = payload.get("figures", [])
    embodiments = payload.get("embodiments", [])
    appendices = _as_list(payload.get("appendices"))

    def table_text(value):
        return _inline_value(value).replace("|", "\\|").replace("\n", " ")

    lines: List[str] = [
        "| 发明名称 | " + table_text(title) + " |",
        "| --- | --- |",
        "| 发明人姓名 | " + table_text("、".join(inventors)) + " |",
        "| 所属部门 | " + table_text(payload.get("department")) + " |",
        "| 第一发明人身份证号 | " + table_text(payload.get("first_inventor_id")) + " |",
        "", "## 本发明的关键点和欲保护点是什么？", "",
    ]
    _append_named_block(lines, "### 关键技术点和欲保护点", payload.get("protection_points") or invention.get("key_features"))
    lines.extend(["", "### 技术领域", ""])
    lines.append(_normalize_markdown_block(payload.get("technical_field")))

    _append_named_block(lines, "### 术语定义", payload.get("terminology"))

    lines.extend(["", "### 背景技术", ""])
    background = payload.get("background")
    if isinstance(background, dict):
        summary = background.get("summary") or background.get("known_solution")
        if summary:
            lines.append(_normalize_markdown_block(summary))
        _append_named_block(lines, "#### 现有方案", background.get("current_solutions"))
        _append_named_block(lines, "#### 现有方案的技术不足", background.get("limitations"))
    else:
        lines.append(_normalize_markdown_block(background))

    lines.extend(["", "### 要解决的技术问题", ""])
    problem = invention.get("technical_problem")
    lines.append(_normalize_markdown_block(problem))

    lines.extend(["", "### 发明目的", ""])
    lines.append(_normalize_markdown_block(invention.get("purpose")))

    lines.extend(["", "### 技术方案", ""])
    if invention.get("solution"):
        lines.append(_normalize_markdown_block(invention.get("solution")))
    _append_named_block(lines, "#### 输入/处理对象", invention.get("inputs"))
    _append_named_block(lines, "#### 核心必要技术特征", invention.get("key_features"))
    if invention.get("solution_steps"):
        lines.extend(["", "#### 处理步骤/模块关系", ""])
        _append_solution_steps(lines, invention.get("solution_steps"))
    _append_named_block(lines, "#### 输出", invention.get("outputs"))
    _append_named_block(lines, "#### 参考资料", payload.get("references"))
    lines.extend(["", "### 具体实施方式", ""])
    if embodiments:
        for i, emb in enumerate(embodiments, start=1):
            if not isinstance(emb, dict):
                lines.append(f"#### 实施例{i}")
                lines.append("")
                lines.append(_normalize_markdown_block(emb))
                lines.append("")
                continue

            emb_title = _to_text(emb.get("title"))
            lines.append(f"#### 实施例{i}" + (f"：{emb_title}" if emb_title else ""))
            lines.append("")
            if emb.get("objective"):
                lines.append(_normalize_markdown_block(emb.get("objective")))
            _append_named_block(lines, "#### 前提与环境", emb.get("preconditions"))
            if emb.get("steps"):
                lines.extend(["", "#### 实施步骤", ""])
                _append_solution_steps(lines, emb.get("steps"))
            _append_named_block(lines, "#### 参数与条件", emb.get("parameters"))
            _append_named_block(lines, "#### 输出与结果", emb.get("outputs"))
            _append_named_block(
                lines,
                "#### 效果证据",
                emb.get("observed_effects") or emb.get("effects"),
            )
            _append_named_block(lines, "#### 替代实现", emb.get("variations"))
            if emb.get("figure_refs"):
                lines.extend(["", f"对应附图：{_inline_value(emb.get('figure_refs'))}", ""])
    else:
        lines.append("无")

    lines.extend(["", "## 与现有技术相比，本发明有何优点？", ""])
    _append_items(lines, effects, ordered=True)
    lines.extend(["", "## 本发明是否经过实验、模拟、使用而证明可行，结果如何？", ""])
    verification = payload.get("verification", {})
    if isinstance(verification, dict):
        for key, label in (("status", "验证情况"), ("method", "验证方法"), ("conditions", "验证条件"),
                           ("baseline", "对比基线"), ("results", "验证结果"), ("evidence", "验证依据")):
            if verification.get(key):
                lines.extend([f"**{label}：**{_inline_value(verification[key])}", ""])
    elif verification:
        lines.append(_normalize_markdown_block(verification))
    lines.extend(["", "## 本发明的变更设计（替代方案）及其它用途：", ""])
    _append_items(lines, invention.get("alternatives") or payload.get("alternative_statement"))
    _append_named_block(lines, "### 其它用途", payload.get("other_uses"))
    lines.extend(["", "## 附图及说明", ""])
    for fig in figures:
        if isinstance(fig, dict):
            caption = f"图{fig['num']} {fig['caption']}"
            if fig.get("file"):
                lines.extend([f"![{caption}](<{fig['file']}>){{width=14cm}}", ""])
            else:
                lines.extend([caption, ""])
            if fig.get("elements"):
                lines.extend(["**图中标记：**" + _inline_value(fig['elements']), ""])
    if not figures and payload.get("drawings_not_applicable"):
        lines.append(_normalize_markdown_block(payload['drawings_not_applicable']))

    return "\n".join(lines).strip() + "\n"


def convert_markdown_to_docx(markdown_text: str, output: Path, strict_cnipa: bool = False) -> None:
    import pypandoc

    output.parent.mkdir(parents=True, exist_ok=True)

    extra_args: List[str] = ["--resource-path", str(output.resolve().parent)]
    if strict_cnipa:
        if not DEFAULT_REFERENCE_DOC.exists():
            raise RuntimeError(
                f"strict mode requires reference template: {DEFAULT_REFERENCE_DOC}"
            )
        extra_args.extend(["--reference-doc", str(DEFAULT_REFERENCE_DOC)])

    # Use markdown+raw_tex to keep broad markdown compatibility.
    pypandoc.convert_text(
        markdown_text,
        to="docx",
        format="markdown",
        outputfile=str(output),
        extra_args=extra_args,
    )


def write_markdown_fallback(markdown_text: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown_text, encoding="utf-8")


def generate_docx(
    payload: Dict[str, Any],
    output: Path,
    strict_cnipa: bool = False,
    word_only: bool = False,
) -> Tuple[Path, str]:
    markdown_text = render_markdown(payload, strict_cnipa=strict_cnipa)
    try:
        convert_markdown_to_docx(markdown_text, output, strict_cnipa=strict_cnipa)
        from docx_layout import apply_layout
        apply_layout(output, payload, DEFAULT_REFERENCE_DOC)
        return output, "docx"
    except Exception as e:
        if word_only:
            raise RuntimeError(
                "docx conversion failed in --word-only mode. "
                f"Details: {e}"
            ) from e
        md_output = output.with_suffix(".md")
        write_markdown_fallback(markdown_text, md_output)
        print(f"docx conversion unavailable. Wrote markdown fallback: {md_output}")
        return md_output, "md"


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    strict_cnipa = not args.no_strict_cnipa
    if args.validation_report is None:
        args.validation_report = output_path.with_suffix('.quality.json')

    if args.validation_report:
        report_path = args.validation_report.resolve()
        if report_path in (input_path, output_path, output_path.with_suffix('.md')) or (report_path.exists() and not args.overwrite):
            print('Validation report path conflicts with input/output or already exists; choose a new version path.')
            return 2

    payload = read_json(input_path)
    # A case input remains gated even when the caller omits --workflow-case.
    workflow_case = args.workflow_case
    if workflow_case is None:
        workflow_case = next((parent for parent in input_path.parents if (parent / 'workflow/state.json').is_file()), None)
    if workflow_case is not None:
        from workflow import ensure_export
        try:
            ensure_export(workflow_case.resolve(), input_path)
        except (ValueError, OSError, KeyError) as exc:
            print(f"Workflow validation failed: {exc}")
            return 3
    if output_path.exists() and not args.overwrite:
        # Preserve all companion assets as well as the existing document.
        print("Output exists; use a new version filename or explicit --overwrite.")
        return 2
    if strict_cnipa:
        strict_errors = validate_strict_payload(payload)
        if strict_errors:
            print("Disclosure validation failed:")
            for err in strict_errors:
                print(f"- {err}")
            return 3

    # Generate in an isolated version-specific directory; never mix another draft's figures.
    from generate_figures import prepare_figures
    from validate_disclosure import validate_payload
    try:
        payload = prepare_figures(payload, input_path, output_path)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Figure generation failed: {exc}")
        return 3
    report = validate_payload(payload, output_path, final=True)
    if report["errors"]:
        for error in report["errors"]:
            print(f"[{error['code']}] {error['path']}: {error['message']}")
        return 3
    from check_output_coverage import check_output
    markdown_text = render_markdown(payload, strict_cnipa=strict_cnipa)
    coverage = check_output(payload, markdown_text)
    if coverage['errors']:
        for error in coverage['errors']:
            print(f"[{error['code']}] {error['path']}: {error['message']}")
        return 3
    input_hash = stable_hash(payload, strict_cnipa=strict_cnipa)

    markdown_output = output_path.with_suffix(".md")
    word_only = args.word_only or strict_cnipa
    generated_path, mode = generate_docx(
        payload,
        output_path,
        strict_cnipa=strict_cnipa,
        word_only=word_only,
    )
    coverage = check_output(payload, markdown_text, generated_path if mode == 'docx' else None)
    report['coverage'] = coverage['coverage']
    report['coverage_scope'] = coverage['scope']
    report['errors'].extend(coverage['errors'])
    if coverage['errors']:
        failed_report = output_path.with_suffix('.failed-quality.json')
        failed_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        for error in coverage['errors']:
            print(f"[{error['code']}] {error['path']}: {error['message']}")
        print(f'Output failed coverage review; not a final delivery. Details: {failed_report}')
        return 3
    write_hash(generated_path, input_hash)
    if args.with_markdown:
        write_markdown_fallback(
            markdown_text,
            markdown_output,
        )
        write_hash(markdown_output, input_hash)
        print(f"Generated Markdown companion: {markdown_output}")
    if mode == "docx":
        print(f"Generated: {generated_path}")
    else:
        print(f"Generated fallback markdown: {generated_path}")
    if args.validation_report:
        report_path = args.validation_report.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report['input_sha256'] = _file_sha256(input_path)
        report['output_sha256'] = _file_sha256(generated_path)
        report['output'] = str(generated_path)
        artifact_files = [(mode, generated_path)]
        if args.with_markdown and markdown_output != generated_path:
            artifact_files.append(('markdown', markdown_output))
        figure_dir = output_path.parent / (output_path.stem + '_figures')
        artifact_files.extend(('figure', path) for path in sorted(figure_dir.rglob('*')) if path.is_file())
        report['artifacts'] = [
            {'kind': kind, 'path': os.path.relpath(path, report_path.parent), 'sha256': _file_sha256(path)}
            for kind, path in artifact_files
        ]
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
