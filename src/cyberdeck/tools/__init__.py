"""Policy-gated tools exposed to Cyberdeck agents."""

from __future__ import annotations

import socket
from collections.abc import Callable
from os import PathLike
from typing import Any

from cyberdeck.tools.filesystem import FileSystemHandlers
from cyberdeck.tools.http import HttpGetHandler
from cyberdeck.tools.process import ProcessHandler
from cyberdeck.tools.registry import ToolRegistry


def build_default_registry(
    workspace: str | PathLike[str],
    *,
    runner: Callable[..., Any] | None = None,
    opener: Callable[..., Any] | Any | None = None,
    resolver: Callable[..., Any] = socket.getaddrinfo,
    max_file_bytes: int = 64 * 1024,
    max_process_output_bytes: int = 64 * 1024,
    max_http_bytes: int = 256 * 1024,
) -> ToolRegistry:
    """Build Cyberdeck's default read-only, workspace-confined tool registry."""

    filesystem = FileSystemHandlers(workspace, max_bytes=max_file_bytes)
    registry = ToolRegistry()
    registry.register("file.read", filesystem.read)
    registry.register("file.search", filesystem.search)
    registry.register(
        "process.run",
        ProcessHandler(
            workspace,
            runner=runner,
            max_output_bytes=max_process_output_bytes,
        ),
    )
    registry.register(
        "http.get",
        HttpGetHandler(opener=opener, resolver=resolver, max_bytes=max_http_bytes),
    )
    return registry


__all__ = ["ToolRegistry", "build_default_registry"]
