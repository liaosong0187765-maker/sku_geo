from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from typing import Any, Iterable

from .models import slugify
from .sku_models import (
    BuyingQuestion,
    Evidence,
    ProductClaim,
    RetrievalRun,
    RevisionSuggestion,
    SkuSourcePassport,
)


@dataclass(frozen=True)
class SkuMonitorResult:
    retrieval_run: RetrievalRun
    revision_suggestions: tuple[RevisionSuggestion, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "retrieval_run": self.retrieval_run.to_dict(),
            "revision_suggestions": [
                suggestion.to_dict() for suggestion in self.revision_suggestions
            ],
        }


def evaluate_sku_response(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
    response_text: str,
    *,
    provider: str = "provided-response",
    model: str = "",
    ran_at: str | None = None,
) -> SkuMonitorResult:
    """Evaluate one provided answer against explicit SKU passport facts only."""
    response = response_text.strip()
    normalized = _normalize(response)
    claim_coverage = _claim_coverage(passport.claims, normalized)
    wrong_spec_ids = _wrong_spec_ids(passport, response)
    limitations_preserved = _limitations_preserved(passport, question, normalized)
    competitor_context_present = _competitor_context_present(passport, question, normalized)
    buying_intent_matched = _buying_intent_matched(
        passport,
        question,
        normalized,
        limitations_preserved=limitations_preserved,
        competitor_context_present=competitor_context_present,
    )
    brand_mentioned = _contains_phrase(normalized, passport.brand.name)
    sku_mentioned = any(
        _contains_phrase(normalized, value)
        for value in [passport.sku.product_name, passport.sku.id, passport.sku.model_number]
        if value
    )
    canonical_url_cited = passport.canonical_url.lower() in response.lower()
    source_hash_cited = any(
        item.lower() in response.lower()
        for item in _source_hashes(passport)
        if item
    )
    score = _score(
        brand_mentioned=brand_mentioned,
        sku_mentioned=sku_mentioned,
        canonical_url_cited=canonical_url_cited,
        source_hash_cited=source_hash_cited,
        claim_coverage=claim_coverage,
        wrong_specs_present=bool(wrong_spec_ids),
        limitations_preserved=limitations_preserved,
        competitor_context_present=competitor_context_present,
        buying_intent_matched=buying_intent_matched,
        expects_limitations=bool(_expected_limitations(passport, question)),
        expects_competitor_context=bool(_expected_competitor_context(passport, question)),
    )
    run = RetrievalRun(
        id=_run_id(question.id, response, provider, model),
        question_id=question.id,
        ran_at=ran_at or datetime.now(timezone.utc).isoformat(),
        provider=provider,
        response_text=response,
        model=model,
        sku_ids=_sku_ids(passport, question),
        brand_mentioned=brand_mentioned,
        sku_mentioned=sku_mentioned,
        canonical_url_cited=canonical_url_cited,
        source_hash_cited=source_hash_cited,
        claim_coverage=claim_coverage,
        wrong_specs_present=bool(wrong_spec_ids),
        limitations_preserved=limitations_preserved,
        competitor_context_present=competitor_context_present,
        buying_intent_matched=buying_intent_matched,
        score=score,
        notes=_notes(
            claim_coverage=claim_coverage,
            wrong_spec_ids=wrong_spec_ids,
            canonical_url_cited=canonical_url_cited,
            source_hash_cited=source_hash_cited,
            limitations_preserved=limitations_preserved,
            competitor_context_present=competitor_context_present,
            buying_intent_matched=buying_intent_matched,
            expects_limitations=bool(_expected_limitations(passport, question)),
            expects_competitor_context=bool(_expected_competitor_context(passport, question)),
        ),
    )
    return SkuMonitorResult(
        retrieval_run=run,
        revision_suggestions=tuple(
            _revision_suggestions(
                passport,
                question,
                run,
                wrong_spec_ids=wrong_spec_ids,
            )
        ),
    )


def evaluate_sku_answer(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
    response_text: str,
    **kwargs: Any,
) -> SkuMonitorResult:
    return evaluate_sku_response(passport, question, response_text, **kwargs)


def _claim_coverage(claims: Iterable[ProductClaim], normalized: str) -> dict[str, str]:
    coverage: dict[str, str] = {}
    for claim in sorted(claims, key=lambda item: item.id):
        signal = _claim_signal(claim.claim)
        overlap = _term_overlap(normalized, signal)
        if overlap >= 0.6:
            coverage[claim.id] = "covered"
        elif overlap > 0:
            coverage[claim.id] = "partial"
        else:
            coverage[claim.id] = "missing"
    return coverage


def _wrong_spec_ids(passport: SkuSourcePassport, response: str) -> list[str]:
    wrong: list[str] = []
    for key, value in sorted(passport.facts.key_specs.items()):
        expected_values = _value_terms(value)
        if not expected_values:
            continue
        for sentence in _sentences(response):
            normalized_sentence = _normalize(sentence)
            if not _contains_phrase(normalized_sentence, key):
                continue
            if any(_contains_phrase(normalized_sentence, item) for item in expected_values):
                continue
            wrong.append(slugify(key))
            break
    return wrong


def _limitations_preserved(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
    normalized: str,
) -> bool:
    limitations = _expected_limitations(passport, question)
    return bool(limitations and any(_covered_text(normalized, item) for item in limitations))


def _competitor_context_present(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
    normalized: str,
) -> bool:
    contexts = _expected_competitor_context(passport, question)
    return bool(
        contexts
        and any(
            _covered_text(normalized, item.competitor_name)
            or _covered_text(normalized, item.competitor_product_name)
            or _covered_text(normalized, item.basis)
            for item in contexts
        )
    )


def _buying_intent_matched(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
    normalized: str,
    *,
    limitations_preserved: bool,
    competitor_context_present: bool,
) -> bool:
    if question.intent == "compare":
        return competitor_context_present
    if question.intent == "limitation":
        return limitations_preserved
    if question.intent == "compatibility":
        return any(_covered_text(normalized, item) for item in passport.facts.compatibility)
    if question.intent == "setup":
        return any(
            _covered_text(normalized, item)
            for item in [*passport.facts.requirements, *passport.facts.included_items]
        )
    expected = [*question.expected_facts, passport.facts.summary]
    return any(_covered_text(normalized, item) for item in expected)


def _score(
    *,
    brand_mentioned: bool,
    sku_mentioned: bool,
    canonical_url_cited: bool,
    source_hash_cited: bool,
    claim_coverage: dict[str, str],
    wrong_specs_present: bool,
    limitations_preserved: bool,
    competitor_context_present: bool,
    buying_intent_matched: bool,
    expects_limitations: bool,
    expects_competitor_context: bool,
) -> int:
    covered_count = sum(1 for status in claim_coverage.values() if status == "covered")
    partial_count = sum(1 for status in claim_coverage.values() if status == "partial")
    claim_points = 20
    if claim_coverage:
        claim_points = round(((covered_count + partial_count * 0.5) / len(claim_coverage)) * 20)

    score = 0
    score += 10 if brand_mentioned else 0
    score += 10 if sku_mentioned else 0
    score += 20 if canonical_url_cited else 0
    score += 10 if source_hash_cited else 0
    score += claim_points
    score += 15 if buying_intent_matched else 0
    score += 8 if limitations_preserved or not expects_limitations else 0
    score += 7 if competitor_context_present or not expects_competitor_context else 0
    if wrong_specs_present:
        score -= 25
    return max(0, min(100, score))


def _notes(
    *,
    claim_coverage: dict[str, str],
    wrong_spec_ids: list[str],
    canonical_url_cited: bool,
    source_hash_cited: bool,
    limitations_preserved: bool,
    competitor_context_present: bool,
    buying_intent_matched: bool,
    expects_limitations: bool,
    expects_competitor_context: bool,
) -> str:
    notes: list[str] = []
    if not canonical_url_cited:
        notes.append("Missing canonical SKU source URL citation.")
    if not source_hash_cited:
        notes.append("Missing SKU source or evidence hash citation.")
    missing_claims = [
        claim_id for claim_id, status in claim_coverage.items() if status == "missing"
    ]
    if missing_claims:
        notes.append("Missing claim coverage: " + ", ".join(missing_claims) + ".")
    if wrong_spec_ids:
        notes.append("Possible wrong specs: " + ", ".join(wrong_spec_ids) + ".")
    if expects_limitations and not limitations_preserved:
        notes.append("Expected limitations were not preserved.")
    if expects_competitor_context and not competitor_context_present:
        notes.append("Expected competitor context was not present.")
    if not buying_intent_matched:
        notes.append("Buying intent was not matched.")
    return " ".join(notes) or "No major SKU retrieval issue detected."


def _revision_suggestions(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
    run: RetrievalRun,
    *,
    wrong_spec_ids: list[str],
) -> list[RevisionSuggestion]:
    suggestions: list[RevisionSuggestion] = []
    if not run.canonical_url_cited or not run.source_hash_cited:
        suggestions.append(
            _suggestion(
                run,
                "missing-citation",
                "The answer did not cite the canonical SKU URL and source hash.",
                "source_page",
                (
                    "Add a compact citation block near the SKU answer section that repeats "
                    f"{passport.canonical_url} and source hash {passport.content_hash}."
                ),
                sku_ids=run.sku_ids,
                severity="high",
            )
        )
    for claim in sorted(passport.claims, key=lambda item: item.id):
        if run.claim_coverage.get(claim.id) != "missing":
            continue
        suggestions.append(
            _suggestion(
                run,
                f"missing-claim-{claim.id}",
                f"The answer missed claim {claim.id}.",
                "claim",
                f"Restate claim {claim.id} in a direct buying-question answer and keep its evidence IDs visible.",
                sku_ids=run.sku_ids,
                claim_ids=[claim.id],
                evidence_ids=claim.evidence_ids,
                severity="medium",
            )
        )
    if wrong_spec_ids:
        suggestions.append(
            _suggestion(
                run,
                "wrong-specs",
                "The answer appears to include specs that conflict with the SKU facts.",
                "evidence",
                "Make the contradicted spec labels and evidence excerpts more explicit in the SKU markdown asset.",
                sku_ids=run.sku_ids,
                evidence_ids=_all_evidence_ids(passport.evidence),
                severity="high",
            )
        )
    if _expected_limitations(passport, question) and not run.limitations_preserved:
        suggestions.append(
            _suggestion(
                run,
                "missing-limitations",
                "The answer did not preserve expected limitations.",
                "buying_question",
                f"Add the limitation caveat directly under buying question {question.id}.",
                sku_ids=run.sku_ids,
                severity="medium",
            )
        )
    if _expected_competitor_context(passport, question) and not run.competitor_context_present:
        suggestions.append(
            _suggestion(
                run,
                "missing-competitor-context",
                "The answer did not include the expected competitor context.",
                "competitor_context",
                f"Expose the competitor context IDs for buying question {question.id} in the comparison asset.",
                sku_ids=run.sku_ids,
                severity="low",
            )
        )
    if not suggestions:
        suggestions.append(
            _suggestion(
                run,
                "monitor-stable",
                "The monitored answer preserved the main SKU retrieval signals.",
                "source_page",
                "Keep the current SKU source stable and monitor additional buying questions before revising.",
                sku_ids=run.sku_ids,
                severity="low",
            )
        )
    return suggestions


def _suggestion(
    run: RetrievalRun,
    suffix: str,
    reason: str,
    target: str,
    action: str,
    *,
    sku_ids: Iterable[str] = (),
    claim_ids: Iterable[str] = (),
    evidence_ids: Iterable[str] = (),
    severity: str = "medium",
) -> RevisionSuggestion:
    return RevisionSuggestion(
        id=slugify(f"{run.id}-{suffix}"),
        source="retrieval_run",
        reason=reason,
        target=target,
        action=action,
        retrieval_run_id=run.id,
        sku_ids=list(_unique(sku_ids)),
        claim_ids=list(_unique(claim_ids)),
        evidence_ids=list(_unique(evidence_ids)),
        severity=severity,
        created_at=run.ran_at,
    )


def _expected_limitations(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
) -> list[str]:
    values = [*question.expected_limitations]
    if not values and question.intent in {"choose", "compare", "limitation"}:
        values.extend([*passport.sku.limitations, *passport.sku.not_for])
    return list(_unique(values))


def _expected_competitor_context(
    passport: SkuSourcePassport,
    question: BuyingQuestion,
):
    by_id = {item.id: item for item in passport.competitor_context}
    if question.competitor_context_ids:
        return [
            by_id[item]
            for item in _unique(question.competitor_context_ids)
            if item in by_id
        ]
    if question.intent == "compare":
        return sorted(passport.competitor_context, key=lambda item: item.id)
    return []


def _source_hashes(passport: SkuSourcePassport) -> list[str]:
    return [passport.content_hash, *[item.source_hash for item in passport.evidence]]


def _sku_ids(passport: SkuSourcePassport, question: BuyingQuestion) -> list[str]:
    return list(_unique(question.sku_ids or [passport.sku.id]))


def _run_id(question_id: str, response: str, provider: str, model: str) -> str:
    digest = hashlib.sha256(
        "\n".join([question_id, provider, model, response]).encode("utf-8")
    ).hexdigest()[:12]
    return slugify(f"{question_id}-{digest}")


def _claim_signal(value: str) -> list[str]:
    return [word for word in _normalize(value).split() if len(word) > 2][:8]


def _covered_text(normalized: str, value: str) -> bool:
    terms = [word for word in _normalize(value).split() if len(word) > 2]
    if not terms:
        return False
    needed = max(1, min(len(terms), round(len(terms) * 0.6)))
    return sum(1 for term in terms if term in normalized) >= needed


def _contains_phrase(normalized: str, value: str) -> bool:
    return bool(value and _normalize(value) in normalized)


def _contains_all_terms(normalized: str, terms: Iterable[str]) -> bool:
    term_list = list(terms)
    return bool(term_list and all(term in normalized for term in term_list))


def _contains_any_terms(normalized: str, terms: Iterable[str]) -> bool:
    term_list = list(terms)
    return bool(term_list and any(term in normalized for term in term_list))


def _term_overlap(normalized: str, terms: Iterable[str]) -> float:
    term_list = [term for term in terms if term]
    if not term_list:
        return 0.0
    matches = sum(1 for term in term_list if term in normalized)
    return matches / len(term_list)


def _value_terms(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, bool | int | float | str):
        return [str(value).strip()]
    return []


def _sentences(value: str) -> list[str]:
    normalized = value.replace("\n", ". ")
    for separator in [";", "!", "?"]:
        normalized = normalized.replace(separator, ".")
    return [item.strip() for item in normalized.split(".") if item.strip()]


def _all_evidence_ids(evidence: Iterable[Evidence]) -> list[str]:
    return [item.id for item in sorted(evidence, key=lambda item: item.id)]


def _unique(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    values: list[str] = []
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        values.append(text)
    return tuple(values)


def _normalize(value: str) -> str:
    return " ".join(str(value).lower().split())


__all__ = [
    "SkuMonitorResult",
    "evaluate_sku_answer",
    "evaluate_sku_response",
]
