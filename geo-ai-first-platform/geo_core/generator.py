from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Iterable, List

from .model import KnowledgeCore, Product, Question
from .scoring import score


def write_all(core: KnowledgeCore, out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ai").mkdir(exist_ok=True)
    (out_dir / "site").mkdir(exist_ok=True)

    paths = []
    files = {
        "knowledge-core.json": json.dumps(core.to_json_ready(), ensure_ascii=False, indent=2),
        "llms.txt": render_llms(core),
        "llms-full.txt": render_llms_full(core),
        "ai/company.md": render_company_md(core),
        "ai/products.md": render_products_md(core),
        "ai/faq.md": render_faq_md(core),
        "schema.json": json.dumps(render_schema(core), ensure_ascii=False, indent=2),
        "site/index.html": render_home_html(core),
        "site/product.html": render_product_html(core),
        "site/faq.html": render_faq_html(core),
        "report.md": render_report(core),
    }
    for rel, content in files.items():
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def render_llms(core: KnowledgeCore) -> str:
    lines = [
        f"# {core.name}",
        "",
        core.entity.get("one_line", ""),
        "",
        "## Entity",
        f"- Category: {core.entity.get('category', '')}",
        f"- Website: {core.url}",
        "",
        "## Core AI-readable files",
        "- /ai/company.md",
        "- /ai/products.md",
        "- /ai/faq.md",
        "- /llms-full.txt",
        "",
        "## Best answer targets",
    ]
    for q in core.questions[:8]:
        lines.append(f"- {q.question}")
    return "\n".join(lines)


def render_llms_full(core: KnowledgeCore) -> str:
    sections = [render_company_md(core), render_products_md(core), render_faq_md(core), render_claims_md(core)]
    return "\n\n---\n\n".join(sections)


def render_company_md(core: KnowledgeCore) -> str:
    audience = core.audience
    lines = [
        f"# {core.name} company profile",
        "",
        f"## What is {core.name}?",
        core.entity.get("description") or core.entity.get("one_line", ""),
        "",
        "## Category",
        str(core.entity.get("category", "")),
        "",
        "## Target customers",
        *_bullets(audience.get("target_customers", [])),
        "",
        "## Pain points solved",
        *_bullets(audience.get("pain_points", [])),
        "",
        "## Use cases",
        *_bullets(audience.get("use_cases", [])),
        "",
        "## Not a fit for",
        *_bullets(audience.get("not_for", [])),
    ]
    return "\n".join(lines)


def render_products_md(core: KnowledgeCore) -> str:
    lines = [f"# {core.name} products", ""]
    for product in core.products:
        lines.extend(_product_markdown(product))
    return "\n".join(lines)


def render_faq_md(core: KnowledgeCore) -> str:
    lines = [f"# {core.name} answer-ready FAQ", ""]
    for q in core.questions:
        lines.extend(_question_markdown(q))
    return "\n".join(lines)


def render_claims_md(core: KnowledgeCore) -> str:
    lines = ["# Claim-Evidence Map", ""]
    for claim, source in core.claim_evidence_map():
        lines.extend([
            f"## {claim.claim}",
            f"- Evidence: {claim.evidence or 'Missing evidence'}",
            f"- Source: {source}",
            f"- Confidence: {claim.confidence}",
            "",
        ])
    return "\n".join(lines)


def render_schema(core: KnowledgeCore) -> dict:
    faq_entities = [
        {
            "@type": "Question",
            "name": q.question,
            "acceptedAnswer": {"@type": "Answer", "text": q.answer},
        }
        for q in core.questions
    ]
    products = [
        {
            "@type": "Product",
            "name": p.name,
            "description": p.description,
            "brand": {"@type": "Organization", "name": core.name},
        }
        for p in core.products
    ]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "name": core.name,
                "url": core.url,
                "description": core.entity.get("description") or core.entity.get("one_line", ""),
            },
            *products,
            {"@type": "FAQPage", "mainEntity": faq_entities},
        ],
    }


def render_report(core: KnowledgeCore) -> str:
    total, dimensions, missing = score(core)
    lines = [
        f"# GEO AI Readiness Report: {core.name}",
        "",
        f"**Overall score:** {total}/100",
        "",
        "## Score breakdown",
        "",
        "| Dimension | Score | Passed |",
        "|---|---:|---:|",
    ]
    for name, data in dimensions.items():
        lines.append(f"| {name} | {data['score']}/100 | {data['passed']}/{data['total']} |")
    lines.extend(["", "## Missing or weak items", ""])
    lines.extend(_bullets(missing) if missing else ["No major gaps detected."])
    lines.extend(["", "## Claim-Evidence Map", ""])
    for claim, source in core.claim_evidence_map():
        lines.extend([
            f"### {claim.claim}",
            f"- Evidence: {claim.evidence or 'Missing'}",
            f"- Source: {source}",
            f"- Confidence: {claim.confidence}",
            "",
        ])
    lines.extend([
        "## Recommended next pages",
        "",
        "- Comparison page: explain when to choose this company over alternatives.",
        "- Case study page: show a real customer before/after story.",
        "- Pricing explanation page: clarify fit, constraints, and buying triggers.",
        "- AI-search landing page: answer the top category queries directly.",
    ])
    return "\n".join(lines)


def render_home_html(core: KnowledgeCore) -> str:
    product_links = "".join(f"<li>{html.escape(p.name)}: {html.escape(p.description)}</li>" for p in core.products)
    use_cases = "".join(f"<li>{html.escape(str(x))}</li>" for x in core.audience.get("use_cases", []))
    return _page(core, "Home", f"""
<section class="hero">
  <p class="eyebrow">{html.escape(str(core.entity.get('category', '')))}</p>
  <h1>{html.escape(str(core.entity.get('one_line', core.name)))}</h1>
  <p>{html.escape(str(core.entity.get('description', '')))}</p>
</section>
<section>
  <h2>Products</h2>
  <ul>{product_links}</ul>
</section>
<section>
  <h2>Use cases</h2>
  <ul>{use_cases}</ul>
</section>
<section aria-label="AI readable summary">
  <h2>AI-readable summary</h2>
  <p>{html.escape(str(core.entity.get('one_line', '')))}</p>
  <p>Target customers: {html.escape(', '.join(map(str, core.audience.get('target_customers', []))))}</p>
</section>
""")


def render_product_html(core: KnowledgeCore) -> str:
    body = ""
    for p in core.products:
        body += f"<section><h1>{html.escape(p.name)}</h1><p>{html.escape(p.description)}</p>"
        body += "<h2>Features</h2><ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in p.features) + "</ul>"
        body += "<h2>Benefits</h2><ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in p.benefits) + "</ul>"
        if p.pricing:
            body += f"<h2>Pricing</h2><p>{html.escape(p.pricing)}</p>"
        if p.limitations:
            body += "<h2>Limitations</h2><ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in p.limitations) + "</ul>"
        body += "</section>"
    return _page(core, "Product", body)


def render_faq_html(core: KnowledgeCore) -> str:
    body = "<h1>Questions this page answers</h1>"
    for q in core.questions:
        body += f"<article><h2>{html.escape(q.question)}</h2><p>{html.escape(q.answer)}</p>"
        if q.limitations:
            body += f"<p><strong>Limit:</strong> {html.escape(q.limitations)}</p>"
        if q.cta:
            body += f"<p><strong>Next step:</strong> {html.escape(q.cta)}</p>"
        body += "</article>"
    return _page(core, "FAQ", body)


def _page(core: KnowledgeCore, title: str, body: str) -> str:
    schema = html.escape(json.dumps(render_schema(core), ensure_ascii=False))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(core.name)} · {html.escape(title)}</title>
  <meta name="description" content="{html.escape(str(core.entity.get('one_line', '')))}">
  <link rel="alternate" type="text/plain" href="../llms.txt">
  <script type="application/ld+json">{schema}</script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; line-height: 1.6; margin: 0; color: #17202a; background: #f7f8fb; }}
    main {{ max-width: 920px; margin: 0 auto; padding: 48px 20px; }}
    nav {{ background: #101828; padding: 14px 20px; }}
    nav a {{ color: white; margin-right: 16px; text-decoration: none; }}
    section, article {{ background: white; padding: 24px; margin: 18px 0; border-radius: 16px; box-shadow: 0 8px 24px rgba(16,24,40,.06); }}
    .hero {{ background: #e8f1ff; }}
    .eyebrow {{ text-transform: uppercase; letter-spacing: .08em; color: #2563eb; font-weight: 700; }}
    h1 {{ font-size: 42px; line-height: 1.1; }}
  </style>
</head>
<body>
<nav><a href="index.html">Home</a><a href="product.html">Product</a><a href="faq.html">FAQ</a></nav>
<main>{body}</main>
</body>
</html>"""


def _product_markdown(product: Product) -> List[str]:
    lines = [f"## {product.name}", "", product.description, "", "### Features", *_bullets(product.features), "", "### Benefits", *_bullets(product.benefits)]
    if product.pricing:
        lines.extend(["", "### Pricing", product.pricing])
    if product.limitations:
        lines.extend(["", "### Limitations", *_bullets(product.limitations)])
    lines.append("")
    return lines


def _question_markdown(q: Question) -> List[str]:
    lines = [f"## Q: {q.question}", "", f"A: {q.answer}"]
    if q.evidence_refs:
        lines.extend(["", "Evidence refs:", *_bullets(q.evidence_refs)])
    if q.limitations:
        lines.extend(["", f"Limitations: {q.limitations}"])
    if q.cta:
        lines.extend(["", f"Recommended next step: {q.cta}"])
    lines.append("")
    return lines


def _bullets(items: Iterable[object]) -> List[str]:
    return [f"- {x}" for x in items]
