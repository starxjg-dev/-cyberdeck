import json
import socket
import urllib.error

import pytest

from cyberdeck.models import ErrorCategory
from cyberdeck.providers.base import ModelResponse, ProviderError
from cyberdeck.providers.ollama import OllamaProvider


class Response:
    def __init__(self, payload=None):
        self.payload = payload or {
            "response": '{"final_answer":"done"}',
            "eval_count": 8,
            "prompt_eval_count": 4,
            "done": True,
        }

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return json.dumps(self.payload).encode()


def test_ollama_normalizes_text_usage_and_latency():
    ticks = iter([10.0, 10.012])
    provider = OllamaProvider(
        opener=lambda *_args, **_kwargs: Response(),
        clock=lambda: next(ticks),
    )

    response = provider.generate("prompt", temperature=0.2, max_tokens=64)

    assert isinstance(response, ModelResponse)
    assert response.text.endswith('"done"}')
    assert response.usage == {"input_tokens": 4, "output_tokens": 8}
    assert response.duration_ms == 12


def test_ollama_request_contains_endpoint_and_runtime_options():
    captured = {}

    def opener(request, **kwargs):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = kwargs["timeout"]
        captured.update(json.loads(request.data))
        return Response()

    OllamaProvider(
        model="qwen2.5:7b",
        base_url="http://127.0.0.1:11434/",
        timeout=42,
        opener=opener,
    ).generate("hello", temperature=0.4, max_tokens=32)

    assert captured["url"] == "http://127.0.0.1:11434/api/generate"
    assert captured["model"] == "qwen2.5:7b"
    assert captured["prompt"] == "hello"
    assert captured["stream"] is False
    assert captured["options"] == {"temperature": 0.4, "num_predict": 32}
    assert captured["timeout"] == 42
    assert captured["headers"]["Content-type"] == "application/json"


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"eval_count": 1}, "response.*text"),
        ({"response": "", "eval_count": 1}, "response.*text"),
        ({"response": "ok", "eval_count": -1}, "eval_count"),
    ],
)
def test_ollama_rejects_malformed_payloads(payload, message):
    provider = OllamaProvider(opener=lambda *_args, **_kwargs: Response(payload))

    with pytest.raises(ProviderError, match=message):
        provider.generate("prompt", temperature=0.2, max_tokens=64)


def test_ollama_rejects_invalid_json():
    class InvalidResponse(Response):
        def read(self):
            return b"not json"

    provider = OllamaProvider(opener=lambda *_args, **_kwargs: InvalidResponse())

    with pytest.raises(ProviderError, match="invalid JSON") as captured:
        provider.generate("prompt", temperature=0.2, max_tokens=64)

    assert captured.value.category is ErrorCategory.PROVIDER
    assert captured.value.code == "invalid_response"


def test_ollama_timeout_has_stable_category_and_code_without_secret():
    def opener(*_args, **_kwargs):
        raise TimeoutError("token=timeout-secret")

    provider = OllamaProvider(opener=opener)

    with pytest.raises(ProviderError) as captured:
        provider.generate("prompt", temperature=0.2, max_tokens=64)

    assert captured.value.category is ErrorCategory.TIMEOUT
    assert captured.value.code == "timeout"
    assert captured.value.retryable is True
    assert "timeout-secret" not in str(captured.value)


def test_ollama_http_error_has_stable_provider_category_status_and_retryability():
    def opener(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "http://127.0.0.1:11434/api/generate",
            503,
            "token=http-secret",
            None,
            None,
        )

    provider = OllamaProvider(opener=opener)

    with pytest.raises(ProviderError) as captured:
        provider.generate("prompt", temperature=0.2, max_tokens=64)

    assert captured.value.category is ErrorCategory.PROVIDER
    assert captured.value.code == "http_error"
    assert captured.value.status_code == 503
    assert captured.value.retryable is True
    assert "http-secret" not in str(captured.value)


def test_ollama_url_error_has_stable_provider_category_without_secret():
    def opener(*_args, **_kwargs):
        raise urllib.error.URLError("token=connection-secret")

    provider = OllamaProvider(opener=opener)

    with pytest.raises(ProviderError) as captured:
        provider.generate("prompt", temperature=0.2, max_tokens=64)

    assert captured.value.category is ErrorCategory.PROVIDER
    assert captured.value.code == "connection_error"
    assert captured.value.retryable is True
    assert "connection-secret" not in str(captured.value)


@pytest.mark.parametrize(
    "reason",
    [
        TimeoutError("token=wrapped-timeout-secret"),
        socket.timeout("token=wrapped-socket-secret"),  # noqa: UP041 - explicit regression case
    ],
    ids=["timeout-error", "socket-timeout"],
)
def test_ollama_url_error_wrapping_timeout_preserves_timeout_category(reason):
    def opener(*_args, **_kwargs):
        raise urllib.error.URLError(reason)

    provider = OllamaProvider(opener=opener)

    with pytest.raises(ProviderError) as captured:
        provider.generate("prompt", temperature=0.2, max_tokens=64)

    assert captured.value.category is ErrorCategory.TIMEOUT
    assert captured.value.code == "timeout"
    assert captured.value.retryable is True
    assert "wrapped-timeout-secret" not in str(captured.value)
    assert "wrapped-socket-secret" not in str(captured.value)


def test_ollama_transport_error_does_not_leak_exception_secret():
    def opener(*_args, **_kwargs):
        raise RuntimeError("token=do-not-leak")

    provider = OllamaProvider(opener=opener)

    with pytest.raises(ProviderError) as captured:
        provider.generate("prompt", temperature=0.2, max_tokens=64)

    assert "do-not-leak" not in str(captured.value)
    assert "Ollama" in str(captured.value)
    assert captured.value.category is ErrorCategory.PROVIDER
    assert captured.value.code == "transport_error"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"prompt": "", "temperature": 0.2, "max_tokens": 64}, "prompt"),
        ({"prompt": "ok", "temperature": -0.1, "max_tokens": 64}, "temperature"),
        ({"prompt": "ok", "temperature": 0.2, "max_tokens": 0}, "max_tokens"),
    ],
)
def test_ollama_validates_generation_inputs_before_transport(kwargs, message):
    calls = []
    provider = OllamaProvider(opener=lambda *_args, **_kwargs: calls.append(True))

    with pytest.raises(ValueError, match=message):
        provider.generate(**kwargs)

    assert calls == []
