# SKU Source Field Dictionary

Reusable field dictionary for building a brand-neutral SKU Source Passport input package.

This asset explains what each field is for, how delivery teams should collect it, and what must be excluded. It is not tied to any example brand or SKU.

## Excluded Data

Do not collect or store these values in the core SKU Source Passport package:

- Price
- Inventory or stock status
- Discount, coupon, bundle, campaign, or promotion
- Rating, review count, review excerpt, sales volume, or marketplace rank
- Automated publishing credentials or platform account data

If a customer sends excluded data, keep it out of the source passport and note the omission in the handoff.

## Brand Fields

| Field | Required | Purpose | Delivery Rule |
|---|---:|---|---|
| `brand.id` | Yes | Stable slug for joins and output paths. | Lowercase letters, numbers, and hyphens only. |
| `brand.name` | Yes | Public brand name. | Use the customer's official public spelling. |
| `brand.domain` | Yes | Canonical brand host. | Prefer HTTPS domain or official source host. |
| `brand.market` | No | Primary market or locale. | Use broad locale such as `US`, `EU`, or `global`. |
| `brand.official_urls` | No | Brand-owned home, support, FAQ, warranty, or documentation URLs. | Only include official or customer-approved URLs. |
| `brand.description` | No | Short factual brand description. | Avoid positioning claims unless provided by official evidence. |

## SKU Fields

| Field | Required | Purpose | Delivery Rule |
|---|---:|---|---|
| `skus[].id` | Yes | Stable SKU slug. | Unique within the brand. |
| `skus[].brand_id` | Yes | Link to `brand.id`. | Must match the brand object. |
| `skus[].product_name` | Yes | Public product name. | Use official naming. |
| `skus[].category` | Yes | Product category. | Use buyer-recognizable category language. |
| `skus[].canonical_url` | Yes | Primary citation target. | Must be official or customer-approved. |
| `skus[].model_number` | No | Manufacturer model or SKU code. | Include only when official evidence supports it. |
| `skus[].slug` | No | Preferred output slug. | Defaults from product name or SKU id. |
| `skus[].status` | No | Workflow state. | Use `draft`, `reviewed`, or `published`. |
| `skus[].source_urls` | No | Official product, support, manual, FAQ, certification, or documentation URLs. | Exclude marketplace pages unless explicitly customer-approved as evidence context. |
| `skus[].updated_at` | No | Last human-approved fact date. | ISO date. |

## Fact Fields

| Field | Purpose | Delivery Rule |
|---|---|---|
| `facts.summary` | One or two factual sentences describing the SKU. | No promotional phrasing. |
| `facts.positioning` | Factual buying context. | Describe intended role, not superiority. |
| `facts.key_specs` | Normalized specification map. | Values must be strings, numbers, booleans, or arrays of primitives. |
| `facts.dimensions` | Size or weight facts. | Preserve units. |
| `facts.materials` | Material facts. | Include only if official. |
| `facts.included_items` | Box contents. | Do not infer accessories. |
| `facts.compatibility` | Supported devices, systems, standards, environments, or accessories. | Include conditions where relevant. |
| `facts.requirements` | Required host device, accessory, software, power, network, or setup condition. | State constraints plainly. |
| `facts.certifications` | Official certifications or compliance marks. | Require evidence. |
| `facts.protocols` | Technical protocols or standards. | Preserve official names. |
| `facts.ports` | Ports, connectors, channels, slots, or interfaces. | Use normalized labels. |
| `facts.power` | Input/output facts where relevant. | Preserve units and allocation rules. |
| `facts.warranty` | Warranty facts from official sources. | Do not interpret legal coverage. |
| `facts.region_availability` | Region or language availability. | Must not become inventory status. |

## Claim Fields

| Field | Required | Purpose | Delivery Rule |
|---|---:|---|---|
| `claims[].id` | Yes | Stable claim id. | Use readable slugs such as `claim-port-count`. |
| `claims[].claim` | Yes | Concise factual claim. | One claim per sentence. |
| `claims[].evidence_ids` | Yes | Evidence backing the claim. | At least one evidence id. |
| `claims[].claim_type` | No | Claim category. | Use `spec`, `compatibility`, `use_case`, `limitation`, `certification`, `comparison`, or `support`. |
| `claims[].confidence` | No | Review confidence. | Use `low`, `medium`, or `high`. |
| `claims[].notes` | No | Human review notes. | Keep internal and factual. |

## Evidence Fields

| Field | Required | Purpose | Delivery Rule |
|---|---:|---|---|
| `evidence[].id` | Yes | Stable evidence id. | Use readable slugs such as `ev-official-manual`. |
| `evidence[].source_type` | Yes | Source class. | Use official page, manual, FAQ, support page, certification, spec sheet, human note, or other. |
| `evidence[].title` | Yes | Source title. | Use document or page title when available. |
| `evidence[].excerpt` | Yes | Short supporting text or normalized fact. | Keep short and precise. |
| `evidence[].url` | No | Source URL. | Prefer official or customer-approved HTTPS URL. |
| `evidence[].file_path` | No | Approved local source path. | Do not point to secrets, uploads, or private customer files in reusable templates. |
| `evidence[].captured_at` | No | Capture date or timestamp. | ISO date or timestamp. |
| `evidence[].source_hash` | No | Source hash. | Recompute after evidence correction. |
| `evidence[].page` | No | Precise locator. | Useful for PDFs or manuals. |
| `evidence[].section` | No | Precise section. | Use visible section heading. |
| `evidence[].anchor` | No | URL or generated anchor. | Use for canonical citation blocks. |
| `evidence[].confidence` | No | Evidence confidence. | Use `low`, `medium`, or `high`. |

## Buying Question Fields

| Field | Required | Purpose | Delivery Rule |
|---|---:|---|---|
| `buying_questions[].id` | Yes | Stable question id. | Use intent-based slug. |
| `buying_questions[].question` | Yes | Natural buyer question. | Must reflect realistic buying, setup, compatibility, or limitation intent. |
| `buying_questions[].intent` | Yes | Question class. | Use `choose`, `compare`, `compatibility`, `setup`, `limitation`, `troubleshooting`, or `general`. |
| `buying_questions[].sku_ids` | No | Relevant SKUs. | Include known SKU ids. |
| `buying_questions[].expected_facts` | No | Facts a good answer should preserve. | Reference claims or exact normalized facts. |
| `buying_questions[].expected_limitations` | No | Caveats a good answer should include. | Keep concrete. |
| `buying_questions[].priority` | No | Monitor priority. | Use `low`, `medium`, or `high`. |

## Delivery Review Rule

A SKU source package is not ready for source-pack generation until:

- Every required brand and SKU field is present.
- Every claim references evidence.
- Unknown facts are omitted instead of guessed.
- Limitation and compatibility boundaries are explicit.
- Excluded data is absent.
- The canonical URL is official or customer-approved.
