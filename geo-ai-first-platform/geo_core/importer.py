from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

DEFAULT_CAMOUFOX_SCRIPT = Path("/home/jetson/.hermes/scripts/camoufox_fetch.py")


class ImportError(RuntimeError):
    pass


@dataclass
class FetchResult:
    title: str
    url: str
    content: str
    screenshot_path: str = ""
    error: str = ""

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "FetchResult":
        return cls(
            title=str(data.get("title") or "").strip(),
            url=str(data.get("url") or "").strip(),
            content=str(data.get("content") or "").strip(),
            screenshot_path=str(data.get("screenshot_path") or "").strip(),
            error=str(data.get("error") or "").strip(),
        )


def fetch_url(url: str, script_path: Path = DEFAULT_CAMOUFOX_SCRIPT, timeout: int = 120) -> FetchResult:
    if not script_path.exists():
        raise ImportError(f"Camoufox script not found: {script_path}")
    command = [
        "python3",
        str(script_path),
        url,
        "--format",
        "markdown",
        "--json",
        "--timeout",
        str(timeout),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout + 30)
    except subprocess.TimeoutExpired as exc:
        raise ImportError(f"Camoufox fetch timed out for {url}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ImportError(f"Camoufox fetch failed for {url}: {detail or exc}") from exc

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ImportError(f"Camoufox returned invalid JSON for {url}") from exc

    fetched = FetchResult.from_json(payload)
    if fetched.error:
        raise ImportError(f"Camoufox reported an error for {url}: {fetched.error}")
    if not fetched.content:
        raise ImportError(f"Camoufox returned empty content for {url}")
    return fetched


def fetch_urls(urls: List[str], script_path: Path = DEFAULT_CAMOUFOX_SCRIPT, timeout: int = 120) -> List[FetchResult]:
    results = []
    for url in urls:
        results.append(fetch_url(url, script_path=script_path, timeout=timeout))
    return results


def import_url_to_core(url: str, script_path: Path = DEFAULT_CAMOUFOX_SCRIPT, timeout: int = 120) -> Dict[str, Any]:
    fetched = fetch_url(url, script_path=script_path, timeout=timeout)
    return build_draft_core(fetched)


def import_urls_to_core(urls: List[str], script_path: Path = DEFAULT_CAMOUFOX_SCRIPT, timeout: int = 120) -> Dict[str, Any]:
    fetched = fetch_urls(urls, script_path=script_path, timeout=timeout)
    return build_merged_draft_core(fetched)


def build_draft_core(fetched: FetchResult) -> Dict[str, Any]:
    content = _clean_text(fetched.content)
    title = fetched.title or _guess_title_from_content(content) or _name_from_url(fetched.url)
    paragraphs = _extract_paragraphs(content)
    bullets = _extract_bullets(content)
    description = _first_nonempty(paragraphs) or title
    one_line = _compress_sentence(description, 180)
    body_sentences = _extract_sentences(content)
    category = _guess_category(content, fetched.url)
    target_customers = _collect_list(body_sentences, bullets, fallback=[
        f"Teams evaluating {title}",
        f"Buyers researching {category.lower()}",
        f"People landing on {title} from AI search",
    ])
    pain_points = _collect_list(
        [s for s in body_sentences if re.search(r"\b(problem|challenge|slow|hard|manual|avoid|without|need)\b", s, re.I)],
        bullets,
        fallback=[
            "Key buyer problems are not clearly structured yet on the site.",
            "Important claims may be buried in page copy instead of answer-ready blocks.",
            "AI systems need a cleaner summary of what this page is about.",
        ],
    )
    use_cases = _collect_list(
        [s for s in body_sentences if re.search(r"\b(use|for|helps|lets|designed|works)\b", s, re.I)],
        bullets,
        fallback=[
            f"Use this page as the base profile for {title}.",
            "Convert long-form page copy into AI-readable summaries.",
            "Draft GEO assets before a manual editor refines them.",
        ],
    )
    not_for = _collect_list(
        [s for s in body_sentences if re.search(r"\b(not|except|avoid|without)\b", s, re.I)],
        [],
        fallback=[
            "Teams expecting this raw import to replace human review.",
            "Pages with missing product or company context.",
            "Sites that hide critical information behind login walls.",
        ],
    )
    features = _collect_list(bullets, body_sentences, fallback=[
        "Imported page title and body content",
        "Initial AI-readable summary generated from Camoufox fetch",
        "Draft claim and FAQ generation from live URL",
    ])
    benefits = _collect_list(
        [s for s in body_sentences if re.search(r"\b(help|benefit|improve|faster|better|save|reduce|enable)\b", s, re.I)],
        bullets,
        fallback=[
            "Turns a live page into a draft knowledge core quickly.",
            "Keeps one source of truth for human pages and AI artifacts.",
            "Creates a reviewable GEO draft before deeper enrichment.",
        ],
    )
    limitations = [
        "This draft is inferred from one fetched page and should be reviewed by a human.",
        "Hidden navigation, pricing, and customer evidence may require more URLs.",
        "AI-facing claims should be checked against original business sources before publishing.",
    ]
    source_id = "source_1"
    review_source_id = "source_2"
    claims = _make_claims(title, body_sentences, description, source_id, review_source_id)
    questions = _make_questions(title, category, description, use_cases, target_customers, claims)
    core = {
        "entity": {
            "name": title,
            "url": fetched.url,
            "category": category,
            "one_line": one_line,
            "description": _join_paragraphs(paragraphs[:2]) or description,
        },
        "audience": {
            "target_customers": target_customers[:4],
            "pain_points": pain_points[:4],
            "use_cases": use_cases[:4],
            "not_for": not_for[:3],
        },
        "products": [
            {
                "name": title,
                "description": description,
                "features": features[:5],
                "benefits": benefits[:4],
                "pricing": _extract_pricing_hint(content),
                "limitations": limitations,
            }
        ],
        "claims": claims,
        "questions": questions,
        "sources": [
            {
                "id": source_id,
                "title": f"Imported page: {title}",
                "url": fetched.url,
                "type": "web_page",
                "date": "",
            },
            {
                "id": review_source_id,
                "title": f"Camoufox markdown snapshot: {title}",
                "url": fetched.url,
                "type": "camoufox_snapshot",
                "date": "",
            },
        ],
        "competitors": [
            {
                "name": "Status quo website copy",
                "url": "",
                "comparison_angle": "This imported GEO draft turns a single page into structured AI-readable assets instead of leaving important facts trapped in free-form page copy.",
            }
        ],
        "import_context": {
            "method": "camoufox",
            "fetched_title": fetched.title,
            "fetched_url": fetched.url,
            "screenshot_path": fetched.screenshot_path,
            "page_count": 1,
        },
    }
    return core


def build_merged_draft_core(fetched_items: List[FetchResult]) -> Dict[str, Any]:
    if not fetched_items:
        raise ImportError("No fetched pages were provided for merge.")
    drafts = [build_draft_core(item) for item in fetched_items]
    if len(drafts) == 1:
        return drafts[0]

    primary = drafts[0]
    merged: Dict[str, Any] = {
        "entity": {
            "name": primary["entity"].get("name", "Imported Website"),
            "url": primary["entity"].get("url", ""),
            "category": _merge_category(drafts),
            "one_line": _first_nonempty([draft["entity"].get("one_line", "") for draft in drafts]),
            "description": _join_paragraphs(_dedupe_keep_order([draft["entity"].get("description", "") for draft in drafts])[:3]),
        },
        "audience": {
            "target_customers": _merge_list_field(drafts, "audience", "target_customers", limit=5),
            "pain_points": _merge_list_field(drafts, "audience", "pain_points", limit=5),
            "use_cases": _merge_list_field(drafts, "audience", "use_cases", limit=5),
            "not_for": _merge_list_field(drafts, "audience", "not_for", limit=4),
        },
        "products": _merge_products(drafts),
        "claims": _merge_claims(drafts),
        "questions": _merge_questions(drafts),
        "sources": _merge_sources(drafts),
        "competitors": _merge_competitors(drafts),
        "import_context": {
            "method": "camoufox-multi-url",
            "page_count": len(fetched_items),
            "urls": [item.url for item in fetched_items],
            "titles": [item.title for item in fetched_items],
            "primary_url": primary["entity"].get("url", ""),
        },
    }
    return merged


def save_fetch_artifacts(fetched: FetchResult, out_dir: Path) -> List[Path]:
    return save_fetch_artifacts_batch([fetched], out_dir)


def save_fetch_artifacts_batch(fetched_items: List[FetchResult], out_dir: Path) -> List[Path]:
    source_dir = out_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    manifest = []
    for index, fetched in enumerate(fetched_items, start=1):
        slug = _slugify(fetched.title or _name_from_url(fetched.url) or f"page-{index}")
        md_path = source_dir / f"page-{index:02d}-{slug}.md"
        json_path = source_dir / f"page-{index:02d}-{slug}.json"
        md_path.write_text(fetched.content.rstrip() + "\n", encoding="utf-8")
        json_path.write_text(json.dumps({
            "title": fetched.title,
            "url": fetched.url,
            "screenshot_path": fetched.screenshot_path,
            "error": fetched.error,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths.extend([md_path, json_path])
        manifest.append({
            "index": index,
            "title": fetched.title,
            "url": fetched.url,
            "markdown_file": md_path.name,
            "metadata_file": json_path.name,
            "screenshot_path": fetched.screenshot_path,
        })

    manifest_path = source_dir / "manifest.json"
    manifest_path.write_text(json.dumps({"pages": manifest}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths.append(manifest_path)
    return paths


def _make_claims(title: str, sentences: List[str], description: str, source_id: str, review_source_id: str) -> List[Dict[str, Any]]:
    base = _collect_list(sentences, [], fallback=[description, f"{title} has a live web presence that can be converted into AI-readable assets."])
    templates = [
        (f"{title} can be summarized into a structured AI-readable business profile.", base[0], source_id, "high"),
        (f"{title} contains product or company information that can seed answer-ready GEO content.", base[1] if len(base) > 1 else base[0], review_source_id, "medium"),
        (f"{title} should be reviewed by a human before publishing AI-facing claims.", "This draft comes from one fetched URL and may miss supporting context from other pages.", review_source_id, "high"),
    ]
    claims = []
    for index, (claim, evidence, claim_source, confidence) in enumerate(templates, start=1):
        claims.append({
            "id": f"claim_{index}",
            "claim": _compress_sentence(claim, 180),
            "evidence": _compress_sentence(evidence, 220),
            "source": claim_source,
            "confidence": confidence,
            "related_questions": [],
        })
    return claims


def _make_questions(
    title: str,
    category: str,
    description: str,
    use_cases: List[str],
    target_customers: List[str],
    claims: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    primary_claims = [claim["id"] for claim in claims]
    return [
        {
            "question": f"What is {title}?",
            "answer": _compress_sentence(description, 260),
            "evidence_refs": primary_claims[:2],
            "limitations": "This answer is based on imported pages and may need extra business context.",
            "cta": "Review the imported summary and replace generic wording with exact positioning.",
        },
        {
            "question": f"Who is {title} for?",
            "answer": _compress_sentence(" ".join(target_customers[:3]), 260),
            "evidence_refs": primary_claims[:1],
            "limitations": "Audience fit is inferred from visible copy, not confirmed by the business owner.",
            "cta": "Add a precise ICP section after import.",
        },
        {
            "question": f"What category does {title} belong to?",
            "answer": f"This content is currently categorized as {category.lower()} for GEO drafting.",
            "evidence_refs": primary_claims[:1],
            "limitations": "Category should be manually refined if the website serves multiple business lines.",
            "cta": "Confirm the final category before publishing schema or llms files.",
        },
        {
            "question": f"How can {title} be used in an AI-first content workflow?",
            "answer": _compress_sentence(" ".join(use_cases[:3]), 260),
            "evidence_refs": primary_claims[:2],
            "limitations": "Use cases are inferred from page text and may not cover the full offer.",
            "cta": "Import more URLs like pricing, FAQ, and case-study pages for a stronger draft.",
        },
        {
            "question": f"What should be checked before publishing {title} as GEO content?",
            "answer": "Check the factual claims, add stronger evidence sources, confirm target audience fit, and rewrite any generic import placeholders.",
            "evidence_refs": primary_claims,
            "limitations": "An imported draft is not a final brand-approved content asset.",
            "cta": "Run human review on claims, FAQ answers, and comparison angles.",
        },
    ]


def _merge_list_field(drafts: List[Dict[str, Any]], section: str, key: str, limit: int) -> List[str]:
    values: List[str] = []
    for draft in drafts:
        values.extend(draft.get(section, {}).get(key, []))
    return _dedupe_keep_order(values)[:limit]


def _merge_products(drafts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    products: List[Dict[str, Any]] = []
    seen = set()
    for draft in drafts:
        for product in draft.get("products", []):
            name = _clean_line(str(product.get("name", "")))
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            products.append(product)
    return products[:5] or drafts[0].get("products", [])


def _merge_claims(drafts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = []
    seen = set()
    index = 1
    for draft in drafts:
        for claim in draft.get("claims", []):
            text = _clean_line(str(claim.get("claim", "")))
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append({
                **claim,
                "id": f"claim_{index}",
            })
            index += 1
    return merged[:8]


def _merge_questions(drafts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = []
    seen = set()
    for draft in drafts:
        for question in draft.get("questions", []):
            text = _clean_line(str(question.get("question", "")))
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(question)
    return merged[:10]


def _merge_sources(drafts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = []
    seen = set()
    index = 1
    for draft in drafts:
        for source in draft.get("sources", []):
            key = (str(source.get("url", "")).strip(), str(source.get("title", "")).strip())
            if key in seen:
                continue
            seen.add(key)
            merged.append({
                **source,
                "id": f"source_{index}",
            })
            index += 1
    return merged[:10]


def _merge_competitors(drafts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged = []
    seen = set()
    for draft in drafts:
        for competitor in draft.get("competitors", []):
            name = _clean_line(str(competitor.get("name", "")))
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(competitor)
    return merged[:5]


def _merge_category(drafts: List[Dict[str, Any]]) -> str:
    categories = _dedupe_keep_order([draft.get("entity", {}).get("category", "") for draft in drafts])
    if not categories:
        return "Imported multi-page website"
    if len(categories) == 1:
        return categories[0]
    return f"Multi-page website import ({'; '.join(categories[:3])})"


def _guess_title_from_content(content: str) -> str:
    for line in content.splitlines():
        line = line.strip().lstrip("#").strip()
        if line:
            return line
    return ""


def _extract_paragraphs(content: str) -> List[str]:
    paragraphs: List[str] = []
    current: List[str] = []
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        if line.startswith("#") or line.startswith("-") or line.startswith("*"):
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        if re.match(r"^\[.+\]\(.+\)$", line):
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current).strip())
    return [_compress_sentence(p, 420) for p in paragraphs if p.strip()]


def _extract_bullets(content: str) -> List[str]:
    bullets = []
    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith(("- ", "* ")):
            bullets.append(_clean_line(line[2:]))
    return [item for item in bullets if item]


def _extract_sentences(content: str) -> List[str]:
    text = re.sub(r"[#*`>]", " ", content)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    chunks = re.split(r"(?<=[.!?])\s+", text)
    sentences = []
    seen = set()
    for chunk in chunks:
        line = _clean_line(chunk)
        if len(line) < 25:
            continue
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        sentences.append(line)
    return sentences


def _guess_category(content: str, url: str) -> str:
    lowered = content.lower()
    keyword_map = [
        ("pricing", "Commercial software or service page"),
        ("faq", "FAQ or support page"),
        ("case study", "Case study or proof page"),
        ("product", "Product or solution page"),
        ("platform", "Software platform page"),
    ]
    for keyword, label in keyword_map:
        if keyword in lowered:
            return label
    host = urlparse(url).netloc.replace("www.", "")
    return f"Imported website page from {host or 'unknown site'}"


def _extract_pricing_hint(content: str) -> str:
    money = re.findall(r"(?:\$|USD|RMB|¥|€)\s?\d[\d,]*(?:\.\d+)?", content, flags=re.I)
    if money:
        return "Pricing hints found on page: " + ", ".join(money[:3]) + "."
    return "Pricing not clearly visible in the imported page."


def _collect_list(primary: List[str], secondary: List[str], fallback: List[str], limit: int = 5) -> List[str]:
    items: List[str] = []
    seen = set()
    for source in (primary, secondary, fallback):
        for raw in source:
            line = _clean_line(raw)
            if len(line) < 12:
                continue
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            items.append(_compress_sentence(line, 180))
            if len(items) >= limit:
                return items
    return items


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clean_line(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip(" -•\t")
    return text.strip()


def _compress_sentence(text: str, limit: int) -> str:
    text = _clean_line(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _join_paragraphs(paragraphs: List[str]) -> str:
    return "\n\n".join(p for p in paragraphs if p)


def _first_nonempty(values: List[str]) -> str:
    for value in values:
        if str(value).strip():
            return str(value).strip()
    return ""


def _dedupe_keep_order(values: List[str]) -> List[str]:
    items = []
    seen = set()
    for raw in values:
        value = _clean_line(str(raw))
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(value)
    return items


def _name_from_url(url: str) -> str:
    host = urlparse(url).netloc.replace("www.", "")
    if not host:
        return "Imported Website"
    base = host.split(".")[0]
    return base.replace("-", " ").replace("_", " ").title()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "page"
