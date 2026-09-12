from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from test_validate_blueprint import MODULE, build_valid_blueprint, document


DIRECTION = "## Visual direction\n\nReference-led community dictionary; expressive search area and compact results.\n"
HANDOFF = "## Prototype handoff\n\nReview room search and copying with supplied real content on desktop and narrow screens. Return screenshots and task observations.\n- Deferred reason: User requested documentation only; frontend owner will deliver the preview before visual acceptance.\n"
PREVIEW = (
    "## Visual preview\n\n- Artifact: [Component and room search preview](design/preview.html)\n"
    "- Preview revision and viewing/startup instructions: preview-v1; open the HTML directly.\n"
    "- Components, variants and states demonstrated: buttons, filters, empty results and search page.\n"
)
PENDING = "## Visual review\n\n- Review status: pending\n"
REVIEW = (
    "## Visual review\n\n- Review status: confirmed\n"
    "- Evidence: [Approved system](design-system.md)\n"
    "- Reviewed revision: Atlas baseline approved on 2026-09-10\n"
    "- Confirmed scope: Existing portal page patterns, components and responsive states; no deltas.\n"
    "- Reviewer: Design team\n- Reviewed on: 2026-09-10\n"
    "- Findings and adjustments: Approved page patterns apply; no project-specific deltas.\n"
)
DETAILS = (
    "## Application shell and layout\n\nconfirmed: header navigation and filtered results; mobile filters use a drawer.\n"
    "## Token source\n\n[Maintained theme](design-system.md) owned by the design team.\n"
    "## Color system\n\n[Semantic palette and contrast states](design-system.md#palette).\n"
    "## Typography system\n\n[Type scale and fallbacks](design-system.md#type).\n"
    "## UI foundation and component sourcing\n\nconfirmed: company Atlas components.\n"
    "## Component specifications\n\nButton uses Atlas primary; search input uses Atlas search; list uses result-row. Inherit focus, error and disabled states.\n"
)


class DesignStageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        build_valid_blueprint(self.root)
        self.root.joinpath("design-system.md").write_text(
            "# Approved system\n\n## Palette\n\nCanvas #fff; text #111.\n\n## Type\n\nBody system-ui, sans-serif 16px/24px.\n",
            encoding="utf-8",
        )

    def write_design(self, stage: str | None, body: str) -> None:
        text = document("design", body)
        if stage is not None:
            text = text.replace("blueprint_kind: design\n", f"blueprint_kind: design\ndesign_stage: {stage}\n")
        self.root.joinpath("DESIGN.md").write_text(text, encoding="utf-8")

    def set_ready(self, status: str = "ready") -> None:
        path = self.root / "SPEC.md"
        path.write_text(path.read_text() + f"\n| Gate | Status |\n|---|---|\n| implementation-ready | {status} |\n")

    def codes(self) -> set[str]:
        return {item.code for item in MODULE.validate(self.root) if item.severity != "info"}

    def test_direction_accepts_no_exact_visual_values(self) -> None:
        self.write_design("direction", DIRECTION)
        self.assertEqual(set(), self.codes())

    def test_direction_requires_a_direction(self) -> None:
        self.write_design("direction", "# Draft\n")
        self.assertIn("DESIGN_DIRECTION_MISSING", self.codes())

    def test_prototype_accepts_pending_review_without_visual_parameters(self) -> None:
        self.write_design("prototype", DIRECTION + HANDOFF + PENDING)
        self.assertEqual(set(), self.codes())

    def test_prototype_requires_handoff_and_review(self) -> None:
        self.write_design("prototype", DIRECTION)
        self.assertTrue({"DESIGN_HANDOFF_MISSING", "DESIGN_REVIEW_MISSING"} <= self.codes())

    def test_delivered_preview_can_await_human_review(self) -> None:
        self.root.joinpath("design").mkdir()
        self.root.joinpath("design/preview.html").write_text("<!doctype html><title>Room search preview</title>")
        self.write_design("prototype", DIRECTION + PREVIEW + PENDING)
        self.assertEqual(set(), self.codes())
        self.set_ready()
        self.assertIn("DESIGN_READINESS_CONFLICT", self.codes())

    def test_preview_link_must_exist(self) -> None:
        self.write_design("prototype", DIRECTION + PREVIEW + PENDING)
        self.assertIn("BROKEN_LINK", self.codes())

    def test_existing_preview_route_does_not_require_single_html(self) -> None:
        preview = PREVIEW.replace("design/preview.html", "http://localhost:5173/design-preview")
        self.write_design("prototype", DIRECTION + preview + PENDING)
        self.assertEqual(set(), self.codes())

    def test_brief_alone_must_explain_missing_preview(self) -> None:
        handoff = HANDOFF.split("- Deferred reason:")[0]
        for reason in ("", "TBD", "[explain later]"):
            with self.subTest(reason=reason):
                self.write_design("prototype", DIRECTION + handoff + f"- Deferred reason: {reason}\n" + PENDING)
                self.assertIn("DESIGN_PREVIEW_DELIVERY_MISSING", self.codes())

    def test_chinese_preview_fields_are_supported(self) -> None:
        preview = "## 视觉预览\n\n- 暂缓原因: 用户本轮只要文档，设计负责人在下次评审前制作组件与业务页面预览。\n"
        self.write_design("prototype", DIRECTION + preview + PENDING)
        self.assertEqual(set(), self.codes())

    def test_confirmed_record_requires_evidence_reviewer_date_and_findings(self) -> None:
        for field in ("Evidence", "Reviewed revision", "Confirmed scope", "Reviewer", "Reviewed on", "Findings and adjustments"):
            with self.subTest(field=field):
                lines = [line if not line.startswith(f"- {field}:") else f"- {field}:" for line in REVIEW.splitlines()]
                self.write_design("specification", DIRECTION + "\n".join(lines) + "\n" + DETAILS)
                self.assertIn("DESIGN_REVIEW_EVIDENCE_INCOMPLETE", self.codes())

    def test_confirmation_without_baseline_or_scope_blocks_readiness(self) -> None:
        self.set_ready()
        for field in ("Reviewed revision", "Confirmed scope"):
            for value in ("", "TBD", "[fill in]"):
                with self.subTest(field=field, value=value):
                    lines = [line if not line.startswith(f"- {field}:") else f"- {field}: {value}" for line in REVIEW.splitlines()]
                    self.write_design("specification", DIRECTION + "\n".join(lines) + "\n" + DETAILS)
                    self.assertTrue({"DESIGN_REVIEW_EVIDENCE_INCOMPLETE", "DESIGN_READINESS_CONFLICT"} <= self.codes())

    def test_review_date_must_be_a_real_calendar_date(self) -> None:
        self.write_design("specification", DIRECTION + REVIEW.replace("2026-09-10", "2026-02-30") + DETAILS)
        self.assertIn("DESIGN_REVIEW_EVIDENCE_INCOMPLETE", self.codes())

    def test_confirmed_word_in_prose_is_not_confirmation(self) -> None:
        self.write_design("specification", DIRECTION + PENDING + "Brand confirmed; no page reviewed.\n" + DETAILS)
        self.assertIn("DESIGN_REVIEW_UNCONFIRMED", self.codes())

    def test_linked_approved_system_avoids_duplicate_component_values(self) -> None:
        self.write_design("specification", DIRECTION + REVIEW + DETAILS)
        self.set_ready()
        self.assertEqual(set(), self.codes())

    def test_chinese_review_fields_are_supported(self) -> None:
        review = REVIEW
        for english, chinese in (("Visual review", "视觉评审"), ("Review status", "评审状态"), ("Evidence", "证据"), ("Reviewed revision", "评审版本"), ("Confirmed scope", "确认范围"), ("Reviewer", "评审人"), ("Reviewed on", "评审日期"), ("Findings and adjustments", "结论与调整")):
            review = review.replace(english, chinese)
        self.write_design("specification", DIRECTION + review + DETAILS)
        self.assertEqual(set(), self.codes())

    def test_inline_token_source_is_supported_and_bad_anchor_reported(self) -> None:
        details = DETAILS.replace("[Maintained theme](design-system.md)", "[Inline tokens](#shared-tokens)")
        inline = "\n## Shared tokens\n\nUse the maintained semantic palette above.\n"
        self.write_design("specification", DIRECTION + REVIEW + details + inline)
        self.assertEqual(set(), self.codes())
        self.write_design("specification", DIRECTION + REVIEW + details)
        self.assertIn("DESIGN_TOKEN_SOURCE_UNRESOLVED", self.codes())

    def test_missing_source_and_empty_component_rules_are_reported(self) -> None:
        details = DETAILS.replace("[Maintained theme](design-system.md)", "Use our brand")
        details = details[:details.index("## Component specifications")] + "## Component specifications\n"
        self.write_design("specification", DIRECTION + REVIEW + details)
        self.assertTrue({"DESIGN_TOKEN_SOURCE_UNRESOLVED", "DESIGN_COMPONENT_SPECS_MISSING"} <= self.codes())

    def test_full_parameters_cannot_replace_review(self) -> None:
        self.write_design("specification", DIRECTION + DETAILS)
        self.set_ready()
        self.assertTrue({"DESIGN_REVIEW_MISSING", "DESIGN_READINESS_CONFLICT"} <= self.codes())

    def test_broken_review_or_token_links_are_errors(self) -> None:
        self.write_design("specification", DIRECTION + REVIEW + DETAILS)
        self.root.joinpath("design-system.md").unlink()
        self.assertIn("BROKEN_LINK", self.codes())

    def test_exploration_cannot_claim_implementation_ready(self) -> None:
        self.set_ready()
        for stage, body in (("direction", DIRECTION), ("prototype", DIRECTION + HANDOFF + PENDING)):
            with self.subTest(stage=stage):
                self.write_design(stage, body)
                self.assertIn("DESIGN_READINESS_CONFLICT", self.codes())

    def test_blocked_gate_does_not_report_readiness_conflict(self) -> None:
        self.set_ready("blocked")
        self.write_design("direction", DIRECTION)
        self.assertEqual(set(), self.codes())

    def test_invalid_or_empty_stage_is_an_error(self) -> None:
        for stage in ("", "draft", "approved", "Direction"):
            with self.subTest(stage=stage):
                self.write_design(stage, DIRECTION)
                findings = MODULE.validate(self.root)
                self.assertTrue(any(item.code == "DESIGN_STAGE_INVALID" and item.severity == "error" for item in findings))

    def test_api_only_exemption_requires_a_reason_and_preserves_other_checks(self) -> None:
        self.write_design("not-applicable", "## Applicability\n\nAPI-only integration; no user-facing UI.\n")
        self.set_ready()
        self.assertEqual(set(), self.codes())
        self.root.joinpath("SECURITY.md").unlink()
        self.assertIn("MISSING_ARTIFACT", self.codes())
        self.write_design("not-applicable", "# Design\n")
        self.assertTrue({"DESIGN_APPLICABILITY_MISSING", "DESIGN_READINESS_CONFLICT"} <= self.codes())

    def test_legacy_retains_strict_detail_checks_and_gets_migration_info(self) -> None:
        self.write_design(None, DIRECTION)
        findings = MODULE.validate(self.root)
        self.assertTrue(any(item.code == "LEGACY_DESIGN_STAGE" and item.severity == "info" for item in findings))
        self.assertTrue({"DESIGN_COLOR_SYSTEM_MISSING", "DESIGN_COMPONENT_SPECS_MISSING"} <= self.codes())

    def test_cli_json_shape_and_error_exit_code_are_unchanged(self) -> None:
        self.write_design("direction", DIRECTION)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = MODULE.main([str(self.root), "--json"])
        self.assertEqual(0, result)
        payload = json.loads(output.getvalue())
        self.assertEqual({"summary", "findings"}, set(payload))
        self.set_ready()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, MODULE.main([str(self.root), "--json"]))


if __name__ == "__main__":
    unittest.main()
