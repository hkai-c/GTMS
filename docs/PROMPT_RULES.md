# PROMPT_RULES.md

> GTMS Prompt Writing Specification
>
> Version: 2.0
>
> Last Updated: YYYY-MM-DD

---

# 1. Purpose

本文件用于规范 GTMS 项目中 AI Prompt 的编写方式。

Prompt 仅描述：

- 当前开发任务
- 当前开发目标
- 当前开发范围

Prompt 不负责：

- 定义开发规范
- 定义数据库设计
- 定义编码规范
- 定义 Review 流程

上述内容统一由：

- AI_RULES.md
- TASK_TEMPLATES.md

负责维护。

---

# 2. Document Reference

所有 Prompt 默认引用：

1. AI_RULES.md
2. PROMPT_RULES.md
3. TASK_TEMPLATES.md

如涉及业务设计，

自动参考：

- DB_DESIGN.md
- SRS.md
- CODE_WIKI.md
- DEVELOPMENT_ROADMAP.md

无需在 Prompt 中重复说明。

若存在新增设计文档，

Prompt 中仅补充新增文档即可。

---

# 3. Prompt Scope

一个 Prompt：

仅允许完成：

一个 Sprint

一个 Task

禁止：

- 同时开发多个 Task
- 顺便重构其它模块
- 顺便修复其它 Bug
- 顺便同步所有文档

若发现需要跨 Task 修改，

立即停止，

输出：

Design Conflict Report。

---

# 4. Prompt Structure

所有 Prompt 必须按照以下结构编写：

```
Sprint

Task

Template

Task Goal

Task Scope

Deliverables

Acceptance

Special Notes（可选）
```

不得增加其它固定章节。

---

# 5. Template Selection

Prompt 必须引用：

TASK_TEMPLATES.md

根据任务类型选择对应模板。

| Task Type | Template |
|------------|----------|
| ORM | Template-A |
| Repository | Template-A |
| Service | Template-A |
| API | Template-A |
| UI | Template-A |
| Migration | Template-A |
| Seed Data | Template-A |
| Review | Template-B |
| Documentation Sync | Template-C |
| Design Audit | Template-D |
| Architecture Refactor | Template-E |
| Bug Fix | Template-F |

Prompt 中无需重复模板内容。

---

# 6. Prompt Content

Prompt 仅允许描述：

当前任务：

- 做什么
- 修改哪些文件
- 不允许修改哪些文件
- 输出哪些结果
- 验收标准

不得重复：

- AI_RULES.md
- TASK_TEMPLATES.md

中的内容。

---

# 7. Prompt Length

建议：

50~150 行。

最长：

不超过 200 行。

若超过：

说明 Prompt 包含了不属于当前 Task 的内容。

应拆分多个 Task。

---

# 8. Prompt Lifecycle

一个 Prompt 生命周期：

```
Create Prompt
      │
      ▼
Development
      │
      ▼
Review
      │
      ▼
Documentation Sync
      │
      ▼
Git Commit
      │
      ▼
Task Complete
```

完成后结束。

不得继续进入下一 Task。

---

# 9. Output Principle

Prompt 不规定输出格式。

输出格式统一由：

TASK_TEMPLATES.md

定义。

包括：

- Schema Preview
- Design Review
- Code Review
- Architecture Review
- Documentation Sync
- Self Test
- ORM Quality Score

Prompt 不得再次复制。

---

# 10. Naming Convention

Prompt 标题统一：

```
Sprint X — Task X.X

Task Name
```

例如：

```
Sprint 1 — Task 1.6

Receipt ORM
```

---

# 11. Prompt Example

```
开始执行：

Sprint 1 — Task 1.6

Task：

Receipt ORM

Template：

Template-A

━━━━━━━━━━━━━━━━━━━━━━

Task Goal

创建 Receipt ORM。

━━━━━━━━━━━━━━━━━━━━━━

Task Scope

允许：

server/models/receipt.py

禁止：

修改其它 ORM

修改数据库设计

修改 Enum

修改 API

━━━━━━━━━━━━━━━━━━━━━━

Deliverables

Receipt ORM

Relationship

Review

Self Test

━━━━━━━━━━━━━━━━━━━━━━

Acceptance

符合：

DB_DESIGN.md

SRS.md

CODE_WIKI.md

完成后停止。

END
```

---

# 12. Responsibilities

AI_RULES.md

负责：

开发规范。

PROMPT_RULES.md

负责：

Prompt 编写规范。

TASK_TEMPLATES.md

负责：

任务输出模板。

三者职责不得交叉。

---

# 13. Document Priority

若多个规范存在冲突：

优先级如下：

```
AI_RULES.md
        │
        ▼
PROMPT_RULES.md
        │
        ▼
TASK_TEMPLATES.md
```

低优先级文档不得覆盖高优先级文档。

若发现冲突：

停止开发。

输出：

Design Conflict Report。

等待用户确认。

---

# Change Log

## Version 2.0

重构：

- Prompt 职责
- Template 引用机制
- 生命周期
- 文档优先级
- Prompt 示例
- Prompt 长度规范
