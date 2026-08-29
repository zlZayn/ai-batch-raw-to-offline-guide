# schema-fields.md — Schema 字段手册

- 用途：schema.json + data/*.json 的字段清单、引用关系、改字段影响路由
- 定位：改 Schema/数据前必读；架构原因见 [ARCHITECTURE.md](ARCHITECTURE.md)
- 事实来源：字段以 schema.json 声明 + data/ 实际为准（两者现已对齐）

## 实体与文件对照（13 实体 = data/ 下 13 个 JSON）

| 实体 | JSON 文件 | 形态 | 关键引用字段 |
|------|-----------|------|--------------|
| meta | meta.json | 单例对象 | source_files（源文件索引） |
| tags | tags.json | tags 数组 + categories 数组 | 被所有实体 tags/zone_ids 引用 |
| attractions | attractions.json | 数组 | zone_ids/tags/review_ids/opinion_ids/warning_ids |
| shows | shows.json | 数组 | zone_ids/tags/opinion_ids/warning_ids |
| restaurants | restaurants.json | 数组 | recommended_dish_ids/review_ids/opinion_ids/warning_ids |
| dishes | dishes.json | 数组 | restaurant_ids/review_ids/opinion_ids |
| tips | tips.json | 数组 | attraction_ids/opinion_ids |
| warnings | warnings.json | 数组 | attraction_ids/show_ids/restaurant_ids/shortcut_ids |
| shortcuts | shortcuts.json | 数组 | 无出向引用 |
| itineraries | itineraries.json | 数组 | time_slots[].items[].{attraction,show,restaurant}_ids |
| reviews | reviews.json | 数组（依附实体） | target_id（ref: attractions/shows/restaurants/dishes） |
| opinions | opinions.json | 数组（依附实体） | target_id（ref: 上述 + tips） |
| preparations | preparations.json | 单例对象 | warning_ids（schema 未声明，data 实际含） |

## 引用与反向引用规则

- 正向引用：实体字段（`{type}_ids` / target_id）指向目标实体 id
- 反向声明：schema 中 `backref` 声明反向字段，validator 校验双向一致
- 索引：schema `indexes` 声明 tag_index（按 tags）/ zone_index（按 zone_ids）；backrefs 分组 reviews/opinions/warnings
- 唯一约束：id 全项目唯一；重复即验证失败

## 改字段影响路由

| 改动 | 必须同步 | 验证 |
|------|----------|------|
| schema.json 增删字段 | data/*.json 对应实体 + 模板渲染（如用） | uv run python scripts/schema_validator.py |
| data/ 改引用（_ids） | 目标实体存在性 + 反向实体 | 同上（引用完整性/双向一致性） |
| data/ 改类型/必填 | 与 schema 声明一致 | 同上（字段类型/必填） |
| 模板渲染新字段 | guide_template.html 对应用法 | 重新生成 + 打开检查 |
| 增删实体 | schema entities + data/*.json + 模板列表页/路由 | validator + 生成 |

## 已知约定

- ID 格式 `{前缀}_{标识}`：前缀规约表见 [usage.md](usage.md)「ID 命名规范」（validator 不硬检查，AI 规范要求）
- stance 枚举：`pro` / `contra`（数据实际值，schema 已对齐）
- sentiment 枚举：`positive` / `negative` / `neutral` / `mixed`
- severity 枚举：`high` / `medium` / `low`
- rating：schema 声明 1-5，data 中存在 0 分记录（validator 不检查范围，已知遗留）