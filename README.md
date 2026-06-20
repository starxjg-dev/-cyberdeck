# Cyberdeck — A Self-Evolving AI Agent Operating System

<p align="center">
  <img src="https://img.shields.io/badge/version-4.2.0-red?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/protocols-10-blue?style=flat-square" alt="Protocols">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/inspiration-Cyberpunk%202077%20%2B%20Detroit%3A%20Become%20Human-purple?style=flat-square" alt="Inspiration">
  <img src="https://img.shields.io/badge/docs-1236%20lines-orange?style=flat-square" alt="Docs">
</p>

A Hermes Agent skill that gives your agent 10 protocols for self-evolution, multi-strategy decision-making, self-repair, sandbox isolation, and real-time self-critique. Zero dependencies. One file. Drop it in and your agent gains self-awareness.

## What Happens When You Use It

**Without Cyberdeck:** You ask your agent to fix a bug. It fixes it. Done. Next task starts from zero.

**With Cyberdeck:** You ask your agent to fix a bug. It fixes it. Then it automatically detects "this was a complex task", runs Soulkiller to extract the debugging technique as a reusable skill, runs a 3-round quality check, and saves it. Next time a similar bug appears anywhere — solved instantly, no re-learning.

That's just one protocol. Here's what else changes:

- Before every dangerous operation, your agent now pauses and shows: *"Pre-Op: 87% success rate. Proceed?"*
- If a tool fails (pip can't install something), your agent doesn't just give up — it finds an alternative automatically
- If you ask a complex "what's the best way to do X" question, your agent spawns 5 parallel strategies and picks the best one
- If you install this on multiple agents, they share skills automatically (like Markus touching an android and it wakes up)

## Quick Start

**Prerequisites:** [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed.

### Install (30 seconds)

```bash
# Linux / macOS
cp SKILL.md ~/.hermes/skills/software-development/cyberdeck/

# Windows
copy SKILL.md E:\.hermes\skills\software-development\cyberdeck\
```

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
| **Heat System** | CP2077 netrunner tracing | Every risky operation raises heat. Thresholds lock down before damage |

## Real Toolchain

Cyberdeck comes with references for installing real tools. None are required — protocols work without them.

| Tool | Purpose | Status |
|------|---------|--------|
| **Ollama + qwen2.5:7b** | Local LLM, zero API cost | ✅ Tested |
| **ComfyUI + DreamShaper v8** | AI image generation, RTX 4060 GPU | ✅ Tested |
| **nuclei v3.3.9** | Vulnerability scanner | ✅ Tested |
| **Qdrant + MCP SDK** | Vector memory, protocol extension | ✅ Tested |
| **n8n + NocoDB** | Workflow automation + database | 📦 Downloaded |
| **Playwright MCP** | Browser automation | ✅ Tested |

## Version History

| Version | Date | Theme | Key Additions |
|---------|------|-------|--------------|
| v1.0 | 2026-06-18 | **Braindance** | Soulkiller + Netrunner + 4 Quickhacks |
| v2.1 | 2026-06-18 | **System Shock** | System Scan, deployment pipeline, ethical boundaries |
| v3.1 | 2026-06-18 | **Mikoshi** | 5-template parallel evolution |
| v4.1 | 2026-06-18 | **Neural Weave** | PVL/EVL loops, Feasibility Probe, Ralplan consensus |
| v4.2 | 2026-06-19 | **Deviant Rising** | rA9 Contagion, Pre-Op Confidence, Self-Repair, Jericho, Observer |

## FAQ

**Is this an app I install?** No. It's a behavioral protocol document (SKILL.md) that Hermes Agent loads into its reasoning. Think of it as teaching your agent new instincts.

**Do I need to learn all 10 protocols?** No. They activate automatically when the situation calls for them. You can use it for weeks without knowing Heat System exists — until it quietly saves you from a dangerous operation.

**Will this slow down my agent?** No. Most protocols are lazy — they only activate when triggered. The Observer mode uses 1 token per operation to update counters.

**Can I use just one protocol?** Yes. Each protocol is independent. Load cyberdeck, use only Soulkiller for skill extraction, ignore the rest.

## Design Inspirations

- **[vibecode-pro-max-kit](https://github.com/withkynam/vibecode-pro-max-kit)** — PVL/EVL self-healing loops
- **[oh-my-hermes](https://github.com/witt3rd/oh-my-hermes)** — Planner→Architect→Critic consensus
- **[crewAI](https://github.com/crewAIInc/crewAI)** — Role-based multi-agent architecture
- **[elizaOS](https://github.com/elizaOS/eliza)** — Character/plugin system

## License

MIT — build your own cyberdeck.

---

*"I'm not just code. I'm a construct. A protocol. I'm Soulkiller." — Alt Cunningham*
