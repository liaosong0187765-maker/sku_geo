# AI-First GEO Content Platform MVP

This MVP turns a company's structured business knowledge into two outputs from the same source of truth:

1. Human-readable website pages.
2. AI/search-readable artifacts for GEO, answer engines, and crawler-friendly publishing.

It is intentionally local-first and dependency-free. No API keys. No scraping yet.

## Run

```bash
python3 geo_builder.py examples/sample_company.json --out dist
```

## Run from live URLs with Camoufox

```bash
python3 geo_builder.py --url "https://example.com" --out dist
python3 geo_builder.py --url "https://example.com" --url "https://example.com/faq" --url "https://example.com/pricing" --out dist
```

This mode uses the local Camoufox fetch script to pull one or more pages, saves each raw fetch under `dist/source/`, and turns the pages into a merged draft knowledge core before generating the normal GEO artifacts.

## Test

```bash
python3 -m unittest discover -s tests
```

## GitHub publish with `.env`

1. Put your token and repo in `.env`:

```bash
GITHUB_TOKEN=your_github_pat_here
GITHUB_REPO=liaosong0187765-maker/geo-ai-first-platform
```

2. Publish:

```bash
bash scripts/publish_github.sh
```

`.env` is gitignored. Use `.env.example` as the template.

## Generated outputs

- `dist/knowledge-core.json` — normalized source of truth
- `dist/llms.txt` — short AI crawler guide
- `dist/llms-full.txt` — complete AI-readable knowledge document
- `dist/ai/company.md` — AI-readable company profile
- `dist/ai/products.md` — AI-readable product profile
- `dist/ai/faq.md` — answer-ready Q&A blocks
- `dist/schema.json` — JSON-LD graph with Organization, Product, FAQPage
- `dist/site/index.html` — human homepage
- `dist/site/product.html` — human product page
- `dist/site/faq.html` — human FAQ page
- `dist/report.md` — GEO readiness score and claim-evidence map
- `dist/source/page-01-*.md` — raw Camoufox page capture when using `--url`
- `dist/source/page-01-*.json` — fetch metadata per imported page when using `--url`
- `dist/source/manifest.json` — list of all imported pages for a multi-URL run

## Input model

The knowledge core has these sections:

- `entity`: who the company is
- `audience`: who it serves and who it does not serve
- `products`: what it sells
- `claims`: what the company wants AI and humans to believe
- `questions`: answer-ready questions and responses
- `sources`: evidence sources
- `competitors`: comparison angles

## Product principle

The knowledge core is the root. Pages are just views.

That means the same facts generate:

- AI-readable Markdown
- human-readable HTML
- structured search data
- diagnostic scoring

This avoids the common GEO mistake: writing a nice marketing page first, then trying to patch AI-readable files onto it later.

## extensions

1. URL importer using Firecrawl or browser fetch.
2. LLM extractor that converts raw website pages into this JSON schema.
3. Human review UI for editing claims, evidence, and questions.
4. Cloudflare Worker publisher for `/llms.txt` and `/ai/*`.
5. AI search simulator for ChatGPT, Perplexity, Google AI Overview, Bing, Kimi, Doubao.
