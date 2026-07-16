"""Conservative secret redaction for trace-safe data."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

REDACTED = "[REDACTED]"

_SENSITIVE_KEY_MARKERS = (
    "token",
    "secret",
    "password",
    "passwd",
    "apikey",
    "authorization",
    "cookie",
)
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[^\s,;]+")
_SK_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")
_HEADER_PATTERN = re.compile(
    r"(?im)\b(authorization|proxy-authorization|cookie|set-cookie)"
    r"\s*([=:])\s*[^\r\n]*"
)
_ASSIGNMENT_PATTERN = re.compile(
    r"(?im)\b(token|secret|password|passwd|api[_-]?key)"
    r"\s*([=:])\s*[^\r\n,;&]*"
)


def _is_sensitive_key(key: object) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", str(key).casefold())
    return any(marker in normalized for marker in _SENSITIVE_KEY_MARKERS)


def _redact_string(value: str) -> str:
    cleaned = _HEADER_PATTERN.sub(
        lambda match: f"{match.group(1)}{match.group(2)}{REDACTED}",
        value,
    )
    cleaned = _BEARER_PATTERN.sub("Bearer " + REDACTED, cleaned)
    cleaned = _SK_PATTERN.sub(REDACTED, cleaned)
    return _ASSIGNMENT_PATTERN.sub(
        lambda match: f"{match.group(1)}{match.group(2)}{REDACTED}",
        cleaned,
    )


def redact(value: Any) -> Any:
    """Return a recursively redacted copy without mutating ``value``."""

    if isinstance(value, Mapping):
        return {
            key: REDACTED if _is_sensitive_key(key) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    if isinstance(value, str):
        return _redact_string(value)
    return value
