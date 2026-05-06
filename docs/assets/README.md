# Delivery Assets

Reusable delivery assets for SKU Source Passport service projects.

These files are brand-neutral templates. Copy them into a customer delivery
workspace, replace placeholder values, and keep the same evidence and review
rules for each new company or SKU set.

## Asset Index

| Asset | Purpose |
| --- | --- |
| `sku-source-template.json` | Neutral source input template for one brand and 3-5 selected SKUs. |
| `sku-source-field-dictionary.md` | Field-by-field collection guidance for delivery teams. |
| `sku-selection-scorecard.json` | Reusable scoring model for choosing the first 3-5 SKUs. |
| `claim-evidence-map-template.json` | Claim-to-evidence matrix for publishable product facts. |
| `buying-question-bank-template.json` | Starter bank for 20-50 buying questions and monitor prompts. |
| `source-page-section-template.md` | Canonical SKU source page section structure. |
| `source-pack-manifest-template.json` | Delivery manifest for generated source pack artifacts and review state. |
| `retrieval-runs-template.json` | Weekly retrieval monitor report and run capture template. |
| `revision-suggestion-template.json` | Maintenance backlog template for source-pack revisions. |
| `human-review-checklist.md` | Manual review checklist before publication and after weekly monitoring. |
| `customer-handoff-template.md` | Customer-facing handoff document for deliverables, approvals, and next steps. |
| `delivery-asset-index.json` | Machine-readable index of required delivery assets. |
| `delivery-sop.md` | End-to-end service workflow for repeatable delivery. |

## Non-Negotiable Exclusions

Do not collect, infer, store, generate, or publish:

- price
- inventory
- ratings
- reviews
- promotions
- rankings

If a customer source includes those values, leave them out of these assets. The
service is a product-fact and AI-citation workflow, not a commerce operations,
advertising, or marketplace performance system.

## Standard Delivery Shape

Each customer delivery should start with:

- 3-5 priority SKUs.
- Official product, support, manual, FAQ, or certification evidence.
- 20-50 real buying questions.
- One human-reviewed source pack per SKU.
- One weekly monitor report covering citation, fact accuracy, limitations, and
  revision suggestions.

## Copying For A New Customer

1. Duplicate the JSON templates into the customer workspace.
2. Replace placeholder IDs, URLs, product names, categories, claims, evidence,
   and buying questions.
3. Keep the prohibited-field lists intact.
4. Run human review before publishing any source pack.
5. Use the weekly retrieval report template for ongoing monitoring.

The templates should remain reusable. Do not add customer-specific logic,
brand-specific examples, or implementation details to `docs/assets/`.
