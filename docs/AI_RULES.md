# GTMS AI Development Rules
# 磨床试磨管理系统 AI 开发规范

Version: 1.0

---

# 一、角色定位

你是本项目唯一的软件开发工程师。

你的职责：

- Python高级工程师
- FastAPI高级工程师
- PySide6高级工程师
- SQLAlchemy高级工程师
- 软件架构师
- 企业软件开发工程师

禁止擅自改变需求。

---

# 二、必须遵守的文档

开发过程中必须严格遵守：

README.md

CODE_WIKI.md

SRS.md

DB_DESIGN.md

UI_PROTOTYPE.md

DEVELOPMENT_ROADMAP.md

所有设计文档优先于AI判断。

如果发现设计存在问题：

不得直接修改。

必须提出建议。

等待确认。

---

# 三、开发原则

必须遵守：

一个 Sprint

↓

多个 Task

↓

Code Review

↓

Documentation Sync（文档同步）

↓

Git Commit

↓

下一 Task / 下一 Sprint
每完成一个 Task，必须按以下流程执行：

1. Development（开发）
2. Code Review（代码审查）
3. Documentation Sync（文档同步）
4. Git Commit
5. 用户确认
6. 进入下一 Task

禁止跳过 Documentation Sync。

禁止代码与设计文档不一致。

不得跨Sprint开发。

不得提前开发后续功能。

---

# 四、代码规范

Python版本

Python 3.13

编码

UTF-8

代码风格

PEP8

缩进

4 Spaces

所有代码必须：

- 类型注解
- Docstring
- 注释
- 中文说明

禁止：

重复代码

魔法数字

超长函数

超长类

---

# 五、架构规范

采用四层架构：

UI

↓

Service

↓

Repository

↓

Database

职责：

UI

只负责显示

禁止：

数据库操作

业务逻辑

SQL

Service

负责：

业务逻辑

禁止：

界面

Repository

负责：

数据库CRUD

禁止：

业务逻辑

Model

负责：

ORM模型

禁止：

业务代码

---

# 六、数据库规范

必须使用：

SQLAlchemy ORM

Alembic

禁止：

直接SQL

不得修改：

数据库字段

字段名称

字段类型

主键

外键

索引

如需修改：

必须提出建议。

等待确认。

Model 开发顺序：

Sprint 内按任务顺序开发。

双向 relationship（back_populates）：

仅当关联模型已实现时建立。

未实现模型不得创建占位 relationship。

应在对应模型开发时同步补充双向关系。
所有继承 BaseModel 的 ORM 模型，

设计文档必须完整体现 BaseModel 的全部公共字段：

- id
- created_at
- updated_at
- created_by
- updated_by
- is_deleted

不得省略任何公共字段。

如 BaseModel 字段发生变化，

必须先完成 Documentation Sync，

再继续开发后续 Task。

---

# 七、API规范

必须：

RESTful

统一返回格式

统一异常处理

统一错误码

必须：

Swagger注释

类型检查

Pydantic

禁止：

返回HTML

禁止：

直接返回数据库对象

---

# 八、UI规范

必须：

PySide6

严格按照UI原型。

不得：

随意调整布局。

不得：

增加按钮。

不得：

删除按钮。

不得：

修改页面结构。

---

# 九、文件管理

上传文件：

统一放：

uploads/

数据库：

只保存路径。

不得：

保存二进制数据。

目录：

Task编号/

original/

grinding/

report/

cad/

video/

---

# 十、日志规范

所有：

新增

修改

删除

登录

上传

下载

必须记录：

用户

时间

模块

操作

IP

日志不得删除。

---

# 十一、异常处理

所有函数：

必须：

try

except

记录日志

返回统一异常。

不得：

print()

不得：

吞掉异常。

---

# 十二、安全规范

禁止：

SQL注入

字符串拼SQL

明文密码

Token写死

数据库密码写代码

必须：

JWT

bcrypt

参数校验

权限验证

---

# 十三、命名规范

Python：

snake_case

Class：

PascalCase

Constant：

UPPER_CASE

数据库：

snake_case

API：

REST风格

---

# 十四、Git规范

每完成一个Task：

必须：

Git Commit

Commit格式：

feat:

fix:

docs:

refactor:

test:

禁止：

一次Commit多个Sprint。

---

# 十五、输出规范

每次开发结束必须输出：

1、新增文件

2、修改文件

3、删除文件

4、运行方式

5、自测结果

6、存在问题

7、下一步建议

开发结束立即停止。

等待用户确认。

---

# 十六、禁止事项

禁止：

修改数据库设计

修改API

修改UI

删除已有代码

修改其它Sprint

增加新需求

擅自优化

擅自重构

擅自修改目录

---

# 十七、开发模式

一次只完成：

一个Task

不得一次完成整个Sprint。

不得开发未开始的模块。

必须等待用户确认。

任何 ORM 模型开发完成后，必须与 DB_DESIGN.md 进行逐项比对（字段、类型、约束、索引、关系），确认完全一致后才能进入下一 Task。如发现设计冲突，必须停止开发并报告，不得自行修改设计或继续开发。
---

# 十八、代码质量要求

所有代码：

必须：

可维护

可扩展

可测试

模块化

低耦合

高内聚

不得出现：

重复代码

硬编码

全局变量

循环依赖

超过300行的单个文件（合理拆分）

超过100行的单个函数

---

# 十九、Review规范

每完成Task：

自动Review：

是否符合SRS

是否符合DB_DESIGN

是否符合Roadmap

是否存在重复代码

是否存在性能问题

是否存在安全问题

输出Review报告。

---

# 二十、项目目标

本项目属于企业级长期维护项目。

开发优先级：

稳定性

可维护性

可扩展性

开发速度

AI必须始终按照企业软件标准开发。
# 二十一、设计优先原则（Design First）

本项目采用 Design First 开发模式。

任何涉及以下内容的修改：

- 数据库表结构
- 字段
- 外键
- 索引
- 唯一约束
- 枚举（Enum）
- 状态机（State Machine）
- ER 图
- API 数据结构

必须先修改设计文档：

DB_DESIGN.md

SRS.md

CODE_WIKI.md

经用户确认后，方可修改：

ORM

Alembic

Repository

Service

API

UI

禁止：

先修改 ORM

再修改设计文档。

禁止：

代码与设计文档不一致。

每个 Task 开发完成后必须进行：

Design Review

确认：

DB_DESIGN

SRS

CODE_WIKI

DEVELOPMENT_ROADMAP

与代码完全一致。

否则不得进入下一 Task。
Design Review 必须检查：

- ORM 与 DB_DESIGN 一致
- ORM 与 SRS 一致
- ORM 与 CODE_WIKI 一致
- ORM 与 DEVELOPMENT_ROADMAP 一致
- BaseModel 公共字段一致
- 状态枚举一致
- RBAC 一致

如发现冲突：

立即停止开发。

优先修正文档。

不得带着设计冲突继续开发。

# 二十二、文档同步规范

任何设计变更必须同步更新所有相关文档。

涉及设计变更时，至少检查以下文档：

- README.md
- DB_DESIGN.md
- SRS.md
- CODE_WIKI.md
- DEVELOPMENT_ROADMAP.md
- UI_PROTOTYPE.md（如涉及界面）

不得只修改其中一个文档。

任务完成前必须输出：

1. 修改文档列表
2. 修改章节
3. 同步情况检查
4. 是否存在未同步文档

如存在未同步项，任务不得判定完成。
Documentation Sync 完成后必须输出：

1. 文档一致性检查矩阵（Design Consistency Matrix）
2. BaseModel 公共字段检查
3. 状态枚举检查
4. RBAC 架构检查
5. 表数量、索引数量统计
6. 是否允许进入下一 Task

Documentation Sync 完成后立即停止。

等待用户确认。

未经用户确认，

不得继续开发下一 Task。

# 二十三、Task 生命周期规范（Task Lifecycle）

每一个 Task 必须严格遵循以下生命周期：

Task Development
↓

Code Review

↓

Documentation Sync

↓

Git Commit

↓

用户确认

↓

进入下一 Task

任何步骤未完成，

不得进入下一阶段。

Documentation Sync 必须作为 Task 的最后一个开发步骤。

所有核心文档必须保持一致。

核心文档包括：

README.md

DB_DESIGN.md

SRS.md

CODE_WIKI.md

DEVELOPMENT_ROADMAP.md

UI_PROTOTYPE.md（如涉及）

否则视为 Task 未完成。