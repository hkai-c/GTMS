# 磨床试磨管理系统（GTMS）— 数据库设计说明书

> **Grinding Trial Management System — Database Design Specification**  
> 版本：V1.0 | 文档日期：2026-07-02 | 数据库：SQLite / MySQL 8.0

---

## 目录

1. [设计概述](#1-设计概述)
2. [ER 图（实体关系图）](#2-er-图实体关系图)
3. [完整 DDL 语句](#3-完整-ddl-语句)
4. [表结构详述](#4-表结构详述)
5. [索引设计](#5-索引设计)
6. [关系与外键](#6-关系与外键)
7. [视图设计](#7-视图设计)
8. [种子数据](#8-种子数据)
9. [Alembic 迁移策略](#9-alembic-迁移策略)

---

## 1. 设计概述

### 1.1 数据库选型

| 环境 | 数据库 | 驱动 |
|------|------|------|
| 开发环境 | SQLite 3 | 内置 |
| 生产环境 | MySQL 8.0 | PyMySQL |

### 1.2 设计原则

1. **每表必须有主键**（自增整数 ID）
2. **每表必须有 `created_at`** 时间戳
3. **可变数据表增加 `updated_at`** 时间戳
4. **外键关系通过 ORM relationship 维护**，DDL 中显式声明
5. **索引覆盖所有查询条件字段**
6. **状态字段使用枚举约束**
7. **软删除**：核心业务表使用 `is_deleted` 标记，不物理删除
8. **审计字段**：所有业务表统一继承 BaseModel 的 created_by 和 updated_by 审计字段
9. **索引规范（Index Rule）**：§5.1（索引汇总）为整个项目唯一权威索引定义。所有 ORM、DDL、Migration、Review、Roadmap 必须以 §5.1 为准。若 §4.x 单表章节与 §5.1 不一致，视为文档错误，不得按照 §4.x 自行创建额外索引，必须先修正文档再继续开发。

### 1.3 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写蛇形命名，复数 | `trial_tasks` |
| 字段名 | 小写蛇形命名 | `task_no`, `customer_id` |
| 主键 | `id` | `id` |
| 外键 | `{关联表单数}_id` | `customer_id` |
| 索引 | `ix_{表名}_{字段名}` | `ix_trial_tasks_process_status` |
| 唯一约束 | `uq_{表名}_{字段名}` | `uq_trial_tasks_task_no` |

---

## 2. ER 图（实体关系图）

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  ┌──────────────┐          ┌──────────────────┐                             │
│  │    users     │          │    customers     │                             │
│  │──────────────│          │──────────────────│                             │
│  │ id (PK)      │◄────┐    │ id (PK)          │                             │
│  │ username     │     │    │ company_name     │                             │
│  │ password_hash│     │    │ contact          │                             │
│  │ real_name    │     │    │ phone            │                             │
│  │ phone        │     │    │ address          │                             │
│  │ is_active    │     │    │ created_by (FK)──┼──► users.id                 │
│  │ is_deleted   │     │    │ updated_by       │                             │
│  │ created_by   │     │    │ is_deleted       │                             │
│  │ updated_by   │     │    │ created_at       │                             │
│  │ created_at   │     │    │ updated_at       │                             │
│  │ updated_at   │     │    └────────┬─────────┘                             │
│  └──────┬───────┘     │           │ 1:N                                     │
│         │             │           ▼                                         │
│         │             │  ┌──────────────────┐                               │
│         │             │  │   trial_tasks    │  (核心表)                      │
│         │             │  │──────────────────│                               │
│         │  ┌──────────┼──│ id (PK)          │                               │
│         │  │          │  │ task_no (UQ)     │                               │
│         │  │  ┌───────┼──│ customer_id (FK) │                               │
│         │  │  │       │  │ requirement      │                               │
│         │  │  │       │  │ tracking_no      │                               │
│         │  │  │  ┌────┼──│ sales_id (FK)    │                               │
│         │  │  │  │    │  │ process_status   │                               │
│         │  │  │  │    │  │ result_status    │                               │
│         │  │  │  │    │  │ destination      │                               │
│         │  │  │  │    │  │ destination_date │                               │
│         │  │  │  │    │  │ failure_reason   │                               │
│         │  │  │  │    │  │ created_by       │                               │
│         │  │  │  │    │  │ updated_by       │                               │
│         │  │  │  │    │  │ is_deleted       │                               │
│         │  │  │  │    │  │ created_at       │                               │
│         │  │  │  │    │  │ updated_at       │                               │
│         │  │  │  │    │  └──┬───┬───┬───┬──┘                               │
│         │  │  │  │    │     │   │   │   │ 1:1                               │
│         │  │  │  │    │     │   │   │   │                                   │
│         │  │  │  │    │  ┌──┘   │   │   └──────────────┐                    │
│         │  │  │  │    │  │  ┌───┘   └──────────┐       │                    │
│         │  │  │  │    │  │  │  ┌──────────────┐│  ┌────┴──────────┐          │
│         │  │  │  │    │  │  │  │              ││  │               │          │
│         ▼  │  │  │    │  ▼  ▼  ▼              ▼│  ▼               │          │
│  ┌──────────┴──┐ │  ┌─┴──────────┐ ┌──────────┴──┐ ┌──────────┐  │          │
│  │  receipts   │ │  │  grinding  │ │ inspections │ │dispatches│  │          │
│  │─────────────│ │  │  _records  │ │─────────────│ │──────────│  │          │
│  │ id (PK)     │ │  │────────────│ │ id (PK)     │ │ id (PK)  │  │          │
│  │ task_id(FK)─┼─┘  │ task_id(FK)│ │ task_id(FK) │ │task_id(FK│  │          │
│  │ received_at │    │ operator_id│ │ report_path │ │direction │  │          │
│  │ receiver_id─┼──► │   (FK)     │ │ accuracy    │ │date      │  │          │
│  │ image_paths │    │ machine_   │ │ roughness   │ │operator_ │  │          │
│  │ (JSON)      │    │   type     │ │ result      │ │  id(FK)──┼──► users   │
│  └─────────────┘    │ wheel_type│ │ inspector_  │ │created_at│  │          │
│                     │ params     │ │   id(FK)───┼─►users     │  │          │
│                     │ start_time │ │ created_at  │ └──────────┘  │          │
│                     │ end_time   │ └─────────────┘               │          │
│                     │ image_paths│                                │          │
│                     │ fail_reason│                                │          │
│                     │ created_at │                                │          │
│                     └────────────┘                                │          │
│                                                                   │          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │          │
│  │ attachments  │    │ system_logs  │    │notifications │        │          │
│  │──────────────│    │──────────────│    │──────────────│        │          │
│  │ id (PK)      │    │ id (PK)      │    │ id (PK)      │        │          │
│  │ task_id (FK)─┼──► │ user_id (FK)─┼──► │ task_id (FK)─┼────────┘          │
│  │ file_type    │    │ action       │    │ type (ENUM)  │                   │
│  │ file_name    │    │ target_type  │    │ message      │                   │
│  │ file_path    │    │ target_id    │    │ is_read      │                   │
│  │ file_size    │    │ changes(JSON)│    │ target_user_ │                   │
│  │ uploaded_by──┼──► │ ip_address   │    │   id (FK)────┼──► users.id       │
│  │ created_at   │    │ created_at   │    │ created_at   │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│                                                                              │
│  ┌─────────────────────────── RBAC 权限体系 ────────────────────────────┐    │
│  │                                                                     │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │    │
│  │  │    roles     │    │  user_roles  │    │ permissions  │           │    │
│  │  │──────────────│    │──────────────│    │──────────────│           │    │
│  │  │ id (PK)      │◄───│ role_id (FK) │    │ id (PK)      │◄──┐       │    │
│  │  │ name (UQ)    │    │ user_id (FK)─┼──► │ code (UQ)    │   │       │    │
│  │  │ display_name │    └──────────────┘    │ name         │   │       │    │
│  │  │ description  │                        │ description  │   │       │    │
│  │  │ is_system    │    ┌──────────────┐    │ module       │   │       │    │
│  │  │ created_by   │    │role_permiss. │    │ created_by   │   │       │    │
│  │  │ updated_by   │    │──────────────│    │ updated_by   │   │       │    │
│  │  │ is_deleted   │    │ role_id (FK)─┼──► │ is_deleted   │   │       │    │
│  │  │ created_at   │    │ permission_id│───────────────────────┘       │    │
│  │  │ updated_at   │    └──────────────┘                               │    │
│  │  └──────────────┘                                                   │    │
│  │                                                                     │    │
│  │    User ↔ user_roles ↔ Role ↔ role_permissions ↔ Permission        │    │
│  │              (纯多对多 RBAC，无单角色字段)                            │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

关系说明：
  ───  1:1 (一对一)
  ───► 1:N (一对多)
  ──┼  外键引用
```

---

## 3. 完整 DDL 语句

### 3.1 MySQL 8.0 版本

```sql
-- ============================================================
-- GTMS V1.0 数据库初始化脚本 (MySQL 8.0)
-- ============================================================

CREATE DATABASE IF NOT EXISTS gtms
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE gtms;

-- -----------------------------------------------------------
-- 1. 用户表
-- -----------------------------------------------------------
CREATE TABLE users (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    real_name       VARCHAR(50)     NOT NULL,
    phone           VARCHAR(20)     DEFAULT NULL,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_username UNIQUE (username)
) ENGINE=InnoDB COMMENT='用户表';

-- -----------------------------------------------------------
-- 2. 客户表
-- -----------------------------------------------------------
CREATE TABLE customers (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    company_name    VARCHAR(200)    NOT NULL,
    contact         VARCHAR(50)     DEFAULT NULL,
    phone           VARCHAR(20)     DEFAULT NULL,
    address         TEXT            DEFAULT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_customers_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='客户表';

-- -----------------------------------------------------------
-- 2.1 角色表
-- -----------------------------------------------------------
CREATE TABLE roles (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    name            VARCHAR(50)     NOT NULL,
    display_name    VARCHAR(50)     NOT NULL,
    description     TEXT            DEFAULT NULL,
    is_system       TINYINT(1)      NOT NULL DEFAULT 0,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_roles_name UNIQUE (name)
) ENGINE=InnoDB COMMENT='角色表';

-- -----------------------------------------------------------
-- 2.2 权限表
-- -----------------------------------------------------------
CREATE TABLE permissions (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    code            VARCHAR(100)    NOT NULL,
    name            VARCHAR(100)    NOT NULL,
    description     TEXT            DEFAULT NULL,
    module          VARCHAR(50)     NOT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_permissions_code UNIQUE (code)
) ENGINE=InnoDB COMMENT='权限表';

-- -----------------------------------------------------------
-- 2.3 用户-角色关联表
-- -----------------------------------------------------------
CREATE TABLE user_roles (
    user_id         INT             NOT NULL,
    role_id         INT             NOT NULL,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='用户-角色关联表';

-- -----------------------------------------------------------
-- 2.4 角色-权限关联表
-- -----------------------------------------------------------
CREATE TABLE role_permissions (
    role_id         INT             NOT NULL,
    permission_id   INT             NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    CONSTRAINT fk_role_permissions_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_perm FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='角色-权限关联表';

-- -----------------------------------------------------------
-- 3. 试磨任务表（核心表）
-- -----------------------------------------------------------
CREATE TABLE trial_tasks (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    task_no         VARCHAR(20)     NOT NULL,
    customer_id     INT             NOT NULL,
    requirement     TEXT            NOT NULL,
    tracking_no     VARCHAR(100)    DEFAULT NULL,
    sales_id        INT             NOT NULL,
    process_status  ENUM('created','received','grinding','dispatched','closed') NOT NULL
                    DEFAULT 'created',
    result_status   ENUM('pending','passed','failed') NOT NULL
                    DEFAULT 'pending',
    destination     ENUM('returned_customer','retained_company','scrapped','returned_sales','other')
                    DEFAULT NULL,
    destination_date DATE           DEFAULT NULL,
    failure_reason  TEXT            DEFAULT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_trial_tasks_task_no UNIQUE (task_no),
    CONSTRAINT fk_trial_tasks_customer  FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
    CONSTRAINT fk_trial_tasks_sales     FOREIGN KEY (sales_id)    REFERENCES users(id)     ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='试磨任务表';

-- -----------------------------------------------------------
-- 4. 收件记录表
-- -----------------------------------------------------------
CREATE TABLE receipts (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    task_id         INT             NOT NULL,
    received_at     DATETIME        NOT NULL,
    receiver_id     INT             NOT NULL,
    image_paths     JSON            DEFAULT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_receipts_task_id UNIQUE (task_id),
    CONSTRAINT fk_receipts_task     FOREIGN KEY (task_id)     REFERENCES trial_tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_receipts_receiver FOREIGN KEY (receiver_id) REFERENCES users(id)       ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='收件记录表';

-- -----------------------------------------------------------
-- 5. 试磨记录表
-- -----------------------------------------------------------
CREATE TABLE grinding_records (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    task_id         INT             NOT NULL,
    operator_id     INT             NOT NULL,
    machine_type    VARCHAR(100)    DEFAULT NULL,
    wheel_type      VARCHAR(100)    DEFAULT NULL,
    params          TEXT            DEFAULT NULL,
    start_time      DATETIME        DEFAULT NULL,
    end_time        DATETIME        DEFAULT NULL,
    image_paths     JSON            DEFAULT NULL,
    fail_reason     TEXT            DEFAULT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_grinding_task_id UNIQUE (task_id),
    CONSTRAINT fk_grinding_task     FOREIGN KEY (task_id)     REFERENCES trial_tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_grinding_operator FOREIGN KEY (operator_id) REFERENCES users(id)       ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='试磨记录表';

-- -----------------------------------------------------------
-- 6. 检测记录表
-- -----------------------------------------------------------
CREATE TABLE inspection_records (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    task_id         INT             NOT NULL,
    report_path     VARCHAR(500)    DEFAULT NULL,
    accuracy        VARCHAR(100)    DEFAULT NULL,
    roughness       VARCHAR(100)    DEFAULT NULL,
    result          ENUM('pass','fail') DEFAULT NULL,
    inspector_id    INT             DEFAULT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_inspection_task_id UNIQUE (task_id),
    CONSTRAINT fk_inspection_task      FOREIGN KEY (task_id)      REFERENCES trial_tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_inspection_inspector FOREIGN KEY (inspector_id) REFERENCES users(id)       ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='检测记录表';

-- -----------------------------------------------------------
-- 7. 工件去向表
-- -----------------------------------------------------------
CREATE TABLE dispatches (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    task_id         INT             NOT NULL,
    direction       VARCHAR(200)    NOT NULL,
    dispatch_date   DATETIME        NOT NULL,
    operator_id     INT             NOT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_dispatches_task_id UNIQUE (task_id),
    CONSTRAINT fk_dispatches_task     FOREIGN KEY (task_id)     REFERENCES trial_tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_dispatches_operator FOREIGN KEY (operator_id) REFERENCES users(id)       ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='工件去向表';

-- -----------------------------------------------------------
-- 8. 附件表
-- -----------------------------------------------------------
CREATE TABLE attachments (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    task_id         INT             NOT NULL,
    file_type       ENUM('image','document','cad','video') NOT NULL,
    file_name       VARCHAR(255)    NOT NULL,
    file_path       VARCHAR(500)    NOT NULL,
    file_size       INT             DEFAULT NULL,
    uploaded_by     INT             NOT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_attachments_task   FOREIGN KEY (task_id)     REFERENCES trial_tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_attachments_uploader FOREIGN KEY (uploaded_by) REFERENCES users(id)     ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='附件表';

-- -----------------------------------------------------------
-- 9. 系统日志表
-- -----------------------------------------------------------
CREATE TABLE system_logs (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    user_id         INT             NOT NULL,
    action          ENUM('create','update','delete','status_change') NOT NULL,
    target_type     VARCHAR(50)     NOT NULL,
    target_id       INT             DEFAULT NULL,
    changes         JSON            DEFAULT NULL,
    ip_address      VARCHAR(50)     DEFAULT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='系统日志表';

-- -----------------------------------------------------------
-- 10. 消息提醒表
-- -----------------------------------------------------------
CREATE TABLE notifications (
    id              INT             AUTO_INCREMENT  PRIMARY KEY,
    task_id         INT             NOT NULL,
    type            ENUM('receipt_delay','grinding_delay','report_missing') NOT NULL,
    message         TEXT            NOT NULL,
    is_read         TINYINT(1)      NOT NULL DEFAULT 0,
    target_user_id  INT             NOT NULL,
    created_by      INT             DEFAULT NULL,
    updated_by      INT             DEFAULT NULL,
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_notifications_task   FOREIGN KEY (task_id)        REFERENCES trial_tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_notifications_user   FOREIGN KEY (target_user_id) REFERENCES users(id)       ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='消息提醒表';
```

### 3.2 SQLite 版本（开发环境）

```sql
-- 与 MySQL 版本逻辑相同，差异点：
-- 1. AUTO_INCREMENT → AUTOINCREMENT
-- 2. ENUM → TEXT + CHECK 约束
-- 3. TINYINT(1) → INTEGER
-- 4. JSON → TEXT (存储 JSON 字符串)
-- 5. ON UPDATE CURRENT_TIMESTAMP → 需触发器模拟
-- 6. ENGINE=InnoDB 移除
```

---

## 4. 表结构详述

> **Index Definition Rule**
>
> 各表章节中的"索引"行仅用于说明该表涉及的约束类型。
>
> 项目唯一权威索引来源为 **§5.1 Index Summary**。
>
> ORM、DDL、Migration、Review、自测均必须以 §5.1 为准。
>
> 若 §4.x 与 §5.1 不一致，应以 §5.1 为准，并同步修正文档。

### 4.1 users — 用户表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | username | VARCHAR(50) | NOT | | 登录用户名 |
| 3 | password_hash | VARCHAR(255) | NOT | | bcrypt 密码哈希 |
| 4 | real_name | VARCHAR(50) | NOT | | 真实姓名 |
| 5 | phone | VARCHAR(20) | YES | NULL | 联系电话 |
| 6 | is_active | TINYINT(1) | NOT | 1 | 启用状态 |
| 7 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 8 | created_by | INT | YES | NULL | 创建人 ID |
| 9 | updated_by | INT | YES | NULL | 更新人 ID |
| 10 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 11 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), UNIQUE(username)

### 4.2a roles — 角色表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | name | VARCHAR(50) | NOT | | 角色标识（唯一） |
| 3 | display_name | VARCHAR(50) | NOT | | 角色显示名 |
| 4 | description | TEXT | YES | NULL | 角色描述 |
| 5 | is_system | TINYINT(1) | NOT | 0 | 是否系统内置角色 |
| 6 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 7 | created_by | INT | YES | NULL | 创建人 ID |
| 8 | updated_by | INT | YES | NULL | 更新人 ID |
| 9 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 10 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), UNIQUE(name)

### 4.2b permissions — 权限表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | code | VARCHAR(100) | NOT | | 权限编码（唯一，如 task:create） |
| 3 | name | VARCHAR(100) | NOT | | 权限名称 |
| 4 | description | TEXT | YES | NULL | 权限描述 |
| 5 | module | VARCHAR(50) | NOT | | 所属模块 |
| 6 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 7 | created_by | INT | YES | NULL | 创建人 ID |
| 8 | updated_by | INT | YES | NULL | 更新人 ID |
| 9 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 10 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), UNIQUE(code), INDEX(module)

### 4.2c user_roles — 用户-角色关联表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | user_id | INT | NOT | | 用户ID（FK → users.id） |
| 2 | role_id | INT | NOT | | 角色ID（FK → roles.id） |

**索引：** PRIMARY(user_id, role_id), INDEX(role_id)

### 4.2d role_permissions — 角色-权限关联表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | role_id | INT | NOT | | 角色ID（FK → roles.id） |
| 2 | permission_id | INT | NOT | | 权限ID（FK → permissions.id） |

**索引：** PRIMARY(role_id, permission_id), INDEX(permission_id)

### 4.3 customers — 客户表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | company_name | VARCHAR(200) | NOT | | 公司名称 |
| 3 | contact | VARCHAR(50) | YES | NULL | 联系人 |
| 4 | phone | VARCHAR(20) | YES | NULL | 联系电话 |
| 5 | address | TEXT | YES | NULL | 地址 |
| 6 | created_by | INT | YES | NULL | 创建人（FK → users.id） |
| 7 | updated_by | INT | YES | NULL | 更新人 ID |
| 8 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 9 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 10 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), INDEX(company_name)

### 4.4 trial_tasks — 试磨任务表（核心）

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | task_no | VARCHAR(20) | NOT | | 任务编号 (`YYYYMMDD-N`) |
| 3 | customer_id | INT | NOT | | 客户（FK → customers.id） |
| 4 | requirement | TEXT | NOT | | 加工要求 |
| 5 | tracking_no | VARCHAR(100) | YES | NULL | 快递单号 |
| 6 | sales_id | INT | NOT | | 销售（FK → users.id） |
| 7 | process_status | ENUM | NOT | 'created' | 流程状态（created/received/grinding/dispatched/closed） |
| 8 | result_status | ENUM | NOT | 'pending' | 结果状态（pending/passed/failed） |
| 9 | destination | ENUM | YES | NULL | 工件去向（returned_customer/retained_company/scrapped/returned_sales/other） |
| 10 | destination_date | DATE | YES | NULL | 工件去向日期 |
| 11 | failure_reason | TEXT | YES | NULL | 失败原因（result_status=failed 时填写） |
| 12 | created_by | INT | YES | NULL | 创建人 ID |
| 13 | updated_by | INT | YES | NULL | 更新人 ID |
| 14 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 15 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 16 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**流程状态流转（process_status）：**
```
created → received → grinding → dispatched → closed
```
- 禁止跳级、禁止逆向
- closed 为终态

**结果状态流转（result_status）：**
```
pending → passed
pending → failed
```
- 不可逆（passed/failed 不可互转）
- 终态

**索引：** PRIMARY(id), UNIQUE(task_no), INDEX(customer_id), INDEX(sales_id), INDEX(process_status), INDEX(result_status), INDEX(created_at), INDEX(is_deleted)

### 4.5 receipts — 收件记录表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | task_id | INT | NOT | | 任务（FK → trial_tasks.id, UNIQUE） |
| 3 | received_at | DATETIME | NOT | | 收件日期 |
| 4 | receiver_id | INT | NOT | | 收件人（FK → users.id） |
| 5 | image_paths | JSON | YES | NULL | 图片路径数组 |
| 6 | created_by | INT | YES | NULL | 创建人 ID |
| 7 | updated_by | INT | YES | NULL | 更新人 ID |
| 8 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 9 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 10 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), UNIQUE(task_id)

### 4.6 grinding_records — 试磨记录表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | task_id | INT | NOT | | 任务（FK, UNIQUE） |
| 3 | operator_id | INT | NOT | | 责任人（FK → users.id） |
| 4 | machine_type | VARCHAR(100) | YES | NULL | 试磨机型 |
| 5 | wheel_type | VARCHAR(100) | YES | NULL | 砂轮型号 |
| 6 | params | TEXT | YES | NULL | 加工参数 |
| 7 | start_time | DATETIME | YES | NULL | 领出时间 |
| 8 | end_time | DATETIME | YES | NULL | 完成时间 |
| 9 | image_paths | JSON | YES | NULL | 图片路径数组 |
| 10 | fail_reason | TEXT | YES | NULL | 失败原因 |
| 11 | created_by | INT | YES | NULL | 创建人 ID |
| 12 | updated_by | INT | YES | NULL | 更新人 ID |
| 13 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 14 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 15 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), UNIQUE(task_id), INDEX(operator_id), INDEX(machine_type), INDEX(start_time)

### 4.7 inspection_records — 检测记录表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | task_id | INT | NOT | | 任务（FK, UNIQUE） |
| 3 | report_path | VARCHAR(500) | YES | NULL | 报告文件路径 |
| 4 | accuracy | VARCHAR(100) | YES | NULL | 精度 |
| 5 | roughness | VARCHAR(100) | YES | NULL | 粗糙度 |
| 6 | result | ENUM | YES | NULL | pass / fail |
| 7 | inspector_id | INT | YES | NULL | 检测人（FK → users.id） |
| 8 | created_by | INT | YES | NULL | 创建人 ID |
| 9 | updated_by | INT | YES | NULL | 更新人 ID |
| 10 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 11 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 12 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), UNIQUE(task_id)

### 4.8 dispatches — 工件去向表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | task_id | INT | NOT | | 任务（FK, UNIQUE） |
| 3 | direction | VARCHAR(200) | NOT | | 去向 |
| 4 | dispatch_date | DATETIME | NOT | | 去向日期 |
| 5 | operator_id | INT | NOT | | 操作人（FK → users.id） |
| 6 | created_by | INT | YES | NULL | 创建人 ID |
| 7 | updated_by | INT | YES | NULL | 更新人 ID |
| 8 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 9 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 10 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), UNIQUE(task_id)

### 4.9 attachments — 附件表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | task_id | INT | NOT | | 任务（FK） |
| 3 | file_type | ENUM | NOT | | image/document/cad/video |
| 4 | file_name | VARCHAR(255) | NOT | | 原始文件名 |
| 5 | file_path | VARCHAR(500) | NOT | | 存储路径 |
| 6 | file_size | INT | YES | NULL | 文件大小(bytes) |
| 7 | uploaded_by | INT | NOT | | 上传人（FK → users.id） |
| 8 | created_by | INT | YES | NULL | 创建人 ID |
| 9 | updated_by | INT | YES | NULL | 更新人 ID |
| 10 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 11 | created_at | DATETIME | NOT | NOW | 上传时间 |
| 12 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), INDEX(task_id), INDEX(file_type)

### 4.10 system_logs — 系统日志表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | user_id | INT | NOT | | 操作人（FK → users.id） |
| 3 | action | ENUM | NOT | | create/update/delete/status_change |
| 4 | target_type | VARCHAR(50) | NOT | | 操作对象类型 |
| 5 | target_id | INT | YES | NULL | 操作对象 ID |
| 6 | changes | JSON | YES | NULL | 变更内容 |
| 7 | ip_address | VARCHAR(50) | YES | NULL | IP 地址 |
| 8 | created_by | INT | YES | NULL | 创建人 ID |
| 9 | updated_by | INT | YES | NULL | 更新人 ID |
| 10 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 11 | created_at | DATETIME | NOT | NOW | 操作时间 |
| 12 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), INDEX(user_id), INDEX(action), INDEX(created_at)

### 4.11 notifications — 消息提醒表

| # | 字段 | 类型 | 空 | 默认值 | 说明 |
|---|------|------|:--:|------|------|
| 1 | id | INT | | AUTO | 主键 |
| 2 | task_id | INT | NOT | | 任务（FK） |
| 3 | type | ENUM | NOT | | receipt_delay/grinding_delay/report_missing |
| 4 | message | TEXT | NOT | | 提醒内容 |
| 5 | is_read | TINYINT(1) | NOT | 0 | 是否已读 |
| 6 | target_user_id | INT | NOT | | 目标用户（FK → users.id） |
| 7 | created_by | INT | YES | NULL | 创建人 ID |
| 8 | updated_by | INT | YES | NULL | 更新人 ID |
| 9 | is_deleted | TINYINT(1) | NOT | 0 | 软删除标记 |
| 10 | created_at | DATETIME | NOT | NOW | 创建时间 |
| 11 | updated_at | DATETIME | NOT | NOW | 更新时间 |

**索引：** PRIMARY(id), INDEX(target_user_id), INDEX(is_read), INDEX(type)

---

## 5. 索引设计

### 5.1 索引清单

| 序号 | 表名 | 索引名 | 列 | 类型 | 用途 |
|------|------|------|------|------|------|
| I-01 | users | PRIMARY | id | 主键 | — |
| I-02 | users | uq_users_username | username | 唯一 | 登录查询 |
| I-03 | customers | PRIMARY | id | 主键 | — |
| I-04 | customers | ix_customers_company_name | company_name | 普通 | 客户搜索 |
| I-05 | trial_tasks | PRIMARY | id | 主键 | — |
| I-06 | trial_tasks | uq_trial_tasks_task_no | task_no | 唯一 | 任务编号查询 |
| I-07 | trial_tasks | ix_trial_tasks_customer_id | customer_id | 普通 | 按客户筛选 |
| I-08 | trial_tasks | ix_trial_tasks_sales_id | sales_id | 普通 | 按销售筛选 |
| I-09 | trial_tasks | ix_trial_tasks_process_status | process_status | 普通 | 按流程状态筛选 |
| I-10 | trial_tasks | ix_trial_tasks_result_status | result_status | 普通 | 按结果状态筛选 |
| I-11 | trial_tasks | ix_trial_tasks_created_at | created_at | 普通 | 按日期筛选 |
| I-12 | trial_tasks | ix_trial_tasks_is_deleted | is_deleted | 普通 | 软删除过滤 |
| I-13 | receipts | PRIMARY | id | 主键 | — |
| I-14 | receipts | uq_receipts_task_id | task_id | 唯一 | 任务关联 |
| I-15 | grinding_records | PRIMARY | id | 主键 | — |
| I-16 | grinding_records | uq_grinding_task_id | task_id | 唯一 | 任务关联 |
| I-17 | grinding_records | ix_grinding_operator_id | operator_id | 普通 | 按责任人筛选 |
| I-18 | grinding_records | ix_grinding_machine_type | machine_type | 普通 | 按机型筛选 |
| I-19 | grinding_records | ix_grinding_start_time | start_time | 普通 | 超时检查 |
| I-20 | inspection_records | PRIMARY | id | 主键 | — |
| I-21 | inspection_records | uq_inspection_task_id | task_id | 唯一 | 任务关联 |
| I-22 | dispatches | PRIMARY | id | 主键 | — |
| I-23 | dispatches | uq_dispatches_task_id | task_id | 唯一 | 任务关联 |
| I-24 | attachments | PRIMARY | id | 主键 | — |
| I-25 | attachments | ix_attachments_task_id | task_id | 普通 | 按任务查询 |
| I-26 | attachments | ix_attachments_file_type | file_type | 普通 | 按类型筛选 |
| I-27 | system_logs | PRIMARY | id | 主键 | — |
| I-28 | system_logs | ix_logs_user_id | user_id | 普通 | 按操作人筛选 |
| I-29 | system_logs | ix_logs_action | action | 普通 | 按操作类型筛选 |
| I-30 | system_logs | ix_logs_created_at | created_at | 普通 | 按时间筛选 |
| I-31 | notifications | PRIMARY | id | 主键 | — |
| I-32 | notifications | ix_notifications_target_user | target_user_id | 普通 | 按用户查消息 |
| I-33 | notifications | ix_notifications_is_read | is_read | 普通 | 未读消息过滤 |
| I-34 | notifications | ix_notifications_type | type | 普通 | 按类型筛选 |
| I-35 | roles | PRIMARY | id | 主键 | — |
| I-36 | roles | uq_roles_name | name | 唯一 | 角色标识查询 |
| I-37 | permissions | PRIMARY | id | 主键 | — |
| I-38 | permissions | uq_permissions_code | code | 唯一 | 权限编码查询 |
| I-39 | permissions | ix_permissions_module | module | 普通 | 按模块筛选 |
| I-40 | user_roles | PRIMARY | (user_id, role_id) | 主键 | — |
| I-41 | user_roles | ix_user_roles_role_id | role_id | 普通 | 按角色查用户 |
| I-42 | role_permissions | PRIMARY | (role_id, permission_id) | 主键 | — |
| I-43 | role_permissions | ix_role_permissions_perm | permission_id | 普通 | 按权限查角色 |

### 5.2 复合索引（推荐）

以下复合索引用于高频组合查询，可在 MySQL 正式环境添加：

```sql
-- 任务列表多条件查询
CREATE INDEX ix_tasks_process_status_created ON trial_tasks (process_status, created_at DESC);

-- 按责任人 + 状态查询任务
CREATE INDEX ix_grinding_operator_status ON grinding_records (operator_id);
-- （配合 JOIN trial_tasks.process_status 使用）

-- 日志按用户 + 时间查询
CREATE INDEX ix_logs_user_time ON system_logs (user_id, created_at DESC);

-- 消息按用户 + 已读状态查询
CREATE INDEX ix_notifications_user_read ON notifications (target_user_id, is_read, created_at DESC);
```

---

## 6. 关系与外键

### 6.1 外键关系汇总

| 子表 | 外键列 | 父表 | 父键 | 删除规则 | 更新规则 | 说明 |
|------|------|------|------|------|------|------|
| customers | created_by | users | id | SET NULL | — | 用户删除后客户保留 |
| trial_tasks | customer_id | customers | id | RESTRICT | — | 有任务则不能删客户 |
| trial_tasks | sales_id | users | id | RESTRICT | — | 有任务则不能删销售 |
| receipts | task_id | trial_tasks | id | CASCADE | — | 删任务级联删除收件 |
| receipts | receiver_id | users | id | RESTRICT | — | |
| grinding_records | task_id | trial_tasks | id | CASCADE | — | 删任务级联删除试磨 |
| grinding_records | operator_id | users | id | RESTRICT | — | |
| inspection_records | task_id | trial_tasks | id | CASCADE | — | 删任务级联删除检测 |
| inspection_records | inspector_id | users | id | SET NULL | — | |
| dispatches | task_id | trial_tasks | id | CASCADE | — | 删任务级联删除去向 |
| dispatches | operator_id | users | id | RESTRICT | — | |
| attachments | task_id | trial_tasks | id | CASCADE | — | 删任务级联删除附件 |
| attachments | uploaded_by | users | id | RESTRICT | — | |
| system_logs | user_id | users | id | RESTRICT | — | 日志不可删除 |
| notifications | task_id | trial_tasks | id | CASCADE | — | 删任务级联删除通知 |
| notifications | target_user_id | users | id | CASCADE | — | 删用户级联删除通知 |
| user_roles | user_id | users | id | CASCADE | — | 删用户级联删除关联 |
| user_roles | role_id | roles | id | CASCADE | — | 删角色级联删除关联 |
| role_permissions | role_id | roles | id | CASCADE | — | 删角色级联删除关联 |
| role_permissions | permission_id | permissions | id | CASCADE | — | 删权限级联删除关联 |

> 注：本项目使用 SQLAlchemy ORM 作为唯一建模来源，主键 id 原则上永不更新，因此 ON UPDATE 不显式指定，采用数据库默认行为。

### 6.2 级联删除规则说明

| 规则 | 含义 | 使用场景 |
|------|------|------|
| CASCADE | 父表删除时子表记录自动删除 | 任务删除时，关联的收件/试磨/检测/去向/附件/通知一并删除 |
| RESTRICT | 父表有子表引用时禁止删除 | 客户有任务时禁止删除客户；用户有任务时禁止删除用户 |
| SET NULL | 父表删除时子表外键置为 NULL | 用户删除后，创建的客户记录保留但 created_by 置空 |

---

## 7. 视图设计

### 7.1 任务详情视图（推荐）

```sql
CREATE VIEW v_task_details AS
SELECT
    t.id                AS task_id,
    t.task_no,
    t.requirement,
    t.tracking_no,
    t.process_status,
    t.result_status,
    t.created_at        AS task_created_at,
    t.updated_at        AS task_updated_at,

    -- 客户信息
    c.id                AS customer_id,
    c.company_name,
    c.contact           AS customer_contact,
    c.phone             AS customer_phone,

    -- 销售信息
    u_sales.id          AS sales_id,
    u_sales.real_name   AS sales_name,

    -- 收件信息
    r.received_at,
    u_recv.real_name    AS receiver_name,

    -- 试磨信息
    g.operator_id       AS grinder_id,
    u_grind.real_name   AS grinder_name,
    g.machine_type,
    g.wheel_type,
    g.start_time,
    g.end_time,
    g.fail_reason,

    -- 检测信息
    i.result            AS inspection_result,
    i.accuracy,
    i.roughness,
    i.report_path,

    -- 去向信息
    d.direction,
    d.dispatch_date

FROM trial_tasks t
LEFT JOIN customers c         ON t.customer_id = c.id
LEFT JOIN users u_sales       ON t.sales_id = u_sales.id
LEFT JOIN receipts r          ON t.id = r.task_id
LEFT JOIN users u_recv        ON r.receiver_id = u_recv.id
LEFT JOIN grinding_records g  ON t.id = g.task_id
LEFT JOIN users u_grind       ON g.operator_id = u_grind.id
LEFT JOIN inspection_records i ON t.id = i.task_id
LEFT JOIN dispatches d        ON t.id = d.task_id
WHERE t.is_deleted = 0;
```

### 7.2 统计视图

```sql
-- 月度统计
CREATE VIEW v_monthly_stats AS
SELECT
    DATE_FORMAT(created_at, '%Y-%m') AS month,
    COUNT(*)                         AS total_tasks,
    SUM(CASE WHEN result_status = 'passed' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN result_status = 'failed' THEN 1 ELSE 0 END)    AS failed
FROM trial_tasks
WHERE is_deleted = 0
GROUP BY DATE_FORMAT(created_at, '%Y-%m');

-- 客户排行
CREATE VIEW v_customer_ranking AS
SELECT
    c.id,
    c.company_name,
    COUNT(t.id) AS task_count,
    SUM(CASE WHEN t.result_status = 'passed' THEN 1 ELSE 0 END) AS completed_count
FROM customers c
LEFT JOIN trial_tasks t ON c.id = t.customer_id AND t.is_deleted = 0
GROUP BY c.id, c.company_name
ORDER BY task_count DESC;
```

---

## 8. 种子数据

### 8.1 默认用户

```sql
-- 密码均为 "admin123" 的 bcrypt 哈希
-- 生产环境请修改密码！

INSERT INTO users (username, password_hash, real_name, phone) VALUES
('admin',   '$2b$12$LJ3m4ys3LkBCVxJGqOjPkuYVOYpGOKbHgEMoJxYzRqcMdFNP2sCuS', '系统管理员', '13800000000'),
('sales01', '$2b$12$LJ3m4ys3LkBCVxJGqOjPkuYVOYpGOKbHgEMoJxYzRqcMdFNP2sCuS', '张销售',     '13800000001'),
('tech01',  '$2b$12$LJ3m4ys3LkBCVxJGqOjPkuYVOYpGOKbHgEMoJxYzRqcMdFNP2sCuS', '李技术',     '13800000002'),
('tech02',  '$2b$12$LJ3m4ys3LkBCVxJGqOjPkuYVOYpGOKbHgEMoJxYzRqcMdFNP2sCuS', '王技术',     '13800000003'),
('leader01','$2b$12$LJ3m4ys3LkBCVxJGqOjPkuYVOYpGOKbHgEMoJxYzRqcMdFNP2sCuS', '陈领导',     '13800000004');
```

### 8.2 默认客户

```sql
INSERT INTO customers (company_name, contact, phone, address, created_by) VALUES
('上海精密机械有限公司', '赵经理', '021-12345678', '上海市浦东新区XX路100号', 1),
('苏州轴承制造厂',       '钱工',   '0512-87654321', '苏州市工业园区XX路200号', 1),
('浙江汽车零部件有限公司', '孙总',  '0571-56789012', '杭州市余杭区XX路300号', 1);
```

### 8.3 默认角色

```sql
INSERT INTO roles (name, display_name, description, is_system) VALUES
('admin',      '管理员', '系统管理员，拥有全部权限', 1),
('sales',      '销售',   '销售人员，负责创建任务和客户管理', 1),
('technician', '技术员', '技术员，负责收件、试磨、检测、去向', 1),
('leader',     '领导',   '领导，查看统计报表和仪表盘', 1);
```

### 8.4 默认权限

```sql
INSERT INTO permissions (code, name, module, description) VALUES
('task:create',       '创建任务',   'task',        '创建试磨任务'),
('task:view',         '查看任务',   'task',        '查看任务详情'),
('task:edit',         '编辑任务',   'task',        '编辑任务信息'),
('task:delete',       '删除任务',   'task',        '删除任务'),
('customer:create',   '创建客户',   'customer',    '新增客户'),
('customer:view',     '查看客户',   'customer',    '查看客户列表'),
('customer:edit',     '编辑客户',   'customer',    '编辑客户信息'),
('customer:delete',   '删除客户',   'customer',    '删除客户'),
('receipt:create',    '收件登记',   'receipt',     '登记收件'),
('grinding:start',    '开始试磨',   'grinding',    '开始试磨'),
('grinding:complete', '完成试磨',   'grinding',    '完成试磨'),
('inspection:upload', '上传报告',   'inspection',  '上传检测报告'),
('dispatch:create',   '填写去向',   'dispatch',    '填写工件去向'),
('report:view',       '查看报告',   'report',      '查看检测报告'),
('user:manage',       '用户管理',   'user',        '管理用户'),
('system:manage',     '系统设置',   'system',      '系统设置'),
('log:view',          '查看日志',   'log',         '查看操作日志'),
('statistics:view',   '查看统计',   'statistics',  '查看统计报表'),
('dashboard:view',    '查看仪表盘', 'dashboard',   '查看仪表盘'),
('attachment:upload', '上传附件',   'attachment',  '上传附件');
```

### 8.5 默认角色-权限关联

```sql
-- admin: 所有权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions;

-- sales: 任务+客户+查看
INSERT INTO role_permissions (role_id, permission_id)
SELECT 2, id FROM permissions WHERE code IN ('task:create','task:view','task:edit','customer:create','customer:view','customer:edit','report:view','statistics:view','dashboard:view');

-- technician: 操作类权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 3, id FROM permissions WHERE code IN ('task:view','receipt:create','grinding:start','grinding:complete','inspection:upload','dispatch:create','report:view','attachment:upload','dashboard:view');

-- leader: 查看类权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 4, id FROM permissions WHERE code IN ('task:view','report:view','statistics:view','dashboard:view','log:view');
```

### 8.6 默认用户-角色关联

```sql
INSERT INTO user_roles (user_id, role_id) VALUES
(1, 1),  -- admin → admin
(2, 2),  -- sales01 → sales
(3, 3),  -- tech01 → technician
(4, 3),  -- tech02 → technician
(5, 4);  -- leader01 → leader
```

---

## 9. Alembic 迁移策略

### 9.1 初始化

```bash
cd server
alembic init database/migrations
```

### 9.2 生成迁移脚本

```bash
# 修改 models 后生成迁移
alembic revision --autogenerate -m "描述性信息"

# 示例
alembic revision --autogenerate -m "add_is_deleted_to_trial_tasks"
```

### 9.3 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 回滚一个版本
alembic downgrade -1

# 查看当前版本
alembic current
```

### 9.4 迁移命名规范

```
{YYYYMMDD}_{序号}_{简短描述}.py

示例:
  20260702_001_initial_schema.py
  20260702_002_add_notifications_table.py
```

---

## 附录 A：SQLAlchemy ORM 配置对照

| SQLAlchemy 类型 | MySQL 类型 | SQLite 类型 |
|------|------|------|
| Integer | INT | INTEGER |
| String(50) | VARCHAR(50) | VARCHAR(50) |
| Text | TEXT | TEXT |
| Boolean | TINYINT(1) | INTEGER |
| DateTime | DATETIME | DATETIME |
| Enum | ENUM | VARCHAR + CHECK |
| JSON | JSON | TEXT |
| Float | FLOAT | REAL |

## 附录 B：数据量估算

| 表名 | 预计年增长 | 3年后预估 |
|------|------|------|
| users | 0-5 条 | 20 条 |
| roles | 0-1 条 | 4 条 |
| permissions | 0-2 条 | 20 条 |
| user_roles | = users | 20 条 |
| role_permissions | 0-5 条 | 80 条 |
| customers | 50-100 条 | 500 条 |
| trial_tasks | 500-2000 条 | 10,000 条 |
| receipts | = trial_tasks | 10,000 条 |
| grinding_records | = trial_tasks | 10,000 条 |
| inspection_records | = trial_tasks | 10,000 条 |
| dispatches | = trial_tasks | 10,000 条 |
| attachments | 5 × trial_tasks | 50,000 条 |
| system_logs | 10 × trial_tasks | 100,000 条 |
| notifications | 3 × trial_tasks | 30,000 条 |

> 数据量级：小型企业应用，3 年数据总量 < 50 万条，SQLite 可承载，MySQL 绰绰有余。

---

> **文档维护者：** GTMS 开发团队  
> **最后更新：** 2026-07-02  
> **对应版本：** V1.0