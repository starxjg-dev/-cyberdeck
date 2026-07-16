"""Bounded, workspace-confined filesystem read and search handlers."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from cyberdeck.models import ErrorCategory, ToolRequest, ToolResult
from cyberdeck.policy import PolicyEngine

_IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "vendor",
}


class FileSystemHandlers:
    def __init__(
        self,
        workspace: str | os.PathLike[str],
        *,
        max_bytes: int = 64 * 1024,
        max_lines: int = 2_000,
        max_results: int = 100,
    ) -> None:
        if max_bytes <= 0 or max_lines <= 0 or max_results <= 0:
            raise ValueError("filesystem limits must be positive")
        self.policy = PolicyEngine(workspace)
        self.workspace = self.policy.workspace
        self.max_bytes = max_bytes
        self.max_lines = max_lines
        self.max_results = max_results

    def read(self, request: ToolRequest) -> ToolResult:
        started = time.perf_counter()
        try:
            path = self.policy.resolve_path(request.arguments.get("path"))
            max_lines = self._bounded_integer(
                request.arguments.get("max_lines", self.max_lines),
                maximum=self.max_lines,
                name="max_lines",
            )
            max_bytes = self._bounded_integer(
                request.arguments.get("max_bytes", self.max_bytes),
                maximum=self.max_bytes,
                name="max_bytes",
            )
            if not path.is_file():
                return self._error(request, "file does not exist", started)
            with path.open("rb") as handle:
                raw = handle.read(max_bytes + 1)
            byte_truncated = len(raw) > max_bytes
            text = raw[:max_bytes].decode("utf-8", errors="replace")
            lines = text.splitlines()
            line_truncated = len(lines) > max_lines
            rendered = "\n".join(lines[:max_lines])
            output = self._truncate_utf8(rendered, max_bytes)
            output_truncated = output != rendered
            return ToolResult(
                request_id=request.request_id,
                tool_name=request.name,
                success=True,
                output=output,
                duration_ms=self._elapsed(started),
                metadata={
                    "path": self._relative(path),
                    "truncated": byte_truncated or line_truncated or output_truncated,
                },
            )
        except ValueError as exc:
            return self._error(request, str(exc), started, ErrorCategory.VALIDATION)
        except OSError:
            return self._error(request, "file read failed", started)

    def search(self, request: ToolRequest) -> ToolResult:
        started = time.perf_counter()
        try:
            query = request.arguments.get("query")
            if not isinstance(query, str) or not query:
                raise ValueError("file search requires a non-empty query")
            base = self.policy.resolve_path(request.arguments.get("path", "."))
            max_results = self._bounded_integer(
                request.arguments.get("max_results", self.max_results),
                maximum=self.max_results,
                name="max_results",
            )
            if not base.exists():
                return self._error(request, "search path does not exist", started)
            matches, truncated = self._search(base, query, max_results)
            return ToolResult(
                request_id=request.request_id,
                tool_name=request.name,
                success=True,
                output="\n".join(matches),
                duration_ms=self._elapsed(started),
                metadata={"matches": len(matches), "truncated": truncated},
            )
        except ValueError as exc:
            return self._error(request, str(exc), started, ErrorCategory.VALIDATION)
        except OSError:
            return self._error(request, "file search failed", started)

    def _search(self, base: Path, query: str, max_results: int) -> tuple[list[str], bool]:
        matches: list[str] = []
        output_bytes = 0
        for path in self._iter_files(base):
            try:
                confined = self.policy.resolve_path(path)
                if confined.stat().st_size > self.max_bytes:
                    continue
                content = confined.read_bytes()
            except (OSError, ValueError):
                continue
            if b"\x00" in content:
                continue
            for line_number, line in enumerate(
                content.decode("utf-8", errors="replace").splitlines(),
                start=1,
            ):
                if query not in line:
                    continue
                if len(matches) >= max_results:
                    return matches, True
                rendered = f"{self._relative(confined)}:{line_number}:{line}"
                separator_bytes = 1 if matches else 0
                remaining = self.max_bytes - output_bytes - separator_bytes
                if remaining <= 0:
                    return matches, True
                bounded = self._truncate_utf8(rendered, remaining)
                matches.append(bounded)
                rendered_bytes = len(rendered.encode("utf-8"))
                output_bytes += separator_bytes + len(bounded.encode("utf-8"))
                if rendered_bytes > remaining:
                    return matches, True
        return matches, False

    @staticmethod
    def _iter_files(base: Path):
        if base.is_file():
            yield base
            return
        for root, directories, filenames in os.walk(base, followlinks=False):
            directories[:] = sorted(
                directory
                for directory in directories
                if directory not in _IGNORED_DIRECTORIES and not directory.startswith(".")
            )
            for filename in sorted(filenames):
                if not filename.startswith("."):
                    yield Path(root) / filename

    def _relative(self, path: Path) -> str:
        return path.relative_to(self.workspace).as_posix()

    @staticmethod
    def _bounded_integer(value: Any, *, maximum: int, name: str) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
        return min(value, maximum)

    @staticmethod
    def _truncate_utf8(value: str, limit: int) -> str:
        encoded = value.encode("utf-8")
        if len(encoded) <= limit:
            return value
        return encoded[:limit].decode("utf-8", errors="ignore")

    @staticmethod
    def _elapsed(started: float) -> int:
        return max(0, int((time.perf_counter() - started) * 1000))

    @classmethod
    def _error(
        cls,
        request: ToolRequest,
        message: str,
        started: float,
        category: ErrorCategory = ErrorCategory.TOOL,
    ) -> ToolResult:
        return ToolResult(
            request_id=request.request_id,
            tool_name=request.name,
            success=False,
            error_category=category,
            error_message=message,
            duration_ms=cls._elapsed(started),
        )


__all__ = ["FileSystemHandlers"]
