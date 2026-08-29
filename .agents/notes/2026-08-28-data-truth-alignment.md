# 决策：数据真相对齐与文档用法同步（2026-08-28）

已实施：已实施

## 问题
- schema.json 声明字段落后于 data/*.json 实际字段：attractions 缺 5 个、reviews/opinions 缺 2 个
- opinions.stance 枚举 schema 写 `pro/con`，实际数据是 `pro/contra`（usage.md 教程与数据一致，schema 错）
- data/meta.json 的 source_files 引用不存在的 src/10_小红书补充/*.md（幽灵索引）
- usage.md / workflow.md / README 命令仍是裸 python，项目已 uv 管理

## 决策
- schema.json 补全实际数据字段（attractions: locker/queue_strategy/seat_advice/height_requirement/source_files；reviews/opinions: target_type/source_files），stances 枚举改为 `["pro", "contra"]`
- 删除 meta.json 中指向不存在文件的 2 条 source_files 记录（md_xhs_01/02）
- 文档命令统一为 `uv run python ...`（与 AGENTS.md 一致）
- 哲学写入文档：data/ 是运行真相，src/ 是素材参考，不一致以 data/ 为准

## 替代方案（强制）
- schema.json 保持原样仅改文档声明：validator 对实际字段零类型检查，AI 教程字段与 schema 永久分裂，越埋越深
- 保留幽灵索引并在文档标注"历史遗留"：data/ 与文件系统不一致持续存在，违背"data 是真相"
- 命令保持裸 python：AGENTS.md 用 uv run、教程用 python，两套口径，agent 行为不可预判

## 影响
- 收益：schema 与数据字段对齐，validator 类型检查覆盖实际字段；AI 教程与项目规则单一口径
- 代价：schema.json 变更属功能配置，需重跑 validator 确认（PASS：311/779/234 不变）
- 遗留：rating 数据含 0 分而 schema 声明 min:1（validator 不检查范围，仅记录不修）
- 验证：uv run python scripts/schema_validator.py PASS + uv run pytest 2 passed