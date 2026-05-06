from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.__main__ import main
from tests.test_sku_models import valid_contract


class SkuCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = ROOT / "generated" / "test-runs" / uuid.uuid4().hex
        self.tmp.mkdir(parents=True, exist_ok=True)

    def test_sku_generate_and_check_write_complete_product_pack(self) -> None:
        input_path = self.tmp / "sku-source.json"
        input_path.write_text(json.dumps(valid_contract()), encoding="utf-8")
        out_dir = self.tmp / "out"

        self.assertEqual(main(["sku-generate", str(input_path), "--out", str(out_dir)]), 0)
        self.assertEqual(main(["sku-check", str(out_dir)]), 0)
        self.assertTrue((out_dir / "schema.json").exists())
        self.assertTrue((out_dir / "llms.txt").exists())
        self.assertTrue((out_dir / "faq.json").exists())

    def test_sku_generate_handles_multiple_skus_without_flattening_to_first(self) -> None:
        data = valid_contract()
        second = {
            **data["skus"][0],
            "id": "reference-item-b",
            "product_name": "Reference Item B",
            "slug": "reference-item-b",
            "canonical_url": "https://source.test/items/reference-item-b",
            "facts": {
                "summary": "Reference Item B is a second SKU for batch generation.",
                "key_specs": {"interface": "beta"},
            },
        }
        data["skus"] = [data["skus"][0], second]
        input_path = self.tmp / "multi-sku-source.json"
        input_path.write_text(json.dumps(data), encoding="utf-8")
        out_dir = self.tmp / "out"

        self.assertEqual(main(["sku-generate", str(input_path), "--out", str(out_dir)]), 0)
        product_files = sorted(path.name for path in (out_dir / "ai" / "products").glob("*.md"))

        self.assertEqual(product_files, ["reference-item-a.md", "reference-item-b.md"])

    def test_sku_build_writes_catalog_review_and_monitor_outputs(self) -> None:
        data = valid_contract()
        data["skus"][0]["claims"] = [
            {
                "id": "claim-alpha",
                "claim": "Reference Item A uses interface alpha.",
                "evidence_ids": ["ev-alpha"],
                "claim_type": "spec",
            }
        ]
        data["skus"][0]["evidence"] = [
            {
                "id": "ev-alpha",
                "source_type": "human_note",
                "title": "Reference Item A source note",
                "excerpt": "Interface: alpha.",
            }
        ]
        data["skus"][0]["limitations"] = ["Does not include beta interface support."]
        second = {
            **data["skus"][0],
            "id": "reference-item-b",
            "product_name": "Reference Item B",
            "slug": "reference-item-b",
            "canonical_url": "https://source.test/items/reference-item-b",
            "facts": {
                "summary": "Reference Item B is a second SKU for product-loop generation.",
                "key_specs": {"interface": "beta"},
            },
            "claims": [
                {
                    "id": "claim-beta",
                    "claim": "Reference Item B uses interface beta.",
                    "evidence_ids": ["ev-beta"],
                    "claim_type": "spec",
                }
            ],
            "evidence": [
                {
                    "id": "ev-beta",
                    "source_type": "human_note",
                    "title": "Reference Item B source note",
                    "excerpt": "Interface: beta.",
                }
            ],
        }
        data["skus"] = [data["skus"][0], second]
        data["buying_questions"] = [
            {
                "id": "q-alpha",
                "question": "Does Reference Item A support beta?",
                "intent": "limitation",
                "sku_ids": ["reference-item-a"],
                "expected_limitations": ["Does not include beta interface support."],
            }
        ]
        data["retrieval_runs"] = [
            {
                "id": "run-alpha-missing-citation",
                "question_id": "q-alpha",
                "ran_at": "2026-05-06",
                "provider": "manual-fixture",
                "sku_ids": ["reference-item-a"],
                "response_text": "Reference Item A uses alpha, but no source citation is included.",
            }
        ]
        input_path = self.tmp / "sku-source.json"
        input_path.write_text(json.dumps(data), encoding="utf-8")
        out_dir = self.tmp / "out"

        self.assertEqual(main(["sku-build", str(input_path), "--out", str(out_dir)]), 0)
        self.assertEqual(main(["sku-check", str(out_dir)]), 0)

        index = (out_dir / "ai" / "product-index.md").read_text(encoding="utf-8")
        self.assertIn("Reference Item A", index)
        self.assertIn("Reference Item B", index)
        self.assertTrue((out_dir / "sku-review.json").exists())
        self.assertTrue((out_dir / "sku-review.md").exists())
        report = (out_dir / "monitor" / "report.md").read_text(encoding="utf-8")
        self.assertIn("run-alpha-missing-citation", report)
        suggestions = json.loads((out_dir / "revision_suggestions.json").read_text(encoding="utf-8"))
        self.assertTrue(any(item["target"] == "source_page" for item in suggestions["revision_suggestions"]))

    def test_sku_check_rejects_stale_sku_artifacts(self) -> None:
        input_path = self.tmp / "sku-source.json"
        input_path.write_text(json.dumps(valid_contract()), encoding="utf-8")
        out_dir = self.tmp / "out"

        self.assertEqual(main(["sku-generate", str(input_path), "--out", str(out_dir)]), 0)
        stale_path = out_dir / "ai" / "products" / "stale-sku.md"
        stale_path.write_text("# stale", encoding="utf-8")

        self.assertEqual(main(["sku-check", str(out_dir)]), 1)

    def test_sku_review_rejects_claim_without_evidence(self) -> None:
        data = valid_contract()
        data["skus"][0]["claims"] = [
            {
                "id": "claim-unsupported",
                "claim": "Reference Item A has an unsupported claim.",
                "evidence_ids": ["missing-evidence"],
            }
        ]
        input_path = self.tmp / "sku-source.json"
        input_path.write_text(json.dumps(data), encoding="utf-8")

        self.assertEqual(main(["sku-review", "--input", str(input_path), "--out", str(self.tmp)]), 1)


if __name__ == "__main__":
    unittest.main()
