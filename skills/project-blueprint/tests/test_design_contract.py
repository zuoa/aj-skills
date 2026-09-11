from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "templates" / "DESIGN.md"
SKILL = SKILL_ROOT / "SKILL.md"
GUIDANCE = SKILL_ROOT / "references" / "design-and-architecture.md"


class DesignContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = TEMPLATE.read_text(encoding="utf-8")
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.guidance = GUIDANCE.read_text(encoding="utf-8")

    def test_template_requires_complete_semantic_palette(self) -> None:
        required_tokens = (
            "color-canvas",
            "color-surface",
            "color-text-primary",
            "color-text-secondary",
            "color-border",
            "color-action-primary",
            "color-action-primary-hover",
            "color-action-primary-pressed",
            "color-text-on-action",
            "color-focus-ring",
            "color-disabled",
            "color-success",
            "color-warning",
            "color-error",
            "color-info",
        )
        self.assertIn("## Color system", self.template)
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, self.template)

    def test_template_requires_concrete_type_scale(self) -> None:
        required_roles = (
            "type-page-title",
            "type-section-title",
            "type-body",
            "type-body-small",
            "type-label",
            "type-action",
            "type-helper",
            "type-data",
        )
        self.assertIn("## Typography system", self.template)
        self.assertIn("Desktop size / line height", self.template)
        self.assertIn("Mobile size / line height", self.template)
        self.assertIn("Font source, license, loading/fallback", self.template)
        for role in required_roles:
            with self.subTest(role=role):
                self.assertIn(role, self.template)

    def test_template_maps_core_components_to_typography_and_geometry(self) -> None:
        required_components = (
            "Button",
            "Input/Select",
            "Navigation/Tabs",
            "Table/List",
            "Card",
            "Dialog/Drawer",
            "Toast/Alert",
        )
        self.assertIn("## Component specifications", self.template)
        self.assertIn("Resolved font family", self.template)
        self.assertIn("Size / line height / weight", self.template)
        self.assertIn("Height/padding/gap", self.template)
        for component in required_components:
            with self.subTest(component=component):
                self.assertIn(component, self.template)

    def test_skill_and_guidance_disallow_blanket_visual_tbd(self) -> None:
        self.assertIn("provisional 基线值", self.skill)
        self.assertIn("不能用空白占位符代替", self.skill)
        self.assertIn("Do not leave every visual token pending", self.guidance)


if __name__ == "__main__":
    unittest.main()
