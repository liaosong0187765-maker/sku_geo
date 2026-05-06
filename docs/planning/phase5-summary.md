# Phase 5 Summary - Buying Questions, FAQ, and Comparisons

## Scope

Phase 5 added deterministic buying question, FAQ, and comparison generation on top of the SKU Source Passport domain model.

## Files Added

- `src/creator_passport/sku_questions.py`
- `tests/test_sku_questions.py`

## Behavior

- Generates buying question and FAQ answers from `SkuSourcePassport`.
- Prefers explicit `BuyingQuestion.expected_facts` and `expected_limitations`.
- Falls back only to explicit `SkuFacts` and SKU limitation fields when question-level expectations are absent.
- Binds matching `ProductClaim.id` and `Evidence.id` when available.
- Renders comparison sections only from explicit `CompetitorContext` fields.
- Does not invent competitor pricing, rankings, performance, reviews, or unsupported advantages.
- Leaves the existing Creator Source Passport workflow unchanged.

## Verification

- `python -m unittest tests.test_sku_questions` passed.
- `python -m unittest discover tests` passed.
- `python -m compileall src tests` passed.

## Review Gate

Verdict: `PASS_WITH_NOTES`.

Notes carried forward:

- `SkuSourcePassport.compute_hash()` does not include `retrieval_runs` or `revision_suggestions`, while `to_dict()` can output them.
- Phase 6 should treat retrieval runs and revision suggestions as runtime monitoring state unless there is an explicit versioning decision.
- Monitor output should not silently change the canonical SKU passport path or content hash.

## Next Boundary

Phase 6 may start. It should add SKU retrieval monitoring and revision suggestions while preserving canonical source hash semantics.
