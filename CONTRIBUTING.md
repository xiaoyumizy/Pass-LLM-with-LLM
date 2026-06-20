# 开发规范 - 协作指南

> 适用于本项目开源后的 PR 协作，不过度约束，保留 ACM 备考工程的轻量风格。

## 1. 项目性质

本项目是**备考执行工程**，不是库或框架。所有产出围绕"刷题 → 复盘 → 提分"闭环。
贡献前请阅读 `AGENTS.md` 了解完整的 Component Map 和 Skill Pipeline。

## 2. 分支与 PR

| 规则 | 说明 |
|------|------|
| 主分支 | `main`，始终保持可运行 |
| 功能分支 | `feat/xxx`（新功能）、`fix/xxx`（修复）、`docs/xxx`（文档） |
| PR 粒度 | 一个 PR 做一件事：一道算法题 / 一个 Skill 更新 / 一篇 cheatsheet |
| PR 描述 | 必须说明：改了什么、为什么改、影响哪些 Skill 或数据流 |

## 3. Python 代码规范

算法代码遵循 ACM/OJ 风格，**不引入工程化框架**：

```python
# 标准开头
import sys
input = sys.stdin.readline

def solve():
    # 解题逻辑
    ...

if __name__ == "__main__":
    solve()
```

- Python 3.10+，标准库为主，不用第三方包（除非 `python_oj_template.py` 已有）。
- 变量名简洁但可读：`n, m, arr, dp, res` 合适，`a, b, c` 仅用于短循环。
- 每个 `solve()` 函数必须能独立运行（可粘贴到 OJ 平台）。
- 复杂度注释写在函数上方一行：`# O(n log n) time, O(n) space`。

## 4. Skill 文件规范

Skill 是 Markdown 文件，存放于 `skills/`，格式要求：

```markdown
---
name: skill-name          # kebab-case，与文件名一致
description: 一句话说明
tools: [tool1, tool2]     # 依赖的 MCP 工具（如有）
---

# Skill 内容
...
```

- frontmatter 必须包含 `name` 和 `description`。
- 工作流步骤用有序列表，触发词用无序列表。
- 引用其他文件用相对路径，并优先使用当前目录结构：`targets/{target}/mistake_log.md`、`shared/cheatsheets/`、`shared/exam_memory/`。

## 5. 目录归属规则

| 内容类型 | 存放位置 | 命名规则 |
|----------|----------|----------|
| 考试真题解答 | `targets/{target}/solutions/` 或 `targets/{target}/solutions_batch.py` | 统一编号或单题文件 |
| 非考试练习题 | `targets/{target}/practice/{topic}.py` | 按算法专题命名 |
| 错误记录 | `targets/{target}/mistake_log.md` | 按主题分区，表格式 |
| 计时模拟记录 | `targets/{target}/mock_exam_log.md` | 按日期追加 |
| 目标专属每日计划 | `targets/{target}/daily/YYYY-MM-DD.md` | 日期命名 |
| 共享每日计划 | `shared/daily/YYYY-MM-DD.md` | 日期命名 |
| 目标专属速记资料 | `targets/{target}/cheatsheets/{topic}.md` | 主题命名 |
| 通用速记资料 | `shared/cheatsheets/{topic}.md` | 主题命名 |
| Skill 定义 | `skills/{name}.md` 或 `skills/{name}/SKILL.md` | kebab-case |
| 目标进度追踪 | `targets/{target}/progress/` | 按 choice-questions、study-planning、task-board 等分区 |
| 共享进度追踪 | `shared/progress/` | 跨目标通用任务或索引 |

**不要**把非考试练习题放进考试真题解答目录，也不要把考试真题放进 `practice/`。旧的 `algorithms/`、`llm/`、顶层 `daily/` 路径只应作为历史兼容占位，不应作为新贡献入口。

错题、模拟记录和进度追踪默认是本地运行态数据。公开 PR 只应提交去个人化的示例、模板或说明，不应包含个人 `mistake_log.md`、`mock_exam_log.md` 或 `progress/` 记录。`shared/progress/**` 只允许公开 `README.md`、`.gitkeep`、`*.example.md` 和 `*.template.md`，真实 task board 与复盘文件必须留在本地或 dev 分支。

## 6. Commit Message

```
<type>: <简短描述>

类型：
  feat     新功能/新题/新 Skill
  fix      修复错误/修正解法
  docs     文档更新
  log      错误日志/复盘记录（mistake_log, mock_exam_log）
  refactor Skill 或模板重构
```

示例：
```
feat: add BFS skeleton for grid traversal
fix: correct sliding window off-by-one in solution #12
log: record WA on binary search boundary condition
docs: update GNN cheatsheet with message passing detail
```

## 7. PR Checklist

提交 PR 前确认：

- [ ] 算法题已走 solve-skeleton → algo-annotation 完整流程
- [ ] WA/TLE 错误已在本地记录（如适用），且本 PR 未包含个人日志
- [ ] 新 Skill 有完整的 frontmatter（name, description）
- [ ] 未引入不必要的第三方依赖
- [ ] 不涉及个人经验数据（例如本地 `shared/exam_memory/experiences/` 中的私有记录）

## 8. 外部项目引用与许可

如 PR 借鉴外部项目、论文、博客或工具设计，请在 README、文档或 PR 描述中注明来源链接和借鉴范围。不要复制外部项目的大段文档、代码或品牌表达，除非其许可证明确允许且 PR 中说明了许可证兼容性。

OneFind、ChatMem、MemPalace 等外部工具只能作为可选集成或设计启发提及，不应写成项目自带能力或官方关联。

## 9. 不做的事

以下**不在本项目范围内**，请勿贡献：

- 通用算法库封装（本项目是备考用，不是 LeetCode 题解库）
- CI/CD 流水线（过度工程化）
- 前端 UI / Web 界面
- 数据库迁移脚本
- 大规模重构目录结构（除非先开 Issue 讨论）
