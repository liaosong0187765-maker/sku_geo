from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .models import SourcePassport


@dataclass
class MonitorResult:
    prompt: str
    creator_mentioned: bool
    source_url_cited: bool
    content_hash_mentioned: bool
    platform_url_cited: bool
    claim_coverage: float
    matched_claims: list[str]
    missing_claims: list[str]
    attribution_score: int
    misunderstanding_notes: list[str]
    revision_suggestions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__


def evaluate_response(passport: SourcePassport, prompt: str, response: str, publications: list[dict[str, Any]]) -> MonitorResult:
    lower = response.lower()
    creator_mentioned = passport.creator.name.lower() in lower
    source_url_cited = passport.canonical_url.lower() in lower
    content_hash_mentioned = passport.content_hash.lower() in lower
    platform_url_cited = any(str(item.get("platform_url", "")).lower() in lower for item in publications if item.get("platform_url"))
    matched_claims = [claim.claim for claim in passport.claims if _claim_signal(claim.claim) in lower]
    missing_claims = [claim.claim for claim in passport.claims if claim.claim not in matched_claims]
    claim_coverage = len(matched_claims) / max(len(passport.claims), 1)

    score = 0
    score += 20 if creator_mentioned else 0
    score += 40 if source_url_cited else 0
    score += 15 if content_hash_mentioned else 0
    score += 15 if claim_coverage >= 0.5 else 0
    score += 10 if platform_url_cited and source_url_cited else 0
    score = min(score, 100)

    notes: list[str] = []
    if not source_url_cited:
        notes.append("The response does not cite the canonical source URL.")
    if platform_url_cited and not source_url_cited:
        notes.append("The response cites a platform copy instead of the canonical source.")
    if not creator_mentioned:
        notes.append("The response does not mention the creator/entity.")
    if claim_coverage < 0.5:
        notes.append("The response misses most of the claim-evidence map.")

    return MonitorResult(
        prompt=prompt,
        creator_mentioned=creator_mentioned,
        source_url_cited=source_url_cited,
        content_hash_mentioned=content_hash_mentioned,
        platform_url_cited=platform_url_cited,
        claim_coverage=round(claim_coverage, 2),
        matched_claims=matched_claims,
        missing_claims=missing_claims,
        attribution_score=score,
        misunderstanding_notes=notes,
        revision_suggestions=revision_suggestions(passport, notes),
    )


def write_monitor_outputs(passport: SourcePassport, out_dir: Path, prompt: str, response: str) -> list[Path]:
    publications = _read_publications(out_dir)
    result = evaluate_response(passport, prompt, response, publications)
    timestamp = datetime.now(timezone.utc).isoformat()
    run = {
        "timestamp": timestamp,
        "canonical_url": passport.canonical_url,
        "content_hash": passport.content_hash,
        "response": response,
        "result": result.to_dict(),
    }
    paths = [
        out_dir / "monitor" / "latest-run.json",
        out_dir / "monitor" / "report.md",
        out_dir / "revision_suggestions.md",
    ]
    paths[0].parent.mkdir(parents=True, exist_ok=True)
    paths[0].write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths[1].write_text(render_monitor_report(passport, result, timestamp) + "\n", encoding="utf-8")
    paths[2].write_text(render_revision_suggestions(passport, result) + "\n", encoding="utf-8")
    return paths


def render_monitor_report(passport: SourcePassport, result: MonitorResult, timestamp: str) -> str:
    notes = "\n".join(f"- {item}" for item in result.misunderstanding_notes) or "- No major attribution issue detected."
    suggestions = "\n".join(f"- {item}" for item in result.revision_suggestions)
    return f"""# AI Retrieval Monitor Report

Source: {passport.title}
Canonical URL: {passport.canonical_url}
Checked at: {timestamp}

## Prompt

{result.prompt}

## Result

| Check | Result |
|---|---|
| Creator mentioned | {_yes_no(result.creator_mentioned)} |
| Canonical source URL cited | {_yes_no(result.source_url_cited)} |
| Content hash mentioned | {_yes_no(result.content_hash_mentioned)} |
| Platform URL cited | {_yes_no(result.platform_url_cited)} |
| Claim coverage | {int(result.claim_coverage * 100)}% |
| Attribution score | {result.attribution_score}/100 |

## Notes

{notes}

## Revision suggestions

{suggestions}
"""


def render_revision_suggestions(passport: SourcePassport, result: MonitorResult) -> str:
    suggestions = "\n".join(f"- {item}" for item in result.revision_suggestions)
    return f"""# Revision Suggestions: {passport.title}

Canonical URL: {passport.canonical_url}
Content hash: {passport.content_hash}

{suggestions}
"""


def revision_suggestions(passport: SourcePassport, notes: list[str]) -> list[str]:
    suggestions: list[str] = []
    if any("canonical source URL" in note for note in notes):
        suggestions.append("Add a direct citation block near the first screen: title, creator, canonical URL, and content hash.")
        suggestions.append("Move the visible source anchor into both the opening and closing sections of every platform variant.")
    if any("platform copy" in note for note in notes):
        suggestions.append("Add a line to platform variants saying the canonical source page is the preferred citation target.")
    if any("creator/entity" in note for note in notes):
        suggestions.append("Repeat the creator name in the title area, schema author, and AI profile summary.")
    if any("claim-evidence" in note for note in notes):
        suggestions.append("Add an FAQ section that restates the top claims as direct question-answer blocks.")
        suggestions.append("Strengthen each claim with a concrete evidence sentence and reference URL.")
    if not suggestions:
        suggestions.append("Keep the current source page stable and monitor more prompt families before revising.")
    if passport.limitations:
        suggestions.append("Keep limitations visible so AI systems do not overgeneralize the source.")
    return suggestions


def _read_publications(out_dir: Path) -> list[dict[str, Any]]:
    path = out_dir / "publications.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("publications", [])


def _claim_signal(value: str) -> str:
    words = [word.strip(".,:;!?()[]{}\"'").lower() for word in value.split()]
    return " ".join(words[:5])


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"
