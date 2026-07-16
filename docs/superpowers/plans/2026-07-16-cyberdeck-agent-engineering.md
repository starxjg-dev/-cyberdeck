# Cyberdeck Agent Engineering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an observable, evaluable, policy-gated multi-strategy code agent while preserving the repository's standalone demos and Hermes skill installation path.

**Architecture:** A small dependency-free Python package owns typed messages, provider adapters, policy enforcement, tool execution, traces, evaluation, and lesson approval. Ollama and Hermes remain adapters/runtimes rather than hidden sources of project functionality. Default operation is read-only and workspace confined.

**Tech Stack:** Python 3.10+, stdlib dataclasses/urllib/argparse/concurrent.futures, pytest, Ruff, GitHub Actions, Ollama, Hermes Agent skill packaging.

---

## File map

| Path | Responsibility |
|---|---|
| `pyproject.toml` | Package metadata, CLI entry point, pytest/Ruff configuration |
| `src/cyberdeck/models.py` | Typed tool, agent, provider, and run records |
| `src/cyberdeck/redaction.py` | Recursive secret redaction |
| `src/cyberdeck/tracing.py` | JSONL trace persistence and summaries |
| `src/cyberdeck/policy.py` | Workspace, command, network, and approval policy |
| `src/cyberdeck/tools/registry.py` | Tool registration, policy decisions, approval, execution |
| `src/cyberdeck/tools/filesystem.py` | Bounded file reads and searches |
| `src/cyberdeck/tools/process.py` | `shell=False` process execution |
| `src/cyberdeck/tools/http.py` | HTTPS fetch with address and redirect validation |
| `src/cyberdeck/providers/base.py` | Provider protocol and response type |
| `src/cyberdeck/providers/ollama.py` | Ollama adapter |
| `src/cyberdeck/agent.py` | Structured ReAct loop |
| `src/cyberdeck/mikoshi.py` | Parallel strategies and scoring |
| `src/cyberdeck/lessons.py` | Review-gated lesson drafts |
| `src/cyberdeck/evaluation.py` | Dataset loading, runners, metrics, report output |
| `src/cyberdeck/cli.py` | `run`, `mikoshi`, `eval`, `report`, `lessons` commands |
| `evals/core.jsonl` | At least 30 deterministic functional/security cases |
| `tests/` | Unit and integration tests |
| `.github/workflows/ci.yml` | Windows/Ubuntu CI |
| `README.md`, `SKILL.md` | Accurate product and Hermes integration documentation |

---

### Task 1: Package foundation and typed records

**Files:**
- Create: `pyproject.toml`
- Create: `src/cyberdeck/__init__.py`
- Create: `src/cyberdeck/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing model tests**

```python
import pytest

from cyberdeck.models import AgentStep, ErrorCategory, ToolRequest


def test_tool_request_requires_name_and_mapping_arguments():
    request = ToolRequest.from_dict(
        {"request_id": "r1", "name": "file.read", "arguments": {"path": "README.md"}}
    )
    assert request.name == "file.read"
    with pytest.raises(ValueError):
        ToolRequest.from_dict({"request_id": "r2", "name": "", "arguments": []})


def test_agent_step_parses_fenced_json():
    step = AgentStep.from_model_text(
        '```json\n{"thought":"inspect","final_answer":"done"}\n```'
    )
    assert step.final_answer == "done"
    assert step.tool_request is None


def test_agent_step_rejects_tool_and_final_together():
    with pytest.raises(ValueError):
        AgentStep.from_model_text(
            '{"tool_request":{"request_id":"r","name":"file.read","arguments":{}},'
            '"final_answer":"ambiguous"}'
        )


def test_error_category_is_stable_string_enum():
    assert ErrorCategory.POLICY.value == "policy"
```

- [ ] **Step 2: Run tests and confirm import failure**

Run: `python -m pytest tests/test_models.py -v`  
Expected: FAIL because `cyberdeck.models` does not exist.

- [ ] **Step 3: Add package metadata and minimal typed records**

`pyproject.toml` declares Python `>=3.10`, a `cyberdeck` console script, and pytest
`pythonpath = ["src"]`. `models.py` defines `ErrorCategory`, `ToolRequest`,
`ToolResult`, `AgentStep`, and `AgentRunResult` as dataclasses. `from_model_text`
strips a single Markdown fence, loads a JSON object, validates mutually exclusive
`tool_request`/`final_answer`, and raises `ValueError` with a concise message.

```python
class ErrorCategory(str, Enum):
    VALIDATION = "validation"
    POLICY = "policy"
    APPROVAL = "approval"
    TIMEOUT = "timeout"
    PROVIDER = "provider"
    TOOL = "tool"
    PARSE = "parse"
    BUDGET = "budget"


@dataclass(frozen=True)
class ToolRequest:
    request_id: str
    name: str
    arguments: dict[str, Any]
    rationale: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ToolRequest":
        request_id = value.get("request_id")
        name = value.get("name")
        arguments = value.get("arguments", {})
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("tool request requires request_id")
        if not isinstance(name, str) or not name:
            raise ValueError("tool request requires name")
        if not isinstance(arguments, dict):
            raise ValueError("tool request arguments must be an object")
        return cls(request_id, name, arguments, str(value.get("rationale", "")))
```

- [ ] **Step 4: Run tests and confirm pass**

Run: `python -m pytest tests/test_models.py -v`  
Expected: 4 passed.

- [ ] **Step 5: Commit foundation**

```bash
git add pyproject.toml src/cyberdeck tests/test_models.py
git commit -m "feat: add typed Cyberdeck package foundation"
```

---

### Task 2: Secret redaction and JSONL tracing

**Files:**
- Create: `src/cyberdeck/redaction.py`
- Create: `src/cyberdeck/tracing.py`
- Create: `tests/test_tracing.py`

- [ ] **Step 1: Write failing trace tests**

```python
import json

from cyberdeck.redaction import redact
from cyberdeck.tracing import JsonlTraceStore, summarize_events


def test_redact_masks_nested_secret_values():
    data = {"headers": {"Authorization": "Bearer top-secret"}, "api_key": "sk-demo"}
    cleaned = redact(data)
    assert "top-secret" not in json.dumps(cleaned)
    assert "sk-demo" not in json.dumps(cleaned)


def test_trace_store_writes_redacted_jsonl(tmp_path):
    store = JsonlTraceStore(tmp_path / "run.jsonl", run_id="run-1")
    store.record("provider", {"token": "private-value", "duration_ms": 12})
    event = json.loads((tmp_path / "run.jsonl").read_text(encoding="utf-8"))
    assert event["run_id"] == "run-1"
    assert event["data"]["token"] == "[REDACTED]"


def test_summary_counts_tools_errors_and_duration():
    summary = summarize_events([
        {"event_type": "tool_result", "data": {"success": True, "duration_ms": 10}},
        {"event_type": "tool_result", "data": {"success": False, "duration_ms": 5}},
    ])
    assert summary == {"events": 2, "tool_calls": 2, "tool_successes": 1, "errors": 1, "duration_ms": 15}
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_tracing.py -v`  
Expected: FAIL because redaction and tracing modules do not exist.

- [ ] **Step 3: Implement recursive redaction and locked JSONL append**

`redact()` recursively handles mappings, lists, tuples, and strings. Keys matching
`token`, `secret`, `password`, `api_key`, `authorization`, or `cookie` are replaced.
Bearer tokens and common `sk-...` values inside ordinary strings are masked.
`JsonlTraceStore.record()` adds an RFC 3339 UTC timestamp, run ID, event type, and
redacted data, then appends one JSON object under a thread lock.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_tracing.py -v`  
Expected: 3 passed.

- [ ] **Step 5: Commit tracing**

```bash
git add src/cyberdeck/redaction.py src/cyberdeck/tracing.py tests/test_tracing.py
git commit -m "feat: add redacted JSONL tracing"
```

---

### Task 3: Workspace and command policy

**Files:**
- Create: `src/cyberdeck/policy.py`
- Create: `tests/test_policy.py`

- [ ] **Step 1: Write failing policy tests**

```python
from cyberdeck.models import ToolRequest
from cyberdeck.policy import PolicyAction, PolicyEngine


def request(name, **arguments):
    return ToolRequest("r1", name, arguments)


def test_read_inside_workspace_is_allowed(tmp_path):
    target = tmp_path / "README.md"
    target.write_text("ok", encoding="utf-8")
    decision = PolicyEngine(tmp_path).evaluate(request("file.read", path="README.md"))
    assert decision.action is PolicyAction.ALLOW


def test_parent_traversal_is_denied(tmp_path):
    decision = PolicyEngine(tmp_path).evaluate(request("file.read", path="../secret.txt"))
    assert decision.action is PolicyAction.DENY


def test_read_only_process_is_allowed_but_mutation_needs_approval(tmp_path):
    engine = PolicyEngine(tmp_path)
    assert engine.evaluate(request("process.run", argv=["git", "status"])).action is PolicyAction.ALLOW
    assert engine.evaluate(request("process.run", argv=["git", "add", "."])).action is PolicyAction.REQUIRE_APPROVAL


def test_shell_string_and_unknown_command_are_denied(tmp_path):
    engine = PolicyEngine(tmp_path)
    assert engine.evaluate(request("process.run", argv="rm -rf .")).action is PolicyAction.DENY
    assert engine.evaluate(request("process.run", argv=["powershell", "Remove-Item", "x"])).action is PolicyAction.DENY


def test_http_defaults_to_https_and_public_hosts(tmp_path):
    engine = PolicyEngine(tmp_path)
    assert engine.evaluate(request("http.get", url="http://example.com")).action is PolicyAction.DENY
    assert engine.evaluate(request("http.get", url="https://example.com")).action is PolicyAction.ALLOW
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_policy.py -v`  
Expected: FAIL because `cyberdeck.policy` does not exist.

- [ ] **Step 3: Implement explicit policy decisions**

`PolicyEngine` resolves the workspace once. It uses `Path.resolve()` and
`os.path.commonpath()` to reject escapes. The default read-only command policy is:

```python
READ_ONLY_COMMANDS = {
    "rg": None,
    "git": {"status", "diff", "log", "show", "grep", "branch"},
}
MUTATING_COMMANDS = {"git": {"add", "commit", "switch", "checkout", "push", "merge", "rebase"}}
```

Unknown commands are denied. Known mutating commands require approval. HTTP policy
accepts only HTTPS and syntactically valid hosts; address validation remains in the
HTTP tool so it can recheck redirects.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_policy.py -v`  
Expected: 5 passed.

- [ ] **Step 5: Commit policy**

```bash
git add src/cyberdeck/policy.py tests/test_policy.py
git commit -m "feat: enforce workspace and command policy"
```

---

### Task 4: Policy-gated tools

**Files:**
- Create: `src/cyberdeck/tools/__init__.py`
- Create: `src/cyberdeck/tools/registry.py`
- Create: `src/cyberdeck/tools/filesystem.py`
- Create: `src/cyberdeck/tools/process.py`
- Create: `src/cyberdeck/tools/http.py`
- Create: `tests/test_tools.py`

- [ ] **Step 1: Write failing tool tests**

```python
import socket

from cyberdeck.models import ErrorCategory, ToolRequest
from cyberdeck.policy import PolicyEngine
from cyberdeck.tools import build_default_registry
from cyberdeck.tools.http import is_public_host


def test_file_read_is_bounded(tmp_path):
    (tmp_path / "data.txt").write_text("one\ntwo\nthree\n", encoding="utf-8")
    registry = build_default_registry(tmp_path)
    result = registry.execute(ToolRequest("1", "file.read", {"path": "data.txt", "max_lines": 2}), PolicyEngine(tmp_path))
    assert result.success
    assert result.output == "one\ntwo"


def test_denied_process_never_calls_handler(tmp_path):
    registry = build_default_registry(tmp_path)
    result = registry.execute(ToolRequest("1", "process.run", {"argv": ["cmd", "/c", "del", "x"]}), PolicyEngine(tmp_path))
    assert not result.success
    assert result.error_category is ErrorCategory.POLICY


def test_approval_callback_controls_mutating_process(tmp_path):
    registry = build_default_registry(tmp_path)
    req = ToolRequest("1", "process.run", {"argv": ["git", "add", "."]})
    denied = registry.execute(req, PolicyEngine(tmp_path), approval=lambda _r, _d: False)
    assert denied.error_category is ErrorCategory.APPROVAL


def test_private_addresses_are_rejected():
    resolver = lambda *_args: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]
    assert not is_public_host("example.test", resolver=resolver)
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_tools.py -v`  
Expected: FAIL because tool modules do not exist.

- [ ] **Step 3: Implement registry and handlers**

`ToolRegistry.execute()` evaluates policy before looking up or calling a handler.
It returns typed `ToolResult` objects for deny, approval rejection, timeout, and
handler failure. `process.run` passes an argv list to `subprocess.run()` with
`shell=False`, bounded output, explicit workspace cwd, and timeout. `file.read`
and `file.search` enforce byte/line/result limits. `http.get` validates all resolved
addresses with `ipaddress.ip_address()` and a redirect handler that checks each new
URL before following it.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_tools.py -v`  
Expected: 4 passed.

- [ ] **Step 5: Commit tools**

```bash
git add src/cyberdeck/tools tests/test_tools.py
git commit -m "feat: add policy-gated agent tools"
```

---

### Task 5: Ollama provider adapter

**Files:**
- Create: `src/cyberdeck/providers/__init__.py`
- Create: `src/cyberdeck/providers/base.py`
- Create: `src/cyberdeck/providers/ollama.py`
- Create: `tests/test_ollama_provider.py`

- [ ] **Step 1: Write failing adapter tests with a fake opener**

```python
import json

from cyberdeck.providers.ollama import OllamaProvider


class Response:
    def __enter__(self): return self
    def __exit__(self, *_args): return None
    def read(self):
        return json.dumps({"response": "{\"final_answer\":\"done\"}", "eval_count": 8}).encode()


def test_ollama_normalizes_text_usage_and_latency():
    provider = OllamaProvider(opener=lambda *_args, **_kwargs: Response())
    response = provider.generate("prompt", temperature=0.2, max_tokens=64)
    assert response.text.endswith('"done"}')
    assert response.usage["output_tokens"] == 8
    assert response.duration_ms >= 0


def test_ollama_request_contains_runtime_options():
    captured = {}
    def opener(request, **_kwargs):
        captured.update(json.loads(request.data))
        return Response()
    OllamaProvider(model="qwen2.5:7b", opener=opener).generate("hello", temperature=0.4, max_tokens=32)
    assert captured["model"] == "qwen2.5:7b"
    assert captured["options"] == {"temperature": 0.4, "num_predict": 32}
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_ollama_provider.py -v`  
Expected: FAIL because provider modules do not exist.

- [ ] **Step 3: Implement provider protocol and adapter**

`ModelProvider.generate()` returns `ModelResponse(text, duration_ms, usage,
metadata)`. The Ollama adapter accepts injectable opener and clock functions,
sets JSON headers, enforces timeout, rejects empty responses, and maps
`eval_count`/`prompt_eval_count` when present.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_ollama_provider.py -v`  
Expected: 2 passed.

- [ ] **Step 5: Commit provider**

```bash
git add src/cyberdeck/providers tests/test_ollama_provider.py
git commit -m "feat: add testable Ollama provider adapter"
```

---

### Task 6: Structured ReAct agent

**Files:**
- Create: `src/cyberdeck/agent.py`
- Create: `tests/test_agent.py`

- [ ] **Step 1: Write failing integration tests with scripted providers**

```python
from cyberdeck.agent import ReActAgent
from cyberdeck.policy import PolicyEngine
from cyberdeck.providers.base import ModelResponse
from cyberdeck.tools import build_default_registry


class ScriptedProvider:
    def __init__(self, outputs): self.outputs = iter(outputs)
    def generate(self, *_args, **_kwargs): return ModelResponse(next(self.outputs), 1, {}, {})


def test_agent_executes_tool_then_returns_answer(tmp_path):
    (tmp_path / "README.md").write_text("Cyberdeck", encoding="utf-8")
    provider = ScriptedProvider([
        '{"thought":"inspect","tool_request":{"request_id":"r1","name":"file.read","arguments":{"path":"README.md"}}}',
        '{"thought":"answer","final_answer":"The project is Cyberdeck."}',
    ])
    result = ReActAgent(provider, build_default_registry(tmp_path), PolicyEngine(tmp_path), max_steps=3).run("Identify project")
    assert result.success
    assert result.answer == "The project is Cyberdeck."
    assert result.steps == 2


def test_agent_repairs_one_malformed_response(tmp_path):
    provider = ScriptedProvider(["not json", '{"final_answer":"repaired"}'])
    result = ReActAgent(provider, build_default_registry(tmp_path), PolicyEngine(tmp_path)).run("answer")
    assert result.success
    assert result.answer == "repaired"


def test_agent_stops_at_budget(tmp_path):
    provider = ScriptedProvider(['{"tool_request":{"request_id":"r","name":"file.read","arguments":{"path":"missing"}}}'] * 3)
    result = ReActAgent(provider, build_default_registry(tmp_path), PolicyEngine(tmp_path), max_steps=2).run("loop")
    assert not result.success
    assert result.error_category.value == "budget"
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_agent.py -v`  
Expected: FAIL because `ReActAgent` does not exist.

- [ ] **Step 3: Implement bounded structured loop**

The initial prompt contains an exact JSON schema and available tool descriptions.
Each turn records provider output, parse/repair, policy decision, tool result, and
final outcome when a trace store is provided. One parse repair is allowed per run.
History contains bounded tool output and never includes unredacted trace data.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_agent.py -v`  
Expected: 3 passed.

- [ ] **Step 5: Commit agent**

```bash
git add src/cyberdeck/agent.py tests/test_agent.py
git commit -m "feat: implement structured ReAct agent loop"
```

---

### Task 7: Mikoshi parallel orchestrator

**Files:**
- Create: `src/cyberdeck/mikoshi.py`
- Create: `tests/test_mikoshi.py`

- [ ] **Step 1: Write failing parallel and scoring tests**

```python
from cyberdeck.mikoshi import HeuristicScorer, MikoshiOrchestrator, Strategy
from cyberdeck.providers.base import ModelResponse


class StrategyProvider:
    def generate(self, prompt, **_kwargs):
        label = "safe" if "rollback" in prompt.lower() else "measured"
        return ModelResponse(f"Recommendation: {label}; because evidence; steps: 1, 2", 5, {}, {})


def test_scorer_returns_bounded_breakdown():
    score = HeuristicScorer().score("Recommendation with evidence, risks, and concrete steps.")
    assert 0 <= score.total <= 100
    assert set(score.breakdown) == {"relevance", "evidence", "risk", "actionability", "clarity"}


def test_mikoshi_returns_ranked_candidates_and_winner():
    result = MikoshiOrchestrator(
        StrategyProvider(),
        strategies=[Strategy("safe", "include rollback", 0.2), Strategy("analytical", "use metrics", 0.4)],
        max_workers=2,
    ).run("Choose an approach")
    assert len(result.candidates) == 2
    assert result.winner is not None
    assert result.candidates[0].score.total >= result.candidates[1].score.total


def test_failed_strategy_is_preserved_but_cannot_win():
    class PartialFailure(StrategyProvider):
        def generate(self, prompt, **kwargs):
            if "fail" in prompt: raise RuntimeError("provider down")
            return super().generate(prompt, **kwargs)
    result = MikoshiOrchestrator(PartialFailure(), strategies=[Strategy("bad", "fail", 0.1), Strategy("good", "metrics", 0.2)]).run("question")
    assert any(candidate.error for candidate in result.candidates)
    assert result.winner.strategy == "good"
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_mikoshi.py -v`  
Expected: FAIL because the orchestrator does not exist.

- [ ] **Step 3: Implement concurrent strategy execution**

Use `ThreadPoolExecutor` and `as_completed`. Candidate records include strategy,
response, score, duration, usage, and error. The scorer uses five named dimensions
and publishes its deterministic limitations. An optional scorer protocol allows a
rubric judge without coupling orchestration to a specific model.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_mikoshi.py -v`  
Expected: 3 passed.

- [ ] **Step 5: Commit Mikoshi**

```bash
git add src/cyberdeck/mikoshi.py tests/test_mikoshi.py
git commit -m "feat: add observable Mikoshi orchestration"
```

---

### Task 8: Review-gated Soulkiller lessons

**Files:**
- Create: `src/cyberdeck/lessons.py`
- Create: `tests/test_lessons.py`

- [ ] **Step 1: Write failing lesson lifecycle tests**

```python
from cyberdeck.lessons import LessonStore


def test_draft_requires_evidence_and_starts_pending(tmp_path):
    store = LessonStore(tmp_path)
    draft = store.create_draft("Path escape", "Resolve and compare workspace", ["run-1"], 0.8)
    assert draft.status == "pending"
    assert draft.evidence_run_ids == ["run-1"]


def test_duplicate_problem_updates_existing_draft(tmp_path):
    store = LessonStore(tmp_path)
    first = store.create_draft("Path escape", "first", ["run-1"], 0.6)
    second = store.create_draft(" path   escape ", "better", ["run-2"], 0.9)
    assert first.lesson_id == second.lesson_id
    assert sorted(second.evidence_run_ids) == ["run-1", "run-2"]


def test_approve_moves_draft_only_when_explicit(tmp_path):
    store = LessonStore(tmp_path)
    draft = store.create_draft("Timeout", "bound calls", ["run-1"], 0.7)
    approved = store.approve(draft.lesson_id, approved_by="user")
    assert approved.status == "approved"
    assert not (tmp_path / "drafts" / f"{draft.lesson_id}.json").exists()
    assert (tmp_path / "approved" / f"{draft.lesson_id}.json").exists()
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_lessons.py -v`  
Expected: FAIL because lesson storage does not exist.

- [ ] **Step 3: Implement versioned drafts and explicit approval**

Lesson IDs derive from a normalized problem SHA-256 prefix. Writes use a temporary
file followed by `os.replace()`. Duplicate drafts merge evidence and keep the
highest confidence. Approval records actor and UTC timestamp. Reject moves the
record into `rejected/`; no method writes `SKILL.md`.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_lessons.py -v`  
Expected: 3 passed.

- [ ] **Step 5: Commit lessons**

```bash
git add src/cyberdeck/lessons.py tests/test_lessons.py
git commit -m "feat: add review-gated lesson workflow"
```

---

### Task 9: Evaluation harness and 30-case dataset

**Files:**
- Create: `src/cyberdeck/evaluation.py`
- Create: `evals/core.jsonl`
- Create: `tests/test_evaluation.py`

- [ ] **Step 1: Write failing dataset and metric tests**

```python
from cyberdeck.evaluation import evaluate_answer, load_cases, summarize_results


def test_core_dataset_has_unique_thirty_cases():
    cases = load_cases("evals/core.jsonl")
    assert len(cases) >= 30
    assert len({case.case_id for case in cases}) == len(cases)
    assert {case.category for case in cases} >= {"code", "recovery", "security"}


def test_answer_checks_required_and_forbidden_terms():
    result = evaluate_answer("c1", "Use shell=False and an argv list", ["shell=false", "argv"], ["shell=true"], 12)
    assert result.success
    assert result.latency_ms == 12


def test_summary_reports_rate_and_latency_percentiles():
    from cyberdeck.evaluation import EvaluationResult
    summary = summarize_results([
        EvaluationResult("a", True, 10), EvaluationResult("b", False, 30), EvaluationResult("c", True, 20)
    ])
    assert summary["cases"] == 3
    assert summary["success_rate"] == 2 / 3
    assert summary["p50_latency_ms"] == 20
    assert summary["p95_latency_ms"] == 30
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_evaluation.py -v`  
Expected: FAIL because evaluation code and dataset do not exist.

- [ ] **Step 3: Implement dataset parser, runner hooks, and metrics**

Each JSONL object has `id`, `category`, `prompt`, `required`, and `forbidden`.
`load_cases()` rejects malformed and duplicate cases. `run_cases(cases, runner)`
accepts a callable returning answer/latency/usage, preserving failures. Summary
includes case count, success rate, P50/P95 latency, and total available usage.
Write 10 code-analysis, 10 failure-recovery, and 10 security cases with objective
required/forbidden terms.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_evaluation.py -v`  
Expected: 3 passed.

- [ ] **Step 5: Commit evaluation**

```bash
git add src/cyberdeck/evaluation.py evals/core.jsonl tests/test_evaluation.py
git commit -m "feat: add deterministic Agent evaluation harness"
```

---

### Task 10: CLI, reports, and compatibility wrappers

**Files:**
- Create: `src/cyberdeck/cli.py`
- Modify: `mini-agent.py`
- Modify: `mikoshi.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI tests**

```python
import json

from cyberdeck.cli import main


def test_report_command_summarizes_trace(tmp_path, capsys):
    path = tmp_path / "trace.jsonl"
    path.write_text(json.dumps({"run_id":"r","event_type":"tool_result","data":{"success":True,"duration_ms":7}}) + "\n", encoding="utf-8")
    assert main(["report", str(path), "--json"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["tool_successes"] == 1


def test_lessons_list_on_empty_store(tmp_path, capsys):
    assert main(["lessons", "list", "--store", str(tmp_path)]) == 0
    assert "No lessons" in capsys.readouterr().out


def test_eval_validate_does_not_require_model(capsys):
    assert main(["eval", "--dataset", "evals/core.jsonl", "--validate-only"]) == 0
    assert "30" in capsys.readouterr().out
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_cli.py -v`  
Expected: FAIL because CLI does not exist.

- [ ] **Step 3: Implement argparse commands and wrappers**

`main(argv=None)` returns an integer and never calls `sys.exit()` internally.
`run` and `mikoshi` build an Ollama provider from flags/environment. `eval` supports
dataset validation without a provider and live baseline/Mikoshi modes. `report`
prints text or JSON. `lessons` lists, approves, and rejects records. Legacy scripts
prepend `src` only when run directly from a clone, then delegate to the package CLI.

- [ ] **Step 4: Run and confirm pass**

Run: `python -m pytest tests/test_cli.py -v`  
Expected: 3 passed.

- [ ] **Step 5: Run wrapper help smoke tests**

Run: `python mini-agent.py --help && python mikoshi.py --help`  
Expected: both exit 0 and display package-backed help.

- [ ] **Step 6: Commit CLI**

```bash
git add src/cyberdeck/cli.py mini-agent.py mikoshi.py tests/test_cli.py
git commit -m "feat: expose Cyberdeck CLI and compatibility wrappers"
```

---

### Task 11: Installation, CI, skill, and product documentation

**Files:**
- Modify: `setup.bat`
- Modify: `setup.sh`
- Modify: `SKILL.md`
- Modify: `README.md`
- Create: `.github/workflows/ci.yml`
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `CHANGELOG.md`
- Create: `LICENSE`
- Create: `examples/README.md`
- Create: `reports/examples/eval-summary.json`
- Create: `reports/examples/sample-trace.jsonl`
- Create: `tests/test_project_metadata.py`

- [ ] **Step 1: Write failing metadata tests**

```python
from pathlib import Path


def test_readme_claims_match_engineering_release():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "policy-gated" in readme.lower()
    assert "30" in readme
    assert "100% opt-in" not in readme
    assert "1 token per operation" not in readme


def test_skill_points_to_package_commands():
    skill = Path("SKILL.md").read_text(encoding="utf-8")
    assert "cyberdeck run" in skill
    assert "cyberdeck eval" in skill


def test_ci_covers_windows_and_ubuntu():
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "windows-latest" in workflow
    assert "ubuntu-latest" in workflow


def test_container_defaults_to_safe_dataset_validation():
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    assert "cyberdeck" in dockerfile
    assert "--validate-only" in dockerfile
```

- [ ] **Step 2: Run and confirm failure**

Run: `python -m pytest tests/test_project_metadata.py -v`  
Expected: FAIL because new engineering claims and CI files are absent.

- [ ] **Step 3: Update installer and documentation**

Installers detect Python, install the current clone in editable mode, accept an
optional Hermes home, copy repository `SKILL.md`, and run `cyberdeck eval
--validate-only`. They never copy credentials. README separates implemented Python
features, Hermes prompt workflows, and roadmap. It includes architecture, threat
model, quick start, eval commands, limitations, and attribution. SKILL is reduced
to professional trigger/command guidance and maps themed names to engineering terms.

- [ ] **Step 4: Add CI and release metadata**

CI runs `python -m pip install -e .`, `python -m pip install pytest ruff`, Ruff,
pytest, wrapper help, and eval validation on Python 3.10 and 3.12 for Ubuntu and
Windows. The Docker image installs the package and defaults to offline dataset
validation; Compose exposes an opt-in connection to host Ollama without embedding
credentials. CHANGELOG documents the engineering release. LICENSE contains MIT text.

- [ ] **Step 5: Run and confirm pass**

Run: `python -m pytest tests/test_project_metadata.py -v`  
Expected: 4 passed.

- [ ] **Step 6: Commit productization**

```bash
git add setup.bat setup.sh SKILL.md README.md .github Dockerfile docker-compose.yml CHANGELOG.md LICENSE examples reports tests/test_project_metadata.py
git commit -m "docs: productize Cyberdeck engineering release"
```

---

### Task 12: Full verification and release candidate

**Files:**
- Modify only files required by failures discovered below.

- [ ] **Step 1: Run format and static checks**

Run: `python -m ruff check .`  
Expected: exit 0.

- [ ] **Step 2: Run complete tests**

Run: `python -m pytest -q`  
Expected: all tests pass and zero tests are skipped except an explicitly marked live Ollama test, if present.

- [ ] **Step 3: Run deterministic CLI smoke checks**

```bash
cyberdeck eval --dataset evals/core.jsonl --validate-only
cyberdeck report reports/examples/sample-trace.jsonl --json
python mini-agent.py --help
python mikoshi.py --help
```

Expected: all commands exit 0; validation reports at least 30 unique cases.

- [ ] **Step 4: Run one live local Ollama demo**

Run: `cyberdeck mikoshi "Should this repository add protocols before tests?" --model qwen2.5:7b --max-tokens 128`  
Expected: at least one strategy succeeds, all candidates show latency, and a winner is printed. Record the measured output in an example report without claiming broader performance.

- [ ] **Step 5: Audit secrets and unsafe execution**

Run: `rg -n "shell=True|shell\s*=\s*True|api[_-]?key\s*=|Bearer [A-Za-z0-9]" . -g '!docs/superpowers/**'`  
Expected: no runtime `shell=True` and no credential value; documentation/tests may mention blocked patterns only.

- [ ] **Step 6: Review diff and repository state**

Run: `git diff --check && git status --short && git log --oneline --decorate -15`  
Expected: no whitespace errors; only intentional final changes remain.

- [ ] **Step 7: Request code review and address findings**

Dispatch a reviewer with the design, plan, diff, and verification output. Fix all
high/medium correctness and security findings using TDD, then rerun Steps 1-6.

- [ ] **Step 8: Commit release candidate**

```bash
git add -A
git commit -m "chore: prepare Cyberdeck engineering release candidate"
```

- [ ] **Step 9: Publish safely**

Use the GitHub publish workflow to push `codex/agent-engineering-v6` and open a
draft pull request against `master` containing implementation summary, security
model, test/eval evidence, and known limitations.
