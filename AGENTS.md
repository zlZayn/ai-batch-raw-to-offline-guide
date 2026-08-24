# ai-batch-raw-to-offline-guide — 维护索引

## 全局规则
- 架构（为什么）→ [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 生成器手册 → [generator/README.md](generator/README.md)
- 脚本手册 → [scripts/README.md](scripts/README.md)
- 决策记录 → [.agents/notes/](.agents/notes/)

## 常用命令（uv 环境，真实可跑）
- uv run python scripts/schema_validator.py（数据验证）
- uv run python generator/schema_generator.py（生成 HTML）
- uv run python scripts/stats.py · analyze_data.py · export_xlsx.py
- uv run pytest（项目暂无 tests/）

## 验证快照（2026-08-24 实际跑过）
- schema_validator: PASS（唯一ID 311 / 有效引用 779 / 双向链接 234）
- pytest: 0 collected（项目无 tests/ 目录）

## 待办
- [ ] 补最小测试后建 tests/ 目录

## 活跃坑
- output/ 被 .gitignore 排除，clone 后需先跑生成器
- Windows 控制台中文乱码不影响校验结果

## 文档地图
- 架构设计 → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 生成器 → [generator/README.md](generator/README.md)
- 脚本 → [scripts/README.md](scripts/README.md)
- 决策记录 → [.agents/notes/](.agents/notes/)