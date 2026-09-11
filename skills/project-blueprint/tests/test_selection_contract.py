from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).parents[1]
MANDATORY_STACKS = (
    "Java Spring Boot + React",
    "Python FastAPI + Vue SPA",
    "Python Flask + Jinja SSR",
)


class SelectionContractTests(unittest.TestCase):
    def test_mandatory_stacks_are_in_skill_reference_and_template(self) -> None:
        documents = (
            SKILL_ROOT.joinpath("SKILL.md").read_text(encoding="utf-8"),
            SKILL_ROOT.joinpath("references/selection-rubric.md").read_text(encoding="utf-8"),
            SKILL_ROOT.joinpath("assets/templates/ARCHITECTURE.md").read_text(encoding="utf-8"),
        )
        for stack in MANDATORY_STACKS:
            for document in documents:
                self.assertIn(stack, document)

    def test_selection_reference_preserves_and_assesses_all_three(self) -> None:
        reference = SKILL_ROOT.joinpath("references/selection-rubric.md").read_text(encoding="utf-8")
        self.assertIn("Keep all three rows", reference)
        self.assertIn("not recommended", reference)
        self.assertIn("Add no more than two analysis-derived alternatives", reference)
        self.assertLess(
            reference.index(MANDATORY_STACKS[0]),
            reference.index(MANDATORY_STACKS[1]),
        )
        self.assertLess(
            reference.index(MANDATORY_STACKS[1]),
            reference.index(MANDATORY_STACKS[2]),
        )

    def test_stack_selection_eval_covers_the_contract(self) -> None:
        data = json.loads(SKILL_ROOT.joinpath("evals/evals.json").read_text(encoding="utf-8"))
        stack_eval = next(item for item in data["evals"] if item["id"] == 8)
        combined = "\n".join([stack_eval["prompt"], *stack_eval["expectations"]])
        for stack in MANDATORY_STACKS:
            self.assertIn(stack, combined)


if __name__ == "__main__":
    unittest.main()
