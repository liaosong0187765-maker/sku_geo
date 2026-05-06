from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .sku_models import load_sku_passports, SkuSourcePassport
from .sku_monitor_batch import load_runs, write_batch_monitor_outputs
from .sku_render import write_catalog_pack
from .sku_review import write_review_artifacts


@dataclass(frozen=True)
class SkuBuildResult:
    passports: tuple[SkuSourcePassport, ...]
    paths: tuple[Path, ...]


def build_sku_catalog(
    input_path: str | Path,
    out_dir: str | Path,
    *,
    base_url: str | None = None,
    runs_path: str | Path | None = None,
    write_monitor: bool = True,
) -> SkuBuildResult:
    passports = tuple(load_sku_passports(input_path, base_url=base_url))
    output = Path(out_dir)
    paths: list[Path] = []
    paths.extend(write_catalog_pack(passports, output))
    paths.extend(write_review_artifacts(passports, output))
    if write_monitor:
        runs = load_runs(runs_path) if runs_path else None
        if runs is not None or any(passport.retrieval_runs for passport in passports):
            paths.extend(write_batch_monitor_outputs(passports, output, runs=runs))
    return SkuBuildResult(passports=passports, paths=tuple(paths))


__all__ = [
    "SkuBuildResult",
    "build_sku_catalog",
]
