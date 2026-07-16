"""Ollama ``/api/generate`` adapter."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from typing import Any
from urllib.parse import urlsplit

from cyberdeck.models import ErrorCategory
from cyberdeck.providers.base import ModelResponse, ProviderError


class OllamaProvider:
    def __init__(
        self,
        *,
        model: str = "qwen2.5:7b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 120.0,
        opener: Callable[..., Any] | Any = urllib.request.urlopen,
        clock: Callable[[], float] = time.perf_counter,
        max_tokens_limit: int = 32_768,
        max_response_bytes: int = 4 * 1024 * 1024,
    ) -> None:
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Ollama model must be non-empty text")
        self._validate_base_url(base_url)
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
            raise ValueError("Ollama timeout must be positive")
        if max_tokens_limit <= 0 or max_response_bytes <= 0:
            raise ValueError("Ollama response limits must be positive")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.opener = opener
        self.clock = clock
        self.max_tokens_limit = max_tokens_limit
        self.max_response_bytes = max_response_bytes

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1_024,
    ) -> ModelResponse:
        self._validate_inputs(prompt, temperature, max_tokens)
        body = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + "/api/generate",
            data=body,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        started = self.clock()
        try:
            response_context = self._open(request)
            with response_context as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise ProviderError(
                f"Ollama returned HTTP status {exc.code}; verify the model is installed",
                code="http_error",
                retryable=500 <= exc.code < 600,
                status_code=exc.code,
            ) from None
        except TimeoutError:
            raise ProviderError(
                "Ollama request timed out; reduce the prompt or increase the timeout",
                category=ErrorCategory.TIMEOUT,
                code="timeout",
                retryable=True,
            ) from None
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise ProviderError(
                    "Ollama request timed out; reduce the prompt or increase the timeout",
                    category=ErrorCategory.TIMEOUT,
                    code="timeout",
                    retryable=True,
                ) from None
            raise ProviderError(
                "Could not reach Ollama; start the service with `ollama serve`",
                code="connection_error",
                retryable=True,
            ) from None
        except OSError:
            raise ProviderError(
                "Could not reach Ollama; start the service with `ollama serve`",
                code="connection_error",
                retryable=True,
            ) from None
        except Exception:
            raise ProviderError(
                "Ollama request failed; verify the local service",
                code="transport_error",
            ) from None
        duration_ms = max(0, int(round((self.clock() - started) * 1000)))
        payload = self._parse_payload(raw)
        return ModelResponse(
            text=payload["response"],
            duration_ms=duration_ms,
            usage=self._usage(payload),
            metadata=self._metadata(payload),
        )

    def _open(self, request: urllib.request.Request):
        if callable(self.opener):
            return self.opener(request, timeout=self.timeout)
        return self.opener.open(request, timeout=self.timeout)

    def _parse_payload(self, raw: Any) -> Mapping[str, Any]:
        if not isinstance(raw, bytes):
            raise ProviderError(
                "Ollama returned a non-byte response",
                code="invalid_response",
            )
        if len(raw) > self.max_response_bytes:
            raise ProviderError(
                "Ollama response exceeded the configured byte limit",
                code="response_too_large",
            )
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ProviderError(
                "Ollama returned invalid JSON",
                code="invalid_response",
            ) from None
        if not isinstance(payload, Mapping):
            raise ProviderError(
                "Ollama returned a JSON value instead of an object",
                code="invalid_response",
            )
        text = payload.get("response")
        if not isinstance(text, str) or not text.strip():
            raise ProviderError(
                "Ollama response did not contain non-empty response text",
                code="invalid_response",
            )
        self._optional_count(payload, "eval_count")
        self._optional_count(payload, "prompt_eval_count")
        return payload

    @staticmethod
    def _optional_count(payload: Mapping[str, Any], key: str) -> int | None:
        value = payload.get(key)
        if value is None:
            return None
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ProviderError(
                f"Ollama returned an invalid {key}",
                code="invalid_response",
            )
        return value

    @classmethod
    def _usage(cls, payload: Mapping[str, Any]) -> dict[str, int]:
        usage = {}
        input_tokens = cls._optional_count(payload, "prompt_eval_count")
        output_tokens = cls._optional_count(payload, "eval_count")
        if input_tokens is not None:
            usage["input_tokens"] = input_tokens
        if output_tokens is not None:
            usage["output_tokens"] = output_tokens
        return usage

    def _metadata(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        metadata: dict[str, Any] = {"model": payload.get("model", self.model)}
        for key in ("done", "done_reason"):
            value = payload.get(key)
            if isinstance(value, (str, bool)):
                metadata[key] = value
        total_duration = payload.get("total_duration")
        if isinstance(total_duration, int) and not isinstance(total_duration, bool):
            metadata["provider_duration_ms"] = max(0, total_duration // 1_000_000)
        return metadata

    def _validate_inputs(self, prompt: Any, temperature: Any, max_tokens: Any) -> None:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be non-empty text")
        if (
            not isinstance(temperature, (int, float))
            or isinstance(temperature, bool)
            or not 0 <= temperature <= 2
        ):
            raise ValueError("temperature must be between 0 and 2")
        if (
            not isinstance(max_tokens, int)
            or isinstance(max_tokens, bool)
            or not 0 < max_tokens <= self.max_tokens_limit
        ):
            raise ValueError(
                f"max_tokens must be between 1 and {self.max_tokens_limit}"
            )

    @staticmethod
    def _validate_base_url(base_url: Any) -> None:
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("Ollama base_url must be non-empty text")
        try:
            parsed = urlsplit(base_url)
            _ = parsed.port
        except ValueError as exc:
            raise ValueError("Ollama base_url is invalid") from exc
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Ollama base_url must use HTTP or HTTPS and include a host")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("Ollama base_url must not contain credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("Ollama base_url must not contain a query or fragment")


__all__ = ["OllamaProvider"]
