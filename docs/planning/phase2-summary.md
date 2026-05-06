# Phase 2 Summary: Source Intake Interface

Date: 2026-05-06
Branch: codex-auto
Status: implemented, reviewed, and verified

## Scope

Phase 2 adds a manual source intake interface. It supports manual Markdown and local UTF-8 `.md`, `.markdown`, `.txt`, and `.text` files only.

It does not add network fetching, MarkItDown, Crawl4AI, Firecrawl, external APIs, publishing automation, CMS features, or social scheduling.

## Subagent Work

- Intake implementation worker created `src/creator_passport/intake.py`.
- Intake test worker created `tests/test_intake.py`.
- Test fix worker removed `TemporaryDirectory` cleanup dependence that failed in the Windows sandbox.
- Hardening worker added approved-root checks, global `external/` path rejection, strict deserialization, and expanded tests.

## Decisions

- `RawSourceDocument.content_hash` is based only on UTF-8 `raw_markdown`.
- `from_local_file()` reads files only after approved-root and extension checks.
- Any resolved path with a component named `external`, case-insensitive, is rejected.
- `from_dict(strict=True)` rejects missing identity fields and unknown keys.
- `from_dict(strict=False)` remains convenient for internal callers and fills identity fields.

## Changed Files

- `src/creator_passport/intake.py`
- `tests/test_intake.py`
- `docs/planning/phase2-summary.md`

## Review Gate

Initial review returned `PASS_WITH_CONCERNS` for path boundary and strict validation risks. Those concerns were fixed before proceeding.

Main-thread scoped review passed after verifying:

- no network or external dependencies
- no MarkItDown, Crawl4AI, or Firecrawl
- approved-root guard
- global `external/` rejection
- strict unknown-key rejection
- hash mismatch rejection
- UTF-8 file intake coverage

## Verification

Passed:

```powershell
python -m unittest tests.test_intake
python -m unittest discover tests
python -m compileall src tests
```

Results:

- Intake tests: 18 passed.
- Full unittest discovery: 31 passed.
- Compileall: passed.

## Next Phase Boundary

Phase 3 should build a deterministic SKU fact extractor from `RawSourceDocument` and `SkuSourcePassport` structures. It must pass explicit `approved_roots` whenever reading local source files. Do not add external adapters or LLM dependencies in Phase 3.
