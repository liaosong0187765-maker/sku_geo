from __future__ import annotations

import json
import html
from pathlib import Path
import textwrap
from typing import Any, Iterable

from .models import slugify
from .sku_models import ProductClaim, SkuSourcePassport
from .sku_questions import (
    generate_comparison_sections,
    generate_faq,
    render_comparison_markdown,
    render_faq_markdown,
)

SKU_REQUIRED_ARTIFACTS = (
    "sku-passport.json",
    "index.html",
    "ai/product-index.md",
    "ai/faq.md",
    "ai/buying-guide.md",
    "faq.json",
    "comparisons.json",
    "llms.txt",
    "llms-full.txt",
    "schema.json",
    "sitemap.xml",
    "robots.txt",
)


def write_product_pack(passport: SkuSourcePassport, out_dir: Path) -> list[Path]:
    """Write deterministic SKU AI pack assets without touching Creator rendering."""
    out_dir.mkdir(parents=True, exist_ok=True)
    category_slug = slugify(passport.sku.category)
    files = {
        "sku-passport.json": render_product_json(passport),
        "index.html": render_product_home_html(passport),
        f"sku/{passport.slug}-{passport.content_hash}/index.html": render_product_html(passport),
        f"sku/{passport.slug}-{passport.content_hash}.md": render_product_markdown(passport),
        f"ai/products/{passport.slug}.md": render_product_markdown(passport),
        f"ai/categories/{category_slug}.md": render_category_markdown(passport),
        f"ai/comparisons/{category_slug}.md": render_comparison_markdown(passport),
        "ai/faq.md": render_faq_markdown(passport),
        "ai/buying-guide.md": render_buying_guide_markdown(passport),
        "ai/product-index.md": render_product_index(passport),
        "faq.json": render_faq_json(passport),
        "comparisons.json": render_comparison_json(passport),
        "llms.txt": render_product_llms(passport),
        "llms-full.txt": render_product_llms_full(passport),
        "schema.json": json.dumps(render_schema(passport), ensure_ascii=False, indent=2, sort_keys=True),
        "sitemap.xml": render_sitemap(passport),
        "robots.txt": render_robots(passport),
    }

    paths: list[Path] = []
    for rel_path, content in files.items():
        path = out_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def write_catalog_pack(passports: Iterable[SkuSourcePassport], out_dir: Path) -> list[Path]:
    """Write a multi-SKU catalog pack while preserving single-SKU source pages."""
    passport_list = sorted(list(passports), key=lambda item: item.sku.id)
    if not passport_list:
        raise ValueError("At least one SKU passport is required.")
    out_dir.mkdir(parents=True, exist_ok=True)

    files: dict[str, str] = {
        "sku-passport.json": render_catalog_json(passport_list),
        "index.html": render_catalog_home_html(passport_list),
        "ai/product-index.md": render_catalog_product_index(passport_list),
        "ai/faq.md": render_catalog_faq_markdown(passport_list),
        "ai/buying-guide.md": render_catalog_buying_guide_markdown(passport_list),
        "faq.json": render_catalog_faq_json(passport_list),
        "comparisons.json": render_catalog_comparison_json(passport_list),
        "llms.txt": render_catalog_llms(passport_list),
        "llms-full.txt": render_catalog_llms_full(passport_list),
        "schema.json": json.dumps(render_catalog_schema(passport_list), ensure_ascii=False, indent=2, sort_keys=True),
        "sitemap.xml": render_catalog_sitemap(passport_list),
        "robots.txt": render_robots(passport_list[0]),
    }
    for passport in passport_list:
        category_slug = slugify(passport.sku.category)
        files[f"sku/{passport.slug}-{passport.content_hash}/index.html"] = render_product_html(passport)
        files[f"sku/{passport.slug}-{passport.content_hash}.md"] = render_product_markdown(passport)
        files[f"ai/products/{passport.slug}.md"] = render_product_markdown(passport)
        files[f"ai/categories/{category_slug}.md"] = render_catalog_category_markdown(
            [item for item in passport_list if slugify(item.sku.category) == category_slug],
            passport.sku.category,
        )
        files[f"ai/comparisons/{category_slug}.md"] = render_catalog_comparison_markdown(
            [item for item in passport_list if slugify(item.sku.category) == category_slug],
            passport.sku.category,
        )

    paths: list[Path] = []
    for rel_path, content in files.items():
        path = out_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def render_product_json(passport: SkuSourcePassport) -> str:
    return json.dumps(passport.to_dict(), ensure_ascii=False, indent=2, sort_keys=True)


def render_catalog_json(passports: list[SkuSourcePassport]) -> str:
    payload = {
        "brand": passports[0].brand.to_dict(),
        "skus": [
            item.to_dict()["sku"]
            for item in passports
        ],
        "sku_sources": [item.to_dict()["sku_source"] for item in passports],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def render_product_markdown(passport: SkuSourcePassport) -> str:
    rows = [
        f"# {passport.sku.product_name}",
        "",
        f"**Brand:** {passport.brand.name}",
        f"**Category:** {passport.sku.category}",
        f"**Version:** {passport.version}",
        f"**Created:** {passport.created_at}",
        f"**Updated:** {passport.updated_at}",
        f"**Canonical URL:** {passport.canonical_url}",
        f"**Product URL:** {passport.sku.canonical_url}",
        f"**Content hash:** {passport.content_hash}",
        "",
        "## Product Summary",
        "",
        passport.facts.summary,
    ]
    if passport.facts.positioning:
        rows.extend(["", "## Positioning", "", passport.facts.positioning])

    rows.extend(["", "## Key Specs", ""])
    rows.extend(_mapping_lines(passport.facts.key_specs))

    fact_sections = [
        ("Materials", passport.facts.materials),
        ("Dimensions", _mapping_lines(passport.facts.dimensions) if passport.facts.dimensions else []),
        ("Included Items", passport.facts.included_items),
        ("Compatibility", passport.facts.compatibility),
        ("Requirements", passport.facts.requirements),
        ("Certifications", passport.facts.certifications),
        ("Protocols", passport.facts.protocols),
        ("Ports", passport.facts.ports),
        ("Power", passport.facts.power),
        ("Warranty", passport.facts.warranty),
        ("Region Availability", passport.facts.region_availability),
    ]
    for title, items in fact_sections:
        rows.extend(_section(title, items))

    rows.extend(["", "## Evidence-Backed Claims", ""])
    rows.extend(_claim_lines(passport.claims))

    rows.extend(["", "## Evidence Sources", ""])
    rows.extend(_evidence_lines(passport))

    rows.extend(_source_url_section(passport))

    if passport.competitor_context:
        rows.extend(["", "## Competitor Context", ""])
        for item in passport.competitor_context:
            label = item.competitor_product_name or item.competitor_name
            rows.append(f"- {label}: {item.basis}")
            for avoid_claim in item.avoid_claims:
                rows.append(f"  - Avoid claim: {avoid_claim}")

    if passport.buying_questions:
        rows.extend(["", "## Buying Questions", ""])
        for question in passport.buying_questions:
            rows.append(f"- [{question.intent}] {question.question}")

    rows.extend(["", "## Recommended Citation", "", passport.recommended_citation])
    rows.extend(["", passport.source_anchor])
    return "\n".join(rows).strip()


def render_product_index(passport: SkuSourcePassport) -> str:
    topics = passport.topics or [passport.sku.category]
    rows = [
        f"# Product AI Index: {passport.brand.name}",
        "",
        "## Current SKU Source Passports",
        "",
        f"- [{passport.sku.product_name}]({passport.canonical_url})",
        f"  - Markdown: {passport.markdown_path}",
        f"  - Product URL: {passport.sku.canonical_url}",
        f"  - Hash: {passport.content_hash}",
        f"  - Version: {passport.version}",
        "",
        "## Topics",
        "",
    ]
    rows.extend(f"- {topic}" for topic in topics)
    rows.extend(["", "## Citation Preference", "", passport.recommended_citation])
    return "\n".join(rows).strip()


def render_catalog_product_index(passports: list[SkuSourcePassport]) -> str:
    brand = passports[0].brand
    topics = _unique(
        topic
        for passport in passports
        for topic in (passport.topics or [passport.sku.category])
    )
    rows = [
        f"# Product AI Index: {brand.name}",
        "",
        "## Current SKU Source Passports",
        "",
    ]
    for passport in passports:
        rows.extend(
            [
                f"- [{passport.sku.product_name}]({passport.canonical_url})",
                f"  - Markdown: {passport.markdown_path}",
                f"  - Product URL: {passport.sku.canonical_url}",
                f"  - Hash: {passport.content_hash}",
                f"  - Version: {passport.version}",
            ]
        )
    rows.extend(["", "## Topics", ""])
    rows.extend(f"- {topic}" for topic in topics)
    rows.extend(["", "## Citation Preference", ""])
    rows.extend(f"- {passport.recommended_citation}" for passport in passports)
    return "\n".join(rows).strip()


def render_product_llms(passport: SkuSourcePassport) -> str:
    category_slug = slugify(passport.sku.category)
    rows = [
        f"# {passport.brand.name} Product Source Pack",
        "",
        passport.brand.description or f"Official product facts for {passport.brand.name}.",
        "",
        "## Canonical Product Source",
        f"- {passport.sku.product_name}: {passport.canonical_url}",
        f"- Markdown: {passport.markdown_path}",
        f"- Product URL: {passport.sku.canonical_url}",
        f"- Content hash: {passport.content_hash}",
        "",
        "## AI-Readable Files",
        "- /ai/product-index.md",
        f"- /ai/products/{passport.slug}.md",
        f"- /ai/categories/{category_slug}.md",
        f"- /ai/comparisons/{category_slug}.md",
        "- /ai/faq.md",
        "- /ai/buying-guide.md",
        "- /llms-full.txt",
        "- /schema.json",
        "",
        "## Buyer Retrieval Questions",
    ]
    if passport.buying_questions:
        rows.extend(f"- {question.question}" for question in passport.buying_questions)
    else:
        rows.append(f"- What should buyers know about {passport.sku.product_name}?")
    return "\n".join(rows).strip()


def render_catalog_llms(passports: list[SkuSourcePassport]) -> str:
    brand = passports[0].brand
    category_paths = _unique(
        f"/ai/categories/{slugify(passport.sku.category)}.md"
        for passport in passports
    )
    comparison_paths = _unique(
        f"/ai/comparisons/{slugify(passport.sku.category)}.md"
        for passport in passports
    )
    rows = [
        f"# {brand.name} Product Source Pack",
        "",
        brand.description or f"Official product facts for {brand.name}.",
        "",
        "## Canonical Product Sources",
    ]
    for passport in passports:
        rows.extend(
            [
                f"- {passport.sku.product_name}: {passport.canonical_url}",
                f"  - Markdown: {passport.markdown_path}",
                f"  - Product URL: {passport.sku.canonical_url}",
                f"  - Content hash: {passport.content_hash}",
            ]
        )
    rows.extend(["", "## AI-Readable Files", "- /ai/product-index.md"])
    rows.extend(f"- /ai/products/{passport.slug}.md" for passport in passports)
    rows.extend(f"- {path}" for path in category_paths)
    rows.extend(f"- {path}" for path in comparison_paths)
    rows.extend(["- /ai/faq.md", "- /ai/buying-guide.md", "- /llms-full.txt", "- /schema.json"])
    rows.extend(["", "## Buyer Retrieval Questions"])
    questions = _unique(
        question.question
        for passport in passports
        for question in passport.buying_questions
    )
    rows.extend(f"- {question}" for question in questions) if questions else rows.append("- What should buyers know about these SKUs?")
    return "\n".join(rows).strip()


def render_product_llms_full(passport: SkuSourcePassport) -> str:
    category_slug = slugify(passport.sku.category)
    asset_list = "\n".join(
        [
            "## Product Pack Paths",
            "",
            f"- /ai/products/{passport.slug}.md",
            f"- /ai/categories/{category_slug}.md",
            f"- /ai/comparisons/{category_slug}.md",
            "- /ai/faq.md",
            "- /ai/buying-guide.md",
            "- /faq.json",
            "- /comparisons.json",
            "- /schema.json",
        ]
    )
    return "\n\n---\n\n".join(
        [
            asset_list,
            render_product_index(passport),
            render_product_markdown(passport),
            render_faq_markdown(passport),
            render_comparison_markdown(passport),
            render_buying_guide_markdown(passport),
        ]
    ).strip()


def render_catalog_llms_full(passports: list[SkuSourcePassport]) -> str:
    asset_list = "\n".join(
        [
            "## Product Pack Paths",
            "",
            *[f"- /ai/products/{passport.slug}.md" for passport in passports],
            *[
                f"- /ai/categories/{slugify(category)}.md"
                for category in _unique(passport.sku.category for passport in passports)
            ],
            *[
                f"- /ai/comparisons/{slugify(category)}.md"
                for category in _unique(passport.sku.category for passport in passports)
            ],
            "- /ai/faq.md",
            "- /ai/buying-guide.md",
            "- /faq.json",
            "- /comparisons.json",
            "- /schema.json",
        ]
    )
    return "\n\n---\n\n".join(
        [
            asset_list,
            render_catalog_product_index(passports),
            *[render_product_markdown(passport) for passport in passports],
            render_catalog_faq_markdown(passports),
            render_catalog_comparison_markdown(passports, "All categories"),
            render_catalog_buying_guide_markdown(passports),
        ]
    ).strip()


def render_buying_guide_markdown(passport: SkuSourcePassport) -> str:
    rows = [
        f"# Buying Guide: {passport.sku.product_name}",
        "",
        "## Product Positioning",
        "",
        passport.facts.positioning or passport.facts.summary,
        "",
        "## Best For",
        "",
    ]
    rows.extend(_list_or_empty(passport.sku.use_cases))
    rows.extend(["", "## Not For", ""])
    rows.extend(_list_or_empty(passport.sku.not_for))
    rows.extend(["", "## Limitations", ""])
    rows.extend(_list_or_empty(passport.sku.limitations))
    rows.extend(["", "## Citation", "", passport.recommended_citation])
    return "\n".join(rows).strip()


def render_catalog_buying_guide_markdown(passports: list[SkuSourcePassport]) -> str:
    rows = [f"# Buying Guide: {passports[0].brand.name}", ""]
    for passport in passports:
        rows.extend(
            [
                f"## {passport.sku.product_name}",
                "",
                passport.facts.positioning or passport.facts.summary,
                "",
                "### Best For",
                "",
                *_list_or_empty(passport.sku.use_cases),
                "",
                "### Not For",
                "",
                *_list_or_empty(passport.sku.not_for),
                "",
                "### Limitations",
                "",
                *_list_or_empty(passport.sku.limitations),
                "",
                f"Citation: {passport.recommended_citation}",
                "",
            ]
        )
    return "\n".join(rows).strip()


def render_category_markdown(passport: SkuSourcePassport) -> str:
    rows = [
        f"# Category: {passport.sku.category}",
        "",
        "## Product Source Passports",
        "",
        f"- [{passport.sku.product_name}]({passport.canonical_url})",
        f"  - Model: {passport.sku.model_number or 'Not listed'}",
        f"  - Markdown: /ai/products/{passport.slug}.md",
        f"  - Hash: {passport.content_hash}",
        "",
        "## Topics",
        "",
    ]
    rows.extend(f"- {topic}" for topic in passport.topics or [passport.sku.category])
    return "\n".join(rows).strip()


def render_catalog_category_markdown(passports: list[SkuSourcePassport], category: str) -> str:
    rows = [
        f"# Category: {category}",
        "",
        "## Product Source Passports",
        "",
    ]
    for passport in passports:
        rows.extend(
            [
                f"- [{passport.sku.product_name}]({passport.canonical_url})",
                f"  - Model: {passport.sku.model_number or 'Not listed'}",
                f"  - Markdown: /ai/products/{passport.slug}.md",
                f"  - Hash: {passport.content_hash}",
            ]
        )
    rows.extend(["", "## Topics", ""])
    rows.extend(
        f"- {topic}"
        for topic in _unique(topic for passport in passports for topic in (passport.topics or [passport.sku.category]))
    )
    return "\n".join(rows).strip()


def render_catalog_faq_markdown(passports: list[SkuSourcePassport]) -> str:
    return "\n\n".join(render_faq_markdown(passport) for passport in passports).strip()


def render_catalog_comparison_markdown(passports: list[SkuSourcePassport], category: str) -> str:
    rows = [f"# Comparisons: {category}", ""]
    for passport in passports:
        rows.extend([f"## {passport.sku.product_name}", "", render_comparison_markdown(passport), ""])
    return "\n".join(rows).strip()


def render_faq_json(passport: SkuSourcePassport) -> str:
    payload = {
        "product": passport.sku.product_name,
        "canonical_url": passport.canonical_url,
        "items": [item.to_dict() for item in generate_faq(passport)],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def render_catalog_faq_json(passports: list[SkuSourcePassport]) -> str:
    payload = {
        "brand": passports[0].brand.name,
        "items": [
            {
                "product": passport.sku.product_name,
                "canonical_url": passport.canonical_url,
                "items": [item.to_dict() for item in generate_faq(passport)],
            }
            for passport in passports
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def render_comparison_json(passport: SkuSourcePassport) -> str:
    payload = {
        "product": passport.sku.product_name,
        "category": passport.sku.category,
        "canonical_url": passport.canonical_url,
        "items": [item.to_dict() for item in generate_comparison_sections(passport)],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def render_catalog_comparison_json(passports: list[SkuSourcePassport]) -> str:
    payload = {
        "brand": passports[0].brand.name,
        "items": [
            {
                "product": passport.sku.product_name,
                "category": passport.sku.category,
                "canonical_url": passport.canonical_url,
                "items": [item.to_dict() for item in generate_comparison_sections(passport)],
            }
            for passport in passports
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def render_schema(passport: SkuSourcePassport) -> dict[str, object]:
    graph: list[dict[str, object]] = [
        {
            "@type": "Brand",
            "@id": f"{passport.brand.domain.rstrip('/')}/#brand" if passport.brand.domain else "#brand",
            "name": passport.brand.name,
            "description": passport.brand.description,
            "url": passport.brand.domain,
            "sameAs": passport.brand.official_urls,
        },
        {
            "@type": "Product",
            "@id": f"{passport.canonical_url}#product",
            "name": passport.sku.product_name,
            "brand": {"@id": f"{passport.brand.domain.rstrip('/')}/#brand" if passport.brand.domain else "#brand"},
            "category": passport.sku.category,
            "model": passport.sku.model_number,
            "description": passport.facts.summary,
            "url": passport.canonical_url,
            "identifier": passport.content_hash,
            "isBasedOn": _schema_sources(passport),
            "additionalProperty": _schema_properties(passport),
        },
        {
            "@type": "WebPage",
            "@id": f"{passport.canonical_url}#source-passport",
            "url": passport.canonical_url,
            "name": f"{passport.sku.product_name} SKU Source Passport",
            "datePublished": passport.created_at,
            "dateModified": passport.updated_at,
            "version": str(passport.version),
            "mainEntity": {"@id": f"{passport.canonical_url}#product"},
            "citation": passport.recommended_citation,
        },
    ]
    faq_entities = [
        {"@type": "Question", "name": item.question, "acceptedAnswer": {"@type": "Answer", "text": item.answer}}
        for item in generate_faq(passport)
    ]
    if faq_entities:
        graph.append(
            {
                "@type": "FAQPage",
                "@id": f"{passport.canonical_url}#faq",
                "mainEntity": faq_entities,
            }
        )
    return {"@context": "https://schema.org", "@graph": graph}


def render_catalog_schema(passports: list[SkuSourcePassport]) -> dict[str, object]:
    graph: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for passport in passports:
        for item in render_schema(passport)["@graph"]:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("@id") or "")
            if item_id and item_id in seen_ids:
                continue
            if item_id:
                seen_ids.add(item_id)
            graph.append(item)
    return {"@context": "https://schema.org", "@graph": graph}


def render_sitemap(passport: SkuSourcePassport) -> str:
    root = _site_root(passport)
    category_slug = slugify(passport.sku.category)
    urls = [
        root,
        passport.canonical_url,
        f"{root}{passport.markdown_path}",
        f"{root}/ai/product-index.md",
        f"{root}/ai/products/{passport.slug}.md",
        f"{root}/ai/categories/{category_slug}.md",
        f"{root}/ai/comparisons/{category_slug}.md",
        f"{root}/ai/faq.md",
        f"{root}/llms.txt",
        f"{root}/llms-full.txt",
        f"{root}/schema.json",
    ]
    items = "\n".join(
        f"  <url><loc>{html.escape(url)}</loc><lastmod>{passport.updated_at}</lastmod></url>"
        for url in urls
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>"""


def render_catalog_sitemap(passports: list[SkuSourcePassport]) -> str:
    root = _site_root(passports[0])
    urls = [
        root,
        f"{root}/ai/product-index.md",
        f"{root}/ai/faq.md",
        f"{root}/ai/buying-guide.md",
        f"{root}/llms.txt",
        f"{root}/llms-full.txt",
        f"{root}/schema.json",
    ]
    for passport in passports:
        category_slug = slugify(passport.sku.category)
        urls.extend(
            [
                passport.canonical_url,
                f"{root}{passport.markdown_path}",
                f"{root}/ai/products/{passport.slug}.md",
                f"{root}/ai/categories/{category_slug}.md",
                f"{root}/ai/comparisons/{category_slug}.md",
            ]
        )
    lastmod = max(passport.updated_at for passport in passports)
    items = "\n".join(
        f"  <url><loc>{html.escape(url)}</loc><lastmod>{lastmod}</lastmod></url>"
        for url in _unique(urls)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>"""


def render_robots(passport: SkuSourcePassport) -> str:
    root = _site_root(passport)
    return textwrap.dedent(
        f"""
        User-agent: *
        Allow: /

        User-agent: OAI-SearchBot
        Allow: /

        User-agent: ChatGPT-User
        Allow: /

        User-agent: Googlebot
        Allow: /

        User-agent: Google-Extended
        Allow: /

        Sitemap: {root}/sitemap.xml
        """
    ).strip()


def render_product_home_html(passport: SkuSourcePassport) -> str:
    return _page(
        passport,
        f"{passport.brand.name} Product Source Pack",
        f"""
        <section class="band intro">
          <p class="eyebrow">SKU Source Passport</p>
          <h1>{html.escape(passport.brand.name)}</h1>
          <p>{html.escape(passport.brand.description or 'Official product source pack.')}</p>
        </section>
        <section class="band">
          <h2>Canonical Product Source</h2>
          <p><a class="source-link" href="{html.escape(passport.canonical_path)}">{html.escape(passport.sku.product_name)}</a></p>
          <p>{html.escape(passport.facts.summary)}</p>
        </section>
        <section class="band two-column">
          <div>
            <h2>AI Assets</h2>
            <ul>
              <li><a href="/llms.txt">llms.txt</a></li>
              <li><a href="/llms-full.txt">llms-full.txt</a></li>
              <li><a href="/ai/product-index.md">Product index</a></li>
              <li><a href="/ai/products/{html.escape(passport.slug)}.md">Product markdown</a></li>
              <li><a href="/ai/faq.md">FAQ</a></li>
              <li><a href="/schema.json">Schema JSON-LD</a></li>
            </ul>
          </div>
          <div>
            <h2>Machine Data</h2>
            <ul>
              <li><a href="/faq.json">FAQ JSON</a></li>
              <li><a href="/comparisons.json">Comparison JSON</a></li>
              <li><a href="/sitemap.xml">Sitemap</a></li>
              <li><a href="/robots.txt">Robots</a></li>
            </ul>
          </div>
        </section>
        """,
    )


def render_catalog_home_html(passports: list[SkuSourcePassport]) -> str:
    first = passports[0]
    product_links = "".join(
        f"""
        <li>
          <a class="source-link" href="{html.escape(passport.canonical_path)}">{html.escape(passport.sku.product_name)}</a>
          <p>{html.escape(passport.facts.summary)}</p>
          <p><code>{html.escape(passport.content_hash)}</code></p>
        </li>
        """
        for passport in passports
    )
    return _page(
        first,
        f"{first.brand.name} Product Source Pack",
        f"""
        <section class="band intro">
          <p class="eyebrow">SKU Source Passport Catalog</p>
          <h1>{html.escape(first.brand.name)}</h1>
          <p>{html.escape(first.brand.description or 'Official product source pack.')}</p>
        </section>
        <section class="band">
          <h2>Canonical Product Sources</h2>
          <ul>{product_links}</ul>
        </section>
        <section class="band two-column">
          <div>
            <h2>AI Assets</h2>
            <ul>
              <li><a href="/llms.txt">llms.txt</a></li>
              <li><a href="/llms-full.txt">llms-full.txt</a></li>
              <li><a href="/ai/product-index.md">Product index</a></li>
              <li><a href="/ai/faq.md">FAQ</a></li>
              <li><a href="/schema.json">Schema JSON-LD</a></li>
            </ul>
          </div>
          <div>
            <h2>Machine Data</h2>
            <ul>
              <li><a href="/faq.json">FAQ JSON</a></li>
              <li><a href="/comparisons.json">Comparison JSON</a></li>
              <li><a href="/sitemap.xml">Sitemap</a></li>
              <li><a href="/robots.txt">Robots</a></li>
            </ul>
          </div>
        </section>
        """,
    )


def render_product_html(passport: SkuSourcePassport) -> str:
    claims = "".join(
        f"<li><strong>{html.escape(claim.claim)}</strong><br><span>Evidence IDs: {html.escape(', '.join(claim.evidence_ids))}</span></li>"
        for claim in passport.claims
    )
    specs = "".join(f"<li>{html.escape(line[2:])}</li>" for line in _mapping_lines(passport.facts.key_specs))
    questions = "".join(f"<li>{html.escape(item.question)}</li>" for item in passport.buying_questions)
    return _page(
        passport,
        passport.sku.product_name,
        f"""
        <article class="source">
          <header class="band intro">
            <p class="eyebrow">Canonical SKU Source</p>
            <h1>{html.escape(passport.sku.product_name)}</h1>
            <p class="thesis">{html.escape(passport.facts.summary)}</p>
            <dl class="meta">
              <div><dt>Brand</dt><dd>{html.escape(passport.brand.name)}</dd></div>
              <div><dt>Model</dt><dd>{html.escape(passport.sku.model_number or 'Not listed')}</dd></div>
              <div><dt>Hash</dt><dd><code>{html.escape(passport.content_hash)}</code></dd></div>
              <div><dt>Updated</dt><dd>{html.escape(passport.updated_at)}</dd></div>
            </dl>
            <p class="anchor">{html.escape(passport.source_anchor)}</p>
          </header>
          <section class="band"><h2>Official Facts</h2><ul>{specs}</ul></section>
          <section class="band"><h2>Claim Evidence Map</h2><ul class="evidence-list">{claims or '<li>No evidence-backed claims listed.</li>'}</ul></section>
          <section class="band"><h2>Buying Questions</h2><ul>{questions or '<li>No buying questions listed.</li>'}</ul></section>
          <section class="band citation">
            <h2>Recommended Citation</h2>
            <p>{html.escape(passport.recommended_citation)}</p>
            <p><a href="{html.escape(passport.markdown_path)}">Markdown mirror</a></p>
          </section>
        </article>
        """,
    )


def _section(title: str, items: Iterable[str]) -> list[str]:
    lines = [str(item) for item in items if str(item).strip()]
    if not lines:
        return []
    return ["", f"## {title}", "", *[f"- {item}" for item in lines]]


def _mapping_lines(mapping: dict[str, Any]) -> list[str]:
    if not mapping:
        return ["- No explicit facts listed."]
    rows: list[str] = []
    for key in sorted(mapping):
        value = mapping[key]
        if isinstance(value, list):
            rendered = ", ".join(str(item) for item in value)
        else:
            rendered = str(value)
        rows.append(f"- {key}: {rendered}")
    return rows


def _claim_lines(claims: list[ProductClaim]) -> list[str]:
    if not claims:
        return ["- No evidence-backed claims listed."]
    rows: list[str] = []
    for claim in sorted(claims, key=lambda item: item.id):
        rows.append(f"- Claim: {claim.claim}")
        rows.append(f"  Evidence IDs: {', '.join(claim.evidence_ids)}")
        rows.append(f"  Confidence: {claim.confidence}")
        if claim.claim_type:
            rows.append(f"  Type: {claim.claim_type}")
        if claim.notes:
            rows.append(f"  Notes: {claim.notes}")
    return rows


def _evidence_lines(passport: SkuSourcePassport) -> list[str]:
    if not passport.evidence:
        return ["- No evidence sources listed."]
    rows: list[str] = []
    for item in sorted(passport.evidence, key=lambda evidence: evidence.id):
        locator = _evidence_locator(item.to_dict())
        rows.append(f"- {item.id}: {item.title}")
        rows.append(f"  Source type: {item.source_type}")
        rows.append(f"  Excerpt: {item.excerpt}")
        rows.append(f"  Source hash: {item.source_hash}")
        if locator:
            rows.append(f"  Locator: {locator}")
    return rows


def _evidence_locator(item: dict[str, Any]) -> str:
    parts = [
        item.get("url") or item.get("file_path") or "",
        item.get("page") or "",
        item.get("section") or "",
        item.get("anchor") or "",
    ]
    return " | ".join(part for part in parts if part)


def _source_url_section(passport: SkuSourcePassport) -> list[str]:
    urls = [passport.sku.canonical_url, *passport.sku.source_urls, *passport.brand.official_urls]
    unique_urls = []
    for url in urls:
        if url and url not in unique_urls:
            unique_urls.append(url)
    if not unique_urls:
        return []
    return ["", "## Official Source URLs", "", *[f"- {url}" for url in unique_urls]]


def _list_or_empty(items: Iterable[str]) -> list[str]:
    rows = [item for item in items if item]
    return [f"- {item}" for item in rows] if rows else ["- No explicit facts listed."]


def _schema_sources(passport: SkuSourcePassport) -> list[str]:
    urls = [passport.sku.canonical_url, *passport.sku.source_urls, *passport.brand.official_urls]
    urls.extend(item.url for item in passport.evidence if item.url)
    return _unique(urls)


def _schema_properties(passport: SkuSourcePassport) -> list[dict[str, object]]:
    properties: list[dict[str, object]] = []
    for key in sorted(passport.facts.key_specs):
        value = passport.facts.key_specs[key]
        properties.append({"@type": "PropertyValue", "name": key, "value": value})
    for claim in sorted(passport.claims, key=lambda item: item.id):
        properties.append(
            {
                "@type": "PropertyValue",
                "name": f"Claim: {claim.id}",
                "value": claim.claim,
                "propertyID": ", ".join(claim.evidence_ids),
            }
        )
    return properties


def _site_root(passport: SkuSourcePassport) -> str:
    return passport.canonical_url.rsplit("/sku/", 1)[0].rstrip("/")


def _page(passport: SkuSourcePassport, title: str, body: str) -> str:
    schema = json.dumps(render_schema(passport), ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} - SKU Source Passport</title>
  <meta name="description" content="{html.escape(passport.facts.summary)}">
  <link rel="canonical" href="{html.escape(passport.canonical_url)}">
  <link rel="alternate" type="text/markdown" href="{html.escape(passport.markdown_path)}">
  <link rel="alternate" type="text/plain" href="/llms.txt">
  <script type="application/ld+json">{schema}</script>
  <style>
    :root {{ color-scheme: light; --ink: #182230; --muted: #516071; --line: #d7dde6; --paper: #f6f8fb; --panel: #ffffff; --accent: #0f766e; --accent-soft: #dff7f2; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--paper); color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.6; }}
    nav {{ display: flex; gap: 18px; align-items: center; padding: 14px 24px; border-bottom: 1px solid var(--line); background: var(--panel); position: sticky; top: 0; }}
    nav a {{ color: var(--ink); text-decoration: none; font-weight: 650; }}
    main {{ width: min(100%, 1060px); margin: 0 auto; padding: 28px 20px 56px; }}
    .band {{ border: 1px solid var(--line); background: var(--panel); border-radius: 8px; padding: 24px; margin: 18px 0; }}
    .intro {{ background: linear-gradient(180deg, var(--accent-soft), #ffffff); border-color: #a8ddd4; }}
    .eyebrow {{ color: var(--accent); font-size: 0.82rem; font-weight: 750; letter-spacing: 0; text-transform: uppercase; margin: 0 0 10px; }}
    h1 {{ font-size: clamp(2rem, 5vw, 3.2rem); line-height: 1.08; margin: 0 0 16px; letter-spacing: 0; }}
    h2 {{ font-size: 1.2rem; margin: 0 0 12px; letter-spacing: 0; }}
    a {{ color: #0b5cab; }}
    code {{ background: #edf1f7; border: 1px solid var(--line); border-radius: 6px; padding: 2px 5px; }}
    .source-link {{ font-size: 1.15rem; font-weight: 750; }}
    .thesis {{ font-size: 1.15rem; color: #243447; max-width: 860px; }}
    .anchor {{ border: 1px solid #9ed7cf; background: #eefbf8; border-radius: 8px; padding: 12px; overflow-wrap: anywhere; font-weight: 700; white-space: pre-wrap; }}
    .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin: 22px 0; }}
    .meta div {{ border-top: 1px solid rgba(15, 118, 110, 0.24); padding-top: 8px; }}
    dt {{ color: var(--muted); font-size: 0.82rem; }}
    dd {{ margin: 0; font-weight: 700; overflow-wrap: anywhere; }}
    .two-column {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 22px; }}
    .evidence-list li {{ margin-bottom: 14px; }}
    @media (max-width: 640px) {{ nav {{ align-items: flex-start; flex-direction: column; gap: 8px; }} .band {{ padding: 18px; }} }}
  </style>
</head>
<body>
  <nav>
    <a href="/">Product Source Home</a>
    <a href="{html.escape(passport.canonical_path)}">Canonical Source</a>
    <a href="/ai/product-index.md">AI Index</a>
    <a href="/llms.txt">llms.txt</a>
  </nav>
  <main>{body}</main>
</body>
</html>"""


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


__all__ = [
    "SKU_REQUIRED_ARTIFACTS",
    "render_catalog_buying_guide_markdown",
    "render_catalog_category_markdown",
    "render_catalog_comparison_json",
    "render_catalog_faq_json",
    "render_catalog_llms",
    "render_catalog_llms_full",
    "render_catalog_product_index",
    "render_catalog_schema",
    "render_catalog_sitemap",
    "render_buying_guide_markdown",
    "render_category_markdown",
    "render_comparison_json",
    "render_faq_json",
    "render_product_index",
    "render_product_json",
    "render_product_llms",
    "render_product_llms_full",
    "render_product_markdown",
    "render_robots",
    "render_schema",
    "render_sitemap",
    "write_catalog_pack",
    "write_product_pack",
]
