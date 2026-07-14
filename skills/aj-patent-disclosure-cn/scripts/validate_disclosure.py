#!/usr/bin/env python3
"""Validate structured patent disclosure input before DOCX generation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


PLACEHOLDER_PATTERNS = (
    re.compile(r"【待确认[:：]?"),
    re.compile(r"\b(?:TBD|TODO|FIXME)\b", re.IGNORECASE),
    re.compile(r"待补(?:充|录|写|实验|检索)?"),
)
QUANTITATIVE_PATTERN = re.compile(
    r"\d+(?:\.\d+)?\s*(?:%|％|ms|毫秒|秒|分钟|倍|MB|GB|KB|dB|帧|次/秒|QPS)",
    re.IGNORECASE,
)
MARKETING_WORDS = (
    "行业领先",
    "世界首创",
    "全球首创",
    "革命性",
    "颠覆性",
    "完美",
    "绝对安全",
    "百分之百",
)
ALLOWED_FACT_STATUSES = {
    "用户已确认",
    "资料有据",
    "合理推断",
    "待确认",
    "建议方案",
    "user-confirmed",
    "source-backed",
    "inferred",
    "to-confirm",
    "proposal",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a structured Chinese patent disclosure JSON file"
    )
    parser.add_argument("--input", required=True, help="Path to disclosure JSON")
    parser.add_argument(
        "--final",
        action="store_true",
        help="Apply final-delivery checks (no unresolved placeholders, evidence for numbers)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable validation report",
    )
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def iter_strings(value: Any, path: str = "$") -> Iterable[Tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")


def has_placeholder(value: str) -> bool:
    return any(pattern.search(value) for pattern in PLACEHOLDER_PATTERNS)


def effect_text(item: Any) -> str:
    if not isinstance(item, dict):
        return text(item)
    for key in ("effect", "description", "result", "text"):
        if text(item.get(key)):
            return text(item.get(key))
    return ""


def has_effect_basis(item: Dict[str, Any]) -> bool:
    return any(
        text(item.get(key))
        for key in ("basis", "evidence", "test_conditions", "source", "comparison_baseline")
    )


def validate_payload(
    payload: Dict[str, Any], input_path: Path, final: bool
) -> Dict[str, List[Dict[str, str]]]:
    errors: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    info: List[Dict[str, str]] = []

    def add(bucket: List[Dict[str, str]], code: str, path: str, message: str) -> None:
        bucket.append({"code": code, "path": path, "message": message})

    for key in ("title", "technical_field", "background"):
        if not payload.get(key):
            add(errors, "required", f"$.{key}", f"missing required field: {key}")

    title = text(payload.get("title"))
    if title:
        if len(title) > 25:
            add(
                warnings,
                "title-length",
                "$.title",
                f"title has {len(title)} characters; verify that the length is necessary",
            )
        for word in MARKETING_WORDS:
            if word in title:
                add(warnings, "marketing-language", "$.title", f"remove marketing term: {word}")

    invention = payload.get("invention")
    if not isinstance(invention, dict):
        add(errors, "required-object", "$.invention", "invention must be an object")
        invention = {}

    problem = text(invention.get("technical_problem")) or text(invention.get("purpose"))
    if not problem:
        add(
            errors,
            "technical-problem",
            "$.invention.technical_problem",
            "state the technical problem or purpose",
        )

    solution = text(invention.get("solution"))
    solution_steps = as_list(invention.get("solution_steps"))
    if not solution and not solution_steps:
        add(
            errors,
            "technical-solution",
            "$.invention",
            "provide invention.solution or invention.solution_steps",
        )
    if final and not solution_steps:
        add(
            errors,
            "structured-solution",
            "$.invention.solution_steps",
            "final delivery requires step/module-level structured disclosure",
        )

    if solution_steps:
        seen_ids: set[str] = set()
        for index, step in enumerate(solution_steps):
            path = f"$.invention.solution_steps[{index}]"
            if isinstance(step, dict):
                step_id = text(step.get("id"))
                action = text(step.get("action")) or text(step.get("description"))
                if not action:
                    add(errors, "step-action", path, "structured step requires action or description")
                if step_id:
                    if step_id in seen_ids:
                        add(errors, "duplicate-step-id", f"{path}.id", f"duplicate step id: {step_id}")
                    seen_ids.add(step_id)
                if final and not (step.get("input") or step.get("inputs")):
                    add(warnings, "step-input", path, "verify the step input or trigger condition")
                if final and not (step.get("output") or step.get("outputs")):
                    add(warnings, "step-output", path, "verify the step output or resulting state")
            elif not text(step):
                add(errors, "empty-step", path, "solution step cannot be empty")

    effects = as_list(invention.get("effects"))
    if not effects:
        add(errors, "effects", "$.invention.effects", "provide at least one technical effect")
    for index, item in enumerate(effects):
        path = f"$.invention.effects[{index}]"
        value = effect_text(item)
        if not value:
            add(errors, "empty-effect", path, "effect description cannot be empty")
            continue
        if QUANTITATIVE_PATTERN.search(value):
            supported = isinstance(item, dict) and has_effect_basis(item)
            if not supported:
                target = errors if final else warnings
                add(
                    target,
                    "quantitative-evidence",
                    path,
                    "quantitative effect needs test conditions, baseline, evidence, or source",
                )

    embodiments = as_list(payload.get("embodiments"))
    if not embodiments:
        add(errors, "embodiment", "$.embodiments", "provide at least one end-to-end embodiment")
    structured_embodiment = False
    for index, embodiment in enumerate(embodiments):
        path = f"$.embodiments[{index}]"
        if isinstance(embodiment, dict):
            steps = as_list(embodiment.get("steps"))
            if steps:
                structured_embodiment = True
            else:
                add(warnings, "embodiment-steps", path, "structured embodiment should include steps")
            if final and not embodiment.get("outputs"):
                add(warnings, "embodiment-output", path, "verify embodiment outputs/results")
        elif not text(embodiment):
            add(errors, "empty-embodiment", path, "embodiment cannot be empty")
    if final and embodiments and not structured_embodiment:
        add(
            errors,
            "structured-embodiment",
            "$.embodiments",
            "final delivery requires at least one embodiment with structured steps",
        )

    figures = as_list(payload.get("figures"))
    figure_numbers: set[str] = set()
    for index, figure in enumerate(figures):
        path = f"$.figures[{index}]"
        if not isinstance(figure, dict):
            if not text(figure):
                add(errors, "empty-figure", path, "figure entry cannot be empty")
            continue
        number = text(figure.get("num"))
        caption = text(figure.get("caption"))
        if not number:
            add(errors, "figure-number", path, "figure requires num")
        elif number in figure_numbers:
            add(errors, "duplicate-figure", f"{path}.num", f"duplicate figure number: {number}")
        figure_numbers.add(number)
        if not caption:
            add(errors, "figure-caption", path, "figure requires caption")
        file_value = text(figure.get("file"))
        if final and file_value:
            candidates = [Path(file_value), input_path.parent / file_value]
            if not any(candidate.exists() for candidate in candidates):
                add(warnings, "figure-file", f"{path}.file", f"figure file not found: {file_value}")

    facts = as_list(payload.get("facts"))
    for index, fact in enumerate(facts):
        if not isinstance(fact, dict):
            continue
        status = text(fact.get("status"))
        if status and status not in ALLOWED_FACT_STATUSES:
            add(
                warnings,
                "fact-status",
                f"$.facts[{index}].status",
                f"unrecognized fact status: {status}",
            )

    prior_art = as_list(payload.get("prior_art"))
    for index, document in enumerate(prior_art):
        if not isinstance(document, dict):
            continue
        identifier = text(document.get("publication_no")) or text(document.get("document_id"))
        if identifier and not text(document.get("source_url")):
            add(
                warnings,
                "source-url",
                f"$.prior_art[{index}]",
                f"add a traceable source URL for {identifier}",
            )

    claim_strategy = payload.get("claim_strategy", {})
    if isinstance(claim_strategy, dict):
        independent = as_list(claim_strategy.get("independent_subjects"))
        support_matrix = as_list(claim_strategy.get("support_matrix"))
        if final and independent and not support_matrix:
            add(
                warnings,
                "support-matrix",
                "$.claim_strategy.support_matrix",
                "add a support matrix for proposed independent subjects",
            )

    for path, value in iter_strings(payload):
        if final and has_placeholder(value):
            add(errors, "placeholder", path, "unresolved placeholder in final delivery")
        for word in MARKETING_WORDS:
            if word in value and path != "$.title":
                add(warnings, "marketing-language", path, f"review marketing/absolute term: {word}")

    if not figures:
        add(info, "figures", "$.figures", "no figures declared; verify whether drawings are necessary")
    if not prior_art:
        add(info, "prior-art", "$.prior_art", "no verified prior-art records included")

    return {"errors": errors, "warnings": warnings, "info": info}


def print_human(report: Dict[str, List[Dict[str, str]]], input_path: Path, final: bool) -> None:
    mode = "final" if final else "draft"
    print(f"Validation mode: {mode}")
    print(f"Input: {input_path}")
    for bucket_name in ("errors", "warnings", "info"):
        items = report[bucket_name]
        print(f"\n{bucket_name.upper()} ({len(items)})")
        for item in items:
            print(f"- [{item['code']}] {item['path']}: {item['message']}")
    print(
        f"\nSummary: {len(report['errors'])} error(s), "
        f"{len(report['warnings'])} warning(s), {len(report['info'])} info item(s)"
    )


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    try:
        payload = load_json(input_path)
    except ValueError as exc:
        if args.json:
            print(json.dumps({"errors": [{"code": "input", "path": "$", "message": str(exc)}]}, ensure_ascii=False))
        else:
            print(f"Validation failed: {exc}", file=sys.stderr)
        return 2

    report = validate_payload(payload, input_path=input_path, final=args.final)
    if args.json:
        output = {
            "input": str(input_path),
            "mode": "final" if args.final else "draft",
            **report,
            "summary": {key: len(value) for key, value in report.items()},
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_human(report, input_path=input_path, final=args.final)
    return 2 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
