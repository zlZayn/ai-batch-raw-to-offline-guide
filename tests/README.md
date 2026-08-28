# tests/ — 测试手册

- 职责：Schema 校验与数据规范的自动化闸门
- test_schema_validator.py：加载 scripts/schema_validator.py 的 SchemaValidator 类，跑完整校验
  - test_validation_passes：校验必须通过且无错误
  - test_snapshot_counts：断言唯一ID 311 / 有效引用 779 / 双向链接 234
  - 对应对象：scripts/schema_validator.py（直接驱动其类，非 subprocess）
  - 改后必测：uv run pytest -q
- 变更影响路由：改 schema.json 或 data/ 计数 → 快照断言可能漂移，需同步本文件 + 根 [AGENTS.md](../AGENTS.md) 验证快照
- 使用约束与工作偏好 → 见 [AGENTS.md](AGENTS.md)