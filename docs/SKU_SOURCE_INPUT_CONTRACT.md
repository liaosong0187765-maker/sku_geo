# SKU Source Passport Phase 1 Input Contract

Status: Phase 1 contract  
Scope: input data only; no demo company, demo SKU, fixtures, or hardcoded brand assumptions.

## Purpose

The SKU Source Passport layer extends the existing Creator Source Passport workflow from creator-authored source material to product facts. It must preserve the current source-page, markdown mirror, source hash, canonical URL, source anchor, AI index, retrieval monitor, and revision suggestion loop.

Phase 1 accepts structured input for real brand-owned SKUs. It does not fetch, publish, price, promote, or manage inventory.

## Default Exclusions

Do not include these fields unless a later contract explicitly opts in:

- price
- inventory or stock status
- discount, coupon, bundle, campaign, or promotional claim
- marketplace ranking, review count, rating, or sales volume
- automated publishing credentials or platform account data

If supplied by upstream data, these values must be ignored or stored outside this contract.

## Root Shape

```json
{
  "brand": {},
  "skus": [],
  "competitor_context": [],
  "buying_questions": [],
  "retrieval_runs": [],
  "revision_suggestions": []
}
```

Only `brand` and at least one `skus[]` item are required for initial source-pack generation. Monitor and revision objects may be absent until retrieval checks run.

## Brand

Required:

- `id`: stable slug-style brand id.
- `name`: public brand name.
- `domain`: canonical brand domain or source host.

Optional:

- `market`: primary market or locale, for example `US`, `EU`, or `global`.
- `official_urls`: array of official home, support, warranty, FAQ, or documentation URLs.
- `description`: short factual brand description.

Validation:

- `id` must be lowercase letters, numbers, and hyphens.
- `name` must not be empty.
- `domain` must be a URL host or full HTTPS URL.
- `official_urls` must use `https://` unless explicitly marked as internal test data.

## SKU

Required:

- `id`: stable slug-style SKU id, unique within the brand.
- `brand_id`: references `Brand.id`.
- `product_name`: public product name.
- `category`: product category.
- `canonical_url`: official product source URL.
- `facts`: `SkuFacts`.

Optional:

- `model_number`: manufacturer model number.
- `slug`: preferred output slug; defaults from `product_name` or `id`.
- `status`: `draft`, `reviewed`, or `published`; defaults to `draft`.
- `source_urls`: official product, support, manual, FAQ, certification, or documentation URLs.
- `claims`: array of `ProductClaim`.
- `evidence`: array of `Evidence`.
- `limitations`: factual usage limits, exclusions, or caveats.
- `use_cases`: recommended scenarios.
- `not_for`: scenarios where the SKU should not be recommended.
- `compatibility_notes`: human-readable compatibility summary.
- `updated_at`: ISO date for the last human-approved fact update.

Validation:

- `id` must be unique and slug-safe.
- `canonical_url` must be official or brand-approved.
- Every claim must reference evidence.
- Facts must avoid unsupported marketing language.
- `updated_at`, when present, must be an ISO date.

## SkuFacts

Required:

- `summary`: one or two factual sentences describing what the SKU is.
- `key_specs`: object of normalized specification names to values.

Optional:

- `positioning`: factual product positioning.
- `dimensions`: size or weight facts.
- `materials`: material facts.
- `included_items`: box contents.
- `compatibility`: supported devices, standards, systems, accessories, or environments.
- `requirements`: required host devices, accessories, software, power, network, or setup conditions.
- `certifications`: official certifications or compliance marks.
- `protocols`: supported technical protocols or standards.
- `ports`: ports, connectors, channels, slots, or interfaces.
- `power`: power input/output facts where relevant.
- `warranty`: warranty facts from official sources.
- `region_availability`: factual region or language availability, not inventory.

Validation:

- `key_specs` values must be strings, numbers, booleans, or arrays of those primitives.
- Unknown facts should be omitted, not guessed.
- Compatibility claims must name the supported target and condition when relevant.

## ProductClaim

Required:

- `id`: stable claim id.
- `claim`: concise factual claim.
- `evidence_ids`: one or more `Evidence.id` values.

Optional:

- `claim_type`: `spec`, `compatibility`, `use_case`, `limitation`, `certification`, `comparison`, or `support`.
- `confidence`: `low`, `medium`, or `high`; defaults to `medium`.
- `notes`: human review notes.

Validation:

- Claims must be grounded in at least one evidence item.
- Comparative claims must be factual and tied to explicit competitor context or official specs.
- Promotional phrasing must be rewritten as verifiable product facts.

## Evidence

Required:

- `id`: stable evidence id.
- `source_type`: `official_page`, `manual`, `faq`, `support_page`, `certification`, `spec_sheet`, `human_note`, or `other`.
- `title`: source title.
- `excerpt`: short supporting text or normalized fact.

Optional:

- `url`: source URL.
- `file_path`: local source path when the input came from an approved file.
- `captured_at`: ISO timestamp or date.
- `source_hash`: hash of the source document or excerpt.
- `page`, `section`, or `anchor`: precise source locator.
- `confidence`: `low`, `medium`, or `high`.

Validation:

- At least one of `url`, `file_path`, or `excerpt` must be present.
- `url`, when present, must be official, brand-approved, or clearly marked as third-party context.
- Evidence must be immutable for a generated source hash; corrected evidence should create a new evidence item or revision.

## CompetitorContext

Required:

- `id`: stable context id.
- `category`: category being compared.
- `competitor_name`: competitor brand or product line name.
- `basis`: why this competitor is relevant.

Optional:

- `competitor_product_name`
- `competitor_url`
- `comparison_points`: factual points to compare.
- `known_differences`: evidence-backed differences.
- `avoid_claims`: claims the system must not make.

Validation:

- Competitor context is for answer quality and comparison grounding only.
- Do not include pricing, inventory, ads, review counts, or marketplace ranking by default.
- Do not make legal, superiority, or performance claims without evidence.

## BuyingQuestion

Required:

- `id`: stable question id.
- `question`: natural-language buyer question.
- `intent`: `choose`, `compare`, `compatibility`, `setup`, `limitation`, `troubleshooting`, or `general`.

Optional:

- `sku_ids`: SKUs relevant to the question.
- `category`: relevant product category.
- `expected_facts`: facts that a good answer should preserve.
- `expected_limitations`: caveats that a good answer should include.
- `competitor_context_ids`: relevant `CompetitorContext.id` values.
- `priority`: `low`, `medium`, or `high`; defaults to `medium`.

Validation:

- Questions must reflect real buyer decision intent.
- Questions must not assume unsupported product capabilities.
- A monitor prompt may be generated from a buying question, but the original question remains brand-neutral where possible.

## RetrievalRun

Required:

- `id`: stable run id.
- `question_id`: references `BuyingQuestion.id`.
- `ran_at`: ISO timestamp or date.
- `provider`: AI/search provider name.
- `response_text`: captured response text.

Optional:

- `model`: model or engine name.
- `sku_ids`: SKUs evaluated.
- `brand_mentioned`: boolean.
- `sku_mentioned`: boolean.
- `canonical_url_cited`: boolean.
- `source_hash_cited`: boolean.
- `claim_coverage`: object mapping `ProductClaim.id` to `missing`, `partial`, or `covered`.
- `wrong_specs_present`: boolean.
- `limitations_preserved`: boolean.
- `competitor_context_present`: boolean.
- `buying_intent_matched`: boolean.
- `score`: number from `0` to `100`.
- `notes`: monitor notes.

Validation:

- `question_id` must exist.
- Booleans must reflect observed response content, not expected behavior.
- Wrong specs must be tied to the contradicted fact or claim when possible.

## RevisionSuggestion

Required:

- `id`: stable suggestion id.
- `source`: `retrieval_run`, `human_review`, or `validation`.
- `reason`: concise issue statement.
- `target`: `source_page`, `markdown_asset`, `llms_txt`, `schema`, `claim`, `evidence`, `buying_question`, or `competitor_context`.
- `action`: concrete recommended edit.

Optional:

- `retrieval_run_id`
- `sku_ids`
- `claim_ids`
- `evidence_ids`
- `severity`: `low`, `medium`, or `high`; defaults to `medium`.
- `status`: `open`, `accepted`, `rejected`, or `applied`; defaults to `open`.
- `created_at`: ISO timestamp or date.

Validation:

- Suggestions must be actionable and point to the affected object.
- Suggestions must not invent facts; new facts require evidence first.
- Applied suggestions should result in a new source hash or documented revision.

## Compatibility With Creator Source Passport

The SKU contract maps onto the existing Creator Source Passport concepts without replacing the rendering pipeline:

- `Brand` is the product equivalent of `Creator`.
- `SKU.product_name` and `SkuFacts.positioning` feed the source title and thesis-like summary.
- `ProductClaim` maps to existing claim handling.
- `Evidence` maps to existing evidence and references.
- `SKU.canonical_url`, source hash, markdown path, and source anchor preserve the existing citation model.
- `BuyingQuestion` maps to monitor prompts and platform/buying-decision variants.
- `RetrievalRun` extends the current monitor report from attribution checks to product-answer quality checks.
- `RevisionSuggestion` preserves the existing revision suggestion loop.

Phase 1 success means this contract can represent real SKU source input as JSON while the existing Creator Source Passport workflow remains valid.
