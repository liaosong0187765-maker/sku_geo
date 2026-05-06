from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
import hashlib
import json
from pathlib import Path
from typing import Any

from .models import ValidationError, slugify


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _string_list(value: Any) -> list[str]:
    return [item for item in (_text(item) for item in _list(value)) if item]


def _string_dict(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        _text(key): _text(item)
        for key, item in value.items()
        if _text(key) and _text(item)
    }


def _fact_value(value: Any) -> str | int | float | bool | list[str | int | float | bool]:
    if isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, list):
        return [
            item
            for item in value
            if isinstance(item, bool | int | float | str)
        ]
    return _text(value)


def _fact_dict(value: Any) -> dict[str, str | int | float | bool | list[str | int | float | bool]]:
    if not isinstance(value, dict):
        return {}
    return {
        _text(key): _fact_value(item)
        for key, item in value.items()
        if _text(key)
    }


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _score(value: Any) -> float | int | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number < 0:
        return 0
    if number > 100:
        return 100
    return int(number) if number.is_integer() else number


@dataclass
class Brand:
    id: str
    name: str
    domain: str
    market: str = ""
    official_urls: list[str] = field(default_factory=list)
    support_urls: list[str] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Brand":
        name = _text(data.get("name"))
        official_urls = _string_list(data.get("official_urls"))
        legacy_official_url = _text(data.get("official_url") or data.get("url"))
        if legacy_official_url:
            official_urls.append(legacy_official_url)
        return cls(
            id=slugify(_text(data.get("id")) or name),
            name=name,
            domain=_text(data.get("domain")).rstrip("/"),
            market=_text(data.get("market")),
            official_urls=official_urls,
            support_urls=_string_list(data.get("support_urls")),
            description=_text(data.get("description")),
        )

    def validate(self) -> None:
        missing: list[str] = []
        if not self.id:
            missing.append("brand.id")
        if not self.name:
            missing.append("brand.name")
        if not self.domain:
            missing.append("brand.domain")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SKU:
    id: str
    brand_id: str
    product_name: str
    slug: str
    category: str
    canonical_url: str
    model_number: str = ""
    status: str = "draft"
    source_urls: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    not_for: list[str] = field(default_factory=list)
    compatibility_notes: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], brand_id: str = "") -> "SKU":
        product_name = _text(data.get("product_name") or data.get("name"))
        slug = slugify(_text(data.get("slug")) or product_name or _text(data.get("id")))
        return cls(
            id=slugify(_text(data.get("id")) or slug),
            brand_id=_text(data.get("brand_id")) or brand_id,
            product_name=product_name,
            slug=slug,
            category=_text(data.get("category")),
            canonical_url=_text(
                data.get("canonical_url") or data.get("product_url") or data.get("url")
            ),
            model_number=_text(data.get("model_number") or data.get("model")),
            status=_text(data.get("status")) or "draft",
            source_urls=_string_list(data.get("source_urls")),
            limitations=_string_list(data.get("limitations")),
            use_cases=_string_list(data.get("use_cases")),
            not_for=_string_list(data.get("not_for")),
            compatibility_notes=_text(data.get("compatibility_notes")),
            updated_at=_text(data.get("updated_at")),
        )

    def validate(self) -> None:
        missing: list[str] = []
        if not self.id:
            missing.append("sku.id")
        if not self.brand_id:
            missing.append("sku.brand_id")
        if not self.product_name:
            missing.append("sku.product_name")
        if not self.category:
            missing.append("sku.category")
        if not self.canonical_url:
            missing.append("sku.canonical_url")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkuFacts:
    summary: str = ""
    key_specs: dict[
        str, str | int | float | bool | list[str | int | float | bool]
    ] = field(default_factory=dict)
    positioning: str = ""
    materials: list[str] = field(default_factory=list)
    dimensions: dict[str, str] = field(default_factory=dict)
    included_items: list[str] = field(default_factory=list)
    compatibility: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)
    ports: list[str] = field(default_factory=list)
    power: list[str] = field(default_factory=list)
    warranty: list[str] = field(default_factory=list)
    region_availability: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SkuFacts":
        return cls(
            summary=_text(data.get("summary")),
            key_specs=_fact_dict(data.get("key_specs") or data.get("attributes")),
            positioning=_text(data.get("positioning")),
            materials=_string_list(data.get("materials")),
            dimensions=_string_dict(data.get("dimensions")),
            included_items=_string_list(data.get("included_items")),
            compatibility=_string_list(data.get("compatibility")),
            requirements=_string_list(data.get("requirements")),
            certifications=_string_list(data.get("certifications")),
            protocols=_string_list(data.get("protocols")),
            ports=_string_list(data.get("ports")),
            power=_string_list(data.get("power")),
            warranty=_string_list(data.get("warranty")),
            region_availability=_string_list(data.get("region_availability")),
        )

    def validate(self) -> None:
        missing: list[str] = []
        if not self.summary:
            missing.append("facts.summary")
        if not self.key_specs:
            missing.append("facts.key_specs")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProductClaim:
    id: str
    claim: str
    evidence_ids: list[str] = field(default_factory=list)
    claim_type: str = ""
    confidence: str = "medium"
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProductClaim":
        claim = _text(data.get("claim"))
        return cls(
            id=slugify(_text(data.get("id")) or claim),
            claim=claim,
            evidence_ids=_string_list(data.get("evidence_ids") or data.get("evidence")),
            claim_type=_text(data.get("claim_type") or data.get("type")),
            confidence=_text(data.get("confidence")) or "medium",
            notes=_text(data.get("notes") or data.get("limitation")),
        )

    def validate(self) -> None:
        missing: list[str] = []
        if not self.id:
            missing.append("claims.id")
        if not self.claim:
            missing.append("claims.claim")
        if not self.evidence_ids:
            missing.append("claims.evidence_ids")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Evidence:
    id: str
    source_type: str
    title: str
    excerpt: str
    url: str = ""
    file_path: str = ""
    captured_at: str = ""
    source_hash: str = ""
    page: str = ""
    section: str = ""
    anchor: str = ""
    confidence: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Evidence":
        title = _text(data.get("title"))
        evidence = cls(
            id=slugify(_text(data.get("id")) or title),
            source_type=_text(data.get("source_type") or data.get("type")),
            title=title,
            excerpt=_text(data.get("excerpt") or data.get("summary")),
            url=_text(data.get("url")),
            file_path=_text(data.get("file_path")),
            captured_at=_text(data.get("captured_at") or data.get("observed_at")),
            source_hash=_text(data.get("source_hash") or data.get("content_hash")),
            page=_text(data.get("page")),
            section=_text(data.get("section")),
            anchor=_text(data.get("anchor")),
            confidence=_text(data.get("confidence")),
        )
        if not evidence.source_hash:
            evidence.source_hash = evidence.compute_hash()
        return evidence

    def compute_hash(self) -> str:
        payload = {
            "title": self.title,
            "excerpt": self.excerpt,
            "url": self.url,
            "file_path": self.file_path,
            "source_type": self.source_type,
            "captured_at": self.captured_at,
            "page": self.page,
            "section": self.section,
            "anchor": self.anchor,
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:12]

    def validate(self) -> None:
        missing: list[str] = []
        if not self.id:
            missing.append("evidence.id")
        if not self.source_type:
            missing.append("evidence.source_type")
        if not self.title:
            missing.append("evidence.title")
        if not self.excerpt and not self.url and not self.file_path:
            missing.append("evidence.excerpt|url|file_path")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompetitorContext:
    id: str = ""
    category: str = ""
    competitor_name: str = ""
    basis: str = ""
    competitor_product_name: str = ""
    competitor_url: str = ""
    comparison_points: list[str] = field(default_factory=list)
    known_differences: list[str] = field(default_factory=list)
    avoid_claims: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompetitorContext":
        competitor_name = _text(
            data.get("competitor_name")
            or next(iter(_string_list(data.get("competitors"))), "")
        )
        basis = _text(data.get("basis")) or ", ".join(_string_list(data.get("comparison_basis")))
        return cls(
            id=slugify(_text(data.get("id")) or competitor_name),
            category=_text(data.get("category")),
            competitor_name=competitor_name,
            basis=basis,
            competitor_product_name=_text(data.get("competitor_product_name")),
            competitor_url=_text(data.get("competitor_url")),
            comparison_points=_string_list(data.get("comparison_points")),
            known_differences=_string_list(data.get("known_differences") or data.get("differentiators")),
            avoid_claims=_string_list(data.get("avoid_claims") or data.get("limitations")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BuyingQuestion:
    id: str
    question: str
    intent: str
    sku_ids: list[str] = field(default_factory=list)
    category: str = ""
    expected_facts: list[str] = field(default_factory=list)
    expected_limitations: list[str] = field(default_factory=list)
    competitor_context_ids: list[str] = field(default_factory=list)
    priority: str = "medium"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BuyingQuestion":
        question = _text(data.get("question"))
        return cls(
            id=slugify(_text(data.get("id")) or question),
            question=question,
            intent=_text(data.get("intent")) or "general",
            sku_ids=_string_list(data.get("sku_ids")),
            category=_text(data.get("category")),
            expected_facts=_string_list(data.get("expected_facts") or data.get("answer")),
            expected_limitations=_string_list(data.get("expected_limitations")),
            competitor_context_ids=_string_list(data.get("competitor_context_ids")),
            priority=_text(data.get("priority")) or "medium",
        )

    def validate(self) -> None:
        missing: list[str] = []
        if not self.id:
            missing.append("buying_questions.id")
        if not self.question:
            missing.append("buying_questions.question")
        if not self.intent:
            missing.append("buying_questions.intent")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievalRun:
    id: str
    question_id: str
    ran_at: str
    provider: str
    response_text: str
    model: str = ""
    sku_ids: list[str] = field(default_factory=list)
    brand_mentioned: bool = False
    sku_mentioned: bool = False
    canonical_url_cited: bool = False
    source_hash_cited: bool = False
    claim_coverage: dict[str, str] = field(default_factory=dict)
    wrong_specs_present: bool = False
    limitations_preserved: bool = False
    competitor_context_present: bool = False
    buying_intent_matched: bool = False
    score: float | int | None = None
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RetrievalRun":
        response_text = _text(data.get("response_text") or data.get("response"))
        return cls(
            id=slugify(_text(data.get("id")) or _text(data.get("question_id")) or _text(data.get("prompt"))),
            question_id=_text(data.get("question_id")),
            ran_at=_text(data.get("ran_at") or data.get("run_at")),
            provider=_text(data.get("provider")),
            response_text=response_text,
            model=_text(data.get("model")),
            sku_ids=_string_list(data.get("sku_ids")),
            brand_mentioned=_bool(data.get("brand_mentioned")),
            sku_mentioned=_bool(data.get("sku_mentioned")),
            canonical_url_cited=_bool(data.get("canonical_url_cited") or data.get("cited_source")),
            source_hash_cited=_bool(data.get("source_hash_cited")),
            claim_coverage=_string_dict(data.get("claim_coverage")),
            wrong_specs_present=_bool(data.get("wrong_specs_present")),
            limitations_preserved=_bool(data.get("limitations_preserved")),
            competitor_context_present=_bool(data.get("competitor_context_present")),
            buying_intent_matched=_bool(data.get("buying_intent_matched")),
            score=_score(data.get("score")),
            notes=_text(data.get("notes")),
        )

    def validate(self) -> None:
        missing: list[str] = []
        if not self.id:
            missing.append("retrieval_runs.id")
        if not self.question_id:
            missing.append("retrieval_runs.question_id")
        if not self.ran_at:
            missing.append("retrieval_runs.ran_at")
        if not self.provider:
            missing.append("retrieval_runs.provider")
        if not self.response_text:
            missing.append("retrieval_runs.response_text")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RevisionSuggestion:
    id: str
    source: str
    reason: str
    target: str
    action: str
    retrieval_run_id: str = ""
    sku_ids: list[str] = field(default_factory=list)
    claim_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    severity: str = "medium"
    status: str = "open"
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RevisionSuggestion":
        reason = _text(data.get("reason") or data.get("issue"))
        action = _text(data.get("action") or data.get("recommendation"))
        return cls(
            id=slugify(_text(data.get("id")) or reason),
            source=_text(data.get("source")),
            reason=reason,
            target=_text(data.get("target")),
            action=action,
            retrieval_run_id=_text(data.get("retrieval_run_id")),
            sku_ids=_string_list(data.get("sku_ids")),
            claim_ids=_string_list(data.get("claim_ids")),
            evidence_ids=_string_list(data.get("evidence_ids")),
            severity=_text(data.get("severity") or data.get("priority")) or "medium",
            status=_text(data.get("status")) or "open",
            created_at=_text(data.get("created_at")),
        )

    def validate(self) -> None:
        missing: list[str] = []
        if not self.id:
            missing.append("revision_suggestions.id")
        if not self.source:
            missing.append("revision_suggestions.source")
        if not self.reason:
            missing.append("revision_suggestions.reason")
        if not self.target:
            missing.append("revision_suggestions.target")
        if not self.action:
            missing.append("revision_suggestions.action")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SkuSourcePassport:
    brand: Brand
    sku: SKU
    facts: SkuFacts
    created_at: str
    updated_at: str
    version: int
    topics: list[str]
    claims: list[ProductClaim]
    evidence: list[Evidence]
    competitor_context: list[CompetitorContext] = field(default_factory=list)
    buying_questions: list[BuyingQuestion] = field(default_factory=list)
    retrieval_runs: list[RetrievalRun] = field(default_factory=list)
    revision_suggestions: list[RevisionSuggestion] = field(default_factory=list)
    recommended_citation: str = ""
    slug: str = ""
    canonical_url: str = ""
    content_hash: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], base_url: str | None = None) -> "SkuSourcePassport":
        passport_data = data.get("sku_source") or data.get("source") or data
        brand = Brand.from_dict(data.get("brand") or passport_data.get("brand") or {})
        sku_data = data.get("sku") or passport_data.get("sku") or {}
        if not sku_data and isinstance(data.get("skus"), list) and data["skus"]:
            sku_data = data["skus"][0]
        sku = SKU.from_dict(sku_data, brand.id)
        facts = SkuFacts.from_dict(sku_data.get("facts") or passport_data.get("facts") or {})
        slug = slugify(_text(passport_data.get("slug")) or sku.slug or f"{brand.name} {sku.product_name}")
        raw_competitor_context = passport_data.get("competitor_context") or data.get("competitor_context")
        if isinstance(raw_competitor_context, list):
            competitor_context = [
                CompetitorContext.from_dict(item)
                for item in raw_competitor_context
                if isinstance(item, dict)
            ]
        elif isinstance(raw_competitor_context, dict) and raw_competitor_context:
            competitor_context = [CompetitorContext.from_dict(raw_competitor_context)]
        else:
            competitor_context = []
        passport = cls(
            brand=brand,
            sku=sku,
            facts=facts,
            created_at=_text(passport_data.get("created_at")) or date.today().isoformat(),
            updated_at=_text(passport_data.get("updated_at") or sku.updated_at) or date.today().isoformat(),
            version=int(passport_data.get("version") or 1),
            topics=_string_list(passport_data.get("topics")),
            claims=[
                ProductClaim.from_dict(item)
                for item in _list(passport_data.get("claims") or sku_data.get("claims"))
                if isinstance(item, dict)
            ],
            evidence=[
                Evidence.from_dict(item)
                for item in _list(passport_data.get("evidence") or sku_data.get("evidence"))
                if isinstance(item, dict)
            ],
            competitor_context=competitor_context,
            buying_questions=[
                BuyingQuestion.from_dict(item)
                for item in _list(passport_data.get("buying_questions") or data.get("buying_questions"))
                if isinstance(item, dict)
            ],
            retrieval_runs=[
                RetrievalRun.from_dict(item)
                for item in _list(passport_data.get("retrieval_runs") or data.get("retrieval_runs"))
                if isinstance(item, dict)
            ],
            revision_suggestions=[
                RevisionSuggestion.from_dict(item)
                for item in _list(
                    passport_data.get("revision_suggestions") or data.get("revision_suggestions")
                )
                if isinstance(item, dict)
            ],
            recommended_citation=_text(passport_data.get("recommended_citation")),
            slug=slug,
        )
        passport.content_hash = _text(passport_data.get("content_hash")) or passport.compute_hash()
        root_url = (base_url or brand.domain or "https://sku-source.local").rstrip("/")
        passport.canonical_url = (
            _text(passport_data.get("canonical_url")) or f"{root_url}{passport.canonical_path}"
        )
        if not passport.recommended_citation:
            passport.recommended_citation = (
                f"{brand.name}, \"{sku.product_name},\" SKU Source Passport v{passport.version}, "
                f"{passport.canonical_url}"
            )
        passport.validate()
        return passport

    @property
    def canonical_path(self) -> str:
        return f"/sku/{self.slug}-{self.content_hash}"

    @property
    def markdown_path(self) -> str:
        return f"/sku/{self.slug}-{self.content_hash}.md"

    @property
    def source_anchor(self) -> str:
        return f"SKU Source Passport: {self.content_hash}\nSource: {self.canonical_url}"

    def compute_hash(self) -> str:
        payload = {
            "brand": self.brand.to_dict(),
            "sku": self.sku.to_dict(),
            "facts": self.facts.to_dict(),
            "version": self.version,
            "topics": self.topics,
            "claims": [claim.to_dict() for claim in self.claims],
            "evidence": [item.to_dict() for item in self.evidence],
            "competitor_context": [item.to_dict() for item in self.competitor_context],
            "buying_questions": [question.to_dict() for question in self.buying_questions],
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:12]

    def validate(self) -> None:
        missing: list[str] = []
        try:
            self.brand.validate()
        except ValidationError as exc:
            missing.append(str(exc).removeprefix("Missing required fields: "))
        try:
            self.sku.validate()
        except ValidationError as exc:
            missing.append(str(exc).removeprefix("Missing required fields: "))
        try:
            self.facts.validate()
        except ValidationError as exc:
            missing.append(str(exc).removeprefix("Missing required fields: "))
        for claim in self.claims:
            try:
                claim.validate()
            except ValidationError as exc:
                missing.append(str(exc).removeprefix("Missing required fields: "))
        for item in self.evidence:
            try:
                item.validate()
            except ValidationError as exc:
                missing.append(str(exc).removeprefix("Missing required fields: "))
        evidence_ids = {item.id for item in self.evidence}
        for claim in self.claims:
            for evidence_id in claim.evidence_ids:
                if evidence_id not in evidence_ids:
                    missing.append(f"claims.evidence_ids[{evidence_id}]")
        for question in self.buying_questions:
            try:
                question.validate()
            except ValidationError as exc:
                missing.append(str(exc).removeprefix("Missing required fields: "))
        for run in self.retrieval_runs:
            try:
                run.validate()
            except ValidationError as exc:
                missing.append(str(exc).removeprefix("Missing required fields: "))
        for suggestion in self.revision_suggestions:
            try:
                suggestion.validate()
            except ValidationError as exc:
                missing.append(str(exc).removeprefix("Missing required fields: "))
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        sku_payload = {
            **self.sku.to_dict(),
            "facts": self.facts.to_dict(),
            "claims": [claim.to_dict() for claim in self.claims],
            "evidence": [item.to_dict() for item in self.evidence],
        }
        return {
            "brand": self.brand.to_dict(),
            "skus": [sku_payload],
            "sku": sku_payload,
            "sku_source": {
                "slug": self.slug,
                "facts": self.facts.to_dict(),
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "canonical_url": self.canonical_url,
                "canonical_path": self.canonical_path,
                "markdown_path": self.markdown_path,
                "content_hash": self.content_hash,
                "version": self.version,
                "topics": self.topics,
                "claims": [claim.to_dict() for claim in self.claims],
                "evidence": [item.to_dict() for item in self.evidence],
                "competitor_context": [item.to_dict() for item in self.competitor_context],
                "buying_questions": [question.to_dict() for question in self.buying_questions],
                "retrieval_runs": [run.to_dict() for run in self.retrieval_runs],
                "revision_suggestions": [
                    suggestion.to_dict() for suggestion in self.revision_suggestions
                ],
                "recommended_citation": self.recommended_citation,
                "source_anchor": self.source_anchor,
            },
        }


def load_sku_passports(path: str | Path, base_url: str | None = None) -> list[SkuSourcePassport]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data.get("skus"), list) and len(data["skus"]) > 1:
        passports: list[SkuSourcePassport] = []
        for sku_data in data["skus"]:
            item = dict(data)
            item["sku"] = sku_data
            item["skus"] = [sku_data]
            passports.append(SkuSourcePassport.from_dict(item, base_url=base_url))
        return passports
    return [SkuSourcePassport.from_dict(data, base_url=base_url)]
