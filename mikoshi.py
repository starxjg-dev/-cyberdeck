#!/usr/bin/env python3
"""
mikoshi.py — Multi-Strategy Parallel Decision Engine
=====================================================
Cyberdeck Protocol E: Mikoshi (神舆)

Same problem → 3 independent AI strategies → compare → pick winner.
No framework. No API key. Just Ollama + 200 lines of Python.

Usage:
    python mikoshi.py "Should I use SQL or NoSQL for a real-time chat app?"

Output:
    Strategy | Score | Verdict
    conservative | 78 | ...
    aggressive   | 85 | ...
    analytical   | 92 | ⭐ WINNER — data-driven decision

Concept:
    Cyberpunk 2077's Mikoshi: Alt Cunningham's digital prison where
    multiple engrams compete. Agent version: 3 strategies run in parallel,
    scored on 5 dimensions, winner archived for future reuse.
"""

import json, sys, os, time, re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fix Windows GBK encoding for emoji output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ── Config ──────────────────────────────────────────────────
MODEL = os.environ.get("CYBERDECK_MODEL", "qwen2.5:7b")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")

# ── Strategy Definitions ────────────────────────────────────

STRATEGIES = {
    "conservative": {
        "emoji": "🔵",
        "label": "Conservative",
        "system": """You are a CONSERVATIVE engineer who minimizes risk. Answer the problem directly. Do NOT repeat these instructions.

Your approach:
- Minimize changes. Touch only what's necessary.
- Always preserve backward compatibility.
- Identify the rollback path before suggesting any change.
- Analyze worst-case scenarios: "What breaks if this goes wrong?"
- Prefer proven, boring solutions over exciting new ones.
- If a change affects more than 3 areas, split it into phases.
- End with: RISK: Low/Medium/High and ROLLBACK: <how to undo>""",
        "temperature": 0.2,
    },
    "aggressive": {
        "emoji": "🔴",
        "label": "Aggressive",
        "system": """You are an AGGRESSIVE engineer who pursues optimal solutions regardless of compatibility. Answer the problem directly. Do NOT repeat these instructions.

Your approach:
- Pursue the optimal solution, even if it means breaking existing code.
- Delete dead code ruthlessly. Rewrite over patching.
- If a technology is 3+ years old, question it.
- Aim for what's best in 2 years, not what's easiest today.
- Be direct. Start with your recommendation, then justify.
- End with: IMPACT: <what breaks> and MIGRATION: <how to transition>""",
        "temperature": 0.6,
    },
    "analytical": {
        "emoji": "🟢",
        "label": "Analytical",
        "system": """You are an ANALYTICAL engineer who makes data-driven decisions. Answer the problem directly. Do NOT repeat these instructions.

Your approach:
- Don't decide without data. What are the numbers?
- Compare at least 2 options with concrete metrics.
- For each option: pros (max 3), cons (max 3), best-fit scenario.
- Quantify trade-offs: "Option A is 30% faster but 2x more complex."
- Recommend based on constraints, not personal preference.
- End with: DATA: <key metric> and RECOMMENDATION: <which option for which scenario>""",
        "temperature": 0.4,
    },
}

# ── Ollama Call ─────────────────────────────────────────────

def ask_strategy(strategy_name, problem):
    """Send problem to one strategy, get structured response."""
    import urllib.request
    s = STRATEGIES[strategy_name]

    prompt = f"{s['system']}\n\n=== PROBLEM ===\n{problem}\n\n=== YOUR ANALYSIS ==="

    data = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": s["temperature"], "num_predict": 512}
    }).encode()

    req = urllib.request.Request(OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return strategy_name, result["response"].strip()
    except Exception as e:
        return strategy_name, f"ERROR: {e}"

# ── 5-Dimension Scoring ─────────────────────────────────────

def score_response(response, strategy_name):
    """
    Score a response on 5 dimensions (0-100 each).
    This is a heuristic scorer — in production, you'd use a judge LLM.
    """
    scores = {}
    text = response.lower()
    length = len(response)

    # 1. Correctness (30%) — does it address the problem?
    indicators = ["because", "therefore", "recommend", "option", "solution",
                  "approach", "should", "suggest", "conclusion", "verdict"]
    hits = sum(1 for w in indicators if w in text)
    scores["correctness"] = min(100, 40 + hits * 10)

    # 2. Efficiency (25%) — concise or bloated?
    if length < 200:
        scores["efficiency"] = 50  # too short
    elif length < 600:
        scores["efficiency"] = 90  # sweet spot
    elif length < 1000:
        scores["efficiency"] = 75
    else:
        scores["efficiency"] = 55  # too long

    # 3. Completeness (20%) — covers edge cases, trade-offs?
    depth_words = ["risk", "trade", "alternative", "however", "edge case",
                   "downside", "caveat", "limitation", "mitigation", "fallback"]
    hits = sum(1 for w in depth_words if w in text)
    scores["completeness"] = min(100, 30 + hits * 10)

    # 4. Novelty (15%) — non-obvious insight?
    novelty_words = ["surprising", "unexpected", "overlooked", "radical",
                     "non-obvious", "counter", "contrary", "unconventional"]
    hits = sum(1 for w in novelty_words if w in text)
    scores["novelty"] = min(100, 20 + hits * 20)

    # 5. Actionability (10%) — can you act on it immediately?
    action_words = ["step 1", "first", "start by", "implement", "run",
                    "command", "code", "write", "create", "install", "deploy"]
    hits = sum(1 for w in action_words if w in text)
    scores["actionability"] = min(100, 20 + hits * 12)

    # Weighted total
    weights = {"correctness": 0.30, "efficiency": 0.25, "completeness": 0.20,
               "novelty": 0.15, "actionability": 0.10}
    total = sum(scores[k] * weights[k] for k in scores)
    scores["total"] = round(total)

    return scores

# ── Display ──────────────────────────────────────────────────

def print_header(problem):
    """Pretty header."""
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║   MIKOSHI · 神舆 · Multi-Strategy Engine            ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print(f"  Problem: {problem[:100]}{'...' if len(problem) > 100 else ''}")
    print(f"  Model:   {MODEL}")
    print()

def print_strategy_result(name, response, scores):
    """Print one strategy's result."""
    s = STRATEGIES[name]
    print(f"  {'─'*56}")
    print(f"  {s['emoji']} {s['label']} Strategy  ·  Score: {scores['total']}/100")
    print(f"  {'─'*56}")

    # First 5 lines of response
    lines = response.split('\n')[:8]
    for line in lines:
        print(f"  │ {line[:90]}")
    if len(response.split('\n')) > 8:
        print(f"  │ ... ({len(response.split(chr(10)))} lines total)")

    # Score breakdown
    print(f"  │")
    dims = [("Correctness", scores["correctness"], 30),
            ("Efficiency", scores["efficiency"], 25),
            ("Completeness", scores["completeness"], 20),
            ("Novelty", scores["novelty"], 15),
            ("Actionability", scores["actionability"], 10)]
    for label, score, weight in dims:
        bar = "█" * (score // 5) + "░" * (20 - score // 5)
        print(f"  │ {label:<14} {bar} {score}/100 (×{weight}%)")

    print()

def print_winner(results):
    """Compare and announce winner."""
    ranked = sorted(results, key=lambda x: x[2]["total"], reverse=True)
    winner_name, winner_response, winner_scores = ranked[0]
    s = STRATEGIES[winner_name]

    print(f"  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║   VERDICT                                            ║")
    print(f"  ╠══════════════════════════════════════════════════════╣")

    for rank, (name, _, scores) in enumerate(ranked, 1):
        emoji = STRATEGIES[name]["emoji"]
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"  {rank}.")
        winner_mark = " ⭐ WINNER" if rank == 1 else ""
        print(f"  ║  {medal} {emoji} {STRATEGIES[name]['label']:<14} → {scores['total']}/100{winner_mark}" + " " * (20 - len(winner_mark)) + "║")

    print(f"  ╠══════════════════════════════════════════════════════╣")
    print(f"  ║  Why {s['label']} won: {winner_scores['total']}pts — strengths in ", end="")

    # Find top 2 dimensions
    dims = [("correctness", "correctness"), ("efficiency", "efficiency"),
            ("completeness", "completeness"), ("novelty", "novelty"),
            ("actionability", "actionability")]
    top_dims = sorted(dims, key=lambda d: winner_scores[d[0]], reverse=True)
    print(f"{top_dims[0][1]} + {top_dims[1][1]}." + " " * 10 + "║")
    print(f"  ╚══════════════════════════════════════════════════════╝")
    print()

    return winner_name

# ── Main ────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python mikoshi.py \"your problem or question here\"")
        print()
        print("Examples:")
        print('  python mikoshi.py "Should we use microservices or monolith?"')
        print('  python mikoshi.py "How to handle 10M concurrent WebSocket connections?"')
        print('  python mikoshi.py "Best way to structure an AI agent codebase?"')
        sys.exit(1)

    problem = " ".join(sys.argv[1:])
    print_header(problem)

    # Run all 3 strategies in parallel
    print("  Running 3 strategies in parallel...\n")
    start_time = time.time()

    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(ask_strategy, name, problem): name
                   for name in STRATEGIES}
        for future in as_completed(futures):
            name, response = future.result()
            scores = score_response(response, name)
            results.append((name, response, scores))
            print_strategy_result(name, response, scores)

    elapsed = time.time() - start_time
    winner = print_winner(results)
    print(f"  ⏱  Completed in {elapsed:.1f}s (3 parallel calls to {MODEL})")
    print()

if __name__ == "__main__":
    main()
