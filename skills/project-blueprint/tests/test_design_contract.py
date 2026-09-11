from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "templates" / "DESIGN.md"
SKILL = SKILL_ROOT / "SKILL.md"
GUIDANCE = SKILL_ROOT / "references" / "design-and-architecture.md"
THEME_CATALOG = SKILL_ROOT / "references" / "theme-catalog.md"
LAYOUT_CATALOG = SKILL_ROOT / "references" / "layout-catalog.md"
EVALS = SKILL_ROOT / "evals" / "evals.json"


class DesignContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = TEMPLATE.read_text(encoding="utf-8")
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.guidance = GUIDANCE.read_text(encoding="utf-8")
        cls.theme_catalog = THEME_CATALOG.read_text(encoding="utf-8")
        cls.layout_catalog = LAYOUT_CATALOG.read_text(encoding="utf-8")

    def test_layout_recommendation_separates_shell_navigation_surface_and_chrome(self) -> None:
        self.assertIn("## Application shell and layout", self.template)
        self.assertIn("### Layout shortlist and recommendation", self.template)
        for term in ("layout family", "navigation model", "work-surface model", "platform chrome"):
            with self.subTest(term=term):
                self.assertIn(term, self.skill.lower())
                self.assertIn(term, self.guidance.lower())
                self.assertIn(term, self.layout_catalog.lower())
        self.assertIn("Closest rejected alternative", self.template)
        self.assertIn("Compact/mobile transformation", self.template)

    def test_layout_catalog_covers_recommendable_families_and_unified_identity(self) -> None:
        for layout_id in (
            "enterprise-workspace",
            "compact-product-shell",
            "focused-workbench",
            "operations-console",
            "catalog-hub",
            "guided-flow",
            "public-service-portal",
            "adaptive-mobile-app",
        ):
            with self.subTest(layout_id=layout_id):
                self.assertIn(layout_id, self.layout_catalog)
        for capability in ("Authentication", "SSO", "Tenant/workspace switcher", "Global search", "Notifications"):
            with self.subTest(capability=capability):
                self.assertIn(capability, self.layout_catalog)
        self.assertIn("SSO or unified login", self.template)
        self.assertIn("does not by itself justify a left sidebar", self.layout_catalog)

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

    def test_template_requires_a_coherent_ui_foundation_decision(self) -> None:
        self.assertIn("## UI foundation and component sourcing", self.template)
        self.assertIn("Selected foundation and mode", self.template)
        self.assertIn("Official compatibility evidence and access date", self.template)
        self.assertIn("Component coverage", self.template)
        self.assertIn("Icon system", self.template)

    def test_theme_recommendation_separates_family_appearance_and_density(self) -> None:
        self.assertIn("### Theme shortlist and recommendation", self.template)
        for term in ("theme family", "appearance", "density"):
            with self.subTest(term=term):
                self.assertIn(term, self.skill.lower())
                self.assertIn(term, self.theme_catalog.lower())
        self.assertIn("Framework adaptation", self.template)
        self.assertIn("Closest rejected alternative", self.template)

    def test_theme_catalog_covers_audience_directions_and_framework_adaptation(self) -> None:
        for theme_id in (
            "precision-neutral",
            "editorial-paper",
            "institutional-trust",
            "operations-dense",
            "calm-guidance",
            "expressive-studio",
        ):
            with self.subTest(theme_id=theme_id):
                self.assertIn(theme_id, self.theme_catalog)
        for foundation in (
            "shadcn/ui",
            "React Aria",
            "Chakra UI",
            "MUI",
            "Ant Design",
            "daisyUI",
            "PrimeVue",
            "Element Plus",
            "Flutter Material",
            "Jetpack Compose Material 3",
            "React Native Paper",
            "SwiftUI",
        ):
            with self.subTest(foundation=foundation):
                self.assertIn(foundation, self.theme_catalog)
        self.assertIn("primitive/semantic/component", self.theme_catalog)
        self.assertIn("SSR/no-flash", self.theme_catalog)

    def test_skill_and_guidance_prevent_browser_default_ui_regression(self) -> None:
        self.assertIn("React、Vue 等交互型客户端", self.skill)
        self.assertIn("浏览器未主题化的原生控件", self.skill)
        self.assertIn("shadcn/ui", self.skill)
        self.assertIn("shadcn-vue", self.skill)
        self.assertIn("Do not confuse semantic native HTML with unstyled browser UI", self.guidance)
        self.assertIn("A library's default demo appearance is not sufficient evidence", self.guidance)

    def test_vue_ui_foundation_regression_eval_exists(self) -> None:
        data = json.loads(EVALS.read_text(encoding="utf-8"))
        regression_eval = next(item for item in data["evals"] if item["id"] == 9)
        combined = "\n".join(
            [
                regression_eval["prompt"],
                regression_eval["expected_output"],
                *regression_eval["expectations"],
            ]
        )
        for term in ("Vue 3 + Vite", "UI 基础", "Select/Combobox", "Toast", "浏览器未主题化"):
            with self.subTest(term=term):
                self.assertIn(term, combined)

    def test_theme_and_framework_adaptation_eval_exists(self) -> None:
        data = json.loads(EVALS.read_text(encoding="utf-8"))
        regression_eval = next(item for item in data["evals"] if item["id"] == 10)
        combined = "\n".join(
            [
                regression_eval["prompt"],
                regression_eval["expected_output"],
                *regression_eval["expectations"],
            ]
        )
        for term in (
            "theme family",
            "appearance",
            "density",
            "shadcn/ui",
            "MUI",
            "SSR",
            "框架适配成本",
        ):
            with self.subTest(term=term):
                self.assertIn(term, combined)

    def test_skill_and_guidance_disallow_blanket_visual_tbd(self) -> None:
        self.assertIn("provisional 基线值", self.skill)
        self.assertIn("不能用空白占位符代替", self.skill)
        self.assertIn("Do not leave every visual token pending", self.guidance)


if __name__ == "__main__":
    unittest.main()
