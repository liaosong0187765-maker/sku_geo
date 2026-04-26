import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from geo_builder import main
from geo_core.generator import render_schema
from geo_core.importer import FetchResult, build_draft_core, build_merged_draft_core
from geo_core.model import KnowledgeCore
from geo_core.scoring import score


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "sample_company.json"


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_cli_generates_expected_files(self):
        exit_code = main([str(SAMPLE), "--out", str(self.tmp)])
        self.assertEqual(exit_code, 0)
        expected = [
            "knowledge-core.json",
            "llms.txt",
            "llms-full.txt",
            "ai/company.md",
            "ai/products.md",
            "ai/faq.md",
            "schema.json",
            "site/index.html",
            "site/product.html",
            "site/faq.html",
            "report.md",
        ]
        for rel in expected:
            self.assertTrue((self.tmp / rel).exists(), rel)

    def test_schema_contains_organization_product_and_faq(self):
        data = json.loads(SAMPLE.read_text(encoding="utf-8"))
        core = KnowledgeCore.from_dict(data)
        schema = render_schema(core)
        types = [node.get("@type") for node in schema["@graph"]]
        self.assertIn("Organization", types)
        self.assertIn("Product", types)
        self.assertIn("FAQPage", types)
        faq = next(node for node in schema["@graph"] if node.get("@type") == "FAQPage")
        self.assertGreaterEqual(len(faq["mainEntity"]), 5)

    def test_score_and_report_include_claim_evidence(self):
        exit_code = main([str(SAMPLE), "--out", str(self.tmp)])
        self.assertEqual(exit_code, 0)
        report = (self.tmp / "report.md").read_text(encoding="utf-8")
        self.assertIn("Overall score", report)
        self.assertIn("Claim-Evidence Map", report)
        self.assertIn("HarborAI Sales is designed for B2B export companies", report)
        data = json.loads(SAMPLE.read_text(encoding="utf-8"))
        core = KnowledgeCore.from_dict(data)
        total, dimensions, missing = score(core)
        self.assertGreaterEqual(total, 80)
        self.assertIn("entity_clarity", dimensions)

    def test_build_draft_core_from_fetch_result(self):
        fetched = FetchResult(
            title="Example Domain",
            url="https://example.com/",
            content="# Example Domain\n\nExample Domain is for use in documentation examples without needing permission.\n\n- Clean example page\n- Useful for docs\n- Publicly accessible\n",
        )
        core_dict = build_draft_core(fetched)
        core = KnowledgeCore.from_dict(core_dict)
        self.assertEqual(core.name, "Example Domain")
        self.assertEqual(core.url, "https://example.com/")
        self.assertGreaterEqual(len(core.questions), 5)
        self.assertGreaterEqual(len(core.claims), 3)
        self.assertTrue(core.products[0].features)

    def test_build_merged_draft_core_from_multiple_fetch_results(self):
        fetched_items = [
            FetchResult(
                title="Example Domain",
                url="https://example.com/",
                content="# Example Domain\n\nExample Domain is for use in documentation examples without needing permission.\n\n- Publicly accessible\n- Documentation use\n",
            ),
            FetchResult(
                title="Example Domain Pricing",
                url="https://example.com/pricing",
                content="# Example Domain Pricing\n\nPricing starts at $19 for sample usage.\n\n- Pricing page\n- Commercial details\n",
            ),
        ]
        core_dict = build_merged_draft_core(fetched_items)
        core = KnowledgeCore.from_dict(core_dict)
        self.assertEqual(core.url, "https://example.com/")
        self.assertGreaterEqual(len(core.sources), 4)
        self.assertGreaterEqual(len(core.questions), 5)
        self.assertIn("page_count", core.raw["import_context"])
        self.assertEqual(core.raw["import_context"]["page_count"], 2)

    @patch("geo_builder.fetch_urls")
    def test_cli_can_import_url_with_camoufox_fetch(self, mock_fetch):
        mock_fetch.return_value = [
            FetchResult(
                title="Example Domain",
                url="https://example.com/",
                content="# Example Domain\n\nExample Domain is for use in documentation examples without needing permission.\n\n- Clean example page\n- Useful for docs\n- Publicly accessible\n",
            )
        ]
        exit_code = main(["--url", "https://example.com", "--out", str(self.tmp)])
        self.assertEqual(exit_code, 0)
        self.assertTrue((self.tmp / "source" / "page-01-example-domain.md").exists())
        self.assertTrue((self.tmp / "source" / "page-01-example-domain.json").exists())
        self.assertTrue((self.tmp / "source" / "manifest.json").exists())
        self.assertTrue((self.tmp / "knowledge-core.json").exists())
        report = (self.tmp / "report.md").read_text(encoding="utf-8")
        self.assertIn("Example Domain", report)

    @patch("geo_builder.fetch_urls")
    def test_cli_can_merge_multiple_urls(self, mock_fetch):
        mock_fetch.return_value = [
            FetchResult(
                title="Example Domain",
                url="https://example.com/",
                content="# Example Domain\n\nExample Domain is for use in documentation examples without needing permission.\n\n- Publicly accessible\n",
            ),
            FetchResult(
                title="Example Domain FAQ",
                url="https://example.com/faq",
                content="# Example Domain FAQ\n\nFrequently asked questions about example usage.\n\n- FAQ content\n- Support answers\n",
            ),
        ]
        exit_code = main([
            "--url", "https://example.com",
            "--url", "https://example.com/faq",
            "--out", str(self.tmp),
        ])
        self.assertEqual(exit_code, 0)
        manifest = json.loads((self.tmp / "source" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["pages"]), 2)
        knowledge_core = json.loads((self.tmp / "knowledge-core.json").read_text(encoding="utf-8"))
        self.assertEqual(knowledge_core["import_context"]["page_count"], 2)
        self.assertEqual(len(knowledge_core["import_context"]["urls"]), 2)


if __name__ == "__main__":
    unittest.main()
