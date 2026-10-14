from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_validate_blueprint import MODULE, build_valid_blueprint, document


TEMPLATES = Path(__file__).parents[1] / "assets/templates"
CLI = os.environ.get("BLUEPRINT_OPENSPEC_CLI") or shutil.which("openspec")


class OpenSpecTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        build_valid_blueprint(self.root)
        self.root.joinpath("specs/core.md").unlink()
        self.change = self.root / "openspec/changes/add-core-action"
        self.delta = self.change / "specs/core-action/spec.md"
        self.delta.parent.mkdir(parents=True)
        self.root.joinpath("openspec/specs").mkdir()
        shutil.copyfile(TEMPLATES / "OPENSPEC_CONFIG.yaml", self.root / "openspec/config.yaml")
        replacements = {
            "[change-name]": "add-core-action",
            "[Problem and why this delivery matters. Link the source product requirements.]": "Deliver the confirmed reservation slice from [PRD](../../../PRD.md).",
            "[Observable additions, modifications or removals; mark breaking changes explicitly.]": "Add reservation creation and safe conflict handling.",
            "[cohesive behavior; exact relative capability path]": "Member reservation behavior",
            "[Existing capability paths whose behavior changes, or none. Do not invent paths.]": "None.",
            "[Affected clients, APIs, data, dependencies, security, deployment and existing project documents.]": "Reservation API and storage; see [architecture](../../../ARCHITECTURE.md).",
            "[New capability only: explain its cohesive behavior and user/system boundary in at least 50 characters. Remove this section when changing an existing capability.]": "Allow signed-in members to reserve available slots and observe conflict results without creating duplicate or excess reservations.",
            "[observable capability]": "Reserve an available slot",
            "[observable behavior and applicable business invariants]": "create exactly one reservation for an available slot and reject conflicting requests",
            "[successful outcome]": "Successful reservation",
            "[relevant failure or boundary]": "Reservation conflict",
            "[observable starting state and relevant data]": "a signed-in member and an available slot",
            "[actor action or event]": "the member reserves the slot",
            "[decidable visible result and state/data effects]": "one reservation appears in that member's list",
            "[failure/boundary/permission condition]": "an already reserved slot",
            "[action]": "the member requests that slot",
            "[safe observable result and retained/changed state]": "a conflict is reported and no second reservation exists",
            "[planned command or reproducible steps]": "run the reservation integration check",
            "[report/response/manual approval]": "integration report and observed stored record",
            "[responsible reviewer]": "product owner",
            "[reproducible checks and human judgment]": "run conflict checks and review the observable error",
            "[test report and reviewer record]": "integration report and product review",
            "[Independently reviewable outcome]": "Reservation slice",
            "[implement or enable the outcome for SPEC-CORE-001 / AC-CORE-001]": "Deliver SPEC-CORE-001 and verify AC-CORE-001",
            "[requirement/scenario links in specs/<capability>/spec.md]": "[reservation behavior](specs/core-action/spec.md)",
            "[allowed modules/boundaries; exclude unrelated work]": "reservation API and storage; exclude payments",
            "[design.md, root architecture/security and canonical contracts]": "[technical design](design.md) and [architecture](../../../ARCHITECTURE.md)",
            "[test command or reproducible manual checks and required evidence]": "run reservation integration checks and retain their report",
            "[cover AC-CORE-002 failure/boundary and its verification]": "Verify AC-CORE-002 conflict handling",
            "[checks that demonstrate the referenced scenario]": "run the conflict integration check and product review",
        }
        for source, target in (("PROPOSAL.md", "proposal.md"), ("DELTA_SPEC.md", "specs/core-action/spec.md"), ("TASK_SPEC.md", "tasks.md")):
            text = TEMPLATES.joinpath(source).read_text()
            for before, after in replacements.items():
                text = text.replace(before, after)
            text = text.replace("- State: pending", "- State: confirmed")
            if source == "PROPOSAL.md":
                text = text[:text.index("## Open decisions")]
            self.change.joinpath(target).write_text(text)
        self.change.joinpath("design.md").write_text("# Design\n\n## Context\n\nSee [architecture](../../../ARCHITECTURE.md).\n\n## Goals / Non-Goals\n\nPreserve slot uniqueness; exclude payments.\n\n## Decisions\n\nUse the confirmed relational transaction boundary.\n\n## Risks / Trade-offs\n\nConcurrent reservations require conflict verification.\n")
        self.root.joinpath("DESIGN.md").write_text(document("design", "## Applicability\n\nAPI-only delivery without user-facing UI.\n").replace("blueprint_kind: design", "blueprint_kind: design\ndesign_stage: not-applicable"))
        self.index()

    def index(self, current="add-core-action", ready="ready") -> None:
        text = document("spec-index", """# Delivery

## Traceability

PRD-CORE-001 | SPEC-CORE-001 | AC-CORE-001, AC-CORE-002
[proposal](openspec/changes/add-core-action/proposal.md)
[behavior](openspec/changes/add-core-action/specs/core-action/spec.md)
[tasks](openspec/changes/add-core-action/tasks.md)

## Readiness ledger

| Gate | Status |
|---|---|
| design-ready | ready |
| implementation-ready | READY |
| production-ready | blocked |
""").replace("READY", ready)
        text = text.replace("blueprint_kind: spec-index", f"blueprint_kind: spec-index\nspec_framework: openspec\ndelivery_scope: first-reservation\ncurrent_changes: {current}")
        self.root.joinpath("SPEC.md").write_text(text)

    def codes(self):
        return {item.code for item in MODULE.validate(self.root) if item.severity != "info"}

    def replace(self, path: Path, before: str, after: str) -> None:
        text = path.read_text()
        self.assertIn(before, text)
        path.write_text(text.replace(before, after))

    def test_greenfield_change_is_ready_without_an_implemented_baseline(self):
        self.assertEqual(set(), self.codes())
        self.assertEqual([], list(self.root.joinpath("openspec/specs").rglob("*.md")))
        self.assertIn("OPENSPEC_NATIVE_VALIDATION_REQUIRED", {item.code for item in MODULE.validate(self.root)})

    def test_archived_change_cannot_be_current_and_history_is_not_audited(self):
        archive = self.root / "openspec/changes/archive/2026-10-01-old-change"
        archive.mkdir(parents=True)
        archive.joinpath("spec.md").write_text("[old report](missing.md)\nTBD-OLD-001\n")
        self.assertEqual(set(), self.codes())
        self.index(current="old-change")
        self.assertTrue({"OPENSPEC_CHANGE_UNKNOWN", "SPEC_READINESS_CONFLICT"} <= self.codes())

    def test_blocked_draft_may_have_no_current_change(self):
        self.index(current="none", ready="blocked")
        self.assertEqual(set(), self.codes())
        self.index(current="none")
        self.assertIn("SPEC_READINESS_CONFLICT", self.codes())

    def test_framework_migration_cannot_leave_legacy_schema_selected(self):
        self.replace(self.root / "SPEC.md", "spec_framework: openspec", "spec_framework: openspec\nspec_schema: 2")
        self.assertIn("SPEC_FRAMEWORK_CONFLICT", self.codes())
        self.assertNotIn("MISSING_DOMAIN_SPEC", self.codes())

    def test_scope_references_need_active_changes_and_valid_names(self):
        for value in ("Missing_Change", "add-core-action,,other", "[add-core-action]"):
            with self.subTest(value=value):
                self.index(current=value)
                self.assertIn("OPENSPEC_SCOPE_INVALID", self.codes())

    def test_missing_current_artifacts_and_task_coverage_block_readiness(self):
        self.change.joinpath("tasks.md").unlink()
        self.assertTrue({"OPENSPEC_ARTIFACT_MISSING", "OPENSPEC_TASKS_MISSING", "CURRENT_AC_UNCOVERED", "SPEC_READINESS_CONFLICT"} <= self.codes())

    def test_manual_acceptance_requires_a_named_owner(self):
        self.replace(self.delta, "- Acceptance owner: product owner", "- Acceptance owner:")
        self.assertTrue({"OPENSPEC_ACCEPTANCE_OWNER_MISSING", "SPEC_READINESS_CONFLICT"} <= self.codes())

    def test_coverage_uses_existing_titles_without_inventing_ids(self):
        self.replace(self.delta, "AC-CORE-001 Successful reservation", "Successful reservation")
        self.replace(self.change / "tasks.md", "AC-CORE-001", "[successful reservation](specs/core-action/spec.md#scenario-successful-reservation)")
        self.assertEqual(set(), self.codes())

    def test_sources_and_relative_links_are_checked_without_execution(self):
        self.replace(self.delta, "PRD-CORE-001", "PRD-MISSING-001")
        self.assertIn("UNKNOWN_PRD_SOURCE", self.codes())
        self.replace(self.change / "design.md", "../../../ARCHITECTURE.md", "../../../missing.md")
        self.assertIn("BROKEN_LINK", self.codes())
        marker = self.root / "unexpected-execution"
        self.replace(self.delta, "run the reservation integration check", f"touch {marker}")
        MODULE.validate(self.root)
        self.assertFalse(marker.exists())

    def test_broken_current_links_conflict_with_ready_gate(self):
        self.replace(self.change / "design.md", "../../../ARCHITECTURE.md", "../../../missing.md")
        self.assertTrue({"BROKEN_LINK", "SPEC_READINESS_CONFLICT"} <= self.codes())

    def test_custom_schema_contract_is_deferred_to_official_tools(self):
        self.replace(self.root / "openspec/config.yaml", "schema: spec-driven", "schema: research-first")
        self.change.joinpath("proposal.md").unlink()
        self.change.joinpath("tasks.md").unlink()
        self.delta.unlink()
        self.replace(self.root / "SPEC.md", "[proposal](openspec/changes/add-core-action/proposal.md)", "")
        self.replace(self.root / "SPEC.md", "[behavior](openspec/changes/add-core-action/specs/core-action/spec.md)", "")
        self.replace(self.root / "SPEC.md", "[tasks](openspec/changes/add-core-action/tasks.md)", "")
        self.assertEqual(set(), self.codes())
        self.assertIn("OPENSPEC_CUSTOM_SCHEMA", {item.code for item in MODULE.validate(self.root)})

    def test_passed_claims_require_evidence_revision_and_valid_date(self):
        self.replace(self.delta, "- Result: not-run", "- Result: passed")
        self.assertTrue({"SPEC_PASS_WITHOUT_EVIDENCE", "SPEC_PASS_WITHOUT_REVISION", "SPEC_PASS_WITHOUT_DATE", "SPEC_READINESS_CONFLICT"} <= self.codes())
        self.change.joinpath("verification.md").write_text("# Synthetic fixture report\n")
        self.replace(self.delta, "- Result: passed", "- Result: passed\n- Evidence: [report](../../verification.md)\n- Tested revision: fixture-revision\n- Executed on: 2026-10-14")
        self.assertEqual(set(), self.codes())
        self.replace(self.delta, "2026-10-14", "2026-02-30")
        self.assertIn("SPEC_PASS_WITHOUT_DATE", self.codes())

    def test_json_interface_contracts_are_checked(self):
        note = self.root / "docs/interfaces/reservation.md"
        note.parent.mkdir(parents=True)
        note.write_text("# Contract\n\n[request](../../contracts/request.json)\n")
        contract = self.root / "contracts/request.json"
        contract.parent.mkdir()
        contract.write_text("{broken json")
        self.assertIn("CONTRACT_JSON_INVALID", self.codes())

    def test_cli_json_shape_and_read_only_behavior(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(0, MODULE.main([str(self.root), "--json"]))
        self.assertEqual({"summary", "findings"}, set(json.loads(output.getvalue())))
        self.assertEqual(before, {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()})

    @unittest.skipUnless(CLI, "Official OpenSpec CLI is unavailable")
    def test_generated_templates_pass_official_strict_validation_and_status(self):
        environment = dict(os.environ, OPENSPEC_TELEMETRY="0", DO_NOT_TRACK="1")
        result = subprocess.run([CLI, "validate", "--all", "--strict", "--no-interactive"], cwd=self.root,
                                env=environment, capture_output=True, text=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        status = subprocess.run([CLI, "status", "--change", "add-core-action", "--json"], cwd=self.root,
                                env=environment, capture_output=True, text=True, timeout=30)
        self.assertEqual(0, status.returncode, status.stdout + status.stderr)
        self.assertTrue(json.loads(status.stdout)["isComplete"])
        self.assertNotIn("- [x]", self.change.joinpath("tasks.md").read_text())
        self.assertEqual([], list(self.root.joinpath("openspec/specs").rglob("spec.md")))


if __name__ == "__main__":
    unittest.main()
