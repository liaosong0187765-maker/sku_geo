from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from creator_passport.intake import RawSourceDocument
from creator_passport.sku_extract import extract_sku_facts


CAPTURED_AT = "2026-03-01T00:00:00Z"


def manual_document(raw_markdown: str, *, title: str = "SKU Source") -> RawSourceDocument:
    return RawSourceDocument.from_manual_markdown(
        raw_markdown,
        title=title,
        origin_url="https://example.test/sku-source",
        captured_at=CAPTURED_AT,
    )


class SkuExtractTests(unittest.TestCase):
    def test_explicit_labels_headings_bullets_and_key_values_extract_all_supported_fields(self) -> None:
        raw_markdown = """# Source Note

Marketing: Built for teams who want effortless growth.
Summary: Compact Matter bridge for apartment-scale smart-home installs.

## Key Specs
- Model: Hub Mini S1
- Wireless: Thread border router
- Ports: USB-C upstream
- Power: 5V DC, 2A

## Compatibility
- iOS 17 Home app
- Android 14 app

## Requirements
- 2.4 GHz Wi-Fi

## Certifications
- FCC
- Matter 1.2

## Protocols
- Matter
- Thread

## Ports
- Ethernet: 1x RJ45
- USB-C

## Power
- 5V DC input

## Warranty
- 2-year limited warranty

## Region Availability
- United States

## Limitations
- Indoor use only

## Use Cases
- Multi-room sensor onboarding

## Not For
- Outdoor installations

Claim: Reduces setup time by 30% in internal lab tests.
"""
        document = manual_document(raw_markdown)

        extracted = extract_sku_facts(document)
        facts = extracted.facts

        self.assertEqual(
            facts.summary,
            "Compact Matter bridge for apartment-scale smart-home installs.",
        )
        self.assertEqual(
            facts.key_specs,
            {
                "model": "Hub Mini S1",
                "wireless": "Thread border router",
                "ports": "USB-C upstream",
                "power": "5V DC, 2A",
            },
        )
        self.assertEqual(facts.compatibility, ["iOS 17 Home app", "Android 14 app"])
        self.assertEqual(facts.requirements, ["2.4 GHz Wi-Fi"])
        self.assertEqual(facts.certifications, ["FCC", "Matter 1.2"])
        self.assertEqual(facts.protocols, ["Matter", "Thread"])
        self.assertEqual(facts.ports, ["USB-C upstream", "Ethernet: 1x RJ45", "USB-C"])
        self.assertEqual(facts.power, ["5V DC, 2A", "5V DC input"])
        self.assertEqual(facts.warranty, ["2-year limited warranty"])
        self.assertEqual(facts.region_availability, ["United States"])
        self.assertEqual(extracted.limitations, ["Indoor use only"])
        self.assertEqual(extracted.use_cases, ["Multi-room sensor onboarding"])
        self.assertEqual(extracted.not_for, ["Outdoor installations"])
        self.assertEqual([claim.claim for claim in extracted.claims], [
            "Reduces setup time by 30% in internal lab tests."
        ])
        self.assertEqual(extracted.source_document_id, document.id)
        self.assertEqual(extracted.source_hash, document.content_hash)

        evidence_by_id = {item.id: item for item in extracted.evidence}
        self.assertTrue(evidence_by_id)
        self.assertTrue(all(item.source_hash == document.content_hash for item in extracted.evidence))
        self.assertIn(extracted.claims[0].evidence_ids[0], evidence_by_id)

    def test_claims_are_created_only_from_explicit_claim_labels_or_claims_section(self) -> None:
        raw_markdown = """# Product Copy

Fast setup for all teams.
Best-in-class range for every room.

## Claims
- Setup completes in under 3 minutes with QR onboarding.
Claims: Matter pairing succeeds on iOS and Android in QA matrix.
Claim: Reduces support tickets during pilot.

## Limitations
- Not compatible with outdoor sensors.
"""
        extracted = extract_sku_facts(manual_document(raw_markdown))

        self.assertEqual(
            [claim.claim for claim in extracted.claims],
            [
                "Setup completes in under 3 minutes with QR onboarding.",
                "Matter pairing succeeds on iOS and Android in QA matrix.",
                "Reduces support tickets during pilot.",
            ],
        )
        evidence_ids = {item.id for item in extracted.evidence}
        for claim in extracted.claims:
            self.assertEqual(len(claim.evidence_ids), 1)
            self.assertIn(claim.evidence_ids[0], evidence_ids)

        all_excerpts = [item.excerpt for item in extracted.evidence]
        self.assertNotIn("Fast setup for all teams.", all_excerpts)
        self.assertNotIn("Best-in-class range for every room.", all_excerpts)

    def test_unlabeled_marketing_copy_is_not_inferred_into_facts_or_claims(self) -> None:
        raw_markdown = """# Launch Copy

Built for modern homes with reliable setup.
Works beautifully with phones, hubs, and everyday routines.
Designed to make onboarding faster and simpler.
"""
        extracted = extract_sku_facts(manual_document(raw_markdown))

        self.assertEqual(extracted.facts.to_dict(), {
            "summary": "",
            "key_specs": {},
            "positioning": "",
            "materials": [],
            "dimensions": {},
            "included_items": [],
            "compatibility": [],
            "requirements": [],
            "certifications": [],
            "protocols": [],
            "ports": [],
            "power": [],
            "warranty": [],
            "region_availability": [],
        })
        self.assertEqual(extracted.evidence, [])
        self.assertEqual(extracted.claims, [])
        self.assertEqual(extracted.limitations, [])
        self.assertEqual(extracted.use_cases, [])
        self.assertEqual(extracted.not_for, [])

    def test_empty_like_no_label_document_returns_empty_result_without_exception(self) -> None:
        extracted = extract_sku_facts(manual_document(" \n\t\n"))

        self.assertEqual(extracted.facts.summary, "")
        self.assertEqual(extracted.facts.key_specs, {})
        self.assertEqual(extracted.evidence, [])
        self.assertEqual(extracted.claims, [])
        self.assertEqual(extracted.limitations, [])
        self.assertEqual(extracted.use_cases, [])
        self.assertEqual(extracted.not_for, [])

    def test_evidence_ids_source_hash_and_serialized_output_are_deterministic(self) -> None:
        raw_markdown = """Summary: Stable extraction target.

## Key Specs
- Model: Stable One
- Protocols: Matter

## Claims
- Battery lasts 12 months in standby tests.
"""
        first = extract_sku_facts(manual_document(raw_markdown, title="First Title"))
        second = extract_sku_facts(manual_document(raw_markdown, title="First Title"))
        same_content_different_title = extract_sku_facts(
            manual_document(raw_markdown, title="Different Title")
        )

        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(
            [item.id for item in first.evidence],
            [item.id for item in same_content_different_title.evidence],
        )
        self.assertEqual(first.source_hash, same_content_different_title.source_hash)
        self.assertEqual(
            [claim.id for claim in first.claims],
            [claim.id for claim in same_content_different_title.claims],
        )


if __name__ == "__main__":
    unittest.main()
