# SKU Source Passport Delivery SOP

Use this SOP to deliver reusable SKU Source Passport assets for a new customer.
The output should be copyable to the next customer without changing the process.

## Scope

Deliver:

- 3-5 selected SKUs.
- Evidence-backed product facts.
- Canonical source pages and AI-readable markdown assets.
- 20-50 buying questions.
- Weekly retrieval monitor report.
- Human-reviewed revision suggestions.

Do not deliver:

- price
- inventory
- ratings
- reviews
- promotions
- rankings
- generic GEO SaaS
- full CMS
- social scheduler
- marketplace or social publishing bot

## Step 1: Intake

Inputs:

- Customer brand name, domain, and approved source hosts.
- Candidate SKU list.
- Official product pages, support pages, manuals, FAQs, and certifications.
- Customer-approved human notes for facts not visible in official pages.

Output:

- Draft `sku-source-template.json` copy.
- Candidate SKU list for scoring.

Verification:

- No prohibited fields are copied into the delivery workspace.
- Every source URL is official or customer-approved.

## Step 2: Select 3-5 SKUs

Use `sku-selection-scorecard.json`.

Selection criteria:

- Official evidence depth.
- Buying decision value.
- Fact stability.
- Comparison clarity.
- Limitation clarity.
- Weekly maintenance fit.

Output:

- 3-5 selected SKUs.
- Deferred and rejected SKU notes.
- Human approval for the selected set.

Verification:

- Each selected SKU has enough evidence for a source page.
- Each selected SKU can support buyer questions without prohibited commerce fields.

## Step 3: Normalize SKU Facts

For each selected SKU, complete:

- product identity
- category
- canonical URL
- model number when applicable
- key specs
- compatibility
- requirements
- certifications
- included items
- limitations
- use cases
- not-for scenarios
- claims
- evidence

Output:

- Completed SKU source input JSON.

Verification:

- Every claim references evidence.
- Unknown facts are omitted.
- Comparative claims are grounded in approved context.

## Step 4: Build Buying Question Bank

Use `buying-question-bank-template.json`.

Question count:

- Minimum: 20.
- Target: 20-50.
- Maximum: 50 unless the customer approves a larger monitoring scope.

Required coverage:

- choose
- compare
- compatibility
- limitation
- setup
- general or troubleshooting

Output:

- Approved buying question bank.

Verification:

- Questions map to selected SKUs or category pages.
- Questions do not depend on price, inventory, ratings, reviews, promotions, or rankings.
- Expected facts and expected limitations are listed for high-priority questions.

## Step 5: Generate Source Pack

Generate or prepare:

- canonical SKU source page
- markdown mirror
- AI product index
- category or comparison markdown where applicable
- `llms.txt`
- sitemap
- robots
- schema
- source hash or revision id

Output:

- One source pack per selected SKU.
- Completed `source-pack-manifest-template.json` copy that lists generated
  artifacts, source hash or revision id, review status, and open revision
  suggestions.

Verification:

- Canonical source page and markdown mirror agree.
- Citation block is visible.
- Schema contains factual product data only.
- Source hash or revision id is documented.
- Manifest lists canonical page, markdown mirror, `llms.txt`, sitemap, robots,
  schema, source hash or revision id, and revision suggestions.

## Step 6: Human Review

Use `human-review-checklist.md`.

Reviewers:

- delivery owner
- customer product subject-matter reviewer
- legal or compliance reviewer when claims require it

Output:

- Approved source pack or documented revision queue.

Verification:

- No prohibited commerce fields appear.
- Claims, evidence, limitations, and buying questions are approved.

## Step 7: Weekly Retrieval Monitor

Use `retrieval-runs-template.json`.

Cadence:

- Run once per week.
- Run 20-50 approved buying questions.
- Check each selected SKU across approved providers or engines.

Score:

- brand mention
- SKU mention
- canonical URL citation
- source hash citation
- claim coverage
- wrong specs
- limitation preservation
- competitor context
- buying-intent match

Output:

- Weekly monitor report.
- Revision suggestions.
- Customer review actions.

Verification:

- Every run maps to a known question id.
- Observations reflect captured AI responses, not expected behavior.
- Suggestions are actionable and do not invent new facts.

## Step 8: Customer Handoff

Use `customer-handoff-template.md`.

Include:

- selected SKUs
- delivered assets
- evidence summary
- buying question coverage
- weekly monitor report
- revision suggestions
- open customer approvals
- out-of-scope reminder

Output:

- Customer-ready handoff document.

Verification:

- The customer can understand what was delivered, what needs approval, and what
  repeats next week.
- The handoff can be copied for the next enterprise without rewriting the process.
