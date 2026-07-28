# GTMS Version History

---

## v1.0.0-rc1 (2026-07-27)

**Release Candidate**

基于 Sprint 14 Final Release (v0.14.0) 生成。

变更:
- 版本标识更新为 1.0.0-rc1
- 新增 CHANGELOG.md
- 新增 RELEASE_NOTES.md
- 新增 VERSION_HISTORY.md

---

## v0.14.0 (2026-07-27)

**Sprint 14 Final Release**

- Sprint 14.1 End-to-End Workflow Test: PASS
- Sprint 14.2 Permission Matrix Test: PASS
- Sprint 14.3 Status Machine Test: PASS
- Sprint 14.4 Boundary Test: PASS
- Sprint 14.5 File Upload Test: PASS
- Sprint 14.6 Statistics Verification: PASS
- Sprint 14.7 Notification Test: PASS
- Sprint 14.8 Bug Fix & Regression: 11 bugs FIXED

---

## v0.13.0

**Sprint 13: Backup & Settings**

- 系统设置管理
- 数据备份功能
- 备份调度器

---

## v0.12.0

**Sprint 12: Notification System**

- 消息提醒创建/查询/已读
- 幂等性保证
- 自动规则生成（收件超时/试磨超时/报告缺失）

---

## v0.11.0

**Sprint 11: Audit Logging**

- 操作日志审计
- LogService 统一日志入口
- 所有 Service 写操作自动记录

---

## v0.10.0

**Sprint 10: Query & Statistics**

- 多条件组合查询
- 统计概览（本月/年度任务数、成功率）
- 客户排行 / 机型排行
- 数据导出

---

## v0.9.0

**Sprint 9: Dispatch**

- 发货流程
- 工件去向管理
- 状态推进 DISPATCHED → CLOSED

---

## v0.8.0

**Sprint 8: Inspection**

- 检测记录管理
- 检测结果 PASSED / FAILED
- 报告上传

---

## v0.7.0

**Sprint 7: Grinding**

- 试磨记录管理
- 设备 / 机型跟踪
- 试磨失败处理
- 状态推进 RECEIVED → GRINDING

---

## v0.6.0

**Sprint 6: Receipt**

- 收件登记
- 图片上传
- 状态推进 CREATED → RECEIVED

---

## v0.5.0

**Sprint 5: Trial Task**

- 试磨任务 CRUD
- 任务编号自动生成
- 状态流转基础

---

## v0.4.0

**Sprint 4: Customer Management**

- 客户 CRUD (前后端)

---

## v0.3.0

**Sprint 3: Auth & Permission**

- JWT 认证
- RBAC 权限系统
- 登录页、角色权限管理

---

## v0.2.0

**Sprint 2: Core Framework**

- FastAPI 骨架
- 中间件体系
- 异常处理体系
- 文件处理工具

---

## v0.1.0

**Sprint 1: ORM Models**

- 数据库 ORM 模型
- DDL 生成
- 种子数据