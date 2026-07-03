# TASK_TEMPLATES.md

> GTMS Task Execution Templates
>
> Version: 2.0
>
> Last Updated: YYYY-MM-DD

---

## Purpose

本文件定义 GTMS 项目所有 AI 开发任务的标准执行模板。

所有开发任务均应引用本文件。

本文件仅规定：

- 任务结构
- 输出格式
- Review 内容
- Documentation Sync 内容

不规定：

- 编码规范
- 数据库设计
- 开发流程

上述内容由 AI_RULES.md 管理。

## 目录

1. [模板使用说明](#1-模板使用说明)
2. [模板 A：开发任务（Development Task）](#2-模板-a开发任务development-task)
3. [模板 B：审查与优化（Review & Polish）](#3-模板-b审查与优化review--polish)
4. [模板 C：文档同步（Documentation Sync）](#4-模板-c文档同步documentation-sync)
5. [模板 D：设计一致性审计（Design Consistency Audit）](#5-模板-d设计一致性审计design-consistency-audit)
6. [模板 E：架构重构（Architecture Refactor）](#6-模板-e架构重构architecture-refactor)
7. [通用输出格式](#7-通用输出格式)
8. [任务生命周期](#8-任务生命周期)

---

## 1. 模板使用说明

### 1.1 模板选择规则

| 任务类型 | 使用模板 | 触发条件 |
|----------|:--:|------|
| 新建 ORM 模型 | 模板 A | 创建新模型文件 |
| 新建 API / Service / Repository | 模板 A | 创建新功能模块 |
| 新建 UI 界面 | 模板 A | 创建新界面 |
| 代码审查 | 模板 B | Task 开发完成后 |
| 代码规范优化 | 模板 B | 审查发现规范问题 |
| 文档同步 | 模板 C | 代码变更后或发现文档不一致 |
| 设计一致性审计 | 模板 D | 用户明确要求审计 |
| 架构重构 | 模板 E | 用户明确要求重构 |

### 1.2 优先级

```
TASK_TEMPLATES.md  >  PROMPT_RULES.md  >  AI_RULES.md
```

如 TASK_TEMPLATES.md 有特殊模板，则优先采用对应模板。

### 1.3 模板结构

所有模板由以下部分组成：

| 部分 | 是否必须 | 说明 |
|------|:--:|------|
| 角色定义 | ✅ | 明确本次任务的 AI 角色 |
| 范围声明 | ✅ | 明确本次任务做什么、不做什么 |
| 参考文档 | ✅ | 列出必须遵守的文档 |
| 任务要求 | ✅ | 具体执行内容 |
| 禁止事项 | ✅ | 明确禁止的操作 |
| 输出格式 | ✅ | 规定输出结构 |

---

## 2. 模板 A：开发任务（Development Task）

### 2.1 适用场景

- 新建 ORM 模型
- 新建 API 接口
- 新建 Service 层
- 新建 Repository 层
- 新建 UI 界面
- 新建枚举类

### 2.2 模板内容

```
开始执行 Sprint {N} — Task {N}.{M}：{任务名称}。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
你的角色
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

你是 GTMS 项目的首席软件架构师（Chief Software Architect）。

本次任务是开发新功能。

必须严格遵守：

AI_RULES.md

PROMPT_RULES.md

DB_DESIGN.md

SRS.md

CODE_WIKI.md

DEVELOPMENT_ROADMAP.md

README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
任务目标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{简洁描述任务目标}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
范围
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

允许：

- {允许的操作 1}
- {允许的操作 2}

禁止：

- {禁止的操作 1}
- {禁止的操作 2}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
详细要求
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{具体要求，逐条列出}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
参考
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 参考项 | 文档 | 章节 |
|--------|------|------|
| {参考项 1} | {文档名} | {章节} |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
验收标准
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- {验收标准 1}
- {验收标准 2}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
禁止事项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

禁止：

- 修改数据库设计
- 修改 API
- 修改 UI
- 修改其它 Sprint
- 修改其它模块
- 新增不必要功能
- 擅自优化
- 擅自重构

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输出格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输出：

① 新增文件（New Files）

② 修改文件（Modified Files）

③ 字段清单（Field Summary）

④ Schema Preview（Database）

⑤ Schema Statistics

⑥ Relationship Summary

⑦ Metadata Summary

⑧ Design Consistency Review

⑨ 自测结果（Self Test）

⑩ ORM Quality Score

⑪ Suggested Commit

⑫ 最终确认（Final Confirmation）

⑬ Exit Criteria

必须逐项确认：

□ ORM 实现完成

□ Schema Preview 完成

□ Schema Statistics 完成

□ Relationship Summary 完成

□ Metadata Summary 完成

□ ORM Quality Score =100

□ Design Review 全部通过

□ Self Test 全部通过

□ 无 Design Conflict

□ Suggested Commit 已生成

□ 可以进入下一 Task

完成后立即停止。

不得继续开发下一 Task。
```

### 2.3 开发完成后的必须动作

开发完成后，必须按顺序执行：

```
1. Code Review（模板 B）
2. Documentation Sync（模板 C）
3. Git Commit
4. 用户确认
```

---

## 3. 模板 B：审查与优化（Review & Polish）

### 3.1 适用场景

- Task 开发完成后的代码审查
- 代码规范优化
- ORM 质量审查

### 3.2 模板内容

```
开始执行 Sprint {N} — Task {N}.{M} Review & Polish（{审查对象} 审查与规范优化）。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
你的角色
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

你是 GTMS 项目的首席软件架构师（Chief Software Architect）。

本次任务不是开发新功能。

不是新增字段。

不是修改数据库设计。

不是修改业务流程。

而是对已经完成的 {审查对象} 进行企业级代码审查（Code Review）和规范优化（Polish）。

必须严格遵守：

AI_RULES.md

PROMPT_RULES.md

DB_DESIGN.md

SRS.md

CODE_WIKI.md

DEVELOPMENT_ROADMAP.md

README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
本次任务目标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

保持：

- 数据库结构
- ORM 字段
- ForeignKey
- Relationship
- Enum
- 业务逻辑

全部不变。

仅优化：

- 代码规范
- Review 输出
- Schema Preview
- 统计信息
- 文档一致性

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
优化项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{逐条列出优化项，每项包含具体要求}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
禁止事项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

禁止：

- 新增字段
- 删除字段
- 修改字段类型
- 修改 Enum
- 修改数据库设计
- 新增 API
- 新增 Repository
- 新增 Service
- 新增 UI
- 新增 Migration
- 修改业务逻辑

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输出格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输出：

① 修改文件
② 修改内容
③ Schema Preview（企业版）
④ Schema Statistics（企业版）
⑤ Relationship Statistics
⑥ ForeignKey Review
⑦ Index Review
⑧ ORM Quality Review
⑨ Design Consistency Review
⑩ 自测结果
⑪ 最终评分
⑪ Suggested Commit

fix(task x.x):

或

refactor(task x.x):


格式：

⭐⭐⭐⭐⭐

ORM Quality Score：

{score} / 100

是否建议进入下一 Task：

✅ 可以

或

❌ 不建议（说明原因）

完成后立即停止。

不得继续开发下一 Task。
```

### 3.3 Review 检查清单

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | 命名规范 | 类名 PascalCase、字段 snake_case、表名复数 |
| 2 | SQLAlchemy 2.x | Mapped[] + mapped_column() |
| 3 | 类型注解 | 全部字段有 Mapped[type] |
| 4 | mapped_column() | 全部字段使用 mapped_column() 定义 |
| 5 | Relationship | 使用 relationship() + lazy="selectin" |
| 6 | ForeignKey | 显式声明 ForeignKey("table.column") |
| 7 | Enum | 使用 SAEnum(EnumClass)，无硬编码字符串 |
| 8 | Comment | 全部 mapped_column() 带有 comment= |
| 9 | PEP8 | 4 空格缩进、导入分组、行长度 |
| 10 | 循环引用 | TYPE_CHECKING 保护 |
| 11 | Import | stdlib → 第三方 → 本地 |
| 12 | Docstring | 模块级 + 类级 + 内联注释 |
| 13 | 字段顺序 | 业务字段 → Relationship → BaseModel |

---

## 4. 模板 C：文档同步（Documentation Sync）

### 4.1 适用场景

- 代码变更后文档未同步
- 发现文档与代码不一致
- 每个 Task 开发完成后的必须步骤

### 4.2 模板内容

```
开始执行 Sprint {N} — Task {N}.{M}：Documentation Sync（架构文档同步）。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
你的角色
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

你是 GTMS（Grinding Trial Management System）项目的首席软件架构师（Chief Software Architect）。

本任务不是开发代码。

不是修改 ORM。

不是新增数据库。

不是新增 API。

不是新增业务逻辑。

本任务唯一目标：

统一所有设计文档，使其与当前 ORM 代码完全一致。

必须严格遵守：

AI_RULES.md

PROMPT_RULES.md

DB_DESIGN.md

SRS.md

CODE_WIKI.md

DEVELOPMENT_ROADMAP.md

README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
任务目标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

本次任务属于 Documentation Sync。

允许修改：

- DB_DESIGN.md
- SRS.md
- CODE_WIKI.md
- DEVELOPMENT_ROADMAP.md
- README.md
- AI_RULES.md（如本 Task 涉及规范同步）

禁止修改：

- Python 代码
- ORM 模型
- 数据库
- Alembic
- API
- UI

若发现仅为文档与代码不同步，而代码符合当前架构设计，则以代码为准同步文档。

不得因文档同步任务而要求修改 ORM 代码。

本次任务完成标准：

1. 所有核心文档与当前 ORM 完全一致。
2. BaseModel 六个公共字段全部同步。
3. {具体模块} 字段数量统一为 {N}。
4. RBAC 架构一致。
5. 双状态（process_status / result_status）一致。
6. 不再存在 P0/P1 文档冲突。
7. Documentation Sync 完成后立即停止，不进入下一 Task。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
任务一
{具体同步任务}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{任务详细描述}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
禁止事项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

禁止修改：

server/

client/

models/

database/

api/

repository/

service/

UI

Alembic

Migration

Seed

任何 Python 文件。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输出格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输出以下内容：

① 修改文档清单

② 每份文档修改章节

③ 修改内容摘要

④ BaseModel 公共字段统一结果

⑤ 字段统计（更新后）

⑥ ForeignKey 规范说明

⑦ 文档一致性检查矩阵

格式：

文档 | 检查项 | 是否一致

⑧ 遗留问题（如有）

⑨ 自测结果

全部通过后输出：

==============================

Documentation Sync

PASSED

Documentation Statistics

修改文档数量

修改章节数量

新增章节数量

删除章节数量

同步字段数量

同步索引数量

==============================

⑩ 最终确认

是否所有核心文档一致：

✅ 是

是否允许继续下一 Task：

✅ 可以

完成后立即停止。

不得继续开发任何代码。
```

### 4.3 文档同步检查清单

| # | 检查项 | 涉及文档 |
|---|--------|------|
| 1 | BaseModel 6 公共字段 | DB_DESIGN.md, CODE_WIKI.md |
| 2 | 表结构字段数 | DB_DESIGN.md §4 |
| 3 | DDL 字段数 | DB_DESIGN.md §3 |
| 4 | RBAC 模型 | DB_DESIGN.md, SRS.md, CODE_WIKI.md |
| 5 | 状态枚举 | DB_DESIGN.md, SRS.md, CODE_WIKI.md |
| 6 | 外键规范 | DB_DESIGN.md §6 |
| 7 | 视图设计 | DB_DESIGN.md §7, CODE_WIKI.md §7 |
| 8 | ER 图 | DB_DESIGN.md, CODE_WIKI.md |
| 9 | 索引数量 | DB_DESIGN.md §5, DEVELOPMENT_ROADMAP.md |
| 10 | 技术栈版本 | README.md, CODE_WIKI.md, DEVELOPMENT_ROADMAP.md |
| 11 | 旧状态引用 | 全部文档 |
| 12 | 旧目录名称 | 全部文档 |

---

## 5. 模板 D：设计一致性审计（Design Consistency Audit）

### 5.1 适用场景

- 用户明确要求全项目文档审计
- 跨 Sprint 的文档一致性检查
- 架构重构前的基线确认

### 5.2 模板内容

```
开始执行 GTMS 项目设计文档一致性审计（Design Consistency Review）。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
你的角色
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

你是 GTMS 项目的首席软件架构师。

本次审计范围：

{审计范围简述}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
审计范围
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

逐项核对以下 7 份核心文档：

- README.md
- DB_DESIGN.md
- SRS.md
- UI_PROTOTYPE.md
- CODE_WIKI.md
- DEVELOPMENT_ROADMAP.md
- AI_RULES.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
审计项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{逐条列出审计项}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输出格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输出：

① 审计发现清单

按严重程度分级：

P0（致命）：
P1（重要）：
P2（建议）：

② 每项发现的影响分析

③ 修复建议

④ 审计结论

是否允许继续开发：

✅ 可以

或

❌ 不建议（说明原因）

完成后立即停止。

不得直接修改文档。

等待用户确认。
```

### 5.3 审计发现分级标准

| 级别 | 定义 | 示例 |
|:--:|------|------|
| P0 | 代码与设计文档严重冲突，影响功能正确性 | 字段数量不一致、状态枚举不匹配 |
| P1 | 设计文档内部不一致，但代码正确 | 例代码与文档描述不符、统计数字错误 |
| P2 | 文档格式或描述不精确，不影响开发 | 注释不清晰、命名不统一 |

---

## 6. 模板 E：架构重构（Architecture Refactor）

### 6.1 适用场景

- 用户明确要求架构重构
- 修复多个设计文档冲突
- 跨文档统一修改

### 6.2 模板内容

```
开始执行 GTMS Architecture Refactor（架构文档统一修复）。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
你的角色
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

你是 GTMS 项目的首席软件架构师。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
核心原则
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{核心原则描述}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
修复项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{逐条列出修复项}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
禁止事项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

禁止：

- 修改 Python 代码
- 修改 ORM 模型
- 修改数据库
- 修改 API
- 修改 UI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输出格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输出：

① 修改文档清单
② 每项修复内容
③ 修复前后对比
④ 自测结果
⑤ 遗留问题

完成后立即停止。
```

---

## 7. 通用输出格式

### 7.1 自测结果格式

```
============================================================
{序号}. {测试项}
============================================================
  [OK] {测试内容}
  [OK] {测试内容}

============================================================
SUMMARY
============================================================
  {统计项 1}
  {统计项 2}

=== ALL TESTS PASSED ===
```

### 7.2 设计一致性检查矩阵格式

| 文档 | 检查项 | 是否一致 |
|------|------|:--:|
| DB_DESIGN.md | {检查项} | ✅ |
| SRS.md | {检查项} | ✅ |
| CODE_WIKI.md | {检查项} | ✅ |
| DEVELOPMENT_ROADMAP.md | {检查项} | ✅ |
| README.md | {检查项} | ✅ |

### 7.3 Schema Preview 格式（企业版）

| 字段 | Python 类型 | SQLAlchemy 类型 | 数据库类型 | Nullable | Default | PK | FK | Unique | Index | Enum | Comment |
|------|-------------|----------------|-----------|----------|---------|----|----|--------|-------|------|---------|

### 7.4 ORM Quality Score 格式

```
| # | 检查项 | 状态 |
|---|--------|------|
| 1 | 命名规范 | ✅ |
| 2 | SQLAlchemy 2.x | ✅ |
| ... | ... | ... |

ORM Quality Score：{score} / 100

⭐⭐⭐⭐⭐
```
### 7.5 Relationship Summary

| Relationship | Target Model | Cardinality | back_populates | lazy | cascade |
|--------------|--------------|------------|----------------|------|---------|
| customer | Customer | N:1 | tasks | selectin | — |
| receipt | Receipt | 1:1 | task | selectin | all, delete-orphan |

### 7.6 Schema Statistics

| Item | Count |
|------|------:|
| Business Fields | {count} |
| BaseModel Fields | {count} |
| Total Columns | {count} |
| Foreign Keys | {count} |
| Relationships | {count} |
| Indexes | {count} |
| Unique Constraints | {count} |
| Enum Fields | {count} |
| Metadata Tables | {count} |

### 7.7 Suggested Commit

统一输出格式：

text
Suggested Commit

feat(task{Sprint}.{Task}): {summary}

示例
feat(task1.6): implement Receipt ORM

fix(task1.5): synchronize TrialTask schema

docs(task1.5.1): synchronize architecture documents

---

## 8. 任务生命周期

### 8.1 标准流程

每个 Task 必须严格遵循以下生命周期：

```
Task Development（模板 A）
        ↓
Code Review（模板 B）
        ↓
Documentation Sync（模板 C）
        ↓
Git Commit
        ↓
用户确认
        ↓
Git Tag（Sprint 完成时）
        ↓
进入下一 Task
```

### 8.2 步骤说明

| 步骤 | 模板 | 必须 | 说明 |
|------|:--:|:--:|------|
| Development | 模板 A | ✅ | 开发新功能 |
| Code Review | 模板 B | ✅ | 审查代码质量 |
| Documentation Sync | 模板 C | ✅ | 同步文档与代码 |
| Git Commit | — | ✅ | 提交代码 |
| 用户确认 | — | ✅ | 等待用户批准 |

### 8.3 禁止行为

- 跳过 Documentation Sync
- 代码与设计文档不一致
- 跨 Sprint 开发
- 提前开发后续功能
- 一次完成多个 Task
- 未经确认进入下一 Task

---

> **文档版本：** V1.0  
> **签发人：** 首席架构师  
> **签发日期：** 2026-07-02  
> **适用范围：** GTMS 项目全部 Sprint