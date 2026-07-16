"""Typed, JSON-serializable records shared by Cyberdeck components."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class ErrorCategory(str, Enum):
    """Stable machine-readable failure categories."""

    VALIDATION = "validation"
    POLICY = "policy"
    APPROVAL = "approval"
    TIMEOUT = "timeout"
    PROVIDER = "provider"
    TOOL = "tool"
    PARSE = "parse"
    BUDGET = "budget"


def _required_text(value: Any, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(message)
    return value


def _mapping(value: Any, message: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(message)
    result = dict(value)
    try:
        json.dumps(result)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{message}; values must be JSON serializable") from exc
    return result


def _optional_category(value: Any) -> ErrorCategory | None:
    if value is None or value == "":
        return None
    if isinstance(value, ErrorCategory):
        return value
    try:
        return ErrorCategory(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("unknown error category") from exc


@dataclass(frozen=True)
class ToolRequest:
    request_id: str
    name: str
    arguments: dict[str, Any]
    rationale: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "request_id",
            _required_text(self.request_id, "tool request requires request_id"),
        )
        object.__setattr__(self, "name", _required_text(self.name, "tool request requires name"))
        object.__setattr__(
            self,
            "arguments",
            _mapping(self.arguments, "tool request arguments must be an object"),
        )
        if not isinstance(self.rationale, str):
            raise ValueError("tool request rationale must be text")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ToolRequest":
        if not isinstance(value, Mapping):
            raise ValueError("tool request must be an object")
        return cls(
            request_id=value.get("request_id"),
            name=value.get("name"),
            arguments=value.get("arguments", {}),
            rationale=value.get("rationale", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "name": self.name,
            "arguments": dict(self.arguments),
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class ToolResult:
    request_id: str
    tool_name: str
    success: bool
    output: str = ""
    error_category: ErrorCategory | None = None
    error_message: str = ""
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "request_id",
            _required_text(self.request_id, "result requires request_id"),
        )
        object.__setattr__(
            self,
            "tool_name",
            _required_text(self.tool_name, "result requires tool_name"),
        )
        if not isinstance(self.success, bool):
            raise ValueError("result success must be boolean")
        if not isinstance(self.output, str) or not isinstance(self.error_message, str):
            raise ValueError("result output and error_message must be text")
        object.__setattr__(self, "error_category", _optional_category(self.error_category))
        if (
            not isinstance(self.duration_ms, int)
            or isinstance(self.duration_ms, bool)
            or self.duration_ms < 0
        ):
            raise ValueError("result duration_ms must be a non-negative integer")
        object.__setattr__(
            self,
            "metadata",
            _mapping(self.metadata, "result metadata must be an object"),
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ToolResult":
        if not isinstance(value, Mapping):
            raise ValueError("tool result must be an object")
        return cls(
            request_id=value.get("request_id"),
            tool_name=value.get("tool_name"),
            success=value.get("success"),
            output=value.get("output", ""),
            error_category=value.get("error_category"),
            error_message=value.get("error_message", ""),
            duration_ms=value.get("duration_ms", 0),
            metadata=value.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "success": self.success,
            "output": self.output,
            "error_category": self.error_category.value if self.error_category else None,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "metadata": dict(self.metadata),
        }


_FENCED_JSON = re.compile(
    r"^```(?:json)?[ \t]*\r?\n(?P<body>.*)\r?\n```$",
    re.DOTALL | re.IGNORECASE,
)


@dataclass(frozen=True)
class AgentStep:
    thought: str = ""
    tool_request: ToolRequest | None = None
    final_answer: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.thought, str):
            raise ValueError("agent thought must be text")
        if self.tool_request is not None and not isinstance(self.tool_request, ToolRequest):
            raise ValueError("agent tool_request must be a ToolRequest")
        if self.final_answer is not None and not isinstance(self.final_answer, str):
            raise ValueError("agent final_answer must be text")
        if self.tool_request is not None and self.final_answer is not None:
            raise ValueError("agent step cannot contain both tool_request and final_answer")

    @classmethod
    def from_model_text(cls, model_text: str) -> "AgentStep":
        if not isinstance(model_text, str) or not model_text.strip():
            raise ValueError("model output must be valid JSON")
        text = model_text.strip()
        if text.startswith("```") or text.endswith("```"):
            match = _FENCED_JSON.fullmatch(text)
            if match is None:
                raise ValueError("model output has an invalid Markdown fence")
            text = match.group("body").strip()
        try:
            value = json.loads(text)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError("model output must be valid JSON") from exc
        if not isinstance(value, Mapping):
            raise ValueError("model output must be a JSON object")
        raw_tool_request = value.get("tool_request")
        if raw_tool_request is not None and not isinstance(raw_tool_request, Mapping):
            raise ValueError("tool_request must be an object")
        tool_request = (
            ToolRequest.from_dict(raw_tool_request) if raw_tool_request is not None else None
        )
        return cls(
            thought=value.get("thought", ""),
            tool_request=tool_request,
            final_answer=value.get("final_answer"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "thought": self.thought,
            "tool_request": self.tool_request.to_dict() if self.tool_request else None,
            "final_answer": self.final_answer,
        }


@dataclass(frozen=True)
class AgentRunResult:
    run_id: str
    success: bool
    answer: str
    steps: int
    error_category: ErrorCategory | None = None
    error_message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "run_id",
            _required_text(self.run_id, "agent result requires run_id"),
        )
        if not isinstance(self.success, bool):
            raise ValueError("agent result success must be boolean")
        if not isinstance(self.answer, str) or not isinstance(self.error_message, str):
            raise ValueError("agent result answer and error_message must be text")
        if (
            not isinstance(self.steps, int)
            or isinstance(self.steps, bool)
            or self.steps < 0
        ):
            raise ValueError("agent result steps must be a non-negative integer")
        object.__setattr__(self, "error_category", _optional_category(self.error_category))
        object.__setattr__(
            self,
            "metadata",
            _mapping(self.metadata, "agent result metadata must be an object"),
        )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "AgentRunResult":
        if not isinstance(value, Mapping):
            raise ValueError("agent result must be an object")
        return cls(
            run_id=value.get("run_id"),
            success=value.get("success"),
            answer=value.get("answer", ""),
            steps=value.get("steps"),
            error_category=value.get("error_category"),
            error_message=value.get("error_message", ""),
            metadata=value.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "success": self.success,
            "answer": self.answer,
            "steps": self.steps,
            "error_category": self.error_category.value if self.error_category else None,
            "error_message": self.error_message,
            "metadata": dict(self.metadata),
        }
