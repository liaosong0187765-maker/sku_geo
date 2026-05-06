from __future__ import annotations

from dataclasses import dataclass, field
import asyncio
import importlib
import inspect
import ipaddress
import os
from pathlib import Path
from typing import Any, Callable, Protocol
from urllib.parse import urlparse

from .intake import RawSourceDocument


class AdapterUnavailableError(RuntimeError):
    pass


class AdapterConversionError(RuntimeError):
    pass


class _MarkItDownConverter(Protocol):
    def convert_local(self, path: str) -> Any: ...

    def convert(self, path: str) -> Any: ...


class _Crawl4AICrawler(Protocol):
    def arun(self, url: str, **kwargs: Any) -> Any: ...


@dataclass(frozen=True)
class SourceAdapterResult:
    document: RawSourceDocument
    adapter: str
    source_kind: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter,
            "source_kind": self.source_kind,
            "metadata": dict(self.metadata),
            "document": self.document.to_dict(),
        }


def markitdown_available() -> bool:
    try:
        importlib.import_module("markitdown")
    except ModuleNotFoundError:
        return False
    return True


def crawl4ai_available() -> bool:
    try:
        importlib.import_module("crawl4ai")
    except ModuleNotFoundError:
        return False
    return True


def convert_local_file_with_markitdown(
    path: str | Path,
    *,
    approved_roots: list[str | Path] | None = None,
    title: str = "",
    origin_url: str = "",
    captured_at: str = "",
    metadata: dict[str, Any] | None = None,
    allow_external_source: bool = False,
    converter_factory: Callable[[], _MarkItDownConverter] | None = None,
) -> SourceAdapterResult:
    source_path = _validate_adapter_source_path(
        path,
        approved_roots,
        allow_external_source=allow_external_source,
    )
    converter = _load_markitdown_converter(converter_factory)
    try:
        converted = converter.convert_local(str(source_path))
    except AttributeError:
        converted = converter.convert(str(source_path))
    raw_markdown = _extract_markdown(converted)
    adapter_metadata = _adapter_metadata(
        "markitdown",
        metadata,
        source_kind="local_file",
        original_file_path=str(source_path),
    )
    document = RawSourceDocument.from_manual_markdown(
        raw_markdown,
        title=title or source_path.stem,
        origin_url=origin_url,
        captured_at=captured_at,
        metadata=adapter_metadata,
    )
    return SourceAdapterResult(
        document=document,
        adapter="markitdown",
        source_kind="local_file",
        metadata=adapter_metadata,
    )


def convert_url_with_crawl4ai(
    url: str,
    *,
    title: str = "",
    captured_at: str = "",
    metadata: dict[str, Any] | None = None,
    crawler_factory: Callable[[], _Crawl4AICrawler] | None = None,
    crawl_kwargs: dict[str, Any] | None = None,
    allow_private_network: bool = False,
    allowed_domains: list[str] | None = None,
) -> SourceAdapterResult:
    validated_url = _validate_adapter_source_url(
        url,
        allow_private_network=allow_private_network,
        allowed_domains=allowed_domains,
    )
    crawler = _load_crawl4ai_crawler(crawler_factory)
    kwargs = dict(crawl_kwargs or {})
    result = _crawl_url(crawler, validated_url, kwargs)
    result = _resolve_maybe_awaitable(result)
    raw_markdown = _extract_markdown(result)
    page_title = title or _extract_title(result) or validated_url
    adapter_metadata = _adapter_metadata("crawl4ai", metadata, source_kind="url")
    document = RawSourceDocument.from_manual_markdown(
        raw_markdown,
        title=page_title,
        origin_url=validated_url,
        captured_at=captured_at,
        metadata=adapter_metadata,
    )
    return SourceAdapterResult(
        document=document,
        adapter="crawl4ai",
        source_kind="url",
        metadata=adapter_metadata,
    )


def _load_markitdown_converter(
    converter_factory: Callable[[], _MarkItDownConverter] | None,
) -> _MarkItDownConverter:
    if converter_factory is not None:
        return converter_factory()
    try:
        module = importlib.import_module("markitdown")
    except ModuleNotFoundError as exc:
        raise AdapterUnavailableError("MarkItDown is not installed") from exc
    try:
        converter_cls = getattr(module, "MarkItDown")
    except AttributeError as exc:
        raise AdapterUnavailableError("MarkItDown module does not expose MarkItDown") from exc
    return converter_cls()


def _load_crawl4ai_crawler(
    crawler_factory: Callable[[], _Crawl4AICrawler] | None,
) -> _Crawl4AICrawler:
    if crawler_factory is not None:
        return crawler_factory()
    try:
        module = importlib.import_module("crawl4ai")
    except ModuleNotFoundError as exc:
        raise AdapterUnavailableError("Crawl4AI is not installed") from exc
    try:
        crawler_cls = getattr(module, "AsyncWebCrawler")
    except AttributeError as exc:
        raise AdapterUnavailableError("Crawl4AI module does not expose AsyncWebCrawler") from exc
    return crawler_cls()


def _extract_markdown(value: Any) -> str:
    if value is None:
        return ""
    text = getattr(value, "text_content", None)
    if text is not None:
        return str(text).strip()
    markdown = getattr(value, "markdown", None)
    if markdown is not None:
        return str(markdown).strip()
    return str(value).strip()


def _crawl_url(crawler: _Crawl4AICrawler, url: str, kwargs: dict[str, Any]) -> Any:
    if hasattr(crawler, "__aenter__") and hasattr(crawler, "__aexit__"):
        return _crawl_url_with_async_context(crawler, url, kwargs)
    try:
        return crawler.arun(url=url, **kwargs)
    except TypeError:
        return crawler.arun(url, **kwargs)


async def _crawl_url_with_async_context(
    crawler: _Crawl4AICrawler,
    url: str,
    kwargs: dict[str, Any],
) -> Any:
    async with crawler as active_crawler:  # type: ignore[attr-defined]
        try:
            return await active_crawler.arun(url=url, **kwargs)
        except TypeError:
            return await active_crawler.arun(url, **kwargs)


def _resolve_maybe_awaitable(value: Any) -> Any:
    if not inspect.isawaitable(value):
        return value
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(value)
    close = getattr(value, "close", None)
    if callable(close):
        close()
    raise AdapterConversionError(
        "Crawl4AI returned an awaitable while an event loop is already running"
    )


def _extract_title(value: Any) -> str:
    if value is None:
        return ""
    metadata = getattr(value, "metadata", None)
    if isinstance(metadata, dict):
        title = metadata.get("title") or metadata.get("og:title")
        if title:
            return str(title).strip()
    title = getattr(value, "title", None)
    return "" if title is None else str(title).strip()


def _adapter_metadata(
    adapter: str,
    metadata: dict[str, Any] | None,
    *,
    source_kind: str,
    original_file_path: str = "",
) -> dict[str, Any]:
    merged = dict(metadata or {})
    merged.update({"adapter": adapter, "source_kind": source_kind})
    if original_file_path:
        merged["original_file_path"] = original_file_path
    return merged


def _validate_adapter_source_path(
    path: str | Path,
    approved_roots: list[str | Path] | None,
    *,
    allow_external_source: bool,
) -> Path:
    source_path = Path(path).resolve(strict=False)
    roots = [Path.cwd()] if approved_roots is None else [Path(root) for root in approved_roots]
    resolved_roots = [root.resolve(strict=False) for root in roots]

    if not allow_external_source and any(
        part.casefold() == "external" for part in source_path.parts
    ):
        raise ValueError("Source file path is inside external/ and cannot be used for intake")
    if not resolved_roots or not any(_is_within(source_path, root) for root in resolved_roots):
        raise ValueError("Source file path is outside approved roots")
    return source_path


def _validate_adapter_source_url(
    url: str,
    *,
    allow_private_network: bool,
    allowed_domains: list[str] | None,
) -> str:
    parsed = urlparse(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Source URL must use http or https")
    if not parsed.hostname:
        raise ValueError("Source URL must include a host")

    host = _normalize_url_host(parsed.hostname)
    if allowed_domains is not None:
        domains = [_normalize_url_host(domain) for domain in allowed_domains]
        if not domains or not any(_host_matches_domain(host, domain) for domain in domains):
            raise ValueError("Source URL host is outside allowed domains")

    if not allow_private_network and _is_private_network_host(host):
        raise ValueError("Source URL host is private and requires explicit opt-in")
    return url


def _normalize_url_host(host: str) -> str:
    normalized = host.strip().rstrip(".").casefold()
    try:
        return normalized.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("Source URL host is invalid") from exc


def _host_matches_domain(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")


def _is_private_network_host(host: str) -> bool:
    if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address.is_private or address.is_loopback or address.is_link_local


def _is_within(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath(
            [os.path.normcase(str(path)), os.path.normcase(str(root))]
        ) == os.path.normcase(str(root))
    except ValueError:
        return False


__all__ = [
    "AdapterConversionError",
    "AdapterUnavailableError",
    "SourceAdapterResult",
    "convert_local_file_with_markitdown",
    "convert_url_with_crawl4ai",
    "crawl4ai_available",
    "markitdown_available",
]
