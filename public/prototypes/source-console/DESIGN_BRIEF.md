# Source Console UI Redesign Brief

## CEO-Level Product Prompt

Design the Creator Source Passport MVP as if the product has one job:

> Help a creator turn one serious idea into a canonical source that AI and humans can cite correctly.

Do not design a SaaS dashboard. Do not design a CMS. Do not design a social scheduler.

The first screen should feel like a precision instrument. It should ask the creator for one thing: the idea they want AI to cite correctly.

## Product Shape

The interface should collapse the MVP into five visible steps:

1. Register the source: title, thesis, body, claims, evidence, limitations.
2. Preview the canonical source page: URL, version, source hash, citation block.
3. Generate anchored platform variants: X, LinkedIn, WeChat, Zhihu.
4. Backfill publication URLs after manual posting, while reserving API slots for future one-click publishing.
5. Check AI citation and apply concrete revision tasks.

The system may generate `llms.txt`, schema, sitemap, robots, markdown, and hash metadata, but those should be status signals, not primary UI modules.

## Interaction Rules

- The user should be able to generate a source page in one obvious action.
- Every platform variant must show a visible source anchor.
- Publishing controls should show future API hooks without implying current automatic WeChat or Zhihu posting.
- URL backfill must be visible and fast.
- Citation check must inspect canonical URL, source hash, creator name, and core claim.
- Revision suggestions must be concrete. Each suggestion should support one-click apply to the draft.

## Visual Direction

- Extremely simple, calm, and technical.
- White and graphite base, one restrained signal color, no decorative blobs.
- Dense enough for experts, but not intimidating.
- Think "source authority console", not "AI writing app".
- Use restrained borders, precise spacing, monospace only for machine identifiers.
- Avoid generic dashboard metrics, oversized marketing sections, emoji, and busy charts.

## Success Criteria

- A creator understands the workflow in under 10 seconds.
- The first useful action is visible without scrolling.
- Canonical URL and source hash are always easy to find.
- Platform publishing and URL backfill are obvious.
- AI citation failures turn into three specific edit actions.
- The UI leaves room for future one-click publishing APIs without changing the current MVP scope.
