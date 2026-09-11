from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).parents[3]
SKILL_ROOT = Path(__file__).parents[1]
README = REPO_ROOT / "README.md"
SKILL = SKILL_ROOT / "SKILL.md"
GUIDANCE = SKILL_ROOT / "references" / "frontend-companion-skills.md"


class FrontendCompanionSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.readme = README.read_text(encoding="utf-8")
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.guidance = GUIDANCE.read_text(encoding="utf-8")

    def test_installation_commands_cover_the_frontend_stack(self) -> None:
        expected = (
            "https://github.com/anthropics/skills --skill frontend-design",
            "https://github.com/vercel-labs/agent-skills --skill web-design-guidelines",
            "https://github.com/vercel-labs/agent-skills --skill vercel-react-best-practices",
            "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max",
        )
        for command_fragment in expected:
            with self.subTest(command_fragment=command_fragment):
                self.assertIn(command_fragment, self.readme)

    def test_skill_routes_to_companion_guidance(self) -> None:
        self.assertIn(
            "references/frontend-companion-skills.md",
            self.skill,
        )
        for skill_name in (
            "frontend-design",
            "ui-ux-pro-max",
            "web-design-guidelines",
            "vercel-react-best-practices",
        ):
            with self.subTest(skill_name=skill_name):
                self.assertIn(skill_name, self.skill)
                self.assertIn(skill_name, self.guidance)

    def test_react_guidance_is_conditional(self) -> None:
        self.assertIn("React/Next.js", self.guidance)
        self.assertIn("Vue, Svelte", self.guidance)
        self.assertIn("React/Next.js 专属规则只能在确认技术栈后启用", self.skill)

    def test_companions_are_not_claimed_as_automatic_dependencies(self) -> None:
        self.assertIn("不是 `project-blueprint` 的自动硬依赖", self.readme)
        self.assertIn("not automatic dependencies", self.guidance)
        self.assertIn("Do not add an unsupported `depends_on` field", self.guidance)


if __name__ == "__main__":
    unittest.main()
