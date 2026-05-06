from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.models import load_passport
from creator_passport.sku_monitor import evaluate_sku_answer
from tests.test_sku_render import sample_passport


class SkuMonitorTests(unittest.TestCase):
    def test_positive_citation_and_coverage_scoring(self) -> None:
        passport = sample_passport()
        question = passport.buying_questions[0]
        response = (
            f"{passport.brand.name} says the {passport.sku.product_name} includes a backlit LCD "
            f"and supports CAT III test leads. See {passport.canonical_url} "
            f"and source hash {passport.content_hash}."
        )

        result = evaluate_sku_answer(passport, question, response)

        run = result.retrieval_run
        self.assertTrue(run.brand_mentioned)
        self.assertTrue(run.sku_mentioned)
        self.assertTrue(run.canonical_url_cited)
        self.assertTrue(run.source_hash_cited)
        self.assertGreaterEqual(run.score, 70)
        self.assertEqual(run.claim_coverage["claim-display"], "covered")
        self.assertFalse(run.wrong_specs_present)
        self.assertTrue(result.revision_suggestions)
        self.assertEqual(result.revision_suggestions[0].reason, "The monitored answer preserved the main SKU retrieval signals.")

    def test_missing_citation_creates_revision_suggestion(self) -> None:
        passport = sample_passport()
        question = passport.buying_questions[0]
        response = f"{passport.brand.name} says the {passport.sku.product_name} includes a backlit LCD."

        result = evaluate_sku_answer(passport, question, response)

        self.assertFalse(result.retrieval_run.canonical_url_cited)
        self.assertFalse(result.retrieval_run.source_hash_cited)
        self.assertTrue(
            any("canonical SKU URL" in item.reason for item in result.revision_suggestions)
        )
        self.assertTrue(
            any(item.target == "source_page" for item in result.revision_suggestions)
        )

    def test_wrong_spec_limitations_and_competitor_context_are_detected(self) -> None:
        passport = sample_passport()
        data = passport.to_dict()
        data["sku_source"]["buying_questions"] = [
            {
                "id": "q-compare",
                "question": "How does the NS 200 compare to a rival meter?",
                "intent": "compare",
                "expected_limitations": ["Use only with supported AC circuits."],
                "competitor_context_ids": ["ctx-meter"],
            }
        ]
        data["sku_source"]["competitor_context"] = [
            {
                "id": "ctx-meter",
                "category": "field instruments",
                "competitor_name": "Field Gauge Co",
                "competitor_product_name": "FG 10 Meter",
                "basis": "Both are handheld field meters.",
                "comparison_points": ["Display type"],
            }
        ]
        passport = type(passport).from_dict(data, base_url="https://northstar.example")
        question = passport.buying_questions[0]
        response = (
            "The display is a monochrome LCD and the NS 200 is cheaper than the FG 10 Meter. "
            "Use only with supported AC circuits."
        )

        result = evaluate_sku_answer(passport, question, response)

        run = result.retrieval_run
        self.assertTrue(run.wrong_specs_present)
        self.assertTrue(run.limitations_preserved)
        self.assertTrue(run.competitor_context_present)
        self.assertTrue(run.buying_intent_matched)
        self.assertTrue(any(item.target == "evidence" for item in result.revision_suggestions))

    def test_creator_workflow_remains_unchanged(self) -> None:
        from creator_passport.render import render_source_markdown

        passport = load_passport(str(ROOT / "examples" / "source_passport.json"))
        rendered = render_source_markdown(passport)

        self.assertIn("## Claim-evidence map", rendered)
        self.assertIn(passport.source_anchor, rendered)


if __name__ == "__main__":
    unittest.main()
