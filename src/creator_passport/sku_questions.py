from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from .sku_models import (
    BuyingQuestion,
    CompetitorContext,
    ProductClaim,
    SkuSourcePassport,
)


@dataclass(frozen=True)
class AnswerFact:
    text: str
    claim_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BuyingQuestionAnswer:
    question_id: str
    question: str
    intent: str
    answer: str
    facts: tuple[AnswerFact, ...] = ()
    limitations: tuple[AnswerFact, ...] = ()
    comparison_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComparisonSection:
    context_id: str
    title: str
    basis: str = ""
    comparison_points: tuple[str, ...] = ()
    known_differences: tuple[str, ...] = ()
    avoid_claims: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_buying_question_answers(
    passport: SkuSourcePassport,
) -> list[BuyingQuestionAnswer]:
    """Generate deterministic answers from explicit SKU passport facts only."""
    return [
        _answer_question(passport, question)
        for question in sorted(passport.buying_questions, key=lambda item: item.id)
    ]


def generate_faq(passport: SkuSourcePassport) -> list[BuyingQuestionAnswer]:
    return generate_buying_question_answers(passport)


def generate_comparison_sections(passport: SkuSourcePassport) -> list[ComparisonSection]:
    sections: list[ComparisonSection] = []
    for item in sorted(passport.competitor_context, key=lambda context: context.id):
        label = item.competitor_product_name or item.competitor_name
        sections.append(
            ComparisonSection(
                context_id=item.id,
                title=f"{passport.sku.product_name} vs {label}",
                basis=item.basis,
                comparison_points=tuple(item.comparison_points),
                known_differences=tuple(item.known_differences),
                avoid_claims=tuple(item.avoid_claims),
            )
        )
    return sections


def render_faq_markdown(passport: SkuSourcePassport) -> str:
    rows = [f"# Buying Questions: {passport.sku.product_name}", ""]
    answers = generate_buying_question_answers(passport)
    if not answers:
        rows.append("No buying questions listed.")
        return "\n".join(rows).strip()

    for answer in answers:
        rows.extend([f"## {answer.question}", "", answer.answer])
        rows.extend(_answer_fact_lines("Facts", answer.facts))
        rows.extend(_answer_fact_lines("Limitations", answer.limitations))
        if answer.comparison_ids:
            rows.extend(["", "Comparison context:", *[f"- {item}" for item in answer.comparison_ids]])
        rows.append("")
    return "\n".join(rows).strip()


def render_comparison_markdown(passport: SkuSourcePassport) -> str:
    rows = [f"# Comparisons: {passport.sku.product_name}", ""]
    sections = generate_comparison_sections(passport)
    if not sections:
        rows.append("No explicit competitor context listed.")
        return "\n".join(rows).strip()

    for section in sections:
        rows.extend([f"## {section.title}", ""])
        if section.basis:
            rows.extend(["Basis:", f"- {section.basis}", ""])
        rows.extend(_plain_lines("Comparison points", section.comparison_points))
        rows.extend(_plain_lines("Known differences", section.known_differences))
        rows.extend(_plain_lines("Avoid claims", section.avoid_claims))
        rows.append("")
    return "\n".join(rows).strip()


def _answer_question(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
) -> BuyingQuestionAnswer:
    facts = _question_facts(passport, question)
    limitations = _question_limitations(passport, question)
    comparison_ids = _comparison_ids(passport, question)

    parts = [
        f"{passport.sku.product_name} is documented as {passport.facts.summary}".rstrip(".") + "."
    ]
    if facts:
        parts.append("Relevant facts: " + "; ".join(fact.text for fact in facts) + ".")
    if limitations:
        parts.append("Relevant limitations: " + "; ".join(item.text for item in limitations) + ".")
    if comparison_ids:
        parts.append(
            "Comparison context is limited to explicit competitor context IDs: "
            + ", ".join(comparison_ids)
            + "."
        )

    return BuyingQuestionAnswer(
        question_id=question.id,
        question=question.question,
        intent=question.intent,
        answer=" ".join(parts),
        facts=tuple(facts),
        limitations=tuple(limitations),
        comparison_ids=tuple(comparison_ids),
    )


def _question_facts(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
) -> list[AnswerFact]:
    explicit = _unique(question.expected_facts)
    if not explicit:
        explicit = _fallback_facts(passport, question.intent)
    return [_bind_fact(passport, text) for text in explicit]


def _question_limitations(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
) -> list[AnswerFact]:
    explicit = _unique(question.expected_limitations)
    if not explicit and question.intent in {"limitation", "choose", "compare"}:
        explicit = _unique([*passport.sku.limitations, *passport.sku.not_for])
    return [_bind_fact(passport, text) for text in explicit]


def _fallback_facts(passport: SkuSourcePassport, intent: str) -> list[str]:
    if intent == "compatibility":
        return _unique([*passport.facts.compatibility, passport.sku.compatibility_notes])
    if intent == "setup":
        return _unique([*passport.facts.requirements, *passport.facts.included_items])
    if intent == "limitation":
        return _unique(passport.sku.limitations)
    if intent == "compare":
        return _unique([passport.facts.positioning, *passport.facts.compatibility])
    return _unique([passport.facts.summary])


def _bind_fact(passport: SkuSourcePassport, text: str) -> AnswerFact:
    claim_ids: list[str] = []
    evidence_ids: list[str] = []
    normalized_text = _normalize(text)

    for claim in sorted(passport.claims, key=lambda item: item.id):
        if _matches(normalized_text, claim):
            claim_ids.append(claim.id)
            evidence_ids.extend(claim.evidence_ids)

    for evidence in sorted(passport.evidence, key=lambda item: item.id):
        haystack = _normalize(" ".join([evidence.title, evidence.excerpt, evidence.section]))
        if normalized_text and normalized_text in haystack:
            evidence_ids.append(evidence.id)

    return AnswerFact(
        text=text,
        claim_ids=tuple(_unique(claim_ids)),
        evidence_ids=tuple(_unique(evidence_ids)),
    )


def _matches(normalized_text: str, claim: ProductClaim) -> bool:
    haystack = _normalize(" ".join([claim.claim, claim.claim_type, claim.notes]))
    return bool(normalized_text and (normalized_text in haystack or haystack in normalized_text))


def _comparison_ids(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
) -> list[str]:
    by_id: dict[str, CompetitorContext] = {
        item.id: item for item in passport.competitor_context
    }
    if question.competitor_context_ids:
        return [
            context_id
            for context_id in _unique(question.competitor_context_ids)
            if context_id in by_id
        ]
    if question.intent == "compare":
        return [item.id for item in sorted(passport.competitor_context, key=lambda item: item.id)]
    return []


def _answer_fact_lines(title: str, items: Iterable[AnswerFact]) -> list[str]:
    item_list = list(items)
    if not item_list:
        return []
    rows = ["", f"{title}:"]
    for item in item_list:
        suffixes = []
        if item.claim_ids:
            suffixes.append("claims: " + ", ".join(item.claim_ids))
        if item.evidence_ids:
            suffixes.append("evidence: " + ", ".join(item.evidence_ids))
        suffix = f" ({'; '.join(suffixes)})" if suffixes else ""
        rows.append(f"- {item.text}{suffix}")
    return rows


def _plain_lines(title: str, items: Iterable[str]) -> list[str]:
    item_list = [item for item in items if item]
    if not item_list:
        return []
    return [f"{title}:", *[f"- {item}" for item in item_list], ""]


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    unique_items: list[str] = []
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        unique_items.append(text)
    return unique_items


def _normalize(value: str) -> str:
    return " ".join(str(value).lower().split())


__all__ = [
    "AnswerFact",
    "BuyingQuestionAnswer",
    "ComparisonSection",
    "generate_buying_question_answers",
    "generate_comparison_sections",
    "generate_faq",
    "render_comparison_markdown",
    "render_faq_markdown",
]
