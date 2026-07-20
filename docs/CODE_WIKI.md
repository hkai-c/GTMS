# 磨床试磨管理系统（GTMS）— Code Wiki

> **Grinding Trial Management System**  
> 版本：V1.0 | 文档生成日期：2026-07-02

---

## 目录

1. [项目概述](#1-项目概述)
2. [项目目录结构](#2-项目目录结构)
3. [系统架构](#3-系统架构)
4. [技术栈与依赖](#4-技术栈与依赖)
5. [数据库设计](#5-数据库设计)
6. [后端模块详解（server/）](#6-后端模块详解server)
7. [桌面客户端模块详解（client/）](#7-桌面客户端模块详解client)
8. [小程序模块详解（miniapp/）](#8-小程序模块详解miniapp)
9. [API 接口文档](#9-api-接口文档)
10. [状态流转机制](#10-状态流转机制)
11. [关键类与函数说明](#11-关键类与函数说明)
12. [附件管理规范](#12-附件管理规范)
13. [权限模型](#13-权限模型)
14. [项目运行方式](#14-项目运行方式)
15. [开发规范](#15-开发规范)
16. [V1.0 开发计划](#16-v10-开发计划)

---

## 1. 项目概述

### 1.1 项目名称

磨床试磨管理系统（GTMS — Grinding Trial Management System）

### 1.2 项目目标

建立一套适用于磨床制造企业的试磨件全过程管理系统，实现从**销售接单 → 试磨完成 → 检测报告上传 → 工件去向登记**的全流程数字化管理。

### 1.3 支持平台

| 平台 | 技术 | 说明 |
|------|------|------|
| Windows 桌面客户端 | Python + PySide6 | 主力操作终端 |
| 微信小程序 | UniApp | 移动端查看与操作 |
| Web 管理后台 | （V2.0 预留） | 浏览器端管理 |

### 1.4 用户角色

| 角色 | 职责 |
|------|------|
| **销售** | 新建试磨任务、填写客户信息、查看进度、查看检测报告 |
| **技术员** | 收件登记、上传图片、填写试磨责任人、上传检测报告、填写试磨机型、填写失败原因 |
| **管理员** | 用户管理、权限管理、数据管理、系统设置 |
| **领导** | 查看今日任务、完成率、工作量、统计报表 |

---

## 2. 项目目录结构

```
data_control/
├── client/                        # 桌面客户端 (PySide6)
│   ├── main.py                    # 应用入口
│   ├── config.py                  # 客户端配置
│   ├── views/                     # 界面模块
│   │   ├── login_view.py          # 登录界面
│   │   ├── main_window.py         # 主窗口
│   │   ├── dashboard_view.py      # 首页仪表盘 / 消息提醒
│   │   ├── customer_view.py       # 客户管理
│   │   ├── trial_task_view.py     # 试磨任务管理
│   │   ├── receipt_view.py        # 收件管理
│   │   ├── grinding_view.py       # 试磨管理
│   │   ├── inspection_view.py     # 检测管理
│   │   ├── dispatch_view.py       # 工件去向
│   │   ├── query_view.py          # 查询统计
│   │   ├── user_manage_view.py    # 用户管理（管理员）
│   │   ├── system_log_view.py     # 操作日志
│   │   └── settings_view.py       # 系统设置
│   ├── widgets/                   # 可复用组件
│   │   ├── status_badge.py        # 状态标签组件
│   │   ├── image_viewer.py        # 图片预览组件
│   │   ├── file_uploader.py       # 文件上传组件
│   │   └── search_bar.py          # 搜索栏组件
│   ├── services/                  # 客户端服务层（API调用封装）
│   │   ├── api_client.py          # HTTP 请求封装
│   │   ├── auth_service.py        # 认证服务
│   │   ├── customer_service.py    # 客户服务
│   │   ├── task_service.py        # 任务服务
│   │   ├── receipt_service.py     # 收件服务
│   │   ├── grinding_service.py    # 试磨服务
│   │   ├── inspection_service.py  # 检测服务
│   │   ├── dispatch_service.py    # 去向服务
│   │   ├── query_service.py       # 查询服务
│   │   ├── log_service.py         # 日志服务
│   │   └── notification_service.py # 消息提醒服务
│   └── utils/                     # 客户端工具
│       ├── validators.py          # 表单校验
│       ├── formatters.py          # 格式化工具
│       └── constants.py           # 常量定义
│
├── server/                        # 后端服务 (FastAPI)
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 服务端配置
│   ├── core/                      # 核心模块
│   │   ├── security.py            # 认证与权限 (JWT)
│   │   ├── dependencies.py        # 依赖注入
│   │   └── exceptions.py          # 自定义异常
│   ├── models/                    # 数据库模型 (SQLAlchemy ORM)
│   │   ├── base.py                # 基础模型
│   │   ├── user.py                # 用户模型
│   │   ├── customer.py            # 客户模型
│   │   ├── trial_task.py          # 试磨任务模型
│   │   ├── receipt.py             # 收件记录模型
│   │   ├── grinding.py            # 试磨记录模型
│   │   ├── inspection.py          # 检测记录模型
│   │   ├── dispatch.py            # 工件去向模型
│   │   ├── attachment.py          # 附件模型
│   │   ├── system_log.py          # 系统日志模型
│   │   └── notification.py        # 消息提醒模型
│   ├── schemas/                   # Pydantic 数据校验
│   │   ├── user_schema.py
│   │   ├── customer_schema.py
│   │   ├── trial_task_schema.py
│   │   ├── receipt_schema.py
│   │   ├── grinding_schema.py
│   │   ├── inspection_schema.py
│   │   ├── dispatch_schema.py
│   │   ├── attachment_schema.py
│   │   ├── log_schema.py
│   │   └── notification_schema.py
│   ├── routers/                   # API 路由
│   │   ├── auth_router.py         # 登录/认证
│   │   ├── customer_router.py     # 客户 CRUD
│   │   ├── trial_task_router.py   # 试磨任务 CRUD
│   │   ├── receipt_router.py      # 收件管理
│   │   ├── grinding_router.py     # 试磨管理
│   │   ├── inspection_router.py   # 检测管理
│   │   ├── dispatch_router.py     # 工件去向
│   │   ├── query_router.py        # 查询统计
│   │   ├── user_router.py         # 用户管理
│   │   ├── log_router.py          # 操作日志
│   │   ├── notification_router.py # 消息提醒
│   │   └── upload_router.py       # 文件上传
│   ├── services/                  # 业务逻辑层
│   │   ├── auth_service.py        # 认证逻辑
│   │   ├── customer_service.py    # 客户业务逻辑
│   │   ├── task_service.py        # 任务业务逻辑
│   │   ├── receipt_service.py     # 收件业务逻辑
│   │   ├── grinding_service.py    # 试磨业务逻辑
│   │   ├── inspection_service.py  # 检测业务逻辑
│   │   ├── dispatch_service.py    # 去向业务逻辑
│   │   ├── query_service.py       # 查询统计逻辑
│   │   ├── log_service.py         # 日志记录逻辑
│   │   └── notification_service.py # 消息提醒逻辑
│   ├── utils/                     # 工具函数
│   │   ├── id_generator.py        # 任务编号生成器 (YYYYMMDD-N)
│   │   ├── file_handler.py        # 文件处理
│   │   └── backup.py              # 自动备份
│   └── middleware/                 # 中间件
│       ├── log_middleware.py       # 请求日志中间件
│       └── cors_middleware.py      # 跨域中间件
│
├── database/                      # 数据库
│   ├── migrations/                # 数据库迁移 (Alembic)
│   ├── seed_data.py               # 初始数据
│   └── gtms.db                    # SQLite 开发数据库
│
├── miniapp/                       # 微信小程序 (UniApp)
│   ├── pages/
│   │   ├── login/                 # 登录页
│   │   ├── dashboard/             # 首页
│   │   ├── task_list/             # 任务列表
│   │   ├── task_detail/           # 任务详情
│   │   ├── receipt/               # 收件
│   │   ├── statistics/            # 统计
│   │   └── notification/          # 消息通知
│   ├── api/                       # 接口封装
│   └── utils/
│
├── docs/                          # 文档
│   └── CODE_WIKI.md               # 本文件
│
├── uploads/                       # 上传文件存储
│   ├── images/                    # 收件图片、试磨图片
│   ├── reports/                   # 检测报告 (PDF/Word/Excel)
│   ├── cad/                       # CAD 文件 (DWG/DXF)
│   └── videos/                    # 视频文件
│
├── backup/                        # 自动备份目录
│
├── requirements.txt               # Python 依赖
├── README.md                      # 项目说明
└── .gitignore
```

---

## 3. 系统架构

### 3.1 整体架构图

```
┌──────────────────────────────────────────────────────────────────┐
│                        客户端层 (Client)                          │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐  │
│  │ Windows 桌面端   │  │   微信小程序       │  │ Web 管理后台    │  │
│  │ (PySide6)       │  │   (UniApp)       │  │  (V2.0 预留)   │  │
│  └────────┬────────┘  └────────┬─────────┘  └───────┬────────┘  │
│           │                    │                     │           │
│           └────────────────────┼─────────────────────┘           │
│                                │ HTTP/REST                       │
└────────────────────────────────┼──────────────────────────────────┘
                                 │
┌────────────────────────────────┼──────────────────────────────────┐
│                      服务层 (Server)                              │
│  ┌─────────────────────────────┴──────────────────────────────┐  │
│  │                    FastAPI 应用                              │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │  │
│  │  │ Middleware│  │ Routers  │  │ Schemas  │  │  CORS    │   │  │
│  │  └──────────┘  └────┬─────┘  └──────────┘  └──────────┘   │  │
│  │                      │                                      │  │
│  │  ┌───────────────────┴──────────────────────────────────┐  │  │
│  │  │                  Services (业务逻辑层)                 │  │  │
│  │  │  Auth │ Customer │ Task │ Receipt │ Grinding │ ...   │  │  │
│  │  └───────────────────┬──────────────────────────────────┘  │  │
│  │                      │                                      │  │
│  │  ┌───────────────────┴──────────────────────────────────┐  │  │
│  │  │              Models (SQLAlchemy ORM)                  │  │  │
│  │  └───────────────────┬──────────────────────────────────┘  │  │
│  └──────────────────────┼─────────────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                    数据层 (Database)                              │
│  ┌───────────────────────┴──────────────────────────────────┐   │
│  │          SQLite (开发) / MySQL (正式)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    uploads/ (文件存储)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 分层职责

| 层级 | 职责 | 规则 |
|------|------|------|
| **Views** (client/views/) | 界面渲染、用户交互 | 不包含业务逻辑 |
| **Services** (client/services/) | 封装 API 调用 | 仅负责 HTTP 通信 |
| **Routers** (server/routers/) | 路由定义、请求校验 | 不含业务逻辑 |
| **Services** (server/services/) | 核心业务逻辑 | 所有业务规则在此 |
| **Models** (server/models/) | 数据库 ORM 映射 | 统一封装数据库操作 |
| **Schemas** (server/schemas/) | 请求/响应数据校验 | Pydantic 模型 |

---

## 4. 技术栈与依赖

### 4.1 技术选型

| 层级 | 技术 | 版本要求 |
|------|------|----------|
│ 桌面端 | Python 3.13 / PySide6 | >= 6.5 |
│ 后端 | Python 3.13 / FastAPI | >= 0.100 |
| ORM | SQLAlchemy | >= 2.0 |
| 数据库 | SQLite (开发) / MySQL 8.0 (正式) | — |
| 认证 | python-jose (JWT) | >= 3.3 |
| 文件校验 | python-multipart | — |
| 迁移工具 | Alembic | >= 1.12 |
| 小程序 | UniApp (Vue3) | — |
| 打包 | PyInstaller | — |

### 4.2 requirements.txt

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.0
pydantic>=2.7.0
pydantic-settings>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9
pyside6>=6.11.0
httpx>=0.27.0
```

---

## 5. 数据库设计

### 5.1 ER 图（逻辑关系）

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐
│     User     │     │   Customer   │     │      TrialTask       │
│──────────────│     │──────────────│     │──────────────────────│
│ id           │     │ id           │◄────│ customer_id          │
│ username     │     │ company_name │     │ task_no              │
│ password_hash│     │ contact      │     │ requirement          │
│ real_name    │     │ phone        │     │ tracking_no          │
│ phone        │     │ address      │     │ sales_id ────────────┼──► User
│ is_active    │     │ created_by ──┼──►  │ process_status       │
│ is_deleted   │     │ updated_by   │     │ result_status        │
│ created_by   │     │ is_deleted   │     │ destination          │
│ updated_by   │     │ created_at   │     │ destination_date     │
│ created_at   │     │ updated_at   │     │ failure_reason       │
│ updated_at   │     └──────────────┘     │ created_by           │
└──────┬───────┘                          │ updated_by           │
       │ (user_roles)                     │ is_deleted           │
       ▼                                  │ created_at           │
┌──────────────┐    ┌──────────────┐      │ updated_at           │
│     Role     │    │  Permission  │     └──────┬───────────────┘
│──────────────│    │──────────────│           │
│ id           │    │ id           │     ┌─────┴──────┐ ┌──────────────┐
│ name         │    │ code         │     │────────────│ │──────────────│
│ display_name │    │ name         │     │ task_id ───┼►│ task_id ─────┼──►
│ description  │    │ description  │     │ received_at│ │ operator_id  │
│ is_system    │    │ module       │     │ receiver_id│ │ machine_type │
│ is_deleted   │    │ is_deleted   │     │ image_paths│ │ wheel_type   │
│ created_by   │    │ created_by   │     └────────────┘ │ params       │
│ updated_by   │    │ updated_by   │                    │ start_time   │
│ created_at   │    │ created_at   │                    │ end_time     │
│ updated_at   │    │ updated_at   │     ┌──────────────┐ ┌──────────────┐
└──────────────┘    └──────────────┘     │ Inspection  │ │  Dispatch    │
                                         │─────────────│ │──────────────│
                                         │ task_id ────┼►│ task_id ─────┼──►
RBAC: User ↔ user_roles ↔ Role          │ report_path │ │ direction    │
      Role ↔ role_permissions ↔ Permission│ accuracy   │ │ dispatch_date│
                                         │ roughness   │ │ operator_id  │
                                         │ result      │ └──────────────┘
                                         │ inspector_id│
                                         └──────────────┘
```

### 5.2 核心数据表结构

#### 5.2.1 用户表 (users)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, AUTO_INCREMENT | 主键 |
| username | String(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | String(255) | NOT NULL | 密码哈希 (bcrypt) |
| real_name | String(50) | NOT NULL | 真实姓名 |
| phone | String(20) | — | 联系电话 |
| is_active | Boolean | DEFAULT True | 是否启用 |
| is_deleted | Boolean | DEFAULT False | 软删除 |
| created_by | Integer | — | 创建人 |
| updated_by | Integer | — | 更新人 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | ON UPDATE | 更新时间 |

用户与角色通过 user_roles 关联表实现多对多关系（纯 RBAC，无单一 role_id）。

#### 5.2.1a 角色表 (roles)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| name | String(50) | UNIQUE, NOT NULL | 角色标识 (admin/sales/technician/leader) |
| display_name | String(50) | NOT NULL | 显示名称 |
| description | Text | — | 角色描述 |
| is_system | Boolean | DEFAULT False | 系统角色（不可删除） |

#### 5.2.1b 权限表 (permissions)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| code | String(100) | UNIQUE, NOT NULL | 权限标识 (task:create) |
| name | String(100) | NOT NULL | 权限名称 |
| description | Text | — | 权限描述 |
| module | String(50) | NOT NULL | 所属模块 |

#### 5.2.1c 用户-角色关联表 (user_roles)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | Integer | PK, FK → users.id | 用户ID |
| role_id | Integer | PK, FK → roles.id | 角色ID |

#### 5.2.1d 角色-权限关联表 (role_permissions)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| role_id | Integer | PK, FK → roles.id | 角色ID |
| permission_id | Integer | PK, FK → permissions.id | 权限ID |

#### 5.2.2 客户表 (customers)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| company_name | String(200) | NOT NULL | 公司名称 |
| contact | String(50) | — | 联系人 |
| phone | String(20) | — | 联系电话 |
| address | Text | — | 地址 |
| created_by | Integer | FK → users.id | 创建人 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | ON UPDATE | 更新时间 |

#### 5.2.3 试磨任务表 (trial_tasks) — 核心表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| task_no | String(20) | UNIQUE, NOT NULL | 任务编号 (`YYYYMMDD-N`) |
| customer_id | Integer | FK → customers.id | 客户 |
| requirement | Text | NOT NULL | 加工要求 |
| tracking_no | String(100) | — | 快递单号 |
| sales_id | Integer | FK → users.id | 接单人员 |
| process_status | Enum | NOT NULL, DEFAULT 'created' | 流程状态 |
| result_status | Enum | NOT NULL, DEFAULT 'pending' | 结果状态 |
| destination | Enum | NULL | 工件去向 |
| destination_date | Date | NULL | 去向日期 |
| failure_reason | Text | NULL | 失败原因 |
| created_by | Integer | — | 创建人 |
| updated_by | Integer | — | 更新人 |
| is_deleted | Boolean | DEFAULT False | 软删除 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | ON UPDATE | 更新时间 |

**流程状态 (process_status)：**
created → received → grinding → dispatched → closed（禁止跳级逆向，closed 终态）

**结果状态 (result_status)：**
pending → passed | failed（不可逆，passed/failed 均为终态）

**工件去向 (destination)：**
returned_customer / retained_company / scrapped / returned_sales / other

#### 5.2.4 收件记录表 (receipts)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| task_id | Integer | FK → trial_tasks.id, UNIQUE | 关联任务 |
| received_at | DateTime | NOT NULL | 收件日期 |
| receiver_id | Integer | FK → users.id | 收件人 |
| image_paths | JSON/Text | — | 收件图片路径列表 |

#### 5.2.5 试磨记录表 (grinding_records)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| task_id | Integer | FK → trial_tasks.id, UNIQUE | 关联任务 |
| operator_id | Integer | FK → users.id | 试磨责任人 |
| machine_type | String(100) | — | 试磨机型 |
| wheel_type | String(100) | — | 砂轮型号 |
| params | Text | — | 加工参数 |
| start_time | DateTime | — | 工件领出时间 |
| end_time | DateTime | — | 完成时间 |
| image_paths | JSON/Text | — | 试磨图片路径列表 |
| fail_reason | Text | — | 失败原因 |

#### 5.2.6 检测记录表 (inspection_records)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| task_id | Integer | FK → trial_tasks.id, UNIQUE | 关联任务 |
| report_path | String(500) | — | 检测报告文件路径 |
| accuracy | String(100) | — | 精度 |
| roughness | String(100) | — | 粗糙度 |
| result | Enum | — | pass / fail |
| inspector_id | Integer | FK → users.id | 检测人 |

#### 5.2.7 工件去向表 (dispatches)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| task_id | Integer | FK → trial_tasks.id, UNIQUE | 关联任务 |
| direction | String(200) | NOT NULL | 去向 |
| dispatch_date | DateTime | NOT NULL | 去向日期 |
| operator_id | Integer | FK → users.id | 操作人 |
| created_by | Integer | — | 创建人 |
| updated_by | Integer | — | 更新人 |
| is_deleted | Boolean | DEFAULT False | 软删除 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | ON UPDATE | 更新时间 |

#### 5.2.8 附件表 (attachments)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| task_id | Integer | FK → trial_tasks.id | 关联任务 |
| file_type | Enum | NOT NULL | image / document / cad / video |
| file_name | String(255) | NOT NULL | 原始文件名 |
| file_path | String(500) | NOT NULL | 存储路径 |
| file_size | Integer | — | 文件大小 (bytes) |
| uploaded_by | Integer | FK → users.id | 上传人 |
| created_by | Integer | — | 创建人 |
| updated_by | Integer | — | 更新人 |
| is_deleted | Boolean | DEFAULT False | 软删除 |
| created_at | DateTime | DEFAULT NOW | 上传时间 |
| updated_at | DateTime | ON UPDATE | 更新时间 |

#### 5.2.9 系统日志表 (system_logs)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| user_id | Integer | FK → users.id | 操作人 |
| action | String(50) | NOT NULL | create / update / delete |
| target_type | String(50) | NOT NULL | 操作对象类型 |
| target_id | Integer | — | 操作对象 ID |
| changes | JSON/Text | — | 变更内容 |
| ip_address | String(50) | — | IP 地址 |
| created_by | Integer | — | 创建人 |
| updated_by | Integer | — | 更新人 |
| is_deleted | Boolean | DEFAULT False | 软删除 |
| created_at | DateTime | DEFAULT NOW | 操作时间 |
| updated_at | DateTime | ON UPDATE | 更新时间 |

#### 5.2.10 消息提醒表 (notifications)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK | 主键 |
| task_id | Integer | FK → trial_tasks.id | 关联任务 |
| type | Enum | NOT NULL | receipt_delay / grinding_delay / report_missing |
| message | Text | NOT NULL | 提醒内容 |
| is_read | Boolean | DEFAULT False | 是否已读 |
| target_user_id | Integer | FK → users.id | 目标用户 |
| created_by | Integer | — | 创建人 |
| updated_by | Integer | — | 更新人 |
| is_deleted | Boolean | DEFAULT False | 软删除 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | ON UPDATE | 更新时间 |

---

## 6. 后端模块详解（server/）

### 6.1 入口文件 `main.py`

```python
# FastAPI 应用入口
# Sprint 2 已冻结：仅允许新增 register_exception_handlers() 调用和 Router 注册，
# 不得修改已有代码。

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from server.core.exception_handlers import register_exception_handlers
from server.middleware.cors_middleware import setup_cors
from server.middleware.log_middleware import setup_request_logging

app = FastAPI(
    title="GTMS API",
    version="0.2.0",
    description="Grinding Trial Management System API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ① 注册 CORS 中间件
setup_cors(app)

# ② 注册请求日志中间件
setup_request_logging(app)

# ③ 注册全局异常处理器
register_exception_handlers(app)

# ④ 注册路由（Sprint 3 开始逐步添加）
# app.include_router(auth_router.router, prefix="/api/auth", tags=["认证"])
# ...


@app.get("/")
async def root() -> JSONResponse:
    """健康检查 — 根路径"""
    return JSONResponse(content={
        "message": "GTMS API Running",
        "version": "0.2.0",
    })


@app.get("/health")
async def health_check() -> JSONResponse:
    """健康检查端点"""
    return JSONResponse(content={"status": "ok"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
```

### 6.2 核心模块 (core/)

#### 6.2.1 `security.py` — 认证与权限

```python
# Sprint 2 已冻结 API
# 函数签名不可修改，只能新增调用

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 小时

# 角色权限映射（4 角色 × 20 权限）
ROLE_PERMISSION_MAP: dict[str, set[str]] = {
    "administrator": { ... },  # 20 权限
    "manager":       { ... },  # 14 权限
    "technician":    { ... },  # 6 权限
    "viewer":        { ... },  # 3 权限
}

def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希"""
    ...

def verify_password(plain: str, hashed: str) -> bool:
    """验证明文密码与哈希是否匹配"""
    ...

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """生成 JWT 访问令牌，payload: sub, username, role, iat, exp, type"""
    ...

def decode_access_token(token: str) -> dict:
    """解析 JWT 令牌，返回 payload"""
    ...

def has_permission(role: str, permission: str) -> bool:
    """检查角色是否拥有指定权限"""
    ...

def check_permission(user: User, permission: str) -> None:
    """检查用户权限，无权限则抛 PermissionDeniedException"""
    ...

def is_admin(user: User) -> bool:
    """检查用户是否为管理员"""
    ...

def is_manager(user: User) -> bool:
    """检查用户是否为经理"""
    ...

def is_technician(user: User) -> bool:
    """检查用户是否为技术员"""
    ...

def is_viewer(user: User) -> bool:
    """检查用户是否为观察者"""
    ...
```

#### 6.2.2 `dependencies.py` — 依赖注入

```python
# Sprint 2 已冻结 API
# 函数签名不可修改，只能新增调用

from fastapi import Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from server.core.security import decode_access_token
from server.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：获取数据库会话（try-yield-finally 模式）"""
    ...

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从 JWT 令牌解析当前用户，注入到路由处理函数"""
    ...

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户（已启用且未删除）"""
    ...

def get_optional_user(
    token: str | None = Depends(oauth2_scheme) or None,
    db: Session = Depends(get_db),
) -> User | None:
    """获取可选用户，Token 不存在时返回 None"""
    ...

def require_permission(permission: str):
    """工厂函数：生成指定权限的依赖检查器"""
    ...

def require_role(role: str):
    """工厂函数：生成指定角色的依赖检查器"""
    ...
```

#### 6.2.3 `exceptions.py` — 自定义异常

> Sprint 2 已冻结 | 异常类签名不可修改，只能新增调用

统一异常体系，所有业务异常继承自 `BaseAppException`。

**异常层次结构：**

```
BaseAppException (Exception)
├── BusinessLogicException      — 业务逻辑错误 (HTTP 400)
├── AuthenticationException     — 认证失败 (HTTP 401)
├── PermissionDeniedException   — 权限不足 (HTTP 403)
├── NotFoundException           — 资源不存在 (HTTP 404)
└── DuplicateException          — 重复数据 (HTTP 409)
```

**异常详情：**

| 异常类 | HTTP 状态码 | 默认 code | 默认 message | 说明 |
|--------|-------------|-----------|-------------|------|
| `BaseAppException` | — | — | — | 所有业务异常基类，提供 to_dict() 统一输出 |
| `BusinessLogicException` | 400 | BUSINESS_ERROR | Business logic error | 参数校验失败、业务规则不满足 |
| `AuthenticationException` | 401 | AUTHENTICATION_FAILED | Authentication failed | 登录失败、Token 无效 |
| `PermissionDeniedException` | 403 | PERMISSION_DENIED | Permission denied | 无权限访问资源 |
| `NotFoundException` | 404 | NOT_FOUND | Resource not found | 查询不到指定资源 |
| `DuplicateException` | 409 | DUPLICATE_DATA | Duplicate data | 唯一约束冲突 |

**to_dict() 输出格式：**

```json
{
    "code": "NOT_FOUND",
    "message": "用户不存在",
    "detail": {"user_id": 123}
}
```

**使用示例：**

```python
from server.core.exceptions import NotFoundException

raise NotFoundException("用户不存在", detail={"user_id": 123})
```

> 注意：所有异常类均为纯 Python Exception，不依赖 FastAPI / HTTPException。通过 `exception_handlers.py` 统一转换为 HTTP 响应。

#### 6.2.4 `exception_handlers.py` — 全局异常处理器

> Sprint 2 已冻结 | 函数签名不可修改，只能新增调用

将 Task 2.1 异常体系统一转换为 FastAPI JSON 响应。

```python
# Sprint 2 已冻结 API
# 仅允许导出: register_exception_handlers(app: FastAPI) -> None

from fastapi import FastAPI

def register_exception_handlers(app: FastAPI) -> None:
    """在 FastAPI 应用上注册所有全局异常处理器。

    注册顺序:
        1. BaseAppException 及其子类
        2. Starlette HTTPException
        3. RequestValidationError
        4. 未知 Exception（兜底）

    统一返回格式:
        {
            "code": <HTTP状态码>,
            "message": "<错误信息>",
            "detail": "<详细说明>"
        }
    """
    ...
```

**支持异常映射：**

| 异常类型 | HTTP 状态码 | message | detail |
|------|:--:|------|------|
| `BusinessLogicException` | 400 | 异常 message | 异常 detail |
| `AuthenticationException` | 401 | 异常 message | 异常 detail |
| `PermissionDeniedException` | 403 | 异常 message | 异常 detail |
| `NotFoundException` | 404 | 异常 message | 异常 detail |
| `DuplicateException` | 409 | 异常 message | 异常 detail |
| `HTTPException` | 原 status_code | 原 detail | 空字符串 |
| `RequestValidationError` | 422 | "请求参数错误" | FastAPI 默认错误 |
| `Exception` | 500 | "服务器内部错误" | "Internal Server Error" |

> 未知异常使用 `logger.exception()` 记录完整 stack trace，不暴露给客户端。

### 6.3 数据模型层 (models/)

#### 6.3.1 `base.py` — 基础模型与数据库会话

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 数据库连接由 server.config.settings 统一管理
from server.config import settings
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""
    pass

def get_db():
    """FastAPI 依赖：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 6.3.2 关键模型示例 — `trial_task.py`

```python
from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String, Text, Date, Enum as SAEnum, ForeignKey, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.models.base_model import BaseModel
from server.enums import (
    TrialTaskProcessStatus,
    TrialTaskResultStatus,
    DestinationType,
)

if TYPE_CHECKING:
    from server.models.user import User
    from server.models.customer import Customer


class TrialTask(BaseModel):
    """试磨任务模型 — GTMS 核心业务表"""

    __tablename__ = "trial_tasks"

    __table_args__ = (
        Index("ix_trial_tasks_customer_id", "customer_id"),
        Index("ix_trial_tasks_sales_id", "sales_id"),
        Index("ix_trial_tasks_process_status", "process_status"),
        Index("ix_trial_tasks_result_status", "result_status"),
        Index("ix_trial_tasks_created_at", "created_at"),
        Index("ix_trial_tasks_is_deleted", "is_deleted"),
    )

    # 业务字段
    task_no: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="任务编号"
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, comment="客户 ID"
    )
    requirement: Mapped[str] = mapped_column(Text, nullable=False, comment="加工要求")
    tracking_no: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, default=None, comment="快递单号"
    )
    sales_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, comment="销售 ID"
    )
    process_status: Mapped[TrialTaskProcessStatus] = mapped_column(
        SAEnum(TrialTaskProcessStatus), nullable=False,
        default=TrialTaskProcessStatus.CREATED, comment="流程状态"
    )
    result_status: Mapped[TrialTaskResultStatus] = mapped_column(
        SAEnum(TrialTaskResultStatus), nullable=False,
        default=TrialTaskResultStatus.PENDING, comment="结果状态"
    )
    destination: Mapped[Optional[DestinationType]] = mapped_column(
        SAEnum(DestinationType), nullable=True, default=None, comment="工件去向"
    )
    destination_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, default=None, comment="工件去向日期"
    )
    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None, comment="失败原因"
    )

    # 关联关系（已实现模型）
    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="tasks", lazy="selectin"
    )
    sales: Mapped["User"] = relationship(
        "User", foreign_keys=[sales_id], lazy="selectin"
    )

    # TODO: 待后续 Task 补充的关联关系
    # Task 1.6  (Receipt): receipt
    # Task 1.7  (GrindingRecord): grinding
    # Task 1.8  (InspectionRecord): inspection
    # Task 1.9  (Dispatch): dispatch
    # Task 1.10 (Attachment): attachments
```

### 6.3a 数据校验层 (schemas/) — 客户管理

> Sprint 4 已冻结 | 使用 Pydantic v2 ConfigDict(from_attributes=True)

#### 6.3a.1 `customer_schema.py` — 客户 Schema

```python
# 5 个 Schema 类，全部使用 Pydantic v2

class CustomerBase(BaseModel):
    """客户公共字段（company_name 必填，其余可选）"""
    company_name: str        # 必填，min_length=1, max_length=200
    contact_person: Optional[str]  # 联系人（映射 ORM contact 列）
    phone: Optional[str]
    email: Optional[str]     # 预留字段
    address: Optional[str]
    remark: Optional[str]    # 预留字段

class CustomerCreate(CustomerBase):
    """创建客户 — 继承 CustomerBase，company_name 必填"""
    pass

class CustomerUpdate(BaseModel):
    """更新客户 — 所有字段均为可选，仅更新传入的非 None 字段"""
    company_name: Optional[str]
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    remark: Optional[str]

class CustomerResponse(BaseModel):
    """客户响应 — 含 id、created_at、updated_at，不含 created_by/is_deleted"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_name: str
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

class CustomerListResponse(BaseModel):
    """客户列表响应 — 分页"""
    items: list[CustomerResponse]
    total: int
```

> 注意：email 和 remark 为预留字段（ORM 中暂无对应列），始终返回 None。

---

### 6.4 业务逻辑层 (services/)

#### 6.4.1 `task_service.py` — 试磨任务服务（核心）

```python
class TaskService:
    """试磨任务业务逻辑"""

    def __init__(self, db: Session):
        self.db = db

    def create_task(self, data: TaskCreateSchema, user_id: int) -> TrialTask:
        """创建试磨任务
        1. 生成任务编号 (YYYYMMDD-N)
        2. 校验客户是否存在
        3. 创建任务记录
        4. 写入操作日志
        5. 返回创建的任务
        """
        ...

    def update_task(self, task_id: int, data: TaskUpdateSchema, user_id: int) -> TrialTask:
        """更新任务
        1. 校验任务存在性
        2. 比对变更字段
        3. 更新记录
        4. 写入操作日志（记录变更内容）
        """
        ...

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """软删除任务"""
        ...

    def get_task_detail(self, task_id: int) -> dict:
        """获取任务完整详情（含关联的收件、试磨、检测、去向记录）"""
        ...

    def get_task_list(self, filters: dict) -> list:
        """分页查询任务列表，支持多条件筛选"""
        ...

    def get_tasks_by_process_status(self, status: TrialTaskProcessStatus) -> list:
        """按流程状态查询任务"""
        ...

    def get_dashboard_stats(self) -> dict:
        """获取仪表盘统计数据"""
        ...
```

#### 6.4.2 `notification_service.py` — 消息提醒服务

```python
class NotificationService:
    """消息提醒服务"""

    def __init__(self, db: Session):
        self.db = db

    def check_and_notify(self):
        """定时检查并生成提醒
        规则：
        - 已收件超过2天未试磨 → 提醒技术员
        - 试磨中超过5天未完成 → 提醒试磨责任人
        - 已完成但未上传检测报告 → 提醒技术员
        """
        ...

    def get_unread_notifications(self, user_id: int) -> list:
        """获取用户未读消息"""
        ...

    def mark_as_read(self, notification_id: int):
        """标记消息为已读"""
        ...
```

#### 6.4.3 `log_service.py` — 操作日志服务

```python
class LogService:
    """操作日志服务"""

    def __init__(self, db: Session):
        self.db = db

    def log_action(
        self,
        user_id: int,
        action: str,
        target_type: str,
        target_id: int,
        changes: dict = None,
        ip_address: str = None
    ):
        """记录操作日志
        每次修改任务自动记录：
        - 谁修改了 (user_id)
        - 修改时间 (created_at)
        - 修改内容 (changes JSON)
        """
        ...

    def get_logs(self, filters: dict) -> list:
        """查询日志（支持按用户、操作类型、时间范围筛选）"""
        ...
```

#### 6.4.4 `customer_service.py` — 客户服务

> Sprint 4 已冻结 | Customer 不提供删除功能。

```python
class CustomerService:
    """客户业务逻辑"""

    def list_customers(
        self, db, *,
        company_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> CustomerListResponse:
        """客户列表查询（分页 + 模糊搜索 + 排序）
        支持按 company_name 模糊搜索（LIKE %xxx%），按 company_name 升序排列。
        """
        ...

    def get_customer(self, db, customer_id: int) -> CustomerResponse:
        """根据 ID 查询客户（过滤 is_deleted=False）
        Raises: NotFoundException (客户不存在)
        """
        ...

    def create_customer(
        self, db, data: CustomerCreate, operator_id: int
    ) -> CustomerResponse:
        """创建客户
        流程:
          ① 自动 strip company_name
          ② 检查 company_name 全库唯一 → BusinessLogicException
          ③ 创建 Customer ORM
          ④ 提交事务
          ⑤ 写入 SystemLog（Customer Created）
        """
        ...

    def update_customer(
        self, db, customer_id: int,
        data: CustomerUpdate, operator_id: int,
    ) -> CustomerResponse:
        """更新客户（仅更新非 None 字段，exclude_unset）
        Raises: NotFoundException | BusinessLogicException
        """
        ...
```

**业务规则：**
- `company_name` 必填（Pydantic 校验）
- `company_name` 全库唯一（Create 和 Update 均检查，Update 排除自身）
- `company_name` 自动 strip() 去首尾空格
- 所有写操作记录 SystemLog
- 事务管理：commit 成功 / rollback 失败
- **不提供 delete_customer() 方法**

---

### 6.5 路由层 (routers/)

#### 6.5.1 标准CRUD路由示例 — `trial_task_router.py`

```python
from fastapi import APIRouter, Depends, Query
from server.schemas.trial_task_schema import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
)
from server.services.task_service import TaskService
from server.core.dependencies import get_current_user, get_db

router = APIRouter()

@router.post("/", response_model=TaskResponse)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """销售创建试磨任务"""
    service = TaskService(db)
    return service.create_task(data, user.id)

@router.get("/", response_model=TaskListResponse)
def list_tasks(
    status: str = Query(None),
    customer_id: int = Query(None),
    task_no: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    operator_id: int = Query(None),
    machine_type: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """多条件查询任务列表"""
    ...

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取任务详情"""
    ...

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, ...):
    """更新任务"""
    ...

@router.delete("/{task_id}")
def delete_task(task_id: int, ...):
    """删除任务"""
    ...
```

#### 6.5.2 `customer_router.py` — 客户路由

> Sprint 4 已冻结 | Customer 不提供 DELETE 接口。

```python
router = APIRouter(prefix="/api/customers", tags=["Customer"])

# GET /api/customers — 客户列表（分页+搜索）
@router.get("", response_model=CustomerListResponse)
def list_customers(
    company_name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("customer:view")),
) -> CustomerListResponse: ...

# GET /api/customers/{customer_id} — 客户详情
@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("customer:view")),
) -> CustomerResponse: ...

# POST /api/customers — 创建客户
@router.post("", response_model=CustomerResponse, status_code=201)
def create_customer(
    data: CustomerCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("customer:create")),
) -> CustomerResponse: ...

# PUT /api/customers/{customer_id} — 修改客户
@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    data: CustomerUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_permission("customer:edit")),
) -> CustomerResponse: ...
```

**权限映射：**
| 接口 | 权限码 |
|------|--------|
| GET /api/customers | `customer:view` |
| GET /api/customers/{id} | `customer:view` |
| POST /api/customers | `customer:create` |
| PUT /api/customers/{id} | `customer:edit` |

> 注意：不存在 `customer:delete` 权限，不提供 DELETE 接口。

**路由规范：**
- Router 不实现任何业务逻辑，全部委托给 CustomerService
- Router 不捕获业务异常，全部交由全局异常处理器统一处理
- Router 不使用 try/except、HTTPException、JWT、ORM

---

### 6.6 公共工具与业务规则模块 (utils/)

#### 6.6.1 `id_generator.py` — 任务编号生成器

> Sprint 2 已冻结 | 函数签名不可修改

```python
from datetime import date
from sqlalchemy.orm import Session

def generate_task_no(db: Session) -> str:
    """生成格式为 YYYYMMDD-N 的唯一任务编号（如 20260704-1）。
    每日流水号从 1 开始，数据库 LIKE 查询 + Python 侧解析序列号。
    内置 3 次重试机制应对并发唯一约束冲突。"""
    ...

#### 6.6.2 `file_handler.py` — 文件处理模块

> Sprint 2 已冻结 | 函数签名不可修改

```python
# 4 个冻结 API

from fastapi import UploadFile
from server.enums.file_type import FileType

def save_upload_file(
    file: UploadFile,
    task_no: str,
    file_type: FileType,
    upload_dir: str = "uploads",
) -> str:
    """保存上传文件到对应目录，返回文件路径。
    目录映射: IMAGE→images, VIDEO→videos, DOCUMENT→reports, CAD→files"""
    ...

def delete_file(file_path: str) -> bool:
    """删除指定文件，返回是否成功"""
    ...

def validate_file(file: UploadFile, file_type: FileType) -> None:
    """校验文件扩展名、大小、MIME 类型"""
    ...

def generate_filename(
    task_no: str,
    file_type: FileType,
    original_filename: str,
) -> str:
    """生成文件名: {task_no}_{file_type}_{YYYYMMDDHHMMSS}_{uuid}.{ext}"""
    ...
```

**文件命名规则：** `{task_no}_{file_type}_{YYYYMMDDHHMMSS}_{uuid}.{ext}`

**目录映射：**

| FileType | 目录 |
|------|------|
| `IMAGE` | `uploads/images/` |
| `VIDEO` | `uploads/videos/` |
| `DOCUMENT` | `uploads/reports/` |
| `CAD` | `uploads/files/` |

**校验规则：**

| 项目 | 限制 |
|------|------|
| 扩展名白名单 | IMAGE: jpg/jpeg/png/bmp/gif; VIDEO: mp4/avi/mov; DOCUMENT: pdf/doc/docx/xls/xlsx; CAD: dwg/dxf/stp/step |
| 大小限制 | IMAGE: 20MB; VIDEO: 200MB; DOCUMENT: 50MB; CAD: 100MB |
| MIME 校验 | 基于扩展名映射验证 |

#### 6.6.3 `task_permission.py` — 阶段负责人规则

GTMS 采用"阶段负责人（Stage Owner）"机制，而不是固定责任人。

不同业务阶段允许由不同技术员完成，每个阶段均记录实际操作人。

##### Stage Owner

| 阶段 | 实际记录方式 | 说明 |
|------|-------------|------|
| 收件登记 | Receipt.created_by | 收件登记实际操作人 |
| 开始试磨 | GrindingRecord.operator_id | 点击"开始试磨"时自动确定试磨负责人 |
| 完成试磨 | GrindingRecord.operator_id | 与开始试磨责任人保持一致 |
| 上传检测报告 | InspectionRecord.created_by | 上传检测报告实际操作人 |
| 工件去向 | Dispatch.created_by | 填写工件去向实际操作人 |

##### Permission Rule

| 操作 | 可执行人员 |
|------|-----------|
| 收件登记 | 任意具有 Receipt 权限的技术员 |
| 开始试磨 | 任意具有 Grinding 权限的技术员 |
| 完成试磨 | GrindingRecord.operator_id 或 Administrator |
| 上传检测报告 | 任意具有 Inspection 权限的技术员 |
| 填写工件去向 | 任意具有 Dispatch 权限的技术员 |
| 管理员 | 拥有全部阶段权限 |

##### Business Rules

1. 收件登记人员无需成为试磨负责人。
2. 点击"开始试磨"时，系统自动将当前登录技术员写入 `GrindingRecord.operator_id`。
3. `GrindingRecord.operator_id` 在试磨结束前不得修改。
4. 完成试磨仅允许 `GrindingRecord.operator_id` 或 Administrator 执行。
5. 检测与工件去向允许其他具有对应权限的技术员执行。
6. 每个阶段均记录实际操作人，用于日志、统计、审计和消息提醒。
7. 本规则不修改 Sprint 1 已完成 ORM 设计，阶段操作人均使用现有 ORM 字段记录。

##### Notification Rule

| 场景 | 通知对象 |
|------|----------|
| Receipt Delay（收件后超时未开始试磨） | 所有具有 Grinding 权限的技术员、任务创建销售（created_by）、Administrator |
| Grinding Delay（试磨超时未完成） | GrindingRecord.operator_id、任务创建销售（created_by）、Administrator |
| Inspection Delay（待检测超时） | 所有具有 Inspection 权限的技术员、任务创建销售（created_by）、Administrator |

##### Design Notes

- `GrindingRecord.operator_id` 是试磨负责人唯一标识。
- 收件人员、检测人员、去向人员均不是试磨负责人。
- 所有阶段均记录实际操作人，用于操作日志、统计分析和责任追踪。
- 本规范为 GTMS 全局业务规则，TaskService、ReceiptService、GrindingService、InspectionService、DispatchService、NotificationService 均应遵循本规则。

---

### 6.7 中间件模块 (middleware/)

> Sprint 2 已冻结 | 函数签名不可修改，只能新增调用

#### 6.7.1 `cors_middleware.py` — CORS 跨域中间件

```python
# Sprint 2 已冻结 API

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI) -> None:
    """配置 FastAPI CORS 中间件。

    allow_origins: localhost, 127.0.0.1, Vue Dev Server, 微信开发者工具, 预留生产域名
    allow_methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
    allow_headers: Authorization, Content-Type, Accept, Origin, X-Requested-With
    allow_credentials: True
    expose_headers: Authorization
    max_age: 600
    """
    ...
```

#### 6.7.2 `log_middleware.py` — 请求日志中间件

```python
# Sprint 2 已冻结 API

from fastapi import FastAPI

def setup_request_logging(app: FastAPI) -> None:
    """注册请求日志中间件。

    使用 @app.middleware("http") 模式。
    每次请求自动生成 UUID 写入 request.state 和 X-Request-ID 响应头。
    使用 Python logging，logger 名称 "gtms"，INFO 级别。
    记录: 请求时间、耗时、method、path、status、IP、user-agent。
    异常: 记录 ERROR 级别及 stack trace，不吞异常。
    """
    ...
```

## 7. 桌面客户端模块详解（client/）

### 7.1 入口文件 `main.py`

```python
import sys
from PySide6.QtWidgets import QApplication
from client.views.login_view import LoginView
from client.config import APP_CONFIG

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GTMS - 磨床试磨管理系统")

    # 启动登录界面
    login = LoginView()
    if login.exec() == QDialog.Accepted:
        # 登录成功，进入主窗口
        window = MainWindow(user=login.get_user())
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### 7.2 界面模块 (views/)

#### 7.2.1 各界面职责

| 文件 | 类名 | 职责 |
|------|------|------|
| `login_view.py` | `LoginView` | 用户登录对话框，验证账号密码 |
| `main_window.py` | `MainWindow` | 主窗口框架，含侧边栏导航、顶部工具栏 |
| `dashboard_view.py` | `DashboardView` | 首页仪表盘：今日任务数、完成率、消息提醒列表 |
| `customer_view.py` | `CustomerView` | 客户新增、修改、查询、列表展示 |
| `trial_task_view.py` | `TrialTaskView` | 试磨任务创建/编辑/详情，含状态流转按钮 |
| `receipt_view.py` | `ReceiptView` | 收件登记：日期、图片上传 |
| `grinding_view.py` | `GrindingView` | 试磨表单：责任人、机型、砂轮、参数、图片 |
| `inspection_view.py` | `InspectionView` | 检测报告上传、精度/粗糙度填写 |
| `dispatch_view.py` | `DispatchView` | 工件去向登记 |
| `query_view.py` | `QueryView` | 多条件查询、统计图表 |
| `user_manage_view.py` | `UserManageView` | 用户管理（仅管理员可见） |
| `system_log_view.py` | `SystemLogView` | 操作日志查看 |
| `settings_view.py` | `SettingsView` | 系统设置 |

#### 7.2.2 界面设计原则

- 每个界面对应一个独立的 `.py` 文件
- 界面只负责：布局、数据绑定、事件绑定
- **不允许在界面代码中写业务逻辑**
- 所有数据操作通过 `client/services/` 调用 API

#### 7.2.3 `customer_view.py` — 客户管理页面

> Sprint 4 已冻结 | 不提供删除功能。

```python
class CustomerView(QWidget):
    """客户管理页面 — 分页 + 搜索 + 新增/编辑"""

    customer_changed = Signal()  # 客户信息变更信号

    def __init__(self, customer_service: CustomerService, parent=None):
        ...

    def refresh(self) -> None:
        """刷新客户列表，从服务器重新加载数据"""
        ...

    # 工具栏：新增客户、编辑客户、刷新、搜索
    # 表格：NoEditTriggers, SingleSelection, AlternatingRowColors, Stretch
    # 分页：第一页、上一页、下一页、最后一页
    # 搜索：按 company_name 模糊搜索
```

**UI 特性：**
- 表格：不可编辑（NoEditTriggers）、单选（SingleSelection）、交替行颜色（AlternatingRowColors）、自适应列宽（Stretch）
- 分页：第一页 / 上一页 / 下一页 / 最后一页，显示"第 X / Y 页 共 Z 条记录"
- 搜索：按公司名称模糊搜索，搜索后重置到第一页
- 工具栏：新增客户、编辑客户、刷新、搜索框
- **无删除按钮**

#### 7.2.4 `customer_edit_dialog.py` — 客户编辑对话框

> Sprint 4 已冻结 | 支持新增和编辑两种模式。

```python
class CustomerEditDialog(QDialog):
    """客户新增/编辑对话框"""

    def __init__(
        self,
        customer_service: CustomerService,
        mode: str = "create",          # "create" 或 "edit"
        customer_id: int | None = None, # 编辑模式下的客户 ID
        customer_data: dict | None = None,  # 编辑模式下的预填数据
        parent=None,
    ):
        ...

    def get_result(self) -> dict | None:
        """获取操作结果，None 表示取消"""
        ...
```

**表单字段：**
- 公司名称（必填）
- 联系人（可选）
- 电话（可选）
- 邮箱（可选）
- 地址（可选）
- 备注（可选）

**模式说明：**
- 新增模式：空白表单，提交后调用 `CustomerService.create_customer()`
- 编辑模式：预填已有数据，提交后调用 `CustomerService.update_customer()`
- 客户端不校验数据合法性，全部由 Server CustomerService 负责

---

### 7.3 服务层 (services/)

#### 7.3.1 `api_client.py` — HTTP 请求封装

```python
import httpx

class ApiClient:
    """统一的 HTTP 客户端封装"""

    BASE_URL = "http://localhost:8000/api"

    def __init__(self):
        self.client = httpx.Client(timeout=30)
        self.token = None

    def set_token(self, token: str):
        """设置 JWT 认证令牌"""
        self.token = token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def get(self, path: str, params: dict = None) -> dict:
        """GET 请求"""
        ...

    def post(self, path: str, data: dict = None, files: dict = None) -> dict:
        """POST 请求（支持文件上传）"""
        ...

    def put(self, path: str, data: dict = None) -> dict:
        """PUT 请求"""
        ...

    def delete(self, path: str) -> dict:
        """DELETE 请求"""
        ...
```

#### 7.3.2 `customer_service.py` — 桌面端客户服务

> Sprint 4 已冻结 | 仅负责 HTTP 封装，不实现业务逻辑。

```python
class CustomerService:
    """桌面端客户管理 HTTP 请求封装"""

    def __init__(self, api_client: ApiClient):
        """存储 ApiClient 引用"""
        ...

    def list_customers(
        self,
        company_name: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """GET /api/customers — 客户列表（分页+搜索）"""
        ...

    def get_customer(self, customer_id: int) -> dict[str, Any]:
        """GET /api/customers/{customer_id} — 客户详情"""
        ...

    def create_customer(
        self,
        company_name: str,
        contact_person: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """POST /api/customers — 创建客户"""
        ...

    def update_customer(
        self,
        customer_id: int,
        company_name: str | None = None,
        contact_person: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """PUT /api/customers/{customer_id} — 修改客户（仅提交非 None 字段）"""
        ...
```

**职责界定：**
- 仅封装 HTTP 请求（URL、Query、Body）
- 将服务器返回的 JSON 原样返回
- 将服务器异常原样抛出
- 不实现任何业务规则、数据校验、缓存

---

### 7.4 可复用组件 (widgets/)

| 文件 | 类名 | 说明 |
|------|------|------|
| `status_badge.py` | `StatusBadge` | 状态标签，不同状态显示不同颜色 |
| `image_viewer.py` | `ImageViewer` | 图片预览弹窗，支持缩放 |
| `file_uploader.py` | `FileUploader` | 拖拽上传组件，支持多文件、类型过滤 |
| `search_bar.py` | `SearchBar` | 通用搜索栏，含关键词、日期范围、状态下拉 |

---

## 8. 小程序模块详解（miniapp/）

### 8.1 UniApp 页面结构

| 页面路径 | 功能 | 对应角色 |
|------|------|------|
| `pages/login/index` | 登录页，输入账号密码 | 所有用户 |
| `pages/dashboard/index` | 首页仪表盘，今日统计 + 消息提醒 | 所有用户 |
| `pages/task_list/index` | 任务列表，支持筛选 | 所有用户 |
| `pages/task_detail/index` | 任务详情，各阶段数据展示 | 所有用户 |
| `pages/receipt/index` | 收件登记（拍照上传） | 技术员 |
| `pages/statistics/index` | 统计报表 | 领导 |
| `pages/notification/index` | 消息通知列表 | 所有用户 |

### 8.2 小程序特色功能

- 拍照上传：利用微信原生相机，拍照后直接上传到服务器
- 消息推送：通过微信订阅消息，提醒技术员及时处理
- 扫码查询：扫描任务二维码，快速查看任务详情

---

## 9. API 接口文档

### 9.1 认证模块

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login` | 用户登录，返回 JWT Token | 公开 |
| GET | `/api/auth/me` | 获取当前用户信息 | 登录用户 |
| POST | `/api/auth/change-password` | 修改密码 | 登录用户 |

### 9.2 客户管理

> Sprint 4 已冻结 | Customer 永久保留，不提供删除功能。

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/customers` | 客户列表（分页+搜索） | customer:view |
| POST | `/api/customers` | 新增客户 | customer:create |
| GET | `/api/customers/{id}` | 客户详情 | customer:view |
| PUT | `/api/customers/{id}` | 更新客户 | customer:edit |

### 9.3 试磨任务

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/tasks` | 任务列表（多条件筛选） | 登录用户 |
| POST | `/api/tasks` | 创建任务 | 销售 |
| GET | `/api/tasks/{id}` | 任务详情（含关联数据） | 登录用户 |
| PUT | `/api/tasks/{id}` | 更新任务 | 销售 |
| DELETE | `/api/tasks/{id}` | 删除任务 | 管理员 |
| PUT | `/api/tasks/{id}/status` | 更新任务状态 | 对应角色 |

### 9.4 收件管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/receipts` | 创建收件记录（含图片上传） | 技术员 |
| GET | `/api/receipts/{task_id}` | 获取收件记录 | 登录用户 |

### 9.5 试磨管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/grinding` | 创建试磨记录 | 技术员 |
| PUT | `/api/grinding/{id}` | 更新试磨记录 | 技术员 |
| GET | `/api/grinding/{task_id}` | 获取试磨记录 | 登录用户 |

### 9.6 检测管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/inspections` | 上传检测报告 + 填写数据 | 技术员 |
| GET | `/api/inspections/{task_id}` | 获取检测记录 | 登录用户 |

### 9.7 工件去向

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/dispatches` | 填写工件去向 | 技术员 |
| GET | `/api/dispatches/{task_id}` | 获取去向记录 | 登录用户 |

### 9.8 查询统计

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/query/statistics` | 综合统计（本月/年度/成功率/排行） | 登录用户 |
| GET | `/api/query/dashboard` | 仪表盘数据 | 登录用户 |

### 9.9 文件上传

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/upload/image` | 上传图片 | 登录用户 |
| POST | `/api/upload/report` | 上传检测报告 | 技术员 |
| POST | `/api/upload/cad` | 上传 CAD 文件 | 技术员 |
| GET | `/api/upload/{file_path}` | 下载文件 | 登录用户 |

### 9.10 操作日志

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/logs` | 查询操作日志 | 管理员 / 领导 |

### 9.11 消息提醒

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/notifications` | 获取未读消息 | 登录用户 |
| PUT | `/api/notifications/{id}/read` | 标记已读 | 登录用户 |

---

## 10. 状态流转机制

### 10.1 流程状态流转图（process_status）

```
created → received → grinding → dispatched → closed
 灰色      蓝色       橙色       紫色       深灰

created:  销售创建任务 → 已创建
received: 技术员收件登记 → 已收件
grinding: 技术员开始试磨 → 试磨中
dispatched: 技术员填写工件去向 → 已寄回
closed: 管理员归档 → 已关闭（终态）

规则：严格单向，禁止跳级，禁止逆向
```

### 10.2 结果状态流转图（result_status）

```
pending → passed（检测合格，终态）
pending → failed（检测不合格，终态）
 灰色       绿色               红色

规则：不可逆，passed/failed 不可互转
```

### 10.3 状态流转约束

| 当前状态 | 允许的下一状态 | 操作角色 |
|------|------|------|
| created | received | 技术员 |
| received | grinding | 技术员 |
| grinding | dispatched | 技术员 |
| dispatched | closed | 管理员 |
| pending | passed | 技术员 |
| pending | failed | 技术员 |

### 10.4 消息提醒触发规则

| 条件 | 提醒类型 | 触发时机 | 目标用户 |
|------|------|------|------|
| process_status=received 超过 48h | receipt_delay | 定时检查 | 技术员 |
| process_status=grinding 超过 120h | grinding_delay | 定时检查 | 试磨责任人 |
| process_status=grinding 且 result_status=pending 超过 72h | report_missing | 定时检查 | 技术员 |

---

## 11. 关键类与函数说明

### 11.1 后端核心类

| 类名 | 文件 | 职责 |
|------|------|------|
| `SecurityManager` | `server/core/security.py` | 密码哈希、JWT 生成与验证 |
| `PermissionChecker` | `server/core/security.py` | 角色-权限校验 |
| `TaskService` | `server/services/task_service.py` | 试磨任务核心业务逻辑 |
| `NotificationService` | `server/services/notification_service.py` | 消息提醒生成与推送 |
| `LogService` | `server/services/log_service.py` | 操作日志记录与查询 |
| `TaskNumberGenerator` | `server/utils/id_generator.py` | 任务编号自动生成 |
| `AutoBackup` | `server/utils/backup.py` | 数据库定时自动备份 |
| `FileHandler` | `server/utils/file_handler.py` | 文件上传校验、存储、路径管理 |

### 11.2 客户端核心类

| 类名 | 文件 | 职责 |
|------|------|------|
| `ApiClient` | `client/services/api_client.py` | HTTP 请求统一封装 |
| `MainWindow` | `client/views/main_window.py` | 主窗口导航框架 |
| `DashboardView` | `client/views/dashboard_view.py` | 首页仪表盘 + 消息提醒 |
| `TrialTaskView` | `client/views/trial_task_view.py` | 任务创建/编辑/详情 |
| `QueryView` | `client/views/query_view.py` | 多条件查询 + 统计图表 |
| `StatusBadge` | `client/widgets/status_badge.py` | 状态彩色标签 |
| `FileUploader` | `client/widgets/file_uploader.py` | 拖拽文件上传组件 |

### 11.3 关键函数说明

#### `TaskService.create_task()`
```
输入: TaskCreateSchema (customer_id, requirement, tracking_no), user_id
输出: TrialTask 对象
流程:
  1. 调用 TaskNumberGenerator.generate() 生成编号
  2. 校验客户是否存在
  3. 创建 TrialTask 记录，process_status=created, result_status=pending
  4. 调用 LogService.log_action() 记录操作
  5. 返回创建的任务
```

#### `TaskService.update_task_status()`
```
输入: task_id, new_status, user_id, extra_data
输出: 更新后的 TrialTask
流程:
  1. 校验任务存在性
  2. 校验状态流转合法性（当前状态→目标状态）
  3. 校验用户权限（不同状态对应不同角色）
  4. 根据状态创建/更新关联记录
  5. 更新任务状态
  6. 记录操作日志
```

#### `NotificationService.check_and_notify()`
```
流程:
  1. 查询所有 process_status=received 且超过48h未转入 grinding 的任务
  2. 查询所有 process_status=grinding 且超过120h未完成的任务
  3. 查询所有 process_status=grinding 且 result_status=pending 且超过72h未上传报告的任务
  4. 为每个符合条件的任务生成 Notification 记录
  5. 避免重复提醒（已存在未读提醒则跳过）
```

---

## 12. 附件管理规范

### 12.1 文件类型与存储路径

| 文件类型 | 允许扩展名 | 存储路径 | 最大大小 |
|------|------|------|------|
| 图片 | `.jpg` `.jpeg` `.png` | `uploads/images/` | 10 MB |
| 文档 | `.pdf` `.docx` `.xlsx` | `uploads/reports/` | 50 MB |
| CAD | `.dwg` `.dxf` | `uploads/cad/` | 50 MB |
| 视频 | `.mp4` | `uploads/videos/` | 200 MB |

### 12.2 文件命名规则

```
{task_no}_{file_type}_{timestamp}.{ext}

示例: 20260701-1_receipt_20260702_143025.jpg
```

### 12.3 文件处理流程

1. 客户端上传文件 → 校验类型和大小
2. 服务端二次校验 → 生成唯一文件名
3. 存储到对应目录 → 写入 `attachments` 表
4. 返回可访问的 URL 路径

---

## 13. 权限模型

### 13.1 RBAC 架构

用户 → 用户-角色关联 → 角色 → 角色-权限关联 → 权限

### 13.2 预设角色

| 角色 | 标识 | 拥有权限数 | 说明 |
|------|------|:--:|------|
| 管理员 | admin | 全部 | 所有权限 |
| 销售 | sales | 9 | 任务+客户+查看 |
| 技术员 | technician | 9 | 操作类权限 |
| 领导 | leader | 5 | 查看类权限 |

### 13.3 权限清单（19项）

| 权限码 | 名称 | 模块 |
|------|------|------|
| task:create | 创建任务 | task |
| task:view | 查看任务 | task |
| task:edit | 编辑任务 | task |
| task:delete | 删除任务 | task |
| customer:create | 创建客户 | customer |
| customer:view | 查看客户 | customer |
| customer:edit | 编辑客户 | customer |
| receipt:create | 收件登记 | receipt |
| grinding:start | 开始试磨 | grinding |
| grinding:complete | 完成试磨 | grinding |
| inspection:upload | 上传报告 | inspection |
| dispatch:create | 填写去向 | dispatch |
| report:view | 查看报告 | report |
| user:manage | 用户管理 | user |
| system:manage | 系统设置 | system |
| log:view | 查看日志 | log |
| statistics:view | 查看统计 | statistics |
| dashboard:view | 查看仪表盘 | dashboard |
| attachment:upload | 上传附件 | attachment |

### 13.4 权限校验流程

请求 → JWT 解析 → 提取 user_id + permissions 列表
    → 路由装饰器 require_permission("task:create")
    → 比对 permissions 列表
    → 通过 → 执行 / 不通过 → 403

---

## 14. 项目运行方式

### 14.1 环境要求

- Python 3.13
- Node.js 18+ (小程序开发)
- MySQL 8.0 (正式环境)

### 14.2 后端启动

```bash
# 1. 克隆项目
cd GrindingTrialSystem

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
python database/seed_data.py

# 5. 启动后端服务
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

# 访问 API 文档: http://localhost:8000/docs
```

### 14.3 桌面客户端启动

```bash
# 在虚拟环境中
python client/main.py
```

### 14.4 桌面客户端打包

```bash
pyinstaller --onefile --windowed --name GTMS client/main.py
```

### 14.5 微信小程序启动

```bash
cd miniapp
npm install
# 使用 HBuilderX 或微信开发者工具打开项目
```

### 14.6 切换到 MySQL 正式环境

修改 `server/models/base.py` 中的 `DATABASE_URL`：

```python
DATABASE_URL = "mysql+pymysql://用户名:密码@localhost:3306/gtms"
```

然后运行数据库迁移：

```bash
alembic upgrade head
```

---

## 15. 开发规范

### 15.1 代码规范

- 遵守 **PEP8** 标准
- 使用 **Black** 或 **ruff** 进行代码格式化
- 类名：大驼峰 (`TaskService`)
- 函数名：小写下划线 (`create_task`)
- 常量：大写下划线 (`MAX_FILE_SIZE`)

### 15.2 模块化规范

- 每个模块单独维护，一个文件一个职责
- **业务代码不允许写在界面层**（views 只做 UI）
- 所有数据库操作通过 ORM 模型统一封装
- 所有上传文件统一管理到 `uploads/` 目录

### 15.3 Git 提交规范

```
feat: 新功能
fix: 修复 Bug
docs: 文档更新
refactor: 重构
test: 测试
chore: 构建/工具
```

### 15.4 安全规范

- 密码使用 bcrypt 哈希存储
- 使用 JWT 进行无状态认证
- 文件上传校验类型和大小
- API 接口做权限校验
- 生产环境修改 `SECRET_KEY`

### 15.5 View 层开发规范 (View Layer Development Standard)

> **自 Sprint 5 起生效。所有 View (QWidget/QMainWindow) 统一遵循以下规范。**

#### 15.5.1 单一职责 (Single Responsibility)

View 仅负责：
- UI 展示
- 用户交互
- Signal 连接
- Widget 组合
- 页面刷新

View 不得负责：
- 业务规则
- 权限判断
- 数据库操作
- HTTP 请求
- JWT 认证
- ORM 操作
- 编号生成
- 状态流转
- 日志写入

#### 15.5.2 数据来源 (Data Source)

View 只能调用 **Desktop Service** 获取数据。

禁止直接调用：
- `ApiClient`
- `requests`
- Server Service
- Router
- ORM
- Database

#### 15.5.3 业务规则 (Business Rule)

全部业务规则统一由 **Server Service** 实现。View 不得重复实现任何业务规则，包括：
- 唯一性判断
- 状态流转
- 权限校验
- 编号生成
- 数据校验

#### 15.5.4 Widget 复用 (Widget Reuse)

View 必须优先复用 **Widget Layer**，不得重复实现公共组件，包括：
- `SearchBar`
- `StatusBadge`
- `Pagination`
- `ImagePreview`
- `Timeline`

#### 15.5.5 布局标准 (Layout Standard)

推荐统一布局（自上而下）：

```
Toolbar
  ↓
Search Area
  ↓
Data Table
  ↓
Pagination
  ↓
Status Bar
```

所有 CRUD 页面保持统一风格。

#### 15.5.6 Signal 通信 (Signal Communication)

View 通过 **Signal / Slot** 完成交互。Widget 不得直接调用 View 或 Service。

#### 15.5.7 异常处理 (Exception Handling)

View 仅负责通过 `QMessageBox` 显示错误信息。不得：
- 包装异常
- 吞异常
- 修改异常类型

#### 15.5.8 日志 (Logging)

统一使用 `logging.getLogger("gtms.client")`。禁止使用 `print()`。

#### 15.5.9 依赖规则 (Dependency Rule)

| 允许 | 禁止 |
|------|------|
| `Qt (PySide6)` | `Server` 模块 |
| `Desktop Service` | `ORM` |
| `Widget` | `Database` |
| `logging` | `Router` |
| `typing` | `JWT` |
| | `requests` |

#### 15.5.10 公开 API 冻结 (Public API Freeze)

View 公开 API 一旦完成 Mini Freeze，不得修改：
- 函数签名
- Signal
- 公开 Property

仅允许新增私有函数。

#### 15.5.11 代码风格 (Code Style)

- PEP8
- Google Docstring
- Type Hint
- 无 TODO
- 无 FIXME
- 无 `pass`
- 无循环导入

#### 15.5.12 测试 (Testing)

所有 View 必须覆盖：
- `py_compile`
- `import`
- 公开 API
- Signal
- 刷新流程
- 异常处理
- Widget 集成
- 无业务逻辑
- Frozen API
- PEP8

#### 15.5.13 分层依赖 (Layer Dependency)

GTMS 统一架构（自上而下）：

```
Server
  ↓
Desktop Service
  ↓
Widget
  ↓
View
  ↓
MainWindow
```

任何层不得跨层访问。

#### 15.5.14 冻结流程 (Freeze Process)

View 完成开发后必须执行：
1. **Mini Freeze Review** — 单 View 审查
2. **View Baseline Freeze Review** — 全部 View 基线审查
3. **Sprint Baseline Freeze Review** — Sprint 整体审查

#### 15.5.15 适用范围

本规范适用于以下及未来所有 View：
- `TrialTaskView`
- `CustomerView`
- `UserManageView`
- `ReceiptView`
- `GrindingView`
- `InspectionView`
- `DispatchView`
- `Dashboard`
- `Statistics`
- `LogView`

### 15.6 UI 组件开发规范 (UI Component Development Standard)

> **自 Sprint 5 起生效。所有 Widget (Qt UI 组件) 统一遵循以下规范。**
>
> 适用于：`StatusBadge`、`SearchBar`、`Pagination`、`ImagePreview`、`Timeline`、`AttachmentList`、`StatisticsCard`、`DashboardCard`、`EmptyState`、`LoadingOverlay` 以及未来所有公共 Widget。

#### 15.6.1 设计目标 (Design Goal)

Widget 必须：可复用、独立、轻量、Pure UI。不得绑定任何具体业务页面。

#### 15.6.2 单一职责 (Single Responsibility)

Widget 仅负责：
- UI 展示
- 用户输入
- 状态显示
- Signal 发射
- 简单 UI 状态维护

Widget 不得负责：
- 业务规则
- 数据库操作
- HTTP 请求
- JWT 认证
- 权限校验
- 编号生成
- 状态流转
- ORM 操作
- Server 调用

#### 15.6.3 依赖规则 (Dependency Rule)

| 允许 | 禁止 |
|------|------|
| `Qt (PySide6)` | `Desktop Service` |
| `typing` | `ApiClient` |
| `logging` | `Server` 模块 |
| 标准库 | `Router` |
| | `ORM` |
| | `Database` |
| | `requests` |
| | `JWT` |
| | `bcrypt` |
| | 任何业务模块 |

#### 15.6.4 公开 API 设计 (Public API Design)

公开 API 应保持简单、稳定、一致。公开成员仅允许：
- `__init__()`
- 公开方法
- 公开 Property
- 公开 Signal

不得暴露内部状态、内部实现细节、私有成员。

#### 15.6.5 Signal 标准 (Signal Standard)

Signal 统一命名规范：
- `xxx_requested` — 请求类（如 `search_requested`）
- `xxx_changed` — 变更类（如 `customer_changed`）
- `xxx_selected` — 选中类
- `xxx_clicked` — 点击类
- `xxx_finished` — 完成类

Signal 仅负责通知，不得直接调用 View、Desktop Service、Server。

#### 15.6.6 事件处理 (Event Handling)

Widget 仅处理：用户输入、按钮点击、键盘事件、焦点事件、UI 更新。不得执行业务流程。

#### 15.6.7 样式标准 (Style Standard)

统一使用 **Qt StyleSheet** 实现外观。颜色、字体、圆角、边框统一集中管理。除特殊情况外，禁止：
- `paintEvent()`
- `QPainter`
- 自绘控件

#### 15.6.8 布局标准 (Layout Standard)

Widget 内部布局使用 `QHBoxLayout` / `QVBoxLayout` / `QGridLayout`。保持结构清晰、Margin 合理、Spacing 合理。禁止绝对坐标布局。

#### 15.6.9 可配置性 (Configuration)

Widget 支持动态配置，例如：Placeholder、标题、按钮文字、颜色、图标、尺寸等。不得硬编码业务文本。

#### 15.6.10 日志 (Logging)

统一使用 `logging.getLogger("gtms.client")`。禁止 `print()`。

#### 15.6.11 异常处理 (Exception Handling)

Widget 不处理业务异常。允许参数校验（`ValueError`、`TypeError`）。不得使用 `QMessageBox`、`HTTPException`、`BusinessLogicException`、`NotFoundException` 等业务异常。

#### 15.6.12 Widget 通信 (Widget Communication)

Widget 之间通过 **Signal / Slot** 通信。不得直接引用其它 Widget、View、Desktop Service。

#### 15.6.13 可复用性 (Reusability)

任何 Widget 不得绑定 TrialTask、Customer、User、Receipt、Grinding、Inspection、Dispatch 等业务对象。必须保持业务无关。

#### 15.6.14 可访问性 (Accessibility)

Widget 应支持：
- `ObjectName`
- `ToolTip`
- `Placeholder`
- Keyboard Focus
- 快捷键（如适用）

便于自动化测试、可访问性、国际化。

#### 15.6.15 命名规范 (Naming Convention)

| 类别 | 规范 | 示例 |
|------|------|------|
| 文件名 | `snake_case` | `status_badge.py`、`search_bar.py`、`pagination.py` |
| 类名 | `PascalCase` | `StatusBadge`、`SearchBar`、`Pagination` |
| 私有成员 | 下划线开头 | `_status`、`_search_input` |

#### 15.6.16 代码风格 (Code Style)

- PEP8
- Google Docstring
- Type Hint
- UTF-8
- LF 换行
- 禁止：TODO、FIXME、`pass`、循环导入

#### 15.6.17 测试要求 (Testing Requirement)

所有 Widget 必须覆盖：
- `py_compile`
- `import`
- 公开 API
- Signal
- Property
- 参数更新
- 异常
- PEP8
- Type Hint
- Docstring
- 无循环导入
- Frozen API

测试全部 PASS。

#### 15.6.18 公开 API 冻结 (Public API Freeze)

Widget 完成 Mini Freeze 后公开 API 冻结。禁止修改公开方法、Signal、Property、函数签名。允许新增私有函数、新增内部实现、Bug Fix。不得影响外部调用。

#### 15.6.19 分层位置 (Layer Position)

GTMS 统一分层：

```
Server
  ↓
Desktop Service
  ↓
Widget          ← 当前层
  ↓
View
  ↓
MainWindow
```

Widget 只能位于 Desktop Service 与 View 之间，不得跨层访问。

#### 15.6.20 适用范围 (Applicable Scope)

本规范适用于：
- `StatusBadge`
- `SearchBar`
- `Pagination`
- `ImagePreview`
- `AttachmentList`
- `Timeline`
- `StatisticsCard`
- `DashboardCard`
- `EmptyState`
- `LoadingOverlay`
- 以及未来所有公共 Widget

#### 15.6.21 冻结流程

Widget 开发完成后必须执行：
1. **Mini Freeze Review** — 单 Widget 审查
2. **Widget Baseline Freeze Review** — 全部 Widget 基线审查

之后方可进入 View 开发。如需新增规则，应统一更新本文档，对所有 Widget 保持一致。

#### 15.6.22 Standard Upload Widget Principle

1. 所有文件上传页面必须复用 FileUploader。
2. View 不得直接调用 QFileDialog。
3. View 不得自行实现上传按钮。
4. 上传相关 UI 统一由 FileUploader 提供。
5. 后续所有上传场景（Receipt、Grinding、Inspection、Report、Attachment 等）必须复用该组件。

### 15.7 CRUD 页面开发规范 (CRUD View Development Standard)

> **自 Sprint 5 起生效。所有 CRUD 页面统一遵循本规范。**
>
> 适用于：`UserManageView`、`CustomerView`、`TrialTaskView`、`ReceiptView`、`GrindingView`、`InspectionView`、`DispatchView`、`ReportView`、`LogView`、`StatisticsView` 以及未来所有 CRUD 页面。

#### 15.7.1 设计目标 (Design Goal)

CRUD 页面必须：统一布局、统一交互、统一数据刷新流程、统一权限控制、统一分页方式、统一搜索方式、统一异常处理。保持可维护、可扩展。

#### 15.7.2 单一职责 (Single Responsibility)

View 仅负责：
- 页面展示
- 事件响应
- 调用 Desktop Service
- 刷新 UI
- Signal 通信

View 不得负责：
- 业务规则
- 数据库操作
- HTTP 请求
- JWT 认证
- ORM 操作
- 编号生成
- 状态流转
- 权限计算
- 数据校验

#### 15.7.3 分层依赖 (Layer Dependency)

CRUD View 只能依赖：

| 允许 | 禁止 |
|------|------|
| `Widget` | `ApiClient` |
| `Desktop Service` | `Router` |
| `Qt (PySide6)` | `Server` 模块 |
| `typing` | `ORM` |
| `logging` | `Database` |
| | `requests` |
| | `JWT` |
| | `bcrypt` |
| | 任何 Server 模块 |

#### 15.7.4 标准布局 (Standard Layout)

所有 CRUD 页面统一布局（自上而下）：

```
标题
  ↓
Toolbar
  ↓
SearchBar
  ↓
Table
  ↓
Pagination
  ↓
StatusBar
```

不得随意改变布局顺序。

#### 15.7.5 Toolbar 标准 (Toolbar Standard)

Toolbar 统一放置按钮：

| 按钮 | 命名 | 说明 |
|------|------|------|
| 新增 | `add_btn` | 打开新增 Dialog |
| 编辑 | `edit_btn` | 打开编辑 Dialog |
| 删除 | `delete_btn` | 确认后删除（如允许） |
| 刷新 | `refresh_btn` | 刷新列表 |
| 弹簧 | `Stretch` | 占位 |
| 搜索 | `SearchBar` | 搜索框 |

按钮命名统一，禁止业务特殊命名。

#### 15.7.6 搜索标准 (Search Standard)

统一使用 `SearchBar` Widget。不得自行创建 `QLineEdit` + `QPushButton` 搜索框。所有搜索统一：模糊搜索 → Enter / 按钮点击 → `search_requested` Signal。

#### 15.7.7 表格标准 (Table Standard)

统一使用 `QTableWidget`（未来如升级 `QTableView`，应统一迁移）。

默认配置：
- `NoEditTriggers` — 禁止编辑单元格
- `SelectRows` — 行选择模式
- `SingleSelection` — 单选
- `AlternatingRowColors` — 交替行颜色
- `Stretch` — 最后一列自动拉伸

列头统一由 View 定义。

#### 15.7.8 分页标准 (Pagination Standard)

统一分页组件，包含：第一页、上一页、下一页、最后一页。

统一属性：
- `_page_size` — 每页条数
- `_current_page` — 当前页码
- `_total` — 总记录数
- `total_pages` — 总页数

刷新流程统一。

#### 15.7.9 StatusBar 标准 (StatusBar Standard)

统一显示：共 XX 条记录、分页信息、刷新状态。禁止业务逻辑提示。

#### 15.7.10 刷新流程 (Refresh Flow)

统一刷新流程：

```
refresh()
  ↓
Desktop Service.list_xxx()
  ↓
更新 Table
  ↓
更新分页
  ↓
更新 StatusBar
```

`refresh()` 作为唯一刷新入口。

#### 15.7.11 CRUD 流程 (CRUD Flow)

**新增：**

```
Dialog → Desktop Service.create() → refresh() → emit changed Signal
```

**编辑：**

```
Dialog → Desktop Service.update() → refresh() → emit changed Signal
```

**删除：**

```
确认 → Desktop Service.delete() → refresh() → emit changed Signal
```

所有 CRUD 页面保持一致。

#### 15.7.12 Dialog 规则 (Dialog Rule)

新增/编辑统一使用 Dialog。Dialog 负责输入、参数收集、结果返回。View 负责调用 Desktop Service。

#### 15.7.13 权限规则 (Permission Rule)

按钮状态统一由 `_update_button_permissions()` 控制。禁止在多个地方分别判断权限。

#### 15.7.14 数据来源 (Data Source)

数据只能来自 **Desktop Service**。禁止直接访问 `ApiClient`、`requests`、Server、ORM、Database。

#### 15.7.15 异常处理 (Exception Handling)

异常统一通过 `QMessageBox` 显示。禁止 `print()`、吞异常、忽略异常。业务异常统一来自 Server。

#### 15.7.16 Signal 标准 (Signal Standard)

统一使用 `xxx_changed` Signal 刷新页面通知。页面之间通过 Signal/Slot 通信。禁止页面互相直接调用。

#### 15.7.17 日志 (Logging)

统一使用 `logging.getLogger("gtms.client")`。禁止 `print()`。

#### 15.7.18 代码风格 (Code Style)

- PEP8
- Google Docstring
- Type Hint
- UTF-8
- LF 换行
- 禁止：TODO、FIXME、`pass`、循环导入

#### 15.7.19 测试要求 (Testing Requirement)

CRUD 页面必须覆盖：
- `py_compile`
- `import`
- Toolbar
- SearchBar
- Table
- Pagination
- StatusBar
- `refresh()`
- CRUD 流程
- Signal
- 权限
- 异常
- logger
- PEP8
- Type Hint
- Docstring
- Frozen API

测试全部 PASS。

#### 15.7.20 公开 API 冻结 (Public API Freeze)

Mini Freeze 后公开 API 冻结。禁止修改公开方法、Signal、Property、函数签名。允许 Bug Fix、内部实现优化、新增私有函数。

#### 15.7.21 基线冻结 (Baseline Freeze)

所有 CRUD 页面完成后执行 **CRUD View Baseline Freeze Review**。检查布局、交互、Signal、分页、权限、异常、API、测试覆盖。

#### 15.7.22 适用范围 (Applicable Scope)

本规范适用于：
- `UserManageView`
- `CustomerView`
- `TrialTaskView`
- `ReceiptView`
- `GrindingView`
- `InspectionView`
- `DispatchView`
- `ReportView`
- `LogView`
- `StatisticsView`
- 以及未来所有 CRUD 页面

#### 15.7.23 ObjectName 标准 (ObjectName Standard)

所有 CRUD 页面中的 QWidget 必须设置 `ObjectName`。ObjectName 必须唯一、语义明确、统一采用 `snake_case` 命名。

禁止无意义命名：`button1`、`table1`、`widget1`、`layout1`、`lineEdit1`、`pushButton1` 等。

推荐统一命名：

| ObjectName | 用途 |
|------|------|
| `toolbar` | 工具栏 |
| `search_bar` | 搜索栏 |
| `task_table` | 任务表格 |
| `customer_table` | 客户表格 |
| `user_table` | 用户表格 |
| `status_bar` | 状态栏 |
| `pagination_widget` | 分页组件 |
| `add_btn` | 新增按钮 |
| `edit_btn` | 编辑按钮 |
| `delete_btn` | 删除按钮 |
| `refresh_btn` | 刷新按钮 |
| `first_page_btn` | 首页按钮 |
| `prev_page_btn` | 上一页按钮 |
| `next_page_btn` | 下一页按钮 |
| `last_page_btn` | 末页按钮 |
| `page_label` | 页码标签 |
| `total_label` | 总数标签 |
| `title_label` | 标题标签 |
| `dialog_button_box` | 对话框按钮盒 |

ObjectName 用于 QSS、Qt Designer、自动化测试、UI 调试。后续所有 CRUD 页面保持一致。

#### 15.7.24 表头标准 (Table Header Standard)

所有 CRUD 页面 Table Header 必须集中管理。统一定义 `TABLE_HEADERS` 常量。

示例：

```python
TABLE_HEADERS = [
    "任务编号",
    "客户名称",
    "加工要求",
    "销售",
    "流程状态",
    "结果状态",
    "创建时间",
]
```

禁止在多个地方重复 `setHorizontalHeaderLabels([...])`。必须统一使用 `setHorizontalHeaderLabels(TABLE_HEADERS)`。便于维护、国际化（i18n）、自动化测试、代码一致性。

#### 15.7.25 常量标准 (Constants Standard)

所有固定配置必须集中定义，包括但不限于：
- `WINDOW_TITLE` — 窗口标题
- `TABLE_HEADERS` — 表头
- `DEFAULT_PAGE_SIZE` — 默认每页条数
- `BUTTON_TEXT` — 按钮文字
- `COLUMN_INDEX` — 列索引
- `OBJECT_NAMES` — ObjectName 集合
- `DEFAULT_WIDTH` — 默认宽度
- `DEFAULT_HEIGHT` — 默认高度

禁止 Magic Number / Magic String 散落在代码中。所有常量统一放置于文件顶部。

#### 15.7.26 禁止 Magic Number / Magic String (No Magic Number / No Magic String)

禁止将以下值直接写入业务代码：

| 类型 | 禁止示例 | 应改为 |
|------|---------|------|
| 数字 | `20`、`8`、`100` | `DEFAULT_PAGE_SIZE`、`COLUMN_COUNT` |
| 字符串 | `"新增"`、`"编辑"`、`"删除"`、`"刷新"`、`"搜索"` | `BUTTON_TEXT`、`WINDOW_TITLE` |

统一定义常量，后续维护时仅修改常量。

#### 15.7.27 命名一致性 (Naming Consistency)

所有 CRUD 页面统一采用一致命名：

| 组件 | 统一命名 |
|------|---------|
| 表格 | `task_table`、`customer_table`、`user_table` |
| 工具栏 | `toolbar` |
| 搜索栏 | `search_bar` |
| 状态栏 | `status_bar` |
| 分页组件 | `pagination_widget` |
| 刷新入口 | `refresh()` |
| 权限刷新 | `_update_button_permissions()` |
| 数据填充 | `_populate_table()` |
| 搜索回调 | `_on_search()` |
| 新增回调 | `_on_add()` |
| 编辑回调 | `_on_edit()` |
| 删除回调 | `_on_delete()` |

保持 GTMS 全项目统一命名。

#### 15.7.28 CRUD View 常量约定 (CRUD View Constants Convention)

建议所有 CRUD 页面统一定义以下文件顶部常量：

```python
WINDOW_TITLE = "..."

TABLE_HEADERS = [...]

COLUMN_INDEX = {...}

DEFAULT_PAGE_SIZE = 20

BUTTON_TEXT = {...}

OBJECT_NAMES = {...}

LOGGER_NAME = "gtms.client"
```

禁止在多个函数中重复定义。

#### 15.7.29 可维护性原则 (Maintainability Principle)

所有 CRUD 页面应遵循：
- 高内聚、低耦合
- 统一命名
- 统一布局
- 统一刷新流程
- 统一分页
- 统一搜索
- 统一异常处理
- 统一日志
- 统一 Widget 复用

保证后续新增页面无需重新设计开发规范。

### 15.8 Upload & File Management Development Standard

#### 15.8.1 设计目标 (Design Goal)

统一 GTMS 文件上传、图片管理、文件存储、预览及下载开发规范，保证所有上传相关模块遵循统一架构、统一接口、统一命名、统一校验、统一日志、统一异常处理，避免重复实现。

---

#### 15.8.2 单一职责 (Single Responsibility)

各层职责如下：

- Upload Router：仅负责 HTTP 上传接口。
- Server Service：负责业务逻辑、数据库更新、状态流转。
- Desktop Service：仅负责 HTTP 请求封装。
- FileUploader：仅负责文件选择、上传交互。
- ImageViewer：仅负责图片展示。
- View：负责调用 Widget 与 Desktop Service。

禁止跨层承担职责。

---

#### 15.8.3 分层职责 (Layer Responsibility)

统一依赖关系：

Server
↓
Desktop Service
↓
Widget
↓
View
↓
MainWindow

禁止：

- Widget 调用 Server
- View 操作数据库
- Desktop Service 实现业务逻辑
- Router 更新数据库

---

#### 15.8.4 Upload Router 规范

Upload Router：

负责：

- 接收上传请求
- 保存文件
- 返回文件信息

不得：

- 更新数据库
- 修改业务状态
- 实现业务规则
- 调用 ORM 业务逻辑

---

#### 15.8.5 Server Service 规范

Server Service：

负责：

- 文件与业务对象绑定
- 更新数据库
- 状态流转
- 日志记录
- 权限检查
- 事务控制

所有业务规则统一由 Service 实现。

---

#### 15.8.6 Desktop Service 规范

Desktop Service：

仅负责：

- HTTP 请求
- 参数构造
- response.json() 返回

不得：

- 文件操作
- 业务逻辑
- 缓存
- 数据校验

---

#### 15.8.7 FileUploader Widget 规范

FileUploader：

负责：

- 文件选择
- 上传按钮
- 上传进度（如需要）
- Signal 发出

不得：

- 调用数据库
- 实现业务逻辑
- 修改状态
- 保存文件

保持 Pure UI。

---

#### 15.8.8 ImageViewer Widget 规范

ImageViewer：

负责：

- 图片显示
- 缩放
- 自适应
- 滚动浏览

不得：

- 上传图片
- 删除图片
- 修改数据库

保持 Pure UI。

---

#### 15.8.9 View 集成规范

View：

负责：

- 调用 Desktop Service
- 调用 FileUploader
- 调用 ImageViewer
- QMessageBox 提示异常

不得：

- 操作文件系统
- 实现上传业务逻辑

---

#### 15.8.10 文件命名规范

统一命名格式：

{task_no}_{module}_{timestamp}.{ext}

例如：

20260708-1_receipt_20260708153020.jpg

module：

- receipt
- grinding
- inspection
- report
- attachment

禁止随意命名。

---

#### 15.8.11 存储目录规范

统一目录：

uploads/

按模块分类：

uploads/receipt/

uploads/grinding/

uploads/inspection/

uploads/report/

uploads/attachment/

禁止 View 自行拼接路径。

---

#### 15.8.12 文件类型校验规范

必须进行：

- MIME Type 校验
- 扩展名校验

图片允许：

- jpg
- jpeg
- png

其他类型必须明确允许。

---

#### 15.8.13 文件大小限制

默认限制：

图片：

≤10MB

PDF：

≤50MB

其他类型由业务模块单独规定。

---

#### 15.8.14 上传目录配置

上传目录必须统一配置。

禁止：

硬编码路径。

允许：

配置文件统一管理。

---

#### 15.8.15 URL 返回规范

上传成功统一返回：

- filename
- url
- content_type
- size

禁止返回本地磁盘路径。

---

#### 15.8.16 日志规范

统一：

Server：

logging.getLogger("gtms.server")

Desktop：

logging.getLogger("gtms.client")

禁止：

print()

---

#### 15.8.17 异常处理规范

Server：

统一异常体系。

Desktop：

异常原样抛出。

View：

QMessageBox 展示。

Widget：

仅参数校验。

---

#### 15.8.18 安全规范

必须：

- 校验文件类型
- 校验文件大小
- 防止非法文件上传
- 防止路径遍历
- 不信任客户端文件名

文件名统一由服务器生成。

---

#### 15.8.19 API 冻结

Upload Router

Desktop Upload Service

FileUploader

ImageViewer

Public API 一经冻结：

不得修改：

- 方法名
- 参数
- 返回值
- Signal

只能新增调用。

---

#### 15.8.20 测试要求

至少覆盖：

- py_compile
- import
- 上传成功
- 非法类型
- 文件大小限制
- MIME 校验
- 文件命名
- URL 返回
- Widget API
- Pure UI
- PEP8
- Type Hint
- Docstring

全部 PASS 方可冻结。

---

#### 15.8.21 Upload Mini Freeze Review

每个 Upload 模块完成后必须执行：

Upload Mini Freeze Review。

检查：

- Architecture
- Dependency
- API
- Security
- Exception
- Logging
- Testing

全部 PASS 方可进入下一 Task。

---

#### 15.8.22 Upload Baseline Freeze Review

Sprint Upload 全部完成后必须执行：

Upload Baseline Freeze Review。

检查：

- Upload Router
- Desktop Service
- FileUploader
- ImageViewer
- View 集成

全部 PASS 方可进入 Sprint Baseline Freeze Review。

---

#### 15.8.23 适用范围 (Scope)

本规范适用于：

- Receipt
- Grinding
- Inspection
- Report
- Attachment
- Image Upload
- Future Upload Modules

以及未来所有涉及文件上传、图片管理、附件管理的模块。

#### 15.8.24 Upload API Response Standard

所有 Upload API 必须统一返回以下结构：

```json
{
    "filename": "20260708-1_receipt_20260708153020.jpg",
    "url": "/uploads/receipt/20260708-1_receipt_20260708153020.jpg",
    "content_type": "image/jpeg",
    "size": 856421
}
```

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| filename | string | 服务器生成后的文件名 |
| url | string | 文件相对访问路径，不包含 Base URL |
| content_type | string | 文件 MIME Type |
| size | integer | 文件大小，单位 Byte |

统一要求：

- filename 必须由服务器统一生成。
- url 必须为相对访问路径，不包含 Base URL。
- Desktop ApiClient 负责拼接 Base URL。
- content_type 必须使用标准 MIME Type。
- size 必须使用 Byte，不得转换为 KB、MB 或字符串。

禁止返回：

- path
- filepath
- full_path
- Windows 本地路径
- Linux 绝对路径
- Base URL
- 任何服务器磁盘路径

如未来需要扩展返回内容（例如 width、height、sha256 等），仅允许新增字段，不得修改或删除现有字段。

本规范适用于：

- Receipt
- Grinding
- Inspection
- Report
- Attachment
- Future Upload Modules

以及未来所有 Upload API。

### 15.9 Service Development Standard

#### 15.9.1 Design Goal

Service 是 GTMS 唯一业务逻辑层。

所有业务规则统一在 Server Service 实现，保证：

- 高内聚
- 低耦合
- 单一职责
- 可维护
- 可测试
- 可复用

所有业务模块（Customer、TrialTask、Receipt、Grinding、Inspection、Dispatch、Report、User 等）必须遵循本规范。

---

#### 15.9.2 Single Responsibility

Service 仅负责：

- 业务规则
- 数据校验
- CRUD
- 状态流转
- 数据库事务
- SystemLog
- 调用 ORM

不得负责：

- HTTP
- Router
- Qt UI
- Widget
- View
- Desktop Service
- 文件上传
- 文件下载
- 图片显示

---

#### 15.9.3 Dependency Rules

允许依赖：

- ORM Model
- Schema
- Enum
- SQLAlchemy Session
- Core Exceptions
- Core Security
- Utils
- SystemLog

禁止依赖：

- Router
- FastAPI Request
- FastAPI Response
- HTTPException
- QWidget
- Desktop Service
- ApiClient
- requests
- httpx
- PySide6

保持：

Server 独立。

---

#### 15.9.4 Transaction Standard

所有写操作统一采用：

try

↓

commit

↓

except

↓

rollback

↓

raise

禁止：

遗漏 rollback。

禁止：

Router 操作事务。

禁止：

Desktop Service 操作事务。

所有事务统一由 Service 管理。

---

#### 15.9.5 Exception Standard

统一使用项目异常：

- NotFoundException
- BusinessLogicException
- ValidationException
- PermissionDeniedException

禁止：

raise HTTPException

禁止：

raise Exception

Router 负责统一转换为 HTTP Response。

---

#### 15.9.6 Logging Standard

统一：

logging.getLogger("gtms.server")

记录：

- Create
- Update
- Delete
- Status Change
- Upload Metadata
- Business Warning
- Error

禁止：

print()

禁止：

View、Widget、Desktop Service 记录业务日志。

---

#### 15.9.7 SystemLog Standard

所有影响业务数据的操作必须记录 SystemLog：

包括：

- Create
- Update
- Delete
- Status Change

可根据业务需要记录：

- Receipt
- Grinding
- Inspection
- Dispatch

禁止：

View

Widget

Desktop Service

直接写入 SystemLog。

统一：

Server Service。

---

#### 15.9.8 Status Flow Standard

所有状态变更必须通过统一状态机。

禁止：

直接修改状态字段。

必须：

使用统一状态流转规则（如 next_statuses）。

非法状态流转统一抛出：

BusinessLogicException。

所有业务模块必须遵循统一状态流转机制。

---

#### 15.9.9 CRUD Standard

所有 CRUD 方法保持统一命名：

- create_xxx()
- get_xxx()
- list_xxx()
- update_xxx()
- delete_xxx()

保持：

Customer

TrialTask

Receipt

Grinding

Inspection

Dispatch

Report

全部一致。

---

#### 15.9.10 File Responsibility Standard

Service 不负责文件保存。

Service 仅负责：

- 文件元数据保存
- 文件元数据更新
- 文件元数据删除
- 上传成功后的业务处理

文件实际保存统一由：

Upload Router

FileHandler

负责。

禁止：

Service 操作磁盘。

禁止：

Service 保存 UploadFile。

禁止：

Service 保存 Base64。

禁止：

Service 保存 Binary。

---

#### 15.9.11 Upload Metadata Standard

Service 接收 Upload API 返回的数据：

包括：

- filename
- url
- content_type
- size

不得依赖：

磁盘路径

Windows Path

Linux Absolute Path

Upload API 返回结构统一遵循：

§15.8.24 Upload API Response Standard。

---

#### 15.9.12 Data Source Standard

Service 是数据库唯一访问入口。

允许：

ORM

Session

Database

禁止：

View

Widget

Desktop Service

直接访问数据库。

---

#### 15.9.13 Public API Standard

所有公开方法：

必须：

Type Hint

Google Docstring

保持最小公开 API。

私有辅助方法统一：

以下划线开头。

---

#### 15.9.14 Naming Standard

统一命名：

create_xxx

update_xxx

delete_xxx

list_xxx

get_xxx

禁止：

process()

handle()

execute()

run()

等语义不明确的方法名。

---

#### 15.9.15 Code Style

统一：

PEP8

Type Hint

Google Docstring

snake_case

Import 排序

禁止：

TODO

FIXME

Magic Number

Magic String

---

#### 15.9.16 Testing Standard

所有 Service 必须覆盖：

- CRUD
- Transaction
- Exception
- Status Flow
- Pagination
- Search
- Permission
- Soft Delete
- Upload Metadata（如适用）

所有测试必须：

100% PASS。

---

#### 15.9.17 Public API Freeze

每个 Service 完成后必须执行：

Service Mini Freeze Review。

Review 通过后：

公开 API 冻结。

禁止：

修改：

方法名称

参数

返回值

函数签名

仅允许：

新增调用。

---

#### 15.9.18 Service Baseline Freeze

所有 Service 完成后必须执行：

Service Baseline Freeze Review。

Review 内容包括：

- Architecture
- Dependency
- CRUD
- Transaction
- Exception
- Logging
- SystemLog
- Status Flow
- Upload Metadata（如适用）
- Testing
- Frozen API

Review 通过后：

Service Layer 正式冻结。

---

#### 15.9.19 Scope

本规范适用于：

- CustomerService
- UserService
- TrialTaskService
- ReceiptService
- GrindingService
- InspectionService
- DispatchService
- ReportService

以及未来所有 Server Service。

#### 15.9.20 Performance Standard

所有 Service 应遵循性能优先原则，在保证代码可读性和可维护性的前提下，避免产生不必要的数据库、网络或文件系统开销。

##### 查询规范

所有列表查询必须支持分页。

禁止一次性查询全部数据。

统一使用：

- page
- page_size

进行分页。

默认分页大小应使用统一常量配置。

---

##### 查询条件规范

列表查询应优先支持：

- Keyword
- Status
- Date Range
- Sorting

禁止在 Python 内存中进行大规模过滤。

应优先使用数据库查询完成过滤。

---

##### 数据加载规范

列表接口仅返回列表展示所需字段。

详情接口返回完整数据。

禁止列表接口返回大量无用字段。

避免重复查询同一数据。

---

##### 排序规范

所有列表接口应支持统一排序。

默认按照：

创建时间倒序。

排序字段必须明确指定。

禁止依赖数据库默认排序。

---

##### 数据库访问规范

所有数据库访问统一通过 ORM。

禁止直接拼接 SQL。

禁止重复创建 Session。

禁止跨 Service 操作数据库。

数据库连接统一由依赖注入管理。

---

##### 文件处理规范

Service 不负责：

- 文件上传
- 文件下载
- 图片压缩
- 图片缩放
- 文件复制
- 文件移动

所有文件操作统一由：

Upload Router

FileHandler

负责。

Service 仅处理文件元数据。

---

##### 循环与计算规范

禁止在循环内执行数据库查询。

禁止在循环内重复创建对象。

对于批量数据，应尽量减少重复计算。

避免 O(n²) 以上复杂度的数据处理。

---

##### 网络访问规范

Service 禁止：

- requests
- httpx
- urllib

所有 HTTP 通信统一由：

Router

Desktop Service

ApiClient

负责。

---

##### 日志规范

日志应记录关键业务信息。

禁止输出大量调试日志。

禁止在循环内频繁记录日志。

Error 日志应包含必要上下文。

---

##### 内存使用规范

避免长期持有大量对象。

避免缓存数据库实体。

避免在内存中保存大文件。

仅保存当前业务所需数据。

---

##### 可扩展性原则

所有 Service 应支持：

- 数据量增长
- 模块扩展
- 新增查询条件
- 新增排序字段
- 新增分页策略

不得因业务规模扩大而需要重构整体架构。

---

##### 禁止事项

禁止：

- 查询全表后再过滤
- 无分页列表接口
- 在 Service 中执行文件读写
- 在 Service 中执行 HTTP 请求
- 在循环内频繁查询数据库
- 返回超过业务需要的数据
- 重复创建数据库连接
- 使用 Magic Number 控制分页

---

##### 适用范围

本规范适用于：

- CustomerService
- UserService
- TrialTaskService
- ReceiptService
- GrindingService
- InspectionService
- DispatchService
- ReportService

以及未来所有 Server Service。

### 15.10 Desktop Service Development Standard

它将统一规范：

client/services/*.py
ApiClient 调用方式
HTTP 封装
Query 参数
Body 参数
错误处理
日志
Public API Freeze
Mini Freeze
Desktop Service Baseline Freeze

这样你的规范体系就会覆盖整个 GTMS 架构：

Server（Service）
Desktop（Desktop Service）
Widget
View
CRUD
Upload

### 15.11 Business Workflow Development Standard

本规范用于统一 GTMS 业务流程（Workflow）的设计、实现与维护方式，确保各模块业务流程一致、职责清晰、易于扩展。

---

#### 15.11.1 设计目标（Design Goals）

所有业务流程应遵循：

- 流程统一
- 职责单一
- 可扩展
- 可维护
- 状态一致
- 业务集中
- UI 无业务逻辑

保证未来新增业务流程无需重新设计整体架构。

---

#### 15.11.2 适用范围（Scope）

本规范适用于：

- TrialTask
- Receipt
- Grinding
- Inspection
- Dispatch
- Report
- Future Workflow

以及未来所有涉及业务流程管理的模块。

---

#### 15.11.3 Workflow 分层职责（Workflow Layer Responsibility）

业务流程统一遵循：

Server Service

↓

Desktop Service

↓

View

↓

Widget

Server Service：

负责业务流程。

Desktop Service：

负责调用 Server API。

View：

负责展示和事件分发。

Widget：

负责状态展示。

---

#### 15.11.4 Workflow Ownership

所有 Workflow 必须由：

Server Service

统一负责。

禁止：

Desktop Service

View

Widget

直接实现业务流程。

---

#### 15.11.5 Workflow 状态流转

所有状态流转：

统一由 Server Service 控制。

禁止：

View 修改状态。

禁止：

Desktop Service 修改状态。

禁止：

Widget 修改状态。

---

#### 15.11.6 Workflow API

所有 Workflow API：

统一由 Router 暴露。

Desktop Service：

仅负责调用。

禁止：

Widget

View

直接调用 HTTP。

---

#### 15.11.7 Workflow Event

所有 Workflow：

统一使用：

Signal

通知界面刷新。

Signal：

仅通知。

不得携带业务逻辑。

---

#### 15.11.8 Workflow Refresh

所有 Workflow 操作成功后：

统一：

refresh()

刷新页面。

不得局部修改 UI 数据。

---

#### 15.11.9 Workflow Logging

Workflow 应记录：

开始

成功

失败

Error

日志统一使用：

logging.getLogger("gtms.client")

---

#### 15.11.10 Workflow Exception

业务异常：

统一由：

Server

抛出。

Desktop：

原样抛出。

View：

QMessageBox

统一显示。

Widget：

不得处理业务异常。

---

#### 15.11.11 Workflow Testing

所有 Workflow 必须覆盖：

- 创建
- 编辑
- 删除
- 状态流转
- 异常
- 权限
- 上传（如适用）

所有测试必须通过。

---

#### 15.11.12 Public API Freeze

Workflow 对外公开接口：

评审通过后立即冻结。

禁止修改：

函数签名

参数

返回值

Signal

---

#### 15.11.13 Mini Freeze

每个 Workflow 完成后必须执行：

Workflow Mini Freeze Review。

Review 内容包括：

- Architecture
- Dependency
- Workflow
- Refresh
- Logging
- Exception
- Testing
- Frozen API

---

#### 15.11.14 Workflow Baseline Freeze

所有 Workflow 完成后必须执行：

Workflow Baseline Freeze Review。

Review 内容包括：

- Workflow Architecture
- Layer Responsibility
- Business Logic
- Status Flow
- Upload Flow（如适用）
- Exception
- Logging
- Testing
- Frozen API

Review 通过后：

Workflow Layer 正式冻结。

### 15.12 Status Machine Development Standard

本规范用于统一 GTMS 状态机（Status Machine）的设计、实现与维护方式，确保所有业务状态定义一致、状态流转可控、职责清晰、易于扩展。

---

#### 15.12.1 设计目标（Design Goals）

所有状态机应遵循：

- 状态统一
- 流转明确
- 单一入口
- 易扩展
- 易维护
- 状态一致
- UI 无业务逻辑

保证未来新增状态无需重构整体架构。

---

#### 15.12.2 适用范围（Scope）

本规范适用于：

- TrialTask
- Receipt
- Grinding
- Inspection
- Dispatch
- Report
- Future Status Machine

以及未来所有涉及状态管理的模块。

---

#### 15.12.3 状态分类（Status Classification）

GTMS 状态统一分为：

Process Status

Result Status

Process Status：

表示业务流程状态。

Result Status：

表示业务处理结果。

不得混合使用。

---

#### 15.12.4 状态定义原则（Status Definition）

所有状态必须：

- 唯一
- 可读
- 可扩展
- 可序列化

统一使用：

snake_case

命名。

禁止：

Status1

Status2

TempStatus

Done

Finish

等无语义命名。

---

#### 15.12.5 状态流转原则（Status Transition）

所有状态流转必须：

单向。

禁止：

循环跳转。

禁止：

跨阶段跳转。

禁止：

非法状态修改。

状态流转统一由：

Server Service

负责。

---

#### 15.12.6 状态修改权限（Status Ownership）

只有：

Server Service

允许修改状态。

禁止：

Router

Desktop Service

View

Widget

直接修改状态。

---

#### 15.12.7 状态展示规范（Status Presentation）

状态展示统一使用：

StatusBadge Widget

统一颜色

统一文本

统一图标（如适用）

禁止：

View

自行拼接状态文本。

---

#### 15.12.8 状态查询规范（Status Query）

所有列表接口应支持：

process_status

result_status

查询过滤。

统一使用：

Query Parameter。

禁止：

Python 内存过滤。

---

#### 15.12.9 状态刷新规范（Status Refresh）

状态修改成功后：

统一调用：

refresh()

刷新页面。

不得局部修改状态显示。

---

#### 15.12.10 状态日志（Status Logging）

所有状态流转应记录：

原状态

新状态

Task ID

Operator

Time

日志统一使用：

logging.getLogger("gtms.client")

---

#### 15.12.11 状态异常（Status Exception）

非法状态流转：

统一由：

Server

抛出业务异常。

Desktop：

原样抛出。

View：

QMessageBox

统一提示。

Widget：

不得处理状态异常。

---

#### 15.12.12 状态测试（Status Testing）

所有状态机必须覆盖：

- 合法流转
- 非法流转
- 重复流转
- 边界状态
- 状态查询
- 状态展示

所有测试必须通过。

---

#### 15.12.13 Public API Freeze

所有状态相关公开 API：

Review 通过后立即冻结。

禁止修改：

函数签名

参数

返回值

Signal

---

#### 15.12.14 Mini Freeze

每个状态模块完成后必须执行：

Status Machine Mini Freeze Review。

Review 内容包括：

- Architecture
- Status Definition
- Status Transition
- Dependency
- Exception
- Logging
- Testing
- Frozen API

---

#### 15.12.15 Status Machine Baseline Freeze

所有状态机完成后必须执行：

Status Machine Baseline Freeze Review。

Review 内容包括：

- Status Definition
- Status Transition
- Server Ownership
- Desktop Delegation
- View Presentation
- Widget Integration
- Logging
- Exception
- Testing
- Frozen API

Review 通过后：

Status Machine 正式冻结。

---

#### 15.12.16 禁止事项（Prohibited）

禁止：

- View 修改状态
- Widget 修改状态
- Desktop Service 修改状态
- Router 实现状态流转
- 绕过 Server Service 修改状态
- 同时修改 Process Status 与 Result Status 而无业务依据
- 在 UI 中硬编码状态颜色
- 使用 Magic String 判断状态
- 在多个模块维护同一状态逻辑

所有状态逻辑统一由：

Server Service

负责。

---

#### 15.12.17 可扩展性原则（Extensibility Principle）

所有状态机应支持：

- 新增状态
- 新增状态流转
- 新增状态展示
- 新增查询条件
- 新增业务模块

不得因新增状态而重构整体架构。

### 15.13 Query Aggregation Principle

本规范用于统一 GTMS 查询统计（Query & Statistics）的聚合数据来源、计算方式与输出标准，确保所有统计查询一致、可靠、可扩展、可审计。

---

#### 15.13.1 设计目标（Design Goals）

所有查询统计应遵循：

- 数据来源一致
- 统计口径统一
- 数据库优先
- 只读安全
- 可扩展
- 可审计
- UI 无聚合逻辑

保证未来新增 Dashboard、BI、Report 等模块无需重新设计统计架构。

---

#### 15.13.2 适用范围（Scope）

本规范适用于：

- QueryService
- Statistics
- Dashboard
- BI
- Report
- Export
- Future Aggregation Modules

以及未来所有涉及数据查询、统计、聚合、导出的模块。

---

#### 15.13.3 唯一聚合入口（Single Aggregation Entry）

所有统计聚合必须由 **QueryService** 统一提供。

禁止：

- 其他 Service 实现统计聚合
- Router 直接查询聚合
- View 实现统计算法
- Desktop Service 实现数据统计
- Widget 计算统计指标

保证：

所有统计查询结果一致，无重复实现，无口径差异。

---

#### 15.13.4 数据来源统一（Unified Data Source）

所有统计必须基于 **TrialTask** 关联查询。

关联链路：

```
TrialTask
  ├── Customer       (customer_id)
  ├── User           (sales_id)
  ├── GrindingRecord (task_id)
  ├── InspectionRecord (task_id)
  ├── Dispatch       (task_id)
  └── Receipt        (task_id)
```

禁止：

- 跨 Service 直接读取其他表
- 绕过 TrialTask 查询关联数据
- 使用非 ORM 方式查询数据库
- 直接拼接 SQL

所有关联查询必须通过 SQLAlchemy ORM JOIN 完成。

---

#### 15.13.5 数据库优先原则（Database-First Principle）

所有统计必须优先使用数据库聚合函数。

允许：

- `func.count()` — 计数
- `func.sum()` — 求和
- `func.avg()` — 平均值
- `GROUP BY` — 分组聚合
- `ORDER BY` — 排序
- `.filter()` — 条件过滤

禁止：

- Python `len()` 替代 `COUNT`
- Python `sum()` 替代 `SUM`
- Python `for` 循环聚合
- 查询全表后在 Python 内存中统计
- 在循环内逐条查询数据库

所有聚合计算必须在数据库层完成，结果直接返回。

---

#### 15.13.6 过滤与分页（Filtering & Pagination）

所有查询必须使用数据库层过滤与分页。

允许：

- `.filter()` 构建 WHERE 子句
- `.offset()` + `.limit()` 实现分页
- `.order_by()` 实现排序
- `.count()` 获取总数

禁止：

- 查询全表后在 Python 内存中过滤
- `SELECT *` 无限制查询
- Python 列表切片替代分页
- Python `sorted()` 替代数据库排序

所有过滤条件必须转化为 ORM 表达式，确保数据库执行计划最优。

---

#### 15.13.7 导出数据规范（Export Data Standard）

`export_excel()` 仅负责准备导出数据，不生成文件。

允许：

- 返回 `list[dict]` 二维数据
- 复用 `_apply_filters()` 筛选条件
- 复用 `_apply_sorting()` 排序逻辑
- 复用 `_task_to_dict()` 数据转换

禁止：

- 生成 Excel 文件
- 依赖 `openpyxl`
- 文件写入
- 返回文件路径
- 返回二进制流

导出文件生成由调用方（Router / View）负责，QueryService 仅提供数据。

---

#### 15.13.8 只读约束（Read-Only Constraint）

QueryService 全部接口为只读查询。

禁止：

- `db.commit()`
- `db.rollback()`
- `db.flush()`
- `db.add()`
- `db.delete()`
- ORM `update()`
- ORM `insert()`
- ORM `delete()`
- 修改 `process_status`
- 修改 `result_status`
- 修改任何数据库记录

QueryService 不含任何写操作，确保统计查询安全。

---

#### 15.13.9 统计指标定义（Statistics Metrics Definition）

所有统计指标必须统一口径。

通过数量：

```
result_status == TrialTaskResultStatus.PASSED
```

失败数量：

```
result_status == TrialTaskResultStatus.FAILED
```

成功率：

```
passed_count / (passed_count + failed_count) × 100
```

零除保护：

```
total_evaluated > 0 时计算，否则 success_rate = 0.0
```

本月任务数：

```
created_at >= month_start（当月 1 日 00:00:00）
```

年度任务数：

```
created_at >= year_start（当年 1 月 1 日 00:00:00）
```

禁止：

- 各模块自行定义统计口径
- 对同一指标使用不同计算方式
- 硬编码统计日期范围

---

#### 15.13.10 排行统计规范（Ranking Statistics Standard）

排行统计统一使用 `GROUP BY` + `COUNT` + `ORDER BY DESC` + `LIMIT`。

客户排行：

```
GROUP BY customer.id, customer.company_name
ORDER BY COUNT DESC
LIMIT 10
```

机型排行：

```
JOIN grinding_records
GROUP BY grinding_records.machine_type
ORDER BY COUNT DESC
LIMIT 10
```

禁止：

- Python 内存分组
- Python `collections.Counter()` 替代 GROUP BY
- 不限量排行

Top N 排行统一使用 `LIMIT` 控制，默认取 Top 10。

---

#### 15.13.11 日志规范（Logging Standard）

QueryService 应记录：

- 查询条件（page, page_size, 筛选参数）
- 统计请求（month, year, passed, failed, rate）
- 导出请求（total, file_name）
- 排行结果（returned 条数）

日志统一使用：

```
logging.getLogger("gtms.server")
```

禁止：

- 循环日志
- 单条记录日志
- `print()`

---

#### 15.13.12 异常处理规范（Exception Handling Standard）

查询统计为只读操作，空结果不抛异常。

允许：

- 空结果返回空列表 `[]`
- 空结果返回 `total = 0`
- 无排行数据返回空列表 `[]`

禁止：

- 空结果抛出 `NotFoundException`
- 空结果抛出任何异常
- `raise` 任何异常

参数校验由 Schema 层负责，Service 层不重复校验。

---

#### 15.13.13 可扩展性（Extensibility）

QueryService 应支持：

- 新增筛选条件
- 新增排序字段
- 新增统计指标
- 新增排行维度
- 新增导出格式
- Dashboard 集成
- BI 系统集成
- Report 模块集成

不得因新增统计需求而重构整体架构。

---

#### 15.13.14 测试要求（Testing Requirement）

QueryService 必须覆盖：

- list_tasks（组合查询、分页、排序）
- get_statistics（本月/年度/通过/失败/成功率）
- get_customer_ranking（客户排行 Top 10）
- get_machine_ranking（机型排行 Top 10）
- export_excel（数据导出准备）
- 空结果
- 日期范围
- 零除保护
- 只读约束
- 性能标准

所有测试必须 100% PASS。

---

#### 15.13.15 Public API Freeze

QueryService 公开 API 冻结后：

禁止修改：

- 方法名
- 参数签名
- 返回值类型
- 统计口径

允许：

- 新增统计方法
- 新增筛选条件
- 新增排行维度
- 内部实现优化

---

#### 15.13.16 Mini Freeze

QueryService 完成后必须执行：

**Query Service Mini Freeze Review**。

Review 内容包括：

- Architecture
- Single Aggregation Entry
- Unified Data Source
- Database-First Principle
- Read-Only Constraint
- Export Data Standard
- Statistics Metrics
- Ranking Standard
- Logging
- Exception
- Performance
- Testing
- Frozen API

---

#### 15.13.17 Baseline Freeze

Query & Statistics 模块全部完成后必须执行：

**Query & Statistics Baseline Freeze Review**。

Review 内容包括：

- QueryService
- QueryRouter
- Desktop QueryService
- QueryView
- Statistics Metrics
- Ranking Logic
- Export Logic
- Dashboard Integration
- Testing
- Frozen API

Review 通过后：

Query & Statistics 模块正式冻结。

---

#### 15.13.18 适用范围汇总（Scope Summary）

本规范适用于：

- QueryService
- QueryRouter
- Desktop QueryService
- QueryView
- Dashboard
- BI
- Report
- Future Aggregation Modules

以及未来所有涉及数据查询、统计、聚合、导出的模块。

==================================================
### 15.14 Analysis View Principle
==================================================

#### 15.14.1 Design Goal
--------------------------------------------------

Analysis View

用于：

查询

统计展示

排行榜

Dashboard

报表展示。

Analysis View

属于：

Pure View。

==================================================
#### 15.14.2 Scope
==================================================

适用于：

QueryView

Dashboard

Statistics View

Report View

以及：

所有分析展示页面。

==================================================
#### 15.14.3 Zero Business Logic
==================================================

Analysis View

不得：

计算统计数据。

不得：

计算成功率。

不得：

计算排行榜。

不得：

计算汇总。

所有数据：

必须来自：

Desktop Service。

==================================================
#### 15.14.4 Zero Aggregation
==================================================

Analysis View

不得：

count()

sum()

avg()

group by

排序统计。

所有聚合：

必须：

Server QueryService

完成。

==================================================
#### 15.14.5 Zero Export Logic
==================================================

Analysis View

不得：

生成 Excel。

不得：

生成 PDF。

不得：

写入文件。

仅允许：

调用：

Desktop QueryService.export_excel()。

==================================================
#### 15.14.6 Widget Responsibility
==================================================

View

仅负责：

数据显示。

图表刷新。

分页。

搜索。

按钮事件。

不得：

处理业务逻辑。

==================================================
#### 15.14.7 Refresh Flow
==================================================

refresh()

必须作为：

唯一刷新入口。

统一流程：

Desktop Service

↓

Table

↓

Statistics

↓

Ranking

↓

Pagination

↓

StatusBar

==================================================
#### 15.14.8 Dependency
==================================================

Analysis View

仅允许依赖：

Desktop Service。

禁止：

ApiClient。

禁止：

Router。

禁止：

ORM。

禁止：

Database。

==================================================
#### 15.14.9 Workflow
==================================================

Zero Workflow。

不得：

process_status

判断。

==================================================
#### 15.14.10 Status Machine
==================================================

Zero Status Machine。

不得：

result_status

流转。

==================================================
#### 15.14.11 Public API Freeze
==================================================

Public API

冻结后：

不得修改函数签名。

仅允许：

新增调用。

==================================================
#### 15.14.12 Testing
==================================================

必须覆盖：

查询。

刷新。

分页。

统计展示。

排行榜展示。

导出按钮。

Layout。

ObjectName。

Signal。

全部 PASS。

==================================================
#### 15.14.13 Mini Freeze
==================================================

Analysis View

完成后：

必须进行：

Mini Freeze Review。

==================================================
#### 15.14.14 Baseline Freeze
==================================================

Sprint 完成后：

Analysis View

进入：

View Baseline Freeze。

==================================================
#### 15.14.15 Summary
==================================================

Analysis View

定位：

Pure Presentation。

所有：

查询。

统计。

排行。

导出。

全部委托：

Desktop QueryService

↓

Server QueryService。

Analysis View

永远不承担：

统计计算。

业务逻辑。

状态流转。

==================================================
### 15.15 Audit Logging Principle
==================================================

#### 15.15.1 Design Goal
--------------------------------------------------

Audit Logging

用于：

记录系统所有关键操作。

提供：

操作追踪。

问题定位。

责任追溯。

安全审计。

Audit Logging

属于：

Infrastructure Service。

==================================================
#### 15.15.2 Scope
==================================================

适用于：

SystemLog

LogService

所有业务 Service

SystemLogView

以及：

所有产生业务修改的模块。

==================================================
#### 15.15.3 Logging Responsibility
==================================================

仅：

Server LogService

负责：

创建日志。

Desktop Service

View

Router

不得：

写入日志。

==================================================
#### 15.15.4 Trigger Rule
==================================================

以下操作：

必须记录日志：

Create

Update

Delete（软删除）

Status Change

Login

Logout

Permission Change

Import

Export

System Configuration

其他关键业务操作。

==================================================
#### 15.15.5 Read Operation
==================================================

普通查询：

默认：

不记录日志。

如有安全要求：

可新增：

Audit Read Log。

不得影响：

现有 Public API。

==================================================
#### 15.15.6 Log Content
==================================================

每条日志至少包含：

操作时间。

操作人。

操作类型。

模块名称。

目标对象。

目标 ID。

操作结果。

描述信息。

==================================================
#### 15.15.7 Immutable Principle
==================================================

日志：

创建后：

禁止修改。

禁止删除。

禁止覆盖。

仅允许：

新增。

==================================================
#### 15.15.8 Business Independence
==================================================

日志系统不得影响业务流程。

日志失败不得导致业务失败。

日志属于非业务数据。

日志失败不能影响业务成功。

例如：

创建客户成功，但写日志失败 → 客户仍然创建成功。
完成试磨成功，但日志数据库异常 → 试磨仍然完成。
完成检测成功，但日志异常 → 检测结果仍然保存。

==================================================
#### 15.15.9 Transaction Principle
==================================================

日志写入应与业务事务保持一致。

如采用独立事务。

不得影响主业务提交。

==================================================
#### 15.15.10 Exception Rule
==================================================

LogService

仅抛出：

系统异常。

不得：

修改业务异常。

不得：

吞掉异常。

==================================================
#### 15.15.11 Query Principle
==================================================

日志查询：

只读。

支持：

分页。

关键字。

操作人。

操作类型。

时间范围。

排序。

不得：

修改日志。

==================================================
#### 15.15.12 View Principle
==================================================

SystemLogView

属于：

Pure View。

不得：

创建日志。

不得：

修改日志。

不得：

删除日志。

仅负责：

查询。

展示。

筛选。

==================================================
#### 15.15.13 Desktop Service Principle
==================================================

Desktop LogService

仅负责：

HTTP Mapping。

不得：

记录日志。

不得：

业务处理。

不得：

Workflow。

不得：

Status Machine。

==================================================
#### 15.15.14 Performance Principle
==================================================

日志查询：

必须支持：

分页。

排序。

过滤。

不得：

一次加载全部日志。

==================================================
#### 15.15.15 Logging Principle
==================================================

LogService

使用：

gtms.server

logger。

禁止：

print()。

==================================================
#### 15.15.16 Testing
==================================================

必须覆盖：

新增日志。

查询日志。

分页。

筛选。

排序。

不可修改。

不可删除。

全部：

PASS。

==================================================
#### 15.15.17 Public API Freeze
==================================================

Log Module

Public API

冻结后：

不得修改函数签名。

仅允许：

新增调用。

==================================================
#### 15.15.18 Mini Freeze
==================================================

Log Module

完成后：

必须进行：

Mini Freeze Review。

==================================================
#### 15.15.19 Baseline Freeze
==================================================

Sprint 完成后：

Log Module

进入：

Baseline Freeze。

==================================================
#### 15.15.20 Summary
==================================================

Audit Logging

定位：

Infrastructure Service。

所有日志：

统一由：

Server LogService

负责。

Desktop Service

Router

View

不得：

生成日志。

日志：

只追加。

不可修改。

不可删除。

Audit Logging

永远不承担：

业务逻辑。

Workflow。

Status Machine。

### §15.16 Read-Only View Principle

#### §15.16.1 设计目标

Read-Only View 用于展示、查询、统计、审计等只读数据。

其职责仅包括：

- 数据查询
- 数据展示
- 条件筛选
- 分页浏览
- 导出数据请求

不得承担任何业务处理职责。

---

#### §15.16.2 适用范围

本原则适用于所有 Read-Only 页面，包括但不限于：

- QueryView
- SystemLogView
- Dashboard
- StatisticsView
- ReportView
- AuditView
- MonitorView
- HistoryView

所有只读页面必须遵循本规范。

---

#### §15.16.3 Public API

Read-Only View 仅允许公开：

- __init__()
- refresh()

不得新增其它 Public Method。

所有其它方法必须为 Private Method。

---

#### §15.16.4 唯一刷新入口

refresh()

必须作为页面唯一刷新入口。

推荐流程：

refresh()

↓

Desktop Service

↓

populate_table()

↓

update_statistics()

↓

update_pagination()

↓

update_status_bar()

禁止多个刷新入口。

---

#### §15.16.5 数据来源统一

Read-Only View 不得直接访问：

- ApiClient
- HTTP
- Router
- ORM
- SQLAlchemy
- Database

所有数据必须统一来自：

Desktop Service。

---

#### §15.16.6 零业务逻辑原则

Read-Only View 不得包含：

- Business Logic
- Workflow
- Status Machine
- 审批流程
- 状态流转
- 权限决策

所有业务逻辑必须委托给 Service。

---

#### §15.16.7 零 CRUD 原则

Read-Only View 禁止：

- Create
- Update
- Delete

允许：

- Search
- Filter
- Pagination
- Export

若存在新增、编辑、删除需求，应由对应 CRUD View 实现。

---

#### §15.16.8 导出规范

Read-Only View 可以提供：

导出按钮。

点击导出时：

仅允许调用：

Desktop Service.export_xxx()

不得：

- openpyxl
- xlsxwriter
- pandas.ExcelWriter
- CSV 写入
- 文件保存

View 不负责生成任何文件。

---

#### §15.16.9 Widget 规范

允许：

- SearchBar
- Filter Panel
- QTableWidget
- Pagination
- StatusBar
- Statistics Panel
- Ranking Panel

禁止：

复杂业务控件。

---

#### §15.16.10 Table 规范

QTableWidget 建议统一：

- NoEditTriggers
- SelectRows
- SingleSelection
- AlternatingRowColors
- StretchLastSection

保持统一 UI 风格。

---

#### §15.16.11 ObjectName 与 Constants

所有：

- ObjectName
- Button Text
- Label Text
- Default Value
- Column Name

必须集中管理。

禁止：

Magic String。

禁止：

Magic Number。

---

#### §15.16.12 Logging

统一使用：

gtms.client

logger。

禁止：

print()。

---

#### §15.16.13 Exception

Read-Only View

禁止：

try/except。

异常统一交由：

Desktop Service

或

Global Exception Handler

处理。

---

#### §15.16.14 测试要求

必须覆盖：

- 初始化
- refresh()
- 搜索
- 筛选
- 分页
- 导出
- 状态栏
- Signal
- ObjectName
- Constants

并保证全部历史 View 回归测试通过。

---

#### §15.16.15 Public API Freeze

View Mini Freeze 结束后：

Public API 正式冻结。

不得新增：

Public Method。

不得修改：

refresh()。

---

#### §15.16.16 Mini Freeze

Read-Only View 完成开发后必须执行：

Mini Freeze Review。

确认：

- Zero Business Logic
- Zero Workflow
- Zero Status Machine
- Zero CRUD
- Zero Aggregation
- Zero HTTP
- Zero ORM

全部符合后方可冻结。

---

#### §15.16.17 View Baseline Freeze

所有 Read-Only View 完成后：

进入 View Baseline Freeze。

确认：

- Widget Integration
- Refresh Flow
- Desktop Service
- ObjectName
- Constants
- Logging
- Regression

全部通过。

---

#### §15.16.18 适用范围汇总

本规范统一适用于：

- QueryView
- SystemLogView
- Dashboard
- StatisticsView
- ReportView
- MonitorView
- AuditView
- HistoryView

以及未来所有只读页面。

所有新建只读页面默认遵循本规范。

### §15.17 Notification Principle

#### §15.17.1 设计目标

Notification Module 用于统一管理系统消息提醒。

其职责包括：

- 自动生成提醒
- 消息查询
- 消息已读
- 消息跳转
- 用户消息隔离

Notification 不负责：

- 邮件发送
- 短信发送
- 微信推送
- 企业 IM 推送

所有消息均为系统内部通知。

---

#### §15.17.2 适用范围

本规范适用于：

- Notification Schema
- Notification Service
- Notification Router
- APScheduler
- Desktop NotificationService
- Dashboard Notification Panel

所有消息功能必须遵循本规范。

---

#### §15.17.3 唯一消息生成入口

所有消息必须统一由：

NotificationService

生成。

禁止：

Router

View

Scheduler

直接创建 NotificationRecord。

---

#### §15.17.4 Scheduler Principle

APScheduler

仅负责：

Trigger。

允许：

定时调用：

NotificationService。

禁止：

业务判断。

ORM 操作。

Workflow。

Status Machine。

所有业务逻辑必须位于：

NotificationService。

---

#### §15.17.5 消息生成规则

NotificationService

负责：

判断是否需要生成提醒。

生成消息。

去重检查。

写入数据库。

不得由其它模块生成消息。

---

#### §15.17.6 去重原则

相同：

- user_id
- notification_type
- target_type
- target_id

未读状态下：

最多存在一条消息。

禁止重复生成。

---

#### §15.17.7 消息读取原则

读取消息：

不得修改业务数据。

允许：

mark_as_read()

仅修改：

is_read

read_time

不得影响：

Workflow。

Status Machine。

---

#### §15.17.8 用户隔离原则

用户仅允许查看：

属于自己的消息。

禁止：

跨用户。

跨角色。

跨部门。

访问消息。

---

#### §15.17.9 Dashboard Principle

Dashboard

仅负责：

展示消息。

未读数量。

角标。

点击跳转。

禁止：

生成消息。

修改业务状态。

业务判断。

---

#### §15.17.10 Desktop NotificationService

Desktop Service

职责仅包括：

HTTP Mapping。

禁止：

Business Logic。

Workflow。

Status Machine。

Aggregation。

所有方法统一返回：

resp.json()。

---

#### §15.17.11 Router Principle

Notification Router

仅负责：

HTTP。

Permission。

Dependency Injection。

调用：

NotificationService。

禁止：

Business Logic。

ORM。

Workflow。

Status Machine。

---

#### §15.17.12 Logging

Notification

所有新增。

已读。

自动生成。

必须统一记录：

Audit Log。

统一调用：

LogService.create_log()。

禁止直接写：

SystemLog。

---

#### §15.17.13 Exception

NotificationService

统一抛出：

BusinessLogicException。

NotFoundException。

ValidationException。

Desktop

不捕获异常。

Router

不处理异常。

统一交由：

Global Exception Handler。

---

#### §15.17.14 测试要求

必须覆盖：

- 自动生成
- 去重
- 已读
- 查询
- 用户隔离
- Scheduler
- Dashboard
- Desktop Service
- Router

以及全部历史回归测试。

---

#### §15.17.15 Public API Freeze

Notification

Mini Freeze

结束后：

Public API

正式冻结。

不得新增：

Public Method。

不得修改：

函数签名。

---

#### §15.17.16 Mini Freeze

Notification

每个 Layer

完成开发后：

必须执行：

Mini Freeze Review。

确认：

- Zero Workflow
- Zero Status Machine
- Zero Business Logic（Router/Desktop）
- Zero ORM（Router/View）
- Zero HTTP（View）

全部符合后方可冻结。

---

#### §15.17.17 Baseline Freeze

Sprint 12

完成后：

执行：

Baseline Freeze。

确认：

Server。

Desktop。

Scheduler。

Dashboard。

Notification。

全部冻结。

---

#### §15.17.18 Future Extension

未来允许扩展：

- Email Notification
- SMS Notification
- WebSocket Push
- MQTT Push
- 企业微信
- 钉钉
- Slack
- Microsoft Teams

扩展不得修改：

Notification Public API。

---

#### §15.17.19 适用范围汇总

本规范统一适用于：

- Notification Schema
- Notification Service
- Notification Router
- APScheduler
- Desktop NotificationService
- Dashboard Notification Panel

以及未来所有系统消息模块。

所有新建消息功能默认遵循本规范。

### 15.18 Notification Generation Principle（消息生成原则）

#### 15.18.1 设计目标

Notification Generation Principle 用于统一 GTMS 消息提醒生成机制。

所有 Notification 必须遵循：

- 唯一生成入口（Single Entry）
- 幂等（Idempotent）
- 去重（Deduplication）
- 单一职责（Single Responsibility）
- 可扩展（Extensible）

任何模块不得绕过本规范直接生成 Notification。

---

#### 15.18.2 适用范围

本原则适用于：

- NotificationService
- APScheduler
- Notification Router
- Desktop Notification Service
- Dashboard
- Message Panel
- Future Email / SMS / Webhook / Push

---

#### 15.18.3 唯一生成入口（Single Entry）

所有 Notification 必须统一由：

NotificationService.generate_notifications()

负责生成。

禁止：

- Router 生成 Notification
- Scheduler 生成 Notification
- View 生成 Notification
- Desktop Service 生成 Notification
- ORM 直接创建 Notification

---

#### 15.18.4 唯一创建入口

所有 Notification 创建必须统一调用：

NotificationService.create_notification()

禁止：

Session.add(Notification)

db.add(Notification)

任何模块直接创建 Notification。

---

#### 15.18.5 Scheduler 解耦原则

APScheduler 仅负责：

定时调用：

NotificationService.generate_notifications(db)

Scheduler：

不得包含任何业务逻辑。

不得判断消息规则。

不得访问业务 ORM。

不得创建 Notification。

---

#### 15.18.6 幂等原则（Idempotent）

NotificationService.generate_notifications()

必须满足幂等。

连续执行任意次数：

不得产生重复 Notification。

重复执行：

系统状态必须保持一致。

---

#### 15.18.7 去重原则（Deduplication）

Notification 是否重复统一由：

NotificationService

负责判断。

建议唯一判定条件：

- user_id
- notification_type
- target_type
- target_id
- is_read = False

相同条件下：

系统仅允许存在一条未读 Notification。

---

#### 15.18.8 消息规则集中管理

所有提醒规则必须集中位于：

NotificationService。

例如：

- 超时提醒
- 待处理提醒
- 待审核提醒
- 即将到期提醒
- 系统通知

未来新增提醒规则：

仅允许修改 NotificationService。

不得修改：

- Router
- Scheduler
- Desktop Service
- View

---

#### 15.18.9 Notification Service 职责

NotificationService 负责：

- 消息生成
- 消息去重
- 消息创建
- 已读处理
- 批量已读
- 自动生成
- Audit Log

不得负责：

- HTTP
- Router
- View
- Scheduler
- UI
- Push

---

#### 15.18.10 Router 原则

Notification Router：

仅负责：

- 参数接收
- Dependency Injection
- 调用 NotificationService
- 返回结果

不得：

- 生成 Notification
- 判断提醒规则
- 去重
- 写日志

---

#### 15.18.11 Desktop Service 原则

Desktop NotificationService：

仅负责：

HTTP Mapping。

不得：

- 判断提醒规则
- 去重
- 聚合
- Workflow
- Status Machine
- Business Logic

---

#### 15.18.12 View 原则

Notification View：

仅负责：

数据显示。

刷新。

分页。

搜索。

标记已读调用。

不得：

生成 Notification。

去重。

聚合。

Workflow。

Status Machine。

---

#### 15.18.13 Audit Logging

Notification 创建、

Notification 已读、

批量已读、

统一调用：

LogService.create_log()

禁止：

Session.add(SystemLog)

禁止：

直接写日志。

---

#### 15.18.14 性能原则

Notification 查询：

必须使用数据库过滤。

分页：

OFFSET / LIMIT。

禁止：

Python 全表遍历。

禁止：

重复查询。

---

#### 15.18.15 测试要求

Notification Service 必须覆盖：

- create_notification()
- generate_notifications()
- mark_as_read()
- mark_all_as_read()
- 去重
- 幂等
- Rollback
- Audit Log
- 回归测试

全部通过后方可 Freeze。

---

#### 15.18.16 Public API Freeze

NotificationService Public API 冻结后：

不得修改：

- 方法名称
- 方法签名
- 返回类型

新增功能：

仅允许新增方法。

不得破坏历史接口。

---

#### 15.18.17 Mini Freeze

完成 Notification Service 后必须执行：

Mini Freeze Review。

确认：

- Notification Principle
- Notification Generation Principle
- Workflow
- Status Machine
- Audit Logging

全部 PASS。

---

#### 15.18.18 Baseline Freeze

Sprint Notification Baseline Freeze 必须确认：

Notification 全链路：

Schema

↓

Service

↓

Router

↓

Scheduler

↓

Desktop Service

↓

View

全部符合规范。

---

#### 15.18.19 可扩展性（Future Extension）

未来支持：

- Message Priority
- Message Category
- Email Notification
- SMS Notification
- Enterprise WeChat
- DingTalk
- Push Notification
- Webhook
- Dashboard Badge
- Real-time Notification

应仅扩展：

NotificationService。

不得修改：

- Router
- Scheduler
- Desktop Service
- View

---

#### 15.18.20 总结

Notification Generation Principle 是 GTMS Notification 模块唯一生成规范。

所有 Notification 必须满足：

- Single Entry
- Idempotent
- Deduplication
- Separation of Concerns
- Extensible
- Audit Logging
- Frozen API

任何违反本原则的实现均不得通过 Mini Freeze Review。

### 15.19 Scheduler Principle（调度器原则）

#### 15.19.1 设计目标

Scheduler Principle 用于统一 GTMS 后台定时任务架构。

所有 Scheduler 必须遵循：

- 调度与业务解耦（Decoupling）
- Service 唯一业务入口（Single Entry）
- 幂等执行（Idempotent）
- 可重复运行（Repeatable）
- 可扩展（Extensible）

Scheduler 不属于业务层。

---

#### 15.19.2 适用范围

本原则适用于：

- APScheduler
- Cron Job
- Background Task
- Celery（未来）
- 定时消息提醒
- 自动维护任务
- 自动统计任务
- 自动清理任务

---

#### 15.19.3 Scheduler 唯一职责

Scheduler 仅负责：

- 定时触发
- 调用 Service
- 输出运行日志
- 捕获调度异常

不得负责：

- 业务判断
- Workflow
- Status Machine
- Notification 创建
- ORM 操作
- HTTP 请求

---

#### 15.19.4 Service 唯一业务入口（Single Entry）

所有 Scheduler 必须统一调用：

Service。

例如：

NotificationService.generate_notifications()

未来：

StatisticsService.refresh_statistics()

CleanupService.clean_history()

BackupService.create_backup()

Scheduler 不得直接实现业务逻辑。

---

#### 15.19.5 Scheduler 禁止访问业务对象

Scheduler 禁止：

直接操作 ORM。

禁止：

Session.add()

Session.commit()

Session.delete()

禁止：

直接创建：

Notification

TrialTask

Inspection

Dispatch

SystemLog

所有业务操作必须委托对应 Service。

---

#### 15.19.6 幂等原则（Idempotent）

Scheduler 调用的方法必须满足：

Idempotent。

重复执行：

不得产生重复数据。

不得破坏业务状态。

不得产生重复 Notification。

系统状态必须保持一致。

---

#### 15.19.7 重复执行原则

Scheduler 必须允许：

重复启动。

重复运行。

服务重启。

异常恢复。

不得依赖：

单次执行成功。

必须保证：

任意次数运行均安全。

---

#### 15.19.8 Transaction 原则

所有数据库事务：

统一由：

Service

负责。

Scheduler：

不得：

commit()

rollback()

不得控制事务。

---

#### 15.19.9 Audit Logging

Scheduler 本身：

不得写业务日志。

业务日志：

统一由：

LogService.create_log()

负责。

Scheduler 可记录：

启动。

结束。

运行耗时。

异常。

不得记录业务行为。

---

#### 15.19.10 Exception 原则

Scheduler：

统一捕获调度异常。

记录运行日志。

不得影响下一次调度。

业务异常：

由对应 Service 抛出。

不得隐藏异常。

---

#### 15.19.11 Performance Principle

Scheduler：

不得进行：

Python 全表扫描。

不得重复查询。

所有数据过滤：

必须交由数据库完成。

Service：

负责：

分页。

过滤。

聚合。

---

#### 15.19.12 Scheduler Independence

Scheduler：

不得依赖：

Router。

View。

Desktop Service。

ApiClient。

HTTP。

WebSocket。

Scheduler 应可独立运行。

---

#### 15.19.13 Future Extension

未来支持：

- 多 Scheduler
- 多线程
- 多进程
- Celery
- RabbitMQ
- Redis Queue
- Kubernetes CronJob

不得修改：

业务 Service。

仅允许替换 Scheduler 实现。

---

#### 15.19.14 Testing

Scheduler 必须覆盖：

- 正常执行
- 重复执行
- 幂等验证
- 异常恢复
- 调度成功
- 调度失败
- Service 调用
- 回归测试

全部通过后方可 Freeze。

---

#### 15.19.15 Public API Freeze

Scheduler Public API 冻结后：

不得修改：

- 方法名称
- 方法签名
- 调度入口

新增能力：

仅允许新增调度任务。

不得破坏历史接口。

---

#### 15.19.16 Mini Freeze

完成 Scheduler 后必须执行：

Mini Freeze Review。

确认：

- Scheduler Principle
- Notification Principle
- Notification Generation Principle
- Workflow
- Status Machine

全部 PASS。

---

#### 15.19.17 Baseline Freeze

Sprint Scheduler Baseline Freeze 必须确认：

Scheduler

↓

Service

↓

ORM

↓

Database

调用链完整。

业务职责清晰。

全部符合规范。

---

#### 15.19.18 推荐架构（Recommended Design）

推荐调用关系：

Scheduler

↓

NotificationService.generate_notifications()

↓

create_notification()

↓

LogService.create_log()

↓

Database Commit

Scheduler 不直接访问数据库。

---

#### 15.19.19 禁止事项

Scheduler 禁止：

- 写业务逻辑
- 修改 Workflow
- 修改 Status Machine
- ORM CRUD
- HTTP 调用
- Router 调用
- View 调用
- Desktop Service 调用
- Notification 去重
- Notification 创建
- Business Aggregation

以上均属于 Service 职责。

---

#### 15.19.20 总结

Scheduler Principle 是 GTMS 后台调度唯一规范。

所有 Scheduler 必须满足：

- Single Entry
- Decoupling
- Idempotent
- Repeatable
- Transaction by Service
- Audit Logging
- Frozen API
- Future Extensible

任何违反本原则的实现均不得通过 Mini Freeze Review。

### 15.20 Desktop HTTP Mapping Principle（桌面端 HTTP 映射原则）

#### 15.20.1 设计目标

Desktop HTTP Mapping Principle 用于统一 GTMS 桌面端 Service 层架构。

所有 Desktop Service 必须遵循：

- HTTP Mapping
- Zero Business Logic
- Zero Workflow
- Zero Status Machine
- Thin Client
- Single Responsibility

Desktop Service 属于客户端基础设施层（Infrastructure）。

---

#### 15.20.2 适用范围

本原则适用于所有 Desktop Service，包括但不限于：

- TaskService
- CustomerService
- ReceiptService
- GrindingService
- InspectionService
- DispatchService
- QueryService
- LogService
- NotificationService

未来新增 Desktop Service 必须遵循本原则。

---

#### 15.20.3 唯一职责（Single Responsibility）

Desktop Service 仅负责：

- HTTP 请求
- HTTP 参数映射
- HTTP Body 映射
- HTTP Response 返回
- Logger 输出

不得负责：

- 业务逻辑
- Workflow
- Status Machine
- Aggregation
- Notification Generation
- 数据计算
- 数据统计
- 数据转换

所有业务逻辑统一由 Server Service 完成。

---

#### 15.20.4 HTTP Mapping

Desktop Service 必须与对应 Router 保持 100% 一一对应。

每一个 Public API：

对应一个 HTTP Endpoint。

不得：

- 合并多个 Endpoint
- 拆分一个 Endpoint
- 修改 Endpoint
- 修改 HTTP Method

保持客户端与服务端接口一致。

---

#### 15.20.5 Dependency Principle

Desktop Service 仅允许依赖：

- ApiClient
- Logger
- Schema（如需要）

禁止依赖：

- FastAPI
- Router
- SQLAlchemy
- ORM
- Session
- Scheduler
- Server Service
- View

Desktop Service 不得访问数据库。

---

#### 15.20.6 Query Rules

GET 请求：

仅提交非 None 字段。

不得发送：

- None
- 空字段
- 无意义参数

Query 参数应自动过滤。

---

#### 15.20.7 Body Rules

POST、PUT、PATCH 请求：

仅提交非 None 字段。

Body 中不得包含：

- None
- 未修改字段
- 无意义字段

Body 自动过滤空值。

---

#### 15.20.8 Return Rules

所有 Public API 必须统一返回：

resp.json()

不得：

- 包装 Response
- 转换数据结构
- 二次解析
- 构造 DTO

保持返回数据与 Server Response 完全一致。

---

#### 15.20.9 Exception Principle

Desktop Service：

不得使用：

try/except

所有异常统一由：

ApiClient

原样抛出。

异常处理属于上层（View）。

---

#### 15.20.10 Logging Principle

统一使用：

logger.debug()

Logger 名称统一：

gtms.client

禁止：

- print()
- traceback.print_exc()

仅记录：

- HTTP 请求
- HTTP 返回
- 调试信息

不得记录业务日志。

---

#### 15.20.11 Workflow Principle

Desktop Service：

不得包含：

Workflow。

不得引用：

- TrialTaskProcessStatus
- Workflow 判断
- 流程控制

所有 Workflow 统一由 Server Service 完成。

---

#### 15.20.12 Status Machine Principle

Desktop Service：

不得包含：

Status Machine。

不得修改：

- process_status
- result_status

状态流转统一由 Server Service 完成。

---

#### 15.20.13 Business Logic Principle

Desktop Service：

不得实现：

- CRUD 判断
- 权限判断
- Notification Generation
- Aggregation
- Validation
- Transaction
- Audit Logging

Desktop Service 必须保持无业务逻辑。

---

#### 15.20.14 Aggregation Principle

Desktop Service：

不得进行：

- sum()
- sorted()
- groupby()
- Counter()
- Top N
- Ranking
- Statistics

所有聚合统计统一由 Server Service 完成。

---

#### 15.20.15 Testing

Desktop Service 必须覆盖：

- HTTP Mapping
- Query Rules
- Body Rules
- Return Rules
- Public API
- Logger
- Zero Business Logic
- 回归测试

全部测试通过后方可 Freeze。

---

#### 15.20.16 Public API Freeze

Desktop Service Public API 冻结后：

不得修改：

- 方法名称
- 方法签名
- HTTP Mapping
- 返回结构

新增功能：

仅允许新增 Public API。

不得破坏历史接口。

---

#### 15.20.17 Mini Freeze

完成 Desktop Service 后必须执行：

Mini Freeze Review。

确认：

- HTTP Mapping
- Workflow
- Status Machine
- Business Logic
- Frozen API

全部 PASS。

---

#### 15.20.18 Baseline Freeze

Desktop Service Baseline Freeze 必须确认：

Desktop Service

↓

ApiClient

↓

Router

↓

Server Service

↓

Database

调用链完整。

职责清晰。

无重复实现。

---

#### 15.20.19 Recommended Design

推荐架构：

View

↓

Desktop Service

↓

ApiClient

↓

Router

↓

Server Service

↓

Database

Desktop Service 不得直接访问：

- Router
- Database
- ORM
- Scheduler

---

#### 15.20.20 禁止事项

Desktop Service 禁止：

- Business Logic
- Workflow
- Status Machine
- ORM
- SQLAlchemy
- Scheduler
- Aggregation
- Notification Generation
- Audit Logging
- try/except
- print()

以上均属于 Server Service 或 View 职责。

---

#### 15.20.21 总结

Desktop HTTP Mapping Principle 是 GTMS 桌面端 Service 层唯一规范。

所有 Desktop Service 必须满足：

- Thin Client
- HTTP Mapping
- Zero Business Logic
- Zero Workflow
- Zero Status Machine
- Zero Aggregation
- Return resp.json()
- ApiClient Only
- Frozen API
- Future Extensible

任何违反本原则的实现均不得通过 Mini Freeze Review。

---

## 16. V1.0 开发计划

| 阶段 | 模块 | 状态 | 关键产出 |
|------|------|:--:|------|
| 1 | 项目初始化 | ☐ | 目录结构、配置、依赖 |
| 2 | 数据库设计 | ☐ | ORM 模型、迁移脚本、种子数据 |
| 3 | 登录与权限 | ☐ | JWT 认证、角色权限校验 |
| 4 | 客户管理 | ☐ | 客户 CRUD 界面与接口 |
| 5 | 试磨任务 | ☐ | 任务创建、编号生成、状态流转 |
| 6 | 收件管理 | ☐ | 收件登记、图片上传 |
| 7 | 试磨管理 | ☐ | 试磨信息填写、状态更新 |
| 8 | 检测管理 | ☐ | 报告上传、检测数据填写 |
| 9 | 工件去向 | ☐ | 去向登记 |
| 10 | 查询统计 | ☐ | 多条件查询、统计报表 |
| 11 | 操作日志 | ☐ | 自动记录变更、日志查询 |
| 12 | 消息提醒 | ☐ | 定时检查、超时提醒 |
| 13 | Windows 打包 | ☐ | PyInstaller 打包 |
| 14 | 微信小程序 | ☐ | UniApp 开发 |

---

## 附录 A：任务编号生成规则

```
格式: YYYYMMDD-N

示例:
  20260701-1  — 2026年7月1日第1个任务
  20260701-2  — 2026年7月1日第2个任务
  20260702-1  — 2026年7月2日第1个任务（跨天重置）
```

## 附录 B：消息提醒定时策略

使用 APScheduler，定时检查：

| 检查项 | 频率 | 条件 |
|------|------|------|
| 收件超时 | 每小时 | process_status=received 超过 48h |
| 试磨超时 | 每小时 | process_status=grinding 超过 120h |
| 报告缺失 | 每小时 | process_status=grinding 且 result_status=pending 超过 72h |

## 附录 C：快速参考卡片

| 项目 | 值 |
|------|------|
| 后端端口 | 8000 |
| API 文档 | http://localhost:8000/docs |
| 开发数据库 | SQLite (`database/gtms.db`) |
| 默认管理员 | admin / admin123 |
| 文件存储 | `uploads/` 目录 |
| 备份目录 | `backup/` |
| JWT 有效期 | 8 小时 |

---

> **文档维护者：** GTMS 开发团队  
> **最后更新：** 2026-07-16  
> **对应版本：** V1.0

---

## 附录 D：Sprint 4 Frozen API

> **Sprint 4 起公开 API 冻结。后续 Sprint 不得修改以下函数签名，只能新增调用。**

### Server 层

| 文件 | 冻结范围 |
|------|----------|
| `server/schemas/customer_schema.py` | `CustomerBase`, `CustomerCreate`, `CustomerUpdate`, `CustomerResponse`, `CustomerListResponse` — 字段与类型不可修改 |
| `server/services/customer_service.py` | `CustomerService.list_customers()`, `get_customer()`, `create_customer()`, `update_customer()` — 函数签名不可修改 |
| `server/routers/customer_router.py` | `GET/POST/PUT /api/customers` — 路由路径、Query 参数、Body Schema 不可修改 |

### Desktop 层

| 文件 | 冻结范围 |
|------|----------|
| `client/services/customer_service.py` | `CustomerService.list_customers()`, `get_customer()`, `create_customer()`, `update_customer()` — 函数签名不可修改 |
| `client/views/customer_view.py` | `CustomerView.refresh()`, `customer_changed` Signal — 公开 API 不可修改 |
| `client/views/customer_edit_dialog.py` | `CustomerEditDialog.get_result()` — 公开 API 不可修改 |

### 冻结约束

- **禁止修改**：已冻结的函数签名、字段名、字段类型、路由路径、Query 参数、Body Schema
- **允许新增**：内部私有方法、日志输出、新增调用已冻结 API
- **禁止删除**：Customer 不提供 DELETE 接口，不提供 `customer:delete` 权限