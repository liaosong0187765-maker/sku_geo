# GEO Creator Source MVP Autoplan

Date: 2026-04-26

## Product Verdict

Build the product as an AI-readable source-of-truth system for high-signal creators, not as another AI content generator.

The core product:

> A creator publishes one high-quality idea, and the system turns it into a permanent AI-readable source page, generates platform-specific versions for distribution, attaches a traceable source anchor, then monitors whether AI systems can find, cite, and correctly route back to the source.

This is content provenance infrastructure. GEO is the outcome, not the product category.

## User Need

The first users are professional information-source creators:

- AI consultants
- outbound/GEO/SEO advisors
- B2B founders
- industry researchers
- independent developers
- investors or analysts
- expert operators with strong original judgment

Their real pain:

- High-quality thoughts die inside X, WeChat, Zhihu, LinkedIn, and private feeds.
- AI summarizes or remixes their ideas without stable attribution.
- Their old posts are hard for humans and AI to find later.
- They do not want to configure a website, schema, sitemap, llms.txt, hosting, crawler logs, or prompt monitoring.
- They need one workflow that turns a thought into a durable, citeable knowledge asset.

## MVP Modules

### 1. Creator Semantic Home

Default-hosted source site for every creator.

Starter URL shape:

```text
https://{creator}.yourapp.com
https://{creator}.yourapp.com/s/{slug}-{hash}
```

Paid/custom domain:

```text
https://creator.com/s/{slug}-{hash}
```

Do not require users to bring a website in v1. Most creators will not configure DNS, sitemap, robots, schema, and deployment themselves. The product must provide the semantic home by default, with custom domains as an upgrade.

### 2. Source Passport

The core object. One durable source item per original idea.

Required fields:

- title
- short thesis
- full source text
- author/entity
- created date
- updated date
- canonical URL
- content hash
- version number
- topics
- claims
- evidence
- references
- limitations
- related source items
- recommended citation text
- platform variants

The hash is not the main value. The stable canonical URL is the main value. The hash is a content identity and integrity hint.

### 3. AI Index Pack

Generated automatically for each creator site:

```text
/llms.txt
/llms-full.txt
/ai/index.md
/ai/profile.md
/ai/topics/{topic}.md
/ai/sources/{slug}.md
/sitemap.xml
/robots.txt
schema.org JSON-LD
```

Crawler policy should explicitly allow useful AI/search crawlers where appropriate. OpenAI documents `OAI-SearchBot` as the crawler used to surface sites in ChatGPT search answers, and Google documents Googlebot plus Google-Extended controls for search/training/grounding behavior.

Sources:
- OpenAI crawlers: https://developers.openai.com/api/docs/bots
- Google crawlers: https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers
- llms.txt proposal: https://github.com/AnswerDotAI/llms-txt

### 4. Distribution Studio

Generate platform-specific versions from the same Source Passport.

MVP platforms:

- X thread
- LinkedIn post
- WeChat article draft/copy
- Zhihu answer/article copy

Every generated version includes a source anchor:

```text
Source: https://creator.com/s/semantic-source-abc123
```

Track publication state:

- draft generated
- copied
- published manually
- published via API
- platform URL captured
- source anchor present
- needs update after source revision

For v1, automate only where platform APIs are clean. X and LinkedIn have official APIs. WeChat and Zhihu should begin as copy/export workflows because API access and policy constraints are heavier.

### 5. Citation and Retrieval Monitor

Measure whether AI can retrieve and attribute the source.

Track:

- crawler hits to source page and markdown endpoints
- ChatGPT/Search prompt results
- Gemini/Perplexity/Claude/Grok where API or compliant provider access exists
- whether creator name appears
- whether canonical source URL appears
- whether platform copies are cited instead of the source
- whether the AI answer misstates the idea
- which prompt families trigger the source

The first metric is not traffic. It is source recoverability:

> Given a relevant prompt, can AI find the creator's source page and attribute the idea correctly?

### 6. Source Revision Loop

When AI fails to cite or misreads the source, generate concrete edits:

- add a direct answer paragraph
- add FAQ
- strengthen claim-evidence links
- add definition blocks
- add better title and headings
- add related source links
- add comparison/edge-case sections
- update llms-full and topic pages

This is the retention loop. Users keep paying because the system turns AI feedback into better source assets.

## Current Local Assets

### `geo-ai-first-platform`

Use this as the seed for Source Passport generation.

Already has:

- `KnowledgeCore` model
- generator for `llms.txt`, `llms-full.txt`, `/ai/*.md`, schema, site pages, report
- scoring model for entity clarity, audience clarity, Q&A, evidence, artifact completeness
- URL importer that turns fetched pages into a draft knowledge core
- tests around generated assets

Need to change:

- replace company/product model with creator/source-item model
- generate one source page per idea
- add versioning and hash
- add platform variants
- add creator site index/topic pages
- add source-level readiness score
- add source anchor format
- add canonical + markdown alternate links

### `ai-cmo-main` / `ai-cmo`

Use this as the seed for AI retrieval and citation monitoring.

Already has:

- monitored prompt model
- prompt run history
- OpenAI web-search based analyzer
- Gemini/OpenAI monitoring channels
- brand mention and cited URL detection
- share-of-voice dashboard concepts
- scheduled prompt execution

Need to change:

- monitor Source Passport URLs, not just company domains
- detect canonical source citation vs platform-copy citation
- track creator/entity mention
- store platform publication URLs
- score attribution accuracy
- generate source revision recommendations
- build prompt libraries per creator topic

## External Open Source Projects to Reuse or Study

| Project | Use | Recommendation |
|---|---|---|
| Postiz | Multi-platform social scheduling, API, OAuth, agentic workflows | Study and possibly integrate as a separate service. Strong channel coverage, but AGPL-3.0 means avoid copying code into a proprietary codebase without legal review. |
| Mixpost | Self-hosted social media scheduling, MIT license | Better candidate for code adaptation if we need publishing infrastructure. Laravel stack may not match current Python/Vue assets. |
| Crawl4AI | Web crawling and clean Markdown extraction | Replace or supplement current Camoufox importer. Good for importing old creator sites or public articles. |
| Microsoft MarkItDown | Convert PDFs, DOCX, PPTX, XLSX, HTML, CSV, etc. to Markdown | Use for creator source intake from documents, slides, PDFs, and exports. Strong fit for knowledge-source ingestion. |
| AnswerDotAI llms-txt | llms.txt spec and parser/generator tooling | Use as the format reference. Do not invent a private llms format unless needed. |
| Payload CMS | Next.js-native CMS with auth, drafts, versions, access control | Strong if rebuilding as a full SaaS app. Probably too heavy for fastest MVP. |
| TinaCMS | Git/Markdown CMS with visual editing | Good fit if the product wants content portability and Git-backed ownership. Less ideal if we need multi-tenant SaaS fast. |
| Prompt Clarity | Open-source LLM visibility tracker | Study for monitor UX and multi-model prompt execution. Repo appears very early and license signals are inconsistent across pages, so do not depend on it blindly. |

Sources:
- Postiz: https://github.com/gitroomhq/postiz-app
- Mixpost: https://github.com/inovector/mixpost
- Crawl4AI docs: https://docs.crawl4ai.com/core/quickstart/
- MarkItDown: https://github.com/microsoft/markitdown
- llms.txt: https://github.com/AnswerDotAI/llms-txt
- Payload: https://github.com/payloadcms/payload
- TinaCMS: https://github.com/tinacms/tinacms
- Prompt Clarity: https://github.com/promptclarity/promptclarity

## Recommended MVP Architecture

```text
Raw idea / notes / doc
  -> Source Passport model
  -> Semantic source page
  -> AI Index Pack
  -> Platform variants
  -> Manual/API publishing
  -> Prompt + crawler monitoring
  -> Revision recommendations
  -> Source version update
```

### Minimal Data Model

```text
Creator
  id
  name
  bio
  domain
  topics
  social_profiles

SourceItem
  id
  creator_id
  slug
  hash
  title
  thesis
  body
  status
  canonical_url
  current_version_id
  created_at
  updated_at

SourceVersion
  id
  source_item_id
  version
  content_hash
  markdown
  json_ld
  llms_excerpt
  change_note

Claim
  id
  source_item_id
  claim
  evidence
  reference_url
  confidence

PlatformVariant
  id
  source_item_id
  platform
  content
  anchor_url
  status

Publication
  id
  platform_variant_id
  platform_url
  published_at
  method
  anchor_present

MonitorPrompt
  id
  source_item_id
  prompt
  platform
  interval

MonitorRun
  id
  prompt_id
  raw_response
  creator_mentioned
  source_url_cited
  platform_url_cited
  attribution_score
  misunderstanding_notes
```

## Build Sequence

### Phase 1: Concierge MVP

Do this before building heavy SaaS.

- Pick 5 high-signal creators.
- Manually create 10 Source Passports each.
- Host under your default domain.
- Generate X, LinkedIn, WeChat, and Zhihu versions.
- Publish or ask users to publish with the source anchor.
- Run 10 to 20 prompts per creator weekly.
- Produce a source recoverability report.

Pass condition:

- 3 creators publish at least 5 source-anchored posts.
- At least 1 creator says the source site is useful enough to keep using.
- At least 1 AI/search surface cites or returns the source page for a relevant query, or crawler logs show discovery.

### Phase 2: Productized Internal Tool

- Extend `geo-ai-first-platform` into Source Passport generator.
- Add a simple web UI for creator/source management.
- Add default-hosted semantic home.
- Add AI Index Pack generation.
- Add platform variant generator.
- Add publication URL tracking.
- Reuse `ai-cmo` monitor logic for prompt checks.

### Phase 3: Platform Integrations

- Add X API publishing.
- Add LinkedIn API publishing.
- Add WeChat export/draft workflow if official account credentials are available.
- Keep Zhihu manual copy/export unless API access is clear and compliant.
- Consider Postiz/Mixpost integration only after the source system works.

## What Not To Build Yet

- Full social media scheduler
- Full CMS clone
- Marketplace of creators
- Automated scraping of closed platforms
- Guaranteed AI citation promises
- WeChat/Zhihu automation that depends on brittle or non-compliant scraping
- A private "hash protocol" before users care about the source URL

## CEO Review

Score: 8/10 if narrowed to Source Passport for expert creators. 5/10 if it becomes a generic AI content scheduler.

The wedge is strong because it sits upstream of social distribution and downstream of original thinking. Most tools optimize posting. This optimizes source authority.

User challenge:

Do not lead with "reach more AI." Lead with "make every serious idea ownable, citeable, and recoverable."

## Design Review

The UI must make users feel one thing:

> I made a durable source asset, not another disposable post.

Primary screen should be the Source Passport editor:

- left: source idea and evidence
- center: source page preview
- right: platform variants and AI readiness

Avoid dashboard-first design. Dashboards are useful after repeated publishing. First-run value is publishing one source asset.

## Engineering Review

Recommended stack path:

- Keep current Python generator for first artifact generation.
- Add a thin web app around it rather than rewriting everything.
- Reuse `ai-cmo` monitoring concepts.
- Do not embed Postiz unless publishing becomes the bottleneck.
- Use Crawl4AI and MarkItDown as optional ingestion adapters.

Main technical risks:

- AI citation is noisy and cannot be guaranteed.
- Social platform APIs have access and policy constraints.
- Closed platforms may not preserve links or make content crawlable.
- Hashes are meaningless unless the canonical source page is stable and crawlable.

## DX Review

If this becomes a developer-installable tool later, the DX needs:

- one-command local demo
- sample creator
- sample source item
- generated source site
- generated platform variants
- sample monitor prompts
- fake monitor run fixtures

Target TTHW: under 10 minutes from clone to seeing a source page and X/LinkedIn variants.

## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|---|---|---|---|---|---|
| 1 | CEO | Build Source Passport, not generic content generator | User challenge | Completeness | Source authority is the durable value | AI bulk publishing tool |
| 2 | CEO | Provide hosted semantic home by default | Auto | Bias toward action | Requiring users to build sites kills adoption | Bring-your-own-site only |
| 3 | Eng | Extend `geo-ai-first-platform` first | Auto | DRY | It already generates AI-readable assets | Start from blank CMS |
| 4 | Eng | Reuse `ai-cmo` for monitoring concepts | Auto | DRY | It already has prompt/run/citation logic | Build monitor from scratch |
| 5 | Eng | Study Postiz/Mixpost but do not lead with scheduling | Taste | Explicit over clever | Publishing is distribution, not core moat | Fork social scheduler first |
| 6 | Design | Make Source Passport editor the main UX | Auto | Explicit | First-run value is one source asset | Dashboard-first product |
| 7 | Scope | Keep WeChat/Zhihu manual/export in v1 | Auto | Pragmatic | Automation can be brittle or policy-heavy | Full closed-platform automation |

## Final Recommendation

Build a small, opinionated MVP around one action:

> Create one Source Passport and publish anchored variants.

Everything else is support machinery.

The fastest path is not to find one open-source project to fork. It is to compose:

- local `geo-ai-first-platform` for source/AI asset generation
- local `ai-cmo` for AI visibility monitoring
- MarkItDown/Crawl4AI for intake
- Postiz/Mixpost later for publishing
- custom Source Passport model as the new core

