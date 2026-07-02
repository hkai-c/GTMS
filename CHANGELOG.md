# 更新日志 (Changelog)

GTMS 项目的所有重要变更记录。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，  
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [0.1.0-alpha] — 2026-07-02

### 新增 (Added)

- 项目初始化：创建完整目录结构
- 设计文档：SRS、DB_DESIGN、UI_PROTOTYPE、CODE_WIKI、DEVELOPMENT_ROADMAP
- 开发规范：AI_RULES.md、PROMPT_RULES.md
- 版本管理：Git 初始化、.gitignore、LICENSE、VERSION
- 依赖管理：requirements.txt、conda 环境 (gtms, Python 3.13)
- 环境配置：.env.example

### 待开发 (Planned)

- 阶段 1：数据库设计 (ORM 模型、DDL、种子数据)
- 阶段 2：后端核心框架 (FastAPI 骨架、中间件、异常体系)
- 阶段 3：登录与权限 (JWT 认证、角色权限)
- 阶段 4-14：核心业务模块开发
- 阶段 15-18：联调、打包、小程序、部署

---

## 版本说明

| 版本号 | 阶段 | 说明 |
|------|------|------|
| 0.1.x | alpha | 项目初始化 + 基础框架 |
| 0.2.x | alpha | 核心业务模块 |
| 0.9.x | beta | 联调测试 |
| 1.0.0 | stable | 正式发布 |