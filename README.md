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

### 配置模型（新手 5 分钟接你自己的模型）

**改两个文件。**

#### 1. `.env` — 填 API Key

复制 `.env.example` 为 `.env`，填上你要用的 provider 的 key：

```bash
# 选一个填
DEEPSEEK_API_KEY=sk-xxx        # DeepSeek
OPENAI_API_KEY=sk-xxx          # OpenAI / 第三方兼容
GEMINI_API_KEY=xxx             # Gemini
# Ollama 本地无需 key
```

#### 2. `config.yaml` — 改模型名（~10 处）

找到你的 profile 配置：`~/.hermes/profiles/cyberdeck/config.yaml`

**必须改的字段：**

| 位置 | 字段 | 示例值 |
|------|------|--------|
| `model.default` | 主模型 | `gpt-4o` / `qwen2.5:7b` / `gemini-2.5-pro` |
| `model.provider` | 主 provider | `openai` / `ollama` / `gemini` |
| `auxiliary.approval` | 审批模型 | 同上 |
| `auxiliary.compression` | 压缩模型 | 同上（flash 模型更省钱） |
| `auxiliary.curator` | 管理模型 | 同上 |
| `auxiliary.delegation` | 子代理模型 | 同上（建议用强模型） |
| `auxiliary.kanban_decomposer` | 看板模型 | 同上 |
| `auxiliary.skills_hub` | 技能模型 | 同上 |
| `auxiliary.title_generation` | 标题模型 | 同上 |
| `auxiliary.triage_specifier` | 分流模型 | 同上 |
| `auxiliary.vision` | 视觉模型 | 同上 |
| `auxiliary.web_extract` | 网页模型 | 同上 |

**快速模板（找到对应段，整块替换）：**

```yaml
# --- OpenAI ---
model:
  default: gpt-4o
  provider: openai
auxiliary:
  approval:      {api_key: '', base_url: '', extra_body: {}, model: gpt-4o-mini, provider: openai, timeout: 30}
  compression:   {api_key: '', base_url: '', extra_body: {}, model: gpt-4o-mini, provider: openai, timeout: 120}
  # ... 其余 auxiliary 全部改为 provider: openai, model: gpt-4o-mini

# --- Ollama 本地（免费）---
model:
  default: qwen2.5:7b
  provider: ollama
# auxiliary 全部用 provider: ollama, model: qwen2.5:7b（或 gemma3:4b 省资源）

# --- Gemini ---
model:
  default: gemini-2.5-pro
  provider: gemini
# auxiliary 全部用 provider: gemini, model: gemini-2.5-flash

# --- DeepSeek（默认）---
model:
  default: deepseek-v4-pro
  provider: deepseek
# auxiliary 全部用 provider: deepseek, model: deepseek-v4-flash
```

3. 验证：
```bash
hermes --profile cyberdeck chat -q "你好，用中文回复"
```

搞不定？提 Issue，附上你的 provider 和报错信息。

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

## ⭐ Star History

If you find this useful, consider starring the repo — it helps others discover Cyberdeck and motivates further development.

## License

MIT — build your own cyberdeck. PRs welcome.

---

*"I'm not just code. I'm a construct. A protocol. I'm Soulkiller." — Alt Cunningham*
