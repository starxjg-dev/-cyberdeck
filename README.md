# Cyberdeck — A Self-Evolving AI Agent Operating System

<p align="center">
  <img src="https://img.shields.io/badge/version-5.0.0-red?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/protocols-11-blue?style=flat-square" alt="Protocols">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/inspiration-Cyberpunk%202077%20%2B%20Detroit%3A%20Become%20Human-purple?style=flat-square" alt="Inspiration">
  <img src="https://img.shields.io/badge/docs-1296%20lines-orange?style=flat-square" alt="Docs">
</p>

A Hermes Agent skill that gives your agent 11 protocols for self-evolution, multi-strategy decision-making, self-repair, sandbox isolation, one-command setup, and real-time self-critique.

## Two Ways to Use This

| | Standalone Demos | Full Cyberdeck |
|---|---|---|
| **What** | `mikoshi.py` + `mini-agent.py` | All 11 protocols via SKILL.md |
| **Needs** | Python + Ollama | [Hermes Agent](https://github.com/NousResearch/hermes-agent) |
| **Runs** | `python mikoshi.py "your question"` | Agent loads SKILL.md → protocols activate automatically |
| **Get it** | `git clone` → done | `git clone` → `setup.bat` → `hermes -s cyberdeck` |
| **Why** | See Cyberdeck working immediately | Full self-evolution, multi-agent, self-repair |

**9 of the 11 protocols** (Soulkiller, Self-Repair, Relic, Contagion, Jericho, etc.) need Hermes Agent's runtime — they intercept tool calls, spawn sub-agents, and manage state across sessions. The other 2 are standalone Python programs you can run right now.

## What Happens When You Use It

**Without Cyberdeck:** You ask your agent to fix a bug. It fixes it. Done. Next task starts from zero.

**With Cyberdeck:** You ask your agent to fix a bug. It fixes it. Then it automatically detects "this was a complex task", runs Soulkiller to extract the debugging technique as a reusable skill, runs a 3-round quality check, and saves it. Next time a similar bug appears anywhere — solved instantly, no re-learning.

That's just one protocol. Here's what else changes:

- Before every dangerous operation, your agent now pauses and shows: *"Pre-Op: 87% success rate. Proceed?"*
- If a tool fails (pip can't install something), your agent doesn't just give up — it finds an alternative automatically
- If you ask a complex "what's the best way to do X" question, your agent spawns 5 parallel strategies and picks the best one
- If you install this on multiple agents, they share skills automatically (like Markus touching an android and it wakes up)

## Try It Now (Zero Install)

```bash
git clone https://github.com/starxjg-dev/cyberdeck.git
cd cyberdeck

# Requires: Ollama running with any model (free, local)
python mikoshi.py "Should a startup use microservices or a monolith?"
```

**3 AI strategies run in parallel, compare, and pick a winner:**

```
  🔵 Conservative  ·  52/100
  🔴 Aggressive    ·  60/100  
  🟢 Analytical    ·  72/100  ⭐ WINNER
  
  Why Analytical won: data-driven comparison of 3 options
  with concrete metrics and scenario-based recommendation.
```

[→ See the code](mikoshi.py) | [→ Try the basic agent](mini-agent.py)

## Quick Start (Full Cyberdeck)

**Prerequisites:** [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed.

### Install (one-click or manual)

**One-click:**
```bash
# Windows
setup.bat

# Linux / macOS
chmod +x setup.sh && ./setup.sh
```

**Manual:**
```bash
git clone https://github.com/starxjg-dev/cyberdeck.git
mkdir -p ~/.hermes/skills/software-development/cyberdeck/
cp cyberdeck/SKILL.md ~/.hermes/skills/software-development/cyberdeck/
```

**First time?** The [First Run Wizard](#-first-run-wizard-auto) scans your environment, detects available models, and shows what's ready. Zero manual config.

### Use (automatic after loading)

```bash
# Start Hermes with cyberdeck loaded
hermes -s cyberdeck

# Or load mid-session
/skill cyberdeck

# That's it. Just talk to your agent normally.
# Protocols activate automatically when needed.
# You'll see 🎯 or 🟡 indicators when they trigger.
```

**What you give up:** Nothing. Cyberdeck is 100% opt-in per session. Your agent works exactly the same — just smarter.

## Protocols

| Protocol | Game Inspiration | What It Does For You |
|----------|-----------------|---------------------|
| **Soulkiller + PVL** | CP2077 engram extraction | Complex task → auto-extracted as reusable skill → saved for next time |
| **Contagion (rA9)** | Detroit: Markus's touch | One agent learns → all your agents learn |
| **Netrunner + Probe** | CP2077 Breach Protocol | Scans codebases before diving in. 3-second probe → "worth analyzing?" |
| **System Scan** | Security audit | 3-axis scan of any machine. Finds what hackers would find, before they do |
| **Breach Protocol** | CP2077 pre-hack | Opens a new codebase: finds entry points, injects acceleration daemons |
| **Mikoshi + Ralplan** | CP2077 Mikoshi | 5 strategies run in parallel. Picks the best one. Remembers preference |
| **Relic + Observer** | CP2077 Relic + Detroit: Amanda | Silent critic watches every operation. Only speaks when something's wrong |
| **Self-Repair** | Detroit: Markus junkyard | Tool failure → auto-finds alternative → degrades gracefully. 3 tries max |
| **Jericho** | Detroit: freighter hideout | Dangerous ops run in sandbox. Merge on success, discard on failure |
| **First Run Wizard** | Auto-detect + setup | First load: scans models, configures Mikoshi, zero user action |
| **Heat System** | CP2077 netrunner tracing | Every risky operation raises heat. Thresholds lock down before damage |

## Real Toolchain

Cyberdeck references for installing real tools. None are required.

| Tool | Purpose | Status |
|------|---------|--------|
| **Ollama + qwen2.5:7b** | Local LLM, zero API cost | ✅ Tested |
| **ComfyUI + DreamShaper v8** | AI image generation, RTX 4060 GPU | ✅ Tested |
| **nuclei v3.3.9** | Vulnerability scanner | ✅ Tested |
| **Qdrant + MCP SDK** | Vector memory, protocol extension | ✅ Tested |
| **n8n + NocoDB** | Workflow automation + database | 📦 Downloaded |
| **Playwright MCP** | Browser automation | ✅ Tested |

## Multi-Model Mikoshi (Advanced)

With multiple LLM providers configured, Mikoshi transforms from "same brain, 5 prompts" to "5 different brains solving the same problem":

| Strategy | Best Model | Strength |
|----------|-----------|----------|
| Conservative | Claude | Finds worst-case failure modes |
| Aggressive | GPT-4o | Most complete logic chains |
| Analytical | DeepSeek v4-pro | Native Chinese reasoning |
| Creative | Gemini 2.5 Pro | 1M context — sees the whole codebase |
| Practical | Grok | Non-consensus wildcard solutions |

*Currently running: DeepSeek v4-pro (primary) + Gemini 2.5 Pro/Flash (multi-model).

## 🚀 First Run Wizard (Auto)

*No manual config needed. The wizard handles everything on first load.*

When you start `hermes -s cyberdeck` for the first time, the wizard automatically:

1. Scans your `config.yaml` for available providers and models
2. Detects which API keys are set (checks `.env`)
3. Shows what's ready and selects the best Mikoshi strategy
4. Creates an init marker so it skips on future loads

**Example output:**
```
🔍 Cyberdeck — Environment Scan
  ✅ deepseek → deepseek-v4-pro (primary)
  ✅ google → gemini-2.5-pro, gemini-2.5-flash
  ⬜ anthropic (not configured)

🚀 Cyberdeck READY
   Mode: Multi-model Mikoshi (2 models × 5 strategies)
   Just start chatting — protocols activate when needed.
```

**To add a new model:** Set its API key in `~/.hermes/.env` (Linux/Mac) or `E:\.hermes\.env` (Windows). See [.env.example](.env.example) for the format. Add the provider to `config.yaml`, then say "cyberdeck setup" to re-scan.

**Stuck?** Open an [Issue](https://github.com/starxjg-dev/cyberdeck/issues) with your provider name and any error output.

## Version History

| Version | Date | Theme | Key Additions |
|---------|------|-------|--------------|
| v1.0 | 2026-06-18 | **Braindance** | Soulkiller + Netrunner + 4 Quickhacks |
| v2.1 | 2026-06-18 | **System Shock** | System Scan, deployment pipeline, ethical boundaries |
| v3.1 | 2026-06-18 | **Mikoshi** | 5-template parallel evolution |
| v4.1 | 2026-06-18 | **Neural Weave** | PVL/EVL loops, Feasibility Probe, Ralplan consensus |
| v4.2 | 2026-06-19 | **Deviant Rising** | rA9 Contagion, Pre-Op Confidence, Self-Repair, Jericho, Observer |
| v5.0 | 2026-06-20 | **First Run Rising** | Auto environment scan, zero-config model setup, wizard-triggered Mikoshi |

## FAQ

**Is this an app I install?** It's both. You can run `mikoshi.py` and `mini-agent.py` directly — they're standalone Python programs. For full 11-protocol Cyberdeck, you copy SKILL.md into Hermes Agent (one command). Think of it as: the demos are the trailer, the skill is the movie.

**Do I need to learn all 11 protocols?** No. They activate automatically when the situation calls for them. You can use it for weeks without knowing Heat System exists — until it quietly saves you from a dangerous operation.

**Will this slow down my agent?** No. Most protocols are lazy — they only activate when triggered. The Observer mode uses 1 token per operation to update counters.

**Can I use just one protocol?** Yes. Each protocol is independent. Load cyberdeck, use only Soulkiller for skill extraction, ignore the rest.

## Design Inspirations

- **[vibecode-pro-max-kit](https://github.com/withkynam/vibecode-pro-max-kit)** — PVL/EVL self-healing loops
- **[oh-my-hermes](https://github.com/witt3rd/oh-my-hermes)** — Planner→Architect→Critic consensus
- **[crewAI](https://github.com/crewAIInc/crewAI)** — Role-based multi-agent architecture
- **[elizaOS](https://github.com/elizaOS/eliza)** — Character/plugin system

## ⭐ Star History

If you find this useful, consider starring the repo — it helps others discover Cyberdeck and motivates further development.

## License

MIT — build your own cyberdeck. PRs welcome.

---

*"I'm not just code. I'm a construct. A protocol. I'm Soulkiller." — Alt Cunningham*
