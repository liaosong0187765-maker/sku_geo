# GEO Creator Source Passport MVP - Project Context

## 1. Final Direction

Build Creator Source Passport first.

This is not a generic GEO SaaS, not a content scheduler, and not a full CMS.

## 2. Core Product

One high-quality idea becomes:

- Source Passport
- canonical source page
- AI index pack
- platform variants
- source anchor
- retrieval monitor
- revision suggestions

## 3. MVP Scope

Must build:

- Source Passport model
- source page generator
- AI index compiler
- platform variant generator
- manual publish workflow
- AI retrieval monitor
- revision suggestion loop

Do not build yet:

- full SaaS
- full CMS
- full social scheduler
- WeChat/Zhihu automation
- payment system
- team permission system

## 4. Codebase Reuse

Use:

- geo-ai-first-platform → Source Passport Core + AI Index Compiler
- ai-cmo → Retrieval Monitor
- MarkItDown → file/document intake
- Crawl4AI → optional URL intake
- Mixpost/Postiz → later publishing reference only

## 5. Acceptance Criteria

A successful MVP means:

- user can create one Source Passport
- system generates source page and markdown page
- system generates llms.txt, sitemap, robots, schema
- system generates X/LinkedIn/WeChat/Zhihu variants
- every variant contains visible source anchor
- user can save platform publication URL
- monitor can test whether AI cites source hash or canonical URL
- system gives revision suggestions when AI fails to cite or understand it

## 6. gstack Execution Plan

Phase 1: map codebase  
Phase 2: build Source Passport Core  
Phase 3: build AI Index Compiler  
Phase 4: build Platform Variant Studio  
Phase 5: build Retrieval Monitor  
Phase 6: run E2E QA
This repository follows strict file management rules. Do not create random files or folders.



\## 1. Read First



Before planning or coding, read these files if they exist:



\- docs/PROJECT\_CONTEXT.md

\- README.md

\- package.json

\- pyproject.toml

\- docker-compose.yml

\- .env.example



Use `docs/PROJECT\\\_CONTEXT.md` as the source of truth for product direction.



\## 2. Project Direction



The current product direction is:



Creator Source Passport MVP.



Do not turn this project into:



\- a generic GEO SaaS

\- a full CMS

\- a full social media scheduler

\- a WeChat/Zhihu automation bot

\- a broad B2B export GEO platform



The MVP should focus on:



\- Source Passport

\- canonical source page

\- AI-readable markdown assets

\- llms.txt / sitemap / robots / schema

\- platform variants

\- visible source anchor

\- AI retrieval / citation monitoring

\- revision suggestions



\## 3. Approved Directory Structure



Only use these top-level folders unless explicitly approved:



```text

docs/                 project docs, plans, context, decisions

src/                  main application source code

tests/                unit and integration tests

scripts/              one-off or maintenance scripts

configs/              config templates, not secrets

public/               public static assets

examples/             sample data and demo inputs

external/             downloaded third-party repos, reference only

generated/            generated demo output, safe to delete

data/                 local development data, do not commit secrets

logs/                 runtime logs, ignored by git




