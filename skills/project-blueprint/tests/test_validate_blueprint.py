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


if __name__ == "__main__":
    unittest.main()
