# AGENTS.md

## Project Goal

This project is an **execution harness** for AI/算法岗位笔试备考。默认配置针对大模型算法方向（Transformer、GNN、扩散模型、LLM 推理优化），可按需替换为目标岗位的考试内容。

Primary goal: maximize the chance of passing the written exam.

Secondary goal: keep only the minimum useful interview preparation for follow-up interviews.

**使用前配置**：运行 `init-guide`（说 "init"）自动配置备考目标、日期和每日可投入时间，或手动编辑 `HANDOFF.md`。

## Exam Format（默认配置，按目标考试调整）

| 维度 | 默认配置 |
|------|----------|
| 题型 | 单选 + 不定项选择 + 编程 |
| 数学 | 线代、概率、微积分选择题 |
| AI 岗位重点 | Transformer、GNN、扩散模型、LLM 推理优化 |
| 通用重叠 | SFT/LoRA/RLHF、RAG、KV Cache、编程算法 |

> 实际考试格式请在 `targets/{target}/sources/` 目录下创建对应的考试分析文件，并更新此表。

## Priority Split

- 25% Python OJ / ACM-style algorithm practice.
- 25% core AI/ML knowledge review（Transformer、GNN、扩散模型、LLM 细节、数学基础）。
- 25% 数学选择题与多选题专项训练。
- 25% project expression for training, Agent, tool use scenarios.

When tradeoffs appear, choose algorithm AC practice first, then math/multiple-choice quick-score topics.

## Target Role Requirements（示例：大模型算法方向）

岗位通用要求：
- 熟练使用 Python，掌握 PyTorch。
- 熟悉 Transformer、扩散模型（Diffusion Model）、图神经网络（GNN）。
- 有 LLM 或多模态模型研究经验。
- 加分：AI for Science、特定领域应用经验。

笔试常见内容：
- 数学基础选择题：线性代数、概率统计、微积分、矩阵运算。
- AI 常识选择题：机器学习、深度学习基础、PyTorch 框架。
- 岗位认知选择题：大模型方向、核心项目。
- 多选题策略：漏选比多选扣分少，不确定的选项宁可不选。

> 请根据目标岗位调整 `targets/{target}/sources/` 下的考试分析和 `shared/cheatsheets/`、`targets/{target}/cheatsheets/` 下的速记资料。

## Harness Engineering Overview

This project is an **execution harness**, not a knowledge base. Every component has a specific role in the daily loop: intake → practice → record → review → handoff. The following sections document the component map, skill pipeline, and data flow so any agent can operate the harness without rediscovering structure.

### Component Map

```
Pass-LLM-with-LLM/
  AGENTS.md                    # This file. Harness rules, skill pipeline, component map.
  START_HERE.md                # Session bootstrap order (read this first each session).
  HANDOFF.md                   # Session handoff: what was done, what's next, blockers.
  README.md                    # Human-readable project overview and directory guide.
  .gitignore                   # Excludes __pycache__, .pyc, temp files, .claude/, daily data.
  LICENSE                      # MIT License (root-level for GitHub auto-detection).
  CONTRIBUTING.md              # Contribution guidelines (root-level for GitHub PR prompts).

  skills/                      # Invokable skill definitions (loaded by Skill tool).
    algo-annotation.md         # Annotates solve() code with Chinese comments + # [防错] markers.
    choice-q-create.md         # Generates targeted multiple-choice question sets (exam_config-driven).
    choice-q-drill.md          # Interactive quiz mode with immediate scoring and mistake_log update.
    solve-skeleton/
      SKILL.md                 # Skeleton selection logic, anti-pattern checklist, workflow.
      references/
        io-modes.md            # 5 I/O templates (single, multi-case, EOF, n-lines, grid).
        algo-skeletons.md      # 8 algorithm templates (BFS, DFS, DSU, Heap, Dijkstra, etc.).
        exam-patterns.md       # 6 exam-specific patterns (simulation, GCD merge, bracket, etc.).
    solve-analyze/
      SKILL.md                 # Diagnosis: user code vs standard solution comparison, root cause tagging.
      references/
        root-cause-tags.md     # 11 root cause tags (pattern/proof/python + 8 algo-code tags).
        comparison-template.md # Structured comparison report template with {{placeholder}} fields.
    exam-assistant.md          # MCP-backed exam assistant with experience retrieval (uses exam-memory tools).
    init-guide.md                # First-run onboarding: collects exam target, updates profile, configures scope.
    review-tracker.md          # Progress aggregation: readiness trends, mistake stats, coverage gaps, today's must-do list.

  targets/                     # Target-specific content (one subdirectory per exam target).
    ai-lab/                    # 上海 AI 实验室 笔试
      cheatsheets/             # AI/ML quick-reference notes (moved from llm/).
        llm_core_cheatsheet.md
        gnn_diffusion_cheatsheet.md
        math_fundamentals.md
        ai_lab_context.md
      daily/                   # Target-specific daily plans (YYYY-MM-DD.md).
      progress/                # Target-specific progress tracking.
        choice-questions/      # 选择题刷题记录（按轮次）
        study-planning/        # 学习计划与准备度
        exam-analysis/         # 考试分析
        task-board/            # 跨域任务追踪
      prompts/                 # Target-specific prompt templates.
      sources/                 # External reference materials.
    pdd-algo/                  # 拼多多算法笔试
      python_oj_template.py    # Utility function library (importable helpers, not a skeleton).
      solutions_batch.py       # Exam problem solution collection (annotated solve() functions).
      practice/                # 按算法专题分类的练习题
      solutions/               # Individual problem solution write-ups.
      topic_checklist.md       # Topic coverage tracking (OJ patterns + AI/ML topics).
      mistake_log.md           # WA/TLE/error patterns by topic — feeds into algo-annotation.
      mock_exam_log.md         # Timed practice records.
      progress/                # Target-specific progress tracking.

  shared/                      # Cross-target shared content.
    cheatsheets/               # Generic quick-reference notes (not target-specific).
      llm_core_cheatsheet.md, sft_lora_miniproject.md, agent_project_pitch.md
      transformer-forward-pass.md, transformer-review.md
    daily/                     # Daily plans with time-capped tasks and Problem Log.
    exam_memory/               # MCP Server: cross-session experience persistence.
      server.py                # MCP tools: experiences, profile, sources, review schedule.
      experiences/             # YAML frontmatter + Markdown experience files.
      user_profile.json        # User strengths/weaknesses/preferences.
    progress/                  # Cross-target progress tracking.
      README.md                # 目录索引和存放规则
      task-board.md
    prompts/                   # Generic prompt templates.

  algorithms/                  # Stub directory (code moved to targets/pdd-algo/).
  exam_memory/                 # Legacy stub (code moved to shared/exam_memory/).
  progress/                    # Top-level stub directories (content in targets/ or shared/).
    choice-questions/.gitkeep, study-planning/.gitkeep, exam-analysis/.gitkeep
    task-board/.gitkeep, reviews/.gitkeep
  prompts/
    new_session_prompt.md      # Session startup prompt template.

  .mcp.json                    # MCP server registration (exam-memory via stdio).

  docs/                        # Dev-only design/review/plan notes; new files are ignored by default and force-added on dev when referenced.
    dev-roadmap.md             # Internal development roadmap.
    INDEX.md                   # dev-only docs index and status tracking.
```

### MCP Integration Architecture

本项目依赖一个自定义 MCP Server 和 Claude Code 内置工具链。理解 MCP 调用机制是正确运行 harness 的前提。

#### MCP 注册（`.mcp.json`）

```
exam-memory (stdio) → python shared/exam_memory/server.py
  ├── list_experiences    — 按题型检索经验（error_count 降序）+ V2 语义检索（query 参数）
  ├── save_experience     — 保存新经验条目（自动编号）+ V2 自动向量化入库
  ├── inc_error_count     — 经验错误计数 +1
  ├── get_user_profile    — 读取用户画像 JSON
  ├── update_user_profile — 增量合并画像字段
  ├── mount_source        — 挂载本地知识源
  ├── list_sources        — 列出已挂载知识源
  └── fetch_from_source   — 从知识源检索内容
```

#### MCP Tool Naming Convention

Claude Code 调用 MCP 工具时使用 **双下划线前缀格式**：

```
mcp__<server-name>__<tool-name>
```

实际调用示例：
```
mcp__exam-memory__list_experiences(type="单选题", limit=5)
mcp__exam-memory__save_experience(title="...", content="...", type="算法", knowledge="双指针")
mcp__exam-memory__inc_error_count(file_path="算法_双指针_001.md")
```

Skill 文档中为简洁使用短名（如 `list_experiences`），agent 在实际执行时必须使用完整前缀格式。

#### Skill → MCP 依赖矩阵

| Skill | MCP 工具 | 是否必需 | Graceful Degradation |
|-------|---------|---------|---------------------|
| solve-skeleton | 无 | N/A | 纯本地 |
| algo-annotation | 无 | N/A | 纯本地，仅读 mistake_log.md |
| choice-q-create | `list_experiences` | 可选 | MCP 不可用时依赖 `exam_config.md` + Markdown 文件；无历史时使用默认高频主题 |
| choice-q-drill | `save_experience`, `inc_error_count` | 可选 | MCP 不可用时本地写入 Markdown；无写权限时返回 append blocks |
| solve-analyze | `list_experiences`, `save_experience`, `inc_error_count`, `update_user_profile` | 可选 | MCP 不可用时仅写 mistake_log.md，跳过画像更新和经验持久化 |
| exam-assistant | exam-memory 经验与画像工具 | 可选 | MCP 不可用时读取本地 Markdown / 当前对话；无写权限时返回 append blocks |
| review-tracker | 无 | N/A | 纯本地；缺失文件输出"暂无数据"并给出今日可执行清单 |

#### Runtime Mode Contract

本 harness 有三档运行模式，三档都必须保持 intake -> practice -> record -> review -> handoff 的最小闭环。

| Mode | 自动选择条件 | 状态读写 | 适用场景 |
|------|--------------|----------|----------|
| **Full MCP Mode** | `exam-memory` MCP 可调用，且仓库可写 | Markdown + MCP 双写；MCP 可增强结构化检索、错误频率和用户画像 | 长期个人备考 |
| **Local Markdown Mode** | MCP 不可用，但仓库文件可读写 | `HANDOFF.md`、`shared/daily/`、`targets/{target}/mistake_log.md`、round 文件 | 默认低配置工作流 |
| **Stateless Lite Mode** | 仓库不可写、文件缺失严重，或只能在聊天中继续 | 在最终输出中返回 `[MISTAKE_LOG_APPEND]`、`[DAILY_PROBLEM_LOG_APPEND]`、`[CHOICE_ROUND_SUMMARY]`、`[HANDOFF_UPDATE]` 等可落盘块 | 临时环境、新用户启动、故障恢复 |

自动选择优先级：
1. MCP 可调用 + 仓库可写 -> Full MCP Mode。
2. 仓库可写但 MCP 不可用 -> Local Markdown Mode。
3. 无写权限、聊天转交、或关键文件无法创建 -> Stateless Lite Mode。

统一降级策略：
- MCP、ChatMem、本地数据库/索引、交互式 quiz 工具不可用时，不中断练习流程。
- 流程内部可以安静跳过不可用增强能力，但最终报告必须说明当前处于哪种降级模式、哪些能力被跳过、哪些 Markdown append blocks 需要落盘。
- Stateless Lite Mode 只适合临时环境、新用户启动和故障恢复；不建议长期作为唯一工作流。长期备考至少迁移到 Local Markdown Mode，最好启用 Full MCP Mode。
- 标准降级提醒：

```text
当前为 Lite/Portable Mode：未检测到 exam-memory MCP / 本地数据库 / ChatMem 或交互式 quiz 工具。
本轮仍可完成出题、答题、错题记录和交接，但跨会话语义检索、错误频率自动合并、用户画像更新不可用。
请务必把本轮输出的 MISTAKE_LOG_APPEND、DAILY_PROBLEM_LOG_APPEND、CHOICE_ROUND_SUMMARY、HANDOFF_UPDATE 落到 Markdown。
该模式适合临时环境、新用户启动和故障恢复，不建议长期作为唯一工作流。
```

#### 跨会话记忆机制（双通道）

```
                ┌─── mistake_log.md ───────────────────────────────────────────┐
                │   本地文件，快速读写                                           │
                │   用途：algo-annotation # [防错] 标记、考前速看               │
 错误发生 ──────┤   格式：Markdown 表格（Date/Problem/Topic/Root Cause/Fix）    │
                │   生命周期：单次备考周期                                       │
                │                                                              │
                └─── exam-memory MCP ──────────────────────────────────────────┘
                    结构化经验库，YAML frontmatter + Markdown
                    用途：choice-q-create 出题定向、exam-assistant 经验检索
                    格式：单文件 = 单条经验（类型/知识点/难度/error_count）
                    生命周期：跨会话持久化
```

两个通道**互补**，不互相替代：
- `mistake_log.md` 是为 **人类考前速读** 和 **annotation skill 自动引用** 优化的。
- `exam-memory MCP` 是为 **结构化检索** 和 **跨会话错误频率追踪** 优化的。
- `choice-q-drill` 的双写逻辑确保两边同步。

#### 错误记录归属

- **算法错误**：`mistake_log.md` 为权威数据源（被 algo-annotation `# [防错]` 引用）
- **选择题错误**：Full MCP Mode 下，exam-memory 可作为结构化经验与错误频率的增强来源；Local Markdown / Stateless Lite 下，`mistake_log.md`、choice round 文件和最终报告是主要记录。
- `choice-q-drill` 双写两个通道，不冲突：本地快速查阅用 mistake_log，跨会话检索用 MCP
- 写入前自动去重（§4b）：mistake_log 同一题号不重复写入，MCP 同一经验不重复创建
- 如果两者不一致：先按当前可用运行模式判断。MCP 可用且记录完整时优先结构化 MCP；MCP 不可用或未同步时优先本地 Markdown 与本轮最终报告。

#### Mock 成绩归属

- **写入目标**：`targets/{target}/progress/choice-questions/round*.md`（choice-q-drill 每次答题后写入）
- **派生快照**：`targets/{target}/progress/exam-analysis/exam-style-analysis.md` §5（手动更新，非实时数据）
- 每次 choice-q-drill 完成后，应手动更新 exam-analysis/exam-style-analysis.md §5 的汇总数据

#### 可用系统级 MCP（非项目注册）

以下 MCP 由 Claude Code 环境全局配置，非本项目 `.mcp.json` 注册，但在特定场景下可用：

| MCP Server | 本项目中的潜在用途 | 何时使用 |
|-----------|------------------|---------|
| ChatMem | 跨会话项目记忆、对话历史检索、session handoff | "之前做过什么"、session 继续、项目历史 |
| mempalace | 结构化知识存储、跨 wing 知识图谱 | 长期备考知识管理（超出本项目范围） |

ChatMem 与 exam-memory 的定位区分：
- **exam-memory**：项目专用，结构化题目经验（错题模式、知识点、错误频率）。
- **ChatMem**：通用项目记忆，存储对话级上下文（决策历史、handoff、startup rules）。

### Data Flow

```
User input (problem statement)
  │
  ▼
[Skill: solve-skeleton] ──► reads problem, selects template, outputs solve() skeleton
  │                            references: io-modes.md, algo-skeletons.md, exam-patterns.md
  ▼
[solve() filled with logic]
  │
  ▼
[Skill: solve-analyze] ──► compares user code vs standard solution, identifies root cause tags
  │                            references: root-cause-tags.md, comparison-template.md
  │                            feedback: mistake_log.md + MCP (optional)
  ▼
[Skill: algo-annotation] ──► adds Chinese comments, # [防错] markers, cross-refs mistake_log.md
  │
  ▼
[Record in shared/daily/YYYY-MM-DD.md Problem Log + targets/{target}/mistake_log.md]
  │
  ▼
[Review: targets/{target}/progress/task-board/task-board.md + targets/{target}/progress/study-planning/readiness-score.md + targets/{target}/progress/reviews/]
  │
  ▼
[Skill: review-tracker] ──► aggregates all data sources into progress report
  │                            outputs: readiness trends, error stats, coverage gaps, today's must-do
  ▼
[Handoff: HANDOFF.md updated before session ends]
```

### MCP Feedback Loop (exam-memory)

**MCP 状态**：`experiences/` 与 `user_profile.json` 是本地运行态数据，公开模板只说明其用途，不承诺仓库内已有记录、画像已初始化或 MCP 写路径可用。每次会话在调用 MCP 依赖 skill 前应按 pre-flight 结果选择 Full MCP / Local Markdown / Stateless Lite 模式。

```
choice-q-drill (quiz results)
  │
  ├──► mistake_log.md (local harness feedback — format-optimized for quick review)
  │
  └──► exam-memory MCP (cross-session persistence)
        │
        ├──► mcp__exam-memory__save_experience() — new error patterns
        ├──► mcp__exam-memory__inc_error_count() — repeated patterns get higher priority
        │
        ▼
        mcp__exam-memory__list_experiences() — fed back into next choice-q-create session
        │
        ├──► choice-q-create reads both mistake_log.md AND MCP experiences
        │    to prioritize weak topics with maximum signal
        │
        └──► skills/exam-assistant.md — full assistant workflow with
             user profile, error tracking, and web search integration
             (web search 使用 Claude Code 内置 WebSearch)
```

**MCP 不可用时的降级行为**：
- `choice-q-create`：使用 `exam_config.md` + `mistake_log.md` + 历史题库；历史文件缺失时使用默认高频主题并标注"暂无数据"。
- `choice-q-drill`：仓库可写时写入 `mistake_log.md` / daily log；仓库不可写时返回 `[MISTAKE_LOG_APPEND]`、`[DAILY_PROBLEM_LOG_APPEND]`、`[CHOICE_ROUND_SUMMARY]`、`[HANDOFF_UPDATE]`。
- `solve-analyze`：仅写入 `mistake_log.md`，跳过画像更新和经验 MCP 持久化。
- `exam-assistant`：读取本地 Markdown 和当前对话；无法持久化时返回 append/update blocks。
- `review-tracker`：缺失数据源输出"暂无数据"，仍给出今日三项可执行清单。

降级时最终报告必须提醒用户能力已降级、跨会话能力不可用、需要把 append blocks 落到 Markdown，并说明 Lite/Portable Mode 不建议长期作为唯一工作流。

The two feedback loops serve different purposes:
- **mistake_log.md**: quick-reference for algo-annotation `# [防错]` markers, human-readable for 考前速看
- **exam-memory MCP**: persistent across sessions, supports semantic filtering by type/knowledge, tracks error frequency

### Skill Pipeline

The two skills form a **sequential pipeline** — solve-skeleton creates structure, algo-annotation adds pedagogy:

1. **solve-skeleton** — invoked when starting any OJ problem. Reads problem keywords → selects I/O mode and algorithm template → outputs a bare-bones `solve()` with TODO markers. Also provides an anti-pattern checklist to catch common WA/TLE causes before running. **无 MCP 依赖**。

3. **solve-analyze** — invoked after the user fills in a `solve()` and wants diagnosis. Runs two parallel analysis paths: Agent A statically analyzes the user's code for logic errors and anti-patterns; Agent B generates a standard solution via the solve-skeleton pipeline. Merges results into a structured comparison report, extracts root cause tags from `references/root-cause-tags.md`, and triggers feedback loops to `mistake_log.md` (automatic), `user_profile` (MCP, optional), and `exam-memory` (MCP, optional). **MCP 可选——不可用时仅写 mistake_log.md**。

4. **algo-annotation** — invoked after `solve()` is complete (or after solve-analyze produces a report). Adds Chinese line-level comments, `# [防错]` markers pulled from `targets/{target}/mistake_log.md`, and a one-sentence summary of the core invariant. **无 MCP 依赖**。

**When to invoke**: Always use solve-skeleton first. After filling in logic, optionally invoke solve-analyze for diagnosis, then algo-annotation for comments. Never skip the skeleton step — it enforces the correct `input = sys.stdin.readline` pattern and prevents the `sys.stdin.buffer` trap that breaks mixed string/numeric input.

The **choice-q pipeline** targets the 选择题/多选题 section (format from `targets/{target}/exam_config.md`, a **pure local file read — no MCP dependency**). It uses a **create → drill → feedback loop**:

1. **choice-q-create** — generates a targeted set of multiple-choice questions. Combines web search for latest exam patterns, `targets/{target}/mistake_log.md` for known weak spots, `targets/{target}/sources/` for historical pattern coverage, and **可选** `mcp__exam-memory__list_experiences()` for cross-session error patterns. Questions generated per `targets/{target}/exam_config.md` format. Outputs questions with answer keys and topic tags. **MCP 可选——不可用时仅依赖本地文件**。

2. **choice-q-drill** — runs the generated question set as an interactive quiz when AskUserQuestion is available, or accepts chat-answer mode such as `1A 2BD 3C` when interactive quiz tooling is unavailable. It scores answers immediately and records per-question results. After completion, **本地优先写入** `targets/{target}/mistake_log.md` / daily log；MCP 可用时再双写 `mcp__exam-memory__save_experience()` / `mcp__exam-memory__inc_error_count()`。无写权限时返回 append blocks。

**When to invoke**: Use choice-q-create first to generate a question set, then choice-q-drill to run the interactive quiz. After each drill session, results flow into `targets/{target}/mistake_log.md`, which feeds back into the next choice-q-create call to prioritize weak topics. This closed loop ensures weak areas get progressively more coverage.

The **exam-assistant** skill provides a full interactive assistant workflow. It uses exam-memory MCP tools (`list_experiences`, `save_experience`, `inc_error_count`, `get_user_profile`, `update_user_profile`) when available, plus Claude Code 内置 `WebSearch` only when requested. MCP 不可用时改用 Local Markdown / Lite blocks，不把 MCP 当作必调前置条件。

The **review-tracker** skill aggregates progress across all data sources (task-board, study-planning/readiness-score, mistake_log, topic_checklist, daily logs, choice-questions files) into a single structured report. It outputs readiness score trends, unresolved error counts by Root Cause, topic coverage gaps, and a prioritized "today's must-do" list. Also supports self-assessment scoring to update study-planning/readiness-score.md. **无 MCP 依赖，纯本地文件读取**。

**When to invoke**: At session start for progress awareness, after practice sessions for summary, or when the user asks "复习进度" / "还差什么" / "今天复习什么". Also triggers when distance to exam ≤ 1 day for a condensed "考前速查模式".

## Operating Rules For Future Agents

- Answer and write task notes in Chinese unless the user asks otherwise.
- Treat this as an execution harness, not a research project.
- Do not spend a session doing broad public-source research unless the user explicitly asks.
- Do not overfit to one company's rumored problem list. Practice transferable OJ patterns.
- Do not spend more than 1 hour blocked on environment deployment, CUDA, local fine-tuning, or cloud setup. Fall back to Colab or skip the deployment detail.
- Prefer Python 3, stdin/stdout ACM templates, and simple readable solutions.
- For algorithm tasks, always record wrong answers, timeout causes, and missing patterns in `targets/{target}/mistake_log.md`.
- For timed practice, always record problem count, solved count, stuck points, and next fixes in `targets/{target}/mock_exam_log.md`.
- Keep edits scoped to this folder unless the user explicitly asks otherwise.
- If using ChatMem, treat indexed local-history hits as evidence, not approved facts. Ask before expanding old conversations.
- **Branch Boundary**：
  - `docs/**`、`skills/branch-ops.md`、`skills/dev-review-flow/**`、`skills/harness-dev-flow/**`、`prompts/review-fix-session-prompt.md` 是 dev-only governance 内容，可在 `dev` tracked，但不得进入 `main`。
  - `.gitignore` 是第一层防误加护栏，不是发布判断；main extraction 必须检查 staged file allowlist/denylist。
  - 新建被引用的 dev-only docs/skill 文件时，只能在 `dev` 用精确路径 `git add -f -- <path>`；禁止 `git add -f .`，也禁止在 `main` 或 main extraction 期间 force-add。
- **MCP 调用规则**：
  - MCP 工具使用完整前缀格式：`mcp__exam-memory__<tool_name>`。
  - 调用 MCP 前先确认 `exam-memory` server 是否可用（`.mcp.json` 注册只是条件之一，实际工具仍可能不可调用）。
  - MCP 调用失败时流程内部**静默降级**：不影响主流程，仅跳过 MCP 写入/读取。
  - 最终报告必须显式提醒用户当前能力已降级、跨会话检索/画像/错误频率合并不可用，并给出需要落盘的 Markdown blocks。
  - 不要在 skill 输出中暴露 MCP 内部机制（用户不需要知道 MCP 命名格式）。

## Skill Invocation Protocol

This section tells agents **when** and **how** to invoke skills during a session.

### MCP Pre-flight Check

Before invoking any MCP-dependent skill, verify:
1. `exam-memory` server is registered in `.mcp.json` (present in project root).
2. MCP tool calls use full prefix: `mcp__exam-memory__<tool_name>`.
3. If MCP call fails (server not running, tool unavailable, network error), continue in Local Markdown or Stateless Lite mode.
4. Do not retry MCP long enough to block practice. Mention skipped persistence/retrieval in the final report.

### Starting a New Session

0. **First time?** If `HANDOFF.md` still has template placeholders, invoke `init-guide` first:
   ```
   Skill(skill="init-guide")
   ```
   Trigger phrases: "初始化"、"init"、"第一次用"、"开始配置"、"换一个考试目标"
   This collects exam target, date, scope, and updates HANDOFF.md + user profile + AGENTS.md.

1. Read `START_HERE.md` (bootstrap order).
2. Read `HANDOFF.md` (last session's status).
3. Open today's `shared/daily/YYYY-MM-DD.md`.

### Starting an OJ Problem

**Always** invoke `solve-skeleton` first:

```
Skill(skill="solve-skeleton")
```

Then follow the 6-step workflow from `skills/solve-skeleton/SKILL.md`:
1. Read problem, note input/output format and n constraints.
2. Match keywords to template table in SKILL.md section 3.
3. Copy skeleton from `references/` into the Algorithm phase.
4. Fill TODOs (no comments yet — annotation comes later).
5. Run anti-pattern checklist from SKILL.md section 2.
6. Once `solve()` passes: invoke `algo-annotation`.

### Diagnosing a Solution

When the user has a completed `solve()` and wants to know what went wrong:

```
Skill(skill="solve-analyze")
```

Trigger phrases:
- "分析一下我的代码"
- "帮我看看哪里错了"
- "对比一下"
- "review my solve"
- "为什么WA"
- "为什么超时"
- "解法对比"
- "代码诊断"

The analyze skill will:
- Run two parallel analysis paths: static analysis of user code vs standard solution generation via solve-skeleton.
- Produce a structured comparison report using `references/comparison-template.md`.
- Extract root cause tags from `references/root-cause-tags.md`.
- Automatically append to `targets/{target}/mistake_log.md` (deduplicated).
- Optionally update `mcp__exam-memory__update_user_profile()` and `mcp__exam-memory__save_experience()` / `mcp__exam-memory__inc_error_count()`. MCP failures are silent.
- After the report, direct the user to invoke `algo-annotation` for `# [防错]` markers on the corrected code.

### Annotating a Solution

After `solve()` is working (or after solve-analyze diagnosis):

```
Skill(skill="algo-annotation")
```

The annotation skill will:
- Add Chinese line-level comments.
- Tag pitfalls with `# [防错]` linked to `targets/{target}/mistake_log.md`.
- Tag dual-role data with `# [双重角色]`.
- Provide a one-sentence summary of the core invariant.

### Generating Choice-Question Sets

When the user wants to practice 选择题/多选题, or before a timed mock exam:

```
Skill(skill="choice-q-create")
```

Trigger phrases:
- "出一套选择题"
- "生成选择题练习"
- "choice question practice"
- "多选题专项训练"
- "帮我准备选择题"

The create skill will:
- Scan `targets/{target}/mistake_log.md` for weak topics (低频 topic tags, repeated WA areas).
- Check `targets/{target}/sources/` for historical exam patterns (按目标组织)。
- **可选**：调用 `mcp__exam-memory__list_experiences(type="单选题", limit=5)` 和 `mcp__exam-memory__list_experiences(type="多选题", limit=5)` 获取跨会话错误模式。MCP 不可用时跳过。
- Search the web for latest exam-style questions if requested (使用 Claude Code 内置 WebSearch)。
- Output a numbered question set with topics, answer keys, and explanations.

### Drilling Choice Questions

After a question set is generated (or from a saved set):

```
Skill(skill="choice-q-drill")
```

Trigger phrases:
- "开始刷题"
- "drill mode"
- "做选择题"
- "开始选择题练习"
- "quiz mode"

The drill skill will:
- Present questions using AskUserQuestion when available; otherwise accept chat-answer mode such as `1A 2BD 3C`.
- Score each answer immediately (correct/incorrect/partial for multi-select).
- Track time per question and total session time.
- After completion, append results to `targets/{target}/mistake_log.md` and `shared/daily/YYYY-MM-DD.md` when the repo is writable.
- If the repo is not writable, return `[CHOICE_ROUND_SUMMARY]`, `[MISTAKE_LOG_APPEND]`, `[DAILY_PROBLEM_LOG_APPEND]`, and `[HANDOFF_UPDATE]`.
- **可选 MCP 双写**：对每道错题，先查 `mcp__exam-memory__list_experiences` 是否有匹配经验，有则 `mcp__exam-memory__inc_error_count()`，无则 `mcp__exam-memory__save_experience()`。MCP 不可用时跳过。
- Return a summary: score, per-topic accuracy, weakest topics flagged for next session.

### Checking Review Progress

When the user wants to see overall preparation status:

```
Skill(skill="review-tracker")
```

Trigger phrases:
- "复习进度"
- "进度报告"
- "还差什么"
- "今天复习什么"
- "自评打分"
- "readiness"

The review-tracker skill will:
- Read all data sources (task-board, study-planning/readiness-score, mistake_log, topic_checklist, daily logs, choice-questions files).
- Generate a 7-section progress report with readiness trends, error stats, coverage gaps, and today's must-do list.
- Support "自评打分" to update `targets/{target}/progress/study-planning/readiness-score.md` with new self-assessment scores.
- Switch to condensed "考前速查模式" when exam is ≤ 1 day away.

### After Each Problem

1. Write Problem Log entry in today's `shared/daily/` file.
2. If WA/TLE: append entry to `targets/{target}/mistake_log.md` (pattern, cause, fix).
3. Update `targets/{target}/progress/task-board/task-board.md` if topic priority changes.
4. Update `targets/{target}/progress/study-planning/readiness-score.md` after significant progress.

### Error Feedback Loop

```
mistake_log.md (recorded WA pattern)
  │
  ├──► algo-annotation references it via # [防错] markers
  │
  ├──► choice-q-create reads it to prioritize weak topics in next question set
  │
  ├──► solve-analyze reads it to cross-reference known patterns during diagnosis
  │
  ├──► topic_checklist.md flags the topic for extra practice
  │
  └──► task_board.md adjusts P0/P1 priority if pattern is frequent

solve-analyze (diagnosis results)
  │
  ├──► appends root-cause-tagged entries back into mistake_log.md (deduplicated)
  │
  ├──► (MCP 可用时) update_user_profile with weakness increments
  │
  └──► (MCP 可用时) save_experience / inc_error_count for cross-session tracking

choice-q-drill (quiz session results)
  │
  ├──► appends per-topic error data back into mistake_log.md
  │
  └──► (MCP 可用时) 双写 exam-memory MCP
       ├──► mcp__exam-memory__save_experience() — 新错误模式
       └──► mcp__exam-memory__inc_error_count() — 重复错误频率 +1

choice-q-create (MCP 增强)
  │
  └──► (MCP 可用时) mcp__exam-memory__list_experiences()
       获取跨会话错误模式，与 mistake_log.md 合并决定出题重点
       MCP 不可用时 → 仅依赖 mistake_log.md
```

New WA patterns discovered during practice must flow into `mistake_log.md` so annotation skill can reference them. This is the only durable feedback mechanism in the harness — without it, the same mistakes repeat. MCP 经验库是可选的增强层，不是替代。

## Daily Workflow

1. Read `START_HERE.md`.
2. Open today's file under `shared/daily/`.
3. Pick a 3-hour minimum plan and optional 5-hour stretch.
4. Do algorithms first under time pressure.
5. Review LLM notes second.
6. Update `targets/{target}/progress/task-board/task-board.md`, `targets/{target}/progress/study-planning/readiness-score.md`, and the relevant logs.
7. Update `HANDOFF.md` before ending a session.

## Algorithm Practice Rules

- Always solve with ACM input/output in mind.
- Write the brute-force idea briefly before optimizing.
- If stuck for 20 minutes, inspect hints or an editorial, then re-code from memory.
- If a solution passes, still write one sentence about the invariant or trick.
- Prioritize: hash/sort, binary search, prefix sum, sliding window, greedy, BFS/DFS, heap, simple DP.
- Avoid advanced topics unless repeated mock exams show they are necessary.

### 真题 vs 练习题存放规则

- 考试真题 / 模拟题的解答 → `targets/{target}/solutions/`（统一编号管理）。
- 非考试来源的练习题 → `targets/{target}/practice/`，按算法专题命名文件（如 `sliding_window.py`、`binary_search.py`）。
- 两者都走 solve-skeleton → algo-annotation 完整流程。

### OJ Practice Workflow (with Skills)

Every OJ problem follows this pipeline:

```
Problem statement
  → [solve-skeleton] select template, output bare-bones solve()
    → fill TODOs, run anti-pattern checklist
      → test solution
        → [solve-analyze] diagnose errors, compare vs standard solution (optional but recommended)
          → feedback: mistake_log.md + MCP (optional)
            → [algo-annotation] add Chinese comments + # [防错]
              → log to mistake_log.md if errors occurred
                → update daily Problem Log
```

## LLM Review Rules

Cover only high-yield written-exam/interview concepts:

- Transformer and attention.
- SFT, LoRA, QLoRA.
- RLHF and DPO.
- RAG and Agent.
- KV cache and inference optimization.
- Evaluation and hallucination control.
- **LLaMA3 架构细节**：RoPE、GQA、SwiGLU、RMSNorm（选择题高频）。
- **GNN 基础**：GCN/GAT、消息传递框架、图任务类型（岗位 JD 明确要求）。
- **扩散模型基础**：DDPM 前向/反向、条件生成、Latent Diffusion（岗位 JD 明确要求）。
- **数学基础**：线性代数、概率统计、微积分选择题速记（笔试必考）。
- **目标公司认知**：核心项目、技术方向、评测平台（按目标岗位调整 `targets/{target}/cheatsheets/ai_lab_context.md`）。

## Mini-Project Rule

The LoRA/SFT mini-project is optional proof of hands-on ability. It must not consume the main preparation week. If local GPU setup is not smooth within 1 hour, use Colab or convert the work into an interview-ready plan.

## Handoff Rule

Before any session ends, update `HANDOFF.md` with:

- What was completed.
- What evidence was used.
- Today's algorithm results.
- Today's LLM review result.
- Next concrete task.
- Any blockers.
