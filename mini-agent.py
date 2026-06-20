#!/usr/bin/env python3
"""
mini-agent.py — A 150-line ReAct AI Agent
===========================================
Cyberdeck Project — https://github.com/starxjg-dev/cyberdeck

Usage:
    python mini-agent.py "How many Python files are in this project?"
    python mini-agent.py "Search for TODO comments in all .py files"

Requirements:
    pip install requests    (or just Python stdlib urllib)
    Ollama running:         ollama serve
    Model pulled:           ollama pull qwen2.5:7b

How it works:
    1. You give it a task
    2. Agent thinks → picks a tool → runs it → sees result → thinks again
    3. Repeats until it has an answer (max 5 loops)
    4. Shows you every Thought → Action → Observation step
"""

import subprocess, json, sys, os, re

# Fix Windows GBK encoding for emoji output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass  # stdout is piped/redirected, emoji rendering is best-effort

# ── Config ──────────────────────────────────────────────────
MODEL = os.environ.get("CYBERDECK_MODEL", "qwen2.5:7b")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MAX_STEPS = 5

TOOLS = """
You have these tools:

1. file_read(path) — Read a file. Returns its contents (first 100 lines).
2. file_search(pattern) — Search file contents for a regex pattern. Returns matching lines with file names.
   Example: file_search("TODO|FIXME") finds all TODOs in the project.
3. terminal(command) — Run a shell command. Use for ls, grep, wc, find, cat, etc.
   Example: terminal("ls *.py") lists Python files.
4. web_fetch(url) — Fetch a URL. Returns the first 500 characters.

Rules:
- Use tools to gather information. Don't guess.
- After each tool result, think: "What do I know now? What do I still need?"
- When you have a complete answer, output: FINAL: <your answer>
- Never output FINAL until you have all the information.
- If a tool fails, try a different approach.
"""

# ── Tools ───────────────────────────────────────────────────

def file_read(path):
    """Read a file, return first 100 lines."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()[:100]
        return ''.join(lines) if lines else "(empty file)"
    except FileNotFoundError:
        return f"ERROR: File not found: {path}"
    except Exception as e:
        return f"ERROR: {e}"

def file_search(pattern):
    """Search all .py/.js/.ts/.md/.txt files for a regex pattern."""
    results = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden and venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules' and d != '__pycache__']
        for f in files:
            if f.endswith(('.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml', '.html', '.css')):
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fh:
                        for i, line in enumerate(fh, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                results.append(f"{os.path.join(root, f)}:{i}: {line.strip()[:120]}")
                except:
                    pass
    if not results:
        return f"No matches for '{pattern}'"
    return '\n'.join(results[:30]) + (f"\n... and {len(results)-30} more" if len(results) > 30 else "")

# Commands that are never allowed (prevent model from running destructive ops)
DENY_LIST = ["rm -rf", "del /F", "rd /S", "format ", "shutdown", "mkfs", "dd if=", ":(){ :|:& };:"]

def terminal_cmd(command):
    """Run a read-only shell command. Destructive commands are blocked."""
    cmd_lower = command.lower()
    for deny in DENY_LIST:
        if deny.lower() in cmd_lower:
            return f"ERROR: Blocked dangerous command (matched: '{deny}')"
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, encoding='utf-8', errors='replace', timeout=15
        )
        parts = []
        if result.stdout.strip():
            parts.append(f"stdout:\n{result.stdout.strip()[:1800]}")
        if result.stderr.strip():
            parts.append(f"stderr:\n{result.stderr.strip()[:1800]}")
        return "\n".join(parts) if parts else "(no output)"
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out (15s)"
    except Exception as e:
        return f"ERROR: {e}"

def web_fetch(url):
    """Fetch a URL, return first 500 chars."""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode('utf-8', errors='ignore')[:500]
    except Exception as e:
        return f"ERROR: {e}"

# ── Agent Loop ──────────────────────────────────────────────

def call_ollama(prompt):
    """Send prompt to Ollama, get response."""
    import urllib.request
    data = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=data,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            text = result.get("response", "") or result.get("message", "") or json.dumps(result)
            if not text.strip():
                raise ValueError(f"empty response from Ollama (keys: {list(result.keys())})")
            return text
    except Exception as e:
        print(f"\n❌ Cannot reach Ollama at {OLLAMA_URL}")
        print(f"   Error: {e}")
        print(f"   Fix: ollama serve           (start Ollama)")
        print(f"        ollama pull {MODEL}    (pull model)")
        print(f"   Or set: CYBERDECK_MODEL=... OLLAMA_URL=...")
        sys.exit(1)

def run_agent(task):
    """Main ReAct loop."""
    history = f"{TOOLS}\n\nUser's task: {task}\n\n"
    history += "Think step by step. Use tools when you need information. "
    history += "Output format:\n  THOUGHT: <your reasoning>\n  ACTION: tool_name(args)\n"
    history += "Or when done:\n  FINAL: <your answer>\n\n"

    for step in range(1, MAX_STEPS + 1):
        print(f"\n{'─'*50}")
        print(f"  STEP {step}/{MAX_STEPS}")

        response = call_ollama(history)

        # Parse response
        thought_match = re.search(r'THOUGHT:\s*(.+?)(?=\n\s*(?:ACTION|FINAL|$)|\Z)', response, re.DOTALL)
        action_match = re.search(r'ACTION:\s*(\w+)\((.+)\)', response)
        final_match = re.search(r'FINAL:\s*(.+)', response, re.DOTALL)

        if thought_match:
            print(f"  🤔 {thought_match.group(1).strip()[:200]}")

        if final_match:
            answer = final_match.group(1).strip()
            print(f"\n{'='*50}")
            print(f"  💬 {answer}")
            print(f"{'='*50}")
            return answer

        if action_match:
            tool = action_match.group(1).strip()
            arg = action_match.group(2).strip()
            # Only strip matching quote pairs, not internal quotes
            if (arg.startswith('"') and arg.endswith('"')) or \
               (arg.startswith("'") and arg.endswith("'")):
                arg = arg[1:-1]
            print(f"  🔧 {tool}({arg[:80]})")

            # Execute tool
            if tool == 'file_read':
                result = file_read(arg)
            elif tool == 'file_search':
                result = file_search(arg)
            elif tool == 'terminal':
                result = terminal_cmd(arg)
            elif tool == 'web_fetch':
                result = web_fetch(arg)
            else:
                result = f"Unknown tool: {tool}. Available: file_read, file_search, terminal, web_fetch"

            preview = result[:300].replace('\n', '\n  ')
            print(f"  👀 {preview}{'...' if len(result) > 300 else ''}")
            history += f"\nACTION: {tool}({arg})\nRESULT: {result}\n"
        else:
            # No action found — feed the raw response back
            history += f"\nASSISTANT: {response}\n"
            print(f"  ⚠️  No structured action found. Retrying...")
            # Help the model: remind it of the format
            history += "\nRemember: output THOUGHT + ACTION, or FINAL when done.\n"

    print(f"\n⚠️  Reached max {MAX_STEPS} steps without FINAL answer.")
    return None

# ── Main ────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mini-agent.py \"your task here\"")
        print("Example: python mini-agent.py \"How many Python files in this project?\"")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    print(f"\n  ╔══════════════════════════════════════════╗")
    print(f"  ║   CYBERDECK mini-agent (ReAct)          ║")
    print(f"  ╚══════════════════════════════════════════╝")
    print(f"  Task: {task}")
    print(f"  Model: {MODEL}")

    run_agent(task)
