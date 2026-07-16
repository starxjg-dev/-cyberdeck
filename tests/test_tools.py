import socket
import subprocess
import urllib.request

import pytest

from cyberdeck.models import ErrorCategory, ToolRequest, ToolResult
from cyberdeck.policy import PolicyEngine
from cyberdeck.tools import ToolRegistry, build_default_registry
from cyberdeck.tools.http import SafeRedirectHandler, UnsafeUrlError, is_public_host


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


def test_approval_cannot_replace_process_arguments_after_policy_allows_request(tmp_path):
    executed = []
    original_arguments = {
        "argv": ["git", "add", "."],
        "context": {"paths": ["safe.txt"]},
    }
    request = ToolRequest("1", "process.run", original_arguments)

    def runner(argv, **_kwargs):
        executed.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout="ok", stderr="")

    def approval(approval_request, _decision):
        approval_request.arguments["argv"][:] = [
            "powershell",
            "Remove-Item",
            "-Recurse",
            ".",
        ]
        approval_request.arguments["context"]["paths"][0] = "../outside.txt"
        return True

    result = build_default_registry(tmp_path, runner=runner).execute(
        request,
        PolicyEngine(tmp_path),
        approval=approval,
    )

    assert result.success
    assert executed == [["git", "add", "."]]
    assert request.arguments["argv"] == ["git", "add", "."]
    assert request.arguments["context"]["paths"] == ["safe.txt"]


def test_approval_receives_independent_copy_of_nested_arguments(tmp_path):
    observed = {}
    original_arguments = {
        "path": "safe.txt",
        "content": {"sections": [{"text": "original"}]},
    }
    request = ToolRequest("1", "file.write", original_arguments)
    registry = ToolRegistry()

    def handler(execution_request):
        observed["path"] = execution_request.arguments["path"]
        observed["text"] = execution_request.arguments["content"]["sections"][0]["text"]
        return ToolResult("1", "file.write", True, output="written")

    def approval(approval_request, _decision):
        approval_request.arguments["path"] = "../outside.txt"
        approval_request.arguments["content"]["sections"][0]["text"] = "mutated"
        return True

    registry.register("file.write", handler)
    result = registry.execute(request, PolicyEngine(tmp_path), approval=approval)

    assert result.success
    assert observed == {"path": "safe.txt", "text": "original"}
    assert request.arguments["path"] == "safe.txt"
    assert request.arguments["content"]["sections"][0]["text"] == "original"


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


def test_process_safely_truncates_multibyte_stdout_and_stderr(tmp_path):
    def runner(argv, **_kwargs):
        return subprocess.CompletedProcess(
            argv,
            0,
            stdout="界" * 10,
            stderr="🙂" * 10,
        )

    registry = build_default_registry(
        tmp_path,
        runner=runner,
        max_process_output_bytes=5,
    )
    result = registry.execute(
        ToolRequest("1", "process.run", {"argv": ["git", "status"]}),
        PolicyEngine(tmp_path),
    )

    assert result.success
    assert len(result.output.encode("utf-8")) <= 5
    assert len(result.metadata["stderr"].encode("utf-8")) <= 5
    assert result.metadata["truncated"] is True


class ChunkStream:
    def __init__(self, chunks):
        self._chunks = iter(chunks)
        self.read_sizes = []

    def read(self, size=-1):
        self.read_sizes.append(size)
        return next(self._chunks, b"")


class FakePopenProcess:
    def __init__(self, stdout_chunks=(), stderr_chunks=(), return_code=0):
        self.stdout = ChunkStream(stdout_chunks)
        self.stderr = ChunkStream(stderr_chunks)
        self.return_code = return_code
        self.returncode = None
        self.killed = False
        self.wait_calls = []
        self.communicate_called = False

    def wait(self, timeout=None):
        self.wait_calls.append(timeout)
        self.returncode = self.return_code
        return self.return_code

    def kill(self):
        self.killed = True

    def communicate(self, *_args, **_kwargs):
        self.communicate_called = True
        raise AssertionError("bounded streaming must not call communicate")


def test_default_process_path_streams_and_bounds_stdout_stderr_without_communicate(tmp_path):
    process = FakePopenProcess(
        stdout_chunks=[b"\xe7\x95", b"\x8c\xe7\x95\x8c", b"discarded"],
        stderr_chunks=[b"\xf0\x9f", b"\x99\x82\xf0\x9f\x99\x82", b"discarded"],
    )
    captured = {}

    def popen_factory(argv, **kwargs):
        captured["argv"] = argv
        captured.update(kwargs)
        return process

    registry = build_default_registry(
        tmp_path,
        popen_factory=popen_factory,
        max_process_output_bytes=5,
    )
    result = registry.execute(
        ToolRequest("1", "process.run", {"argv": ["git", "status"]}),
        PolicyEngine(tmp_path),
    )

    assert result.success
    assert result.output == "界"
    assert result.metadata["stderr"] == "🙂"
    assert result.metadata["truncated"] is True
    assert process.stdout.read_sizes[-1] > 0
    assert process.stderr.read_sizes[-1] > 0
    assert process.communicate_called is False
    assert captured["argv"] == ["git", "status"]
    assert captured["shell"] is False
    assert captured["cwd"] == tmp_path.resolve()
    assert captured["stdout"] is subprocess.PIPE
    assert captured["stderr"] is subprocess.PIPE


def test_default_process_path_kills_and_reaps_on_timeout(tmp_path):
    class TimeoutProcess(FakePopenProcess):
        def wait(self, timeout=None):
            self.wait_calls.append(timeout)
            if not self.killed:
                raise subprocess.TimeoutExpired(["git", "status"], timeout)
            self.returncode = -9
            return self.returncode

    process = TimeoutProcess(stdout_chunks=[b"partial"], stderr_chunks=[b"warning"])
    registry = build_default_registry(
        tmp_path,
        popen_factory=lambda *_args, **_kwargs: process,
    )

    result = registry.execute(
        ToolRequest(
            "1",
            "process.run",
            {"argv": ["git", "status"], "timeout": 0.01},
        ),
        PolicyEngine(tmp_path),
    )

    assert not result.success
    assert result.error_category is ErrorCategory.TIMEOUT
    assert process.killed is True
    assert len(process.wait_calls) == 2
    assert process.communicate_called is False
    assert process.stdout.read_sizes
    assert process.stderr.read_sizes


def test_default_process_path_normalizes_stream_errors_and_reaps_process(tmp_path):
    class ErrorStream:
        def read(self, _size=-1):
            raise OSError("token=stream-secret")

    process = FakePopenProcess(stderr_chunks=[b"warning"])
    process.stdout = ErrorStream()
    registry = build_default_registry(
        tmp_path,
        popen_factory=lambda *_args, **_kwargs: process,
    )

    result = registry.execute(
        ToolRequest("1", "process.run", {"argv": ["git", "status"]}),
        PolicyEngine(tmp_path),
    )

    assert not result.success
    assert result.error_category is ErrorCategory.TOOL
    assert "stream-secret" not in result.error_message
    assert process.wait_calls
    assert process.communicate_called is False


def test_private_addresses_are_rejected():
    def resolver(*_args, **_kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]

    assert not is_public_host("example.test", resolver=resolver)


def test_mixed_public_and_private_dns_answers_are_rejected():
    def resolver(*_args, **_kwargs):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.7", 443)),
        ]

    assert not is_public_host("mixed.example.test", resolver=resolver)


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


def test_redirect_handler_validates_each_hop_before_following():
    resolved_hosts = []

    def resolver(host, *_args, **_kwargs):
        resolved_hosts.append(host)
        address = "127.0.0.1" if host == "private-hop.example.test" else "93.184.216.34"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))]

    handler = SafeRedirectHandler(resolver)
    initial = urllib.request.Request("https://origin.example.test/start")
    first_hop = handler.redirect_request(
        initial,
        None,
        302,
        "Found",
        {},
        "https://public-hop.example.test/one",
    )

    with pytest.raises(UnsafeUrlError):
        handler.redirect_request(
            first_hop,
            None,
            302,
            "Found",
            {},
            "https://private-hop.example.test/two",
        )

    assert first_hop.full_url == "https://public-hop.example.test/one"
    assert resolved_hosts == ["public-hop.example.test", "private-hop.example.test"]


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
