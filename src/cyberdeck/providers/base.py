"""Provider-neutral model response and protocol."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from cyberdeck.models import ErrorCategory


@dataclass(frozen=True)
class ModelResponse:
    text: str
    duration_ms: int
    usage: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise ValueError("model response text must be text")
        if (
            not isinstance(self.duration_ms, int)
            or isinstance(self.duration_ms, bool)
            or self.duration_ms < 0
        ):
            raise ValueError("model response duration_ms must be a non-negative integer")
        if not isinstance(self.usage, dict) or any(
            not isinstance(key, str)
            or not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
            for key, value in self.usage.items()
        ):
            raise ValueError("model response usage must contain non-negative integer values")
        if not isinstance(self.metadata, dict):
            raise ValueError("model response metadata must be an object")
        try:
            json.dumps(self.metadata)
        except (TypeError, ValueError) as exc:
            raise ValueError("model response metadata must be JSON serializable") from exc

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "duration_ms": self.duration_ms,
            "usage": dict(self.usage),
            "metadata": dict(self.metadata),
        }


class ModelProvider(Protocol):
    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1_024,
    ) -> ModelResponse: ...


class ProviderError(RuntimeError):
    """A concise provider failure safe to surface to callers."""

    def __init__(
        self,
        message: str,
        *,
        category: ErrorCategory = ErrorCategory.PROVIDER,
        code: str = "provider_error",
        retryable: bool = False,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        if not isinstance(category, ErrorCategory):
            raise ValueError("provider error category must be an ErrorCategory")
        if not isinstance(code, str) or not code.strip():
            raise ValueError("provider error code must be non-empty text")
        self.category = category
        self.code = code
        self.retryable = retryable
        self.status_code = status_code


__all__ = ["ModelProvider", "ModelResponse", "ProviderError"]
