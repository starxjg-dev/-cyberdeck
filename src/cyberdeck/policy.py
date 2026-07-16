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

_TEXT_VALUE = ("text", None)
_PATH_VALUE = ("path", None)
_INTEGER_VALUE = ("integer", None)
_COLOR_VALUE = ("choice", frozenset({"always", "auto", "never"}))

_RG_FLAG_OPTIONS = frozenset(
    {
        "--count",
        "--files",
        "--files-with-matches",
        "--fixed-strings",
        "--heading",
        "--hidden",
        "--ignore-case",
        "--invert-match",
        "--json",
        "--line-number",
        "--no-heading",
        "--smart-case",
        "--stats",
        "--word-regexp",
        "-F",
        "-S",
        "-c",
        "-i",
        "-l",
        "-n",
        "-v",
        "-w",
    }
)
_RG_VALUE_OPTIONS = {
    "--after-context": _INTEGER_VALUE,
    "--before-context": _INTEGER_VALUE,
    "--color": _COLOR_VALUE,
    "--context": _INTEGER_VALUE,
    "--file": _PATH_VALUE,
    "--glob": _TEXT_VALUE,
    "--max-count": _INTEGER_VALUE,
    "--regexp": _TEXT_VALUE,
    "--type": _TEXT_VALUE,
    "--type-not": _TEXT_VALUE,
    "-A": _INTEGER_VALUE,
    "-B": _INTEGER_VALUE,
    "-C": _INTEGER_VALUE,
    "-T": _TEXT_VALUE,
    "-e": _TEXT_VALUE,
    "-f": _PATH_VALUE,
    "-g": _TEXT_VALUE,
    "-m": _INTEGER_VALUE,
    "-t": _TEXT_VALUE,
}

_GIT_FLAG_OPTIONS = {
    "status": frozenset(
        {"--branch", "--long", "--short", "-b", "-s"}
    ),
    "diff": frozenset(
        {
            "--cached",
            "--check",
            "--exit-code",
            "--name-only",
            "--name-status",
            "--no-color",
            "--no-ext-diff",
            "--no-patch",
            "--numstat",
            "--patch",
            "--quiet",
            "--shortstat",
            "--staged",
            "--stat",
            "-p",
            "-s",
        }
    ),
    "log": frozenset(
        {
            "--all",
            "--decorate",
            "--graph",
            "--merges",
            "--name-only",
            "--name-status",
            "--no-decorate",
            "--no-merges",
            "--oneline",
            "--patch",
            "--reverse",
            "--stat",
            "-p",
        }
    ),
    "show": frozenset(
        {
            "--name-only",
            "--name-status",
            "--no-color",
            "--no-patch",
            "--oneline",
            "--patch",
            "--stat",
            "-p",
            "-s",
        }
    ),
    "grep": frozenset(
        {
            "--break",
            "--count",
            "--files-with-matches",
            "--fixed-strings",
            "--heading",
            "--ignore-case",
            "--line-number",
            "--word-regexp",
            "-F",
            "-I",
            "-c",
            "-i",
            "-l",
            "-n",
            "-w",
        }
    ),
    "branch": frozenset(
        {
            "--all",
            "--list",
            "--remotes",
            "--show-current",
            "-a",
            "-r",
            "-v",
            "-vv",
        }
    ),
}
_GIT_VALUE_OPTIONS = {
    "status": {
        "--porcelain": ("choice", frozenset({"v1", "v2"})),
        "--untracked-files": ("choice", frozenset({"all", "no", "normal"})),
    },
    "diff": {"--color": _COLOR_VALUE, "--unified": _INTEGER_VALUE, "-U": _INTEGER_VALUE},
    "log": {
        "--author": _TEXT_VALUE,
        "--format": _TEXT_VALUE,
        "--grep": _TEXT_VALUE,
        "--max-count": _INTEGER_VALUE,
        "--pretty": _TEXT_VALUE,
        "--since": _TEXT_VALUE,
        "--until": _TEXT_VALUE,
        "-n": _INTEGER_VALUE,
    },
    "show": {
        "--color": _COLOR_VALUE,
        "--format": _TEXT_VALUE,
        "--pretty": _TEXT_VALUE,
    },
    "grep": {"--max-count": _INTEGER_VALUE, "--regexp": _TEXT_VALUE, "-e": _TEXT_VALUE},
    "branch": {
        "--contains": _TEXT_VALUE,
        "--format": _TEXT_VALUE,
        "--merged": _TEXT_VALUE,
        "--no-contains": _TEXT_VALUE,
        "--no-merged": _TEXT_VALUE,
        "--sort": _TEXT_VALUE,
    },
}

_GIT_ADD_FLAG_OPTIONS = frozenset(
    {"--all", "--dry-run", "--patch", "--update", "-A", "-n", "-p", "-u"}
)


class PolicyAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class PolicyDecision:
    action: PolicyAction
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class _ParsedArguments:
    positionals: tuple[tuple[str, bool], ...]
    seen_options: frozenset[str]


class _GrammarError(ValueError):
    pass


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

        if executable not in self.read_only_commands and executable not in self.mutating_commands:
            return _decision(PolicyAction.DENY, "command is not allowlisted")
        try:
            if executable == "rg":
                if executable not in self.read_only_commands:
                    raise _GrammarError("command is not configured as read-only")
                self._validate_rg(argv[1:])
                return _decision(PolicyAction.ALLOW, "read-only command allowed")
            if executable == "git":
                return self._evaluate_git(argv[1:])
            if len(argv) != 1:
                raise _GrammarError("configured command has no safe argument grammar")
        except _GrammarError as exc:
            return _decision(PolicyAction.DENY, str(exc))
        return _decision(PolicyAction.ALLOW, "configured command without arguments allowed")

    def _validate_rg(self, arguments: Sequence[str]) -> None:
        parsed = self._parse_options(arguments, _RG_FLAG_OPTIONS, _RG_VALUE_OPTIONS)
        positionals = [value for value, _after_separator in parsed.positionals]
        options_supply_pattern = bool(
            parsed.seen_options.intersection({"--file", "--regexp", "-e", "-f"})
        )
        files_mode = "--files" in parsed.seen_options
        if files_mode or options_supply_pattern:
            path_operands = positionals
        else:
            if not positionals:
                raise _GrammarError("rg requires a pattern")
            path_operands = positionals[1:]
        self._validate_paths(path_operands)

    def _evaluate_git(self, arguments: Sequence[str]) -> PolicyDecision:
        if not arguments:
            raise _GrammarError("git requires an allowlisted subcommand")
        subcommand = arguments[0].casefold()
        readonly = self.read_only_commands.get("git")
        mutating = self.mutating_commands.get("git")
        if mutating is not None and subcommand in mutating:
            self._validate_git_mutation(subcommand, arguments[1:])
            return _decision(
                PolicyAction.REQUIRE_APPROVAL,
                "mutating command requires approval",
            )
        if readonly is not None and subcommand not in readonly:
            raise _GrammarError("subcommand is not allowlisted")
        flags = _GIT_FLAG_OPTIONS.get(subcommand)
        values = _GIT_VALUE_OPTIONS.get(subcommand)
        if flags is None or values is None:
            raise _GrammarError("subcommand has no safe option grammar")
        parsed = self._parse_options(arguments[1:], flags, values)
        positionals = [value for value, _after_separator in parsed.positionals]
        path_operands = [
            value for value, after_separator in parsed.positionals if after_separator
        ]

        if subcommand == "status":
            self._validate_paths(positionals)
        elif subcommand == "grep":
            pattern_supplied = bool(parsed.seen_options.intersection({"--regexp", "-e"}))
            before_separator = [
                value for value, after_separator in parsed.positionals if not after_separator
            ]
            if not pattern_supplied and not before_separator:
                raise _GrammarError("git grep requires a pattern")
            self._validate_paths(path_operands)
        elif subcommand == "branch":
            if positionals and "--list" not in parsed.seen_options:
                return _decision(
                    PolicyAction.REQUIRE_APPROVAL,
                    "branch mutation requires approval",
                )
        else:
            self._validate_paths(path_operands)
            self._validate_obvious_paths(positionals)
        return _decision(PolicyAction.ALLOW, "read-only command allowed")

    def _validate_git_mutation(self, subcommand: str, arguments: Sequence[str]) -> None:
        if subcommand == "add":
            parsed = self._parse_options(arguments, _GIT_ADD_FLAG_OPTIONS, {})
            self._validate_paths([value for value, _after in parsed.positionals])
            return
        if any(argument.startswith("-") for argument in arguments):
            raise _GrammarError("mutation option is not in the safe grammar")
        self._validate_obvious_paths(arguments)

    def _parse_options(
        self,
        arguments: Sequence[str],
        flag_options: Collection[str],
        value_options: Mapping[str, tuple[str, frozenset[str] | None]],
    ) -> _ParsedArguments:
        positionals: list[tuple[str, bool]] = []
        seen_options: set[str] = set()
        after_separator = False
        index = 0
        while index < len(arguments):
            argument = arguments[index]
            if not after_separator and argument == "--":
                after_separator = True
                index += 1
                continue
            if not after_separator and argument.startswith("-") and argument != "-":
                option, separator, inline_value = argument.partition("=")
                if option in flag_options:
                    if separator:
                        raise _GrammarError(f"option does not accept a value: {option}")
                    seen_options.add(option)
                    index += 1
                    continue
                rule = value_options.get(option)
                if rule is None:
                    raise _GrammarError(f"option is not in the safe grammar: {option}")
                if separator:
                    value = inline_value
                else:
                    index += 1
                    if index >= len(arguments):
                        raise _GrammarError(f"option requires a value: {option}")
                    value = arguments[index]
                self._validate_option_value(option, value, rule)
                seen_options.add(option)
                index += 1
                continue
            positionals.append((argument, after_separator))
            index += 1
        return _ParsedArguments(tuple(positionals), frozenset(seen_options))

    def _validate_option_value(
        self,
        option: str,
        value: str,
        rule: tuple[str, frozenset[str] | None],
    ) -> None:
        if not value:
            raise _GrammarError(f"option requires a non-empty value: {option}")
        kind, choices = rule
        if kind == "path":
            try:
                self.resolve_path(value)
            except (OSError, ValueError) as exc:
                raise _GrammarError(f"option path escapes workspace: {option}") from exc
        elif kind == "integer" and not value.isdecimal():
            raise _GrammarError(f"option requires a non-negative integer: {option}")
        elif kind == "choice" and choices is not None and value.casefold() not in choices:
            raise _GrammarError(f"option value is not allowlisted: {option}")

    def _validate_paths(self, values: Sequence[str]) -> None:
        for value in values:
            try:
                self.resolve_path(value)
            except (OSError, ValueError) as exc:
                raise _GrammarError("command path escapes workspace") from exc

    def _validate_obvious_paths(self, values: Sequence[str]) -> None:
        for value in values:
            candidate = Path(value)
            if candidate.is_absolute() or ".." in candidate.parts:
                self._validate_paths([value])

    @staticmethod
    def _evaluate_url(raw_url: Any) -> PolicyDecision:
        if not isinstance(raw_url, str) or not raw_url.strip():
            return _decision(PolicyAction.DENY, "URL must be non-empty text")
        try:
            parsed = urlsplit(raw_url)
            hostname = parsed.hostname
            _ = parsed.port
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
