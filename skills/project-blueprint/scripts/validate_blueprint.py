#!/usr/bin/env python3
"""Read-only structural validation for project-blueprint artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_KINDS = {
    "PRD.md": "prd",
    "SPEC.md": "spec-index",
    "DESIGN.md": "design",
    "ARCHITECTURE.md": "architecture",
    "SECURITY.md": "security",
    "DEPLOY.md": "deploy",
    "ENGINEERING.md": "engineering",
}
REQUIRED_ADAPTERS = ("CLAUDE.md", "AGENTS.md")
ID_RE = {
    "prd": re.compile(r"\bPRD-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}\b"),
    "spec": re.compile(r"\bSPEC-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}\b"),
    "tbd": re.compile(r"\bTBD-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}\b"),
}
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
SPEC_HEADING_RE = re.compile(
    r"^#{2,4}\s+(SPEC-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3})\b.*$", re.MULTILINE
)
H2_RE = re.compile(r"^##\s+", re.MULTILINE)
H2_TITLE_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
OPEN_HEADING_RE = re.compile(
    r"^##\s+(?:Open decisions|待决定事项|待决策事项)\s*$", re.MULTILINE | re.IGNORECASE
)
COLOR_VALUE_RE = re.compile(
    r"(?:#[0-9a-fA-F]{3,8}\b|(?:rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color)\([^\n)]+\))",
    re.IGNORECASE,
)
TYPE_SIZE_RE = re.compile(r"(?<![\w.-])(?:0|[1-9]\d*(?:\.\d+)?)(?:px|rem|em|pt)\b", re.IGNORECASE)
GENERIC_FONT_RE = re.compile(
    r"\b(?:system-ui|ui-sans-serif|ui-serif|sans-serif|serif|monospace)\b",
    re.IGNORECASE,
)
UI_FOUNDATION_STATE_RE = re.compile(
    r"\b(?:confirmed|provisional|not-applicable)\b|已确认|暂定|不适用",
    re.IGNORECASE,
)
LAYOUT_STATE_RE = UI_FOUNDATION_STATE_RE
EMOJI_RE = re.compile(
    "["
    "\\u2600-\\u26FF"
    "\\u2700-\\u27BF"
    "\\U0001F1E6-\\U0001F1FF"
    "\\U0001F300-\\U0001FAFF"
    "]"
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def add(
    findings: list[Finding], severity: str, code: str, path: str, message: str
) -> None:
    findings.append(Finding(severity, code, path, message))


def adr_files(root: Path) -> list[Path]:
    """Return only ADR Markdown; unrelated repository docs are out of scope."""
    adr_dir = root / "docs" / "adr"
    return sorted(adr_dir.glob("*.md")) if adr_dir.is_dir() else []


def section_after(text: str, heading_match: re.Match[str]) -> str:
    start = heading_match.end()
    next_heading = H2_RE.search(text, start)
    return text[start : next_heading.start() if next_heading else len(text)]


def h2_section_matching(
    text: str,
    terms: tuple[str, ...],
    exclude_terms: tuple[str, ...] = (),
) -> str | None:
    """Return an H2 section whose localized title contains one of the terms."""
    for match in H2_TITLE_RE.finditer(text):
        title = match.group(1).strip().lower()
        if any(term in title for term in exclude_terms):
            continue
        if any(term in title for term in terms):
            return section_after(text, match)
    return None


def validate_design_contract(text: str, findings: list[Finding]) -> None:
    layout = h2_section_matching(
        text,
        ("application shell", "layout recommendation", "应用骨架", "布局推荐", "布局与导航"),
    )
    color = h2_section_matching(text, ("color", "palette", "配色", "色彩", "颜色", "色板"))
    typography = h2_section_matching(text, ("typography", "type system", "字体", "排版", "字号"))
    ui_foundation = h2_section_matching(
        text,
        (
            "ui foundation",
            "ui component system",
            "component sourcing",
            "ui 基础",
            "ui框架",
            "ui 框架",
            "组件基础",
            "组件库",
        ),
    )
    components = h2_section_matching(
        text,
        ("component", "组件"),
        (
            "ui foundation",
            "ui component system",
            "component sourcing",
            "ui 基础",
            "ui框架",
            "ui 框架",
            "组件基础",
            "组件库",
        ),
    )

    if layout is None:
        add(
            findings,
            "warning",
            "DESIGN_LAYOUT_MISSING",
            "DESIGN.md",
            "Add an application-shell section that selects a layout/navigation/work-surface composition and separates platform chrome such as SSO or tenant switching",
        )
    elif not LAYOUT_STATE_RE.search(layout):
        add(
            findings,
            "warning",
            "DESIGN_LAYOUT_UNRESOLVED",
            "DESIGN.md",
            "Layout recommendation must be confirmed, provisional, or explicitly not-applicable; record its compact-window transformation and platform chrome",
        )

    if color is None:
        add(
            findings,
            "warning",
            "DESIGN_COLOR_SYSTEM_MISSING",
            "DESIGN.md",
            "Add an overall color-system section with semantic tokens, theme values, interaction states, and contrast pairs",
        )
    elif not COLOR_VALUE_RE.search(color):
        add(
            findings,
            "warning",
            "DESIGN_COLOR_VALUES_UNRESOLVED",
            "DESIGN.md",
            "Color-system section has no concrete HEX/RGB/HSL/OKLCH/Lab values; provisional values are required when brand inputs are missing",
        )

    if typography is None:
        add(
            findings,
            "warning",
            "DESIGN_TYPOGRAPHY_MISSING",
            "DESIGN.md",
            "Add a typography-system section with font stacks and component-relevant size, line-height, weight, and responsive rules",
        )
    else:
        unresolved: list[str] = []
        if not GENERIC_FONT_RE.search(typography):
            unresolved.append("a concrete font stack with a generic fallback")
        if not TYPE_SIZE_RE.search(typography):
            unresolved.append("type sizes in implementation units")
        if unresolved:
            add(
                findings,
                "warning",
                "DESIGN_TYPOGRAPHY_UNRESOLVED",
                "DESIGN.md",
                "Typography-system section is missing " + " and ".join(unresolved),
            )

    if ui_foundation is None:
        add(
            findings,
            "warning",
            "DESIGN_UI_FOUNDATION_MISSING",
            "DESIGN.md",
            "Add a UI-foundation section naming the selected component system, alternatives, theming/ownership, compatibility evidence, and component coverage",
        )
    elif not UI_FOUNDATION_STATE_RE.search(ui_foundation):
        add(
            findings,
            "warning",
            "DESIGN_UI_FOUNDATION_UNRESOLVED",
            "DESIGN.md",
            "UI-foundation choice must be confirmed, provisional, or explicitly not-applicable; an undecided library list is not implementation-ready",
        )

    if components is None:
        add(
            findings,
            "warning",
            "DESIGN_COMPONENT_SPECS_MISSING",
            "DESIGN.md",
            "Add component specifications mapping used components to typography, dimensions, visual tokens, and states",
        )
    else:
        unresolved = []
        if not GENERIC_FONT_RE.search(components):
            unresolved.append("a resolved font stack with a generic fallback")
        if not TYPE_SIZE_RE.search(components):
            unresolved.append("a resolved font size")
        if unresolved:
            add(
                findings,
                "warning",
                "DESIGN_COMPONENT_TYPE_UNRESOLVED",
                "DESIGN.md",
                "Component specifications are missing "
                + " and ".join(unresolved)
                + "; do not rely on an undocumented typography-token chain",
            )


def registered_tbd_ids(text: str) -> set[str]:
    registered: set[str] = set()
    for match in OPEN_HEADING_RE.finditer(text):
        registered.update(ID_RE["tbd"].findall(section_after(text, match)))
    return registered


def spec_blocks(text: str) -> Iterable[tuple[str, str]]:
    matches = list(SPEC_HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        yield match.group(1), text[match.end() : end]


def has_scenario_terms(block: str) -> bool:
    upper = block.upper()
    given = "GIVEN" in upper or "给定" in block or "假设" in block
    when = "WHEN" in upper or "当" in block
    then = "THEN" in upper or "那么" in block or "则" in block
    return given and when and then


def validate(project_root: Path) -> list[Finding]:
    root = project_root.resolve()
    findings: list[Finding] = []
    texts: dict[Path, str] = {}

    if not root.is_dir():
        return [Finding("error", "ROOT_NOT_FOUND", root.as_posix(), "Project root is not a directory")]

    for filename, expected_kind in REQUIRED_KINDS.items():
        path = root / filename
        if not path.is_file():
            add(findings, "error", "MISSING_ARTIFACT", filename, f"Required artifact is missing: {filename}")
            continue
        text = read_text(path)
        texts[path] = text
        actual_kind = parse_frontmatter(text).get("blueprint_kind")
        if actual_kind != expected_kind:
            add(
                findings,
                "error",
                "INVALID_KIND",
                filename,
                f"Expected blueprint_kind '{expected_kind}', found '{actual_kind or 'missing'}'",
            )

    for filename in REQUIRED_ADAPTERS:
        path = root / filename
        if not path.is_file():
            add(findings, "warning", "MISSING_ADAPTER", filename, f"Agent adapter is missing: {filename}")
        else:
            texts[path] = read_text(path)

    specs_dir = root / "specs"
    domain_files = sorted(specs_dir.glob("*.md")) if specs_dir.is_dir() else []
    domain_files = [path for path in domain_files if path.name.lower() != "readme.md"]
    if not domain_files:
        add(findings, "error", "MISSING_DOMAIN_SPEC", "specs/", "At least one domain spec is required")
    for path in domain_files:
        text = read_text(path)
        texts[path] = text
        actual_kind = parse_frontmatter(text).get("blueprint_kind")
        if actual_kind != "domain-spec":
            add(
                findings,
                "error",
                "INVALID_KIND",
                rel(path, root),
                f"Expected blueprint_kind 'domain-spec', found '{actual_kind or 'missing'}'",
            )

    # Include ADRs, but do not audit unrelated repository Markdown.
    for path in adr_files(root):
        texts.setdefault(path, read_text(path))

    prd_text = texts.get(root / "PRD.md", "")
    index_text = texts.get(root / "SPEC.md", "")
    defined_prd = set(
        re.findall(r"^#{2,4}\s+(PRD-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3})\b", prd_text, re.MULTILINE)
    )
    defined_specs: set[str] = set()

    for path in domain_files:
        text = texts[path]
        blocks = list(spec_blocks(text))
        if not blocks:
            add(findings, "error", "NO_SPEC_REQUIREMENT", rel(path, root), "Domain spec has no SPEC-* requirement heading")
        for spec_id, block in blocks:
            defined_specs.add(spec_id)
            sources = set(ID_RE["prd"].findall(block))
            if not sources:
                add(findings, "error", "SPEC_WITHOUT_SOURCE", rel(path, root), f"{spec_id} has no source PRD ID")
            for source in sorted(sources - defined_prd):
                add(findings, "error", "UNKNOWN_PRD_SOURCE", rel(path, root), f"{spec_id} references undefined {source}")
            if not has_scenario_terms(block):
                add(findings, "error", "MISSING_SCENARIO", rel(path, root), f"{spec_id} needs Given/When/Then behavior")
            if "acceptance" not in block.lower() and "验收" not in block:
                add(findings, "warning", "MISSING_ACCEPTANCE", rel(path, root), f"{spec_id} has no explicit acceptance method")

    for prd_id in sorted(defined_prd):
        if prd_id not in index_text:
            add(findings, "error", "UNTRACED_PRD", "SPEC.md", f"{prd_id} is not present in the traceability index")
    for spec_id in sorted(defined_specs):
        if spec_id not in index_text:
            add(findings, "error", "UNTRACED_SPEC", "SPEC.md", f"{spec_id} is not present in the traceability index")

    for gate in ("design-ready", "implementation-ready", "production-ready"):
        if gate not in index_text:
            add(findings, "error", "MISSING_GATE", "SPEC.md", f"Readiness ledger is missing {gate}")

    design_text = texts.get(root / "DESIGN.md")
    if design_text is not None:
        validate_design_contract(design_text, findings)

    all_tbd: set[str] = set()
    registered_tbd: set[str] = set()
    for text in texts.values():
        all_tbd.update(ID_RE["tbd"].findall(text))
        registered_tbd.update(registered_tbd_ids(text))
    for tbd_id in sorted(all_tbd - registered_tbd):
        add(findings, "error", "UNREGISTERED_TBD", ".", f"{tbd_id} is referenced but absent from an Open decisions table")

    for path, text in texts.items():
        for line_number, line in enumerate(text.splitlines(), start=1):
            if EMOJI_RE.search(line):
                add(
                    findings,
                    "warning",
                    "EMOJI_USAGE",
                    f"{rel(path, root)}:{line_number}",
                    "Emoji usage needs removal or a documented DESIGN.md exception with an accessible alternative",
                )
        for target in MARKDOWN_LINK_RE.findall(text):
            clean_target = target.strip().strip("<>").split("#", 1)[0]
            if not clean_target or clean_target.startswith(("http://", "https://", "mailto:")):
                continue
            if clean_target.startswith("/"):
                target_path = Path(clean_target)
            else:
                target_path = path.parent / clean_target
            if not target_path.exists():
                add(
                    findings,
                    "error",
                    "BROKEN_LINK",
                    rel(path, root),
                    f"Local link target does not exist: {target}",
                )

    if not defined_prd:
        add(findings, "warning", "NO_PRD_REQUIREMENT", "PRD.md", "No PRD-* requirement heading was found")

    return sorted(findings, key=lambda item: ({"error": 0, "warning": 1, "info": 2}.get(item.severity, 3), item.path, item.code))


def summary(findings: list[Finding]) -> dict[str, int]:
    counts = {"errors": 0, "warnings": 0, "info": 0}
    for finding in findings:
        key = {"error": "errors", "warning": "warnings", "info": "info"}.get(finding.severity)
        if key:
            counts[key] += 1
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path, help="Root containing blueprint documents")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    findings = validate(args.project_root)
    counts = summary(findings)
    if args.json:
        print(json.dumps({"summary": counts, "findings": [asdict(item) for item in findings]}, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"{item.severity.upper():7} {item.code:24} {item.path}: {item.message}")
        print(f"Blueprint validation: {counts['errors']} error(s), {counts['warnings']} warning(s)")
    return 1 if counts["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
