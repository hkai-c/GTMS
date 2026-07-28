# GTMS v1.0.0-rc1

---

## Overview

本版本为 GTMS (Grinding Trial Management System) 首个 Release Candidate，
基于 Sprint 14 Final Release (v0.14.0) 生成。

---

## Added Features

### Trial Management (Sprint 5)
- Trial Task Creation — 试磨任务创建、编号生成、状态流转
- Customer Management — 客户 CRUD 管理
- Requirement Tracking — 需求跟踪

### Grinding Workflow (Sprint 6-7)
- Receipt Workflow — 收件登记、图片上传
- Grinding Record — 试磨记录、机型跟踪
- Machine Tracking — 试磨设备管理

### Inspection (Sprint 8)
- Inspection Record — 检测记录管理
- Result Management — 检测结果（PASSED / FAILED）
- Report Attachment — 检测报告上传

### Dispatch (Sprint 9)
- Dispatch Workflow — 发货流程
- Destination Management — 工件去向管理

### Notification (Sprint 12)
- Notification Creation — 消息提醒创建
- Read Status — 已读/未读状态管理
- Duplicate Prevention — 幂等性保证
- Auto Generation — 自动规则生成（收件超时、试磨超时、报告缺失）

### Query & Statistics (Sprint 10)
- Dashboard Statistics — 统计概览（本月/年度任务数、成功率）
- Customer Ranking — 客户排行 Top 10
- Machine Ranking — 机型排行 Top 10
- Query Filter — 多条件组合查询
- Export — 数据导出

### File Management (Sprint 2 / Sprint 6)
- Upload — 文件上传（图片/视频/文档/CAD）
- Validation — MIME 校验、大小限制、扩展名白名单
- Storage Management — 文件存储管理

### System Management (Sprint 3-4 / Sprint 11 / Sprint 13)
- Authentication — 用户认证
- JWT — Token 签发与验证
- RBAC Permission — 基于角色的权限控制
- Audit Log — 操作日志审计
- Settings — 系统设置管理
- Backup — 数据备份

---

## Fixed Issues

### Sprint 14 Bug Fixes

| Bug ID | 类型 | 修复内容 |
|--------|------|----------|
| BUG-E2E-006 | Regression | E2E 回归 Bug 修复 |
| BUG-PERM-001 | Permission | 权限码统一为 Router 规范 (view/create/edit/delete) |
| BUG-PERM-002 | Permission | ROLE_PERMISSION_MAP 权限码同步更新 |
| BUG-STATUS-003 | Status Machine | finish_grinding() 同步 failure_reason 到 TrialTask |
| BUG-BOUND-003 | Boundary | Machine Ranking 过滤 machine_type 空数据 |
| BUG-BOUND-004 | Boundary | sort_order 添加正则校验 (asc/desc) |
| BUG-UPLOAD-001 | Upload | 0 Byte 文件拒绝 |
| BUG-UPLOAD-002 | Upload | None MIME 类型拒绝 |
| BUG-UPLOAD-003 | Upload | URL 使用相对路径 |
| BUG-STATS-001 | Statistics | 非法 process_status → 422 |
| BUG-STATS-002 | Statistics | 非法 sort_order → 422 |
| BUG-NOTIFY-004 | Notification | is_read=True 创建通知跳过幂等检查 |

**Status: All Closed**

---

## Security

- JWT Authentication — HS256 签名，自动过期验证
- RBAC Permission Control — 5 角色权限矩阵 (Admin / Manager / Technician / Sales / Viewer)
- Permission Naming Normalization — 统一 view/create/edit/delete 规范
- Input Validation — 所有输入参数校验
- File Upload Validation — MIME 类型、扩展名、文件大小校验
- SQL Injection Protection — ORM 参数化查询
- XSS Protection — 响应内容安全处理

---

## Architecture

```
Router → Service → Repository/ORM
```

- 无循环依赖
- 无新增依赖
- Status Machine 单一职责
- Workflow Frozen
- 分层清晰，职责明确

---

## Database

- Schema Stable — 无变更
- No Migration Required — 无需新增迁移
- Data Integrity Verified — 数据完整性验证通过
- Backup Verified — 备份功能验证通过

---

## Testing

### Sprint 14 Regression

| 测试 | 结果 |
|------|:----:|
| End-to-End Workflow | PASS (88/88) |
| Permission Matrix | PASS |
| Status Machine | PASS |
| Boundary | PASS |
| File Upload | PASS |
| Statistics | PASS |
| Notification | PASS |
| Bug E2E Regression | PASS (25/25) |

**Regression Status: ALL PASSED**

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v1.0.0-rc1 | 2026-07-27 | Sprint 15 Release Candidate |
| v0.14.0 | 2026-07-27 | Sprint 14 Final Release |
| v0.13.0 | — | Sprint 13 Backup & Settings |
| v0.12.0 | — | Sprint 12 Notification System |
| v0.11.0 | — | Sprint 11 Audit Logging |
| v0.10.0 | — | Sprint 10 Query & Statistics |
| v0.9.0 | — | Sprint 9 Dispatch |
| v0.8.0 | — | Sprint 8 Inspection |
| v0.7.0 | — | Sprint 7 Grinding |
| v0.6.0 | — | Sprint 6 Receipt |
| v0.5.0 | — | Sprint 5 Trial Task |
| v0.4.0 | — | Sprint 4 Customer Management |
| v0.3.0 | — | Sprint 3 Auth & Permission |
| v0.2.0 | — | Sprint 2 Core Framework |
| v0.1.0 | — | Sprint 1 ORM Models |