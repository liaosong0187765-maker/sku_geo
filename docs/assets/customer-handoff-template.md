# Customer Handoff Template

Customer: `[Customer Name]`  
Brand: `[Brand Name]`  
Delivery period: `[YYYY-MM-DD to YYYY-MM-DD]`  
Delivery owner: `[Name]`  
Customer reviewer: `[Name or role]`

## Delivery Summary

This delivery creates a reusable SKU Source Passport package for the selected
products. The package is designed to help AI systems and buyers find, cite,
compare, and understand approved product facts.

This delivery does not include price, inventory, ratings, reviews, promotions, or
rankings.

## Selected SKUs

| SKU id | Product name | Category | Canonical source URL | Status |
| --- | --- | --- | --- | --- |
| `[sku-1-id]` | `[SKU 1 Product Name]` | `[Category]` | `[URL]` | Draft |
| `[sku-2-id]` | `[SKU 2 Product Name]` | `[Category]` | `[URL]` | Draft |
| `[sku-3-id]` | `[SKU 3 Product Name]` | `[Category]` | `[URL]` | Draft |

Use 3-5 rows for the final customer handoff.

## Delivered Assets

- SKU source input JSON.
- Canonical source pages.
- AI-readable markdown assets.
- `llms.txt`.
- Sitemap, robots, and schema assets where applicable.
- Buying question bank with 20-50 questions.
- Weekly retrieval monitor report.
- Revision suggestions.
- Human review checklist.

## Evidence Summary

| SKU id | Evidence sources reviewed | Open evidence gaps |
| --- | --- | --- |
| `[sku-1-id]` | `[Official product page, support page, manual, FAQ]` | `[None or gap]` |
| `[sku-2-id]` | `[Official product page, support page, manual, FAQ]` | `[None or gap]` |
| `[sku-3-id]` | `[Official product page, support page, manual, FAQ]` | `[None or gap]` |

## Buying Question Coverage

Total questions: `[20-50]`

| Intent | Count | Notes |
| --- | ---: | --- |
| Choose | `[count]` | `[coverage notes]` |
| Compare | `[count]` | `[coverage notes]` |
| Compatibility | `[count]` | `[coverage notes]` |
| Limitation | `[count]` | `[coverage notes]` |
| Setup | `[count]` | `[coverage notes]` |
| General or troubleshooting | `[count]` | `[coverage notes]` |

## Weekly Monitor Report

Report id: `[weekly-report-YYYY-WW]`  
Period: `[YYYY-MM-DD to YYYY-MM-DD]`  
Questions run: `[count]`  
Providers checked: `[provider list]`

| Metric | Result | Notes |
| --- | ---: | --- |
| Canonical citation rate | `[percent]` | `[notes]` |
| Source hash citation rate | `[percent]` | `[notes]` |
| Wrong spec count | `[count]` | `[notes]` |
| Missing limitation count | `[count]` | `[notes]` |
| Priority revision count | `[count]` | `[notes]` |

## Revision Suggestions

| Priority | Target | Recommendation | Owner | Status |
| --- | --- | --- | --- | --- |
| High | `[source page or asset]` | `[specific edit]` | `[owner]` | Open |
| Medium | `[source page or asset]` | `[specific edit]` | `[owner]` | Open |

## Customer Review Needed

- [ ] Confirm selected SKUs remain the correct 3-5 priority products.
- [ ] Approve product identity, specs, compatibility, limitations, and not-for scenarios.
- [ ] Approve or reject each revision suggestion.
- [ ] Confirm no prohibited commerce fields have been added.

## Out Of Scope

The following are intentionally excluded:

- price
- inventory
- ratings
- reviews
- promotions
- rankings
- automated marketplace or social publishing
- paid media management
- full CMS workflow
- team permission workflow
