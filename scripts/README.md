# scripts/ — 工具脚本手册

- 职责：工具脚本（校验与分析；模板渲染在 generator/）
- schema_validator.py：Schema 驱动验证（ID 唯一、引用完整、字段类型、双向链接一致）
  - 被谁依赖：CI（static.yml）、生成前必跑
  - 改后必测：uv run python scripts/schema_validator.py
- stats.py：按 JSON 文件统计实体数量
- analyze_data.py：字段覆盖率/值域分析，输出 output/data_analysis/（SVG + report.json）
- export_xlsx.py：导出 output/data.xlsx（依赖 openpyxl）
- 边界：scripts/ 只放校验与分析工具；生成/渲染在 [generator/](../generator/README.md)（二者以 schema.json 为共同契约）
- 变更影响路由：改这里 → 同步根 [AGENTS.md](../AGENTS.md) 验证快照 + 架构影响写 [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- 使用约束与工作偏好 → 见 [AGENTS.md](AGENTS.md)