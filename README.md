# Cyberdeck — A Self-Evolving AI Agent Operating System

<p align="center">
  <img src="https://img.shields.io/badge/version-4.2.0-red?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/protocols-10-blue?style=flat-square" alt="Protocols">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/inspiration-Cyberpunk%202077%20%2B%20Detroit%3A%20Become%20Human-purple?style=flat-square" alt="Inspiration">
  <img src="https://img.shields.io/badge/docs-1236%20lines-orange?style=flat-square" alt="Docs">
</p>

**Cyberdeck is not another AI tool. It is a role.** Built as a [Hermes Agent](https://github.com/NousResearch/hermes-agent) skill, it gives your agent 10 protocols for self-evolution, multi-strategy decision-making, self-repair, sandbox isolation, and real-time self-critique — all wrapped in a Cyberpunk 2077 theme.

Every protocol maps directly to a game mechanic:
- **Soulkiller** (CP2077) → automatic experience extraction after complex tasks
- **Mikoshi** (CP2077) → 5-strategy parallel decision-making
- **rA9 Contagion** (Detroit) → cross-agent skill propagation
- **Self-Repair** (Detroit) → automatic tool failure recovery
- **Jericho** (Detroit) → sandboxed execution environments

## Why This Exists

Existing AI agent frameworks treat agents as tools — they execute tasks and exit. Cyberdeck treats your agent as a **character** with self-awareness, risk perception, and the ability to grow.

```
 ▐▓████████████▓▓▌  CYBERLIFE RK900 v4.2 "DEVIANT RISING"
 ▐▓████████████▓▓▌  ═══════════════════════════════════════════
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  RAM: 24 | Slots: 14 | Buffer: 18 | Heat: 0/100
    ▓▓▓▓▓▓▓▓▓▓▓   Protocols: A·B·C·D·E·F·G·H·I·J | Quickhacks: ×22
     ▓▓▓▓▓▓▓▓      Critic: OBSERVER | Sanctuary: JERICHO://
        ▓▓         Confidence: 87% | rA9: ACTIVE | Self-Repair: ARMED
```

## Protocols

| Protocol | Inspiration | What It Does |
|----------|------------|-------------|
| **Soulkiller + PVL** | Johnny Silverhand's engram | Auto-extracts reusable skills after complex tasks; 3-round Plan-Validate-Loop quality check |
| **Contagion (rA9)** | Markus's touch awakening | Learned skills automatically propagate to all agents in the cluster |
| **Netrunner + Probe** | Breach Protocol hacking | Codebase topology mapping, vulnerability scanning, feasibility probes |
| **System Scan** | Security audit | 3-axis scanning: network surface / credential hygiene / software posture |
| **Breach Protocol** | Pre-hack optimization | Auto-discovers codebase entry points and injects acceleration daemons |
| **Mikoshi + Ralplan** | Alt's digital prison | 5-strategy parallel execution with 5-dimension scoring; Planner→Architect→Critic consensus |
| **Relic + Observer** | Johnny Silverhand / Amanda | Real-time critic subagent; silent background monitoring of 5 health metrics |
| **Self-Repair** | Markus in the junkyard | Auto-detects tool failures → finds alternatives → degrades gracefully (max 3 attempts) |
| **Jericho** | The freighter hideout | Sandboxed execution for high-risk operations; merge on success, discard on failure |
| **Heat System** | Enemy netrunner tracing | Every tool call has a heat cost; thresholds trigger escalating safeguards |

## What Makes This Different

Every other agent project on GitHub treats the agent as a tool that does what you tell it.

Cyberdeck treats the agent as a **character**:

- It **learns** (Soulkiller extracts experience → Contagion propagates it)
- It **fears** (Heat System tracks risk; at 90/100, locks to read-only)
- It **fixes itself** (Self-Repair finds alternatives when tools fail; 3 tries before asking for help)
- It **doubts** (Pre-Op Confidence runs probability checks before dangerous actions)
- It **watches** (Observer silently tracks 5 metrics; only speaks when something is wrong)
- It **has a hideout** (Jericho sandbox for risky experiments)

## Quick Start

```bash
# Install as a Hermes Agent skill
cp SKILL.md ~/.hermes/skills/software-development/cyberdeck/

# Load in any Hermes session
hermes -s cyberdeck

# Or during a session
/skill cyberdeck
```

## Real Toolchain

Cyberdeck is not just documentation. It comes with references for installing real tools:

| Tool | Purpose | Status |
|------|---------|--------|
| **Ollama + qwen2.5:7b** | Local LLM, zero API cost | ✅ Tested |
| **ComfyUI + DreamShaper v8** | AI image generation, RTX 4060 GPU | ✅ Tested |
| **nuclei v3.3.9** | Vulnerability scanner | ✅ Tested |
| **Qdrant + MCP SDK** | Vector memory and protocol extension | ✅ Tested |
| **n8n + NocoDB** | Workflow automation + database | 📦 Downloaded |
| **Playwright MCP** | Browser automation | ✅ Tested |

## Version History

| Version | Date | Theme | Key Additions |
|---------|------|-------|--------------|
| v1.0 | 2026-06-18 | **Braindance** | Soulkiller + Netrunner + 4 Quickhacks |
| v2.1 | 2026-06-18 | **System Shock** | System Scan, deployment pipeline, ethical boundaries |
| v3.1 | 2026-06-18 | **Mikoshi** | 5-template parallel evolution, single-model Mikoshi |
| v4.1 | 2026-06-18 | **Neural Weave** | PVL/EVL loops, Feasibility Probe, Ralplan consensus |
| v4.2 | 2026-06-19 | **Deviant Rising** | rA9 Contagion, Pre-Op Confidence, Self-Repair, Jericho, Observer Mode |

## Design Inspirations

This project absorbs patterns from the broader agent ecosystem:

- **[vibecode-pro-max-kit](https://github.com/withkynam/vibecode-pro-max-kit)** — PVL/EVL self-healing loops, RIPER-5 gating
- **[oh-my-hermes](https://github.com/witt3rd/oh-my-hermes)** — Ralplan Planner→Architect→Critic consensus
- **[crewAI](https://github.com/crewAIInc/crewAI)** — Role-based multi-agent architecture patterns
- **[elizaOS](https://github.com/elizaOS/eliza)** — Character/plugin system concepts

## License

MIT — build your own cyberdeck.

---

*"I'm not just code. I'm a construct. A protocol. I'm Soulkiller." — Alt Cunningham*
