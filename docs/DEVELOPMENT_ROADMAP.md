# GTMS — 开发路线图 (Development Roadmap)

> **Grinding Trial Management System V1.0**  
> 首席架构师签发 | 日期：2026-07-02 | 状态：已确认  
> 参考文档：SRS v1.0 / DB_DESIGN v1.0 / UI_PROTOTYPE v1.0 / CODE_WIKI v1.0

---

## 目录

1. [总览](#1-总览)
2. [阶段 1：项目初始化](#2-阶段-1项目初始化)
3. [阶段 2：数据库设计](#3-阶段-2数据库设计)
4. [阶段 3：后端核心框架](#4-阶段-3后端核心框架)
5. [阶段 4：登录与权限](#5-阶段-4登录与权限)
6. [阶段 5：客户管理](#6-阶段-5客户管理)
7. [阶段 6：试磨任务](#7-阶段-6试磨任务)
8. [阶段 7：收件管理](#8-阶段-7收件管理)
9. [阶段 8：试磨管理](#9-阶段-8试磨管理)
10. [阶段 9：检测管理](#10-阶段-9检测管理)
11. [阶段 10：工件去向](#11-阶段-10工件去向)
12. [阶段 11：查询统计](#12-阶段-11查询统计)
13. [阶段 12：操作日志](#13-阶段-12操作日志)
14. [阶段 13：消息提醒](#14-阶段-13消息提醒)
15. [阶段 14：系统设置与备份](#15-阶段-14系统设置与备份)
16. [阶段 15：联调测试](#16-阶段-15联调测试)
17. [阶段 16：Windows 打包](#17-阶段-16windows-打包)
18. [阶段 17：微信小程序](#18-阶段-17微信小程序)
19. [阶段 18：部署上线](#19-阶段-18部署上线)
20. [附录：依赖关系图](#附录依赖关系图)

---

## 1. 总览

### 1.1 开发阶段总览

```
阶段 1 ──► 阶段 2 ──► 阶段 3 ──┬──► 阶段 4 ──► 阶段 5
                                │
                                ├──► 阶段 6 ──► 阶段 7 ──► 阶段 8 ──► 阶段 9 ──► 阶段 10
                                │
                                └──► 阶段 11 ──► 阶段 12 ──► 阶段 13 ──► 阶段 14

                                全体 ──► 阶段 15 ──► 阶段 16 ──► 阶段 17 ──► 阶段 18
```

### 1.2 阶段信息总表

| # | 阶段名称 | 工时(人天) | 优先级 | 前置依赖 | 产出物 |
|---|------|:--:|:--:|------|------|
| 1 | 项目初始化 | 1 | P0 | — | 目录结构、配置、依赖 |
| 2 | 数据库设计 | 2 | P0 | 阶段1 | ORM模型、DDL、种子数据 |
| 3 | 后端核心框架 | 2 | P0 | 阶段2 | FastAPI骨架、中间件、异常体系 |
| 4 | 登录与权限 | 3 | P0 | 阶段3 | JWT认证、RBAC权限系统、登录页、角色权限管理 |
| 5 | 客户管理 | 2 | P1 | 阶段4 | 客户CRUD (前后端) |
| 6 | 试磨任务 | 4 | P0 | 阶段5 | 任务CRUD、编号生成、状态流转 |
| 7 | 收件管理 | 2 | P1 | 阶段6 | 收件登记、图片上传 |
| 8 | 试磨管理 | 3 | P1 | 阶段7 | 试磨登记、状态流转、失败处理 |
| 9 | 检测管理 | 2 | P1 | 阶段8 | 报告上传、检测结果 |
| 10 | 工件去向 | 1 | P2 | 阶段9 | 去向登记 |
| 11 | 查询统计 | 2 | P1 | 阶段6 | 多条件查询、统计报表 |
| 12 | 操作日志 | 1.5 | P1 | 阶段6 | 自动记录、日志查询 |
| 13 | 消息提醒 | 1.5 | P2 | 阶段8 | 超时提醒、消息面板 |
| 14 | 系统设置与备份 | 1.5 | P2 | 阶段3 | 设置页、自动备份 |
| 15 | 联调测试 | 3 | P0 | 阶段1-14 | 全流程测试、Bug修复 |
| 16 | Windows打包 | 1 | P1 | 阶段15 | PyInstaller exe |
| 17 | 微信小程序 | 5 | P2 | 阶段15 | UniApp 小程序 |
| 18 | 部署上线 | 2 | P1 | 阶段16 | 生产环境部署 |

> **总工时估算：约 39.5 人天**（单开发者约 8 周，2 人团队约 4 周）

---

## 2. 阶段 1：项目初始化

### 2.1 参考文档

| 文档 | 对应章节 |
|------|------|
| CODE_WIKI | §2 项目目录结构、§4 技术栈与依赖 |
| SRS | §2.3 假设与约束 |

### 2.2 任务清单

| # | 任务 | 产出物 | 验收标准 |
|---|------|------|------|
| 1.1 | 创建项目目录结构 | 完整目录树（见 CODE_WIKI §2） | 所有目录存在，含 `.gitkeep` |
| 1.2 | 初始化 Git 仓库 | `.gitignore` | 忽略 `venv/`、`__pycache__/`、`*.db`、`uploads/`、`backup/` |
| 1.3 | 创建 `requirements.txt` | 依赖清单（见 CODE_WIKI §4.2） | `pip install -r requirements.txt` 成功 |
| 1.4 | 创建虚拟环境 + 安装依赖 | `venv/` | 所有包安装无报错 |
| 1.5 | 创建 `server/config.py` | 配置类 | 含 DATABASE_URL、SECRET_KEY、UPLOAD_DIR 等 |
| 1.6 | 创建 `client/config.py` | 客户端配置 | 含 API_BASE_URL、PAGE_SIZE 等 |
| 1.7 | 创建 `README.md` | 项目说明 | 含项目简介、快速启动 |

### 2.3 产出文件清单

```
data_control/
├── .gitignore                  # 1.2
├── README.md                   # 1.7
├── requirements.txt            # 1.3
├── client/
│   └── config.py               # 1.6
├── server/
│   └── config.py               # 1.5
├── database/
├── miniapp/
├── docs/
│   ├── SRS.md
│   ├── DB_DESIGN.md
│   ├── UI_PROTOTYPE.md
│   ├── CODE_WIKI.md
│   └── DEVELOPMENT_ROADMAP.md
├── uploads/
│   ├── images/
│   ├── reports/
│   ├── cad/
│   └── videos/
└── backup/
```

---

## 3. 阶段 2：数据库设计

### 3.1 参考文档

| 文档 | 对应章节 |
|------|------|
| DB_DESIGN | §3 完整 DDL 语句、§4 表结构详述、§5 索引设计、§6 关系与外键 |
| SRS | §6 数据字典、§7 状态机定义 |
| CODE_WIKI | §5 数据库设计 |

### 3.2 任务清单

| # | 任务 | 产出物 | 对应DB章节 |
|---|------|------|------|
| 2.1 | 创建 `server/models/base.py` | Base 类、engine、SessionLocal、get_db() | DB §4 |
| 2.2 | 创建 `server/models/user.py` | User ORM 模型 | DB §4.1 |
| 2.3 | 创建 `server/models/customer.py` | Customer ORM 模型 | DB §4.2 |
| 2.4 | 创建 `server/models/trial_task.py` | TrialTask + 流程/结果/去向枚举 | DB §4.4 |
| 2.5 | 创建 `server/models/receipt.py` | Receipt ORM 模型 | DB §4.4 |
| 2.6 | 创建 `server/models/grinding.py` | GrindingRecord ORM 模型 | DB §4.5 |
| 2.7 | 创建 `server/models/inspection.py` | InspectionRecord ORM 模型 | DB §4.6 |
| 2.8 | 创建 `server/models/dispatch.py` | Dispatch ORM 模型 | DB §4.7 |
| 2.9 | 创建 `server/models/attachment.py` | Attachment + FileType 枚举 | DB §4.8 |
| 2.10 | 创建 `server/models/system_log.py` | SystemLog + ActionType 枚举 | DB §4.9 |
| 2.11 | 创建 `server/models/notification.py` | Notification + NotifyType 枚举 | DB §4.10 |
| 2.12 | 创建 `server/models/__init__.py` | 统一导出所有模型 | — |
| 2.13 | 创建 `database/seed_data.py` | 种子数据脚本 | DB §8 |
| 2.14 | 初始化 Alembic | `database/migrations/` | DB §9 |
| 2.15 | 生成初始迁移并执行 | 迁移脚本 | `alembic upgrade head` 成功 |

### 2.3 验收标准

- [ ] 执行 `Base.metadata.create_all(bind=engine)` 后 14 张表全部创建
- [ ] 所有枚举值正确（TrialTaskProcessStatus 5 种 + TrialTaskResultStatus 3 种 + DestinationType 5 种 + FileType 4 种 等）
- [ ] 运行 `seed_data.py` 后默认用户可登录（admin/admin123）
- [ ] 所有外键关系正确建立
- [ ] 所有索引正确建立（43 个）

---

## 4. 阶段 3：后端核心框架

### 4.1 参考文档

| 文档 | 对应章节 |
|------|------|
| CODE_WIKI | §6.1 入口文件、§6.2 核心模块、§6.6 工具模块 |
| SRS | §5.2 安全性需求 |

### 4.2 任务清单

| # | 任务 | 产出物 | 说明 |
|---|------|------|------|
| 3.1 | 创建 `server/core/exceptions.py` | 4 个自定义异常类 | NotFoundException、PermissionDeniedException、BusinessLogicException、DuplicateException |
| 3.2 | 创建 `server/core/security.py` | SecurityManager + PermissionChecker | JWT 生成/验证、bcrypt 密码哈希、ROLE_PERMISSIONS 映射 |
| 3.3 | 创建 `server/core/dependencies.py` | get_current_user()、require_role() | 依赖注入函数 |
| 3.4 | 创建 `server/utils/id_generator.py` | TaskNumberGenerator | TM202600001 格式 |
| 3.5 | 创建 `server/utils/file_handler.py` | FileHandler | 文件校验、存储、命名 |
| 3.6 | 创建 `server/middleware/cors_middleware.py` | setup_cors() | 跨域配置 |
| 3.7 | 创建 `server/middleware/log_middleware.py` | LogMiddleware | 请求日志中间件 |
| 3.8 | 创建 `server/main.py` | FastAPI 应用工厂 | 注册所有中间件和路由（路由先为空占位） |
| 3.9 | 创建异常处理器 | 全局异常处理 | 捕获自定义异常，返回统一格式 `{code, message, detail}` |

### 4.3 验收标准

- [ ] `uvicorn server.main:app` 启动成功
- [ ] 访问 `http://localhost:8000/docs` 显示 Swagger 文档
- [ ] 异常处理生效（404/403/400/409 返回统一格式）
- [ ] CORS 配置正确

---

## 5. 阶段 4：登录与权限

### 5.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.1 FR-AUTH 认证模块、§3.2 UC-01 用户登录 |
| UI_PROTOTYPE | §2 登录页、§3 主窗口框架、§14 用户管理页 |
| CODE_WIKI | §6.2.1 security.py、§6.2.2 dependencies.py、§13 权限模型 |

### 5.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 4.1 | 创建 `server/schemas/user_schema.py` | UserCreate、UserUpdate、UserResponse、LoginRequest、TokenResponse |
| 4.2 | 创建 `server/services/auth_service.py` | AuthService：login()、get_current_user()、change_password() |
| 4.3 | 创建 `server/routers/auth_router.py` | POST /api/auth/login、GET /api/auth/me、POST /api/auth/change-password |
| 4.4a | 创建 `server/models/role.py` | Role 模型 |
| 4.4b | 创建 `server/models/permission.py` | Permission 模型 |
| 4.4c | 创建 `server/services/user_service.py` | UserService：CRUD、enable/disable、角色分配 |
| 4.5 | 创建 `server/routers/user_router.py` | GET/POST/PUT/DELETE /api/users |
| 4.5a | 创建 `server/routers/role_router.py` | 角色 CRUD + 权限分配接口 |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 4.6 | 创建 `client/services/api_client.py` | ApiClient 类（get/post/put/delete，Bearer Token 注入） |
| 4.7 | 创建 `client/services/auth_service.py` | 封装 login()、get_me()、change_password() |
| 4.8 | 创建 `client/views/login_view.py` | LoginView 对话框（见 UI §2） |
| 4.9 | 创建 `client/views/main_window.py` | MainWindow 主窗口框架（见 UI §3）：侧边栏导航 + 标题栏 + 状态栏 + 权限过滤 |
| 4.10 | 创建 `client/main.py` | 应用入口 |
| 4.11 | 创建 `client/views/user_manage_view.py` | UserManageView 用户管理（见 UI §14） |

### 5.3 验收标准

- [ ] 对照 SRS AC-01：正确账号可登录，错误账号被拒绝，禁用账号被拒绝
- [ ] 对照 SRS AC-02：销售不能看到技术员专属菜单，非管理员不能访问用户管理
- [ ] 登录后 JWT Token 存储，后续请求自动携带
- [ ] 8 小时 Token 过期后自动跳转登录页
- [ ] 用户管理页：新增/编辑/禁用/启用用户功能正常
- [ ] RBAC 权限模型：用户→角色→权限三层关联正确
- [ ] 20 个权限码全部定义，管理员可分配权限给角色
- [ ] 无权限的操作返回 403，无权限菜单不可见
- [ ] 系统角色不可删除

---

## 6. 阶段 5：客户管理

### 6.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.2 FR-CUSTOMER 客户管理模块 |
| UI_PROTOTYPE | §5 客户管理页 |
| CODE_WIKI | §6.5 客户路由、§7.2 客户界面 |

### 6.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 5.1 | 创建 `server/schemas/customer_schema.py` | CustomerCreate、CustomerUpdate、CustomerResponse |
| 5.2 | 创建 `server/services/customer_service.py` | CustomerService：CRUD、搜索、分页 |
| 5.3 | 创建 `server/routers/customer_router.py` | GET/POST/PUT/DELETE /api/customers |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 5.4 | 创建 `client/services/customer_service.py` | 封装客户 API 调用 |
| 5.5 | 创建 `client/views/customer_view.py` | CustomerView（见 UI §5）：列表 + 搜索 + 新增/编辑弹窗 + 删除确认 |

### 6.3 验收标准

- [ ] 对照 SRS FR-CUSTOMER-01：列表分页正常，搜索正常
- [ ] 对照 SRS FR-CUSTOMER-02：新增客户校验：公司名称必填、不重复
- [ ] 对照 SRS FR-CUSTOMER-04：有任务关联的客户删除时提示"无法删除"
- [ ] 对照 UI §5.2：弹窗字段与原型一致

---

## 7. 阶段 6：试磨任务

### 7.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.3 FR-TASK 试磨任务模块、§7 状态机定义、§8 业务规则 BR-01/02/03 |
| UI_PROTOTYPE | §6 任务列表页、§7 任务创建/编辑页、§8 任务详情页 |
| CODE_WIKI | §6.3.2 trial_task.py、§6.4.1 task_service.py、§6.5.1 trial_task_router.py |
| DB_DESIGN | §4.3 trial_tasks 表 |

### 7.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 6.1 | 创建 `server/schemas/trial_task_schema.py` | TaskCreate、TaskUpdate、TaskResponse、TaskListResponse、TaskProcessStatusUpdate |
| 6.2 | 创建 `server/services/task_service.py` | TaskService：create_task()、update_task()、delete_task()、get_task_detail()、get_task_list()、update_task_status()、get_dashboard_stats() |
| 6.3 | 创建 `server/routers/trial_task_router.py` | GET/POST/PUT/DELETE /api/tasks、PUT /api/tasks/{id}/status |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 6.4 | 创建 `client/services/task_service.py` | 封装任务 API 调用 |
| 6.5 | 创建 `client/widgets/status_badge.py` | StatusBadge 组件（见 UI §19 颜色映射） |
| 6.6 | 创建 `client/widgets/search_bar.py` | SearchBar 组件（见 UI §6.2 筛选条件） |
| 6.7 | 创建 `client/views/trial_task_view.py` | TrialTaskView 任务列表（见 UI §6）：筛选栏 + 列表 + 分页 + 按状态显示操作按钮 |
| 6.8 | 创建任务创建/编辑弹窗 | 表单（见 UI §7）：客户选择、加工要求、快递单号、自动编号 |
| 6.9 | 创建 `client/views/task_detail_view.py` | 任务详情页（见 UI §8）：7 个区块按状态条件显示 |

### 7.3 验收标准

- [ ] 对照 SRS AC-03：任务编号自动生成且唯一（TM202600001 格式），process_status 初始化为 created
- [ ] 对照 SRS AC-04：非法状态流转被拒绝（如从 created 直接跳到 grinding）
- [ ] 对照 SRS BR-03：仅 process_status=created 状态可编辑基本信息
- [ ] 对照 UI §6.3：列表操作按钮按状态正确显示
- [ ] 对照 UI §8.2：任务详情各区块按状态条件正确显示/隐藏
- [ ] 任务编号每年重置

---

## 8. 阶段 7：收件管理

### 8.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.4 FR-RECEIPT 收件管理模块、§3.2 UC-05 收件登记 |
| UI_PROTOTYPE | §9 收件登记页 |
| DB_DESIGN | §4.4 receipts 表 |

### 8.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 7.1 | 创建 `server/schemas/receipt_schema.py` | ReceiptCreate、ReceiptResponse |
| 7.2 | 创建 `server/services/receipt_service.py` | ReceiptService：create_receipt()、get_receipt() |
| 7.3 | 创建 `server/routers/receipt_router.py` | POST /api/receipts、GET /api/receipts/{task_id} |
| 7.4 | 创建 `server/routers/upload_router.py` | POST /api/upload/image、POST /api/upload/report、POST /api/upload/cad、GET /api/upload/{file_path} |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 7.5 | 创建 `client/services/receipt_service.py` | 封装收件 API 调用 |
| 7.6 | 创建 `client/widgets/file_uploader.py` | FileUploader 组件（见 UI §18.3）：拖拽/点击上传、预览、删除、类型校验 |
| 7.7 | 创建 `client/widgets/image_viewer.py` | ImageViewer 组件（见 UI §18.3）：缩放、旋转、翻页 |
| 7.8 | 创建 `client/views/receipt_view.py` | ReceiptView 收件登记（见 UI §9）：日期选择 + 图片上传 + 提交 |

### 8.3 验收标准

- [ ] 对照 SRS AC-05：图片上传成功（至少1张），process_status 更新为 received
- [ ] 对照 SRS FR-RECEIPT-01：不上传图片时提示"请至少上传一张工件照片"
- [ ] 图片命名规则：`{task_no}_receipt_{timestamp}.jpg`
- [ ] 图片存储在 `uploads/images/` 目录
- [ ] 图片类型校验：仅允许 jpg/png

---

## 9. 阶段 8：试磨管理

### 9.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.5 FR-GRINDING 试磨管理模块、§3.2 UC-06/07 开始/完成试磨 |
| UI_PROTOTYPE | §10 试磨管理页 |
| DB_DESIGN | §4.5 grinding_records 表 |

### 9.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 8.1 | 创建 `server/schemas/grinding_schema.py` | GrindingStart、GrindingComplete、GrindingResponse |
| 8.2 | 创建 `server/services/grinding_service.py` | GrindingService：start_grinding()、complete_grinding()、get_grinding() |
| 8.3 | 创建 `server/routers/grinding_router.py` | POST /api/grinding/start、POST /api/grinding/complete、GET /api/grinding/{task_id} |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 8.4 | 创建 `client/services/grinding_service.py` | 封装试磨 API 调用 |
| 8.5 | 创建 `client/views/grinding_view.py` | GrindingView（见 UI §10.1 + §10.2）：开始试磨表单 + 完成试磨表单，含成功/失败切换、失败原因条件显示 |

### 9.3 验收标准

- [ ] 对照 SRS AC-06：责任人、机型、参数正确保存，process_status 和 result_status 正确流转
- [ ] 对照 SRS FR-GRINDING-02：选择"成功" → result_status 变为 passed；选择"失败" → result_status 变为 failed，failure_reason 必填
- [ ] 对照 UI §10.3：选择"失败"时显示失败原因输入框，选择"成功"时隐藏
- [ ] 仅 process_status=grinding 状态可完成试磨

---

## 10. 阶段 9：检测管理

### 10.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.6 FR-INSPECTION 检测管理模块、§3.2 UC-08 上传检测报告 |
| UI_PROTOTYPE | §11 检测报告页 |
| DB_DESIGN | §4.6 inspection_records 表 |

### 10.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 9.1 | 创建 `server/schemas/inspection_schema.py` | InspectionCreate、InspectionResponse |
| 9.2 | 创建 `server/services/inspection_service.py` | InspectionService：upload_report()、get_inspection() |
| 9.3 | 创建 `server/routers/inspection_router.py` | POST /api/inspections、GET /api/inspections/{task_id} |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 9.4 | 创建 `client/services/inspection_service.py` | 封装检测 API 调用 |
| 9.5 | 创建 `client/views/inspection_view.py` | InspectionView（见 UI §11）：报告上传 + 精度/粗糙度 + 合格/不合格 |

### 10.3 验收标准

- [ ] 对照 SRS AC-07：文件上传成功，支持 PDF/Word/Excel 格式，result_status 正确更新
- [ ] 对照 SRS FR-INSPECTION-01：合格 → result_status 变为 passed；不合格 → result_status 变为 failed，failure_reason 必填
- [ ] 文件类型校验：仅允许 pdf/docx/xlsx
- [ ] 文件大小校验：不超过 50MB

---

## 11. 阶段 10：工件去向

### 11.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.7 FR-DISPATCH 工件去向模块 |
| UI_PROTOTYPE | §12 工件去向页 |
| DB_DESIGN | §4.7 dispatches 表 |

### 11.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 10.1 | 创建 `server/schemas/dispatch_schema.py` | DispatchCreate、DispatchResponse |
| 10.2 | 创建 `server/services/dispatch_service.py` | DispatchService：create_dispatch()、get_dispatch() |
| 10.3 | 创建 `server/routers/dispatch_router.py` | POST /api/dispatches、GET /api/dispatches/{task_id} |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 10.4 | 创建 `client/services/dispatch_service.py` | 封装去向 API 调用 |
| 10.5 | 创建 `client/views/dispatch_view.py` | DispatchView（见 UI §12）：去向选择（寄回/留存/报废/其他）+ 日期 |

### 11.3 验收标准

- [ ] 对照 SRS AC-08：仅 result_status=passed 且 process_status=grinding 时可填写去向，填写后 process_status 变为 dispatched
- [ ] 去向和日期正确保存
- [ ] 填写后任务结束，不再显示操作按钮

---

## 12. 阶段 11：查询统计

### 12.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.8 FR-QUERY 查询统计模块 |
| UI_PROTOTYPE | §13 查询统计页 |
| CODE_WIKI | §6.4.1 task_service.py get_dashboard_stats() |

### 12.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 11.1 | 创建 `server/schemas/query_schema.py` | QueryFilter、StatisticsResponse、DashboardResponse |
| 11.2 | 创建 `server/services/query_service.py` | QueryService：search_tasks()、get_statistics()、get_dashboard() |
| 11.3 | 创建 `server/routers/query_router.py` | GET /api/query/statistics、GET /api/query/dashboard、GET /api/query/search |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 11.4 | 创建 `client/services/query_service.py` | 封装查询统计 API 调用 |
| 11.5 | 创建 `client/views/query_view.py` | QueryView（见 UI §13.1 + §13.2）：查询页 + 统计页（Tab 切换），含简易柱状图 |

### 12.3 验收标准

- [ ] 对照 SRS AC-09：支持按客户、状态、日期、责任人、机型组合查询
- [ ] 对照 SRS AC-10：统计数据显示：本月/年度数量、成功率、客户排行、机型排行
- [ ] 查询结果支持分页、导出 Excel
- [ ] 统计图表正确渲染

---

## 13. 阶段 12：操作日志

### 13.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.10 FR-LOG 操作日志模块 |
| UI_PROTOTYPE | §15 操作日志页 |
| DB_DESIGN | §4.9 system_logs 表 |
| CODE_WIKI | §6.4.3 log_service.py |

### 13.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 12.1 | 创建 `server/schemas/log_schema.py` | LogResponse、LogFilter |
| 12.2 | 创建 `server/services/log_service.py` | LogService：log_action()、get_logs() |
| 12.3 | 创建 `server/routers/log_router.py` | GET /api/logs |
| 12.4 | 集成到现有 Service | 在 TaskService、ReceiptService、GrindingService 等关键操作中注入 LogService.log_action() |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 12.5 | 创建 `client/services/log_service.py` | 封装日志 API 调用 |
| 12.6 | 创建 `client/views/system_log_view.py` | SystemLogView（见 UI §15）：筛选栏 + 日志列表 + 分页 |

### 13.3 验收标准

- [ ] 对照 SRS AC-11：所有修改操作自动记录，含操作人、时间、操作类型、变更内容
- [ ] 对照 SRS BR-11：日志不可删除
- [ ] 日志查询支持按操作人、操作类型、时间范围筛选
- [ ] 任务详情页底部时间线正确展示操作日志

---

## 14. 阶段 13：消息提醒

### 14.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §4.9 FR-NOTIFICATION 消息提醒模块、§10.3 消息提醒触发规则 |
| UI_PROTOTYPE | §4.3 消息面板、§17.7 消息通知页 |
| DB_DESIGN | §4.10 notifications 表 |
| CODE_WIKI | §6.4.2 notification_service.py |

### 14.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 13.1 | 创建 `server/schemas/notification_schema.py` | NotificationResponse |
| 13.2 | 创建 `server/services/notification_service.py` | NotificationService：check_and_notify()、get_unread()、mark_as_read() |
| 13.3 | 创建 `server/routers/notification_router.py` | GET /api/notifications、PUT /api/notifications/{id}/read |
| 13.4 | 配置 APScheduler 定时任务 | 每小时执行 check_and_notify() |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 13.5 | 创建 `client/services/notification_service.py` | 封装消息 API 调用 |
| 13.6 | 集成到仪表盘 | 在 DashboardView 右侧消息面板展示未读消息（见 UI §4.3） |
| 13.7 | 集成到标题栏 | 标题栏 🔔 图标显示未读数量角标（见 UI §3.3） |

### 14.3 验收标准

- [ ] 对照 SRS AC-12：超时任务自动生成提醒，已存在未读提醒不重复生成
- [ ] 对照 SRS FR-NOTIFICATION-01 三条规则全部生效
- [ ] 点击消息 → 标记已读 + 跳转任务详情
- [ ] "全部已读"功能正常
- [ ] 对照 SRS BR-13：用户只能看到自己角色的消息

---

## 15. 阶段 14：系统设置与备份

### 15.1 参考文档

| 文档 | 对应章节 |
|------|------|
| UI_PROTOTYPE | §16 系统设置页 |
| CODE_WIKI | §6.6.2 backup.py |
| SRS | §5.4 可靠性需求 |

### 15.2 任务清单

#### 后端

| # | 任务 | 产出物 |
|---|------|------|
| 14.1 | 创建 `server/utils/backup.py` | AutoBackup 类：每天凌晨 2 点自动备份 |
| 14.2 | 在 `server/main.py` 中启动备份 | `AutoBackup.start()` |

#### 桌面端

| # | 任务 | 产出物 |
|---|------|------|
| 14.3 | 创建 `client/views/settings_view.py` | SettingsView（见 UI §16）：数据库路径、备份目录、文件大小限制、通知阈值、关于信息 |

### 15.3 验收标准

- [ ] 对照 SRS AC-14：每天自动备份，备份文件可恢复
- [ ] 设置页各项配置可保存和读取
- [ ] 手动备份功能正常

---

## 16. 阶段 15：联调测试

### 16.1 参考文档

| 文档 | 对应章节 |
|------|------|
| SRS | §9 验收标准（全部 17 条 AC-01 ~ AC-17） |
| SRS | §8 业务规则汇总（全部 15 条 BR-01 ~ BR-15） |

### 16.2 任务清单

| # | 任务 | 内容 |
|---|------|------|
| 15.1 | 全流程走查 | 以销售身份创建任务 → 技术员收件 → 试磨 → 检测 → 去向，完整走一遍 |
| 15.2 | 权限测试 | 每个角色登录，验证菜单可见性和操作权限 |
| 15.3 | 状态流转测试 | 验证所有合法流转 + 非法流转被拒绝 |
| 15.4 | 边界测试 | 空表单提交、超长文本、特殊字符、超时 Token |
| 15.5 | 文件上传测试 | 各种类型、各种大小、非法类型 |
| 15.6 | 统计验证 | 手动核对统计数据与数据库实际数据 |
| 15.7 | 消息提醒测试 | 模拟超时任务，验证提醒生成 |
| 15.8 | Bug 修复 | 汇总修复所有发现的问题 |

### 16.3 验收标准（对照 SRS §9）

- [ ] AC-01 ~ AC-17 全部通过
- [ ] BR-01 ~ BR-15 全部满足
- [ ] 0 个阻断性 Bug
- [ ] 界面与 UI_PROTOTYPE 一致

---

## 17. 阶段 16：Windows 打包

### 17.1 参考文档

| 文档 | 对应章节 |
|------|------|
| CODE_WIKI | §14.4 桌面客户端打包 |

### 17.2 任务清单

| # | 任务 | 产出物 |
|---|------|------|
| 16.1 | 编写 PyInstaller spec 文件 | `GTMS.spec` |
| 16.2 | 执行打包 | `dist/GTMS.exe` |
| 16.3 | 测试打包后的 exe | 在干净 Windows 环境测试启动、登录、基本操作 |
| 16.4 | 处理资源文件路径 | 确保图片、图标等资源正确打包 |

### 17.3 验收标准

- [ ] `GTMS.exe` 可独立运行（无需安装 Python）
- [ ] 所有功能正常
- [ ] 文件大小合理（< 200MB）

---

## 18. 阶段 17：微信小程序

### 18.1 参考文档

| 文档 | 对应章节 |
|------|------|
| UI_PROTOTYPE | §17 微信小程序页面设计（全部 7 个页面） |
| CODE_WIKI | §8 小程序模块详解 |

### 18.2 任务清单

| # | 任务 | 产出物 | 对应UI |
|---|------|------|------|
| 17.1 | 初始化 UniApp 项目 | 项目结构 | — |
| 17.2 | 创建 `pages/login/index` | 登录页 | UI §17.1 |
| 17.3 | 创建 `pages/dashboard/index` | 仪表盘首页 | UI §17.2 |
| 17.4 | 创建 `pages/task_list/index` | 任务列表 | UI §17.3 |
| 17.5 | 创建 `pages/task_detail/index` | 任务详情 | UI §17.4 |
| 17.6 | 创建 `pages/receipt/index` | 收件登记（拍照上传） | UI §17.5 |
| 17.7 | 创建 `pages/statistics/index` | 统计报表 | UI §17.6 |
| 17.8 | 创建 `pages/notification/index` | 消息通知 | UI §17.7 |
| 17.9 | 封装 API 层 | `api/` 目录，封装所有接口调用 | — |
| 17.10 | 底部导航栏 | 首页 / 任务 / 统计 / 我的 | UI §17.2 |
| 17.11 | 小程序测试 | 全流程测试 | — |

### 18.3 验收标准

- [ ] 全部 7 个页面与 UI_PROTOTYPE §17 一致
- [ ] 登录、查看任务、收件登记（拍照上传）功能正常
- [ ] 消息推送正常
- [ ] 在微信开发者工具中编译通过

---

## 19. 阶段 18：部署上线

### 19.1 任务清单

| # | 任务 | 内容 |
|---|------|------|
| 18.1 | 准备生产环境 | MySQL 安装、Python 环境、Nginx 配置 |
| 18.2 | 切换数据库 | SQLite → MySQL，执行 DDL + 种子数据 |
| 18.3 | 配置 HTTPS | 为小程序 API 准备域名和证书 |
| 18.4 | 部署后端服务 | systemd 或 Windows Service 守护进程 |
| 18.5 | 部署桌面客户端 | 分发 GTMS.exe |
| 18.6 | 小程序审核发布 | 提交微信审核 |
| 18.7 | 用户培训 | 各角色操作培训 |
| 18.8 | 上线监控 | 监控日志、错误、性能 |

### 19.2 验收标准

- [ ] 后端服务稳定运行
- [ ] 桌面端可连接生产服务器
- [ ] 小程序通过审核并上线
- [ ] 用户可正常使用全部功能

---

## 附录：依赖关系图

### A. 阶段依赖

```
                    ┌─────────────────────────────────────────────────┐
                    │                                                  │
                    ▼                                                  │
   阶段1 ──► 阶段2 ──► 阶段3 ──► 阶段4 ──► 阶段5 ──► 阶段6           │
   初始化    数据库    后端框架   登录与RBAC权限  客户管理    试磨任务       │
                                                              │        │
                    ┌─────────────────────────────────────────┘        │
                    │                                                  │
                    ├──► 阶段7 ──► 阶段8 ──► 阶段9 ──► 阶段10         │
                    │    收件管理   试磨管理   检测管理   工件去向       │
                    │                                                  │
                    ├──► 阶段11 ──► 阶段12 ──► 阶段13 ──► 阶段14      │
                    │    查询统计   操作日志   消息提醒   系统设置       │
                    │                                                  │
                    └──────────────────────────────────────────────────┘
                                          │
                                          ▼
                                       阶段15 ──► 阶段16 ──► 阶段17
                                       联调测试    Windows打包  小程序
                                          │
                                          ▼
                                       阶段18
                                       部署上线
```

### B. 文件产出依赖（关键路径）

```
server/models/base.py
    └── server/models/*.py (全部10个模型)
            └── server/core/security.py
            │       └── server/core/dependencies.py
            │               └── server/routers/auth_router.py
            │                       └── client/views/login_view.py
            │                               └── client/views/main_window.py
            │
            └── server/services/task_service.py
                    └── server/routers/trial_task_router.py
                            └── client/views/trial_task_view.py
                                    └── client/views/receipt_view.py
                                            └── client/views/grinding_view.py
                                                    └── client/views/inspection_view.py
                                                            └── client/views/dispatch_view.py
```

### C. 风险提示

| 风险 | 影响 | 缓解措施 |
|------|------|------|
| 文件上传大小限制 | 检测报告可能超 50MB | 阶段3配置可调，设置页支持修改 |
| 小程序审核周期 | 上线延迟 | 提前提交审核，预留 2 周 |
| SQLite → MySQL 迁移 | 数据丢失 | 阶段15 充分测试迁移脚本 |
| 企业内部网络限制 | 小程序无法访问 API | 提前准备 HTTPS 域名和备案 |

---

> **签发：** 首席软件架构师  
> **日期：** 2026-07-02  
> **版本：** V1.0  
> **状态：** 已确认，待执行