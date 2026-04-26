from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from geo_core.generator import write_all
from geo_core.importer import DEFAULT_CAMOUFOX_SCRIPT, ImportError, build_merged_draft_core, fetch_urls, save_fetch_artifacts_batch
from geo_core.model import KnowledgeCore, ValidationError
from geo_core.scoring import score


def load_input(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() != ".json":
        raise ValueError("This MVP supports JSON input only. Convert YAML to JSON for now.")
    return json.loads(path.read_text(encoding="utf-8"))


def load_from_urls(urls: list[str], out_dir: Path, script_path: Path, timeout: int) -> tuple[dict, list[Path]]:
    fetched_items = fetch_urls(urls, script_path=script_path, timeout=timeout)
    data = build_merged_draft_core(fetched_items)
    artifact_paths = save_fetch_artifacts_batch(fetched_items, out_dir)
    return data, artifact_paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate AI-first GEO artifacts from a company knowledge core.")
    parser.add_argument("input", type=Path, nargs="?", help="Path to company JSON file")
    parser.add_argument("--url", action="append", help="Import one or more live pages with Camoufox and turn them into a draft knowledge core")
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Output directory")
    parser.add_argument("--camoufox-script", type=Path, default=DEFAULT_CAMOUFOX_SCRIPT, help="Path to camoufox_fetch.py")
    parser.add_argument("--fetch-timeout", type=int, default=120, help="Camoufox page fetch timeout in seconds")
    args = parser.parse_args(argv)

    if not args.input and not args.url:
        parser.error("Provide either a JSON input path or at least one --url.")
    if args.input and args.url:
        parser.error("Use either a JSON input path or --url, not both.")

    extra_paths: list[Path] = []
    try:
        if args.url:
            data, extra_paths = load_from_urls(args.url, args.out, args.camoufox_script, args.fetch_timeout)
        else:
            data = load_input(args.input)
        core = KnowledgeCore.from_dict(data)
        paths = extra_paths + write_all(core, args.out)
        total, dimensions, missing = score(core)
    except (OSError, ValueError, ValidationError, json.JSONDecodeError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Generated {len(paths)} files in {args.out}")
    print(f"AI readiness score: {total}/100")
    for name, detail in dimensions.items():
        print(f"- {name}: {detail['score']}/100 ({detail['passed']}/{detail['total']})")
    if missing:
        print("Missing/weak items:")
        for item in missing:
            print(f"  - {item}")
    print("\nKey outputs:")
    for path in paths:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
