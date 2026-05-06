from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.intake import ORIGIN_MANUAL_MARKDOWN
from creator_passport.sku_adapters import (
    AdapterConversionError,
    AdapterUnavailableError,
    convert_local_file_with_markitdown,
    convert_url_with_crawl4ai,
    crawl4ai_available,
    markitdown_available,
)
from creator_passport.variants import render_variants
from creator_passport.models import SourcePassport


def temporary_source_dir() -> Path:
    temp_root = ROOT / "generated" / "test-runs"
    temp_path = temp_root / uuid.uuid4().hex
    temp_path.mkdir(parents=True, exist_ok=True)
    return temp_path


class FakeMarkItDown:
    def __init__(self, markdown: str) -> None:
        self.markdown = markdown
        self.paths: list[str] = []

    def convert_local(self, path: str) -> SimpleNamespace:
        self.paths.append(path)
        return SimpleNamespace(text_content=self.markdown)


class FakeCrawl4AI:
    def __init__(self, result: object) -> None:
        self.result = result
        self.calls: list[tuple[str, dict[str, object]]] = []

    def arun(self, url: str, **kwargs: object) -> object:
        self.calls.append((url, kwargs))
        return self.result


class AsyncFakeCrawl4AI(FakeCrawl4AI):
    async def arun(self, url: str, **kwargs: object) -> object:
        self.calls.append((url, kwargs))
        return self.result


class AsyncContextFakeCrawl4AI(AsyncFakeCrawl4AI):
    def __init__(self, result: object) -> None:
        super().__init__(result)
        self.entered = False
        self.exited = False

    async def __aenter__(self) -> "AsyncContextFakeCrawl4AI":
        self.entered = True
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.exited = True


class SkuAdapterTests(unittest.TestCase):
    def test_dependency_missing_behavior_is_project_local(self) -> None:
        with patch("creator_passport.sku_adapters.importlib.import_module") as import_module:
            import_module.side_effect = ModuleNotFoundError("missing")

            self.assertFalse(markitdown_available())
            self.assertFalse(crawl4ai_available())
            with self.assertRaisesRegex(AdapterUnavailableError, "MarkItDown is not installed"):
                convert_local_file_with_markitdown("source.pdf")
            with self.assertRaisesRegex(AdapterUnavailableError, "Crawl4AI is not installed"):
                convert_url_with_crawl4ai("https://official.example/source")

    def test_dependency_module_without_exports_is_reported(self) -> None:
        def fake_import(name: str) -> object:
            if name in {"markitdown", "crawl4ai"}:
                return SimpleNamespace()
            raise ModuleNotFoundError(name)

        with patch("creator_passport.sku_adapters.importlib.import_module", side_effect=fake_import):
            self.assertTrue(markitdown_available())
            self.assertTrue(crawl4ai_available())
            with self.assertRaisesRegex(AdapterUnavailableError, "does not expose MarkItDown"):
                convert_local_file_with_markitdown(
                    "source.pdf",
                    approved_roots=[ROOT],
                    allow_external_source=True,
                )
            with self.assertRaisesRegex(AdapterUnavailableError, "does not expose AsyncWebCrawler"):
                convert_url_with_crawl4ai("https://official.example/source")

    def test_fake_markitdown_conversion_returns_intake_document(self) -> None:
        tmp_path = temporary_source_dir()
        source_path = tmp_path / "spec-sheet.pdf"
        source_path.write_text("binary placeholder", encoding="utf-8")
        markdown = (
            "# Product Source\n\n"
            "Summary: Compact accessory for a supported host device.\n"
            "Model Number: PX-100\n"
            "Claim: Supports USB-C host devices."
        )
        fake = FakeMarkItDown(markdown)

        result = convert_local_file_with_markitdown(
            source_path,
            approved_roots=[tmp_path],
            title="Spec Sheet",
            captured_at="2026-02-01T00:00:00Z",
            metadata={"owner": "sku"},
            converter_factory=lambda: fake,
        )

        self.assertEqual(result.adapter, "markitdown")
        self.assertEqual(result.source_kind, "local_file")
        self.assertEqual(result.document.origin_type, ORIGIN_MANUAL_MARKDOWN)
        self.assertEqual(result.document.title, "Spec Sheet")
        self.assertEqual(result.document.raw_markdown, markdown)
        self.assertEqual(result.document.file_path, "")
        self.assertEqual(result.document.metadata["adapter"], "markitdown")
        self.assertEqual(result.document.metadata["owner"], "sku")
        self.assertEqual(result.document.metadata["original_file_path"], str(source_path.resolve()))
        self.assertEqual(fake.paths, [str(source_path.resolve())])

    def test_fake_markitdown_output_feeds_sku_passport_parts(self) -> None:
        from creator_passport.sku_extract import extract_passport_parts

        tmp_path = temporary_source_dir()
        source_path = tmp_path / "product.docx"
        source_path.write_text("placeholder", encoding="utf-8")
        fake = FakeMarkItDown(
            "\n".join(
                [
                    "Summary: Durable product for documented setup workflows.",
                    "Category: Work accessory",
                    "Model Number: WK-200",
                    "Compatibility: USB-C laptops",
                    "Warranty: Two-year limited warranty",
                    "Claim: Includes a documented USB-C compatibility statement.",
                ]
            )
        )

        result = convert_local_file_with_markitdown(
            source_path,
            approved_roots=[tmp_path],
            converter_factory=lambda: fake,
        )
        parts = extract_passport_parts(result.document)

        self.assertEqual(parts["facts"]["summary"], "Durable product for documented setup workflows.")
        self.assertEqual(parts["facts"]["compatibility"], ["USB-C laptops"])
        self.assertEqual(parts["facts"]["warranty"], ["Two-year limited warranty"])
        self.assertEqual(len(parts["claims"]), 1)
        self.assertTrue(parts["evidence"])
        self.assertEqual(parts["source_hash"], result.document.content_hash)

    def test_markitdown_rejects_traversal_and_external_without_reading(self) -> None:
        tmp_path = temporary_source_dir()
        approved = tmp_path / "approved"
        outside = tmp_path / "outside"
        external = tmp_path / "external"
        approved.mkdir()
        outside.mkdir()
        external.mkdir()

        with self.assertRaisesRegex(ValueError, "outside approved roots"):
            convert_local_file_with_markitdown(
                approved / ".." / "outside" / "source.pdf",
                approved_roots=[approved],
                converter_factory=lambda: FakeMarkItDown("never"),
            )
        with self.assertRaisesRegex(ValueError, "inside external/"):
            convert_local_file_with_markitdown(
                external / "source.pdf",
                approved_roots=[tmp_path],
                converter_factory=lambda: FakeMarkItDown("never"),
            )

    def test_external_file_can_be_allowed_explicitly_for_adapter_boundary(self) -> None:
        tmp_path = temporary_source_dir()
        external = tmp_path / "external"
        external.mkdir()
        source_path = external / "reference.pdf"
        source_path.write_text("placeholder", encoding="utf-8")

        result = convert_local_file_with_markitdown(
            source_path,
            approved_roots=[tmp_path],
            allow_external_source=True,
            converter_factory=lambda: FakeMarkItDown("Summary: Allowed explicit source."),
        )

        self.assertEqual(result.document.raw_markdown, "Summary: Allowed explicit source.")

    def test_fake_crawl4ai_conversion_returns_intake_document(self) -> None:
        fake = FakeCrawl4AI(
            SimpleNamespace(
                markdown="Summary: Official page facts.\nClaim: Official source supports this fact.",
                metadata={"title": "Official Product Page"},
            )
        )

        result = convert_url_with_crawl4ai(
            "https://official.example/product",
            captured_at="2026-02-02T00:00:00Z",
            crawler_factory=lambda: fake,
            crawl_kwargs={"only_main_content": True},
        )

        self.assertEqual(result.adapter, "crawl4ai")
        self.assertEqual(result.document.origin_type, ORIGIN_MANUAL_MARKDOWN)
        self.assertEqual(result.document.title, "Official Product Page")
        self.assertEqual(result.document.origin_url, "https://official.example/product")
        self.assertIn("Official page facts", result.document.raw_markdown)
        self.assertEqual(fake.calls, [("https://official.example/product", {"only_main_content": True})])

    def test_crawl4ai_rejects_invalid_url_before_crawler_invocation(self) -> None:
        fake = FakeCrawl4AI(SimpleNamespace(markdown="never"))

        with self.assertRaisesRegex(ValueError, "http or https"):
            convert_url_with_crawl4ai(
                "file:///etc/passwd",
                crawler_factory=lambda: fake,
            )
        with self.assertRaisesRegex(ValueError, "include a host"):
            convert_url_with_crawl4ai(
                "https:///missing-host",
                crawler_factory=lambda: fake,
            )

        self.assertEqual(fake.calls, [])

    def test_crawl4ai_rejects_private_url_before_crawler_invocation(self) -> None:
        fake = FakeCrawl4AI(SimpleNamespace(markdown="never"))

        for url in [
            "http://localhost/source",
            "http://127.0.0.1/source",
            "http://10.0.0.5/source",
            "http://169.254.169.254/latest/meta-data",
            "http://[::1]/source",
        ]:
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "private"):
                    convert_url_with_crawl4ai(url, crawler_factory=lambda: fake)

        self.assertEqual(fake.calls, [])

    def test_crawl4ai_private_url_requires_explicit_opt_in(self) -> None:
        fake = FakeCrawl4AI(SimpleNamespace(markdown="Summary: Local source."))

        result = convert_url_with_crawl4ai(
            "http://127.0.0.1/source",
            allow_private_network=True,
            crawler_factory=lambda: fake,
        )

        self.assertEqual(result.document.origin_url, "http://127.0.0.1/source")
        self.assertEqual(fake.calls, [("http://127.0.0.1/source", {})])

    def test_crawl4ai_allowed_domains_rejects_unapproved_host_without_crawling(self) -> None:
        fake = FakeCrawl4AI(SimpleNamespace(markdown="never"))

        with self.assertRaisesRegex(ValueError, "outside allowed domains"):
            convert_url_with_crawl4ai(
                "https://attacker.example/source",
                allowed_domains=["official.example"],
                crawler_factory=lambda: fake,
            )

        self.assertEqual(fake.calls, [])

    def test_crawl4ai_allowed_domains_accepts_subdomain(self) -> None:
        fake = FakeCrawl4AI(SimpleNamespace(markdown="Summary: Official subdomain."))

        result = convert_url_with_crawl4ai(
            "https://docs.official.example/source",
            allowed_domains=["official.example"],
            crawler_factory=lambda: fake,
        )

        self.assertEqual(result.document.origin_url, "https://docs.official.example/source")
        self.assertEqual(fake.calls, [("https://docs.official.example/source", {})])

    def test_async_fake_crawl4ai_conversion_is_resolved_without_network(self) -> None:
        fake = AsyncFakeCrawl4AI(SimpleNamespace(markdown="Summary: Async crawled facts."))

        result = convert_url_with_crawl4ai(
            "https://official.example/async",
            crawler_factory=lambda: fake,
        )

        self.assertEqual(result.document.raw_markdown, "Summary: Async crawled facts.")

    def test_async_context_crawl4ai_conversion_enters_crawler(self) -> None:
        fake = AsyncContextFakeCrawl4AI(SimpleNamespace(markdown="Summary: Context facts."))

        result = convert_url_with_crawl4ai(
            "https://official.example/context",
            crawler_factory=lambda: fake,
        )

        self.assertEqual(result.document.raw_markdown, "Summary: Context facts.")
        self.assertTrue(fake.entered)
        self.assertTrue(fake.exited)

    def test_async_crawl4ai_inside_running_loop_is_explicitly_rejected(self) -> None:
        async def run_case() -> None:
            fake = AsyncFakeCrawl4AI(SimpleNamespace(markdown="Summary: Async facts."))
            with self.assertRaisesRegex(AdapterConversionError, "event loop is already running"):
                convert_url_with_crawl4ai(
                    "https://official.example/async",
                    crawler_factory=lambda: fake,
                )

        asyncio.run(run_case())

    def test_creator_variant_workflow_still_generates_source_anchor(self) -> None:
        passport = SourcePassport.from_dict(
            {
                "creator": {
                    "name": "Creator",
                    "bio": "Source owner.",
                    "domain": "https://source.example",
                },
                "source": {
                    "title": "Creator Source",
                    "thesis": "Creator-owned source pages preserve attribution.",
                    "body": "The source note body explains the idea.",
                    "topics": ["source"],
                    "claims": [
                        {
                            "claim": "Source pages preserve attribution.",
                            "evidence": "The canonical URL and hash are included.",
                        }
                    ],
                    "canonical_url": "https://source.example/p/creator",
                    "created_at": "2026-02-03T00:00:00Z",
                    "updated_at": "2026-02-03T00:00:00Z",
                },
            }
        )

        variants = render_variants(passport)

        self.assertIn(passport.source_anchor, variants["x"])
        self.assertIn(passport.source_anchor, variants["linkedin"])


if __name__ == "__main__":
    unittest.main()
