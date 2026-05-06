from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
from typing import Any, Iterable


SUPPORTED_SOURCE_EXTENSIONS = {".md", ".markdown", ".txt", ".text"}
ORIGIN_MANUAL_MARKDOWN = "manual_markdown"
ORIGIN_LOCAL_FILE = "local_file"
SUPPORTED_ORIGIN_TYPES = {ORIGIN_MANUAL_MARKDOWN, ORIGIN_LOCAL_FILE}


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = [value]
    return [item for item in (_text(item) for item in items) if item]


def _metadata(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items() if str(key)}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "source"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compute_source_hash(raw_markdown: str) -> str:
    return hashlib.sha256(raw_markdown.encode("utf-8")).hexdigest()[:12]


def is_supported_source_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_SOURCE_EXTENSIONS


def _normalize_approved_roots(approved_roots: Iterable[str | Path] | None) -> list[Path]:
    roots = [Path.cwd()] if approved_roots is None else [Path(root) for root in approved_roots]
    return [root.resolve(strict=False) for root in roots]


def _is_within(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath(
            [os.path.normcase(str(path)), os.path.normcase(str(root))]
        ) == os.path.normcase(str(root))
    except ValueError:
        return False


def _has_external_path_component(path: Path) -> bool:
    return any(part.casefold() == "external" for part in path.parts)


def _validate_approved_source_path(
    path: str | Path,
    approved_roots: Iterable[str | Path] | None,
) -> Path:
    source_path = Path(path).resolve(strict=False)
    roots = _normalize_approved_roots(approved_roots)

    if _has_external_path_component(source_path):
        raise ValueError("Source file path is inside external/ and cannot be used for intake")

    if not roots or not any(_is_within(source_path, root) for root in roots):
        raise ValueError("Source file path is outside approved roots")

    return source_path


@dataclass
class RawSourceDocument:
    id: str
    origin_type: str
    title: str
    raw_markdown: str
    origin_url: str = ""
    file_path: str = ""
    captured_at: str = ""
    content_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_manual_markdown(
        cls,
        raw_markdown: str,
        *,
        title: str,
        origin_url: str = "",
        captured_at: str = "",
        id: str = "",
        metadata: dict[str, Any] | None = None,
        warnings: list[str] | None = None,
    ) -> "RawSourceDocument":
        document = cls(
            id=_text(id),
            origin_type=ORIGIN_MANUAL_MARKDOWN,
            title=_text(title),
            raw_markdown=str(raw_markdown or ""),
            origin_url=_text(origin_url),
            file_path="",
            captured_at=_text(captured_at) or _utc_now(),
            warnings=_string_list(warnings),
            metadata=_metadata(metadata),
        )
        document._finalize_identity()
        document.validate()
        return document

    @classmethod
    def from_local_file(
        cls,
        path: str | Path,
        *,
        title: str = "",
        origin_url: str = "",
        captured_at: str = "",
        id: str = "",
        approved_roots: Iterable[str | Path] | None = None,
        metadata: dict[str, Any] | None = None,
        warnings: list[str] | None = None,
    ) -> "RawSourceDocument":
        source_path = _validate_approved_source_path(path, approved_roots)
        if not is_supported_source_path(source_path):
            raise ValueError(
                "Unsupported source file extension: "
                f"{source_path.suffix or '(none)'}. Supported extensions: "
                + ", ".join(sorted(SUPPORTED_SOURCE_EXTENSIONS))
            )
        raw_markdown = source_path.read_text(encoding="utf-8")
        document = cls(
            id=_text(id),
            origin_type=ORIGIN_LOCAL_FILE,
            title=_text(title) or source_path.stem,
            raw_markdown=raw_markdown,
            origin_url=_text(origin_url),
            file_path=str(source_path),
            captured_at=_text(captured_at) or _utc_now(),
            warnings=_string_list(warnings),
            metadata=_metadata(metadata),
        )
        document._finalize_identity()
        document.validate()
        return document

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, strict: bool = False) -> "RawSourceDocument":
        if strict:
            known_keys = set(cls.__dataclass_fields__)
            unknown_keys = sorted(str(key) for key in data if key not in known_keys)
            if unknown_keys:
                raise ValueError("Unknown fields: " + ", ".join(unknown_keys))

        document = cls(
            id=_text(data.get("id")),
            origin_type=_text(data.get("origin_type")),
            title=_text(data.get("title")),
            raw_markdown=str(data.get("raw_markdown") or ""),
            origin_url=_text(data.get("origin_url")),
            file_path=_text(data.get("file_path")),
            captured_at=_text(data.get("captured_at")),
            content_hash=_text(data.get("content_hash")),
            warnings=_string_list(data.get("warnings")),
            metadata=_metadata(data.get("metadata")),
        )
        if not strict:
            document._finalize_identity()
        document.validate()
        return document

    def _finalize_identity(self) -> None:
        if not self.captured_at:
            self.captured_at = _utc_now()
        expected_hash = compute_source_hash(self.raw_markdown)
        if not self.content_hash:
            self.content_hash = expected_hash
        if not self.id:
            self.id = f"{_slugify(self.title)}-{self.content_hash}"

    def validate(self) -> None:
        missing: list[str] = []
        if not self.id:
            missing.append("id")
        if not self.origin_type:
            missing.append("origin_type")
        if not self.title:
            missing.append("title")
        if not self.raw_markdown:
            missing.append("raw_markdown")
        if not self.captured_at:
            missing.append("captured_at")
        if not self.content_hash:
            missing.append("content_hash")
        if missing:
            raise ValueError("Missing required fields: " + ", ".join(missing))

        if self.origin_type not in SUPPORTED_ORIGIN_TYPES:
            raise ValueError(
                "Unsupported origin_type: "
                f"{self.origin_type}. Supported origin types: "
                + ", ".join(sorted(SUPPORTED_ORIGIN_TYPES))
            )
        if self.origin_type == ORIGIN_LOCAL_FILE and not self.file_path:
            raise ValueError("Missing required fields: file_path")
        if self.file_path and not is_supported_source_path(self.file_path):
            self._add_warning(
                "Unsupported source file extension: "
                f"{Path(self.file_path).suffix or '(none)'}"
            )
            raise ValueError(self.warnings[-1])

        expected_hash = compute_source_hash(self.raw_markdown)
        if self.content_hash != expected_hash:
            raise ValueError("content_hash does not match raw_markdown")

    def _add_warning(self, warning: str) -> None:
        if warning and warning not in self.warnings:
            self.warnings.append(warning)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_raw_source(
    path: str | Path,
    *,
    title: str = "",
    origin_url: str = "",
    captured_at: str = "",
    id: str = "",
    approved_roots: Iterable[str | Path] | None = None,
    metadata: dict[str, Any] | None = None,
) -> RawSourceDocument:
    return RawSourceDocument.from_local_file(
        path,
        title=title,
        origin_url=origin_url,
        captured_at=captured_at,
        id=id,
        approved_roots=approved_roots,
        metadata=metadata,
    )
