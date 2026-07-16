"""Bounded ``shell=False`` process execution."""

from __future__ import annotations

import os
import subprocess
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from cyberdeck.models import ErrorCategory, ToolRequest, ToolResult


class _BoundedStreamCapture:
    _CHUNK_SIZE = 8 * 1024

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.buffer = bytearray()
        self.truncated = False
        self.failed = False

    def drain(self, stream: Any) -> None:
        try:
            while True:
                chunk = stream.read(self._CHUNK_SIZE)
                if not chunk:
                    return
                if isinstance(chunk, str):
                    encoded = chunk.encode("utf-8")
                elif isinstance(chunk, (bytes, bytearray, memoryview)):
                    encoded = bytes(chunk)
                else:
                    raise TypeError("process stream returned a non-byte chunk")
                remaining = self.limit - len(self.buffer)
                if remaining > 0:
                    self.buffer.extend(encoded[:remaining])
                if len(encoded) > remaining:
                    self.truncated = True
        except Exception:
            self.failed = True

    def text(self) -> str:
        return bytes(self.buffer).decode("utf-8", errors="ignore").rstrip("\r\n")


class ProcessHandler:
    def __init__(
        self,
        workspace: str | os.PathLike[str],
        *,
        runner: Callable[..., Any] | None = None,
        popen_factory: Callable[..., Any] | None = None,
        timeout: float = 30.0,
        max_output_bytes: int = 64 * 1024,
    ) -> None:
        if timeout <= 0 or max_output_bytes <= 0:
            raise ValueError("process limits must be positive")
        if runner is not None and popen_factory is not None:
            raise ValueError("runner and popen_factory cannot both be configured")
        self.workspace = Path(workspace).expanduser().resolve(strict=False)
        self.runner = runner
        self.popen_factory = subprocess.Popen if popen_factory is None else popen_factory
        self.timeout = timeout
        self.max_output_bytes = max_output_bytes

    def __call__(self, request: ToolRequest) -> ToolResult:
        started = time.perf_counter()
        argv = request.arguments.get("argv")
        timeout = request.arguments.get("timeout", self.timeout)
        if not isinstance(argv, (list, tuple)):
            return self._error(
                request,
                ErrorCategory.VALIDATION,
                "argv must be a sequence",
                started,
            )
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
            return self._error(
                request,
                ErrorCategory.VALIDATION,
                "timeout must be a positive number",
                started,
            )
        timeout = min(float(timeout), self.timeout)
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_PAGER": "cat",
                "GIT_TERMINAL_PROMPT": "0",
                "NO_COLOR": "1",
                "PAGER": "cat",
            }
        )
        if self.runner is not None:
            return self._run_compatibility(
                request,
                list(argv),
                timeout,
                environment,
                started,
            )
        return self._run_streaming(
            request,
            list(argv),
            timeout,
            environment,
            started,
        )

    def _run_compatibility(
        self,
        request: ToolRequest,
        argv: list[str],
        timeout: float,
        environment: dict[str, str],
        started: float,
    ) -> ToolResult:
        try:
            completed = self.runner(
                argv,
                shell=False,
                cwd=self.workspace,
                timeout=timeout,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=environment,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return self._error(request, ErrorCategory.TIMEOUT, "process timed out", started)
        except (OSError, ValueError):
            return self._error(request, ErrorCategory.TOOL, "process execution failed", started)
        except Exception:
            return self._error(request, ErrorCategory.TOOL, "process runner failed", started)

        stdout = completed.stdout if isinstance(completed.stdout, str) else ""
        stderr = completed.stderr if isinstance(completed.stderr, str) else ""
        output, stdout_truncated = self._truncate(stdout.rstrip("\r\n"))
        bounded_stderr, stderr_truncated = self._truncate(stderr.rstrip("\r\n"))
        return_code = completed.returncode if isinstance(completed.returncode, int) else -1
        return self._result(
            request,
            return_code,
            output,
            bounded_stderr,
            stdout_truncated or stderr_truncated,
            started,
        )

    def _run_streaming(
        self,
        request: ToolRequest,
        argv: list[str],
        timeout: float,
        environment: dict[str, str],
        started: float,
    ) -> ToolResult:
        try:
            process = self.popen_factory(
                argv,
                shell=False,
                cwd=self.workspace,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                bufsize=0,
                env=environment,
            )
        except (OSError, ValueError):
            return self._error(request, ErrorCategory.TOOL, "process execution failed", started)
        except Exception:
            return self._error(request, ErrorCategory.TOOL, "process launcher failed", started)

        stdout = getattr(process, "stdout", None)
        stderr = getattr(process, "stderr", None)
        if stdout is None or stderr is None:
            self._kill_and_reap(process)
            return self._error(
                request,
                ErrorCategory.TOOL,
                "process pipes were unavailable",
                started,
            )

        stdout_capture = _BoundedStreamCapture(self.max_output_bytes)
        stderr_capture = _BoundedStreamCapture(self.max_output_bytes)
        readers = [
            threading.Thread(
                target=stdout_capture.drain,
                args=(stdout,),
                name="cyberdeck-stdout-drain",
                daemon=True,
            ),
            threading.Thread(
                target=stderr_capture.drain,
                args=(stderr,),
                name="cyberdeck-stderr-drain",
                daemon=True,
            ),
        ]
        started_readers: list[threading.Thread] = []
        try:
            for reader in readers:
                reader.start()
                started_readers.append(reader)
        except Exception:
            self._kill_and_reap(process)
            for reader in started_readers:
                reader.join()
            return self._error(
                request,
                ErrorCategory.TOOL,
                "process stream reader failed to start",
                started,
            )

        timed_out = False
        wait_failed = False
        return_code = -1
        try:
            waited = process.wait(timeout=timeout)
            if isinstance(waited, int):
                return_code = waited
        except subprocess.TimeoutExpired:
            timed_out = True
            self._kill_and_reap(process)
            if isinstance(getattr(process, "returncode", None), int):
                return_code = process.returncode
        except Exception:
            wait_failed = True
            self._kill_and_reap(process)
        finally:
            for reader in readers:
                reader.join()

        if timed_out:
            return self._error(request, ErrorCategory.TIMEOUT, "process timed out", started)
        if wait_failed:
            return self._error(request, ErrorCategory.TOOL, "process wait failed", started)
        if stdout_capture.failed or stderr_capture.failed:
            return self._error(
                request,
                ErrorCategory.TOOL,
                "process output read failed",
                started,
            )
        return self._result(
            request,
            return_code,
            stdout_capture.text(),
            stderr_capture.text(),
            stdout_capture.truncated or stderr_capture.truncated,
            started,
        )

    @staticmethod
    def _kill_and_reap(process: Any) -> None:
        try:
            process.kill()
        except Exception:
            pass
        try:
            process.wait()
        except Exception:
            pass

    def _result(
        self,
        request: ToolRequest,
        return_code: int,
        output: str,
        stderr: str,
        truncated: bool,
        started: float,
    ) -> ToolResult:
        success = return_code == 0
        if not output and not success:
            output = stderr
        return ToolResult(
            request_id=request.request_id,
            tool_name=request.name,
            success=success,
            output=output,
            error_category=None if success else ErrorCategory.TOOL,
            error_message="" if success else f"process exited with code {return_code}",
            duration_ms=self._elapsed(started),
            metadata={
                "return_code": return_code,
                "stderr": stderr,
                "truncated": truncated,
            },
        )

    def _truncate(self, value: str) -> tuple[str, bool]:
        encoded = value.encode("utf-8")
        if len(encoded) <= self.max_output_bytes:
            return value, False
        return encoded[: self.max_output_bytes].decode("utf-8", errors="ignore"), True

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


__all__ = ["ProcessHandler"]
