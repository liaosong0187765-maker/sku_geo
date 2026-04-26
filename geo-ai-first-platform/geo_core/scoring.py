from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .model import KnowledgeCore


def _has(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, dict):
        return any(_has(v) for v in value.values())
    return True


def score(core: KnowledgeCore) -> Tuple[int, Dict[str, Dict[str, Any]], List[str]]:
    dimensions: Dict[str, Dict[str, Any]] = {}
    missing: List[str] = []

    entity_checks = {
        "name": _has(core.entity.get("name")),
        "url": _has(core.entity.get("url")),
        "category": _has(core.entity.get("category")),
        "one_line": _has(core.entity.get("one_line")),
        "description": _has(core.entity.get("description")),
    }
    _add_dimension(dimensions, missing, "entity_clarity", entity_checks)

    audience_checks = {
        "target_customers": _has(core.audience.get("target_customers")),
        "pain_points": _has(core.audience.get("pain_points")),
        "use_cases": _has(core.audience.get("use_cases")),
        "not_for": _has(core.audience.get("not_for")),
    }
    _add_dimension(dimensions, missing, "audience_clarity", audience_checks)

    qa_checks = {
        "at_least_5_questions": len(core.questions) >= 5,
        "answers_present": all(_has(q.answer) for q in core.questions),
        "limitations_present": any(_has(q.limitations) for q in core.questions),
        "cta_present": any(_has(q.cta) for q in core.questions),
    }
    _add_dimension(dimensions, missing, "answer_readiness", qa_checks)

    evidence_checks = {
        "claims_present": len(core.claims) >= 3,
        "sources_present": len(core.sources) >= 2,
        "claims_have_evidence": all(_has(c.evidence) for c in core.claims),
        "claims_link_sources": all(_has(c.source) for c in core.claims),
    }
    _add_dimension(dimensions, missing, "evidence_chain", evidence_checks)

    artifact_checks = {
        "products_present": len(core.products) >= 1,
        "product_features": any(_has(p.features) for p in core.products),
        "product_benefits": any(_has(p.benefits) for p in core.products),
        "pricing_or_limitations": any(_has(p.pricing) or _has(p.limitations) for p in core.products),
        "competitors_or_comparison": _has(core.competitors),
    }
    _add_dimension(dimensions, missing, "artifact_completeness", artifact_checks)

    total = round(sum(d["score"] for d in dimensions.values()) / len(dimensions))
    return total, dimensions, missing


def _add_dimension(dimensions: Dict[str, Dict[str, Any]], missing: List[str], name: str, checks: Dict[str, bool]) -> None:
    passed = sum(1 for ok in checks.values() if ok)
    total = len(checks)
    dimensions[name] = {
        "score": round((passed / total) * 100),
        "passed": passed,
        "total": total,
        "checks": checks,
    }
    for check_name, ok in checks.items():
        if not ok:
            missing.append(f"{name}.{check_name}")
