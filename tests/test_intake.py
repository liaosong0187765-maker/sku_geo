from __future__ import annotations

from pathlib import Path
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.intake import (
    ORIGIN_LOCAL_FILE,
    ORIGIN_MANUAL_MARKDOWN,
    RawSourceDocument,
    compute_source_hash,
    is_supported_source_path,
    load_raw_source,
)


def temporary_source_dir() -> Path:
    temp_root = ROOT / "generated" / "test-runs"
    temp_path = temp_root / uuid.uuid4().hex
    temp_path.mkdir(parents=True, exist_ok=True)
    return temp_path


class RawSourceDocumentTests(unittest.TestCase):
    def test_manual_markdown_constructor_finalizes_identity_and_preserves_context(self) -> None:
        raw_markdown = "# Source note\n\nA durable source paragraph."

        document = RawSourceDocument.from_manual_markdown(
            raw_markdown,
            title=" Source Note ",
            origin_url=" https://source.test/note ",
            captured_at="2026-01-01T00:00:00Z",
            metadata={"channel": "manual", "rank": 1},
            warnings=["needs follow-up"],
        )

        self.assertEqual(document.origin_type, ORIGIN_MANUAL_MARKDOWN)
        self.assertEqual(document.title, "Source Note")
        self.assertEqual(document.origin_url, "https://source.test/note")
        self.assertEqual(document.raw_markdown, raw_markdown)
        self.assertEqual(document.captured_at, "2026-01-01T00:00:00Z")
        self.assertEqual(document.content_hash, compute_source_hash(raw_markdown))
        self.assertEqual(document.id, f"source-note-{document.content_hash}")
        self.assertEqual(document.metadata, {"channel": "manual", "rank": 1})
        self.assertEqual(document.warnings, ["needs follow-up"])

    def test_from_dict_to_dict_roundtrips_without_losing_metadata_or_warnings(self) -> None:
        raw_markdown = "## Imported\n\nRoundtrip source content."
        data = {
            "id": "custom-source-id",
            "origin_type": ORIGIN_MANUAL_MARKDOWN,
            "title": "Imported Source",
            "raw_markdown": raw_markdown,
            "origin_url": "https://source.test/imported",
            "captured_at": "2026-01-02T00:00:00Z",
            "content_hash": compute_source_hash(raw_markdown),
            "warnings": ["minor formatting issue"],
            "metadata": {"owner": "intake", "nested": {"kept": True}},
        }

        document = RawSourceDocument.from_dict(data)
        serialized = document.to_dict()
        roundtrip = RawSourceDocument.from_dict(serialized)

        self.assertEqual(serialized, {**data, "file_path": ""})
        self.assertEqual(roundtrip.to_dict(), serialized)

    def test_content_hash_is_stable_and_changes_only_with_raw_markdown(self) -> None:
        content = "Stable source content."
        same_content = RawSourceDocument.from_manual_markdown(
            content,
            title="First title",
            captured_at="2026-01-03T00:00:00Z",
        )
        different_title = RawSourceDocument.from_manual_markdown(
            content,
            title="Second title",
            captured_at="2026-01-03T00:00:00Z",
        )
        changed_content = RawSourceDocument.from_manual_markdown(
            content + " Changed.",
            title="First title",
            captured_at="2026-01-03T00:00:00Z",
        )

        self.assertEqual(same_content.content_hash, different_title.content_hash)
        self.assertEqual(same_content.content_hash, compute_source_hash(content))
        self.assertNotEqual(same_content.content_hash, changed_content.content_hash)

    def test_local_utf8_markdown_and_text_files_are_loaded(self) -> None:
        tmp_path = temporary_source_dir()
        md_path = tmp_path / "source.md"
        txt_path = tmp_path / "brief.txt"
        md_path.write_text("# 标题\n\nUTF-8 markdown body.", encoding="utf-8")
        txt_path.write_text("Plain UTF-8 text: 来源说明", encoding="utf-8")

        markdown = RawSourceDocument.from_local_file(md_path, captured_at="2026-01-04T00:00:00Z")
        text = load_raw_source(txt_path, title="Text Brief", captured_at="2026-01-04T00:00:00Z")

        self.assertEqual(markdown.origin_type, ORIGIN_LOCAL_FILE)
        self.assertEqual(markdown.title, "source")
        self.assertEqual(markdown.raw_markdown, "# 标题\n\nUTF-8 markdown body.")
        self.assertEqual(markdown.file_path, str(md_path))
        self.assertEqual(markdown.content_hash, compute_source_hash(markdown.raw_markdown))
        self.assertEqual(text.title, "Text Brief")
        self.assertEqual(text.raw_markdown, "Plain UTF-8 text: 来源说明")
        self.assertTrue(is_supported_source_path(md_path))
        self.assertTrue(is_supported_source_path(txt_path))

    def test_unsupported_extension_is_rejected(self) -> None:
        source_path = temporary_source_dir() / "source.pdf"
        source_path.write_text("Not an accepted source file.", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, r"Unsupported source file extension: \.pdf"):
            RawSourceDocument.from_local_file(source_path)

        self.assertFalse(is_supported_source_path("source.pdf"))

    def test_missing_required_fields_are_rejected(self) -> None:
        cases = [
            ("title", {"title": ""}),
            ("raw_markdown", {"raw_markdown": ""}),
            ("origin_type", {"origin_type": ""}),
            ("file_path", {"origin_type": ORIGIN_LOCAL_FILE, "file_path": ""}),
        ]

        base = {
            "id": "valid-id",
            "origin_type": ORIGIN_MANUAL_MARKDOWN,
            "title": "Valid Title",
            "raw_markdown": "Valid body.",
            "captured_at": "2026-01-05T00:00:00Z",
            "content_hash": compute_source_hash("Valid body."),
        }

        for expected, patch in cases:
            data = {**base, **patch}
            if "raw_markdown" in patch:
                data["content_hash"] = compute_source_hash(data["raw_markdown"])
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(ValueError, expected):
                    RawSourceDocument.from_dict(data)

    def test_from_dict_normalizes_metadata_and_warnings(self) -> None:
        raw_markdown = "Source content with warnings."
        document = RawSourceDocument.from_dict(
            {
                "origin_type": ORIGIN_MANUAL_MARKDOWN,
                "title": "Warning Source",
                "raw_markdown": raw_markdown,
                "captured_at": "2026-01-06T00:00:00Z",
                "warnings": ["kept", "", None],
                "metadata": {"": "dropped", "kept": "value"},
            }
        )

        self.assertEqual(document.warnings, ["kept"])
        self.assertEqual(document.metadata, {"kept": "value"})

    def test_from_dict_strict_rejects_missing_identity_but_default_fills_it(self) -> None:
        raw_markdown = "Convenient imported content."
        data = {
            "origin_type": ORIGIN_MANUAL_MARKDOWN,
            "title": "Imported Draft",
            "raw_markdown": raw_markdown,
        }

        with self.assertRaisesRegex(ValueError, "id"):
            RawSourceDocument.from_dict(data, strict=True)

        document = RawSourceDocument.from_dict(data)

        self.assertEqual(document.content_hash, compute_source_hash(raw_markdown))
        self.assertTrue(document.id.startswith("imported-draft-"))
        self.assertTrue(document.captured_at)

    def test_from_dict_strict_rejects_unknown_keys(self) -> None:
        raw_markdown = "Strict imported content."
        data = {
            "id": "strict-source",
            "origin_type": ORIGIN_MANUAL_MARKDOWN,
            "title": "Strict Source",
            "raw_markdown": raw_markdown,
            "captured_at": "2026-01-06T00:00:00Z",
            "content_hash": compute_source_hash(raw_markdown),
            "html": "<p>derived</p>",
            "source_type": "markdown",
            "adapter_payload": {"ignored": True},
        }

        with self.assertRaisesRegex(
            ValueError,
            r"Unknown fields: adapter_payload, html, source_type",
        ):
            RawSourceDocument.from_dict(data, strict=True)

    def test_from_dict_default_ignores_unknown_keys(self) -> None:
        raw_markdown = "Convenient imported content with adapter data."
        document = RawSourceDocument.from_dict(
            {
                "origin_type": ORIGIN_MANUAL_MARKDOWN,
                "title": "Adapter Draft",
                "raw_markdown": raw_markdown,
                "html": "<p>derived</p>",
                "source_type": "markdown",
                "adapter_payload": {"ignored": True},
            }
        )

        self.assertEqual(document.title, "Adapter Draft")
        self.assertEqual(document.raw_markdown, raw_markdown)
        self.assertEqual(document.content_hash, compute_source_hash(raw_markdown))

    def test_content_hash_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "content_hash does not match raw_markdown"):
            RawSourceDocument.from_dict(
                {
                    "id": "bad-hash",
                    "origin_type": ORIGIN_MANUAL_MARKDOWN,
                    "title": "Bad Hash",
                    "raw_markdown": "Actual content.",
                    "captured_at": "2026-01-07T00:00:00Z",
                    "content_hash": "wronghash",
                }
            )

    def test_unsupported_origin_type_is_rejected(self) -> None:
        raw_markdown = "Valid body."

        with self.assertRaisesRegex(ValueError, "Unsupported origin_type: url"):
            RawSourceDocument.from_dict(
                {
                    "id": "url-source",
                    "origin_type": "url",
                    "title": "URL Source",
                    "raw_markdown": raw_markdown,
                    "captured_at": "2026-01-08T00:00:00Z",
                    "content_hash": compute_source_hash(raw_markdown),
                }
            )

    def test_invalid_utf8_local_file_is_rejected(self) -> None:
        source_path = temporary_source_dir() / "source.md"
        source_path.write_bytes(b"\xff\xfe\x00")

        with self.assertRaises(UnicodeDecodeError):
            RawSourceDocument.from_local_file(source_path)

    def test_uppercase_supported_extension_is_loaded(self) -> None:
        source_path = temporary_source_dir() / "SOURCE.MD"
        source_path.write_text("# Uppercase extension", encoding="utf-8")

        document = RawSourceDocument.from_local_file(source_path)

        self.assertEqual(document.raw_markdown, "# Uppercase extension")
        self.assertTrue(is_supported_source_path(source_path))

    def test_local_file_outside_approved_root_is_rejected_before_reading(self) -> None:
        tmp_path = temporary_source_dir()
        approved_root = tmp_path / "approved"
        outside_root = tmp_path / "outside"
        approved_root.mkdir()
        outside_root.mkdir()
        source_path = outside_root / "source.md"
        source_path.write_text("Outside approved root.", encoding="utf-8")
        traversal_path = approved_root / ".." / "outside" / "source.md"

        with self.assertRaisesRegex(ValueError, "outside approved roots"):
            RawSourceDocument.from_local_file(traversal_path, approved_roots=[approved_root])

    def test_external_path_inside_approved_root_is_rejected_before_reading(self) -> None:
        tmp_path = temporary_source_dir()
        external_root = tmp_path / "external"
        external_root.mkdir()
        source_path = external_root / "source.md"
        source_path.write_text("External reference content.", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "inside external/"):
            RawSourceDocument.from_local_file(source_path, approved_roots=[tmp_path])

    def test_external_path_is_rejected_when_external_root_is_approved(self) -> None:
        tmp_path = temporary_source_dir()
        external_root = tmp_path / "external"
        external_root.mkdir()
        source_path = external_root / "source.md"
        source_path.write_text("External root approved.", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "inside external/"):
            RawSourceDocument.from_local_file(source_path, approved_roots=[external_root])

    def test_external_path_is_rejected_when_external_subdir_is_approved(self) -> None:
        tmp_path = temporary_source_dir()
        approved_root = tmp_path / "External" / "approved"
        approved_root.mkdir(parents=True)
        source_path = approved_root / "source.md"
        source_path.write_text("External subdir approved.", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "inside external/"):
            RawSourceDocument.from_local_file(source_path, approved_roots=[approved_root])


if __name__ == "__main__":
    unittest.main()
