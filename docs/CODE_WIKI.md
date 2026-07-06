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
| task_no | String(20) | UNIQUE, NOT NULL | 任务编号 (TM202600001) |
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
| `customer_view.py` | `CustomerView` | 客户增删改查、列表展示 |
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

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/customers` | 客户列表（分页+搜索） | 登录用户 |
| POST | `/api/customers` | 新增客户 | 销售 / 管理员 |
| GET | `/api/customers/{id}` | 客户详情 | 登录用户 |
| PUT | `/api/customers/{id}` | 更新客户 | 销售 / 管理员 |
| DELETE | `/api/customers/{id}` | 删除客户 | 管理员 |

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

### 13.3 权限清单（20项）

| 权限码 | 名称 | 模块 |
|------|------|------|
| task:create | 创建任务 | task |
| task:view | 查看任务 | task |
| task:edit | 编辑任务 | task |
| task:delete | 删除任务 | task |
| customer:create | 创建客户 | customer |
| customer:view | 查看客户 | customer |
| customer:edit | 编辑客户 | customer |
| customer:delete | 删除客户 | customer |
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
> **最后更新：** 2026-07-02  
> **对应版本：** V1.0