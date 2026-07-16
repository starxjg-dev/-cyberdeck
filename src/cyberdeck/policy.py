"""Explicit workspace, process, network, and approval policy decisions."""

from __future__ import annotations

import ipaddress
import os
import re
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from cyberdeck.models import ToolRequest

READ_ONLY_COMMANDS: dict[str, set[str] | None] = {
    "rg": None,
    "git": {"status", "diff", "log", "show", "grep", "branch"},
}
MUTATING_COMMANDS: dict[str, set[str]] = {
    "git": {"add", "commit", "switch", "checkout", "push", "merge", "rebase"},
}

_SHELL_METACHARACTERS = re.compile(r"[|&;<>`\r\n\x00]")
_HOST_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")
_UNSAFE_RG_OPTIONS = {"--pre", "--hostname-bin"}
_UNSAFE_GIT_OPTIONS = {
    "--config-env",
    "--exec-path",
    "--ext-diff",
    "--paginate",
    "--textconv",
    "-c",
    "-p",
}
_MUTATING_BRANCH_OPTIONS = {
    "--copy",
    "--delete",
    "--edit-description",
    "--move",
    "-C",
    "-D",
    "-M",
    "-c",
    "-d",
    "-m",
}


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class PolicyDecision:
    action: PolicyAction
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _decision(action: PolicyAction, reason: str, **metadata: Any) -> PolicyDecision:
    return PolicyDecision(action=action, reason=reason, metadata=metadata)


def _normalize_command_policy(
    policy: Mapping[str, Collection[str] | None],
) -> dict[str, set[str] | None]:
    normalized: dict[str, set[str] | None] = {}
    for command, subcommands in policy.items():
        normalized[command.casefold()] = (
            None if subcommands is None else {item.casefold() for item in subcommands}
        )
    return normalized


class PolicyEngine:
    """Evaluate structured requests before any tool handler is invoked."""

    def __init__(
        self,
        workspace: str | os.PathLike[str],
        *,
        read_only_commands: Mapping[str, Collection[str] | None] | None = None,
        mutating_commands: Mapping[str, Collection[str]] | None = None,
    ) -> None:
        self.workspace = Path(workspace).expanduser().resolve(strict=False)
        if self.workspace.exists() and not self.workspace.is_dir():
            raise ValueError("workspace must be a directory")
        self.read_only_commands = _normalize_command_policy(
            READ_ONLY_COMMANDS if read_only_commands is None else read_only_commands
        )
        self.mutating_commands = _normalize_command_policy(
            MUTATING_COMMANDS if mutating_commands is None else mutating_commands
        )

    def resolve_path(self, raw_path: Any) -> Path:
        """Resolve a path and raise ``ValueError`` if it escapes the workspace."""

        if not isinstance(raw_path, (str, os.PathLike)):
            raise ValueError("path must be text")
        text = os.fspath(raw_path)
        if not text or "\x00" in text:
            raise ValueError("path must be non-empty text")
        candidate = Path(text).expanduser()
        if not candidate.is_absolute():
            candidate = self.workspace / candidate
        resolved = candidate.resolve(strict=False)
        try:
            common = os.path.commonpath((self.workspace, resolved))
        except ValueError as exc:
            raise ValueError("path escapes workspace") from exc
        if os.path.normcase(common) != os.path.normcase(os.fspath(self.workspace)):
            raise ValueError("path escapes workspace")
        return resolved

    def evaluate(self, request: ToolRequest) -> PolicyDecision:
        if not isinstance(request, ToolRequest):
            return _decision(PolicyAction.DENY, "request must be a ToolRequest")
        if request.name in {"file.read", "file.search"}:
            raw_path = request.arguments.get("path", "." if request.name == "file.search" else None)
            try:
                resolved = self.resolve_path(raw_path)
            except (OSError, ValueError):
                return _decision(PolicyAction.DENY, "path escapes workspace")
            return _decision(PolicyAction.ALLOW, "workspace path allowed", path=str(resolved))
        if request.name == "file.write":
            try:
                resolved = self.resolve_path(request.arguments.get("path"))
            except (OSError, ValueError):
                return _decision(PolicyAction.DENY, "path escapes workspace")
            return _decision(
                PolicyAction.REQUIRE_APPROVAL,
                "file mutation requires approval",
                path=str(resolved),
            )
        if request.name == "process.run":
            return self._evaluate_process(request.arguments.get("argv"))
        if request.name == "http.get":
            return self._evaluate_url(request.arguments.get("url"))
        return _decision(PolicyAction.DENY, "unknown tool")

    def _evaluate_process(self, raw_argv: Any) -> PolicyDecision:
        if (
            isinstance(raw_argv, (str, bytes))
            or not isinstance(raw_argv, Sequence)
            or not raw_argv
        ):
            return _decision(PolicyAction.DENY, "process argv must be a non-empty sequence")
        argv = list(raw_argv)
        if any(not isinstance(item, str) or not item for item in argv):
            return _decision(PolicyAction.DENY, "process arguments must be non-empty text")
        if any(_SHELL_METACHARACTERS.search(item) for item in argv):
            return _decision(PolicyAction.DENY, "process arguments contain shell metacharacters")

        executable = argv[0].casefold()
        if "/" in executable or "\\" in executable:
            return _decision(PolicyAction.DENY, "executable paths are not allowed")
        if executable.endswith(".exe"):
            executable = executable[:-4]

        readonly = self.read_only_commands.get(executable)
        mutating = self.mutating_commands.get(executable)
        if executable not in self.read_only_commands and executable not in self.mutating_commands:
            return _decision(PolicyAction.DENY, "command is not allowlisted")
        if executable == "rg" and self._contains_option(argv[1:], _UNSAFE_RG_OPTIONS):
            return _decision(PolicyAction.DENY, "rg process-execution options are not allowed")
        if executable == "git" and self._contains_option(argv[1:], _UNSAFE_GIT_OPTIONS):
            return _decision(PolicyAction.DENY, "git execution options are not allowed")
        if readonly is None:
            return _decision(PolicyAction.ALLOW, "read-only command allowed")
        if len(argv) < 2:
            return _decision(PolicyAction.DENY, "command requires an allowlisted subcommand")

        subcommand = argv[1].casefold()
        if mutating is not None and subcommand in mutating:
            return _decision(PolicyAction.REQUIRE_APPROVAL, "mutating command requires approval")
        if subcommand not in readonly:
            return _decision(PolicyAction.DENY, "subcommand is not allowlisted")
        if executable == "git" and subcommand == "branch" and self._branch_mutates(argv[2:]):
            return _decision(PolicyAction.REQUIRE_APPROVAL, "branch mutation requires approval")
        return _decision(PolicyAction.ALLOW, "read-only command allowed")

    @staticmethod
    def _contains_option(arguments: Sequence[str], blocked: set[str]) -> bool:
        return any(
            argument in blocked
            or any(
                argument.startswith(option + "=")
                for option in blocked
                if option.startswith("--")
            )
            for argument in arguments
        )

    @staticmethod
    def _branch_mutates(arguments: Sequence[str]) -> bool:
        if any(argument in _MUTATING_BRANCH_OPTIONS for argument in arguments):
            return True
        return any(not argument.startswith("-") for argument in arguments)

    @staticmethod
    def _evaluate_url(raw_url: Any) -> PolicyDecision:
        if not isinstance(raw_url, str) or not raw_url.strip():
            return _decision(PolicyAction.DENY, "URL must be non-empty text")
        try:
            parsed = urlsplit(raw_url)
            hostname = parsed.hostname
            parsed.port
        except ValueError:
            return _decision(PolicyAction.DENY, "URL is invalid")
        if parsed.scheme.casefold() != "https":
            return _decision(PolicyAction.DENY, "only HTTPS URLs are allowed")
        if parsed.username is not None or parsed.password is not None:
            return _decision(PolicyAction.DENY, "URL credentials are not allowed")
        if not hostname:
            return _decision(PolicyAction.DENY, "URL requires a hostname")

        normalized_host = hostname.rstrip(".").casefold()
        if (
            normalized_host == "localhost"
            or normalized_host.endswith(".localhost")
            or normalized_host.endswith(".local")
        ):
            return _decision(PolicyAction.DENY, "local hostnames are not allowed")
        try:
            address = ipaddress.ip_address(normalized_host)
        except ValueError:
            try:
                ascii_host = normalized_host.encode("idna").decode("ascii")
            except UnicodeError:
                return _decision(PolicyAction.DENY, "URL hostname is invalid")
            labels = ascii_host.split(".")
            if len(ascii_host) > 253 or any(not _HOST_LABEL.fullmatch(label) for label in labels):
                return _decision(PolicyAction.DENY, "URL hostname is invalid")
        else:
            if not address.is_global:
                return _decision(PolicyAction.DENY, "private or local IP addresses are not allowed")
        return _decision(PolicyAction.ALLOW, "HTTPS URL syntax allowed", host=normalized_host)


__all__ = ["PolicyAction", "PolicyDecision", "PolicyEngine"]
