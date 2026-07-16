"""HTTPS GET with DNS, address, and redirect checks."""

from __future__ import annotations

import ipaddress
import socket
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any
from urllib.parse import urljoin, urlsplit

from cyberdeck.models import ErrorCategory, ToolRequest, ToolResult

Resolver = Callable[..., Any]


class UnsafeUrlError(ValueError):
    pass


def _hostname_from_https_url(url: str) -> str:
    try:
        parsed = urlsplit(url)
        host = parsed.hostname
        parsed.port
    except ValueError as exc:
        raise UnsafeUrlError("URL is invalid") from exc
    if parsed.scheme.casefold() != "https":
        raise UnsafeUrlError("only HTTPS URLs are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeUrlError("URL credentials are not allowed")
    if not host:
        raise UnsafeUrlError("URL requires a hostname")
    normalized = host.rstrip(".").casefold()
    if (
        normalized == "localhost"
        or normalized.endswith(".localhost")
        or normalized.endswith(".local")
    ):
        raise UnsafeUrlError("local hostnames are not allowed")
    return normalized


def is_public_host(host: str, *, resolver: Resolver = socket.getaddrinfo) -> bool:
    """Return true only when every resolved address is globally routable."""

    normalized = host.rstrip(".").casefold()
    if (
        not normalized
        or normalized == "localhost"
        or normalized.endswith(".localhost")
        or normalized.endswith(".local")
    ):
        return False
    try:
        literal = ipaddress.ip_address(normalized)
    except ValueError:
        try:
            answers = resolver(normalized, 443, type=socket.SOCK_STREAM)
        except (OSError, socket.gaierror):
            return False
        if not answers:
            return False
        addresses = []
        for answer in answers:
            try:
                address_text = answer[4][0].split("%", 1)[0]
                addresses.append(ipaddress.ip_address(address_text))
            except (IndexError, TypeError, ValueError):
                return False
        return bool(addresses) and all(address.is_global for address in addresses)
    return literal.is_global


def _validate_public_url(url: str, resolver: Resolver) -> str:
    host = _hostname_from_https_url(url)
    if not is_public_host(host, resolver=resolver):
        raise UnsafeUrlError("URL resolves to a non-public address")
    return host


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, resolver: Resolver) -> None:
        super().__init__()
        self.resolver = resolver

    def redirect_request(self, request, fp, code, message, headers, new_url):
        target = urljoin(request.full_url, new_url)
        _validate_public_url(target, self.resolver)
        return super().redirect_request(request, fp, code, message, headers, target)


class HttpGetHandler:
    def __init__(
        self,
        *,
        opener: Callable[..., Any] | Any | None = None,
        resolver: Resolver = socket.getaddrinfo,
        timeout: float = 10.0,
        max_bytes: int = 256 * 1024,
    ) -> None:
        if timeout <= 0 or max_bytes <= 0:
            raise ValueError("HTTP limits must be positive")
        self.resolver = resolver
        self.opener = (
            urllib.request.build_opener(_SafeRedirectHandler(resolver))
            if opener is None
            else opener
        )
        self.timeout = timeout
        self.max_bytes = max_bytes

    def __call__(self, request: ToolRequest) -> ToolResult:
        started = time.perf_counter()
        url = request.arguments.get("url")
        timeout = request.arguments.get("timeout", self.timeout)
        if not isinstance(url, str):
            return self._error(request, ErrorCategory.VALIDATION, "URL must be text", started)
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
            return self._error(
                request,
                ErrorCategory.VALIDATION,
                "timeout must be a positive number",
                started,
            )
        try:
            _validate_public_url(url, self.resolver)
            http_request = urllib.request.Request(
                url,
                headers={"Accept": "text/*, application/json", "User-Agent": "Cyberdeck/6"},
                method="GET",
            )
            response_context = self._open(http_request, min(float(timeout), self.timeout))
            with response_context as response:
                final_url = response.geturl() if hasattr(response, "geturl") else url
                _validate_public_url(final_url, self.resolver)
                raw = response.read(self.max_bytes + 1)
                status = getattr(response, "status", 200)
                content_type = response.headers.get("Content-Type", "")
        except UnsafeUrlError as exc:
            return self._error(request, ErrorCategory.POLICY, str(exc), started)
        except (TimeoutError, socket.timeout):
            return self._error(request, ErrorCategory.TIMEOUT, "HTTP request timed out", started)
        except urllib.error.HTTPError as exc:
            return self._error(
                request,
                ErrorCategory.TOOL,
                f"HTTP request failed with status {exc.code}",
                started,
            )
        except (OSError, urllib.error.URLError, ValueError):
            return self._error(request, ErrorCategory.TOOL, "HTTP request failed", started)
        except Exception:
            return self._error(request, ErrorCategory.TOOL, "HTTP handler failed", started)

        if not isinstance(raw, bytes):
            return self._error(request, ErrorCategory.TOOL, "HTTP response was not bytes", started)
        truncated = len(raw) > self.max_bytes
        output = raw[: self.max_bytes].decode("utf-8", errors="replace")
        success = isinstance(status, int) and 200 <= status < 300
        return ToolResult(
            request_id=request.request_id,
            tool_name=request.name,
            success=success,
            output=output,
            error_category=None if success else ErrorCategory.TOOL,
            error_message="" if success else f"HTTP request failed with status {status}",
            duration_ms=self._elapsed(started),
            metadata={
                "status": status,
                "content_type": content_type,
                "final_url": final_url,
                "truncated": truncated,
            },
        )

    def _open(self, request: urllib.request.Request, timeout: float):
        if callable(self.opener):
            return self.opener(request, timeout=timeout)
        return self.opener.open(request, timeout=timeout)

    @staticmethod
    def _elapsed(started: float) -> int:
        return max(0, int((time.perf_counter() - started) * 1000))

    @classmethod
    def _error(
        cls,
        request: ToolRequest,
        category: ErrorCategory,
        message: str,
        started: float,
    ) -> ToolResult:
        return ToolResult(
            request_id=request.request_id,
            tool_name=request.name,
            success=False,
            error_category=category,
            error_message=message,
            duration_ms=cls._elapsed(started),
        )


__all__ = ["HttpGetHandler", "UnsafeUrlError", "is_public_host"]
