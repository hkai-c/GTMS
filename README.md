# 磨床试磨管理系统 GTMS

> **Grinding Trial Management System**  
> 版本：V1.0

---

## 项目简介

磨床试磨管理系统（GTMS）是一套适用于磨床制造企业的试磨件全过程管理系统，实现从销售接单到试磨完成、检测报告上传、工件去向登记的全流程数字化管理。

## 技术栈

| 层级 | 技术 |
|------|------|
| 桌面端 | Python 3.13 + PySide6 |
| 后端 | FastAPI + SQLAlchemy |
| 数据库 | SQLite (开发) / MySQL 8.0 (正式) |
| 小程序 | UniApp (Vue3) |

## 快速启动

```bash
# 1. 创建 conda 环境
conda create -n gtms python=3.13 -y
conda activate gtms

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动后端
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 启动桌面客户端
python client/main.py
```

## 项目结构

```
data_control/
├── client/          # 桌面客户端 (PySide6)
├── server/          # 后端服务 (FastAPI)
├── database/        # 数据库
├── miniapp/         # 微信小程序 (UniApp)
├── docs/            # 设计文档
├── uploads/         # 上传文件
├── backup/          # 数据库备份
├── tests/           # 测试
└── scripts/         # 脚本
```

## 设计文档

- [CODE_WIKI.md](docs/CODE_WIKI.md) — 架构百科
- [SRS.md](docs/SRS.md) — 需求规格说明书
- [DB_DESIGN.md](docs/DB_DESIGN.md) — 数据库设计
- [UI_PROTOTYPE.md](docs/UI_PROTOTYPE.md) — UI 原型
- [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) — 开发路线图
- [AI_RULES.md](docs/AI_RULES.md) — AI 开发规范
- [PROMPT_RULES.md](docs/PROMPT_RULES.md) — 提示规范

## 许可证

Copyright © 2026 All Rights Reserved.