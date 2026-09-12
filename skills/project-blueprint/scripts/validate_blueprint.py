#!/usr/bin/env python3
"""Read-only structural validation for project-blueprint artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime
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


def record_field(section: str, *labels: str) -> str:
    """Read one explicit review field, not a status mentioned in surrounding prose."""
    pattern = r"^[ \t]*-[ \t]*(?:" + "|".join(re.escape(label) for label in labels) + r")[ \t]*[:：][ \t]*([^\n]*)$"
    match = re.search(pattern, section, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip().strip("`") if match else ""


def has_source_reference(section: str, document: str) -> bool:
    """Recognize a source link; resolve same-document heading anchors locally."""
    for target in MARKDOWN_LINK_RE.findall(section):
        target = target.strip().strip("<>")
        if not target:
            continue
        if not target.startswith("#"):
            # Local file existence is checked by validate(); remote content is not fetched.
            return True
        anchor = target[1:]
        for title in re.findall(r"^#{1,6}\s+(.+?)\s*$", document, re.MULTILINE):
            slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
            if anchor == slug:
                return True
    return False


def validate_design_contract(text: str, findings: list[Finding], index_text: str = "") -> None:
    metadata = parse_frontmatter(text)
    stage = metadata.get("design_stage")
    if stage is None:
        add(findings, "info", "LEGACY_DESIGN_STAGE", "DESIGN.md",
            "No design_stage: retaining legacy visual checks; migrate explicitly to the staged design workflow when revising this document")
        validate_visual_details(text, findings)
        return
    if stage not in {"direction", "prototype", "specification", "not-applicable"}:
        add(findings, "error", "DESIGN_STAGE_INVALID", "DESIGN.md",
            "design_stage must be direction, prototype, specification, or not-applicable")
        return

    ready = bool(re.search(r"^\s*\|\s*`?implementation-ready`?\s*\|\s*`?ready`?\s*\|", index_text, re.MULTILINE | re.IGNORECASE))
    start = len(findings)

    def require_section(terms: tuple[str, ...], code: str, message: str) -> str:
        section = h2_section_matching(text, terms)
        if not section or not section.strip():
            add(findings, "warning", code, "DESIGN.md", message)
        return section or ""

    if stage == "not-applicable":
        require_section(("applicability", "适用性"), "DESIGN_APPLICABILITY_MISSING",
                        "Explain why this project has no user-facing UI; retain observable behavior in SPEC")
    else:
        require_section(("visual direction", "视觉方向"), "DESIGN_DIRECTION_MISSING",
                        "Record the selected direction, reference characteristics, key customization and exploration space")
        if stage in {"prototype", "specification"}:
            if stage == "prototype":
                preview = require_section(("visual preview", "视觉预览", "prototype handoff", "样稿交接"), "DESIGN_HANDOFF_MISSING",
                                          "Describe the component/page preview, viewing instructions and review scope, or a concrete deferred handoff")
                artifact = record_field(preview, "Artifact", "预览产物")
                deferred = record_field(preview, "Deferred reason", "暂缓原因")
                if not has_source_reference(artifact, text) and not meaningful(deferred):
                    add(findings, "warning", "DESIGN_PREVIEW_DELIVERY_MISSING", "DESIGN.md",
                        "Link the viewable preview in Artifact / 预览产物, or record an actual Deferred reason / 暂缓原因 and next step")
            review = require_section(("visual review", "视觉评审"), "DESIGN_REVIEW_MISSING",
                                     "Record review status, evidence and findings; use pending when visual work has not been observed")
            status = record_field(review, "Review status", "评审状态")
            if status not in {"pending", "provisional", "confirmed"}:
                add(findings, "warning", "DESIGN_REVIEW_STATUS_INVALID", "DESIGN.md",
                    "Use an explicit Review status / 评审状态 field: pending, provisional or confirmed")
            if stage == "specification" and status != "confirmed":
                add(findings, "warning", "DESIGN_REVIEW_UNCONFIRMED", "DESIGN.md",
                    "Specification requires a confirmed visual review or applicable approved design-system evidence")
            if status == "confirmed":
                missing = []
                if not has_source_reference(record_field(review, "Evidence", "证据"), text):
                    missing.append("linked evidence")
                if not meaningful(record_field(review, "Reviewed revision", "评审版本")):
                    missing.append("reviewed revision or approved baseline")
                if not meaningful(record_field(review, "Confirmed scope", "确认范围")):
                    missing.append("confirmed scope")
                if not record_field(review, "Reviewer", "评审人"):
                    missing.append("reviewer")
                reviewed_on = record_field(review, "Reviewed on", "评审日期")
                try:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_on):
                        raise ValueError
                    date.fromisoformat(reviewed_on)
                except ValueError:
                    missing.append("review date (YYYY-MM-DD)")
                if not record_field(review, "Findings and adjustments", "结论与调整"):
                    missing.append("findings and adjustments")
                if missing:
                    add(findings, "warning", "DESIGN_REVIEW_EVIDENCE_INCOMPLETE", "DESIGN.md",
                        "Confirmed review is missing " + ", ".join(missing))
        if stage == "specification":
            source = require_section(("token source", "token 来源", "token来源"), "DESIGN_TOKEN_SOURCE_MISSING",
                                     "Link the authoritative theme/config/design system or an inline token section")
            if source and not has_source_reference(source, text):
                add(findings, "warning", "DESIGN_TOKEN_SOURCE_UNRESOLVED", "DESIGN.md",
                    "Token source needs a source link or a valid inline heading anchor")
            validate_visual_details(text, findings, allow_sources=True)

    if ready and (stage in {"direction", "prototype"} or any(item.severity in {"warning", "error"} for item in findings[start:])):
        add(findings, "error", "DESIGN_READINESS_CONFLICT", "SPEC.md",
            "implementation-ready is ready but design is exploratory or has unresolved specification evidence; prototype exploration may continue while the overall gate is blocked")


def validate_visual_details(text: str, findings: list[Finding], *, allow_sources: bool = False) -> None:
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
    elif not COLOR_VALUE_RE.search(color) and not (allow_sources and has_source_reference(color, text)):
        add(
            findings,
            "warning",
            "DESIGN_COLOR_VALUES_UNRESOLVED",
            "DESIGN.md",
            "Color-system section needs concrete values or, for staged specifications, a link to the maintained palette",
        )

    if typography is None:
        add(
            findings,
            "warning",
            "DESIGN_TYPOGRAPHY_MISSING",
            "DESIGN.md",
            "Add a typography-system section with font stacks and component-relevant size, line-height, weight, and responsive rules",
        )
    elif not (allow_sources and has_source_reference(typography, text)):
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
    elif allow_sources:
        if not components.strip():
            add(findings, "warning", "DESIGN_COMPONENT_SPECS_MISSING", "DESIGN.md",
                "Map used components to documented tokens or foundation variants, with applicable deltas and states")
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


SPEC_ID_PATTERN = r"(?:PRD|SPEC|AC|IFACE|TASK)-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}"
SPEC_ID_RE = re.compile(r"\b" + SPEC_ID_PATTERN + r"\b")
SPEC_NODE_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
DECISION_STATES = {"confirmed", "provisional", "pending", "not-applicable"}
EXECUTION_RESULTS = {"not-run", "passed", "failed", "blocked"}
SPEC_KINDS = {"domain-spec", "interface-spec", "task-spec"}


@dataclass(frozen=True)
class SpecNode:
    identifier: str
    body: str
    path: Path
    parent: str | None = None
    level: int = 2

    def field(self, label: str) -> str:
        return record_field(self.body, label)


def meaningful(value: str) -> bool:
    """Reject empty/template values; semantic sufficiency still needs review."""
    return bool(value.strip()) and not (
        re.fullmatch(r"\[[^\n]*\]", value.strip())
        or re.fullmatch(r"(?:TBD(?:-[\w-]+)?|pending|unknown|-)", value.strip(), re.IGNORECASE)
    )


def has_ac_scenario(body: str) -> bool:
    """Require explicit nonempty scenario clauses, not words in a test-plan paragraph."""
    for terms in (("GIVEN", "给定", "假设"), ("WHEN", "当"), ("THEN", "那么", "则")):
        labels = "|".join(terms)
        pattern = r"^[ \t]*-[ \t]*(?:\*\*)?(?:" + labels + r")(?:\*\*)?[ \t:：]+([^\n]+)$"
        matches = re.findall(pattern, body, re.MULTILINE | re.IGNORECASE)
        if not any(meaningful(value.strip()) for value in matches):
            return False
    return True


def identifiers(value: str, prefix: str) -> set[str]:
    return {item for item in SPEC_ID_RE.findall(value) if item.startswith(prefix + "-")}


def spec_nodes(path: Path, text: str) -> list[SpecNode]:
    # Example definitions in fenced code are not authoritative definitions.
    text = re.sub(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$", "", text, flags=re.MULTILINE | re.DOTALL)
    headings = list(SPEC_NODE_HEADING_RE.finditer(text))
    parent = None
    nodes = []
    for index, heading in enumerate(headings):
        level = len(heading.group(1))
        match = re.match(r"(" + SPEC_ID_PATTERN + r")(?:\s|$)", heading.group(2))
        if level <= 2:
            parent = None
        if not match:
            continue
        identifier = match.group(1)
        if identifier.startswith("SPEC-") and level == 2:
            parent = identifier
        end = len(text)
        for following in headings[index + 1:]:
            if len(following.group(1)) <= level or re.match(SPEC_ID_PATTERN + r"(?:\s|$)", following.group(2)):
                end = following.start()
                break
        nodes.append(SpecNode(identifier, text[heading.end():end], path,
                              parent if identifier.startswith("AC-") and level == 3 else None, level))
    return nodes


def validate_spec_v2(root: Path, texts: dict[Path, str], index_text: str,
                     findings: list[Finding]) -> None:
    """Structural graph/coverage validation. Never execute document commands."""
    start = len(findings)
    metadata = parse_frontmatter(index_text)
    nodes: dict[str, SpecNode] = {}
    expected = {"prd": {"PRD"}, "domain-spec": {"SPEC", "AC"},
                "interface-spec": {"IFACE"}, "task-spec": {"TASK"}}

    def report(code: str, node: SpecNode | None, message: str, severity: str = "error") -> None:
        add(findings, severity, code, rel(node.path, root) if node else "SPEC.md",
            (node.identifier + ": " if node else "") + message)

    for path, text in texts.items():
        kind = parse_frontmatter(text).get("blueprint_kind")
        if kind not in expected:
            continue
        parsed = spec_nodes(path, text)
        if kind == "task-spec" and len([n for n in parsed if n.identifier.startswith("TASK-")]) != 1:
            add(findings, "error", "TASK_FILE_CARDINALITY", rel(path, root), "Each task-spec file must define exactly one TASK")
        if kind in SPEC_KINDS and not parsed:
            add(findings, "error", "SPEC_DEFINITION_MISSING", rel(path, root), "Typed spec file contains no identifier heading")
        for node in parsed:
            expected_level = 3 if node.identifier.startswith("AC-") else 2
            if kind != "prd" and node.level != expected_level:
                report("SPEC_HEADING_LEVEL", node, f"Use an H{expected_level} definition heading")
            if node.identifier.split("-", 1)[0] not in expected[kind]:
                report("SPEC_DEFINITION_KIND", node, f"Definition does not belong in {kind}")
            if node.identifier in nodes:
                report("DUPLICATE_SPEC_ID", node, f"Already defined in {rel(nodes[node.identifier].path, root)}")
            else:
                nodes[node.identifier] = node

    def refs(value: str, prefix: str, node: SpecNode | None, field: str,
             allow_none: bool = False, required: bool = True) -> set[str]:
        result = identifiers(value, prefix)
        if value.strip() == "none" and allow_none:
            return set()
        if not result and required:
            report("SPEC_REFERENCE_MISSING", node, f"{field} needs {prefix} IDs" + (" or none" if allow_none else ""))
        for identifier in result:
            if identifier not in nodes:
                report("SPEC_REFERENCE_UNKNOWN", node, f"{field} references undefined {identifier}")
        # Field syntax is deliberately simple: comma-separated IDs, not prose/arrays.
        if value and any(not re.fullmatch(prefix + r"-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d{3}", part.strip())
                         for part in value.split(",")):
            report("SPEC_REFERENCE_INVALID", node, f"{field} must contain comma-separated {prefix} IDs" + (" or none" if allow_none else ""))
        return result

    current_specs = refs(metadata.get("current_specs", ""), "SPEC", None, "current_specs", True)
    current_tasks = refs(metadata.get("current_tasks", ""), "TASK", None, "current_tasks", True)
    if not meaningful(metadata.get("delivery_scope", "")) or metadata.get("delivery_scope", "").lower() == "none":
        report("DELIVERY_SCOPE_MISSING", None, "Name the current delivery scope, separately from the entire MVP", "warning")

    def require(node: SpecNode, fields: tuple[str, ...]) -> None:
        for field in fields:
            if not meaningful(node.field(field)):
                report("SPEC_FIELD_MISSING", node, f"Resolve {field} before claiming readiness", "warning")

    def execution(node: SpecNode, label: str, required: bool) -> None:
        result = node.field(label)
        if not result and not required:
            return
        if result not in EXECUTION_RESULTS:
            report("SPEC_RESULT_INVALID", node, f"{label} must be not-run, passed, failed or blocked", "warning")
        if result == "passed":
            evidence = node.field("Evidence")
            if not has_source_reference(evidence, texts[node.path]):
                report("SPEC_PASS_WITHOUT_EVIDENCE", node, "A passing claim needs actual linked evidence")
            if not meaningful(node.field("Tested revision")):
                report("SPEC_PASS_WITHOUT_REVISION", node, "A passing claim needs the actual tested revision")
            executed = node.field("Executed on")
            try:
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", executed):
                    date.fromisoformat(executed)
                elif re.match(r"\d{4}-\d{2}-\d{2}T", executed):
                    datetime.fromisoformat(executed.replace("Z", "+00:00"))
                else:
                    raise ValueError
            except ValueError:
                report("SPEC_PASS_WITHOUT_DATE", node, "A passing claim needs a valid ISO execution date/time")

    sources: dict[str, set[str]] = {}
    task_acs: dict[str, set[str]] = {}
    task_interfaces: dict[str, set[str]] = {}
    dependencies: dict[str, set[str]] = {}
    ac_by_spec: dict[str, set[str]] = {}
    for identifier, node in nodes.items():
        prefix = identifier.split("-", 1)[0]
        if prefix == "PRD":
            continue
        indexed = False
        index_body = FRONTMATTER_RE.sub("", index_text, count=1)
        for line in index_body.splitlines():
            if identifier not in SPEC_ID_RE.findall(line):
                continue
            for target in MARKDOWN_LINK_RE.findall(line):
                clean = target.strip().strip("<>").split("#", 1)[0]
                if clean and not re.match(r"https?://", clean) and (root / clean).resolve() == node.path.resolve():
                    indexed = True
        if not indexed:
            report("SPEC_INDEX_MISSING", node, "Add this definition ID and a link to its source file in the root index")
        if node.field("Superseded by"):
            replacements = refs(node.field("Superseded by"), prefix, node, "Superseded by")
            if identifier in replacements:
                report("SPEC_SUPERSESSION_INVALID", node, "A definition cannot replace itself")
            if identifier in current_specs or identifier in current_tasks:
                report("CURRENT_SPEC_SUPERSEDED", node, "Select the replacement instead of a retired definition", "warning")
        if prefix in {"SPEC", "IFACE", "TASK"} and node.field("State") and node.field("State") not in DECISION_STATES:
            report("SPEC_STATE_INVALID", node, "Use confirmed, provisional, pending or not-applicable", "warning")
        if (identifier in current_specs or identifier in current_tasks or node.parent in current_specs) and ID_RE["tbd"].search(node.body):
            report("CURRENT_SPEC_PENDING", node, "Current contract still references a pending decision", "warning")
        if prefix in {"SPEC", "IFACE", "TASK"}:
            sources[identifier] = refs(node.field("Source"), "PRD" if prefix == "SPEC" else "SPEC", node, "Source")
        if prefix == "AC":
            if node.parent is None or node.parent not in nodes:
                report("AC_PARENT_MISSING", node, "Define each AC as an H3 under its owning H2 functional SPEC")
            elif not node.field("Superseded by"):
                ac_by_spec.setdefault(node.parent, set()).add(identifier)
            if node.parent in current_specs and not node.field("Superseded by"):
                require(node, ("Fixture", "Assertion", "Procedure", "Evidence required"))
                if not has_ac_scenario(node.body):
                    report("AC_SCENARIO_MISSING", node, "AC needs its own Given/When/Then scenario", "warning")
                if node.field("Verification") not in {"automated", "manual", "hybrid"}:
                    report("AC_VERIFICATION_INVALID", node, "Choose automated, manual or hybrid verification", "warning")
                if node.field("Verification") in {"manual", "hybrid"}:
                    require(node, ("Acceptance owner",))
            execution(node, "Result", node.parent in current_specs and not node.field("Superseded by"))
        if prefix == "SPEC" and identifier in current_specs:
            require(node, ("Actors", "Trigger", "Preconditions", "Inputs", "Rules", "Outcome"))
            if node.field("State") != "confirmed":
                report("CURRENT_SPEC_UNCONFIRMED", node, "Current behavior needs confirmation before implementation", "warning")
        if prefix == "TASK":
            require(node, ("Goal", "Risk", "Refine when"))
            dependencies[identifier] = refs(node.field("Depends on"), "TASK", node, "Depends on", True)
            if identifier in current_tasks or node.field("AC"):
                task_acs[identifier] = refs(node.field("AC"), "AC", node, "AC")
            if identifier in current_tasks or node.field("Interfaces"):
                task_interfaces[identifier] = refs(node.field("Interfaces"), "IFACE", node, "Interfaces", True)
            if identifier in current_tasks:
                require(node, ("Non-goals", "Change scope", "Constraints", "Test plan", "Done when"))
                if node.field("State") != "confirmed":
                    report("CURRENT_TASK_UNCONFIRMED", node, "Current task needs confirmation before implementation", "warning")
                if node.field("Readiness") not in {"ready", "blocked"}:
                    report("TASK_READINESS_INVALID", node, "Use ready or blocked", "warning")
                if not sources[identifier] <= current_specs:
                    report("TASK_OUTSIDE_DELIVERY", node, "Current task source specs must be in current_specs")
            execution(node, "Completion", identifier in current_tasks)

    for identifier in current_specs:
        if identifier in nodes and not ac_by_spec.get(identifier):
            report("CURRENT_SPEC_WITHOUT_AC", nodes[identifier], "Current capability needs independently identified AC", "warning")
    current_acs = set().union(*(ac_by_spec.get(key, set()) for key in current_specs))
    covered = set().union(*(task_acs.get(key, set()) for key in current_tasks))
    for ac in sorted(current_acs - covered):
        report("CURRENT_AC_UNCOVERED", nodes[ac], "No current task implements or enables this AC", "warning")
    for task, acs in task_acs.items():
        for ac in acs:
            if ac in nodes and nodes[ac].field("Superseded by") and task in current_tasks:
                report("CURRENT_SPEC_SUPERSEDED", nodes[task], f"Use the replacement of retired AC {ac}", "warning")
            if ac in nodes and nodes[ac].parent not in sources.get(task, set()):
                report("TASK_AC_SOURCE_MISMATCH", nodes[task], f"{ac} does not belong to this task's Source specs")
    for task, ifaces in task_interfaces.items():
        for iface in ifaces:
            if iface in nodes and not sources.get(iface, set()) & sources.get(task, set()):
                report("TASK_INTERFACE_SOURCE_MISMATCH", nodes[task], f"{iface} has no shared source behavior")

    current_ifaces = set().union(*(task_interfaces.get(key, set()) for key in current_tasks))
    # Interfaces for current behavior cannot evade validation by being omitted from a task.
    current_ifaces.update(key for key in nodes if key.startswith("IFACE-") and not nodes[key].field("Superseded by") and sources.get(key, set()) & current_specs)
    for identifier, node in nodes.items():
        if not identifier.startswith("IFACE-"):
            continue
        is_current = identifier in current_ifaces
        if is_current:
            require(node, ("Provider", "Consumer", "Protocol", "Operations", "Auth", "Errors", "Compatibility", "Contract checks"))
            if node.field("Superseded by"):
                report("CURRENT_SPEC_SUPERSEDED", node, "Current behavior still uses a retired interface", "warning")
            if node.field("State") != "confirmed":
                report("CURRENT_INTERFACE_UNCONFIRMED", node, "Current interface needs confirmation", "warning")
        contract = node.field("Contract")
        in_process = node.field("Protocol").lower() in {"in-process", "internal"}
        exemption = bool(re.fullmatch(r"not-applicable:\s*\S.*", contract)) and in_process
        targets = MARKDOWN_LINK_RE.findall(contract)
        if is_current and not targets and not exemption:
            report("INTERFACE_CONTRACT_MISSING", node, "Link a machine contract, or explain an in-process non-applicability", "warning")
        for target in targets:
            clean = target.strip().strip("<>").split("#", 1)[0]
            if not clean:
                report("INTERFACE_CONTRACT_MISSING", node, "Contract must point to a machine artifact, not an inline prose anchor", "warning")
                continue
            if re.match(r"https?://", clean):
                continue
            path = (node.path.parent / clean).resolve()
            if path.suffix.lower() not in {".json", ".yaml", ".yml", ".proto"}:
                report("INTERFACE_CONTRACT_FORMAT", node, "Local machine contracts must use JSON, YAML or protobuf source", "warning")
            if path.is_file() and path.suffix.lower() == ".json":
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except (ValueError, UnicodeError):
                    report("CONTRACT_JSON_INVALID", node, f"Invalid JSON source: {clean}")
        execution(node, "Result", is_current and not exemption)

    # Iterative topological traversal avoids recursion limits on larger task graphs.
    indegree = {key: 0 for key in dependencies}
    dependents: dict[str, list[str]] = {key: [] for key in dependencies}
    for task, prereqs in dependencies.items():
        for prerequisite in prereqs:
            if prerequisite in indegree:
                indegree[task] += 1
                dependents[prerequisite].append(task)
        if task in current_tasks:
            for prerequisite in prereqs - current_tasks:
                if prerequisite in nodes and nodes[prerequisite].field("Completion") != "passed":
                    report("TASK_DEPENDENCY_OUTSIDE_SCOPE", nodes[task], f"Include unfinished dependency {prerequisite} in current_tasks", "warning")
    queue = [key for key, degree in indegree.items() if degree == 0]
    for key in queue:
        for dependent in dependents[key]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)
    if len(queue) != len(indegree):
        report("TASK_DEPENDENCY_CYCLE", None, "Task graph has a cycle; unresolved nodes: " + ", ".join(sorted(key for key, degree in indegree.items() if degree)))

    for task in current_tasks & nodes.keys():
        node = nodes[task]
        relevant = {task} | sources.get(task, set()) | task_acs.get(task, set()) | task_interfaces.get(task, set()) | dependencies.get(task, set())
        relevant.update(key for key in current_ifaces if sources.get(key, set()) & sources.get(task, set()))
        issues = [item for item in findings[start:] if item.severity in {"error", "warning"}
                  and (any(item.message.startswith(key + ":") for key in relevant) or item.code == "TASK_DEPENDENCY_CYCLE")]
        if node.field("Readiness") == "ready" and issues:
            report("TASK_READY_WITH_GAPS", node, "Task claims ready with unresolved source, AC, contract or dependency findings")
    implementation_ready = bool(re.search(r"^\s*\|\s*`?implementation-ready`?\s*\|\s*`?ready`?\s*\|", index_text, re.MULTILINE | re.IGNORECASE))
    if implementation_ready and (
        not current_specs or not current_tasks
        or any(nodes[key].field("Readiness") != "ready" for key in current_tasks & nodes.keys())
        or any(item.severity in {"error", "warning"} for item in findings[start:])
    ):
        report("SPEC_READINESS_CONFLICT", None, "implementation-ready requires a named nonempty current scope, covered AC and ready current task contracts; execution may still be not-run")


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

    index_text = texts.get(root / "SPEC.md", "")
    schema = parse_frontmatter(index_text).get("spec_schema")
    if schema is None:
        add(findings, "info", "LEGACY_SPEC_SCHEMA", "SPEC.md",
            "No spec_schema: retaining legacy checks; migrate explicitly to spec_schema: 2 for AC/interface/task validation")
    elif schema != "2":
        add(findings, "error", "SPEC_SCHEMA_INVALID", "SPEC.md", "Supported spec_schema is 2; absence selects legacy behavior")

    specs_dir = root / "specs"
    candidates = sorted(specs_dir.rglob("*.md") if schema == "2" else specs_dir.glob("*.md")) if specs_dir.is_dir() else []
    domain_files = []
    for path in candidates:
        text = read_text(path)
        actual_kind = parse_frontmatter(text).get("blueprint_kind")
        if path.name.lower() in {"readme.md", "index.md"} and actual_kind is None:
            continue
        texts[path] = text
        if schema == "2":
            if actual_kind not in SPEC_KINDS:
                add(findings, "error", "INVALID_KIND", rel(path, root),
                    f"Expected domain-spec, interface-spec or task-spec, found '{actual_kind or 'missing'}'")
            if actual_kind == "domain-spec":
                domain_files.append(path)
        else:
            domain_files.append(path)
            if actual_kind != "domain-spec":
                add(findings, "error", "INVALID_KIND", rel(path, root),
                    f"Expected blueprint_kind 'domain-spec', found '{actual_kind or 'missing'}'")
    if not domain_files:
        add(findings, "error", "MISSING_DOMAIN_SPEC", "specs/", "At least one domain spec is required")

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
        if schema == "2":
            continue
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

    if schema == "2":
        validate_spec_v2(root, texts, index_text, findings)

    design_text = texts.get(root / "DESIGN.md")
    if design_text is not None:
        validate_design_contract(design_text, findings, index_text)

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
