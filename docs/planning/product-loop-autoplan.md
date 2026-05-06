# SKU Source Passport Product Loop Autoplan

Date: 2026-05-06
Branch: codex-auto
Status: planning only; no implementation in this pass

## Goal

打通 SKU Source Passport Engine 的最小产品闭环：

```text
3-5 SKUs
  -> structured SKU input
  -> source intake / fact extraction boundary
  -> human review checkpoint
  -> product source pack
  -> batch retrieval monitor
  -> revision report
```

This remains a local-first engine on top of the existing Source Passport skeleton:

```text
model -> render -> variants / publish record boundary -> monitor -> revision suggestions
```

It must not become a generic GEO SaaS, CMS, social scheduler, publisher robot, or external-platform clone.

## Subagent Review Summary

Four read-only subagents reviewed the plan with bounded scopes.

| Agent | Key Finding |
|---|---|
| CEO / Product Loop | MVP value is not "more content"; it is durable product facts, evidence, AI-readable source packs, monitoring, and revision suggestions for real buyer questions. |
| Engineering Architecture | Current SKU modules are strong but still lack orchestration, human review artifacts, batch monitor output, and catalog-level multi-SKU rendering. |
| DX / CLI | MVP should start with structured `sku-source.json` and manually captured AI responses. Crawling, AI fact generation, scheduling, dashboards, and CMS are out of scope. |
| Test / Acceptance | Existing tests cover low-level SKU modules. Missing tests are the 3-5 SKU end-to-end orchestration, review checkpoint, batch monitor, and multi-SKU index. |

## What Already Exists

Implemented and covered by existing phase summaries:

- `src/creator_passport/sku_models.py`: Brand, SKU, SkuFacts, ProductClaim, Evidence, CompetitorContext, BuyingQuestion, RetrievalRun, RevisionSuggestion, SkuSourcePassport.
- `src/creator_passport/intake.py`: manual markdown and local approved-file `RawSourceDocument` intake.
- `src/creator_passport/sku_extract.py`: deterministic explicit-label fact extraction with evidence pointers.
- `src/creator_passport/sku_render.py`: SKU product pack rendering for canonical HTML/markdown, AI assets, schema, sitemap, robots, FAQ, comparison JSON.
- `src/creator_passport/sku_questions.py`: deterministic FAQ, buying question, and comparison generation.
- `src/creator_passport/sku_monitor.py`: one-question SKU answer evaluation and revision suggestions.
- `src/creator_passport/sku_adapters.py`: optional MarkItDown and Crawl4AI adapter boundaries.
- `src/creator_passport/__main__.py`: current Creator CLI plus `sku-generate` and `sku-check`.

Existing test coverage:

- `tests/test_workflow.py`: Creator Source Passport closed loop.
- `tests/test_sku_models.py`: SKU domain model and excluded commercial fields.
- `tests/test_intake.py`: source intake path and strictness boundaries.
- `tests/test_sku_extract.py`: deterministic fact extraction and evidence binding.
- `tests/test_sku_render.py`: SKU pack artifacts and no hardcoded demo/brand assumptions.
- `tests/test_sku_questions.py`: grounded FAQ/comparison generation.
- `tests/test_sku_monitor.py`: SKU retrieval scoring and suggestions.
- `tests/test_sku_adapters.py`: optional adapter boundaries.
- `tests/test_sku_cli.py`: current `sku-generate` / `sku-check` smoke path and multiple SKU product markdown output.

## Confirmed Gaps

1. `sku-generate` is not yet the product loop. It generates assets but does not orchestrate intake, review, catalog rendering, monitor, and revision report.
2. Multi-SKU handling risks global artifact overwrite because repeated single-SKU rendering can overwrite `index.html`, `llms.txt`, `schema.json`, `sitemap.xml`, and `robots.txt`.
3. There is no explicit human review artifact between extraction and rendering.
4. Batch monitor is missing. Current SKU monitor evaluates one provided response against one buying question.
5. There is no SKU publish record boundary equivalent for deployment handoff / hosted URL records.
6. README does not yet describe the SKU product-loop CLI path.

## Recommended Route

Build the loop in five narrow engineering passes:

```text
Pass A: catalog-level build command
Pass B: human review artifact
Pass C: catalog-level renderer / multi-SKU index
Pass D: batch retrieval monitor
Pass E: docs and handoff
```

This route reuses the completed Phase 1-7 modules and adds orchestration above them. It avoids rewriting the existing Creator workflow and avoids pulling optional adapters into the core path.

## Rejected Routes

| Route | Decision | Reason |
|---|---|---|
| GEOFlow-style content factory | Reject | Pulls in tasks, queues, knowledge base admin, CMS, and publishing scope before the SKU source loop is proven. |
| Postiz / Mixpost as core | Reject | Turns source-pack generation into social publishing infrastructure. Keep only future adapter reference. |
| Full CMS with Payload / TinaCMS | Reject | Solves editing/versioning too early and expands product surface beyond MVP. |
| Web crawler first | Reject for next pass | Crawling increases network, dependency, and safety complexity. Structured JSON plus manual responses can prove the closed loop faster. |
| LLM fact extractor first | Reject for next pass | The highest current risk is unsupported facts. Deterministic extraction plus human review should stay the default. |
| Rewrite Creator renderer / monitor | Reject | Existing Creator Source Passport workflow is a regression boundary. SKU should remain additive. |

## Engineering Plan

### Pass A: `sku-build` Orchestration

Goal:
Add a thin CLI command that turns one `sku-source.json` containing 3-5 SKUs into a complete build run.

Modify:
- `src/creator_passport/__main__.py`
- New `src/creator_passport/sku_build.py`
- `tests/test_sku_cli.py` or new `tests/test_sku_build.py`

Do not modify:
- `src/creator_passport/models.py`
- `src/creator_passport/render.py`
- `src/creator_passport/variants.py`
- `src/creator_passport/monitor.py`
- external project folders

Acceptance:
- `python -m creator_passport sku-build sku-source.json --out generated/sku` loads all SKUs.
- Output contains one complete source page per SKU.
- Output contains catalog-level AI index artifacts.
- Failures identify the bad SKU id and reason.
- Existing `sku-generate` remains available as a compatibility alias or lower-level command.

Tests:
- 3 SKU input builds without flattening to the first SKU.
- Invalid SKU fails with actionable error.
- Existing Creator workflow tests still pass.

Risks:
- Accidentally hiding current `sku-generate` behavior.
- Global files overwritten by single-SKU renderer.

Needs user confirmation:
- No, if scoped to CLI alias/orchestration only.

### Pass B: Human Review Artifact

Goal:
Add a required review artifact boundary so extracted or loaded facts can be reviewed before source-pack publication.

Modify:
- New `src/creator_passport/sku_review.py`
- `src/creator_passport/__main__.py`
- Tests for review output

Do not modify:
- SKU hash semantics unless explicitly required.
- Creator workflow files.

Acceptance:
- `sku-review OUT --input sku-source.json` writes or validates `sku-review.json` and `sku-review.md`.
- Review artifact lists facts, claims, evidence ids, missing evidence, limitations, not-for notes, competitor context, and open revision suggestions.
- Unsupported claims fail review or are clearly flagged.

Tests:
- Claims without evidence fail review.
- Forbidden commercial fields are ignored or flagged.
- Review output is deterministic enough for assertions.

Risks:
- Making review state part of canonical hash too early.
- Turning review into a CMS workflow.

Needs user confirmation:
- Yes only for exact approval semantics: warning-only vs fail-closed for unreviewed SKUs.

### Pass C: Catalog-Level Product Pack Renderer

Goal:
Create one brand/catalog source pack for 3-5 SKUs without global artifact overwrite.

Modify:
- `src/creator_passport/sku_render.py`
- `tests/test_sku_render.py`
- Possibly `src/creator_passport/sku_build.py`

Do not modify:
- Creator renderer.

Acceptance:
- New `write_catalog_pack(passports, out_dir)` writes global files once.
- Per-SKU files live at stable slug/hash paths.
- Global `index.html`, `llms.txt`, `llms-full.txt`, `schema.json`, `sitemap.xml`, `robots.txt`, `ai/product-index.md`, `ai/categories/*`, `ai/comparisons/*`, `ai/faq.md`, and `ai/buying-guide.md` include all SKUs.
- No demo company, demo SKU, or hardcoded brand strings.

Tests:
- 3 SKU catalog emits all SKU links.
- Sitemap and schema include all canonical SKU URLs.
- No single-SKU overwrite of global files.

Risks:
- Schema grows ambiguous if combining Product and FAQPage nodes without stable ids.
- Category slug collisions.

Needs user confirmation:
- No.

### Pass D: Batch Retrieval Monitor

Goal:
Run stored AI/search responses against buying questions and SKUs, then produce a report and revision suggestions.

Modify:
- New `src/creator_passport/sku_monitor_batch.py`
- `src/creator_passport/__main__.py`
- New tests

Do not modify:
- `src/creator_passport/monitor.py`
- Canonical hash semantics

Acceptance:
- `sku-monitor-batch sku-source.json --out generated/sku --runs runs.json` writes `monitor/latest-runs.json`, `monitor/report.md`, `revision_suggestions.md`, and optionally `revision_suggestions.json`.
- Each run is traceable to `question_id`, SKU ids, provider, response text, score, and detected failure modes.
- Monitor does not call AI services in MVP.

Tests:
- Missing citation creates source-page suggestion.
- Wrong spec creates evidence/claim suggestion.
- Missing limitation creates buying-question/source-page suggestion.
- Multiple questions across multiple SKUs aggregate cleanly.

Risks:
- Without a run schema, historical monitor output becomes hard to compare.
- Scores can look more precise than the deterministic evaluator supports.

Needs user confirmation:
- No, if monitor remains offline and fixture-based.

### Pass E: Docs And Deployment Handoff

Goal:
Document the SKU product-loop workflow so it can be operated end to end.

Modify:
- `README.md`
- `docs/SKU_SOURCE_INPUT_CONTRACT.md`
- `docs/PROJECT_GOAL_MODULE_BRIDGE_DESIGN.md` if only aligning command names and status
- Maybe `docs/planning/product-loop-handoff.md`

Do not modify:
- Implementation modules except if tests expose a docs-command mismatch.

Acceptance:
- README has SKU quickstart: prepare JSON, build, review, monitor-batch, inspect output.
- Input contract has minimal valid JSON shape without real/demo brand or SKU.
- Docs clearly state crawler/adapters are optional and not the MVP path.

Tests:
- No test needed for prose alone, but command examples should match CLI tests.

Risks:
- Adding fake sample data that violates no-demo boundary.

Needs user confirmation:
- No.

## Review Gate Between Passes

After each pass:

1. Run targeted tests for that pass.
2. Run existing Creator workflow tests.
3. Run full unittest discovery if the pass touches shared CLI/render/model paths.
4. Perform review before starting the next pass.
5. Confirm no new scope drift: CMS, SaaS, crawler-first, publisher bot, hardcoded demo, or commercial fields.

## First Implementation Task List

Start with Pass A only:

1. Add failing tests for 3 SKU `sku-build` output and catalog-level global artifacts.
2. Add `sku_build.py` orchestration wrapper around `load_sku_passports`.
3. Add `sku-build` CLI command as the primary product-loop entrypoint.
4. Keep `sku-generate` behavior compatible, or make it call the same build layer.
5. Wire current renderer carefully, but do not solve review or monitor in the same pass.
6. Run `python -m unittest tests.test_sku_cli tests.test_workflow`.
7. Review results before Pass B.

## Can Implementation Start?

Yes, implementation can start with Pass A.

The first pass does not require product confirmation if it is limited to orchestration and tests. User confirmation is needed before enforcing a fail-closed human review policy in Pass B.

