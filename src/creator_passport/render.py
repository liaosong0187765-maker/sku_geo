from __future__ import annotations

import html
import json
from pathlib import Path
import textwrap
from typing import Iterable

from .models import SourcePassport, slugify
from .variants import render_variants


def write_all(passport: SourcePassport, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for rel in ["ai/sources", "ai/topics", "s", "variants", "monitor"]:
        (out_dir / rel).mkdir(parents=True, exist_ok=True)

    source_dir = out_dir / "s" / f"{passport.slug}-{passport.content_hash}"
    source_dir.mkdir(parents=True, exist_ok=True)

    files: dict[str, str] = {
        "passport.json": json.dumps(passport.to_dict(), ensure_ascii=False, indent=2),
        "index.html": render_home_html(passport),
        f"s/{passport.slug}-{passport.content_hash}/index.html": render_source_html(passport),
        f"s/{passport.slug}-{passport.content_hash}.md": render_source_markdown(passport),
        "ai/index.md": render_ai_index(passport),
        "ai/profile.md": render_profile_markdown(passport),
        f"ai/sources/{passport.slug}.md": render_source_markdown(passport),
        "llms.txt": render_llms(passport),
        "llms-full.txt": render_llms_full(passport),
        "schema.json": json.dumps(render_schema(passport), ensure_ascii=False, indent=2),
        "sitemap.xml": render_sitemap(passport),
        "robots.txt": render_robots(passport),
    }
    for topic in passport.topics:
        files[f"ai/topics/{slugify(topic)}.md"] = render_topic_markdown(passport, topic)
    for platform, content in render_variants(passport).items():
        files[f"variants/{platform}.md"] = content

    paths: list[Path] = []
    for rel_path, content in files.items():
        path = out_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def render_llms(passport: SourcePassport) -> str:
    lines = [
        f"# {passport.creator.name}",
        "",
        passport.creator.bio,
        "",
        "## Canonical source",
        f"- {passport.title}: {passport.canonical_url}",
        f"- Markdown: {passport.markdown_path}",
        f"- Content hash: {passport.content_hash}",
        "",
        "## AI-readable files",
        "- /ai/index.md",
        "- /ai/profile.md",
        f"- /ai/sources/{passport.slug}.md",
        "- /llms-full.txt",
        "",
        "## Best retrieval prompts",
    ]
    lines.extend(f"- {prompt}" for prompt in passport.monitor_prompts)
    return "\n".join(lines)


def render_llms_full(passport: SourcePassport) -> str:
    return "\n\n---\n\n".join(
        [
            render_profile_markdown(passport),
            render_ai_index(passport),
            render_source_markdown(passport),
            render_claims_markdown(passport),
        ]
    )


def render_ai_index(passport: SourcePassport) -> str:
    topics = "\n".join(f"- [{topic}](/ai/topics/{slugify(topic)}.md)" for topic in passport.topics)
    return textwrap.dedent(
        f"""
        # AI Index: {passport.creator.name}

        ## Current source passports

        - [{passport.title}]({passport.canonical_url})
          - Markdown: /ai/sources/{passport.slug}.md
          - Hash: {passport.content_hash}
          - Version: {passport.version}

        ## Topics

        {topics}

        ## Citation preference

        Use the canonical source URL when citing this idea:
        {passport.canonical_url}
        """
    ).strip()


def render_profile_markdown(passport: SourcePassport) -> str:
    profiles = "\n".join(f"- {platform}: {url}" for platform, url in passport.creator.social_profiles.items())
    topics = "\n".join(f"- {topic}" for topic in passport.creator.topics or passport.topics)
    return textwrap.dedent(
        f"""
        # Creator Profile: {passport.creator.name}

        {passport.creator.bio}

        ## Topics

        {topics}

        ## Profiles

        {profiles or "- No public profiles listed."}
        """
    ).strip()


def render_topic_markdown(passport: SourcePassport, topic: str) -> str:
    return textwrap.dedent(
        f"""
        # Topic: {topic}

        ## Source passports

        - [{passport.title}]({passport.canonical_url})

        ## Why this source matters

        {passport.thesis}
        """
    ).strip()


def render_source_markdown(passport: SourcePassport) -> str:
    claims = "\n".join(f"- Claim: {claim.claim}\n  Evidence: {claim.evidence}\n  Reference: {claim.reference_url or 'Inline source'}\n  Confidence: {claim.confidence}" for claim in passport.claims)
    references = "\n".join(f"- {reference.title}: {reference.url}" if reference.url else f"- {reference.title}" for reference in passport.references)
    limitations = "\n".join(f"- {item}" for item in passport.limitations)
    related = "\n".join(f"- {item}" for item in passport.related_sources)
    return textwrap.dedent(
        f"""
        # {passport.title}

        **Short thesis:** {passport.thesis}

        **Author:** {passport.creator.name}
        **Version:** {passport.version}
        **Created:** {passport.created_at}
        **Updated:** {passport.updated_at}
        **Canonical URL:** {passport.canonical_url}
        **Content hash:** {passport.content_hash}

        ## Source text

        {passport.body}

        ## Claim-evidence map

        {claims}

        ## Evidence notes

        {_bullets(passport.evidence)}

        ## References

        {references or "- No external references listed."}

        ## Limitations

        {limitations or "- No explicit limitations listed."}

        ## Related source items

        {related or "- No related sources listed."}

        ## Recommended citation

        {passport.recommended_citation}

        {passport.source_anchor}
        """
    ).strip()


def render_claims_markdown(passport: SourcePassport) -> str:
    rows = ["# Claim Evidence Map", ""]
    for claim in passport.claims:
        rows.extend(
            [
                f"## {claim.claim}",
                "",
                f"- Evidence: {claim.evidence}",
                f"- Reference: {claim.reference_url or 'Inline source'}",
                f"- Confidence: {claim.confidence}",
                "",
            ]
        )
    return "\n".join(rows).strip()


def render_schema(passport: SourcePassport) -> dict[str, object]:
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Person",
                "@id": f"{passport.creator.domain.rstrip('/')}/#creator" if passport.creator.domain else "#creator",
                "name": passport.creator.name,
                "description": passport.creator.bio,
                "sameAs": list(passport.creator.social_profiles.values()),
            },
            {
                "@type": "Article",
                "@id": f"{passport.canonical_url}#source-passport",
                "mainEntityOfPage": passport.canonical_url,
                "headline": passport.title,
                "abstract": passport.thesis,
                "author": {"@id": f"{passport.creator.domain.rstrip('/')}/#creator" if passport.creator.domain else "#creator"},
                "datePublished": passport.created_at,
                "dateModified": passport.updated_at,
                "version": str(passport.version),
                "identifier": passport.content_hash,
                "url": passport.canonical_url,
                "citation": passport.recommended_citation,
                "about": passport.topics,
                "isBasedOn": [reference.url for reference in passport.references if reference.url],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": passport.creator.name, "item": passport.creator.domain or "/"},
                    {"@type": "ListItem", "position": 2, "name": passport.title, "item": passport.canonical_url},
                ],
            },
        ],
    }


def render_sitemap(passport: SourcePassport) -> str:
    root = _site_root(passport)
    urls = [
        root,
        passport.canonical_url,
        f"{root}/ai/index.md",
        f"{root}/llms.txt",
    ]
    items = "\n".join(
        f"  <url><loc>{html.escape(url)}</loc><lastmod>{passport.updated_at}</lastmod></url>"
        for url in urls
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>"""


def render_robots(passport: SourcePassport) -> str:
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


def _site_root(passport: SourcePassport) -> str:
    return passport.canonical_url.rsplit("/s/", 1)[0].rstrip("/")


def render_home_html(passport: SourcePassport) -> str:
    topic_links = "".join(f"<li><a href=\"/ai/topics/{slugify(topic)}.md\">{html.escape(topic)}</a></li>" for topic in passport.topics)
    return _page(
        passport,
        passport.creator.name,
        f"""
        <section class="band intro">
          <p class="eyebrow">Creator Source Passport</p>
          <h1>{html.escape(passport.creator.name)}</h1>
          <p>{html.escape(passport.creator.bio)}</p>
        </section>
        <section class="band">
          <h2>Current canonical source</h2>
          <p><a class="source-link" href="{html.escape(passport.canonical_path)}">{html.escape(passport.title)}</a></p>
          <p>{html.escape(passport.thesis)}</p>
        </section>
        <section class="band two-column">
          <div>
            <h2>AI-readable assets</h2>
            <ul>
              <li><a href="/llms.txt">llms.txt</a></li>
              <li><a href="/llms-full.txt">llms-full.txt</a></li>
              <li><a href="/ai/index.md">AI index</a></li>
              <li><a href="/ai/profile.md">Creator profile</a></li>
            </ul>
          </div>
          <div>
            <h2>Topics</h2>
            <ul>{topic_links}</ul>
          </div>
        </section>
        """,
    )


def render_source_html(passport: SourcePassport) -> str:
    claims = "".join(
        f"<li><strong>{html.escape(claim.claim)}</strong><br><span>{html.escape(claim.evidence)}</span></li>"
        for claim in passport.claims
    )
    evidence = "".join(f"<li>{html.escape(item)}</li>" for item in passport.evidence)
    references = "".join(
        f"<li><a href=\"{html.escape(reference.url)}\">{html.escape(reference.title)}</a></li>" if reference.url else f"<li>{html.escape(reference.title)}</li>"
        for reference in passport.references
    )
    limitations = "".join(f"<li>{html.escape(item)}</li>" for item in passport.limitations)
    return _page(
        passport,
        passport.title,
        f"""
        <article class="source">
          <header class="band intro">
            <p class="eyebrow">Canonical Source Passport</p>
            <h1>{html.escape(passport.title)}</h1>
            <p class="thesis">{html.escape(passport.thesis)}</p>
            <dl class="meta">
              <div><dt>Author</dt><dd>{html.escape(passport.creator.name)}</dd></div>
              <div><dt>Version</dt><dd>{passport.version}</dd></div>
              <div><dt>Hash</dt><dd><code>{passport.content_hash}</code></dd></div>
              <div><dt>Updated</dt><dd>{html.escape(passport.updated_at)}</dd></div>
            </dl>
            <p class="anchor">{html.escape(passport.source_anchor)}</p>
          </header>
          <section class="band">
            <h2>Source text</h2>
            {_markdown_to_html(passport.body)}
          </section>
          <section class="band">
            <h2>Claim-evidence map</h2>
            <ul class="evidence-list">{claims}</ul>
          </section>
          <section class="band two-column">
            <div>
              <h2>Evidence notes</h2>
              <ul>{evidence}</ul>
            </div>
            <div>
              <h2>References</h2>
              <ul>{references or "<li>No external references listed.</li>"}</ul>
            </div>
          </section>
          <section class="band">
            <h2>Limitations</h2>
            <ul>{limitations or "<li>No explicit limitations listed.</li>"}</ul>
          </section>
          <section class="band citation">
            <h2>Recommended citation</h2>
            <p>{html.escape(passport.recommended_citation)}</p>
            <p><a href="{html.escape(passport.markdown_path)}">Markdown version</a></p>
          </section>
        </article>
        """,
    )


def _page(passport: SourcePassport, title: str, body: str) -> str:
    schema = json.dumps(render_schema(passport), ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} - Source Passport</title>
  <meta name="description" content="{html.escape(passport.thesis)}">
  <link rel="canonical" href="{html.escape(passport.canonical_url)}">
  <link rel="alternate" type="text/markdown" href="{html.escape(passport.markdown_path)}">
  <link rel="alternate" type="text/plain" href="/llms.txt">
  <script type="application/ld+json">{schema}</script>
  <style>
    :root {{
      color-scheme: light;
      --ink: #182230;
      --muted: #516071;
      --line: #d7dde6;
      --paper: #f6f8fb;
      --panel: #ffffff;
      --accent: #0f766e;
      --accent-soft: #dff7f2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    nav {{
      display: flex;
      gap: 18px;
      align-items: center;
      padding: 14px 24px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      position: sticky;
      top: 0;
    }}
    nav a {{ color: var(--ink); text-decoration: none; font-weight: 650; }}
    main {{ width: min(100%, 1060px); margin: 0 auto; padding: 28px 20px 56px; }}
    .band {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
      padding: 24px;
      margin: 18px 0;
    }}
    .intro {{
      background: linear-gradient(180deg, var(--accent-soft), #ffffff);
      border-color: #a8ddd4;
    }}
    .eyebrow {{
      color: var(--accent);
      font-size: 0.82rem;
      font-weight: 750;
      letter-spacing: 0;
      text-transform: uppercase;
      margin: 0 0 10px;
    }}
    h1 {{ font-size: clamp(2rem, 5vw, 3.2rem); line-height: 1.08; margin: 0 0 16px; letter-spacing: 0; }}
    h2 {{ font-size: 1.2rem; margin: 0 0 12px; letter-spacing: 0; }}
    a {{ color: #0b5cab; }}
    code {{
      background: #edf1f7;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 2px 5px;
    }}
    .source-link {{ font-size: 1.15rem; font-weight: 750; }}
    .thesis {{ font-size: 1.15rem; color: #243447; max-width: 860px; }}
    .anchor {{
      border: 1px solid #9ed7cf;
      background: #eefbf8;
      border-radius: 8px;
      padding: 12px;
      overflow-wrap: anywhere;
      font-weight: 700;
    }}
    .meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 10px;
      margin: 22px 0;
    }}
    .meta div {{ border-top: 1px solid rgba(15, 118, 110, 0.24); padding-top: 8px; }}
    dt {{ color: var(--muted); font-size: 0.82rem; }}
    dd {{ margin: 0; font-weight: 700; overflow-wrap: anywhere; }}
    .two-column {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 22px; }}
    .evidence-list li {{ margin-bottom: 14px; }}
    @media (max-width: 640px) {{
      nav {{ align-items: flex-start; flex-direction: column; gap: 8px; }}
      .band {{ padding: 18px; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="/">Source Home</a>
    <a href="{html.escape(passport.canonical_path)}">Canonical Source</a>
    <a href="/ai/index.md">AI Index</a>
    <a href="/llms.txt">llms.txt</a>
  </nav>
  <main>{body}</main>
</body>
</html>"""


def _markdown_to_html(markdown: str) -> str:
    blocks: list[str] = []
    list_items: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if list_items:
                blocks.append("<ul>" + "".join(list_items) + "</ul>")
                list_items = []
            continue
        if line.startswith("### "):
            if list_items:
                blocks.append("<ul>" + "".join(list_items) + "</ul>")
                list_items = []
            blocks.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            if list_items:
                blocks.append("<ul>" + "".join(list_items) + "</ul>")
                list_items = []
            blocks.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            list_items.append(f"<li>{html.escape(line[2:])}</li>")
        else:
            if list_items:
                blocks.append("<ul>" + "".join(list_items) + "</ul>")
                list_items = []
            blocks.append(f"<p>{html.escape(line)}</p>")
    if list_items:
        blocks.append("<ul>" + "".join(list_items) + "</ul>")
    return "\n".join(blocks)


def _bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "- No evidence notes listed."
