---
name: choice-q-create
description: >
  Generate targeted multiple-choice question sets for the target exam (from exam_config.md).
  Use this skill whenever the user asks for new practice questions — even casual requests
  like "出几道题练练" or "帮我准备一下选择题" or "再来一套". Trigger phrases: "准备选择题",
  "出题", "新题", "选择题制作", "generate choice questions", "new mock", "新一轮选择题",
  "choice q round", "再出一套", "出一套新题", "出几道", "准备一套", "mock", "刷题题库",
  "帮我出题", "选题". Also use when the user wants targeted practice on specific weak topics
  (e.g. "帮我出几道GNN的题"), or when combining web search + historical patterns +
  mistake_log to create targeted practice material. After generation, direct the user to
  `choice-q-drill` for interactive answering.
---

# Choice Question Creation Skill

Generate targeted multiple-choice question sets for the target exam.
Combines exam_config, local Markdown history, optional historical problem bank, and optional
cross-session experience patterns from the exam-memory MCP server to create practice material.
Outputs a self-contained markdown file when the repo is writable, or a chat-ready question set
plus Lite append templates when persistence cannot be guaranteed.

The create skill reads from `exam_config.md` first, then local Markdown feedback such as
`mistake_log.md` and prior round files. `mcp__exam-memory__list_experiences` is an optional
Full MCP Mode enhancement. Topics appearing in both local and MCP sources get highest priority,
but missing history is not a blocker.

## 0. Runtime Modes

| Mode | Behavior |
|------|----------|
| Full MCP Mode | Read Markdown + optional MCP experiences; write `roundN.md`. |
| Local Markdown Mode | Read/write repository Markdown only; no MCP calls required. |
| Stateless Lite Mode | If the repo cannot be written, return the full question set in chat plus `[CHOICE_ROUND_SUMMARY]` and handoff/update templates. |

When degraded, the final message must state which history/retrieval capabilities were skipped and warn that Lite/Portable Mode is only for temporary environments, first-run startup, and recovery.

## 1. Exam Format Reference

> **从 `targets/{target}/exam_config.md` 读取**。以下为格式模板，运行时以 exam_config 为准。

| Item | Value |
|------|-------|
| 单选题 | N 题 × X 分 = XX 分 |
| 不定项选择题 | N 题 × X 分 = XX 分 |
| 选择题合计 | {总题数} 题, {总分} 分 |
| 时间建议 | 见 exam_config.md |
| 多选策略 | 见 exam_config.md |

## 2. Topic Pool

Draw questions from these 12 domains, balanced across rounds:

| Category | Key Topics | Source |
|----------|-----------|--------|
| 线性代数 | 特征值、SVD、正交/正定、行列式 | `targets/{target}/cheatsheets/math_fundamentals.md` |
| 概率统计 | 贝叶斯、分布、独立vs不相关 | `targets/{target}/cheatsheets/math_fundamentals.md` |
| 微积分/优化 | 链式法则、梯度、凸函数、SGD | `targets/{target}/cheatsheets/math_fundamentals.md` |
| DL 基础 | Softmax、BN、CNN、参数量计算 | `shared/cheatsheets/llm_core_cheatsheet.md` |
| Transformer | 注意力、位置编码、KV cache | `shared/cheatsheets/llm_core_cheatsheet.md` |
| LLM 架构 | LLaMA3、GQA/MQA、RoPE、SwiGLU | `shared/cheatsheets/llm_core_cheatsheet.md` |
| 微调/对齐 | LoRA/QLoRA、RLHF/DPO | `shared/cheatsheets/llm_core_cheatsheet.md` |
| RAG/Agent | RAG流程、ReAct、Function Calling | `shared/cheatsheets/llm_core_cheatsheet.md` |
| GNN | GCN vs GAT、过平滑、消息传递 | `targets/{target}/cheatsheets/gnn_diffusion_cheatsheet.md` |
| 扩散模型 | DDPM/DDIM、CFG、Latent Diffusion | `targets/{target}/cheatsheets/gnn_diffusion_cheatsheet.md` |
| 推理优化 | KV Cache、量化、FlashAttention | `shared/cheatsheets/llm_core_cheatsheet.md` |
| 数据结构 | 栈/队列、排序、哈希 | `targets/{target}/mistake_log.md` |

## 3. Question Quality Rules

### Single-choice (单选)
- Exactly 4 options (A/B/C/D), exactly 1 correct.
- Distractors must be plausible — based on common misconceptions from `mistake_log.md`.
- Each question tests ONE clear concept.
- Prefer "下列说法**错误**的是" or "下列说法**正确**的是" format.

### Multi-choice (不定项)
- Exactly 4 options (A/B/C/D), 1-4 correct.
- Clearly state: "漏选得 2 分，多选/错选 0 分".
- Options should be independently evaluable — each is a standalone true/false claim.
- At least one question should be "全选" or "单选" to test confidence.

### Difficulty distribution per round
- 60% concept recall (direct knowledge test)
- 30% application (calculate, compare, reason)
- 10% trap (subtle distinction, common misconception)

## 4. Weak Point Targeting

0. **Read mastery data** — check `targets/{target}/progress/exam-analysis/exam-style-analysis.md` §6 "知识点掌握进度" for mastery levels per topic. Also read `targets/{target}/mistake_log.md` Mastery column. This is the **canonical source** for mastery info; prefer it over re-querying exam-memory MCP.

Before generating, try to read `targets/{target}/progress/exam-analysis/exam-style-analysis.md` §2 频率表 and §4 趋势预测 to calibrate
the topic allocation ratio. If that file is missing, mark related fields as "暂无数据" and fall back to `exam_config.md` plus the default high-yield topics in §2; do not invent historical patterns.
Use §4.2 选择题预测 when available to identify which domains to overweight based on historical exam patterns.
Then read `targets/{target}/mistake_log.md` when available and check:
1. Which topics have the most errors? → Allocate 2-3 questions there.
2. Which errors have `Redo Date` that hasn't passed? → Include reinforcement questions.
3. **Cross-session experience patterns** — call `mcp__exam-memory__list_experiences(type="单选题", limit=5)` and `mcp__exam-memory__list_experiences(type="多选题", limit=5)` to retrieve persistent error patterns from the exam-memory MCP server. These patterns survive across sessions and capture errors that may not yet be in mistake_log.md. If the MCP exposes mastery levels (e.g. per-knowledge mastery scores), also query them — but note that `targets/{target}/progress/exam-analysis/exam-style-analysis.md` §6 is the canonical source and should be preferred. If exam-memory does not yet expose mastery levels, use `error_count` as a proxy for `struggling` topics. Merge these with mistake_log findings — topics appearing in BOTH sources get highest priority. **MCP 不可用时跳过此步骤**。
4. **Mastery-driven allocation** — For each topic, determine mastery level:
   - `blind_spot` → allocate 2-3 questions (highest priority, user doesn't really know it)
   - `struggling` → allocate 2 questions (high priority)
   - `unknown` → allocate 1 question + 1 variant (exploration)
   - `confirmed` → allocate 0-1 question (low priority, just for reinforcement)

   Phase-aware adjustment (if user specified a phase in last drill session):
   - Phase 1 (主攻盲区): blind_spot + struggling get 70% of questions
   - Phase 2 (补盲+拓展): 50% blind_spot/struggling + 50% new
   - Phase 3 (全真模拟): even distribution across 12 domains
   - Phase 4 (考前冲刺): only high-frequency mistake_log topics
5. Which `Root Cause` tags appear most (pattern/proof/python)? → Balance question types.

Also check `targets/{target}/progress/choice-questions/round*.md` for previously used questions. If no previous rounds exist, set duplication history to "暂无数据" and only avoid duplicates within the current generated set.

### 4b. 零历史 / Portable 兜底

When `mistake_log.md`, prior round files, or exam analysis files are missing:

1. Read `targets/{target}/exam_config.md` to get counts, scoring, time, and multi-select policy.
2. Use this 默认高频 topic pool unless the user specifies a topic: Transformer attention/KV cache, LLaMA3 RoPE-GQA-SwiGLU-RMSNorm, LoRA/QLoRA/RLHF/DPO, RAG/Agent, GNN message passing/over-smoothing, diffusion DDPM/DDIM/CFG, linear algebra eigen/SVD/PSD, probability Bayes/distributions, calculus gradients/convexity, Python OJ hash/sort/binary search/sliding window.
3. Label historical fields as "暂无数据" in coverage and provenance tables.
4. Do not fabricate prior mistakes, scores, mastery levels, or source files.
5. If write access is unavailable, return the questions directly in chat and include:

```text
[CHOICE_ROUND_SUMMARY]
题号 | 你的答案 | 正确答案 | 得分 | 知识点 | 是否写入错题

[HANDOFF_UPDATE]
Today's Results / Next Steps / Blockers
```

## 5. Web Search Integration

Use WebSearch for current/recent topics:
- "LLaMA3 architecture details 2024" — latest model specifics
- "GNN over-smoothing solutions" — new research angles
- "DDPM vs DDIM vs DPM-Solver" — sampling method comparisons
- "LoRA variants 2024 QLoRA DoRA" — new fine-tuning methods
- "RAG pipeline best practices" — latest retrieval patterns

Only search when a topic needs fresh material or the user requests it.

## 6. Output Format

Write the question set to `targets/{target}/progress/choice-questions/roundN.md` (N = next available number).
Use this exact structure:

```markdown
# 选择题模拟 — Round N

> {目标单位} | {岗位方向} | 考前模拟
> 时间：{见 exam_config.md} | 满分 {见 exam_config.md} 分
> 策略：单选每题 ≤ 2 分钟，多选每题 ≤ 3 分钟，不确定的多选宁可漏选不多选

---

## Part A：单选题（选唯一正确答案，分值见 exam_config.md）

### Q1. [Topic Tag]

[Question text]

A. ...
B. ...
C. ...
D. ...

---
(repeat for Q2-Q{单选题数})

## Part B：不定项选择题（漏选得部分分，多选/错选 0 分，分值见 exam_config.md）

### Q{单选题数+1}. [Topic Tag]

[Question text]

A. ...
B. ...
C. ...
D. ...

---
(repeat for Q{单选题数+2}-Q{总题数})

---

# 参考答案与解析

## Part A 单选题

### Q1 答案：X

**解析**：
- A：... ✓/✗
- B：... ✓/✗
- **C**：... ✓/✗ (bold the correct one)
- D：... ✓/✗

> **防错**：[one-line pitfall note from mistake_log if applicable]

---
(repeat for all questions)

## 成绩统计表

| 题号 | 你的答案 | 正确答案 | 得分 |
|------|----------|----------|------|
| Q1 | | X | /{分值} |
...
| **总分** | | | **/{总分}** |

## 覆盖知识点与错题溯源

| 题号 | 知识点 | 对应错题/薄弱点 |
|------|--------|----------------|
| Q1 | ... | ... |
...
```

## 7. Workflow

### 阶段一：数据采集（Agent 并行）

> **为什么用 Agent**：出题前需要读取多个数据源（exam-style-analysis、mistake_log、历史 round 文件、cheatsheets/ 笔记、MCP 经验）。这些文件体积大、内容多，逐文件进入主上下文会导致 token 浪费。通过 Agent 并行采集 + 摘要返回，主会话只拿到结构化出题参数。

```python
# 在 choice-q-create 被调用时，主会话启动 Agent 执行数据采集：
# Agent 读取全部数据源 → 返回出题参数 JSON → 主会话基于 JSON 出题
```

**Agent 数据采集任务**：

```
你是选择题出题数据助手。请读取以下文件并提取出题所需的结构化摘要，返回 JSON。

0. targets/{target}/exam_config.md（优先读取，确定考试格式参数）
   返回：{
     single_choice: { count: N, points_each: X, total: XX },
     multi_choice: { count: N, points_each: X, total: XX },
     total_time: str,
     choice_time: str,
     multi_strategy: str
   }

1. targets/{target}/progress/exam-analysis/exam-style-analysis.md
   返回：{
     frequency_table: [{模式, 频次, 占比, 代表题}],
     style_features: [str],
     trend_prediction: { 选择题预测: [str], 编程题预测: [str] },
     mock_scores: [{ round, date, score, total }],
     mastery_progress: {
       confirmed: [{topic, details}],
       struggling: [{topic, details}],
       blind_spot: [{topic, details}],
       unknown: [{topic, details}]
     }
   }

2. targets/{target}/mistake_log.md
   返回：{
     error_topics: [{topic, count, root_cause, fix_rule, redo_date}],
     root_cause_summary: { pattern: n, proof: n, python: n },
     high_frequency_errors: [{topic, count}]  # count >= 2
   }

3. targets/{target}/progress/choice-questions/round*.md
   返回：{
     existing_rounds: [{round, date, questions_covered: [topic_tags]}],
     used_topics: [str]  # 所有已出现过的知识点标签，用于去重
   }

4. targets/{target}/cheatsheets/math_fundamentals.md（如果存在）
   返回：{ available_topics: [str], key_formulas: [str] }

5. shared/cheatsheets/llm_core_cheatsheet.md（如果存在）
   返回：{ available_topics: [str] }

6. targets/{target}/cheatsheets/gnn_diffusion_cheatsheet.md（如果存在）
   返回：{ available_topics: [str] }

7. 调用 MCP（如果可用）：`mcp__exam-memory__list_experiences(type="单选题", limit=5)` 和 `mcp__exam-memory__list_experiences(type="多选题", limit=5)`
   返回：{ single_choice_experiences: [{title, knowledge, error_count}],
           multi_choice_experiences: [{title, knowledge, error_count}] }

如果某个文件不存在或为空，对应字段返回 null、空数组或 "暂无数据"。不要编造数据。
```

**降级规则**：Agent 不可用时，主会话回退到逐文件读取。MCP 不可用时跳过第 7 项。仓库不可写时不声称已保存 round 文件，改为 Stateless Lite chat output。

### 阶段二：出题
7. **Write questions** — generate all {总题数} based on the collected data
8. **Write answers & analysis** — full explanations with 防错 markers
9. **Save file when possible** — `targets/{target}/progress/choice-questions/roundN.md`
10. **Stateless fallback** — if saving is not possible, output the full round in chat and include `[CHOICE_ROUND_SUMMARY]`
11. **Report** — tell user the file is ready or that Lite blocks must be saved manually, then suggest invoking `choice-q-drill`

### 阶段三：输出

输出必须包含三部分：

1. `targets/{target}/progress/choice-questions/roundN.md` 文件路径；若未能写入，则说明当前为 Stateless Lite Mode。
2. 本轮题目覆盖摘要：单选/多选题数、覆盖知识点、重点补弱主题。
3. 下一步指令：建议用户调用 `choice-q-drill` 开始交互答题。
4. 降级提醒：若 MCP/历史/写入不可用，说明哪些能力跳过，并提醒 Lite/Portable Mode 不建议长期作为唯一工作流。

## 8. Cross-References

- `choice-q-drill` — interactive quiz mode for answering the generated questions
- `targets/{target}/progress/exam-analysis/exam-style-analysis.md` — 集中式出题风格分析：频率表、趋势预测、mock 成绩（**核心输入**）
- `targets/{target}/mistake_log.md` — error patterns to target and update
- `targets/{target}/sources/` — historical question patterns and high-frequency topics (按目标组织)
- `shared/cheatsheets/llm_core_cheatsheet.md` — LLM/DL source material
- `targets/{target}/cheatsheets/gnn_diffusion_cheatsheet.md` — GNN/diffusion source material
- `targets/{target}/cheatsheets/math_fundamentals.md` — math source material
- `exam-memory` MCP tools — optional cross-session persistent error patterns (mcp__exam-memory__list_experiences)
- `skills/exam-assistant.md` — MCP-aware exam assistant with local Markdown / Lite fallback
