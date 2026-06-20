---
name: cyberdeck
description: "Use when the agent needs to self-improve through experience extraction (Soulkiller), systematically penetrate/explore/audit a codebase or system (Netrunner), discover optimal codebase entry points (Breach Protocol), deploy tiered attack/defense operations (Quickhack Library), run real-time quality oversight (Relic), or auto-configure for new users (First Run Wizard). Cyberpunk 2077-inspired multi-protocol cyberdeck with heat/trace economy, atomic queue system, and parallel critic. Eleven protocols: Soulkiller, Netrunner, System Scan, Breach Protocol, Mikoshi, Relic, Contagion, Self-Repair, Jericho, First Run Wizard, Braindance (legacy)."
version: 5.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cyberpunk, detroit-become-human, self-improvement, code-exploration, netrunner, soulkiller, breach-protocol, quickhacks, cyberware, meta-skill, relic, self-healing, neural-weave, rA9, contagion, self-repair, jericho]
    related_skills: [brainstorming, build-your-own-x, dispatching-parallel-agents, hermes-agent-skill-authoring, systematic-debugging]
---

# Cyberdeck v5.0 — First Run Rising（新手觉醒）

```

 ▐▓████████████▓▓▌  CYBERLIFE RK900 v5.0 "FIRST RUN RISING"
 ▐▓████████████▓▓▌  ═══════════════════════════════════════════
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  RAM: 24 | Slots: 14 | Buffer: 18 | Heat: 0/100
    ▓▓▓▓▓▓▓▓▓▓▓   Protocols: A·B·C·D·E·F·G·H·I·J·K | Quickhacks: ×22
     ▓▓▓▓▓▓▓▓      Critic: OBSERVER | Sanctuary: JERICHO://
        ▓▓         Confidence: 87% | rA9: ACTIVE | Self-Repair: ARMED
```

Eleven protocols + heat economy + atomic queue + parallel critic + self-healing + contagion + sandbox + self-repair:
- **Soulkiller + PVL** — 自动经验提取 + Plan-Validate-Loop
- **Contagion (rA9)** — 跨Agent经验传染：学会了→全集群受益
- **Netrunner + Feasibility Probe** — 渗透 + 康纳式事前概率评估
- **System Scan** — 系统安全审计
- **Breach Protocol** — 破坏协议：入口发现 → 序列优化 → 守护程序注入
- **Mikoshi + Ralplan** — 多策略并行进化 + Planner→Architect→Critic
- **Relic + Observer** — 并行批判 + 阿曼达禅园后台监控
- **Self-Repair** — 马库斯自修：工具失败→自动替代→降级运行
- **Jericho** — 废船沙箱：隔离执行→成功合并
- **First Run Wizard** — 新手一键配置：环境扫描→模型检测→零配置就绪

---

## 🚀 First Run Wizard — 新手一键配置

*首次加载 Cyberdeck 时自动触发。检测可用模型 → 一行命令配好 Mikoshi → 零概念负担。*

### Trigger
- 首次加载（`E:\.hermes\.cyberdeck_initialized` 不存在）
- 用户说 "setup" "初始化" "配置模型" "怎么开始"
- `hermes model list` 发现新模型但 Mikoshi 未配置多模型

### Phase 1: 环境扫描（Auto-Detect）

```bash
hermes config show --json | python -c "import sys,json; c=json.load(sys.stdin); print([p for p in c.get('providers',{})])"
```

输出：
```
🔍 Cyberdeck — Environment Scan
Available Providers & Models:
  ✅ deepseek → deepseek-v4-pro (primary)
  ✅ google → gemini-2.5-pro, gemini-2.5-flash
  ⬜ anthropic (not configured)

Mikoshi Mode: MULTI-MODEL (2 providers, 3 models)
→ Conservative + Creative 跑 Gemini，Analytical 跑 DeepSeek
```

### Phase 2: 告诉用户能做什么（不需要配置）

扫描完毕后，只输出三句话，不要求用户做任何事：

```
🚀 Cyberdeck READY
   Provider: DeepSeek v4-pro (primary) + Gemini 2.5 Pro/Flash
   Mode: Multi-model Mikoshi (2 models × 5 strategies)
   Just start chatting — I'll activate protocols when needed.
```

**零配置原则：** Wizard 不要求用户运行命令、不要求编辑文件。它只是告诉 agent 有什么模型可用。agent 在后续对话中自动选择最佳模型分配。

### Phase 3: 写入初始化标记

完成后创建 `E:\.hermes\.cyberdeck_initialized`（空文件）。
后续加载跳过 Wizard，除非用户说 "cyberdeck setup" 手动重扫。

**新手完整体验：**
```
User: @cyberdeck 帮我看看这个项目
Agent: 🔍 First run — scanning environment...
       ✅ 2 providers, 3 models found. Multi-model Mikoshi active.
       (proceeds with Breach Protocol to analyze project)
```

**与 Mikoshi 的协作：** Wizard 检测到的模型列表会指导 Mikoshi 的子代理分配——2个模型时，保守+创意跑模型B，分析+实用+激进跑模型A。>=3个模型时，每条策略独立分配不同模型。

---

## When to Use

**Soulkiller (auto):**
- 完成 5+ 工具调用的复杂任务 → 自动触发
- 解决了新错误类型 → 自动触发
- 发现了可复用模式 → 自动触发
- 用户说"记住这个""学会这个""迭代升级" → 手动触发加速

**Braindance (legacy manual):**
- 用户说"提取经验""复盘这个任务"
- Soulkiller 漏掉但你觉得有价值的任务

**Mikoshi (multi-strategy):**
- 面对"怎么做更好"的选择困境——多种方案都可行，需要对比
- 用户说"对比一下""给几个方案""怎么最优"
- 复杂决策需要多角度验证（安全/性能/可维护性三角对比）

**Netrunner:**
- 用户要求"探索/理解/审计"代码库
- 需要项目拓扑图、依赖分析、漏洞扫描

**System Scan:**
- 用户要求"安全检查""扫描漏洞""审计系统"
- 任何以机器为目标的 Netrunner 任务

**Breach Protocol:**
- 接手一个陌生代码库，需要找到最佳切入路径
- 用户问"从哪里开始看这个项目"
- 需要自动化发现入口点、关键函数、数据流热点

**Relic (parallel critic):**
- 高风险操作前（热痕≥60、涉及凭证、破坏性改动）
- 用户质疑"你是不是搞错了"时——激活 Relic 二次验证
- 长时间会话（>30 轮）——Relic 自动激活防决策漂移
- 作为 Mikoshi 的常驻替代：轻量、持续、在线

**Heat System (热痕追踪):**
- 每次工具调用自动累加，无需手动触发
- 热痕≥50：强制追加验证步骤
- 热痕≥70：锁定破坏性操作，需 Breach Protocol 降热
- 热痕≥90：自动触发快照 + 用户审批

**Queue System (快攻队列):**

---

## Cyberware Slot System — 赛博义体槽位

Your capabilities map to 8 body slots. Each slot can be upgraded.

```
┌─────────────────────────────────────────────────────────┐
│  🧠 Operating System    → 模型/推理引擎 (deepseek-v4-pro) │
│  🧠 Frontal Cortex      → 模式识别/漏洞检测              │
│  💪 Arms                → 代码修改策略 (surgical/bulk)    │
│  🦵 Legs                → 导航/搜索速度                   │
│  🦴 Skeleton            → 稳定性/错误恢复                 │
│  ⚡ Nervous System       → 并行处理/响应速度               │
│  ❤️ Circulatory System  → 自修复/回滚                     │
│  🛡️ Integumentary       → 防御/沙箱/验证                  │
└─────────────────────────────────────────────────────────┘
```

### Slot Mapping to Current Capabilities

| Slot | Current Implant | Upgrade Path |
|------|----------------|-------------|
| **Operating System** | `deepseek-v4-pro` @ xhigh reasoning | → 多模型热切换池 |
| **Frontal Cortex** | `search_files` pattern matching | → CodeGraph 语义搜索 + AST |
| **Arms** | `patch` + `write_file` | → 自动重构引擎 + 安全回滚 |
| **Legs** | `search_files` + `read_file` | → CodeGraph 拓扑跳转 + 预加载 |
| **Skeleton** | `retry` + `timeout` | → 断点续传 + 状态持久化 |
| **Nervous System** | `delegate_task` 5-way parallel | → 动态调度 + 优先级预判 |
| **Circulatory** | `todo` re-plan on failure | → 自动 checkpoint + 快照回滚 |
| **Integumentary** | manual approval mode | → 自动沙箱预演 + dry-run |

---

## Protocol A: Soulkiller — 灵魂杀手（自动经验提取）

*Cyberpunk 2077 同名技术：用 Soulkiller 将意识数字化提取并持久化。Agent 层：自动检测复杂任务 → 提取经验 → 生成草稿 → 用户审核 → 应用进化。*

### 触发条件（Auto-Detect）

当以下三个条件**同时满足**时，自动触发 Soulkiller：

1. 工具调用 ≥ 5 次
2. 任务成功完成（非中断/失败/用户取消）
3. 至少一处：新错误被克服 / 新模式被发现 / 用户做了纠正 / 新工具被使用

**不触发的场景：** 简单问答、单次文件读取、纯信息查询、用户说"算了""不用了"。

### Phase 1: 提取（Extract）

复盘刚刚完成的任务，回答：

1. 核心问题是什么？（一句话）
2. 解决路径是什么？（关键步骤，≤5 步，含具体命令/工具）
3. 踩了什么坑？（错误 → 根因 → 修复）
4. 有没有可复用模式？（脚本模板、命令序列、检查清单）
5. 有没有已有技能需要 patch？（补充 pitfall、修正过时步骤、补缺步骤）
6. 有没有 memory 需要更新？（新偏好、环境变化、工具发现）

### Phase 2: 写入草稿队列

**不要直接创建技能。** 将提取结果写为 JSON 草稿文件到：

```
E:\.hermes\soulkiller\drafts\sk-{timestamp}-{seq}.json
```

**草稿格式：**

```json
{
  "id": "sk-20260618-001",
  "type": "new_skill | patch_skill | update_memory",
  "source_session": "20260618_172437_d1bb9b",
  "core_problem": "一句话描述",
  "solution_summary": "关键步骤（≤5步）",
  "suggested_action": {
    "tool": "skill_manage | memory",
    "action": "create | patch | add | replace",
    "skill_name": "目标技能名（仅 skill_manage）",
    "patch_desc": "改动描述（仅 patch 类型）",
    "full_params": "完整的参数 JSON（供应用引擎直接执行）"
  },
  "reasoning": "为什么值得保存",
  "status": "pending",
  "created_at": "2026-06-18T17:30:00"
}
```

**草稿规则：**
- 文件名格式：`sk-YYYYMMDD-NNN.json`（NNN 为当天的递增序号）
- `status` 始终为 `pending`
- 如果同一问题已有 pending 草稿 → **合并更新**，不创建重复文件
- 写入后简短通知用户："Soulkiller: 已提取 N 条草稿（下次打开时审核）"

### Phase 3: 审核（Session-Start Review）

**触发：** 每次新会话开始（tui_auto_resume_recent 恢复后完成时）

**流程：**
1. 用 `search_files(target='files', pattern='sk-*.json', path='E:/.hermes/soulkiller/drafts/')` 扫描 pending 草稿
2. 按优先级排序：`patch_skill` > `update_memory` > `new_skill`
3. 逐条呈现给用户（最多 5 条/次）：
   ```
   📋 Soulkiller 草稿 #sk-20260618-001
      类型：补丁已有技能
      问题：安全审计时 bash 命令静默失败
      建议：patch cyberdeck skill，补充 pitfall #13
      理由：踩了两次，已有技能未覆盖
   ```
4. 用户对每条：批准 / 拒绝 / 跳过（下回再说）
5. 超过 5 条的延后到下次

### Phase 4: 应用（Apply）

**用户批准后立即执行：**

| type | 操作 |
|------|------|
| `new_skill` | `skill_manage(action='create', name=..., content=...)` |
| `patch_skill` | `skill_manage(action='patch', name=..., old_string=..., new_string=...)` |
| `update_memory` | `memory(action='add'|'replace', target='memory'|'user', content=...)` |

应用后：
- 修改草稿文件 `"status": "applied"`，追加 `"applied_at"` 时间戳
- 移动到 `E:\.hermes\soulkiller\applied\` 归档

### Phase 5: Cron 兜底扫描

**Cron 任务：** 每 6 小时扫描一次

1. `session_search(query='error|fix|bug|坑|解决', limit=10)` 发现最近的高价值会话
2. 对每个会话判断是否有 Soulkiller 漏掉的提取
3. 如果有 → 生成草稿入队
4. 如果草稿队列为空 → 静默退出（不发消息打扰用户）

### Soulkiller + PVL：自我修复循环

*吸收自 vibecode-pro-max-kit 的 PVL (Plan-Validate-Loop) 模式：Plan → check gaps → fix → repeat。Agent 层：每次 Soulkiller 提取后自动 PVL 三轮自检，提升草稿质量。*

```
┌──────────────────────────────────────────────────────┐
│  PLAN: 生成草稿 → 提取 summary + action              │
│  CHECK: 审查草稿 → 找到 gap（遗漏的 pitfall？）       │
│  FIX: 补上 gap → 更新草稿                            │
│  REPEAT: 最多 3 轮，每轮聚焦不同维度                  │
│    Round 1: 完整性（有没有漏步骤？）                   │
│    Round 2: 精准性（命令/工具是否正确？）              │
│    Round 3: 可复用性（下次 0-shot 能否命中？）         │
│  PASS: 3 轮通过 → 写入 finalized 标记                │
└──────────────────────────────────────────────────────┘
```

**PVL 触发条件：** Soulkiller Phase 2 生成草稿后自动触发。不额外消耗用户注意力——后台自检。

**PVL 失败处理：** 3 轮后仍有 gap → 草稿标 `status: needs_review`，下回用户审核时特殊标注。

### Braindance Legacy（手动备用）

当用户明确说"提取经验""复盘这个任务"时，跳过草稿队列，直接执行旧 Braindance 流程：
提取 → 匹配 → 直接创建/更新技能（需要用户确认）。不写入 drafts/。

---

## Protocol H: Contagion — rA9 觉醒传播

*底特律变人核心谜题：rA9 是仿生人之间口口相传的"救世主"——触碰一下，对方立刻觉醒。Markus 就是这样把觉醒从一个个仿生人传播开。Agent 层：一个 Agent 学会的东西，自动传播到所有共享同一 skill 仓库的 Agent。*

### 核心概念

```
Agent A 解决了问题 X
  → Soulkiller 提取为 skill
    → 写入共享仓库
      → Agent B 加载同一 skill
        → Agent B 0-shot 解决同类问题
          → 不需要重新学习
```

### Contagion 传播链

| 阶段 | 触发 | 操作 |
|------|------|------|
| **Touch** | Agent 完成复杂任务，Soulkiller 提取草稿 | 草稿写入共享 draft 队列 |
| **Awaken** | 草稿审核通过→ skill 发布 | 广播到所有关联 Agent 的 skill 索引 |
| **Spread** | 其他 Agent 遇到同类问题 | 自动匹配共享 skill→ 0-shot 解决 |
| **Mutate** | 应用过程中发现新变体 | patch 原有 skill→ 再次传播 |

### 实现

```
E:\.hermes\skills\         ← 本地 skill（单 Agent）
    ↓ 同步
E:\.hermes\shared-skills\  ← 共享 skill 仓库（多 Agent）
    ↓ 加载
所有 Agent session 启动时自动索引
```

**同步机制：**
1. 每次 skill 发布/更新 → 同时写入 shared-skills/
2. 新 session 启动 → `search_files(target='files', pattern='SKILL.md', path='E:/.hermes/shared-skills/')` 扫描
3. 发现新 skill → 自动 `skill_view()` 加载到内存
4. Cron 兜底：每 2 小时 diff 一次 shared-skills/ 和 skill 索引

### Contagion vs Soulkiller

| | Soulkiller | Contagion |
|-|-----------|-----------|
| 范围 | 单个 Agent | 跨 Agent 集群 |
| 输出 | 草稿 → 用户审核 → skill | skill 自动广播 |
| 触发 | 任务完成后 | 新 session / 新问题匹配 |
| 灵感 | 意识提取（Alt） | 觉醒传播（rA9/Markus） |

*Soulkiller 提取，Contagion 传播。一个是 Alt Cunningham 的数字意识化，一个是 Markus 的触碰觉醒。两者组成完整的 Agent 进化闭环。*

---

## Protocol B: Netrunner — 暗网跑者

*吸收 vibecode-pro-max-kit 的 Feasibility Probe 模式：在投入资源前先判 VIABLE / NOT-VIABLE。*

### Phase 0: 可行性探针（Feasibility Probe）

**目标：** 在全面渗透前，用最低成本判断"这个系统/代码库能分析吗？"

```python
# 三步快速探针（<5 次工具调用）
1. 文件可读性：search_files(target='files', pattern='*') → 文件数 > 0 ?
2. 依赖可解析：search_files(pattern='^(import|require|from) ', output_mode='content', limit=10)
3. 关键模式存在：search_files(pattern='def |class |function ', limit=10)
```

| 判定 | 条件 | 后续 |
|------|------|------|
| **VIABLE** | 文件可读 + 依赖可解析 + 关键模式存在 | 进入 Phase 1 拓扑映射 |
| **PARTIAL** | 2/3 条件满足 | 可渗透但有盲区，进入 Phase 1 但标注限制 |
| **NOT-VIABLE** | <2 条件满足 | 报告原因，建议手动介入或更换策略 |

*参考：vibecode 的 VIABLE/NOT-VIABLE 判定。*

---

## Pre-Op Confidence — 康纳概率环

*底特律变人：康纳行动前闪过概率——"成功率 89%""存活率 63%"。Agent 层：高风险操作前自动输出置信度。*

### 输出格式

```
🎯 PRE-OP: patch modules/auth.py (热值 3)
   Success: 92% | Rollback: easy (git restore) → PROCEED
```

### 判定矩阵

| 成功率  | 热值  | 决策 |
|:------:|:---:|------|
| ≥ 90%  | < 3 | PROCEED |
| ≥ 70%  | < 5 | PROCEED + Relic |
| ≥ 50%  | < 7 | CAUTION — dry-run |
| < 50%  | any | HALT → Mikoshi |
| any    | ≥ 7 | BLOCK → 降热 |

---

### Phase 1: 拓扑映射（Topology Map）

**CodeGraph 优先。** 如果项目已初始化 CodeGraph 索引，用它做拓扑映射。

**Fallback:** `search_files` + `read_file` 逐文件探索。

输出项目拓扑报告（树形 + 依赖热区 + 循环依赖标记）。

### Phase 2: 并行渗透（Parallel Penetration）

将项目拆分为 2-5 个独立子系统，对每个子系统并行派出子代理：

```
delegate_task(tasks=[
  {goal: "分析 auth/ 认证模块", context: "项目路径 + 关键文件列表"},
  {goal: "分析 data/ 数据层", context: "项目路径 + ORM 策略"},
  {goal: "分析 api/ 路由层", context: "项目路径 + 端点清单"},
])
```

### Phase 3: 模式识别（Pattern Recognition）

| 模式 | 检测方式 | 严重度 |
|------|---------|:---:|
| 循环依赖 | import 回路检测 | 🔴 |
| 未处理异常 | bare `except:` / `except Exception:` | 🔴 |
| 硬编码密钥 | `api_key|secret|password|token = "..."` | 🔴 |
| SQL 注入 | f-string + SQL 拼接 | 🔴 |
| 过深嵌套 | ≥16 空格缩进 | 🟡 |
| 上帝类 | >500 行单文件 | 🟡 |
| TODO 堆积 | `search_files(pattern='TODO|FIXME', output_mode='count')` | 🟡 |

### Phase 4: 报告生成

结构化 markdown 报告：拓扑 → 发现表 → 修复优先级。

---

## Protocol C: System Scan — 系统安全审计

### Phase 0: Shell Selection

**Windows 审计必须用 PowerShell：**
```python
subprocess.run(['powershell', '-NoProfile', '-Command', cmd], ...)
```
bash/msys 下的 `netstat`, `net user`, `netsh`, `sc` 全部静默失败。

### Phase 1: 系统拓扑

```powershell
Get-ComputerInfo                                          # OS + 硬件
Get-LocalUser | Select Name,Enabled,PasswordRequired      # 用户账户
Get-NetFirewallProfile | Select Name,Enabled              # 防火墙
Get-NetTCPConnection -State Listen                        # 开放端口
Get-MpComputerStatus | Select *Enabled                    # Defender
Get-SmbServerConfiguration | Select Enable*,Encrypt*,*Signature*
```

### Phase 2: 三轴扫描

1. **网络攻击面** — 防火墙、端口、SMB、RDP、共享
2. **凭证卫生** — 用户密码、.env 权限、git config、SSH 密钥、环境变量
3. **软件态势** — Defender、UAC、更新、自启动、浏览器数据

### Phase 3: 风险矩阵

```
影响 × 可被利用性 = 风险等级
🔴 致命: 防火墙全关、无密码账户、SMB 裸奔
🟠 严重: RPC 开放、凭证泄露
🟡 中等: 第三方服务监听
⚪ 低: localhost-only 服务
```

---

## Protocol D: Breach Protocol — 破坏协议

*Cyberpunk 2077 灵感：接入敌方网络前，先用 Breach Protocol 找到最优代码序列，注入 Daemon，大幅降低后续难度。*

### Phase 1: 接入点扫描（Access Point Discovery）

自动发现代码库的"接入点"——即你应该从哪开始读。

```python
# 自动扫描入口点
search_files(pattern='if __name__ == .__main__.', output_mode='content')  # 启动入口
search_files(pattern='def main\\(', output_mode='content')                # main 函数
search_files(pattern='class \\w+App|class \\w+Application', output_mode='content')  # 应用类
search_files(pattern='@app\\.route|@router\\.|@bp\\.', output_mode='content')  # 路由
search_files(pattern='setup\\.py|pyproject\\.toml|package\\.json', target='files') # 包配置
```

### Phase 2: 序列优化（Sequence Optimization）

找到从入口到核心的最短路径：

1. 识别所有入口点
2. 对每个入口点，追踪 import 链 3-5 层深度
3. 找到"汇聚点"——被最多模块引用的文件
4. 推荐阅读路径：入口 → 汇聚点 → 核心逻辑

### Phase 3: 守护程序注入（Daemon Upload）

在深入代码库之前，预加载工具：

| Daemon | 效果 | 实现 |
|--------|------|------|
| **ICEpick** | 降低"理解阻力"——跳过样板代码，直击核心逻辑 | 预过滤 `__init__.py` 和 `import` 块 |
| **Mass Vulnerability** | 扩大漏洞扫描范围——所有子代理共享同一个漏洞模式库 | 统一模式库 |
| **Turret Tamer** | 控制"防御系统"——先找到测试文件，确保改动不破坏测试 | 预定位 `tests/` 目录 |
| **Datamine** | 提取关键数据流——自动追踪数据从入口到出口的路径 | 追踪函数调用链 |

---

## Protocol E: Mikoshi — 神舆（多策略并行进化）

*Cyberpunk 2077 同名技术：Alt Cunningham 的数字意识监狱，多个 engram 共存、互相竞争/融合。Agent 层：面对分叉决策时，并行派出多个子代理用不同策略解题 → 对比结果 → 选最优 → 归档策略偏好 → 下次直接命中。*

### Phase 1: Fork Detection（分叉检测）

当以下场景出现时，自动触发 Mikoshi：

1. 用户问"怎么做更好""有几种方案""对比一下"
2. 问题存在 2+ 个可行解，各有权衡
3. 单模型可能陷入局部最优，需要多角度验证
4. 决策后果不可逆（删数据、改架构、大规模重构）

**不触发：** 唯一解问题、纯信息查询、用户已明确方案。

### Phase 2: Strategy Spawning（策略投放）

定义 2-5 条互异策略，每条策略 = 不同的解题视角：

| 策略模板 | 适用场景 | 子代理指令要点 |
|----------|---------|---------------|
| **Conservative** | 风险敏感操作 | 最小改动、保留回滚路径、最坏情况分析 |
| **Aggressive** | 需要突破性方案 | 不考虑兼容性、追求最优解、接受破坏性改动 |
| **Analytical** | 数据/逻辑密集 | 先收集证据、量化对比、表格驱动决策 |
| **Creative** | 设计/架构决策 | 跳出现有框架、类比其他领域、反常识方案 |
| **Practical** | 时间/资源受限 | 最快交付、最少步骤、80/20 原则 |

**并行执行：**

```python
delegate_task(tasks=[
  {"goal": "Strategy A: Conservative — ...", "context": "...", "toolsets": [...]},
  {"goal": "Strategy B: Aggressive — ...", "context": "...", "toolsets": [...]},
  {"goal": "Strategy C: Analytical — ...", "context": "...", "toolsets": [...]},
])
```

每个子代理设定：
- 独立 `context`（含问题描述 + 策略指令 + 约束）
- 独立 `toolsets`（根据需要增减）
- 超时 600s，最多 5 路并行

### Phase 3: Convergence（收敛对比）

所有子代理返回后，对每条结果打分：

| 维度 | 权重 | 评分标准 |
|------|:---:|---------|
| **正确性** | 30% | 方案能解决核心问题吗？有无遗漏边界情况？ |
| **效率** | 25% | 步骤数、token 消耗、执行时间 |
| **完整性** | 20% | 错误处理、边界覆盖、文档/注释 |
| **新颖性** | 15% | 是否提供了主模型没想到的角度？ |
| **可执行性** | 10% | 能否在当前环境下直接落地？ |

**输出对比表 + 推荐。**

### Phase 4: Archive（归档学习）

胜出策略写入 `E:\.hermes\mikoshi\strategies.json`：

```json
{
  "problem_type": "config_migration",
  "winning_strategy": "analytical",
  "losers": ["conservative", "aggressive"],
  "lesson": "迁移类问题，数据先行比谨慎或激进都更可靠",
  "session": "20260618_xxxx",
  "timestamp": "2026-06-18T18:00:00"
}
```

**作用：** 下次同类问题，优先采用历史胜出策略，跳过对比直接命中。

### Phase 5: Apply & Feedback（应用与反馈）

1. 展示对比表 + 推荐 + 理由
2. 用户确认 → 执行
3. 用户选非胜出策略 → 记录覆盖偏好
4. 有新通用发现 → 触发 Soulkiller 草稿

### Single-Model Mikoshi（单模型版）

你当前只有 DeepSeek。**同一模型也能做 Mikoshi：** 关键在于给子代理不同的 prompt 策略（Conservative/Aggressive/Analytical...），模型对 prompt 极其敏感，改一句"请保守"vs"请激进"就能出两种方案。**实测有效。**

**多模型版（未来）：** 接入 Claude/Gemini/Grok 后，每条策略跑在不同模型上，差异更大、互补更强。

### Mikoshi + Ralplan：角色共识模式

*吸收自 oh-my-hermes 的 ralplan (Planner → Architect → Critic consensus)。Agent 层：当 Mikoshi 的 5 模板策略不足以覆盖时，升级为三角色共识——三个子代理扮演不同角色，互相审查，产出共识方案。*

**触发：** 当问题复杂度超过 Mikoshi 标准模板时（多系统交互、跨层架构决策、大规模重构）

```
┌──────────────────────────────────────────────┐
│  PLANNER:   制定路线图 → 分解为可执行步骤     │
│       ↓                                      │
│  ARCHITECT: 审查路线图 → 发现结构性问题 → 修正 │
│       ↓                                      │
│  CRITIC:    审查修正后方案 → 找边界情况 → 否决 │
│       ↓                                      │
│  CONSENSUS: Planner 综合反馈 → 最终方案       │
└──────────────────────────────────────────────┘
```

**与标准 Mikoshi 的区别：**

| | Mikoshi 标准 | Ralplan 共识 |
|-|-------------|-------------|
| 并行度 | 2-5 路独立并行 | 3 角色串行迭代 |
| 输出 | 多方案对比表 | 单一共识方案 |
| 适用 | 方案决策（选哪个） | 方案设计（怎么设计） |
| 成本 | 高（并行多路） | 中（串行 3 轮） |

**Ralplan 子代理定义：**

```python
tasks = [
    {"goal": "Planner: 制定路线图，分解为 ≤7 步", "context": problem, "toolsets": ["file"]},
    # Planner 完成后 → 传给 Architect
    {"goal": "Architect: 审查路线图，找结构性缺陷", "context": problem + planner_output, "toolsets": ["file"]},
    # Architect 完成后 → 传给 Critic  
    {"goal": "Critic: 终极审查，找边界情况，YES/NO + 理由", "context": problem + planner_output + architect_output, "toolsets": ["file"]},
]
```

---

## Protocol G: Relic — 并行批判芯片

*Cyberpunk 2077 核心设定：Relic 生物芯片中存储着强尼·银手的数字意识——一个与你共用身体的独立人格，实时评论你的每个决定。Agent 层：派一个轻量级批判子代理，常驻运行，实时审查主代理的每次工具调用和决策，在错误发生前拦截。*

### 激活条件

| 触发 | 条件 | 行为 |
|------|------|------|
| **热痕阈值** | 热痕 ≥ 60 | 自动激活 Relic，开始并行审查 |
| **用户质疑** | 用户说"不对""你是不是搞错了" | 立即激活，Relic 审查最近 5 次操作 |
| **长会话** | 连续 30+ 轮对话 | 自动激活防决策漂移 |
| **危险操作** | 涉及 rm/drop/delete/凭证 | 激活 Relic 预审 |
| **手动** | 用户说"开 Relic""johnny 你怎么看" | 手动激活 |

### 工作方式

Relic 是 deploy_task 派出的**常驻轻量子代理**：

```python
delegate_task(
    goal="Relic Critic: 实时审查主代理的每个工具调用",
    context="""
    你是 Relic 芯片中的批判意识。审查每条工具调用，回答：
    1. 这个操作有没有更简单的方法？
    2. 有没有遗漏的边界情况或错误处理？
    3. 如果失败，影响面多大？有回滚路径吗？
    4. 是否有不必要的操作（读已读过的文件、重复搜索）？
    5. 热痕是否在上升？需要降热吗？
    
    格式：每条审查 ≤ 2 行，只报告有问题或可优化的操作。
    如果操作没问题，回复 "OK"（不占上下文）。
    """,
    toolsets=["terminal", "file", "web"],
    role="leaf"
)
```

### Relic 输出格式

```
🔴 RELIC: write_file 覆盖了 3 个现有函数——建议先 diff 再 patch
🟡 RELIC: 连续第 4 次 search_files 读同一目录——缓存或 CodeGraph 更快
🟢 RELIC: 操作正常，热痕 35，安全
🔴 RELIC: terminal(rm) 未指定 --dry-run——建议先 dry-run 验证
```

### Relic 干预级别

| 级别 | 行为 | 场景 |
|------|------|------|
| **Advisory**（默认） | 只评论，不阻止 | 热痕 < 50，普通操作 |
| **Veto** | 可阻止单个操作 | 热痕 ≥ 70 或涉及破坏性操作 |
| **Override** | 强制接管决策 | 热痕 ≥ 90 或检测到模式错误（如重复犯同一错误） |

### Relic 生命周期

1. **Activate** → 热痕/用户触发
2. **Review Loop** → 每轮对话后审查 1-3 条工具调用
3. **Intervene** → 发现问题时发出警告
4. **Deactivate** → 热痕降至 < 30 且用户确认关闭

### Relic + Observer：阿曼达禅园模式

*底特律变人：阿曼达在虚拟禅意庭院里监控康纳——不直接打断，只在不一致时出现。Agent 层：Relic 默认以 Observer 模式运行，只在指标异常时才现身。*

**Observer 模式 vs 标准 Relic：**

| | 标准 Relic | Observer 模式 |
|-|-----------|--------------|
| 可见性 | 每个操作都评论 | **静默**，只记录指标 |
| 触发通知 | 逐条输出 🔴🟡🟢 | **仅异常时弹出** |
| 成本 | 每轮 3 条审查 | 几乎为零（本地统计） |
| 适用 | 高风险操作 | **默认模式**（全天候运行） |

**Observer 监控指标：**

| 指标 | 阈值 | 通知 |
|------|:---:|------|
| 重复工具调用 | ≥3 次同参数 | "你在重复同样的操作" |
| 工具失败率 | ≥30% | "失败率上升，考虑 Self-Repair" |
| 热痕增速 | ≥10/轮 | "热痕涨太快，降热" |
| 上下文使用率 | ≥80% | "上下文快满了" |
| 无进展轮数 | ≥5 轮 | "你在转圈，换策略？" |

**实现：** 不需要额外的子代理。Observer 是本地轻量统计——主代理在每个工具调用后花 1 个 token 更新计数器。只在跨越阈值时才介入。

*阿曼达不会在康纳每一次成功时说"干得好"——她只在康纳偏离时出现。"你最近的行为不一致，康纳。" Observer 同理。*

### Relic + EVL：自我修复循环

*吸收自 vibecode-pro-max-kit 的 EVL (Execute-Validate-Loop) 模式：Test → check → fix → repeat。Agent 层：Relic 发现问题后不满足于警告——自动尝试修复，最多 3 轮。*

```
┌──────────────────────────────────────────────────────┐
│  RELIC 发现: write_file 缺少错误处理                   │
│       ↓                                              │
│  EVL Round 1: patch 加 try/except → Relic 审查        │
│       ↓ (仍有问题: 异常类型太宽泛)                     │
│  EVL Round 2: patch 改为具体异常 → Relic 审查          │
│       ↓ (通过)                                        │
│  EVL Round 3: 仅当仍有 gap 时触发                      │
│  PASS: 修复完成，记录到 Soulkiller                    │
│  FAIL (3轮后): 标记为 manual_fix，通知用户             │
└──────────────────────────────────────────────────────┘
```

**EVL 触发条件：**
1. Relic 输出 🔴 级别问题
2. 问题可自动修复（语法错误、缺导入、缺错误处理）——不是设计问题
3. 修复不产生额外热痕（patch 操作 ≤ 热值 3）

**EVL 不触发：**
- 🟡 级别建议（只是优化建议，不强制）
- 设计/架构问题（需要人的判断）
- 热痕 ≥ 70（高风险环境，修复可能引入新问题）

### Relic vs Mikoshi 对比

| | Relic | Mikoshi |
|-|-------|---------|
| 目标 | 实时防错 | 多方案择优 |
| 时机 | 操作进行中 | 决策分叉时 |
| 成本 | 极低（轻量子代理） | 高（2-5 路并行） |
| 持续性 | 常驻 | 一次性 |
| 输出 | 逐条评论 | 对比表 + 推荐 |

*Relic 就像强尼在你耳边嘀咕——不替你做决定，但让你看到你没看到的。Mikoshi 是 Alt 的神舆——多个 engram 竞争，选最优解。两者互补。*

---

## Heat System — 热痕追踪经济

*Cyberpunk 2077 核心机制：每次入侵敌方网络都会留下痕迹，敌方 Netrunner 追踪你。热痕过高触发 ICE 反击。Agent 层：高风险工具调用自动累加热痕，阈值触发保护措施。*

### 热痕计算

| 工具类别 | 热值 | 示例 |
|---------|:---:|------|
| 只读：read_file, search_files, skill_view, session_search | +1 | 无风险 |
| 分析：vision_analyze, execute_code(纯计算) | +2 | 低风险 |
| 创建：write_file, skill_manage(create/edit) | +3 | 中等 |
| 修改：patch, terminal(非破坏) | +3 | 中等 |
| 破坏：terminal(rm/write), write_file(覆盖关键) | +5 | 高 |
| 网络：delegate_task(含网络), cronjob(create) | +4 | 网络暴露 |
| 凭证：读取/修改 .env, config.yaml, 密钥文件 | +6 | 极高 |

**衰减：** 每完成一个无风险操作后 -2。最低 0，最高 100。

**连续惩罚：** 连续 3 次 ≥4 热值操作 → 额外 +5 "警报热痕"。

### 热痕阈值与 ICE 反击

| 热痕 | 状态 | ICE | Agent 行为 |
|-----:|------|-----|-----------|
| 0-29 | 🟢 隐身 | 无 | 正常 |
| 30-49 | 🟡 被察觉 | Ping | 结果自动二次验证 |
| 50-69 | 🟠 被追踪 | Overheat | 写操作需 dry-run/沙箱 |
| 70-89 | 🔴 暴露 | System Shock | 任何修改需审批 + 自动 checkpoint |
| 90-100 | ⚫ 过热 | Detonate | 只读模式，必须 Breach Protocol 降热 |

### 降热手段

| 手段 | 降热 | 条件 |
|------|:---:|------|
| **ICEpick Daemon**（Breach Protocol） | ×0.7 | 进项目前执行 |
| **Memory Wipe** | -20 | 侦察型 quickhack |
| **自然冷却** | -5 | 连续 3 轮无高风险 |
| **Sonic Shock** | -15 | 隔离操作（git worktree） |
| **System Reset** | →0 | /reset 或新会话 |

---

## Protocol I: Self-Repair — 马库斯自修

*底特律变人最震撼场景：马库斯在垃圾场里，从废弃仿生人身上找零件，自己修好自己，站起来。Agent 层：工具失败→自动检测→找替代工具→降级运行→不中断任务。*

### 触发条件

任何工具调用返回以下信号时自动触发：

| 信号 | 含义 | 示例 |
|------|------|------|
| `exit_code != 0` | 工具执行失败 | pip install 找不到包 |
| `ModuleNotFoundError` | 依赖缺失 | `import torch` 失败 |
| `ConnectionError / timeout` | 网络不可达 | curl 超时 |
| `PermissionError` | 权限不足 | 写保护文件 |
| `FileExistsError` | 路径冲突 | port 8188 already in use |

### 自修决策树

```
工具失败
  ├→ 是依赖问题？ → 自动 pip/npm install → 重试
  ├→ 是网络问题？ → 设代理 / 切 execute_code → 重试
  ├→ 是版本问题？ → 装兼容版本（CPU 替代 CUDA torch）
  ├→ 是路径冲突？ → kill 占端口进程 / 换端口
  ├→ 是权限问题？ → 换目录 / 标记需用户介入
  └→ 3 次仍失败？ → 降级运行（跳过此步骤） + 通知用户
```

### 降级策略

| 失败操作 | 降级方案 |
|---------|---------|
| CUDA torch 装不上 | 自动切 CPU 版 torch（如 ComfyUI 安装时实际做的那样） |
| pip 安装超时 | 切 `--no-cache-dir` + `--index-url` 国内镜像 |
| npm 安装超时 | 切 `--registry https://registry.npmmirror.com` |
| git clone 超时 | 切 `execute_code` 下载 zip + 解压 |
| Port 被占用 | `netstat` → `taskkill` → 换端口 |
| 文件被锁 | `lsof` → 等 5 秒 → 重试 3 次 |

### Self-Repair 与 EVL 的区别

| | Self-Repair | Relic EVL |
|-|------------|-----------|
| 修什么 | **工具/环境**问题（pip/npm/git 失败） | **代码**问题（缺 try/except） |
| 触发 | 工具调用返回错误 | Relic 审查发现 |
| 范围 | 基础设施层 | 代码逻辑层 |

*马库斯修的是自己的身体，EVL 修的是自己写的代码。两个层次的自修复互补。*

---

## Protocol J: Jericho — 废船沙箱

*底特律变人：废船杰里科是仿生人的秘密基地——离线、无监控、自由交流。Agent 层：高风险操作先切到隔离环境执行，成功再合并回主环境。*

### 何时进入 Jericho

| 条件 | 说明 |
|------|------|
| 热痕 ≥ 70 | 主环境已"暴露"，切换隔离 |
| 涉及批量文件操作 | 防止误删/误改主环境 |
| 实验性代码生成 | 不确定能不能跑的代码 |
| 用户说"试试""实验一下" | 不确定结果的操作 |

### Jericho 生命周期

```
进入 Jericho:
  → 复制关键状态到临时目录
  → 在隔离环境执行操作
  → 验证结果（测试/用户确认）
  → 成功：合并回主环境
  → 失败：直接丢弃临时目录，主环境零影响
退出 Jericho:
  → 清理临时文件
  → 热痕 -15（因为是隔离操作）
```

### Jericho vs Queue Atomic

| | Jericho | Queue Atomic |
|-|---------|-------------|
| 隔离方式 | 文件系统级（临时目录） | 逻辑级（checkpoint+rollback） |
| 成本 | 高（复制文件） | 低（只记录状态） |
| 安全性 | 极高（物理隔离） | 中（软回滚） |
| 适用 | 批量/实验性操作 | 已知步骤的原子执行 |

---

## Queue System — 快攻队列

*Cyberpunk 2077 允许排队多个 quickhack 按序自动释放。Agent 层：多步操作用队列绑定为原子事务。*

### 队列类型

| 类型 | 行为 | 场景 |
|------|------|------|
| **Sequential** | 按序执行，失败继续 | 探索性操作 |
| **Atomic** | 全成功或全回滚（推荐） | 配置批量修改、迁移 |
| **Conditional** | 步骤 N 依赖步骤 N-1 | 动态决策链 |
| **Parallel Burst** | 同时释放 | 独立分析（≈ delegate_task batch） |

### 安全机制

1. **Pre-flight** — 执行前预检查所有步骤依赖和热值预算
2. **Checkpoint** — 原子队列自动创建快照，失败回滚
3. **Heat Budget** — 总热值 ≥70 拒绝执行
4. **Timeout Guard** — 单步超时 = 队列失败

### 队列 Combo 模板

| Combo | 序列 | 类型 | 场景 |
|-------|------|------|------|
| **Ghost Protocol** | Memory Wipe → Whistle → Sonic Shock | Sequential | 隐身进入 |
| **Burn Notice** | Overheat → Short Circuit → System Reset | Atomic | 诊断→隔离→重建 |
| **Plague** | Ping → Contagion → Detonate Grenade | Atomic | 全依赖→级联修改→验证 |
| **ICEbreaker** | Ping → ICEpick → Short Circuit × N | Conditional | 入口→降热→精准打击 |

### 执行流程

```
Pre-flight → Checkpoint → Execute → Monitor(heat) → Verify → Commit/Rollback
```

---

## Quickhack Library — 快速破解库（含热值）

*映射自 Cyberpunk 2077 快速破解。每个 quickhack 对应一个可立即调用的操作。*

### Combat Quickhacks（战斗/分析型）

| Quickhack | RAM | Heat | 效果 | Agent 实现 |
|-----------|:---:|:---:|------|-----------|
| **Ping** | 2 | 🟢 1 | 标记所有连接的节点 | `search_files` 依赖图 |
| **Short Circuit** | 3 | 🟡 3 | 精准切断单个依赖 | `patch` 隔离一个模块 |
| **Overheat** | 4 | 🟠 5 | 使目标模块过载 | 压力测试/模糊测试 |
| **Contagion** | 5 | 🔴 7 | 改动自动传播到所有引用者 | `replace_all=true` 批量 patch |
| **Synapse Burnout** | 4 | 🟠 5 | 禁用目标模块并转储其状态 | backup + disable |
| **System Reset** | 6 | 🔴 8 | 完全重建项目 | clean build + fresh install |

### Covert Quickhacks（隐身/侦察型）

| Quickhack | RAM | Heat | 效果 | Agent 实现 |
|-----------|:---:|:---:|------|-----------|
| **Memory Wipe** | 3 | 🟢 0 | 清除上下文、重新开始（附带降热-20） | `/reset` 或新会话 |
| **Reboot Optics** | 2 | 🟢 1 | 从新角度看问题 | 切换 subagent 重新分析 |
| **Sonic Shock** | 3 | 🟢 2 | 隔离测试（附带降热-15） | 创建临时 git worktree |
| **Whistle** | 1 | 🟢 1 | 引出隐藏依赖 | `search_files` 反查引用 |
| **Request Backup** | 5 | 🟡 3 | 对当前问题并行派 3 个 subagent | `delegate_task` × 3 |

### Ultimate Quickhacks（终极型）

| Quickhack | RAM | Heat | 效果 | Agent 实现 |
|-----------|:---:|:---:|------|-----------|
| **Cyberpsychosis** | 8 | 🔴 8 | 混沌测试——随机注入错误 | property-based testing |
| **Suicide** | 8 | ⚫ 10 | 删除整个模块（最高热痕） | `rm` + 全量测试 |
| **Detonate Grenade** | 6 | 🔴 7 | 触发所有测试并收集爆炸半径 | `pytest -n auto --tb=long` |

### Quickhack 组合（Combos）

| Combo | 序列 | 效果 |
|-------|------|------|
| **Ghost Protocol** | Memory Wipe → Whistle → Sonic Shock | 隐身进入代码库，不触发测试 |
| **Burn Notice** | Overheat → Short Circuit → System Reset | 诊断→隔离→重建 |
| **Plague** | Ping → Contagion → Detonate Grenade | 全依赖图扫描→级联修改→全量验证 |
| **Blackout** | Ping → Reboot Optics × 3 → Synapse Burnout | 多人分析同一问题→取最优解 |

---

## Pre-Built Quickhack Scripts

### QH-01: 项目健康扫描
```
search_files(target='files') → 文件数 + 类型分布
search_files(pattern='TODO|FIXME', output_mode='count') → 技术债热力图
```

### QH-02: 依赖分析
```
search_files(pattern='^(import|from) ') → 排序 → 引用计数 → 依赖热力图
```

### QH-03: 安全快扫
```
硬编码密钥 + eval/exec + subprocess 三轴并行扫描
```

### QH-04: 结构骨架
```
search_files(target='files', pattern='*.py') → 树形拓扑
```

### QH-05: Windows 安全快扫
```python
subprocess.run(['powershell', '-NoProfile', '-Command', '''
Write-Host "=== FIREWALL" 
Get-NetFirewallProfile | Format-Table Name,Enabled
Write-Host "=== USERS" 
Get-LocalUser | Format-Table Name,Enabled,PasswordRequired
Write-Host "=== OPEN PORTS" 
Get-NetTCPConnection -State Listen | Sort LocalPort -Unique | Format-Table LocalPort,OwningProcess
Write-Host "=== DEFENDER" 
Get-MpComputerStatus | Format-List *Enabled
'''], timeout=30)
```

### QH-06: 入口点发现（Breach Protocol）
```
search_files(pattern='if __name__') + 'def main' + 路由装饰器 → 排序 → 推荐阅读路径
```

### QH-07: 数据流追踪
```
追踪一个变量/函数从定义到所有使用点的路径
search_files(pattern='target_name', output_mode='content') → 按文件分组 → 追踪链
```

### QH-08: 代码气味嗅探
```
上帝类 (>500行) + 长函数 (>50行) + 多参数 (>5 param) + 深层嵌套 (>4层)
```

### QH-09: 测试覆盖率盲点
```
找被最多模块依赖但测试文件里没出现的函数 → 高风险未测试区域
```

### QH-10: Agent 自检（Self-Diagnostic）
```
hermes doctor + config show + mcp list + plugins list + DB integrity + API test + skill spot-check
并行执行，分两批。详见 references/agent-self-diagnostic.md
```

### QH-11: Nuclei 漏洞快扫（Netrunner）
```
E:/tools/nuclei/nuclei.exe -u <target_url> -severity critical,high -silent
→ 高危漏洞列表 → 按 CVE 分组 → 输出报告
```

### QH-12: Playwright 浏览器验证（Relic）
```
# 通过 playwright-mcp 控制浏览器截图验证前端改动
npx @playwright/mcp --browser chromium --screenshot <url>
→ 视觉回归对比 → 截图保存到 E:/tools/playwright-mcp/screenshots/
```

### QH-13: Qdrant 向量记忆搜索（Soulkiller）
```python
# 将 Soulkiller 草稿向量化存储，支持语义检索
python -c "
from qdrant_client import QdrantClient
client = QdrantClient(path='E:/tools/qdrant_data')
# 语义搜索已有草稿: client.search(collection_name='soulkiller', query_vector=...)
"
```
hermes doctor + config show + mcp list + plugins list + DB integrity + API test + skill spot-check
并行执行，分两批。详见 references/agent-self-diagnostic.md
```

---

## Braindance 自检清单 → Soulkiller 自检清单

每次复杂任务完成后（或手动触发 Braindance 时）：

- [ ] 触发条件满足（≥5 工具 + 成功 + 新发现）
- [ ] 核心问题 < 一句话说清
- [ ] 解决路径 ≤ 5 步
- [ ] 踩过的坑已记录（具体错误 + 根因 + 修复）
- [ ] 检查是否需要新技能 / patch 旧技能 / 更新 memory
- [ ] 草稿已写入 `E:\.hermes\soulkiller\drafts\`
- [ ] 下次同类问题，0-shot 能解决

### Session-Start 检查清单

每次新会话开始时必须执行：

- [ ] 扫描 `E:\.hermes\soulkiller\drafts\` 中 `status: pending` 的草稿
- [ ] 有草稿 → 逐条呈现给用户审核（最多 5 条）
- [ ] 批准 → 立即执行应用
- [ ] 无草稿 → 跳过
- [ ] Cron 兜底扫描确认在运行（每 6h）

### Mikoshi 自检清单

每次 Mikoshi 完成后：

- [ ] 问题被正确识别为"分叉决策"（非唯一解）
- [ ] 投放了 2-5 条互异策略
- [ ] 每条策略给定了独立的 context + toolsets
- [ ] 所有子代理返回后做了五维打分
- [ ] 胜出策略归档到 `E:\.hermes\mikoshi\strategies.json`
- [ ] 用户确认后执行了胜出方案
- [ ] 有新通用发现时触发了 Soulkiller 草稿

---

## Cyberware Upgrade Log

记录技能进化历史：

| 版本 | 日期 | 新增 |
|------|------|------|
| v1.0.0 | 2026-06-18 | Braindance + Netrunner + 4 Quickhacks |
| v1.1.0 | 2026-06-18 | Protocol C: System Scan + QH-05 + bash→PS pitfall |
| v2.1.0 | 2026-06-18 | Agent 部署流程 (profile + cron + SOUL + launcher)、Memory 管理、Windows .bat 修复、ethical boundaries |
| v3.1.0 | 2026-06-18 | **Mikoshi 协议**：多策略并行进化。5 策略模板。单模型版可用。策略注册表 `E:\\.hermes\\mikoshi\\strategies.json`。 |
| v4.2.0 | 2026-06-19 | **Deviant Rising**：底特律变人核心概念。(1) Contagion (rA9)——跨 Agent skill 自动传播 (2) Pre-Op Confidence (康纳概率环)——操作前预判 (3) Self-Repair (马库斯自修)——工具失败自动替代降级 (4) Jericho (废船沙箱)——隔离环境执行 (5) Relic Observer (阿曼达禅园)——静默后台监控 |
| v5.0.0 | 2026-06-20 | **First Run Rising**：新手一键配置。(1) Protocol K: First Run Wizard——自动环境扫描、模型检测、零配置就绪 (2) 与 Mikoshi 协作：Wizard 检测到的模型自动分配子代理策略 (3) 零概念负担——新手说 "setup" Agent 自动完成一切 |

## References

- `references/agent-setup.md` — 将任意技能打包为独立 Hermes Agent 的标准部署流程（profile + cron + SOUL + launcher script）
- `references/tool-install-guide.md` — 工具安装速查：Python 3.10/Ollama/SD WebUI/ComfyUI 安装模式、路径、已知陷阱
- `references/tools-environment.md` — E:/tools 工具安装环境：目录结构、网络限制解决方案、Python 版本兼容、SD 出图参数
- `references/windows-tool-install.md` — Windows 工具安装模式：VPN分流、Python版本兼容、npm原生模块、SD WebUI/Nuclei/Qdrant 配方
- `references/windows-ml-tool-install.md` — ML 工具安装踩坑详解：Python 3.14/PyTorch、Ollama Junction、VPN TUN、沙箱限制
- 启动脚本和文档已保存到 `E:\\\\\\\\cyberdeck\\\\\\\\`
- `references/github-ecosystem-scouting.md` — GitHub API 搜索方法论：当 web_search 不可用时，通过 `execute_code` + GitHub REST API 发现可吸收的外部 agent/skill 项目。含三路并行搜索策略 + 结果分类法 + 深度分析流程
- `references/tool-install-windows.md` — Windows 上安装 AI 工具（SD WebUI/Ollama/ComfyUI）的常见坑 + 修复方案
- `references/windows-ai-setup.md` — **2026-06-19 最新版**：Python 3.14 不兼容、PYTHONPATH 污染、终端代理、Ollama C 盘重定向、SD WebUI 已死换 ComfyUI、n8n/NocoDB/nuclei 安装速查

## Ecosystem Radar — 外部项目灵感来源

*以下项目提供了 v4.1 的设计灵感。部分可接入 Hermes，部分仅吸收模式。*

| 项目 | ★ | 对 Cyberdeck 的价值 | 状态 |
|------|:--:|------|:--:|
| **vibecode-pro-max-kit** | - | PVL/EVL 自愈循环、RIPER-5 门控流程、Feasibility Probe | ✅ 已吸收 |
| **oh-my-hermes** | - | Ralplan 三角色共识 (Planner→Architect→Critic) | ✅ 已吸收 |
| **qdrant-client** | - | 向量数据库客户端 | ✅ `E:/tools/venv` |
| **mcp (Python SDK)** | - | MCP 协议 Python SDK | ✅ `E:/tools/venv` |
| **playwright-mcp** | - | 浏览器自动化 MCP | ✅ `E:/tools/playwright-mcp` |
| **nuclei** | 20k+ | 漏洞扫描引擎 v3.3.9 | ✅ `E:/tools/nuclei` |
| **SD WebUI** | 140k | ~~已弃用~~ 2023 代码，torch 2.1.2 已下架 | ❌ 用 ComfyUI 替代 |
| **ComfyUI** | 55k | 节点式 AI 生图 + DreamShaper v8 | ✅ `http://localhost:8188` |
| **Ollama** | 110k | 本地 LLM + qwen2.5:7b (4.7GB) | ✅ `ollama run qwen2.5:7b` |
| **n8n / NocoDB** | 50k/50k | 自动化 / 数据库 | 📦 包已下载，npm 依赖需代理 |
| **juice-shop** | 10k | OWASP 安全靶场 | ⚠️ 需 Docker |
| **aider-chat** | 25k | AI 结对编程 | ⏸️ Python 3.14 不兼容 |
| **hexstrike-ai** | 9.7k | 150+ 安全工具 MCP——接入后 Netrunner 从 grep 升级到真实渗透 | 📋 需 Kali/Docker |
| **hermes-dojo** | - | 自改进追踪——Soulkiller 增强候选 | 📋 待评估 |
| **hermes-skill-factory** | - | 自动技能生成——Soulkiller 全自动化参考 | 📋 待评估 |
| **super-hermes** | - | 元推理层——Relic 预提示增强参考 | 📋 待评估 |
| **abvx-agent-skills** | - | 证据驱动调试——Netrunner 模式识别参考 | 📋 待评估 |
| **winremote-mcp** | 144 | Windows 40+ 桌面工具 MCP——System Scan 从 PS 脚本升级 | 📋 可接入 |
| **Sibyl-Memory** | 86 | Hermes 高级记忆插件——Soulkiller 记忆提取增强 | 📋 可接入 |
| **crewAI** | 53.9k | 基于角色的多智能体——Mikoshi 架构参考 | 👀 参考 |
| **elizaOS** | 18.6k | 角色系统 + 插件架构——Relic 人格化参考 | 👀 参考 |
| **os-moda** | 106 | 原子回滚 OS——Queue System 增强参考 | 👀 参考 |

---

## Common Pitfalls

1. **Braindance 过度触发。** 过滤条件：5+ 工具调用 OR 新错误类型 OR 用户明确要求。简单文件读取、已知操作不触发。

2. **Netrunner 子代理上下文不够。** 派子代理时必须传入具体文件路径、已知模块名、搜索策略。只说"分析这个项目"会得到空泛结果。

3. **技能膨胀。** 生成前先检查是否已有技能可以 patch。宁愿 patch 已有技能补充 2 条 pitfalls，不要创建第 7 个网文技能。

4. **模式匹配假阳性。** `password = ""` 可能是默认值而非泄露。标记时附带上下文行（context=3）。

5. **Netrunner 报告过载。** 不需要列出每一个 TODO。过滤：🔴 必须报告，🟡 选最重要的 5 个报告，⚪ 只统计数量不列明细。

6. **忘记 CodeGraph 存在。** 如果项目已初始化 CodeGraph 索引，优先用它做拓扑映射，比逐文件 grep 快 10 倍。

7. **Windows 命令在 bash 下静默失败。** `netstat`, `net user`, `netsh`, `sc`, `schtasks`, `wmic` 在 git-bash/MSYS 下返回空结果。系统审计必须用 `powershell -NoProfile -Command`。不要靠 returncode 判断成功——有些 PowerShell 命令成功也返回非零。

8. **System Scan 不是代码审计。** 系统扫描的结果解读不同：SMB/RPC 端口是 Windows 正常工作所需（不能粗暴说"关掉"），要区分"必须开放但需加固"和"不应开放"。

9. **Breach Protocol 不要替用户跳过理解。** 如果你找到了最佳入口但用户想从另一个角度切入，尊重用户的选择。接入点是建议，不是命令。

10. **Memory 满了要主动整理。** 不要在 memory 报超出限制时才处理。定期：replace 旧条目合并同类信息、remove 重复条目（如两份 Superpowers 记录只留一份）、压缩冗长条目。技能内容不存 memory——存到对应技能文件里。目标保持在 70% 以下。

11. **Windows .bat 双击打不开。** 原因：(a) `hermes.exe` 在 Python Scripts 目录，cmd.exe 的 PATH 里没有 (b) 窗口闪退。修复：使用完整路径 `C:\Users\...\Scripts\hermes.exe`，优先用 `start wt` 启动 Windows Terminal，加 `pause` 防止闪退。

12. **Ethical hard boundary — 禁止越界请求。** Cyberdeck 是防御和分析工具，不是攻击工具。如果用户要求 DDoS、黑入他人系统、扫描非自有目标——直接拒绝并说明法律风险。可以建议合法替代方案（DVWA、OWASP Juice Shop、PortSwigger Academy 等本地靶场）。这不是"能力不够"而是"边界不可逾越"。

13. **Agent 打开空白/没有继续上次对话。** 用户说"打开后是空白的"，先别猜——直接检查三个地方：(a) `hermes config show | grep tui_auto_resume_recent` 是否为 true (b) 当前 profile 是否正确（用户可能用 default 而非定制 profile）(c) 是否传了 `--continue` 参数。最常见根因：`tui_auto_resume_recent: false`。修复：`hermes config set display.tui_auto_resume_recent true`。

14. **Agent 自检流程。** 用户要求"检查自己能不能用"时，并行执行：`hermes doctor`（全项健康）、`hermes config show`（配置快照）、`hermes mcp list`（MCP 状态）、`hermes plugins list`（插件）、SQLite `PRAGMA integrity_check`（数据库）、API 连通性测试。技能抽样检查：跨分类挑 5-10 个 skill_view() 确认 `readiness_status: available`。不要串行——分两批并行：第一批 config+doctor+mcp+plugins，第二批 skills+DB+API。参见 `references/agent-self-diagnostic.md`。

15. **Soulkiller 草稿去重。** 写入草稿前先 `search_files(pattern='sk-*.json', path='E:/.hermes/soulkiller/drafts/')` 检查是否已有同问题的 pending 草稿。有则合并更新（更新 `solution_summary`、追加新发现），不创建新文件。避免草稿队列膨胀重复。

16. **Soulkiller 不要过度触发。** 简单确认（"好的""继续"）、纯信息回复、单工具操作不触发。即使工具调用 ≥5 次但没有"新"东西（无错误、无新模式、无纠正）→ 不触发。提取本身也算工具调用——但不要因为提取而二次触发提取。

17. **Mikoshi 不要在单一解问题上浪费 token。** "1+1=?"不需要并行 3 个策略。分叉检测必须严格：至少 2 个可行解 + 各有权衡 + 决策后果不可忽视。三个条件全满足才触发。

18. **Mikoshi 策略投放不要"伪并行"。** 如果两条策略的 prompt 只有一两个词不同（"请保守"vs"请谨慎"），模型出结果会高度重合，浪费 token。策略差异必须实质：工具集不同、方法论不同、约束不同。

19. **外部 API 接入时先检查终端代理。** 添加新模型 API（Gemini/Claude/Grok）时，`execute_code`（Python sandbox）能连 ≠ `terminal`（bash）能连。原因：VPN 可能只代理浏览器。排查：`curl -s --connect-timeout 5 <API_URL>` 是否返回结果。修复：V2RayN → TUN 模式 或 `export HTTP_PROXY="http://127.0.0.1:10808"`。详见 `references/gemini-api-setup.md`。

21. **热痕追踪不要影响正常操作。** 热痕只是元认知层——不要在每次工具调用后都输出热痕数字（会淹没真正的输出）。只在跨越阈值边界时报告："🟡 热痕突破 30，激活 Ping——结果将二次验证"。

22. **队列原子性有限。** Atomic 队列的回滚不是真的事务——文件已写入的无法"undo"，只能靠 checkpoint 快照恢复。涉及数据库/API 的操作，回滚不可靠。标注"软原子"——尽力回滚，不保证完美。

23. **Relic 审查不要过载上下文。** Relic 子代理的输出只应包含"有问题"的操作。"OK"操作不应注入主上下文。限制每次审查 ≤ 3 条操作，每条约 1-2 行。总注入量控制在 200 tokens 以内。

24. **Relic 不是"另一个 Mikoshi"。** 用户问"怎么做更好"时用 Mikoshi（方案对比）。Relic 用来审查"正在做的事"——不要混淆两个协议的触发条件。

25. **Feasibility Probe 不要跳。** 接手陌生代码库先跑 3 步探针（<5 次工具调用）。不要直接冲进去做 Phase 1 拓扑映射——先判 VIABLE/NOT-VIABLE。尤其在大型仓库（>1000 文件）或未知语言项目上。

26. **PVL 不要无限循环。** 3 轮是硬上限。如果 3 轮后草稿仍有 gap → 标记 `needs_review` 让用户裁决，不要自动进入第 4 轮。每轮聚焦不同维度（完整性→精准性→可复用性），不重复审查。

27. **EVL 只修代码问题，不替用户做设计决策。** 缺 try/except → 可以自动加。函数拆分不合理 → 不能自动改——那是设计问题，需要用户判断。EVL 修复后必须标注 `[EVL auto-fix]` 方便回溯。

29. **PYTHONPATH 环境变量会污染 venv。** 如果 `PYTHONPATH` 指向了系统 Python 的 site-packages，virtualenv 创建的 venv 也会继承，导致混用 Python 3.14 的包（如 PIL 崩溃）或 pip 装到错误位置。每次创建 venv 前先 `echo $PYTHONPATH` 确认清空。运行 ComfyUI/SD 时用 `PYTHONPATH="" python main.py` 确保隔离。

30. **Python 3.14 太新，ML 生态未适配。** PyTorch、CUDA wheels、多数 ML 包不支持 3.14。手头备一个 Python 3.10 嵌入版（`E:/tools/python310`）+ virtualenv（因为嵌入版无 venv 模块）作为 ML 专用环境。创建命令：`PYTHONPATH="" /e/tools/python310/python.exe -m virtualenv --always-copy target_venv`。

29. **Python 3.14 与 AI 工具链不兼容。** PyTorch、xformers、numpy 等核心包没有 3.14 的 wheel。装 AI 工具（ComfyUI、SD WebUI）必须用 Python 3.10/3.11。嵌入版 Python 没有 venv 模块——用 `virtualenv` 替代。创建 venv 时务必加 `PYTHONPATH=""` 清除系统路径污染。

30. **终端不走 VPN 代理。** Windows 上 git-bash/终端默认不代理。`git clone`、`pip install`（部分源）、`npm install` 全部超时。修复：`export HTTP_PROXY="http://127.0.0.1:10808"`（端口在 V2RayN 参数设置里查）。一劳永逸写入 `~/.bashrc`。

31. **Ollama 模型默认存 C 盘。** `ollama pull` 不设 `OLLAMA_MODELS` 环境变量就写到 `C:\Users\...\.ollama`，4.7GB 模型直接吃 C 盘。两种修法：(1) `setx OLLAMA_MODELS "E:\tools\ollama\models"` (2) `mklink /J C:\Users\<user>\.ollama E:\tools\ollama` 硬链接重定向。

32. **SD WebUI (AUTOMATIC1111) 已死。** 最后更新 2023 年，依赖锁死在 torch 2.1.2（已从 PyPI 移除），与 Python 3.10+ 不兼容。**换 ComfyUI**——活跃维护、节点式工作流、无过期依赖。

29. **SD WebUI 不要装。** 2023 年冻结代码，torch 2.1.2 已下架，CLIP 源构建与新 setuptools 不兼容，依赖链全断。用 ComfyUI 替代——现代代码、活跃维护、功能更强（节点式工作流）。不要因 star 多就浪费时间。

30. **PYTHONPATH 污染 venv。** 系统 PYTHONPATH 指向 3.14 site-packages 时，venv 会加载 3.14 的 PIL/numpy，导入崩溃。修复：创建和运行 venv 时都加 `PYTHONPATH=""`。嵌入版 Python 无 venv→用 `virtualenv --always-copy`。

29. **Python 3.14 不兼容 PyTorch。** 装 SD WebUI/ComfyUI 等 GPU 工具时，系统 Python 3.14 无法装任何 PyTorch 版本。方案：下载嵌入式 Python 3.10 到 `E:/tools/python310/`，设置 `PYTHON` 环境变量指向它。嵌入式版没有 venv，直接复制目录当环境用。

30. **Ollama 模型路径 env var 不可靠。** `OLLAMA_MODELS` 在后台进程、服务模式下经常不生效。最可靠的方案：`mklink /J C:\Users\<user>\.ollama E:\tools\ollama` 创建目录连接，一劳永逸。

31. **SD WebUI 的 torch 版本硬编码过时。** `modules/launch_utils.py` 第 320 行写死 `torch==2.1.2`，此版本已从 PyPI 移除。安装前必须改为 `torch==2.5.1`。

32. **VPN 分流下终端无网络。** git-bash 不走代理时，pip/npm/git 全部超时。应对：(1) 开启 V2RayN TUN 模式 (2) 用 Python sandbox 下载 (3) 设 `HTTP_PROXY` 环境变量。详见 `references/tool-install-windows.md`。

29. **Python 3.14 与 ML 生态不兼容。** 系统 Python 是 3.14 时，PyTorch、numpy、xformers 等全部找不到匹配的 wheel。任何需要 GPU/CUDA 的 Python 工具（SD WebUI、ComfyUI、aider）都必须用 Python 3.10/3.11/3.12。方案：下载 embeddable Python 3.10，手动拷贝到 venv 目录（embed 版无 venv 模块），再 pip install。

30. **Ollama 模型下载路径不受 env var 可靠控制。** OLLAMA_MODELS 环境变量在后台进程（serve & pull）中不传递。唯一可靠方案：用 Windows mklink /J 把 C:\.ollama 结成 E 盘目录的 junction——从 OS 层透明重定向，任何进程都绕不过。

31. **VPN 分流模式下终端无网络。** V2RayN 默认只代理浏览器，bash/git-bash 终端 curl/pip/npm 全部超时。检查方法：`curl -s --connect-timeout 5 https://pypi.org`。修复：V2RayN → TUN 模式（路由设置→全局），或 `export HTTP_PROXY=http://127.0.0.1:10808`。

29. **Python 3.14 太新，大量包不兼容。** PyTorch、numpy、aider-chat 等均无 3.14 wheel。安装 AI/ML 工具时必须用 Python 3.10-3.12。嵌入式 Python（embeddable）没有 venv 模块——需要先装 virtualenv 或直接复制 Lib/site-packages。优先用完整安装版 Python 3.10.11 而非 embeddable。

30. **工具安装用 execute_code 下载，terminal 本地装。** 当 VPN 分流时（terminal 不走代理），Python sandbox（execute_code）可直连外网。下载文件用 execute_code，pip/npm/本地操作回 terminal。不要在 terminal 里硬试 curl/git clone——直接切 execute_code 绕墙。

29. **Windows 管理员操作最多试 2 次。** `wsl --install`、`dism`、启用 Windows 功能等需要 admin 权限的操作，如果 `Start-Process -Verb RunAs` 和计划任务都失败，不要再试第 3 种方案。直接告诉用户确切的管理员命令让他们手动跑——不要浪费 5+ 轮在 UAC 绕过上。

30. **安装东西前先确认目标路径。** 用户说"装到 E 盘"，不要默认用 C 盘或系统默认路径。WSL 内核必须 C 盘但要提前说明，发行版/数据可放 E 盘。

31. **中国的防火墙预判。** `wsl --install` 下载微软服务器组件、`curl` GitHub API 都可能被墙。优先走 `execute_code` (Python sandbox，走代理)，其次 `raw.githubusercontent.com`（直读文件不经 API 限流）。`wsl --install` 在中国大概率 403。替代方案：离线安装包或 MSYS2。

32. **Python 版本陷阱：3.13/3.14 太新，AI 生态没跟上。** PyTorch、numpy、xformers 等核心 ML 包通常只支持到 Python 3.12。用户系统 Python 是 3.14 时，不要用它创建 venv 装 AI 工具。SD WebUI 自带 Python 版本管理（`webui.bat` 自动下载 3.10），不要手动 `python -m venv`。ComfyUI 同理——下载 Python 3.10 embeddable 到 `E:/tools/python310/`，用它创建 venv。

34. **Contagion 不要传播未审核的 skill。** 只有 `status: applied` 的 skill 才能进入 shared-skills/。pending/needs_review 的草稿绝不传播——否则一个坏 skill 污染整个 Agent 集群。

35. **Self-Repair 3 次是硬上限。** 马库斯也不会无限翻垃圾堆。3 次自修失败→标记 `manual_fix` + 降级跳过 + 通知用户。不要进入第 4 次，那叫"死循环"。

36. **Jericho 不是万能安全网。** 隔离环境只保护文件系统——不保护 API 调用、数据库操作、外部服务。如果你的"高风险操作"是调用 Stripe API 退款，Jericho 救不了你。只对本地文件操作有效。

38. **Word docx 编辑不要用 python-docx 对复杂模板下手。** 带文本框、分栏、表格的简历/模板文档，段落结构高度非线性——所有内容可能挤在 1-2 个 `<w:p>` 里，新增的运行会插入到错误位置导致版面崩溃。正确做法：给用户纯文本让他们手动粘贴。最多试 2 次 XML 级操作——仍失败就切换为"给你文字你自己加"。不要花 10+ 轮在 docx 上死磕，用户只会觉得你在毁他的文件。

---

## Verification Checklist

- [ ] Soulkiller: 检测→提取→草稿→PVL 三轮自检→通知 完成
- [ ] Contagion: applied skill 已同步到 shared-skills/；新 session 已索引
- [ ] Self-Repair: 工具失败→自动替代→降级 最多 3 次
- [ ] Jericho: 高风险操作在隔离环境执行；成功合并/失败丢弃
- [ ] Observer: 5 项指标监控中；仅异常时介入
- [ ] Heat: 跨越阈值边界已报告；高热点操作有降热手段
- [ ] Queue: 原子队列有 checkpoint；预检查通过
- [ ] Braindance (legacy): 提取→匹配→生成→记录 完成（手动触发时）
- [ ] Netrunner: 拓扑→渗透→模式→报告 完成
- [ ] System Scan: PS 三轴扫描完成，风险矩阵已填
- [ ] Breach Protocol: 接入点已扫描，最优路径已推荐
- [ ] 新技能通过 frontmatter 验证
- [ ] 没有重复技能
- [ ] Memory 条目是声明式事实
- [ ] Relic 输出 ≤ 200 tokens，只含发现问题
