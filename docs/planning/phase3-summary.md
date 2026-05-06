# Phase 3 Summary - SKU Fact Extractor

## Scope

Phase 3 added a deterministic SKU fact extraction layer on top of the Phase 1 domain contract and Phase 2 intake records.

## Files Added

- `src/creator_passport/sku_extract.py`
- `tests/test_sku_extract.py`

## Decisions

- Keep extraction stdlib-only and deterministic.
- Do not call LLMs, network services, crawlers, or external adapters.
- Extract `ProductClaim` only from explicit `Claim` / `Claims` labels or sections.
- Do not infer facts or claims from unlabeled marketing copy.
- Bind evidence to source records using source hash, section, line number, and excerpt.
- Keep SKU extraction additive; the existing Creator Source Passport workflow remains unchanged.

## Verification

- `python -m unittest tests.test_sku_extract` passed.
- `python -m unittest discover tests` passed.
- `python -m compileall src tests` passed.

## Review Gate

Verdict: `PASS_WITH_NOTES`.

Notes carried into Phase 4:

- `limitations`, `use_cases`, and `not_for` are currently extractor outputs, but are not fields on `SkuFacts` or `SkuSourcePassport`. Phase 4 must not silently drop or invent passport fields for them without an explicit mapping decision.
- Evidence IDs are stable for the same source record content, section, line number, and excerpt. They are not guaranteed to survive arbitrary document reformatting.

## Next Boundary

Phase 4 may start. It should add a product AI pack renderer without modifying the existing Creator renderer unless absolutely necessary.
