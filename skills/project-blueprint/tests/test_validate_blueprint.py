from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_blueprint.py"
SPEC = importlib.util.spec_from_file_location("validate_blueprint", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


KINDS = {
    "PRD.md": "prd",
    "SPEC.md": "spec-index",
    "DESIGN.md": "design",
    "ARCHITECTURE.md": "architecture",
    "SECURITY.md": "security",
    "DEPLOY.md": "deploy",
    "ENGINEERING.md": "engineering",
}


def document(kind: str, body: str = "# Document\n") -> str:
    return f"---\nblueprint_kind: {kind}\nblueprint_status: confirmed\nowner: team\nlast_reviewed: 2026-09-10\n---\n\n{body}"


def build_valid_blueprint(root: Path) -> None:
    for name, kind in KINDS.items():
        body = "# Document\n"
        if name == "PRD.md":
            body += "\n## PRD-CORE-001 — Core behavior\n\nConfirmed requirement.\n"
        elif name == "SPEC.md":
            body += (
                "\n## Traceability\n\nPRD-CORE-001 | SPEC-CORE-001\n"
                "\n## Readiness ledger\n\ndesign-ready\nimplementation-ready\nproduction-ready\n"
            )
        root.joinpath(name).write_text(document(kind, body), encoding="utf-8")
    root.joinpath("CLAUDE.md").write_text("# Claude\n", encoding="utf-8")
    root.joinpath("AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    specs = root / "specs"
    specs.mkdir()
    specs.joinpath("core.md").write_text(
        document(
            "domain-spec",
            "# Core\n\n## SPEC-CORE-001 — Core behavior\n\n"
            "- Source: PRD-CORE-001\n- Acceptance method: automated test\n\n"
            "### Scenario\n\n- GIVEN a valid state\n- WHEN the user acts\n- THEN the result is visible\n",
        ),
        encoding="utf-8",
    )


class ValidateBlueprintTests(unittest.TestCase):
    def test_complete_blueprint_has_no_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            findings = MODULE.validate(root)
            self.assertEqual([], [item for item in findings if item.severity == "error"])

    def test_missing_artifacts_and_domain_spec_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            findings = MODULE.validate(Path(directory))
            codes = {item.code for item in findings}
            self.assertIn("MISSING_ARTIFACT", codes)
            self.assertIn("MISSING_DOMAIN_SPEC", codes)

    def test_untraced_and_unverifiable_spec_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            root.joinpath("SPEC.md").write_text(
                document("spec-index", "# Index\n\ndesign-ready\nimplementation-ready\nproduction-ready\n"),
                encoding="utf-8",
            )
            root.joinpath("specs/core.md").write_text(
                document("domain-spec", "# Core\n\n## SPEC-CORE-001 — Core\n\nSource: PRD-MISSING-001\n"),
                encoding="utf-8",
            )
            codes = {item.code for item in MODULE.validate(root)}
            self.assertIn("UNKNOWN_PRD_SOURCE", codes)
            self.assertIn("MISSING_SCENARIO", codes)
            self.assertIn("UNTRACED_PRD", codes)
            self.assertIn("UNTRACED_SPEC", codes)

    def test_broken_links_and_unregistered_tbd_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            root.joinpath("DESIGN.md").write_text(
                document("design", "# Design\n\n[Missing](does-not-exist.md)\n\nTBD-DESIGN-999\n"),
                encoding="utf-8",
            )
            codes = {item.code for item in MODULE.validate(root)}
            self.assertIn("BROKEN_LINK", codes)
            self.assertIn("UNREGISTERED_TBD", codes)

    def test_unrelated_repository_markdown_is_out_of_scope(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            docs = root / "docs"
            docs.mkdir()
            docs.joinpath("unrelated.md").write_text(
                "# Existing docs\n\n[Legacy missing link](old-file.md)\nTBD-LEGACY-999\n",
                encoding="utf-8",
            )
            findings = MODULE.validate(root)
            self.assertEqual([], [item for item in findings if item.severity == "error"])

    def test_emoji_usage_is_reported_as_a_line_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            emojis = ("\U0001f680", "\U0001f4a1", "\u2705")
            root.joinpath("DESIGN.md").write_text(
                document(
                    "design",
                    "# Design\n\n" + "\n".join(f"## {emoji} Decorative heading" for emoji in emojis) + "\n",
                ),
                encoding="utf-8",
            )
            findings = [item for item in MODULE.validate(root) if item.code == "EMOJI_USAGE"]
            self.assertEqual(3, len(findings))
            for finding in findings:
                self.assertEqual("warning", finding.severity)
                self.assertRegex(finding.path, r"DESIGN\.md:\d+")

    def test_common_blueprint_symbols_are_not_treated_as_emoji(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            root.joinpath("DESIGN.md").write_text(
                document("design", "# Design\n\nDraft -> review → approved; latency <= 2s; target ≥ 95%.\n"),
                encoding="utf-8",
            )
            codes = {item.code for item in MODULE.validate(root)}
            self.assertNotIn("EMOJI_USAGE", codes)

    def test_missing_design_system_constraints_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            root.joinpath("DESIGN.md").write_text(
                document("design", "# Design\n\nUse brand colors and system fonts.\n"),
                encoding="utf-8",
            )
            codes = {item.code for item in MODULE.validate(root)}
            self.assertIn("DESIGN_COLOR_SYSTEM_MISSING", codes)
            self.assertIn("DESIGN_LAYOUT_MISSING", codes)
            self.assertIn("DESIGN_TYPOGRAPHY_MISSING", codes)
            self.assertIn("DESIGN_UI_FOUNDATION_MISSING", codes)
            self.assertIn("DESIGN_COMPONENT_SPECS_MISSING", codes)

    def test_unresolved_design_values_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            root.joinpath("DESIGN.md").write_text(
                document(
                    "design",
                    "# Design\n\n"
                    "## Application shell and layout\n\nCandidates: sidebar or header.\n\n"
                    "## Color system\n\nUse semantic brand colors.\n\n"
                    "## Typography system\n\nUse the chosen brand font.\n\n"
                    "## UI foundation and component sourcing\n\nUse PrimeVue.\n\n"
                    "## Component specifications\n\nButtons use the action token.\n",
                ),
                encoding="utf-8",
            )
            codes = {item.code for item in MODULE.validate(root)}
            self.assertIn("DESIGN_COLOR_VALUES_UNRESOLVED", codes)
            self.assertIn("DESIGN_LAYOUT_UNRESOLVED", codes)
            self.assertIn("DESIGN_TYPOGRAPHY_UNRESOLVED", codes)
            self.assertIn("DESIGN_COMPONENT_TYPE_UNRESOLVED", codes)

    def test_concrete_design_system_satisfies_visual_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            root.joinpath("DESIGN.md").write_text(
                document(
                    "design",
                    "# Design\n\n"
                    "## Application shell and layout\n\n"
                    "State: provisional. Recommend enterprise-workspace with side navigation and a list-detail approval surface; compact windows use a drawer and dedicated detail screen. SSO remains platform chrome.\n\n"
                    "## Color system\n\n"
                    "Canvas `#FFFFFF`; primary text `#17202A`; focus `#1457D9`.\n\n"
                    "## Typography system\n\n"
                    "Font stack: Inter, 'Noto Sans SC', system-ui, sans-serif. Body is 1rem/24px.\n\n"
                    "## UI foundation and component sourcing\n\n"
                    "State: provisional. Vue client uses PrimeVue styled mode; shadcn-vue was rejected because the small team needs broader ready-made coverage.\n\n"
                    "## Component specifications\n\n"
                    "Button labels use Inter, system-ui, sans-serif at 0.875rem/20px, weight 600, in every state.\n",
                ),
                encoding="utf-8",
            )
            design_codes = {
                item.code for item in MODULE.validate(root) if item.code.startswith("DESIGN_")
            }
            self.assertEqual(set(), design_codes)

    def test_missing_ui_foundation_is_reported_independently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            root.joinpath("DESIGN.md").write_text(
                document(
                    "design",
                    "# Design\n\n"
                    "## Color system\n\nCanvas `#FFFFFF`; text `#17202A`.\n\n"
                    "## Typography system\n\nFont stack: Inter, system-ui, sans-serif; body 1rem/24px.\n\n"
                    "## Component specifications\n\nButton: Inter, system-ui, sans-serif at 0.875rem/20px.\n",
                ),
                encoding="utf-8",
            )
            codes = {item.code for item in MODULE.validate(root)}
            self.assertIn("DESIGN_UI_FOUNDATION_MISSING", codes)

    def test_undecided_ui_library_list_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_blueprint(root)
            root.joinpath("DESIGN.md").write_text(
                document(
                    "design",
                    "# Design\n\n"
                    "## UI foundation and component sourcing\n\nCandidates: PrimeVue or shadcn-vue.\n",
                ),
                encoding="utf-8",
            )
            codes = {item.code for item in MODULE.validate(root)}
            self.assertIn("DESIGN_UI_FOUNDATION_UNRESOLVED", codes)


if __name__ == "__main__":
    unittest.main()
