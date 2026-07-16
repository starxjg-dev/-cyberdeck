"""Bounded ``shell=False`` process execution."""

from __future__ import annotations

import os
import subprocess
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from cyberdeck.models import ErrorCategory, ToolRequest, ToolResult


class ProcessHandler:
    def __init__(
        self,
        workspace: str | os.PathLike[str],
        *,
        runner: Callable[..., Any] | None = None,
        timeout: float = 30.0,
        max_output_bytes: int = 64 * 1024,
    ) -> None:
        if timeout <= 0 or max_output_bytes <= 0:
            raise ValueError("process limits must be positive")
        self.workspace = Path(workspace).expanduser().resolve(strict=False)
        self.runner = subprocess.run if runner is None else runner
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
        try:
            completed = self.runner(
                list(argv),
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
        success = return_code == 0
        if not output and not success:
            output = bounded_stderr
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
                "stderr": bounded_stderr,
                "truncated": stdout_truncated or stderr_truncated,
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
