from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.render import render_source_markdown
from creator_passport.sku_models import SkuSourcePassport
from creator_passport.sku_questions import (
    generate_buying_question_answers,
    generate_comparison_sections,
    render_comparison_markdown,
    render_faq_markdown,
)
from creator_passport.models import load_passport
from tests.test_sku_render import sample_passport


def question_passport() -> SkuSourcePassport:
    data = sample_passport().to_dict()
    data["sku_source"]["buying_questions"] = [
        {
            "id": "q-display",
            "question": "Does the NS 200 include a backlit LCD?",
            "intent": "choose",
            "expected_facts": ["backlit LCD"],
            "expected_limitations": ["Use only with supported AC circuits."],
            "competitor_context_ids": ["ctx-meter"],
        },
        {
            "id": "q-compat",
            "question": "Is the NS 200 compatible with CAT III test leads?",
            "intent": "compatibility",
        },
    ]
    data["sku_source"]["competitor_context"] = [
        {
            "id": "ctx-meter",
            "category": "field instruments",
            "competitor_name": "Field Gauge Co",
            "competitor_product_name": "FG 10 Meter",
            "basis": "Both are handheld field meters.",
            "comparison_points": ["Display type", "Supported test leads"],
            "known_differences": ["NS 200 compatibility lists CAT III test leads."],
            "avoid_claims": ["Do not claim lower price."],
        }
    ]
    return SkuSourcePassport.from_dict(data, base_url="https://northstar.example")


class SkuQuestionsTests(unittest.TestCase):
    def test_buying_question_answers_are_deterministic_and_evidence_bound(self) -> None:
        passport = question_passport()
        first = generate_buying_question_answers(passport)
        second = generate_buying_question_answers(passport)

        self.assertEqual(first, second)
        display_answer = first[1]
        self.assertEqual(display_answer.question_id, "q-display")
        self.assertEqual(display_answer.facts[0].claim_ids, ("claim-display",))
        self.assertEqual(display_answer.facts[0].evidence_ids, ("ev-display",))
        self.assertIn("backlit LCD", display_answer.answer)

    def test_fallback_answer_uses_existing_facts_without_inventing_claims(self) -> None:
        answer = generate_buying_question_answers(question_passport())[0]

        self.assertEqual(answer.question_id, "q-compat")
        self.assertEqual(answer.facts[0].text, "CAT III test leads")
        self.assertEqual(answer.facts[0].claim_ids, ())
        self.assertNotIn("best", answer.answer.lower())

    def test_comparison_sections_use_only_explicit_competitor_context(self) -> None:
        markdown = render_comparison_markdown(question_passport())

        self.assertIn("FG 10 Meter", markdown)
        self.assertIn("Both are handheld field meters.", markdown)
        self.assertIn("Display type", markdown)
        self.assertIn("Do not claim lower price.", markdown)
        self.assertNotIn("cheaper", markdown.lower())
        self.assertNotIn("higher rated", markdown.lower())

    def test_missing_optional_context_renders_stable_empty_sections(self) -> None:
        data = sample_passport().to_dict()
        data["sku_source"]["competitor_context"] = []
        passport = SkuSourcePassport.from_dict(data, base_url="https://northstar.example")

        self.assertEqual(generate_comparison_sections(passport), [])
        self.assertIn("No explicit competitor context listed.", render_comparison_markdown(passport))
        self.assertIn("Is the NS 200 compatible", render_faq_markdown(passport))

    def test_creator_workflow_renderer_is_unchanged(self) -> None:
        passport = load_passport(str(ROOT / "examples" / "source_passport.json"))
        rendered = render_source_markdown(passport)

        self.assertIn("## Claim-evidence map", rendered)
        self.assertIn(passport.source_anchor, rendered)


if __name__ == "__main__":
    unittest.main()
