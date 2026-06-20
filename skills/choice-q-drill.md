---
name: choice-q-drill
description: >
  Interactive quiz mode for multiple-choice exam practice. Use this skill whenever
  the user wants to answer, quiz, drill, or practice multiple-choice questions — even if
  they just say "做题" or "考我一下" or "来一套". Trigger phrases: "答题", "开始答题",
  "做题", "交互答题", "选择题练习", "drill", "quiz mode", "开始模拟", "模拟考试",
  "做选择题", "回答选择题", "start quiz", "test me", "考我", "测验", "刷题", "做一套",
  "模拟一下", "开始刷", "练选择题". Also use after `choice-q-create` has generated a
  question set and the user wants to go through it, or when the user opens a
  `targets/{target}/progress/choice-questions/round*.md` file and says "开始". Reads question files and presents them
  interactively using AskUserQuestion when available, or accepts compact chat answers such as
  `1A 2BD 3C` when interactive tooling is unavailable. After completion, updates local
  Markdown first and uses exam-memory MCP only as an optional enhancement.
---

# Choice Question Drill Skill

Interactive quiz mode for multiple-choice exam practice. Reads question files,
presents them one batch at a time using AskUserQuestion when available, or accepts
chat-answer mode when interactive tooling is unavailable. It scores immediately, tracks
results, and updates `targets/{target}/mistake_log.md` / daily logs first. The
exam-memory MCP server is optional cross-session persistence.

The drill→feedback loop is what turns one-time mistakes into lasting knowledge. Without
recording errors, the same blind spots keep recurring. Local Markdown is the minimum
durable loop; MCP dual-write adds cross-session retrieval and error-frequency merging
when available.

## Runtime Modes

| Mode | Behavior |
|------|----------|
| Full MCP Mode | 本地 Markdown 必写；MCP 可选双写，用于跨会话经验和 error_count。 |
| Local Markdown Mode | 本地必写 `mistake_log.md`、daily log、round score summary；MCP 不可用不阻塞。 |
| Stateless Lite Mode | 仓库不可写时不声称已保存，返回 `[CHOICE_ROUND_SUMMARY]`、`[MISTAKE_LOG_APPEND]`、`[DAILY_PROBLEM_LOG_APPEND]`、`[HANDOFF_UPDATE]`。 |

降级最终报告必须说明：MCP/交互式 quiz/写入能力是否不可用、哪些跨会话能力跳过、哪些 append blocks 需要落到 Markdown。Lite/Portable Mode 只适合临时环境、新用户启动和故障恢复，不建议长期作为唯一工作流。

## Mastery Levels

| Level | Meaning | Trigger |
|-------|---------|---------|
| `unknown` | Never encountered | No record in exam-memory or mistake_log |
| `blind_spot` | Lucky guess, doesn't understand | correct + confidence = 完全不懂，猜的 |
| `struggling` | Got wrong or uncertain | error_count >= 2 or recent error, or confidence = 猜的但有道理 |
| `confirmed` | Mastered, can explain | 2 consecutive correct + confidence = 确定会 |

Mastery is tracked per topic and drives adaptive phase selection (§6). A topic at
`blind_spot` is the highest priority for remediation.

## 1. Core Mechanism

Use the **AskUserQuestion** tool to present questions interactively when available:

- **Single-choice (单选)**: Present 4 questions per batch, each as a separate AskUserQuestion
  call with `multiSelect: false` and options A/B/C/D.
- **Multi-choice (不定项)**: Present 1 question per call with `multiSelect: true` and
  options A/B/C/D (user selects multiple).

This creates a natural exam-like flow with submit buttons for each answer.

If AskUserQuestion or the VS Code interactive quiz surface is unavailable, switch to chat-answer mode:

```text
请按这个格式一次性提交答案：
1A 2BD 3C 4A 5ACD
```

The skill must parse the answer string, score each question, return the same score table and explanations, and then write local records or return append blocks. Chat-answer mode is a first-class fallback, not a failure.

## 2. Presentation Format

### For single-choice questions (batch of 4):

```
AskUserQuestion:
  questions:
    - question: "Q1. [Topic]\n\n[Question text]"
      header: "Q1 单选"
      multiSelect: false
      options:
        - label: "A"
          description: "[Option A text]"
        - label: "B"
          description: "[Option B text]"
        - label: "C"
          description: "[Option C text]"
        - label: "D"
          description: "[Option D text]"
```

Present Q1-Q4 as a single batch (4 questions in one AskUserQuestion call),
then Q5-Q8 as a second batch, and so on until all single-choice questions are covered.

### For multi-choice questions (one at a time):

```
AskUserQuestion:
  questions:
    - question: "Q9. [Topic]\n\n[Question text]\n\n（多选，漏选得部分分，多选/错选0分，分值见 exam_config.md）"
      header: "Q9 多选"
      multiSelect: true
      options:
        - label: "A"
          description: "[Option A text]"
        - label: "B"
          description: "[Option B text]"
        - label: "C"
          description: "[Option C text]"
        - label: "D"
          description: "[Option D text]"
```

Present Q{单选题数+1}-Q{总题数} one by one (each is a separate AskUserQuestion call).

## 3. Scoring Rules

> **从 `targets/{target}/exam_config.md` 读取分值**。以下为默认规则，运行时以 exam_config 为准。

After each batch/question, immediately show results:

### Single-choice scoring (分值见 exam_config.md)
- Correct: 满分
- Wrong: 0 points

### Multi-choice scoring (分值见 exam_config.md)
- All correct (exact match): 满分
- Partial (subset of correct, no wrong): 部分分（见 exam_config.md）
- Any wrong option selected: 0 points

### Scoring display format

After each batch:

```
### Batch Results

| 题号 | 你的答案 | 正确答案 | 得分 | 状态 |
|------|----------|----------|------|------|
| Q1 | B | C | 0/{分值} | ✗ |
| Q2 | A | A | {分值}/{分值} | ✓ |

**本批次得分**：3/6
**累计得分**：3/{总分}
```

## 4. Answer Explanation

After scoring each batch, provide **brief** explanations (1-2 lines per question):

```
### 解析

**Q1**：正确答案 C。[One-line explanation]。
> 防错：[pitfall note if exists in mistake_log]

**Q2**：正确答案 A。✓ 正确！
```

- Only explain wrong answers in detail.
- For correct answers, just confirm with ✓.
- Always include 防错 note if the topic has an entry in `mistake_log.md` or `mcp__exam-memory__list_experiences` returns a matching experience.

### 4b. Per-Question Error Persistence (本地优先，不等到最后)

> **为什么在这里**：错误上下文最鲜活的时刻就是刚答完的时刻。等到最后批量处理时，模型已经疲劳，容易遗忘细节。每道错题答完就立即持久化，即使中途退出也不会丢失。
>
> **去重规则**：写入 mistake_log.md 前，先检查该题号（如 Q3）是否已在当前主题分表中出现。已存在 → 跳过重复行；若 MCP 可用则执行 `mcp__exam-memory__inc_error_count`，若 MCP 不可用则在最终报告的 `[UNSYNCED_EXPERIENCES]` 中记录未同步信号。不存在 → 正常写入本地表格行；MCP 可用时再保存经验。

After scoring each wrong/skipped answer, immediately persist locally when the repo is writable:

1. Determine question type: see `targets/{target}/exam_config.md` for which Q-numbers are 单选 vs 多选
2. **Dedup check for mistake_log.md**: Scan the relevant topic table in `targets/{target}/mistake_log.md` for a row with the same question identifier (e.g., "Q3 topic"). If found, skip duplicate local append and record `LastSeen` / count when the table supports it.
3. **Local write**: append a row to `targets/{target}/mistake_log.md` for new wrong/skipped/lucky-pass answers, and later append session summary to `shared/daily/YYYY-MM-DD.md`.
4. **MCP 可选**: If `mcp__exam-memory__*` tools are available, call `mcp__exam-memory__list_experiences(type=题型, limit=5)` to check for matches.
5. **Match found** (same topic + similar error pattern): call `mcp__exam-memory__inc_error_count(file_path=匹配文件名)`.
6. **No match**: call `mcp__exam-memory__save_experience` with:
   - `title`: 简短描述（如"贝叶斯公式分子分母混淆"）
   - `content`: 包含错误理解、正确答案、知识点解析
   - `type`: "单选题" or "多选题"
   - `knowledge`: 题目知识点标签
   - `difficulty`: 根据错误率判断（全班错>50%=困难, 30-50%=中等, <30%=简单）

**MCP 不可用时**：继续完成本地写入或 Lite append blocks。最终报告写明"exam-memory MCP 未配置，跨会话检索、错误频率自动合并和画像更新已跳过"，并包含 `[UNSYNCED_EXPERIENCES]`（如有本轮未同步错题）。

This runs in parallel with the explanation — both happen after each question, not deferred to the end.

### 4c. Per-Question Mastery Self-Report (仅正确回答)

> **为什么在这里**：知道"答对了"不等于"掌握了"。猜对的题目如果不记录，系统会误判用户已掌握该知识点，导致后续不再针对性出题。通过自信度自评，系统能识别 blind_spot 并即时持久化。

After scoring each **correct** answer, immediately ask the user a confidence follow-up:

```
AskUserQuestion:
  questions:
    - question: "你对这道题的答案有多确定？\n\n（这帮助系统识别你的盲区——即使猜对，系统也需要知道你是否真正掌握）"
      header: "Q1 自信度"
      multiSelect: false
      options:
        - label: "确定会"
          description: "理解原理，能解释为什么选这个"
        - label: "猜的但有道理"
          description: "排除了部分选项，但不是完全确定"
        - label: "完全不懂，猜的"
          description: "碰巧选对了，实际上不会"
```

**Mastery mapping**:

| User choice | Mastery level |
|-------------|---------------|
| 确定会 | `confirmed` |
| 猜的但有道理 | `struggling` |
| 完全不懂，猜的 | `blind_spot` |

**When mastery is `blind_spot` or `struggling`**, immediately persist to local Markdown when possible, and optionally to exam-memory MCP (same workflow as §4b, but with Result = `lucky_pass` instead of `WA`):

1. Append row to the topic table in `targets/{target}/mistake_log.md`:
   ```
   | MM-DD | QN topic | topic | lucky_pass | struggling/blind_spot | [root cause] | [fix rule] | MM-DD+1 |
   ```
2. MCP 可用时 call `mcp__exam-memory__save_experience` with the same parameters as §4b (title, content, type, knowledge, difficulty), noting in the content that this was a lucky pass.
3. MCP 不可用时把该题列入 `[UNSYNCED_EXPERIENCES]` 或 `[MISTAKE_LOG_APPEND]`。
4. Update the topic's mastery level in tracking.

**When mastery is `confirmed`**: No persistence needed (unless it's the 2nd consecutive confirmed, in which case mark topic as fully mastered — no redo date).

## 5. Post-Session Update

After all questions are answered, produce a final summary and update files:

### 5a. Final Score Report

```
## 最终成绩

| 指标 | 数值 |
|------|------|
| 单选正确率 | X/{单选题数} |
| 多选全对 | X/{多选题数} |
| 多选部分分 | X 题 |
| 总分 | XX/{总分} (XX%) |
```

### 5b. Update mistake_log.md

For each wrong answer, check dedup before appending to the relevant topic table in
`targets/{target}/mistake_log.md`. This local persistence is required when the repo is writable:

```markdown
| Date | Problem | Topic | Result | Mastery | Root Cause | Fix Rule | Redo Date |
|------|---------|-------|--------|---------|------------|----------|-----------|
| MM-DD | QN topic | topic | WA | WA | proof/pattern | [one-line fix rule] | MM-DD+1 |
```

**Dedup**: If a row for the same problem (same QN + topic) already exists in the table, skip the duplicate row. If the table supports `LastSeen` / count, update that local signal; otherwise mention the repeated error in the final report.

**Mastery value rules**:

| Result | Confidence | Mastery | Redo Date |
|--------|-----------|---------|-----------|
| WA | — | WA | MM-DD+1 |
| Correct | 确定会 | confirmed | No redo date (or 2 days after) |
| Correct | 猜的但有道理 | struggling | MM-DD+1 |
| Correct | 完全不懂，猜的 | lucky_pass | Same day (immediate review) |

Also update:
- Root Cause 汇总 table (increment counts)
- 考前速看 section if a new high-frequency pattern emerges

If the repo cannot be written, return this block instead of claiming persistence:

```text
[MISTAKE_LOG_APPEND]
Date | Problem | Topic | Result | Mastery | Root Cause | Fix Rule | Redo Date
MM-DD | QN topic | topic | WA/lucky_pass | WA/struggling/blind_spot | proof/pattern/careless | one-line fix | MM-DD+1
```

### 5b-2. 经验库兜底更新（exam-memory MCP，可选）

> 主要持久化已移至 §4b（每题答完立即执行）。此处为兜底检查：
> 若中途有错题因故未持久化，在此统一补录。
> **去重**：MCP 可用时先调用 `mcp__exam-memory__list_experiences` 匹配 → 匹配到则调用 `mcp__exam-memory__inc_error_count`，不新建。

MCP 不可用时，不阻塞本地闭环。在最终报告中加入：

```text
[UNSYNCED_EXPERIENCES]
题号 | 知识点 | 本地记录状态 | 未同步原因
Q3 | Bayes | 已写入/待写入 MISTAKE_LOG_APPEND | exam-memory MCP unavailable
```

### 5c. Update daily plan file

Append results to `shared/daily/YYYY-MM-DD.md` Problem Log section:

```markdown
### 选择题 Round N（交互模式）

- **单选正确率**：X/{单选题数}（XX%）— X/{单选总分} 分
- **多选正确率**：X/{多选题数} 全对
- **总分**：XX/{总分}（XX%）
- **主要错因**：
  - [topic]（QN）— [brief cause]
- **薄弱知识点**：[list]
- **进步点**：[previously wrong, now correct]
- **与上次对比**：[previous score] → [current score]
```

If the daily file cannot be written, return:

```text
[DAILY_PROBLEM_LOG_APPEND]
### 选择题 Round N（chat/interactive mode）
- 单选正确率：
- 多选正确率：
- 总分：
- 主要错因：
- 薄弱知识点：
```

Always include the round-level scoring table in the final report or append block:

```text
[CHOICE_ROUND_SUMMARY]
题号 | 你的答案 | 正确答案 | 得分 | 知识点 | 是否写入错题
```

### 5d. Error classification

Tag each error with a Root Cause:

| Tag | When to use |
|-----|-------------|
| `pattern` | Didn't know how to approach (formula, flow, formula) |
| `proof` | Concept confused or property misremembered |
| `python` | Numerical/常识 error |
| `careless` | Knew the concept but made a reading/calculation mistake |

## 6. Adaptive Phase Controller

After the final report (§5), recommend the next study phase based on session results:

**Phase recommendation logic**:

| Condition | Recommendation |
|-----------|----------------|
| total score < 40% OR blind_spot count >= 3 | Phase 1: 主攻盲区 |
| score 40-60% AND has unknown topics | Phase 2: 补盲+拓展 |
| score > 60% AND blind_spot < 2 | Phase 3: 全真模拟 |
| 2 consecutive Phase 3 AND score > 75% | Phase 4: 考前冲刺 |

Count blind_spots from the mastery self-report (§4c) and error records in this session.
Count unknown topics as those with no record in exam-memory or mistake_log.

Present AskUserQuestion with the recommended option pre-selected:

```
下一轮方向：
- A. 主攻易错点/盲区（推荐：当前有 X 个 blind_spot）
- B. 增加新考点（推荐：有 Y 个未接触域）
- C. 全真模拟（均匀覆盖 12 域）
- D. 考前冲刺模式（仅高频易错）
```

If the user selects the recommended option, generate the next round accordingly:
- Phase 1: Focus question generation on topics with `blind_spot` or `struggling` mastery
- Phase 2: Mix remediating topics with new topics the user hasn't encountered
- Phase 3: Uniform coverage across all 12 domains
- Phase 4: High-frequency error patterns only, mixed with confirmed topics for confidence

If the user selects a non-recommended option, respect their choice but note the deviation.

## 7. Question File Discovery

To find available question sets:

```
Glob: targets/{target}/progress/choice-questions/round*.md
```

If multiple files exist, ask the user which round to drill. If only one exists,
start with it automatically.

If no question file exists, suggest invoking `choice-q-create` first.

## 8. Time Tracking

Note the start time when drilling begins. After completion, report:
- Total time taken
- Average time per question
- Comparison with target (见 exam_config.md)

## 9. Workflow

### 阶段一：题目文件解析（Agent 可选）

> **为什么用 Agent**：round 文件包含完整题目 + 答案 + 解析，体积可能较大。通过 Agent 读取并解析为结构化格式，主上下文只接收每道题的题号、知识点标签、正确选项，而非整份文件内容。

```python
# 如果 round 文件较大（>200 行），使用 Agent 解析：
# Agent 读取 roundN.md → 返回 [{q_num, topic, question_text, options, correct_answer, explanation_key_points}]
# 主会话基于结构化数据逐题呈现
```

**Agent 解析任务**（当 round 文件较大时使用）：

```
你是选择题文件解析助手。请读取给定的 round 文件并返回结构化摘要。

对每道题提取：
{
  "q_num": "Q1",
  "topic": "知识点标签",
  "type": "single" | "multi",
  "question": "题干（精简版，保留核心）",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct": "A" 或 "ACD" 等,
  "explanation_key_points": ["关键点1", "关键点2"]
}

只返回 JSON 数组，不要返回原始文件内容。
```

**降级规则**：文件较小时（<200 行或 <15 题），主会话直接读取文件内容，无需 Agent。

### 阶段二：交互流程
3. **Note start time** — for performance tracking
4. **Choose answer mode** — AskUserQuestion if available; otherwise ask for chat-answer string such as `1A 2BD 3C`
5. **Single-choice batch 1** — AskUserQuestion with Q1-Q4 (multiSelect: false), or parse the corresponding chat answers
6. **Score & explain** — immediate feedback after batch; for each wrong answer, immediately persist locally (§4b); for each **correct** answer, ask confidence self-report when possible (§4c)
7. **Single-choice batch 2** — AskUserQuestion with Q5-Q8 (repeat batches until all single-choice covered)
8. **Score & explain** — same local persistence + optional confidence self-report logic
9. **Multi-choice** — AskUserQuestion one at a time (multiSelect: true), starting from Q{单选题数+1}, or parse multi-letter answers like `2BD`
10. **Score & explain + optional MCP persist + confidence self-report** — for each answer, persist errors locally (§4b); MCP 可选双写 when available
11. **Final report** — aggregate scores, time, weak points
12. **Update files** — 本地必写 mistake_log.md (with Mastery column per §5b) and daily plan when repo is writable; MCP 可选 (§5b-2); if not writable, return append blocks
13. **MCP availability check** — If exam-memory MCP tools are unavailable, explicitly state in final report: "exam-memory MCP 未配置，跨会话持久化已跳过"，and list `[UNSYNCED_EXPERIENCES]` when applicable.
14. **Adaptive phase recommendation** — run §6 to recommend next study phase

## 9. Edge Cases

- **User skips a question**: Mark as skipped (0 points), note in report.
- **User wants to change answer**: Not supported in current AskUserQuestion flow.
  Instruct user to commit to their answer. This simulates real exam conditions.
- **Partial file**: If question file lacks answers section, warn user and stop.
- **Timeout**: If user takes >5 min on a batch, note it but don't auto-submit.
- **No interactive quiz tool**: Use chat-answer mode (`1A 2BD 3C ...`) and return the same score/explanation/update blocks.
- **No write access**: Do not claim updates were saved. Return `[CHOICE_ROUND_SUMMARY]`, `[MISTAKE_LOG_APPEND]`, `[DAILY_PROBLEM_LOG_APPEND]`, and `[HANDOFF_UPDATE]`.

## 10. Cross-References

- `choice-q-create` — generates the question sets this skill drills
- `targets/{target}/mistake_log.md` — error log to read (for 防错 notes) and update (after drilling)
- `targets/{target}/progress/choice-questions/round*.md` — question file source
- `shared/daily/YYYY-MM-DD.md` — daily plan to update with results
- `exam-memory` MCP tools — optional cross-session error persistence (mcp__exam-memory__save_experience, mcp__exam-memory__inc_error_count)
- `skills/exam-assistant.md` — MCP-aware exam assistant with local Markdown / Lite fallback
