"""Thread-safe redacted JSONL trace persistence."""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cyberdeck.redaction import redact


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _confined_path(path: Path, trace_dir: Path) -> Path:
    resolved_path = path.expanduser().resolve(strict=False)
    resolved_dir = trace_dir.expanduser().resolve(strict=False)
    try:
        common = Path(os.path.commonpath((resolved_path, resolved_dir)))
    except ValueError as exc:
        raise ValueError("trace path is outside trace_dir") from exc
    if common != resolved_dir:
        raise ValueError("trace path is outside trace_dir")
    return resolved_path


class JsonlTraceStore:
    """Append ordered, redacted events to one UTF-8 JSONL file."""

    def __init__(
        self,
        path: str | os.PathLike[str],
        *,
        run_id: str,
        trace_dir: str | os.PathLike[str] | None = None,
    ) -> None:
        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError("trace store requires run_id")
        raw_path = Path(path)
        allowed_dir = Path(trace_dir) if trace_dir is not None else raw_path.parent
        self.path = _confined_path(raw_path, allowed_dir)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and not self.path.is_file():
            raise ValueError("trace path must be a file")
        self.run_id = run_id
        self._lock = threading.Lock()
        self._sequence = self._existing_event_count()

    def _existing_event_count(self) -> int:
        if not self.path.exists():
            return 0
        with self.path.open("r", encoding="utf-8") as handle:
            return sum(1 for line in handle if line.strip())

    def record(self, event_type: str, data: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("trace event_type must be non-empty text")
        if not isinstance(data, Mapping):
            raise ValueError("trace data must be an object")
        with self._lock:
            self._sequence += 1
            event = {
                "run_id": self.run_id,
                "seq": self._sequence,
                "timestamp": _utc_timestamp(),
                "event_type": event_type,
                "data": redact(dict(data)),
            }
            line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
            with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(line + "\n")
            return event

    def read_events(self) -> list[dict[str, Any]]:
        with self._lock:
            if not self.path.exists():
                return []
            with self.path.open("r", encoding="utf-8") as handle:
                return [json.loads(line) for line in handle if line.strip()]


def summarize_events(events: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """Summarize tool outcomes and recorded duration from trace events."""

    summary = {
        "events": 0,
        "tool_calls": 0,
        "tool_successes": 0,
        "errors": 0,
        "duration_ms": 0,
    }
    for event in events:
        summary["events"] += 1
        data = event.get("data", {})
        if not isinstance(data, Mapping):
            data = {}
        if event.get("event_type") == "tool_result":
            summary["tool_calls"] += 1
            if data.get("success") is True:
                summary["tool_successes"] += 1
            elif data.get("success") is False:
                summary["errors"] += 1
        elif data.get("error_category"):
            summary["errors"] += 1
        duration = data.get("duration_ms", 0)
        if isinstance(duration, (int, float)) and not isinstance(duration, bool) and duration > 0:
            summary["duration_ms"] += int(duration)
    return summary
