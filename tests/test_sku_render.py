from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.render import render_source_markdown
from creator_passport.sku_models import SkuSourcePassport
from creator_passport.sku_render import (
    render_comparison_json,
    render_faq_json,
    render_product_index,
    render_product_json,
    render_product_llms,
    render_product_markdown,
    render_schema,
    write_product_pack,
)
from creator_passport.models import load_passport


def sample_passport() -> SkuSourcePassport:
    return SkuSourcePassport.from_dict(
        {
            "brand": {
                "id": "northstar-tools",
                "name": "Northstar Tools",
                "domain": "https://northstar.example",
                "description": "Manufacturer-owned product facts.",
                "official_urls": ["https://northstar.example/support"],
            },
            "sku": {
                "id": "ns-200",
                "brand_id": "northstar-tools",
                "product_name": "NS 200 Field Meter",
                "category": "field instruments",
                "canonical_url": "https://northstar.example/products/ns-200",
                "model_number": "NS-200",
                "source_urls": ["https://northstar.example/manuals/ns-200"],
                "facts": {
                    "summary": "A handheld field meter for measuring supported AC circuits.",
                    "key_specs": {
                        "display": "backlit LCD",
                        "measurement_modes": ["AC voltage", "continuity"],
                    },
                    "compatibility": ["CAT III test leads"],
                    "requirements": ["Two AA batteries"],
                    "certifications": ["IEC 61010"],
                    "warranty": ["Two-year limited warranty"],
                },
                "limitations": ["Extractor-only note should not render."],
                "use_cases": ["Extractor-only use case should not render."],
                "not_for": ["Extractor-only exclusion should not render."],
                "claims": [
                    {
                        "id": "claim-display",
                        "claim": "The product includes a backlit LCD display.",
                        "evidence_ids": ["ev-display"],
                        "claim_type": "spec",
                        "confidence": "high",
                    }
                ],
                "evidence": [
                    {
                        "id": "ev-display",
                        "source_type": "manual",
                        "title": "NS 200 User Manual",
                        "excerpt": "Display: backlit LCD.",
                        "url": "https://northstar.example/manuals/ns-200",
                        "section": "Specifications",
                        "anchor": "display",
                        "source_hash": "manualhash001",
                    }
                ],
            },
            "sku_source": {
                "created_at": "2026-05-06",
                "updated_at": "2026-05-06",
                "version": 1,
                "topics": ["field instruments", "electrical testing"],
                "slug": "ns-200-field-meter",
                "content_hash": "hash200field",
            },
            "buying_questions": [
                {
                    "id": "q-compat",
                    "question": "Is the NS 200 compatible with CAT III test leads?",
                    "intent": "compatibility",
                    "sku_ids": ["ns-200"],
                }
            ],
            "competitor_context": [
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
            ],
        },
        base_url="https://northstar.example",
    )


class SkuRenderTests(unittest.TestCase):
    def test_product_markdown_is_deterministic_and_claims_are_evidence_backed(self) -> None:
        passport = sample_passport()
        first = render_product_markdown(passport)
        second = render_product_markdown(passport)

        self.assertEqual(first, second)
        self.assertIn("# NS 200 Field Meter", first)
        self.assertIn("- Claim: The product includes a backlit LCD display.", first)
        self.assertIn("Evidence IDs: ev-display", first)
        self.assertIn("manualhash001", first)
        self.assertIn(passport.source_anchor, first)

    def test_product_markdown_does_not_render_extractor_only_notes(self) -> None:
        markdown = render_product_markdown(sample_passport())

        self.assertNotIn("Extractor-only note should not render.", markdown)
        self.assertNotIn("Extractor-only use case should not render.", markdown)
        self.assertNotIn("Extractor-only exclusion should not render.", markdown)
        self.assertNotIn("## Limitations", markdown)
        self.assertNotIn("## Use Cases", markdown)
        self.assertNotIn("## Not For", markdown)

    def test_product_pack_has_no_demo_or_hardcoded_sku(self) -> None:
        combined = "\n".join(
            [
                render_product_markdown(sample_passport()),
                render_product_index(sample_passport()),
                render_product_llms(sample_passport()),
                render_product_json(sample_passport()),
            ]
        ).lower()

        self.assertNotIn("anker", combined)
        self.assertNotIn("demo company", combined)
        self.assertNotIn("demo sku", combined)

    def test_product_json_is_machine_readable_and_sorted(self) -> None:
        rendered = render_product_json(sample_passport())
        data = json.loads(rendered)

        self.assertEqual(data["brand"]["id"], "northstar-tools")
        self.assertEqual(data["sku"]["claims"][0]["evidence_ids"], ["ev-display"])
        self.assertEqual(rendered, render_product_json(sample_passport()))

    def test_write_product_pack_outputs_ai_readable_files(self) -> None:
        passport = sample_passport()
        out_dir = ROOT / "generated" / "test-runs" / uuid.uuid4().hex
        paths = write_product_pack(passport, out_dir)
        rel_paths = {path.relative_to(out_dir).as_posix() for path in paths}

        self.assertEqual(
            rel_paths,
            {
                "ai/buying-guide.md",
                "ai/categories/field-instruments.md",
                "ai/comparisons/field-instruments.md",
                "ai/faq.md",
                "ai/product-index.md",
                "ai/products/ns-200-field-meter.md",
                "comparisons.json",
                "faq.json",
                "index.html",
                "llms-full.txt",
                "llms.txt",
                "robots.txt",
                "schema.json",
                "sitemap.xml",
                "sku-passport.json",
                "sku/ns-200-field-meter-hash200field/index.html",
                "sku/ns-200-field-meter-hash200field.md",
            },
        )
        self.assertIn(
            "Content hash: hash200field",
            (out_dir / "llms.txt").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "/ai/comparisons/field-instruments.md",
            (out_dir / "llms-full.txt").read_text(encoding="utf-8"),
        )

    def test_schema_faq_and_comparison_outputs_are_machine_readable(self) -> None:
        passport = sample_passport()
        schema = render_schema(passport)
        faq = json.loads(render_faq_json(passport))
        comparisons = json.loads(render_comparison_json(passport))

        graph_types = {
            item["@type"]
            for item in schema["@graph"]
            if isinstance(item, dict) and "@type" in item
        }
        self.assertIn("Product", graph_types)
        self.assertIn("FAQPage", graph_types)
        product = next(item for item in schema["@graph"] if item["@type"] == "Product")
        self.assertEqual(product["name"], "NS 200 Field Meter")
        self.assertEqual(product["brand"], {"@id": "https://northstar.example/#brand"})
        self.assertNotIn("offers", product)
        self.assertEqual(faq["items"][0]["question"], "Is the NS 200 compatible with CAT III test leads?")
        self.assertEqual(comparisons["items"][0]["context_id"], "ctx-meter")
        self.assertEqual(comparisons["items"][0]["avoid_claims"], ["Do not claim lower price."])

    def test_creator_workflow_renderer_still_uses_creator_passport(self) -> None:
        passport = load_passport(str(ROOT / "examples" / "source_passport.json"))
        rendered = render_source_markdown(passport)

        self.assertIn("## Claim-evidence map", rendered)
        self.assertIn(passport.source_anchor, rendered)


if __name__ == "__main__":
    unittest.main()
