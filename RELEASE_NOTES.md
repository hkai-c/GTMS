# GTMS Release Notes — v1.0.0-rc1

---

## Release Information

| 项目 | 值 |
|------|-----|
| Project | GTMS (Grinding Trial Management System) |
| Version | v1.0.0-rc1 |
| Release Type | Release Candidate |
| Sprint | 15 |
| Base Version | v0.14.0 |
| Release Date | 2026-07-27 |
| Release Status | Candidate |

---

## System Overview

GTMS (Grinding Trial Management System) 是一套试磨任务管理系统，
支持从任务创建、收件、试磨、检测到发货的全流程管理。

### Core Modules

| 模块 | Sprint | 功能 |
|------|:------:|------|
| Trial Task | 5 | 任务创建、编号生成、状态流转 |
| Receipt | 6 | 收件登记、图片上传 |
| Grinding | 7 | 试磨记录、设备管理、失败处理 |
| Inspection | 8 | 检测记录、报告上传、结果管理 |
| Dispatch | 9 | 发货流程、工件去向 |
| Query & Statistics | 10 | 多条件查询、统计概览、排行 |
| Audit Log | 11 | 操作日志审计 |
| Notification | 12 | 消息提醒、幂等性、自动规则 |
| Settings & Backup | 13 | 系统设置、数据备份 |
| Integration Test | 14 | 端到端测试、Bug 修复 |
| Release Candidate | 15 | RC 发布准备 |

---

## Workflow

```
CREATED → RECEIVED → GRINDING → DISPATCHED → CLOSED
                       ↓
                     CLOSED (试磨失败)
```

### Status Machine

**Process Status:**
- CREATED → RECEIVED
- RECEIVED → GRINDING
- GRINDING → DISPATCHED
- DISPATCHED → CLOSED
- GRINDING → CLOSED (失败流程)

**Result Status:**
- PENDING → PASSED
- PENDING → FAILED

---

## Permission Matrix

| Role | task | receipt | grinding | inspection | dispatch | notification | query |
|------|:----:|:-------:|:--------:|:----------:|:--------:|:------------:|:-----:|
| Admin | Full | Full | Full | Full | Full | Full | Full |
| Manager | Full | Full | Full | Full | Full | Full | Full |
| Technician | View | — | View/Create/Edit | View/Create/Edit | — | View | — |
| Viewer | View | View | View | View | View | View | View |

---

## Fixed Issues (Sprint 14)

| Bug ID | Type | Description | Status |
|--------|------|-------------|:------:|
| BUG-E2E-006 | Regression | E2E 回归 Bug | Closed |
| BUG-PERM-001 | Permission | 权限码统一 (view/create/edit/delete) | Closed |
| BUG-PERM-002 | Permission | ROLE_PERMISSION_MAP 同步 | Closed |
| BUG-STATUS-003 | Status Machine | failure_reason 同步到 TrialTask | Closed |
| BUG-BOUND-003 | Boundary | Machine Ranking 空数据过滤 | Closed |
| BUG-BOUND-004 | Boundary | sort_order 正则校验 | Closed |
| BUG-UPLOAD-001 | Upload | 0 Byte 文件拒绝 | Closed |
| BUG-UPLOAD-002 | Upload | None MIME 拒绝 | Closed |
| BUG-UPLOAD-003 | Upload | URL 相对路径 | Closed |
| BUG-STATS-001 | Statistics | 非法 process_status → 422 | Closed |
| BUG-STATS-002 | Statistics | 非法 sort_order → 422 | Closed |
| BUG-NOTIFY-004 | Notification | is_read=True 幂等跳过 | Closed |

---

## Security

| Feature | Implementation |
|---------|---------------|
| Authentication | JWT (HS256) |
| Authorization | RBAC (5 roles) |
| Password | bcrypt hash |
| File Upload | MIME + extension + size validation |
| SQL Injection | ORM parameterized queries |
| XSS | Content security handling |
| Input Validation | Pydantic + regex validation |

---

## Architecture

```
Router → Service → Repository/ORM
```

- 三层架构，单一职责
- 无循环依赖
- 无跨层调用
- 统一异常处理
- 统一审计日志

---

## Database

- SQLite (development) / PostgreSQL (production)
- 13 tables, 0 pending migrations
- Soft delete pattern
- Timestamp audit (created_at, updated_at)
- User audit (created_by, updated_by)

---

## Testing

### Sprint 14 Regression: ALL PASSED

| Test | Items | Result |
|------|:-----:|:------:|
| End-to-End Workflow | 88 | PASS |
| Permission Matrix | — | PASS |
| Status Machine | — | PASS |
| Boundary | — | PASS |
| File Upload | — | PASS |
| Statistics | — | PASS |
| Notification | — | PASS |
| Bug E2E Regression | 25 | PASS |

---

## Known Limitations

- 无压力测试数据
- 无多语言支持
- 仅支持单机部署
- SQLite 仅适用于开发环境

---

## Next Steps

- Sprint 15 Task 15.3: Final Verification
- Sprint 15 Task 15.4: Release Freeze Review
- Sprint 16: Windows 打包
- Sprint 17: 部署上线