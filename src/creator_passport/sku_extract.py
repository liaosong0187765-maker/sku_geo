from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
from typing import Any

from .intake import RawSourceDocument
from .sku_models import Evidence, ProductClaim, SkuFacts


LIST_FACT_FIELDS = {
    "compatibility",
    "requirements",
    "certifications",
    "protocols",
    "ports",
    "power",
    "warranty",
    "region_availability",
}
SKU_NOTE_FIELDS = {"limitations", "use_cases", "not_for"}

SECTION_LABELS = {
    "summary": "summary",
    "product_summary": "summary",
    "key_specs": "key_specs",
    "key_specifications": "key_specs",
    "specs": "key_specs",
    "specifications": "key_specs",
    "technical_specs": "key_specs",
    "technical_specifications": "key_specs",
    "compatibility": "compatibility",
    "compatible_with": "compatibility",
    "requirements": "requirements",
    "required": "requirements",
    "certifications": "certifications",
    "certification": "certifications",
    "compliance": "certifications",
    "protocols": "protocols",
    "protocol": "protocols",
    "ports": "ports",
    "connectors": "ports",
    "interfaces": "ports",
    "power": "power",
    "power_input": "power",
    "power_output": "power",
    "warranty": "warranty",
    "region_availability": "region_availability",
    "regional_availability": "region_availability",
    "regions": "region_availability",
    "limitations": "limitations",
    "limits": "limitations",
    "use_cases": "use_cases",
    "use_case": "use_cases",
    "recommended_use_cases": "use_cases",
    "not_for": "not_for",
    "not_recommended_for": "not_for",
    "claims": "claims",
    "claim": "claims",
}

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?P<text>.+?)\s*$")
KEY_VALUE_RE = re.compile(r"^\s*(?P<key>[^:=]{1,80})\s*[:=]\s*(?P<value>.+?)\s*$")


@dataclass
class ExtractedSkuFacts:
    facts: SkuFacts = field(default_factory=SkuFacts)
    evidence: list[Evidence] = field(default_factory=list)
    claims: list[ProductClaim] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    not_for: list[str] = field(default_factory=list)
    source_document_id: str = ""
    source_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "facts": self.facts.to_dict(),
            "evidence": [item.to_dict() for item in self.evidence],
            "claims": [claim.to_dict() for claim in self.claims],
            "limitations": self.limitations,
            "use_cases": self.use_cases,
            "not_for": self.not_for,
            "source_document_id": self.source_document_id,
            "source_hash": self.source_hash,
        }


@dataclass
class _ParsedLine:
    text: str
    raw: str
    section: str
    line_number: int
    is_bullet: bool = False


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _clean_markdown(value: str) -> str:
    text = value.strip()
    text = re.sub(r"^\s*#+\s*", "", text)
    text = re.sub(r"\s*#*\s*$", "", text)
    text = text.strip("`*_ \t")
    return re.sub(r"\s+", " ", text).strip()


def _label_key(value: str) -> str:
    cleaned = _clean_markdown(value).lower()
    cleaned = cleaned.replace("&", " and ")
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    return cleaned.strip("_")


def _spec_key(value: str) -> str:
    return _label_key(value)


def _split_key_value(value: str) -> tuple[str, str] | None:
    match = KEY_VALUE_RE.match(value)
    if not match:
        return None
    key = _clean_markdown(match.group("key"))
    item_value = _clean_markdown(match.group("value"))
    if not key or not item_value:
        return None
    return key, item_value


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def _source_type(document: RawSourceDocument) -> str:
    if document.origin_type == "manual_markdown":
        return "human_note"
    return "other"


def _evidence(
    document: RawSourceDocument,
    *,
    field_name: str,
    value: str,
    line: _ParsedLine,
    index: int,
) -> Evidence:
    excerpt = _clean_markdown(line.raw or value)
    evidence_hash = _hash(
        "|".join(
            [
                document.content_hash,
                field_name,
                line.section,
                str(line.line_number),
                excerpt,
            ]
        )
    )
    return Evidence(
        id=f"ev-{_label_key(field_name) or 'fact'}-{index:03d}-{evidence_hash[:8]}",
        source_type=_source_type(document),
        title=document.title,
        excerpt=excerpt,
        url=document.origin_url,
        file_path=document.file_path,
        captured_at=document.captured_at,
        source_hash=document.content_hash,
        section=line.section,
        anchor=f"line-{line.line_number}",
        confidence="high",
    )


def _claim_id(claim: str, evidence_id: str, index: int) -> str:
    return f"claim-{index:03d}-{_hash(claim + '|' + evidence_id)[:8]}"


def _parse_lines(raw_markdown: str) -> list[_ParsedLine]:
    lines: list[_ParsedLine] = []
    current_section = ""
    for line_number, raw in enumerate(raw_markdown.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped:
            continue
        heading = HEADING_RE.match(stripped)
        if heading:
            current_section = _clean_markdown(heading.group(1))
            continue
        bullet = BULLET_RE.match(stripped)
        text = bullet.group("text") if bullet else stripped
        lines.append(
            _ParsedLine(
                text=_clean_markdown(text),
                raw=stripped,
                section=current_section,
                line_number=line_number,
                is_bullet=bool(bullet),
            )
        )
    return lines


def _add_key_spec(
    key_specs: dict[str, str | list[str]],
    key: str,
    value: str,
) -> None:
    normalized_key = _spec_key(key)
    if not normalized_key or not value:
        return
    existing = key_specs.get(normalized_key)
    if existing is None:
        key_specs[normalized_key] = value
    elif isinstance(existing, list):
        _append_unique(existing, value)
    elif existing != value:
        key_specs[normalized_key] = [existing, value]


def _section_field(line: _ParsedLine) -> str:
    if not line.section:
        return ""
    return SECTION_LABELS.get(_label_key(line.section), "")


def _labeled_field(line: _ParsedLine) -> tuple[str, str] | None:
    split = _split_key_value(line.text)
    if not split:
        return None
    key, value = split
    field_name = SECTION_LABELS.get(_label_key(key), "")
    if not field_name:
        return None
    return field_name, value


def extract_sku_facts(document: RawSourceDocument) -> ExtractedSkuFacts:
    """Extract only facts explicitly labeled in a raw Markdown SKU source."""
    document.validate()
    facts = SkuFacts()
    notes: dict[str, list[str]] = {field_name: [] for field_name in SKU_NOTE_FIELDS}
    evidence: list[Evidence] = []
    claims: list[ProductClaim] = []
    evidence_index = 0
    claim_index = 0

    def add_evidence(field_name: str, value: str, line: _ParsedLine) -> Evidence:
        nonlocal evidence_index
        evidence_index += 1
        item = _evidence(
            document,
            field_name=field_name,
            value=value,
            line=line,
            index=evidence_index,
        )
        evidence.append(item)
        return item

    for line in _parse_lines(document.raw_markdown):
        section_field = _section_field(line)
        labeled = _labeled_field(line)

        if section_field == "key_specs":
            split = _split_key_value(line.text)
            if split:
                key, value = split
                field_name = SECTION_LABELS.get(_label_key(key), "")
                if field_name == "claims":
                    claim_evidence = add_evidence("claims", value, line)
                    claim_index += 1
                    claims.append(
                        ProductClaim(
                            id=_claim_id(value, claim_evidence.id, claim_index),
                            claim=value,
                            evidence_ids=[claim_evidence.id],
                            confidence="medium",
                        )
                    )
                    continue
                _add_key_spec(facts.key_specs, key, value)
                add_evidence("key_specs", f"{key}: {value}", line)
                if field_name in LIST_FACT_FIELDS:
                    _append_unique(getattr(facts, field_name), value)
                    add_evidence(field_name, value, line)
                continue

        if labeled:
            field_name, value = labeled
            if field_name == "key_specs":
                nested = _split_key_value(value)
                if nested:
                    key, spec_value = nested
                    _add_key_spec(facts.key_specs, key, spec_value)
                    add_evidence("key_specs", f"{key}: {spec_value}", line)
                continue
            if field_name == "summary":
                if not facts.summary:
                    facts.summary = value
                    add_evidence("summary", value, line)
                continue
            if field_name == "claims":
                claim_evidence = add_evidence("claims", value, line)
                claim_index += 1
                claims.append(
                    ProductClaim(
                        id=_claim_id(value, claim_evidence.id, claim_index),
                        claim=value,
                        evidence_ids=[claim_evidence.id],
                        confidence="medium",
                    )
                )
                continue
            if field_name in LIST_FACT_FIELDS:
                _append_unique(getattr(facts, field_name), value)
                add_evidence(field_name, value, line)
                continue
            if field_name in SKU_NOTE_FIELDS:
                _append_unique(notes[field_name], value)
                add_evidence(field_name, value, line)
                continue

        if section_field == "key_specs":
            split = _split_key_value(line.text)
            if split:
                key, value = split
                _add_key_spec(facts.key_specs, key, value)
                add_evidence("key_specs", f"{key}: {value}", line)
            continue

        if section_field == "summary":
            if not facts.summary:
                facts.summary = line.text
                add_evidence("summary", line.text, line)
            continue

        if section_field == "claims":
            claim_text = line.text
            claim_evidence = add_evidence("claims", claim_text, line)
            claim_index += 1
            claims.append(
                ProductClaim(
                    id=_claim_id(claim_text, claim_evidence.id, claim_index),
                    claim=claim_text,
                    evidence_ids=[claim_evidence.id],
                    confidence="medium",
                )
            )
            continue

        if section_field in LIST_FACT_FIELDS:
            if _split_key_value(line.text) and not line.is_bullet:
                continue
            _append_unique(getattr(facts, section_field), line.text)
            add_evidence(section_field, line.text, line)
            continue

        if section_field in SKU_NOTE_FIELDS:
            if _split_key_value(line.text) and not line.is_bullet:
                continue
            _append_unique(notes[section_field], line.text)
            add_evidence(section_field, line.text, line)

    return ExtractedSkuFacts(
        facts=facts,
        evidence=evidence,
        claims=claims,
        limitations=notes["limitations"],
        use_cases=notes["use_cases"],
        not_for=notes["not_for"],
        source_document_id=document.id,
        source_hash=document.content_hash,
    )


def extract_passport_parts(document: RawSourceDocument) -> dict[str, Any]:
    """Return extracted parts shaped for SkuSourcePassport input assembly."""
    result = extract_sku_facts(document)
    return {
        "facts": result.facts.to_dict(),
        "claims": [claim.to_dict() for claim in result.claims],
        "evidence": [item.to_dict() for item in result.evidence],
        "limitations": result.limitations,
        "use_cases": result.use_cases,
        "not_for": result.not_for,
        "source_document_id": result.source_document_id,
        "source_hash": result.source_hash,
    }


__all__ = [
    "ExtractedSkuFacts",
    "extract_passport_parts",
    "extract_sku_facts",
]
