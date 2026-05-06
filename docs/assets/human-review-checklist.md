# Human Review Checklist

Use this checklist before publishing a SKU source pack and after each weekly
monitor report.

## Delivery Scope

- [ ] The delivery covers 3-5 selected SKUs.
- [ ] Each selected SKU has a canonical product source URL.
- [ ] Each selected SKU has official or customer-approved evidence.
- [ ] The buying question bank contains 20-50 questions.
- [ ] The weekly monitor report template is ready for repeated use.

## Prohibited Fields

Confirm that no source input, generated source page, markdown asset, monitor
report, or handoff document includes:

- [ ] price
- [ ] inventory
- [ ] ratings
- [ ] reviews
- [ ] promotions
- [ ] rankings

If any prohibited value appears in upstream material, remove it from the delivery
assets and note that it is out of scope.

## Evidence And Claims

- [ ] Every claim references at least one evidence id.
- [ ] Evidence comes from official or customer-approved sources.
- [ ] Evidence has a stable title, URL or file path, excerpt, and capture date.
- [ ] Unknown facts are omitted rather than guessed.
- [ ] Comparative claims are factual and tied to approved competitor context.
- [ ] Marketing language has been rewritten as verifiable product facts.

## SKU Facts

- [ ] Product identity, model number, category, and canonical URL are correct.
- [ ] Key specs match official evidence.
- [ ] Compatibility notes include required conditions.
- [ ] Limitations and not-for scenarios are explicit.
- [ ] Use cases are grounded in evidence.
- [ ] Required accessories, software, host devices, or setup conditions are listed.

## AI-Readable Assets

- [ ] Canonical source page has a citation block.
- [ ] Markdown mirror preserves the same facts and limitations.
- [ ] `llms.txt` points to approved AI-readable assets.
- [ ] Schema uses factual product data only.
- [ ] Source hash or revision identifier changes when approved facts change.

## Buying Questions

- [ ] The question bank covers choose, compare, compatibility, limitation, setup,
  and general buyer intents.
- [ ] Questions do not depend on prohibited commerce fields.
- [ ] Each high-priority question maps to at least one SKU or category page.
- [ ] Expected facts and expected limitations are specified for monitor checks.

## Weekly Monitor Review

- [ ] Each run maps to a known question id.
- [ ] Observed AI responses are captured without editing their meaning.
- [ ] Brand mention, SKU mention, citation, fact coverage, wrong facts, and
  limitations are scored consistently.
- [ ] Revision suggestions are actionable and point to the affected asset.
- [ ] New facts requested by a suggestion are not added without evidence.

## Approval

- [ ] Customer subject-matter reviewer approved the facts.
- [ ] Delivery owner approved the source-pack structure.
- [ ] Legal or compliance reviewer approved any sensitive limitations or claims.
- [ ] Open issues are listed in the customer handoff.
