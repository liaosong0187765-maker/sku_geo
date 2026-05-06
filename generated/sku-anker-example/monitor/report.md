# SKU Batch Retrieval Monitor

Average score: 30.0

## Runs

### sample-run-anker-missing-citation

- SKU: anker-735-charger-nano-ii-65w-a2667
- Question: Can Anker 735 Charger provide up to 65W from one USB-C port?
- Provider: manual-fixture
- Score: 35
- Canonical URL cited: False
- Source hash cited: False
- Wrong specs present: False
- Notes: Missing canonical SKU source URL citation. Missing SKU source or evidence hash citation. Buying intent was not matched.

### sample-run-anker-wrong-s22-limitation

- SKU: anker-735-charger-nano-ii-65w-a2667
- Question: Does Anker 735 Charger support Samsung S22 Ultra 45W Super Fast Charging 2.0?
- Provider: manual-fixture
- Score: 25
- Canonical URL cited: False
- Source hash cited: False
- Wrong specs present: True
- Notes: Missing canonical SKU source URL citation. Missing SKU source or evidence hash citation. Missing claim coverage: claim-cable-requirements. Possible wrong specs: ports.

## Revision Suggestions

- [high] source_page: The answer did not cite the canonical SKU URL and source hash. Action: Add a compact citation block near the SKU answer section that repeats https://www.anker.com/sku/anker-735-charger-nano-ii-65w-a2667-e708a9c8c5c8 and source hash e708a9c8c5c8.
- [high] source_page: The answer did not cite the canonical SKU URL and source hash. Action: Add a compact citation block near the SKU answer section that repeats https://www.anker.com/sku/anker-735-charger-nano-ii-65w-a2667-e708a9c8c5c8 and source hash e708a9c8c5c8.
- [medium] claim: The answer missed claim claim-cable-requirements. Action: Restate claim claim-cable-requirements in a direct buying-question answer and keep its evidence IDs visible.
- [high] evidence: The answer appears to include specs that conflict with the SKU facts. Action: Make the contradicted spec labels and evidence excerpts more explicit in the SKU markdown asset.
