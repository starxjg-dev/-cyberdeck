import socket
import subprocess

from cyberdeck.models import ErrorCategory, ToolRequest
from cyberdeck.policy import PolicyEngine
from cyberdeck.tools import build_default_registry
from cyberdeck.tools.http import is_public_host


def test_file_read_is_bounded(tmp_path):
    (tmp_path / "data.txt").write_text("one\ntwo\nthree\n", encoding="utf-8")
    registry = build_default_registry(tmp_path)

    result = registry.execute(
        ToolRequest("1", "file.read", {"path": "data.txt", "max_lines": 2}),
        PolicyEngine(tmp_path),
    )

    assert result.success
    assert result.output == "one\ntwo"
    assert result.metadata["truncated"] is True


def test_file_search_is_bounded_and_ignores_hidden_directories(tmp_path):
    (tmp_path / "visible.py").write_text("needle\nneedle\n", encoding="utf-8")
    hidden = tmp_path / ".git"
    hidden.mkdir()
    (hidden / "secret.txt").write_text("needle", encoding="utf-8")
    registry = build_default_registry(tmp_path)

    result = registry.execute(
        ToolRequest(
            "1",
            "file.search",
            {"path": ".", "query": "needle", "max_results": 1},
        ),
        PolicyEngine(tmp_path),
    )

    assert result.success
    assert result.output == "visible.py:1:needle"
    assert result.metadata["truncated"] is True
    assert ".git" not in result.output


def test_file_search_enforces_total_output_byte_limit(tmp_path):
    (tmp_path / "long.txt").write_text(
        "needle\nneedle\n",
        encoding="utf-8",
    )
    registry = build_default_registry(tmp_path, max_file_bytes=24)

    result = registry.execute(
        ToolRequest("1", "file.search", {"path": ".", "query": "needle"}),
        PolicyEngine(tmp_path),
    )

    assert result.success
    assert len(result.output.encode("utf-8")) <= 24
    assert result.metadata["truncated"] is True


def test_file_read_enforces_byte_limit_after_utf8_replacement(tmp_path):
    (tmp_path / "invalid.txt").write_bytes(b"\xff" * 10)
    registry = build_default_registry(tmp_path, max_file_bytes=4)

    result = registry.execute(
        ToolRequest("1", "file.read", {"path": "invalid.txt"}),
        PolicyEngine(tmp_path),
    )

    assert result.success
    assert len(result.output.encode("utf-8")) <= 4
    assert result.metadata["truncated"] is True


def test_denied_process_never_calls_handler(tmp_path):
    calls = []

    def runner(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("denied process reached handler")

    registry = build_default_registry(tmp_path, runner=runner)
    result = registry.execute(
        ToolRequest("1", "process.run", {"argv": ["cmd", "/c", "del", "x"]}),
        PolicyEngine(tmp_path),
    )

    assert not result.success
    assert result.error_category is ErrorCategory.POLICY
    assert calls == []


def test_approval_callback_controls_mutating_process(tmp_path):
    calls = []

    def runner(argv, **_kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="staged\n", stderr="")

    registry = build_default_registry(tmp_path, runner=runner)
    request = ToolRequest("1", "process.run", {"argv": ["git", "add", "."]})

    denied = registry.execute(
        request,
        PolicyEngine(tmp_path),
        approval=lambda _request, _decision: False,
    )
    approved = registry.execute(
        request,
        PolicyEngine(tmp_path),
        approval=lambda _request, _decision: True,
    )

    assert denied.error_category is ErrorCategory.APPROVAL
    assert approved.success
    assert calls == [["git", "add", "."]]


def test_process_uses_argv_shell_false_and_workspace_cwd(tmp_path):
    captured = {}

    def runner(argv, **kwargs):
        captured["argv"] = argv
        captured.update(kwargs)
        return subprocess.CompletedProcess(argv, 0, stdout="clean\n", stderr="")

    registry = build_default_registry(tmp_path, runner=runner)
    result = registry.execute(
        ToolRequest("1", "process.run", {"argv": ["git", "status"]}),
        PolicyEngine(tmp_path),
    )

    assert result.success
    assert captured["argv"] == ["git", "status"]
    assert captured["shell"] is False
    assert captured["cwd"] == tmp_path.resolve()
    assert captured["capture_output"] is True
    assert captured["text"] is True


def test_handler_exception_is_returned_as_typed_error_without_secret(tmp_path):
    def runner(*_args, **_kwargs):
        raise RuntimeError("token=do-not-leak")

    registry = build_default_registry(tmp_path, runner=runner)
    result = registry.execute(
        ToolRequest("1", "process.run", {"argv": ["git", "status"]}),
        PolicyEngine(tmp_path),
    )

    assert not result.success
    assert result.error_category is ErrorCategory.TOOL
    assert "do-not-leak" not in result.error_message


def test_private_addresses_are_rejected():
    def resolver(*_args, **_kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]

    assert not is_public_host("example.test", resolver=resolver)


def test_localhost_is_rejected_even_if_a_resolver_claims_it_is_public():
    assert not is_public_host("localhost", resolver=public_resolver)


class Response:
    status = 200
    headers = {"Content-Type": "text/plain; charset=utf-8"}

    def __init__(self, body=b"hello", final_url="https://example.com/final"):
        self.body = body
        self.final_url = final_url

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self, size=-1):
        return self.body if size < 0 else self.body[:size]

    def geturl(self):
        return self.final_url


def public_resolver(*_args, **_kwargs):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]


def test_http_get_validates_and_bounds_public_response(tmp_path):
    captured = {}

    def opener(request, **kwargs):
        captured["url"] = request.full_url
        captured.update(kwargs)
        return Response(body=b"abcdef")

    registry = build_default_registry(
        tmp_path,
        opener=opener,
        resolver=public_resolver,
        max_http_bytes=4,
    )
    result = registry.execute(
        ToolRequest("1", "http.get", {"url": "https://example.com/start"}),
        PolicyEngine(tmp_path),
    )

    assert result.success
    assert result.output == "abcd"
    assert result.metadata["truncated"] is True
    assert captured["url"] == "https://example.com/start"


def test_http_get_rechecks_final_redirect_url(tmp_path):
    registry = build_default_registry(
        tmp_path,
        opener=lambda *_args, **_kwargs: Response(final_url="https://127.0.0.1/secret"),
        resolver=public_resolver,
    )
    result = registry.execute(
        ToolRequest("1", "http.get", {"url": "https://example.com/start"}),
        PolicyEngine(tmp_path),
    )

    assert not result.success
    assert result.error_category is ErrorCategory.POLICY
