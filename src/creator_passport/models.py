from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import hashlib
import json
import re
from typing import Any


class ValidationError(ValueError):
    pass


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "source"


@dataclass
class Creator:
    id: str
    name: str
    bio: str
    domain: str
    topics: list[str] = field(default_factory=list)
    social_profiles: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Creator":
        return cls(
            id=slugify(_text(data.get("id") or data.get("name"))),
            name=_text(data.get("name")),
            bio=_text(data.get("bio")),
            domain=_text(data.get("domain")).rstrip("/"),
            topics=[_text(item) for item in _list(data.get("topics")) if _text(item)],
            social_profiles={
                _text(key): _text(value)
                for key, value in (data.get("social_profiles") or {}).items()
                if _text(key) and _text(value)
            },
        )


@dataclass
class Claim:
    claim: str
    evidence: str
    reference_url: str = ""
    confidence: str = "medium"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Claim":
        return cls(
            claim=_text(data.get("claim")),
            evidence=_text(data.get("evidence")),
            reference_url=_text(data.get("reference_url")),
            confidence=_text(data.get("confidence")) or "medium",
        )


@dataclass
class Reference:
    title: str
    url: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Reference":
        return cls(title=_text(data.get("title")), url=_text(data.get("url")))


@dataclass
class SourcePassport:
    creator: Creator
    title: str
    thesis: str
    body: str
    created_at: str
    updated_at: str
    version: int
    topics: list[str]
    claims: list[Claim]
    evidence: list[str]
    references: list[Reference]
    limitations: list[str]
    related_sources: list[str]
    recommended_citation: str
    monitor_prompts: list[str]
    slug: str = ""
    canonical_url: str = ""
    content_hash: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], base_url: str | None = None) -> "SourcePassport":
        creator = Creator.from_dict(data.get("creator") or {})
        source = data.get("source") or data
        title = _text(source.get("title"))
        slug = slugify(_text(source.get("slug")) or title)
        passport = cls(
            creator=creator,
            title=title,
            thesis=_text(source.get("thesis")),
            body=_text(source.get("body")),
            created_at=_text(source.get("created_at")) or date.today().isoformat(),
            updated_at=_text(source.get("updated_at")) or date.today().isoformat(),
            version=int(source.get("version") or 1),
            topics=[_text(item) for item in _list(source.get("topics")) if _text(item)],
            claims=[Claim.from_dict(item) for item in _list(source.get("claims")) if isinstance(item, dict)],
            evidence=[_text(item) for item in _list(source.get("evidence")) if _text(item)],
            references=[Reference.from_dict(item) for item in _list(source.get("references")) if isinstance(item, dict)],
            limitations=[_text(item) for item in _list(source.get("limitations")) if _text(item)],
            related_sources=[_text(item) for item in _list(source.get("related_sources")) if _text(item)],
            recommended_citation=_text(source.get("recommended_citation")),
            monitor_prompts=[_text(item) for item in _list(data.get("monitor_prompts")) if _text(item)],
            slug=slug,
        )
        passport.content_hash = _text(source.get("content_hash")) or passport.compute_hash()
        root_url = (base_url or creator.domain or "https://creator-source.local").rstrip("/")
        passport.canonical_url = _text(source.get("canonical_url")) or f"{root_url}{passport.canonical_path}"
        if not passport.recommended_citation:
            passport.recommended_citation = f"{creator.name}, \"{title},\" Source Passport v{passport.version}, {passport.canonical_url}"
        passport.validate()
        return passport

    @property
    def canonical_path(self) -> str:
        return f"/s/{self.slug}-{self.content_hash}"

    @property
    def markdown_path(self) -> str:
        return f"/s/{self.slug}-{self.content_hash}.md"

    @property
    def source_anchor(self) -> str:
        return f"Source Passport: {self.content_hash}\nSource: {self.canonical_url}"

    def compute_hash(self) -> str:
        payload = {
            "title": self.title,
            "thesis": self.thesis,
            "body": self.body,
            "claims": [claim.__dict__ for claim in self.claims],
            "evidence": self.evidence,
            "references": [reference.__dict__ for reference in self.references],
            "version": self.version,
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:12]

    def validate(self) -> None:
        missing: list[str] = []
        if not self.creator.name:
            missing.append("creator.name")
        if not self.title:
            missing.append("source.title")
        if not self.thesis:
            missing.append("source.thesis")
        if not self.body:
            missing.append("source.body")
        if not self.topics:
            missing.append("source.topics")
        if not self.claims:
            missing.append("source.claims")
        if any(not claim.claim or not claim.evidence for claim in self.claims):
            missing.append("source.claims.claim_and_evidence")
        if missing:
            raise ValidationError("Missing required fields: " + ", ".join(missing))

    def to_dict(self) -> dict[str, Any]:
        return {
            "creator": {
                "id": self.creator.id,
                "name": self.creator.name,
                "bio": self.creator.bio,
                "domain": self.creator.domain,
                "topics": self.creator.topics,
                "social_profiles": self.creator.social_profiles,
            },
            "source": {
                "slug": self.slug,
                "title": self.title,
                "thesis": self.thesis,
                "body": self.body,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "canonical_url": self.canonical_url,
                "canonical_path": self.canonical_path,
                "markdown_path": self.markdown_path,
                "content_hash": self.content_hash,
                "version": self.version,
                "topics": self.topics,
                "claims": [claim.__dict__ for claim in self.claims],
                "evidence": self.evidence,
                "references": [reference.__dict__ for reference in self.references],
                "limitations": self.limitations,
                "related_sources": self.related_sources,
                "recommended_citation": self.recommended_citation,
                "source_anchor": self.source_anchor,
            },
            "monitor_prompts": self.monitor_prompts,
        }


def load_passport(path: str, base_url: str | None = None) -> SourcePassport:
    with open(path, "r", encoding="utf-8") as handle:
        return SourcePassport.from_dict(json.load(handle), base_url=base_url)


def load_generated_passport(out_dir: str) -> SourcePassport:
    with open(f"{out_dir}/passport.json", "r", encoding="utf-8") as handle:
        return SourcePassport.from_dict(json.load(handle))
