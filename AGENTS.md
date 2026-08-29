# AI-batch-raw-to-offline-guide — 维护索引

## 全局规则
- 架构（为什么）→ [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 字段手册（改 Schema 前必读）→ [docs/schema-fields.md](docs/schema-fields.md)
- 生成器手册 → [generator/README.md](generator/README.md)
- 脚本手册 → [scripts/README.md](scripts/README.md)
- 决策记录 → [.agents/notes/](.agents/notes/)

## 常用命令（uv 环境，真实可跑）
- uv run python scripts/schema_validator.py（数据验证）
- uv run python generator/schema_generator.py（生成 HTML）
- uv run python scripts/stats.py · analyze_data.py · export_xlsx.py
- uv run pytest（tests/ 冒烟测试）

## 验证快照（2026-08-28 实际跑过）
- schema_validator: PASS（唯一ID 311 / 有效引用 779 / 双向链接 234）
- pytest: 2 passed / 0 failed

## 活跃坑
- output/ 被 .gitignore 排除，clone 后需先跑生成器
- Windows 控制台中文乱码不影响校验结果
- data/ 是运行真相，src/ 只是素材参考

## 文档地图
- 用户教程 → [docs/usage.md](docs/usage.md)
- 测试 → [tests/README.md](tests/README.md)
- 验证报告 → [VERIFICATION_REPORT.md](VERIFICATION_REPORT.md)
- 变更日志 → [changelog.md](changelog.md)