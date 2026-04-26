# AI-First GEO Content Platform MVP Plan

## Product thesis

Build a local-first MVP that turns raw company content into an AI-readable knowledge core, then generates both human-readable web pages and AI/search-engine-readable artifacts.

The product is not an SEO keyword tool. It is an AI comprehension layer for a business.

## Narrow MVP

Input:
- A company name, website URL, category, target customers, raw notes, product info, evidence, sources, FAQ, competitors.

Process:
- Extract and normalize a structured knowledge core.
- Build a claim-evidence map.
- Generate answer-ready Q&A blocks.
- Generate human-facing pages.
- Generate AI/search artifacts.
- Score the output for crawlability, clarity, evidence, and AI answer readiness.

Output:
- `dist/knowledge-core.json`
- `dist/llms.txt`
- `dist/llms-full.txt`
- `dist/ai/company.md`
- `dist/ai/products.md`
- `dist/ai/faq.md`
- `dist/schema.json`
- `dist/site/index.html`
- `dist/site/faq.html`
- `dist/site/product.html`
- `dist/report.md`

## Why this MVP

No API keys. No cloud. No scraping yet. It proves the hardest product idea first: structured AI-readable business content as the source of truth.

## Implementation constraints

Use a dependency-light app so it works immediately on Jetson:
- Python 3 standard library only.
- CLI command: `python3 geo_builder.py examples/sample_company.yaml --out dist`
- Accept JSON or a simple YAML subset. Since PyYAML may not exist, support JSON first and a tiny YAML-like parser only if easy.
- Include sample input.
- Include tests using `unittest`.
- Include README with commands.

## Data model

Knowledge core fields:
- entity: name, url, category, one_line, description
- audience: target_customers, pain_points, use_cases, not_for
- products: name, description, features, benefits, pricing, limitations
- claims: claim, evidence, source, confidence, related_questions
- questions: question, answer, evidence_refs, limitations, cta
- sources: title, url, type, date
- competitors: name, url, comparison_angle

## Core modules

1. `geo_builder.py`
   - CLI entry point.
   - Load input JSON.
   - Normalize data.
   - Generate files.
   - Print output paths and score.

2. `geo_core/model.py`
   - Dataclasses or typed dictionaries for core structures.
   - Validation helpers.

3. `geo_core/generator.py`
   - Generate llms.txt, llms-full.txt, markdown, schema JSON-LD, human pages, report.

4. `geo_core/scoring.py`
   - Compute AI readiness score.
   - Dimensions: entity clarity, audience clarity, Q&A coverage, evidence coverage, artifact completeness.

5. `examples/sample_company.json`
   - Sample B2B export/AI sales company.

6. `tests/test_generation.py`
   - Verify files are generated.
   - Verify schema has Organization/Product/FAQPage style content where applicable.
   - Verify report contains score and missing items.

## Done criteria

- Running `python3 geo_builder.py examples/sample_company.json --out dist` creates all expected files.
- Running `python3 -m unittest discover -s tests` passes.
- README explains what it does and how to extend to scraping/plugins later.

## Deferred

- Website crawling.
- LLM extraction.
- Cloudflare Worker publishing.
- WordPress plugin.
- Multi-engine AI search monitoring.
- User login/database.

## Next after MVP

Add an importer:
- URL crawler using Firecrawl or browser fetch.
- Prompt-based extraction into the same knowledge-core schema.
- Human review UI.
- Cloudflare Worker deploy target for `/llms.txt` and `/ai/*`.
