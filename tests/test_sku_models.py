from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.models import ValidationError
from creator_passport.sku_models import Evidence, RetrievalRun, SkuSourcePassport


def valid_contract() -> dict:
    return {
        "brand": {
            "id": "neutral-source-unit",
            "name": "Neutral Source Unit",
            "domain": "https://source.test",
            "market": "test",
            "official_urls": ["https://source.test/info"],
        },
        "skus": [
            {
                "id": "reference-item-a",
                "brand_id": "neutral-source-unit",
                "product_name": "Reference Item A",
                "slug": "reference-item-a",
                "category": "Reference category",
                "canonical_url": "https://source.test/items/reference-item-a",
                "facts": {
                    "summary": "Reference Item A is a neutral fixture for SKU contract validation.",
                    "key_specs": {
                        "interface": "alpha",
                        "revision": 1,
                        "enabled": True,
                    },
                },
            }
        ],
    }


def collect_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(collect_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(collect_keys(item))
        return keys
    return set()


class SkuModelTests(unittest.TestCase):
    def test_valid_contract_root_shape_roundtrips_brand_and_skus(self) -> None:
        passport = SkuSourcePassport.from_dict(valid_contract(), base_url="https://source.test")

        serialized = passport.to_dict()
        self.assertEqual(serialized["brand"]["id"], "neutral-source-unit")
        self.assertEqual(len(serialized["skus"]), 1)
        self.assertEqual(serialized["skus"][0]["id"], "reference-item-a")

        roundtrip = SkuSourcePassport.from_dict(serialized, base_url="https://source.test")
        self.assertEqual(roundtrip.brand.to_dict(), passport.brand.to_dict())
        self.assertEqual(roundtrip.sku.to_dict(), passport.sku.to_dict())
        self.assertEqual(roundtrip.facts.to_dict(), passport.facts.to_dict())

    def test_missing_required_brand_sku_facts_and_claim_evidence_are_rejected(self) -> None:
        cases = [
            ("brand.name", {"brand": {"id": "neutral-source-unit", "domain": "https://source.test"}}),
            ("sku.canonical_url", {"skus": [{**valid_contract()["skus"][0], "canonical_url": ""}]}),
            ("facts.key_specs", {"skus": [{**valid_contract()["skus"][0], "facts": {"summary": "Only summary."}}]}),
            (
                "claims.evidence_ids",
                {
                    "skus": [
                        {
                            **valid_contract()["skus"][0],
                            "claims": [{"id": "claim-a", "claim": "Reference Item A has interface alpha."}],
                        }
                    ]
                },
            ),
        ]

        for expected, patch in cases:
            data = valid_contract()
            data.update(patch)
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(ValidationError, expected):
                    SkuSourcePassport.from_dict(data, base_url="https://source.test")

    def test_claims_must_reference_existing_evidence(self) -> None:
        data = valid_contract()
        data["skus"][0]["claims"] = [
            {
                "id": "claim-a",
                "claim": "Reference Item A has interface alpha.",
                "evidence_ids": ["missing-evidence"],
            }
        ]
        data["skus"][0]["evidence"] = [
            {
                "id": "evidence-a",
                "source_type": "human_note",
                "title": "Neutral fixture note",
                "excerpt": "The fixture uses interface alpha.",
            }
        ]

        with self.assertRaisesRegex(ValidationError, r"claims\.evidence_ids\[missing-evidence\]"):
            SkuSourcePassport.from_dict(data, base_url="https://source.test")

    def test_content_hash_is_stable_and_drives_paths_and_source_anchor(self) -> None:
        first = SkuSourcePassport.from_dict(valid_contract(), base_url="https://source.test")
        second = SkuSourcePassport.from_dict(valid_contract(), base_url="https://other.test")

        self.assertEqual(first.content_hash, first.compute_hash())
        self.assertEqual(first.content_hash, second.content_hash)
        self.assertEqual(first.canonical_path, f"/sku/reference-item-a-{first.content_hash}")
        self.assertEqual(first.markdown_path, f"/sku/reference-item-a-{first.content_hash}.md")
        self.assertEqual(first.canonical_url, f"https://source.test{first.canonical_path}")
        self.assertEqual(
            first.source_anchor,
            f"SKU Source Passport: {first.content_hash}\nSource: {first.canonical_url}",
        )

    def test_evidence_hash_is_stable_and_changes_with_source_content(self) -> None:
        source = {
            "id": "evidence-a",
            "source_type": "human_note",
            "title": "Neutral fixture note",
            "excerpt": "The fixture uses interface alpha.",
            "captured_at": "2026-01-01",
        }

        first = Evidence.from_dict(source)
        second = Evidence.from_dict(dict(source))
        changed = Evidence.from_dict({**source, "excerpt": "The fixture uses interface beta."})

        self.assertEqual(first.source_hash, second.source_hash)
        self.assertEqual(len(first.source_hash), 12)
        self.assertNotEqual(first.source_hash, changed.source_hash)

    def test_retrieval_score_is_clamped_to_contract_range(self) -> None:
        base = {
            "id": "run-a",
            "question_id": "question-a",
            "ran_at": "2026-01-01",
            "provider": "neutral-provider",
            "response_text": "Neutral response text.",
        }

        self.assertEqual(RetrievalRun.from_dict({**base, "score": -5}).score, 0)
        self.assertEqual(RetrievalRun.from_dict({**base, "score": 130}).score, 100)
        self.assertEqual(RetrievalRun.from_dict({**base, "score": "86"}).score, 86)
        self.assertEqual(RetrievalRun.from_dict({**base, "score": 42.5}).score, 42.5)

    def test_excluded_commercial_fields_are_not_serialized(self) -> None:
        data = valid_contract()
        data["skus"][0].update(
            {
                "price_range": "not serialized",
                "currency": "XXX",
                "availability": "not serialized",
            }
        )

        serialized = SkuSourcePassport.from_dict(data, base_url="https://source.test").to_dict()

        self.assertFalse({"price_range", "currency", "availability"} & collect_keys(serialized))


if __name__ == "__main__":
    unittest.main()
