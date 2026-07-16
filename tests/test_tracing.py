import json
import re

import pytest

from cyberdeck.redaction import redact
from cyberdeck.tracing import JsonlTraceStore, summarize_events


def test_redact_masks_nested_secret_values_without_mutating_input():
    data = {
        "headers": {"Authorization": "Bearer top-secret"},
        "api_key": "sk-demo-secret",
        "items": [{"password": "hunter2"}],
    }

    cleaned = redact(data)
    encoded = json.dumps(cleaned)

    assert "top-secret" not in encoded
    assert "sk-demo-secret" not in encoded
    assert "hunter2" not in encoded
    assert data["api_key"] == "sk-demo-secret"
    assert cleaned["api_key"] == "[REDACTED]"


def test_redact_masks_secrets_embedded_in_strings_and_tuples():
    value = (
        "Authorization: Bearer abc.def.ghi",
        "password=hunter2 api_key=sk-project-12345678",
    )

    cleaned = redact(value)

    assert isinstance(cleaned, tuple)
    assert "abc.def.ghi" not in cleaned[0]
    assert "hunter2" not in cleaned[1]
    assert "sk-project-12345678" not in cleaned[1]


def test_trace_store_writes_ordered_redacted_jsonl(tmp_path):
    store = JsonlTraceStore(tmp_path / "run.jsonl", run_id="run-1")

    first = store.record("provider", {"token": "private-value", "duration_ms": 12})
    second = store.record("tool_result", {"success": True, "duration_ms": 3})
    events = store.read_events()

    assert first["seq"] == 1
    assert second["seq"] == 2
    assert events == [first, second]
    assert events[0]["run_id"] == "run-1"
    assert events[0]["data"]["token"] == "[REDACTED]"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", events[0]["timestamp"])
    assert (tmp_path / "run.jsonl").read_bytes().endswith(b"\n")


def test_trace_store_continues_sequence_when_reopened(tmp_path):
    path = tmp_path / "run.jsonl"
    JsonlTraceStore(path, run_id="run-1").record("start", {})

    event = JsonlTraceStore(path, run_id="run-1").record("finish", {})

    assert event["seq"] == 2


def test_trace_store_rejects_empty_event_and_trace_directory_escape(tmp_path):
    store = JsonlTraceStore(tmp_path / "traces" / "run.jsonl", run_id="run-1")
    with pytest.raises(ValueError, match="event_type"):
        store.record("", {})

    with pytest.raises(ValueError, match="outside trace_dir"):
        JsonlTraceStore(
            tmp_path / "outside.jsonl",
            run_id="run-1",
            trace_dir=tmp_path / "traces",
        )


def test_summary_counts_tools_errors_and_duration():
    summary = summarize_events(
        [
            {"event_type": "tool_result", "data": {"success": True, "duration_ms": 10}},
            {"event_type": "tool_result", "data": {"success": False, "duration_ms": 5}},
        ]
    )

    assert summary == {
        "events": 2,
        "tool_calls": 2,
        "tool_successes": 1,
        "errors": 1,
        "duration_ms": 15,
    }
