# Phase 6 Summary - SKU Retrieval Monitor and Revision Suggestions

## Scope

Phase 6 added deterministic SKU retrieval monitoring and revision suggestion generation for provided AI response text.

## Files Added

- `src/creator_passport/sku_monitor.py`
- `tests/test_sku_monitor.py`

## Behavior

- Evaluates a provided response against a `SkuSourcePassport` and `BuyingQuestion`.
- Produces `RetrievalRun` and `RevisionSuggestion` compatible objects without mutating the canonical passport.
- Scores brand mention, SKU mention, canonical URL citation, source hash citation, claim coverage, wrong specs, limitation preservation, competitor context, buying intent, and overall score.
- Creates suggestions linked to run, SKU, claim, and evidence IDs where applicable.
- Leaves the existing Creator monitor workflow unchanged.

## Verification

- `python -m unittest tests.test_sku_monitor` passed.
- `python -m unittest discover tests` passed.
- `python -m compileall src tests` passed.

## Review Gate

Verdict: `PASS_WITH_NOTES`.

Notes carried forward:

- `ran_at` defaults to the current timestamp, so callers that need byte-for-byte deterministic `RetrievalRun` output should pass an explicit timestamp.
- Retrieval runs and revision suggestions remain runtime monitoring state and do not participate in canonical `content_hash` / path semantics.
- Limitation and competitor suggestions are specific enough for MVP, but future refinements can add finer-grained limitation or context IDs.
- MarkItDown and Crawl4AI adapters must stay outside `sku_monitor`; they should only produce source/evidence text for intake.

## Next Boundary

Phase 7 may start. It should add optional MarkItDown and Crawl4AI adapter boundaries without making either project core runtime infrastructure.
