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
        self.assertIn("does not by itself justify a left sidebar", self.layout_catalog)

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


if __name__ == "__main__":
    unittest.main()
