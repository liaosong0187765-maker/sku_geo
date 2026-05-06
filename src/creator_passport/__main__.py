from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

from .models import ValidationError, load_generated_passport, load_passport
from .monitor import write_monitor_outputs
from .render import write_all
from .server import serve_directory
from .sku_build import build_sku_catalog
from .sku_models import load_sku_passports
from .sku_monitor_batch import load_runs, write_batch_monitor_outputs
from .sku_render import SKU_REQUIRED_ARTIFACTS, write_catalog_pack
from .sku_review import write_review_artifacts
from .variants import PLATFORMS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Creator Source Passport MVP")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate", help="Generate source site, AI pack, and platform variants")
    generate.add_argument("input", help="Path to Source Passport JSON")
    generate.add_argument("--out", default="generated/demo", help="Output directory")
    generate.add_argument("--base-url", default=None, help="Override creator domain for canonical URLs")

    sku_generate = sub.add_parser("sku-generate", help="Generate SKU source pack artifacts")
    sku_generate.add_argument("input", help="Path to SKU Source Passport JSON")
    sku_generate.add_argument("--out", default="generated/sku", help="Output directory")
    sku_generate.add_argument("--base-url", default=None, help="Override brand domain for canonical URLs")

    sku_build = sub.add_parser("sku-build", help="Build SKU catalog source pack, review artifacts, and monitor outputs")
    sku_build.add_argument("input", help="Path to SKU Source Passport JSON")
    sku_build.add_argument("--out", default="generated/sku", help="Output directory")
    sku_build.add_argument("--base-url", default=None, help="Override brand domain for canonical URLs")
    sku_build.add_argument("--runs", default=None, help="Optional retrieval runs JSON")
    sku_build.add_argument("--no-monitor", action="store_true", help="Skip embedded or external retrieval runs")

    sku_review = sub.add_parser("sku-review", help="Write or validate SKU human review artifacts")
    sku_review.add_argument("--input", required=True, help="Path to SKU Source Passport JSON")
    sku_review.add_argument("--out", default="generated/sku", help="Output directory")
    sku_review.add_argument("--base-url", default=None, help="Override brand domain for canonical URLs")

    sku_monitor_batch = sub.add_parser("sku-monitor-batch", help="Evaluate captured retrieval runs for a SKU catalog")
    sku_monitor_batch.add_argument("input", help="Path to SKU Source Passport JSON")
    sku_monitor_batch.add_argument("--out", default="generated/sku", help="Output directory")
    sku_monitor_batch.add_argument("--runs", required=True, help="Retrieval runs JSON")
    sku_monitor_batch.add_argument("--base-url", default=None, help="Override brand domain for canonical URLs")

    sku_check = sub.add_parser("sku-check", help="Check generated SKU source pack artifacts")
    sku_check.add_argument("out", nargs="?", default="generated/sku")

    publish = sub.add_parser("publish", help="Save a manual platform publication URL")
    publish.add_argument("--out", default="generated/demo", help="Generated output directory")
    publish.add_argument("--platform", required=True, choices=PLATFORMS)
    publish.add_argument("--url", required=True, help="Manually published platform URL")
    publish.add_argument("--method", default="manual")

    monitor = sub.add_parser("monitor", help="Run minimal citation/retrieval monitor against a response fixture")
    monitor.add_argument("--out", default="generated/demo", help="Generated output directory")
    monitor.add_argument("--prompt", default=None)
    monitor.add_argument("--response", default=None)
    monitor.add_argument("--response-file", default=None)

    check = sub.add_parser("check", help="Check generated MVP artifacts")
    check.add_argument("out", nargs="?", default="generated/demo")

    serve = sub.add_parser("serve", help="Generate then serve the static Source Passport site")
    serve.add_argument("input", help="Path to Source Passport JSON")
    serve.add_argument("--out", default="generated/demo")
    serve.add_argument("--base-url", default=None)
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", default=8765, type=int)
    serve.add_argument("--no-build", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            return command_generate(args)
        if args.command == "sku-generate":
            return command_sku_generate(args)
        if args.command == "sku-build":
            return command_sku_build(args)
        if args.command == "sku-review":
            return command_sku_review(args)
        if args.command == "sku-monitor-batch":
            return command_sku_monitor_batch(args)
        if args.command == "sku-check":
            return command_sku_check(args)
        if args.command == "publish":
            return command_publish(args)
        if args.command == "monitor":
            return command_monitor(args)
        if args.command == "check":
            return command_check(args)
        if args.command == "serve":
            return command_serve(args)
    except (OSError, ValueError, ValidationError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


def command_generate(args: argparse.Namespace) -> int:
    passport = load_passport(args.input, base_url=args.base_url)
    paths = write_all(passport, Path(args.out))
    print(f"Generated {len(paths)} files in {args.out}")
    print(f"Canonical source: {passport.canonical_url}")
    print(f"Content hash: {passport.content_hash}")
    return 0


def command_sku_generate(args: argparse.Namespace) -> int:
    passports = load_sku_passports(args.input, base_url=args.base_url)
    paths = write_catalog_pack(passports, Path(args.out))
    print(f"Generated {len(paths)} SKU files in {args.out}")
    for passport in passports:
        print(f"Canonical SKU source: {passport.canonical_url}")
        print(f"Content hash: {passport.content_hash}")
    return 0


def command_sku_build(args: argparse.Namespace) -> int:
    result = build_sku_catalog(
        args.input,
        args.out,
        base_url=args.base_url,
        runs_path=args.runs,
        write_monitor=not args.no_monitor,
    )
    print(f"Built {len(result.passports)} SKU Source Passports in {args.out}")
    print(f"Generated {len(result.paths)} files")
    for passport in result.passports:
        print(f"Canonical SKU source: {passport.canonical_url}")
        print(f"Content hash: {passport.content_hash}")
    return 0


def command_sku_review(args: argparse.Namespace) -> int:
    passports = load_sku_passports(args.input, base_url=args.base_url)
    paths = write_review_artifacts(passports, Path(args.out))
    print(f"Review wrote {len(paths)} files")
    for path in paths:
        print(path)
    return 0


def command_sku_monitor_batch(args: argparse.Namespace) -> int:
    passports = load_sku_passports(args.input, base_url=args.base_url)
    runs = load_runs(args.runs)
    paths = write_batch_monitor_outputs(passports, Path(args.out), runs=runs)
    print(f"Batch monitor wrote {len(paths)} files")
    for path in paths:
        print(path)
    return 0


def command_sku_check(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    required = list(SKU_REQUIRED_ARTIFACTS)
    missing = [rel for rel in required if not (out_dir / rel).exists()]
    stale = _stale_sku_artifacts(out_dir)
    if missing or stale:
        print("Missing required SKU files:")
        for rel in missing:
            print(f"- {rel}")
        if stale:
            print("Unexpected stale SKU files:")
            for rel in stale:
                print(f"- {rel}")
        return 1
    print("Generated SKU Source Passport artifacts look complete.")
    return 0


def command_publish(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    passport = load_generated_passport(str(out_dir))
    publications_path = out_dir / "publications.json"
    data = _read_json(publications_path, {"publications": []})
    variant_path = out_dir / "variants" / f"{args.platform}.md"
    variant_text = variant_path.read_text(encoding="utf-8") if variant_path.exists() else ""
    publication = {
        "platform": args.platform,
        "platform_url": args.url,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "method": args.method,
        "canonical_url": passport.canonical_url,
        "anchor_present": _variant_has_source_anchor(passport, variant_text),
        "status": "published_manually",
    }
    data["publications"] = [item for item in data.get("publications", []) if item.get("platform") != args.platform]
    data["publications"].append(publication)
    publications_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {args.platform} publication URL: {args.url}")
    print(f"Anchor present in variant: {publication['anchor_present']}")
    return 0


def command_monitor(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    passport = load_generated_passport(str(out_dir))
    response = _load_response(args.response, args.response_file)
    prompt = args.prompt or (passport.monitor_prompts[0] if passport.monitor_prompts else f"What is {passport.title}?")
    paths = write_monitor_outputs(passport, out_dir, prompt, response)
    print(f"Monitor wrote {len(paths)} files")
    for path in paths:
        print(path)
    return 0


def command_check(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    passport = load_generated_passport(str(out_dir))
    required = [
        "index.html",
        f"s/{passport.slug}-{passport.content_hash}/index.html",
        f"s/{passport.slug}-{passport.content_hash}.md",
        "llms.txt",
        "llms-full.txt",
        "ai/index.md",
        "ai/profile.md",
        f"ai/sources/{passport.slug}.md",
        "schema.json",
        "sitemap.xml",
        "robots.txt",
        "variants/x.md",
        "variants/linkedin.md",
        "variants/wechat.md",
        "variants/zhihu.md",
    ]
    missing = [rel for rel in required if not (out_dir / rel).exists()]
    anchor_failures = []
    for platform in PLATFORMS:
        path = out_dir / "variants" / f"{platform}.md"
        if path.exists() and not _variant_has_source_anchor(passport, path.read_text(encoding="utf-8")):
            anchor_failures.append(str(path))
    if missing or anchor_failures:
        if missing:
            print("Missing required files:")
            for rel in missing:
                print(f"- {rel}")
        if anchor_failures:
            print("Variants missing canonical source anchor:")
            for rel in anchor_failures:
                print(f"- {rel}")
        return 1
    print("Generated Source Passport artifacts look complete.")
    return 0


def command_serve(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    if not args.no_build:
        passport = load_passport(args.input, base_url=args.base_url)
        write_all(passport, out_dir)
    serve_directory(out_dir, args.host, args.port)
    return 0


def _load_response(response: str | None, response_file: str | None) -> str:
    if response_file:
        return Path(response_file).read_text(encoding="utf-8")
    if response:
        return response
    return "The idea argues that creators should publish durable source pages, but no canonical citation was provided."


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _variant_has_source_anchor(passport: Any, text: str) -> bool:
    return passport.canonical_url in text and passport.content_hash in text


def _stale_sku_artifacts(out_dir: Path) -> list[str]:
    passport_path = out_dir / "sku-passport.json"
    if not passport_path.exists():
        return []
    data = json.loads(passport_path.read_text(encoding="utf-8"))
    sku_sources = data.get("sku_sources") or []
    if not sku_sources and data.get("sku_source"):
        sku_sources = [data["sku_source"]]
    expected_product_files = {
        f"{item.get('slug')}.md"
        for item in sku_sources
        if item.get("slug")
    }
    expected_sku_entries = {
        f"{item.get('slug')}-{item.get('content_hash')}"
        for item in sku_sources
        if item.get("slug") and item.get("content_hash")
    }
    stale: list[str] = []
    products_dir = out_dir / "ai" / "products"
    if products_dir.exists() and expected_product_files:
        for path in products_dir.glob("*.md"):
            if path.name not in expected_product_files:
                stale.append(path.relative_to(out_dir).as_posix())
    sku_dir = out_dir / "sku"
    if sku_dir.exists() and expected_sku_entries:
        expected_markdown = {f"{item}.md" for item in expected_sku_entries}
        for path in sku_dir.iterdir():
            name = path.name
            if path.is_file() and name.endswith(".md") and name not in expected_markdown:
                stale.append(path.relative_to(out_dir).as_posix())
            if path.is_dir() and name not in expected_sku_entries:
                stale.append(path.relative_to(out_dir).as_posix())
    return stale


if __name__ == "__main__":
    raise SystemExit(main())
