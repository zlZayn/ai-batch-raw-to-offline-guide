# generator/ — HTML 生成器手册

- 职责：Schema 驱动的 HTML 生成流水线
- schema_generator.py：读 schema.json + data/，构建 ID 映射与索引，Jinja2 渲染单文件 HTML
  - 关键导出：SchemaGenerator 类、main() 命令行入口
  - 参数：--data-dir / --template-dir / --output-dir / --template / --output
  - 被谁依赖：GitHub Actions（static.yml）、projects/ 子项目、手动运行
  - 改后必测：uv run python scripts/schema_validator.py && uv run python generator/schema_generator.py
- guide_template.html：Jinja2 模板
  - 前端路由/筛选/轮播逻辑内嵌于产物，改动后重新生成并检查渲染
- 变更影响路由：改这里 → 同步根 [AGENTS.md](../AGENTS.md) 待办/坑 + 架构影响写 [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- 使用约束与工作偏好 → 见 [AGENTS.md](AGENTS.md)