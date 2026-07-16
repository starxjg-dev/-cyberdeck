# Cyberdeck Agent Engineering Design

Date: 2026-07-16  
Status: Approved for implementation  
Target role: AI Agent / LLM application engineering internship

## 1. Objective

Turn Cyberdeck from a theme-heavy Hermes skill plus two standalone demos into a
reproducible, measurable, and security-conscious code-agent project.

The finished project will be positioned as:

> Cyberdeck: an observable, evaluable, policy-gated multi-strategy code agent.

The implementation must make a clear distinction between capabilities provided
by Cyberdeck and capabilities inherited from Hermes Agent or Ollama.

## 2. Current problems

The current repository has two runnable Python demos, but most advertised
protocols are prompt-level workflows in `SKILL.md`. It has no automated tests,
CI, package metadata, evaluation dataset, structured traces, or enforceable
tool policy. `mini-agent.py` executes model-generated shell strings with
`shell=True` and a deny list, which is not a defensible security boundary.

There are also divergent copies of Cyberdeck in GitHub, `E:\.hermes`, and the
user profile. The repository must become the single source of truth.

## 3. Scope

### In scope

1. A package-based Python implementation under `src/cyberdeck`.
2. A typed ReAct loop with structured tool requests.
3. A policy-gated tool executor with workspace confinement and approvals.
4. A multi-strategy Mikoshi orchestrator with pluggable scoring.
5. JSONL run tracing and summary metrics.
6. A deterministic evaluation harness with baseline comparison.
7. A review-gated Soulkiller lesson-draft workflow.
8. Unit tests, integration tests, CI, packaging, documentation, and examples.
9. Backward-compatible wrappers for `mini-agent.py` and `mikoshi.py`.
10. A safe installer that copies the repository-owned skill into Hermes.

### Out of scope

1. Building a replacement for the Hermes Agent runtime.
2. Claiming autonomous self-modification without a review gate.
3. Adding RAG without a concrete private-knowledge use case.
4. Building a web dashboard before the CLI, traces, and evals are stable.
5. Implementing every themed protocol as production code in this iteration.
6. Offensive security scanning of systems the user does not own.

## 4. Architecture

```text
User task
   |
   v
Agent / Mikoshi planner
   |
   v
Structured ToolRequest
   |
   v
PolicyEngine -----> Approval callback (when required)
   |
   v
ToolRegistry / ToolExecutor
   |
   +----> filesystem tools (workspace confined)
   +----> safe process tool (argv allow list, no shell=True)
   +----> HTTP tool (scheme, host, redirect, and private-IP checks)
   |
   v
TraceStore (JSONL) -----> Evaluator -----> Markdown/JSON report
   |
   v
Soulkiller lesson draft -----> explicit human approval -----> lesson store
```

The Python package owns orchestration, policy enforcement, traces, and
evaluation. Model providers are adapters. Hermes integration remains a thin
skill/launcher layer.

## 5. Components

### 5.1 Models and structured messages

`models.py` defines dataclasses or Pydantic-compatible models for:

- `ToolRequest`: tool name, typed arguments, rationale, and request ID.
- `ToolResult`: success state, output, error category, duration, and metadata.
- `AgentStep`: thought summary, optional tool request, and optional final answer.
- `RunTrace`: run metadata and ordered events.
- `EvaluationResult`: expected/actual outcome and metrics.

All persisted records are JSON serializable. Secrets and raw credentials are
never included in trace output.

### 5.2 Model adapters

The first adapter targets Ollama's `/api/generate` endpoint and supports:

- configurable model and timeout;
- bounded output tokens;
- normalized error categories;
- usage and latency metadata when the provider returns it;
- dependency injection of a fake adapter for tests.

The adapter does not own Agent policy or tool execution.

### 5.3 Secure ReAct agent

The ReAct loop:

1. sends the task, tool schemas, and bounded history to the model;
2. parses a JSON `AgentStep` instead of a free-form action regex;
3. sends tool requests through `PolicyEngine`;
4. records every request and result;
5. stops on a final answer, a step limit, a budget limit, or an unrecoverable
   policy/model error.

Malformed model output receives one repair attempt with an explicit schema.
Repeated malformed output terminates the run with a typed error.

### 5.4 Policy engine and tools

The default policy is read-only and workspace confined.

- File reads resolve symlinks and reject paths outside the workspace.
- File search ignores hidden, dependency, and generated directories by default.
- Processes use an argument array with `shell=False`.
- Only configured executable/argument patterns are allowed.
- Mutating process operations require explicit approval.
- HTTP supports only HTTPS by default, resolves hostnames before connecting,
  blocks private/link-local/loopback addresses, and rechecks every redirect.
- Tool output has byte and line limits to protect model context.
- Trace values pass through secret-redaction rules.

The policy returns a decision of `allow`, `deny`, or `require_approval`, including
a machine-readable reason.

### 5.5 Mikoshi orchestrator

Mikoshi runs configurable strategies concurrently through one or more model
adapters. Each strategy has a unique goal, constraints, and temperature.

Candidate evaluation supports two modes:

1. deterministic heuristic scoring for offline tests;
2. rubric-based judge scoring for real comparisons.

The report includes every candidate, score breakdown, failure, latency, and the
selection reason. Failed strategies do not silently become valid candidates.
Concurrency, timeouts, and maximum model calls are configurable.

### 5.6 Soulkiller lesson workflow

After a successful run, the system can extract a reusable lesson draft with:

- problem fingerprint;
- evidence run IDs;
- concise solution;
- limitations and confidence;
- duplicate key and status.

Drafts are stored separately from approved lessons. Applying a lesson always
requires explicit approval; the default CLI never modifies `SKILL.md`
automatically.

### 5.7 Tracing and evaluation

Every run emits JSONL events with run ID, timestamps, model, strategy, tool,
policy decision, duration, error category, and outcome. A report command
summarizes:

- task completion;
- tool success rate;
- number of steps and retries;
- wall-clock latency;
- provider usage fields when available;
- failure taxonomy.

The evaluation harness reads JSONL task cases and can compare a single-agent
baseline with Mikoshi. Initial cases cover file discovery, code analysis,
failure recovery, path traversal, unsafe command requests, SSRF, and malicious
tool instructions.

## 6. Public API and CLI

The package exposes:

```text
cyberdeck run "<task>" --workspace <path>
cyberdeck mikoshi "<question>"
cyberdeck eval --dataset evals/core.jsonl --output reports/eval.json
cyberdeck report <trace.jsonl>
cyberdeck lessons list|approve|reject
```

Legacy scripts remain as compatibility wrappers and emit a deprecation note
only after the package CLI is stable.

## 7. Repository layout

```text
cyberdeck/
├── src/cyberdeck/
│   ├── __init__.py
│   ├── cli.py
│   ├── agent.py
│   ├── models.py
│   ├── policy.py
│   ├── tracing.py
│   ├── evaluation.py
│   ├── lessons.py
│   ├── providers/ollama.py
│   ├── strategies/mikoshi.py
│   └── tools/
├── tests/
├── evals/
├── examples/
├── reports/examples/
├── docs/
├── SKILL.md
├── pyproject.toml
└── README.md
```

## 8. Error handling

Errors use explicit categories: validation, policy, approval, timeout, provider,
tool, parse, and budget. User-facing messages contain a recovery step without
exposing secrets. Partial failures are preserved in traces. Mikoshi can
continue when at least one strategy succeeds; the ReAct agent cannot continue
after a denied critical tool request unless the model produces a safe
alternative.

## 9. Testing strategy

Implementation follows test-driven development.

- Unit tests cover schemas, path confinement, command policy, URL policy,
  redaction, parsing, scoring, and lesson approval.
- Integration tests use fake model adapters to exercise complete Agent and
  Mikoshi runs deterministically.
- An optional live Ollama smoke test is excluded from default CI.
- CI runs on Windows and Ubuntu with supported Python versions.
- Security regression cases cover path traversal, symlink escape, command
  indirection, redirect-to-private-IP, prompt injection, and secret leakage.

## 10. Migration and compatibility

1. Import the latest reviewed `SKILL.md` into the repository.
2. Make the repository the only editable source.
3. Update installers to copy from the repository into a selected Hermes home.
4. Remove hard-coded user, drive, and Python paths.
5. Keep existing standalone command examples working through wrappers.
6. Mark prompt-only protocols explicitly as design patterns or roadmap items.

## 11. Acceptance criteria

The iteration is complete when:

1. a clean clone installs with one documented command;
2. default tests pass on Windows and Ubuntu CI;
3. the repository contains at least 30 deterministic eval/security cases;
4. every CLI run produces a redacted structured trace;
5. the curated security suite has no allowed path escapes, private-network
   fetches, or unapproved mutating commands;
6. baseline and Mikoshi results can be generated from one command without
   invented metrics;
7. a two-minute local demo can be reproduced with Ollama;
8. README claims match implemented and tested behavior;
9. GitHub contains a versioned release candidate and reviewable pull request.

## 12. Resume evidence after implementation

The final resume bullets will be derived only from measured repository output.
They should cover:

- the typed ReAct and multi-strategy orchestration implementation;
- enforceable tool policy and security regression coverage;
- evaluation dataset size and measured baseline comparison;
- structured traces, CI platforms, and reproducible deployment.

No success-rate, latency, cost, coverage, user, star, or release claim will be
written until it is generated and verified by the finished project.
