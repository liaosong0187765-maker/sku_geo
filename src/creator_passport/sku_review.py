from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from .models import ValidationError
from .sku_models import SkuSourcePassport


@dataclass(frozen=True)
class SkuReviewIssue:
    sku_id: str
    severity: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "sku_id": self.sku_id,
            "severity": self.severity,
            "reason": self.reason,
        }


def build_review(passports: Iterable[SkuSourcePassport]) -> dict[str, Any]:
    items = list(passports)
    issues = _review_issues(items)
    return {
        "status": "blocked" if any(item.severity == "error" for item in issues) else "ready_for_human_review",
        "sku_count": len(items),
        "issues": [item.to_dict() for item in issues],
        "skus": [_sku_review_item(item) for item in sorted(items, key=lambda passport: passport.sku.id)],
    }


def write_review_artifacts(passports: Iterable[SkuSourcePassport], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    review = build_review(passports)
    paths = [
        out_dir / "sku-review.json",
        out_dir / "sku-review.md",
    ]
    paths[0].write_text(json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths[1].write_text(render_review_markdown(review) + "\n", encoding="utf-8")
    if review["status"] == "blocked":
        reasons = "; ".join(item["reason"] for item in review["issues"] if item["severity"] == "error")
        raise ValidationError(f"SKU review blocked: {reasons}")
    return paths


def render_review_markdown(review: dict[str, Any]) -> str:
    rows = [
        "# SKU Human Review",
        "",
        f"Status: {review['status']}",
        f"SKU count: {review['sku_count']}",
        "",
        "## Issues",
        "",
    ]
    if review["issues"]:
        rows.extend(
            f"- [{item['severity']}] {item['sku_id']}: {item['reason']}"
            for item in review["issues"]
        )
    else:
        rows.append("- No blocking review issues detected.")
    rows.extend(["", "## SKU Checklist", ""])
    for item in review["skus"]:
        rows.extend(
            [
                f"### {item['product_name']}",
                "",
                f"- SKU ID: {item['sku_id']}",
                f"- Status: {item['status']}",
                f"- Claims: {item['claim_count']}",
                f"- Evidence sources: {item['evidence_count']}",
                f"- Missing evidence IDs: {', '.join(item['missing_evidence_ids']) or 'none'}",
                f"- Limitations: {item['limitations'] or 'none listed'}",
                f"- Not for: {item['not_for'] or 'none listed'}",
                f"- Competitor context: {item['competitor_context_count']}",
                f"- Open revision suggestions: {item['open_revision_suggestion_count']}",
                "",
            ]
        )
    return "\n".join(rows).strip()


def _review_issues(passports: list[SkuSourcePassport]) -> list[SkuReviewIssue]:
    issues: list[SkuReviewIssue] = []
    for passport in passports:
        evidence_ids = {item.id for item in passport.evidence}
        if passport.sku.status == "draft":
            issues.append(
                SkuReviewIssue(
                    passport.sku.id,
                    "warning",
                    "SKU status is draft; human approval should happen before publication.",
                )
            )
        for claim in passport.claims:
            if not claim.evidence_ids:
                issues.append(
                    SkuReviewIssue(passport.sku.id, "error", f"Claim {claim.id} has no evidence IDs.")
                )
            missing = [item for item in claim.evidence_ids if item not in evidence_ids]
            if missing:
                issues.append(
                    SkuReviewIssue(
                        passport.sku.id,
                        "error",
                        f"Claim {claim.id} references missing evidence IDs: {', '.join(missing)}.",
                    )
                )
        if passport.claims and not passport.evidence:
            issues.append(
                SkuReviewIssue(passport.sku.id, "error", "Claims exist but no evidence sources are listed.")
            )
    return issues


def _sku_review_item(passport: SkuSourcePassport) -> dict[str, Any]:
    evidence_ids = {item.id for item in passport.evidence}
    missing_evidence_ids = sorted(
        {
            evidence_id
            for claim in passport.claims
            for evidence_id in claim.evidence_ids
            if evidence_id not in evidence_ids
        }
    )
    return {
        "sku_id": passport.sku.id,
        "product_name": passport.sku.product_name,
        "status": passport.sku.status,
        "canonical_url": passport.canonical_url,
        "content_hash": passport.content_hash,
        "claim_count": len(passport.claims),
        "evidence_count": len(passport.evidence),
        "missing_evidence_ids": missing_evidence_ids,
        "limitations": "; ".join(passport.sku.limitations),
        "not_for": "; ".join(passport.sku.not_for),
        "competitor_context_count": len(passport.competitor_context),
        "open_revision_suggestion_count": sum(
            1 for item in passport.revision_suggestions if item.status == "open"
        ),
        "claims": [claim.to_dict() for claim in sorted(passport.claims, key=lambda item: item.id)],
        "evidence": [item.to_dict() for item in sorted(passport.evidence, key=lambda item: item.id)],
    }


__all__ = [
    "SkuReviewIssue",
    "build_review",
    "render_review_markdown",
    "write_review_artifacts",
]
