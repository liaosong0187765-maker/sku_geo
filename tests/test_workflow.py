from __future__ import annotations

import json
from pathlib import Path
import sys
import uuid
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.__main__ import main
from creator_passport.models import load_passport
from creator_passport.monitor import evaluate_response


SAMPLE = ROOT / "examples" / "source_passport.json"


class SourcePassportWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = ROOT / "generated" / "test-runs" / uuid.uuid4().hex

    def test_generate_writes_minimum_closed_loop_files(self) -> None:
        exit_code = main(["generate", str(SAMPLE), "--out", str(self.tmp)])
        self.assertEqual(exit_code, 0)
        passport = json.loads((self.tmp / "passport.json").read_text(encoding="utf-8"))
        source = passport["source"]
        expected = [
            "index.html",
            f"s/{source['slug']}-{source['content_hash']}/index.html",
            f"s/{source['slug']}-{source['content_hash']}.md",
            "llms.txt",
            "llms-full.txt",
            "ai/index.md",
            "ai/profile.md",
            f"ai/sources/{source['slug']}.md",
            "schema.json",
            "sitemap.xml",
            "robots.txt",
            "variants/x.md",
            "variants/linkedin.md",
            "variants/wechat.md",
            "variants/zhihu.md",
        ]
        for rel in expected:
            self.assertTrue((self.tmp / rel).exists(), rel)
        self.assertIn(source["canonical_url"], source["recommended_citation"])

    def test_variants_include_visible_source_anchor(self) -> None:
        self.assertEqual(main(["generate", str(SAMPLE), "--out", str(self.tmp)]), 0)
        passport = json.loads((self.tmp / "passport.json").read_text(encoding="utf-8"))
        canonical_url = passport["source"]["canonical_url"]
        content_hash = passport["source"]["content_hash"]
        for platform in ["x", "linkedin", "wechat", "zhihu"]:
            content = (self.tmp / "variants" / f"{platform}.md").read_text(encoding="utf-8")
            self.assertIn("Source Passport:", content)
            self.assertIn("Source:", content)
            self.assertIn(canonical_url, content)
            self.assertIn(content_hash, content)

    def test_publish_saves_manual_platform_url(self) -> None:
        self.assertEqual(main(["generate", str(SAMPLE), "--out", str(self.tmp)]), 0)
        exit_code = main(["publish", "--out", str(self.tmp), "--platform", "x", "--url", "https://x.com/example/status/123"])
        self.assertEqual(exit_code, 0)
        data = json.loads((self.tmp / "publications.json").read_text(encoding="utf-8"))
        self.assertEqual(data["publications"][0]["platform"], "x")
        self.assertTrue(data["publications"][0]["anchor_present"])

    def test_monitor_outputs_revision_suggestions_when_source_is_missing(self) -> None:
        self.assertEqual(main(["generate", str(SAMPLE), "--out", str(self.tmp)]), 0)
        exit_code = main([
            "monitor",
            "--out",
            str(self.tmp),
            "--response-file",
            str(ROOT / "examples" / "monitor_response_missing_citation.txt"),
        ])
        self.assertEqual(exit_code, 0)
        report = (self.tmp / "monitor" / "report.md").read_text(encoding="utf-8")
        latest_run = json.loads((self.tmp / "monitor" / "latest-run.json").read_text(encoding="utf-8"))
        suggestions = (self.tmp / "revision_suggestions.md").read_text(encoding="utf-8")
        self.assertIn("Canonical source URL cited | no", report)
        self.assertIn("Claim coverage", report)
        self.assertIn("claim_coverage", latest_run["result"])
        self.assertIn("direct citation block", suggestions)

    def test_monitor_scores_canonical_citation(self) -> None:
        passport = load_passport(str(SAMPLE))
        response = f"Lin Source Lab argues this in {passport.canonical_url} with hash {passport.content_hash}. A canonical source page is more durable than a platform post."
        result = evaluate_response(passport, passport.monitor_prompts[0], response, [])
        self.assertTrue(result.creator_mentioned)
        self.assertTrue(result.source_url_cited)
        self.assertGreater(result.claim_coverage, 0)
        self.assertGreaterEqual(result.attribution_score, 75)

    def test_base_url_controls_canonical_sitemap_and_robots(self) -> None:
        base_url = "http://127.0.0.1:8765"
        self.assertEqual(main(["generate", str(SAMPLE), "--out", str(self.tmp), "--base-url", base_url]), 0)
        passport = json.loads((self.tmp / "passport.json").read_text(encoding="utf-8"))
        self.assertTrue(passport["source"]["canonical_url"].startswith(base_url))
        self.assertIn(f"{base_url}/sitemap.xml", (self.tmp / "robots.txt").read_text(encoding="utf-8"))
        self.assertIn(f"{base_url}/ai/index.md", (self.tmp / "sitemap.xml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
