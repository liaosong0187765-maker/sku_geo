from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .models import ValidationError
from .sku_models import (
    BuyingQuestion,
    RetrievalRun,
    RevisionSuggestion,
    SkuSourcePassport,
)
from .sku_monitor import evaluate_sku_response


def load_runs(path: str | Path) -> list[RetrievalRun]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_runs = data.get("retrieval_runs") or data.get("runs") if isinstance(data, dict) else data
    if not isinstance(raw_runs, list):
        raise ValidationError("Runs JSON must be a list or contain retrieval_runs/runs.")
    return [RetrievalRun.from_dict(item) for item in raw_runs if isinstance(item, dict)]


def write_batch_monitor_outputs(
    passports: Iterable[SkuSourcePassport],
    out_dir: Path,
    *,
    runs: Iterable[RetrievalRun] | None = None,
) -> list[Path]:
    passport_list = list(passports)
    run_list = list(runs or _embedded_runs(passport_list))
    results = evaluate_batch(passport_list, run_list)
    latest_runs = [item["retrieval_run"] for item in results]
    suggestions = _dedupe_suggestions(
        RevisionSuggestion.from_dict(item)
        for result in results
        for item in result["revision_suggestions"]
    )

    monitor_dir = out_dir / "monitor"
    monitor_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        monitor_dir / "latest-runs.json",
        monitor_dir / "report.md",
        out_dir / "revision_suggestions.json",
        out_dir / "revision_suggestions.md",
    ]
    paths[0].write_text(
        json.dumps({"retrieval_runs": latest_runs}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths[1].write_text(render_batch_report(results) + "\n", encoding="utf-8")
    paths[2].write_text(
        json.dumps(
            {"revision_suggestions": [item.to_dict() for item in suggestions]},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    paths[3].write_text(render_revision_suggestions_markdown(suggestions) + "\n", encoding="utf-8")
    return paths


def evaluate_batch(
    passports: list[SkuSourcePassport],
    runs: list[RetrievalRun],
) -> list[dict[str, Any]]:
    passports_by_sku = {passport.sku.id: passport for passport in passports}
    questions_by_id = _questions_by_id(passports)
    results: list[dict[str, Any]] = []
    for run in runs:
        question = questions_by_id.get(run.question_id)
        if question is None:
            raise ValidationError(f"Retrieval run {run.id} references unknown question_id {run.question_id}.")
        target_passports = _target_passports(passports, passports_by_sku, run, question)
        for passport in target_passports:
            result = evaluate_sku_response(
                passport,
                question,
                run.response_text,
                provider=run.provider,
                model=run.model,
                ran_at=run.ran_at,
            )
            evaluated = result.retrieval_run.to_dict()
            evaluated["id"] = run.id
            evaluated["sku_ids"] = [passport.sku.id]
            results.append(
                {
                    "input_run_id": run.id,
                    "sku_id": passport.sku.id,
                    "question": question.to_dict(),
                    "retrieval_run": evaluated,
                    "revision_suggestions": [
                        {
                            **suggestion.to_dict(),
                            "id": f"{run.id}-{suggestion.id}",
                            "retrieval_run_id": run.id,
                            "sku_ids": [passport.sku.id],
                        }
                        for suggestion in result.revision_suggestions
                    ],
                }
            )
    return results


def render_batch_report(results: list[dict[str, Any]]) -> str:
    rows = ["# SKU Batch Retrieval Monitor", ""]
    if not results:
        rows.append("No retrieval runs supplied.")
        return "\n".join(rows)
    scores = [item["retrieval_run"]["score"] for item in results if item["retrieval_run"].get("score") is not None]
    if scores:
        rows.extend([f"Average score: {round(sum(scores) / len(scores), 1)}", ""])
    rows.extend(["## Runs", ""])
    for item in results:
        run = item["retrieval_run"]
        rows.extend(
            [
                f"### {run['id']}",
                "",
                f"- SKU: {item['sku_id']}",
                f"- Question: {item['question']['question']}",
                f"- Provider: {run['provider']}",
                f"- Score: {run['score']}",
                f"- Canonical URL cited: {run['canonical_url_cited']}",
                f"- Source hash cited: {run['source_hash_cited']}",
                f"- Wrong specs present: {run['wrong_specs_present']}",
                f"- Notes: {run['notes']}",
                "",
            ]
        )
    rows.extend(["## Revision Suggestions", ""])
    for suggestion in _dedupe_suggestions(
        RevisionSuggestion.from_dict(raw)
        for item in results
        for raw in item["revision_suggestions"]
    ):
        rows.append(f"- [{suggestion.severity}] {suggestion.target}: {suggestion.reason} Action: {suggestion.action}")
    return "\n".join(rows).strip()


def render_revision_suggestions_markdown(suggestions: list[RevisionSuggestion]) -> str:
    rows = ["# SKU Revision Suggestions", ""]
    if not suggestions:
        rows.append("- No revision suggestions.")
        return "\n".join(rows)
    for suggestion in suggestions:
        rows.extend(
            [
                f"## {suggestion.id}",
                "",
                f"- Severity: {suggestion.severity}",
                f"- Target: {suggestion.target}",
                f"- Reason: {suggestion.reason}",
                f"- Action: {suggestion.action}",
                f"- SKU IDs: {', '.join(suggestion.sku_ids)}",
                "",
            ]
        )
    return "\n".join(rows).strip()


def _embedded_runs(passports: Iterable[SkuSourcePassport]) -> list[RetrievalRun]:
    runs: list[RetrievalRun] = []
    seen: set[str] = set()
    for passport in passports:
        for run in passport.retrieval_runs:
            if run.id in seen:
                continue
            seen.add(run.id)
            runs.append(run)
    return runs


def _questions_by_id(passports: Iterable[SkuSourcePassport]) -> dict[str, BuyingQuestion]:
    questions: dict[str, BuyingQuestion] = {}
    for passport in passports:
        for question in passport.buying_questions:
            questions[question.id] = question
    return questions


def _target_passports(
    passports: list[SkuSourcePassport],
    passports_by_sku: dict[str, SkuSourcePassport],
    run: RetrievalRun,
    question: BuyingQuestion,
) -> list[SkuSourcePassport]:
    sku_ids = run.sku_ids or question.sku_ids
    if not sku_ids:
        return passports
    missing = [item for item in sku_ids if item not in passports_by_sku]
    if missing:
        raise ValidationError(f"Retrieval run {run.id} references unknown SKU IDs: {', '.join(missing)}.")
    return [passports_by_sku[item] for item in sku_ids]


def _dedupe_suggestions(suggestions: Iterable[RevisionSuggestion]) -> list[RevisionSuggestion]:
    seen: set[str] = set()
    result: list[RevisionSuggestion] = []
    for suggestion in suggestions:
        if suggestion.id in seen:
            continue
        seen.add(suggestion.id)
        result.append(suggestion)
    return sorted(result, key=lambda item: item.id)


__all__ = [
    "evaluate_batch",
    "load_runs",
    "render_batch_report",
    "render_revision_suggestions_markdown",
    "write_batch_monitor_outputs",
]
