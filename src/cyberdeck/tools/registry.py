"""Tool registration, policy evaluation, approval, and error normalization."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import replace

from cyberdeck.models import ErrorCategory, ToolRequest, ToolResult
from cyberdeck.policy import PolicyAction, PolicyDecision, PolicyEngine

ToolHandler = Callable[[ToolRequest], ToolResult]
ApprovalCallback = Callable[[ToolRequest, PolicyDecision], bool]


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    def register(self, name: str, handler: ToolHandler) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("tool name must be non-empty text")
        if not callable(handler):
            raise ValueError("tool handler must be callable")
        if name in self._handlers:
            raise ValueError(f"tool already registered: {name}")
        self._handlers[name] = handler

    def execute(
        self,
        request: ToolRequest,
        policy: PolicyEngine,
        *,
        approval: ApprovalCallback | None = None,
    ) -> ToolResult:
        started = time.perf_counter()
        try:
            decision = policy.evaluate(request)
        except Exception:
            return self._failure(
                request,
                ErrorCategory.POLICY,
                "policy evaluation failed",
                started,
            )
        if decision.action is PolicyAction.DENY:
            return self._failure(request, ErrorCategory.POLICY, decision.reason, started)
        if decision.action is PolicyAction.REQUIRE_APPROVAL:
            if approval is None:
                return self._failure(
                    request,
                    ErrorCategory.APPROVAL,
                    "explicit approval is required",
                    started,
                )
            try:
                approved = approval(request, decision) is True
            except Exception:
                approved = False
            if not approved:
                return self._failure(
                    request,
                    ErrorCategory.APPROVAL,
                    "approval was not granted",
                    started,
                )

        handler = self._handlers.get(request.name)
        if handler is None:
            return self._failure(
                request,
                ErrorCategory.TOOL,
                "approved tool has no registered handler",
                started,
            )
        try:
            result = handler(request)
        except TimeoutError:
            return self._failure(request, ErrorCategory.TIMEOUT, "tool timed out", started)
        except Exception:
            return self._failure(request, ErrorCategory.TOOL, "tool handler failed", started)
        if not isinstance(result, ToolResult):
            return self._failure(
                request,
                ErrorCategory.TOOL,
                "tool handler returned an invalid result",
                started,
            )
        if result.duration_ms == 0:
            return replace(result, duration_ms=self._elapsed_ms(started))
        return result

    @staticmethod
    def _elapsed_ms(started: float) -> int:
        return max(0, int((time.perf_counter() - started) * 1000))

    @classmethod
    def _failure(
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
            duration_ms=cls._elapsed_ms(started),
        )


__all__ = ["ApprovalCallback", "ToolHandler", "ToolRegistry"]
