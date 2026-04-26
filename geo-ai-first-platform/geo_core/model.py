from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


class ValidationError(ValueError):
    pass


def _list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _str(value: Any) -> str:
    return "" if value is None else str(value).strip()


@dataclass
class Source:
    id: str
    title: str
    url: str = ""
    type: str = "document"
    date: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any], idx: int) -> "Source":
        return cls(
            id=_str(data.get("id")) or f"source_{idx}",
            title=_str(data.get("title")) or f"Source {idx}",
            url=_str(data.get("url")),
            type=_str(data.get("type")) or "document",
            date=_str(data.get("date")),
        )


@dataclass
class Claim:
    id: str
    claim: str
    evidence: str = ""
    source: str = ""
    confidence: str = "medium"
    related_questions: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], idx: int) -> "Claim":
        return cls(
            id=_str(data.get("id")) or f"claim_{idx}",
            claim=_str(data.get("claim")),
            evidence=_str(data.get("evidence")),
            source=_str(data.get("source")),
            confidence=_str(data.get("confidence")) or "medium",
            related_questions=[_str(x) for x in _list(data.get("related_questions")) if _str(x)],
        )


@dataclass
class Question:
    question: str
    answer: str
    evidence_refs: List[str] = field(default_factory=list)
    limitations: str = ""
    cta: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Question":
        return cls(
            question=_str(data.get("question")),
            answer=_str(data.get("answer")),
            evidence_refs=[_str(x) for x in _list(data.get("evidence_refs")) if _str(x)],
            limitations=_str(data.get("limitations")),
            cta=_str(data.get("cta")),
        )


@dataclass
class Product:
    name: str
    description: str
    features: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    pricing: str = ""
    limitations: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        return cls(
            name=_str(data.get("name")),
            description=_str(data.get("description")),
            features=[_str(x) for x in _list(data.get("features")) if _str(x)],
            benefits=[_str(x) for x in _list(data.get("benefits")) if _str(x)],
            pricing=_str(data.get("pricing")),
            limitations=[_str(x) for x in _list(data.get("limitations")) if _str(x)],
        )


@dataclass
class KnowledgeCore:
    raw: Dict[str, Any]
    entity: Dict[str, Any]
    audience: Dict[str, Any]
    products: List[Product]
    claims: List[Claim]
    questions: List[Question]
    sources: List[Source]
    competitors: List[Dict[str, Any]]

    @property
    def name(self) -> str:
        return _str(self.entity.get("name"))

    @property
    def url(self) -> str:
        return _str(self.entity.get("url"))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeCore":
        entity = data.get("entity") or {}
        audience = data.get("audience") or {}
        products = [Product.from_dict(x) for x in _list(data.get("products")) if isinstance(x, dict)]
        claims = [Claim.from_dict(x, i + 1) for i, x in enumerate(_list(data.get("claims"))) if isinstance(x, dict)]
        questions = [Question.from_dict(x) for x in _list(data.get("questions")) if isinstance(x, dict)]
        sources = [Source.from_dict(x, i + 1) for i, x in enumerate(_list(data.get("sources"))) if isinstance(x, dict)]
        competitors = [x for x in _list(data.get("competitors")) if isinstance(x, dict)]
        core = cls(data, entity, audience, products, claims, questions, sources, competitors)
        core.validate()
        return core

    def validate(self) -> None:
        missing = []
        if not self.name:
            missing.append("entity.name")
        if not _str(self.entity.get("category")):
            missing.append("entity.category")
        if not _str(self.entity.get("one_line")):
            missing.append("entity.one_line")
        if not self.products:
            missing.append("products")
        if not self.questions:
            missing.append("questions")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_json_ready(self) -> Dict[str, Any]:
        return self.raw

    def claim_evidence_map(self) -> List[Tuple[Claim, str]]:
        source_titles = {s.id: s.title for s in self.sources}
        return [(claim, source_titles.get(claim.source, claim.source or "No source linked")) for claim in self.claims]
