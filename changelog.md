# 变更日志

记录数据结构的演进。产品设计见 `docs/design.md`，技术实现见 `docs/workflow.md`。

---

## 3.3.0 — 2026-05-05

### 双向链接一致性检查 + 数据修复

#### 一、ci.py 新增第 7 项：双向链接一致性

新增 `bidir_checks` 检查，覆盖 13 组关联关系：

| 正向声明 | 反向验证 |
|---------|---------|
| `attraction.review_ids` → | `review.target_id` 必须指向该 attraction |
| `attraction.opinion_ids` → | `opinion.target_id` 必须指向该 attraction |
| `attraction.warning_ids` → | `warning.attraction_ids` 必须包含该 attraction |
| `show.opinion_ids` → | `opinion.target_id` 必须指向该 show |
| `show.warning_ids` → | `warning.show_ids` 必须包含该 show |
| `restaurant.recommended_dish_ids` → | `dish.restaurant_ids` 必须包含该 restaurant |
| `restaurant.review_ids` → | `review.target_id` 必须指向该 restaurant |
| `restaurant.opinion_ids` → | `opinion.target_id` 必须指向该 restaurant |
| `restaurant.warning_ids` → | `warning.restaurant_ids` 必须包含该 restaurant |
| `dish.review_ids` → | `review.target_id` 必须指向该 dish |
| `dish.opinion_ids` → | `opinion.target_id` 必须指向该 dish |
| `dish.restaurant_ids` → | `restaurant.recommended_dish_ids` 必须包含该 dish |
| `tip.opinion_ids` → | `opinion.target_id` 必须指向该 tip |

#### 二、数据修复：10 处双向链接不一致

首次运行时发现 10 条真实数据不一致（全部为 dish ↔ restaurant 归属关系）：

- `rest_cybertron` 缺失 2 道菜品反向引用（tuna_pancake、lasagna）
- `rest_bubba_gump` 缺失 2 道菜品反向引用（oil_splash_noodles、baozi）
- `rest_energy_crystal` 缺失 2 道菜品反向引用（两个雪泥）
- `rest_nublar_slush` 缺失 2 道菜品反向引用（banana、jasmine_peach）
- `rest_coke_tower_snack` 缺失 1 道菜品反向引用（banana）
- `dish_slush_blueberry` 缺失 1 家餐厅反向引用（nublar_slush）

#### 三、底层修复

- 修复 Windows GBK 编码下 `✓` 无法打印的 bug（`sys.stdout` 改为 UTF-8）

---## 3.2.0 — 2026-04-09

### 客观字段补全 + 样式统一 + CI 管线

#### 一、新增客观字段

| 实体 | 新增字段 | 说明 |
|------|---------|------|
| attractions | `duration_minutes` | 14 个项目从 null 补全为实际值（分钟） |
| attractions | `indoor` | 全部 17 个项目：室内/室外 |
| attractions | `water_splash` | 全部 17 个项目：是否会湿身 |
| attractions | `single_rider` | 全部 17 个项目：是否有单人通道 |
| attractions | `has_photo` | 全部 17 个项目：是否有官方拍照 |
| shows | `language` | 全部 15 个演出：语言（中文/英文/无台词） |
| shows | `is_seasonal` | 全部 15 个演出：是否季节限定 |
| shows | `location` | 全部 15 个演出：具体演出地点 |
| restaurants | `average_price` | 全部 15 家餐厅：人均价格（元） |
| restaurants | `indoor` | 全部 15 家餐厅：室内/室外 |
| restaurants | `business_hours` | 全部 15 家餐厅：营业时间 |
| restaurants | `location` | 12 家餐厅从 null 补全为实际位置 |
| dishes | `price` | 全部 40 道菜品：价格（元） |
| dishes | `is_seasonal` | 全部 40 道菜品：是否季节限定 |
| warnings | `zone_ids` | 10 条避雷从关联实体自动推导补全 |

#### 二、数据修正

- 合并重复避雷 `warn_show_01` 和 `warn_dining_18`（内容 94% 相同），warnings 34→33 条
- 删除过时脚本：`cleanup_tags.py`、`fix_objective_fields.py`、`fix_warning_zones.py`、`fix_remaining_fields.py`、`migrate_type_to_tags.py`、`migrate_v2_to_v3.py`、`generator/validate.py`、`scripts/validate_v3.py`

#### 三、HTML 模板更新

- 新增客观字段渲染：项目详情（时长/室内外/湿身/单人通道/拍照）、演出详情（语言/季节限定）、餐厅详情（人均/营业时间/室内外）、菜品详情（价格）、列表页（人均/价格）
- 统一颜色体系：每个详情页的 section-title 左边框使用实体对应颜色（`--section-color`）
- 统一关联信息渲染：Tip/Warning 详情页去掉 `renderEntityLinks`，统一用 `renderRelations`
- 统一 section-title 风格：去掉 emoji（📌⚡⚠️），全部纯文字
- 提取内联 style 为 CSS class（`.card.standalone`、`.card.hint`）
- Warning 的 tagsHtml 加 section-title + card 包裹

#### 四、新增工具

- `scripts/ci.py`：三阶段 CI 管线（数据校验 → HTML 生成 → 生成后验证）
- `scripts/analyze_data.py`：数据结构分析（字段覆盖率热力图、数值分布、引用密度等 13 张 SVG + JSON 报告）

---

## 3.1.0 — 2026-04-09

### type_id → tags 统一 + 路由复数化 + 标签清理

---

#### 一、type_id 字段迁移到 tags

attractions 和 shows 中的 `type_id` 字段删除，类型标签统一存入 `tags[]` 数组。`tags` 成为唯一标签来源。

| 实体 | v3.0 | v3.1 |
|------|------|------|
| attractions | `type_id: "tag_type_4d5d"` + `tags: [...]` | `type_id` 删除，类型标签已在 `tags` 中 |
| shows | `type_id: "tag_type_parade"` + `tags: [...]` | `type_id` 删除，类型标签已在 `tags` 中 |

**模板影响**：新增 `getTypeTag()` / `getTypeIcon()` 从 `tags` 中筛选 `attraction_type` 分类标签；列表页只显示类型标签，不再显示区域标签。

---

#### 二、路由统一为复数形式

所有详情页路由从单数改为复数，消除单复数映射：

| v3.0 | v3.1 |
|------|------|
| `#attraction/{id}` | `#attractions/{id}` |
| `#show/{id}` | `#shows/{id}` |
| `#restaurant/{id}` | `#restaurants/{id}` |
| `#dish/{id}` | `#dishes/{id}` |
| `#itinerary/{id}` | `#itineraries/{id}` |
| `#tip/{id}` | `#tips/{id}` |
| `#warning/{id}` | `#warnings/{id}` |
| `#preparation/{section}` | `#preparations/{section}` |
| `#shortcut/{id}` | `#shortcuts/{id}` |
| `#tag/{id}` | `#tags/{id}` |

**模板影响**：移除 `SINGULAR` 映射和 `toListPage()` 函数，路由系统简化为 `DETAIL`/`LIST` 两个映射表。

---

#### 三、标签去重清理

删除 5 个冗余标签（51 → 46）：

| 删除的标签 | 原因 | 处理方式 |
|-----------|------|---------|
| `tag_type_show`（演出/表演） | 通用标签，被更具体标签替代 | 从所有实体 tags 中移除 |
| `tag_type_interactive`（互动秀） | 与 `tag_type_interactive_show` 重复 | 合并到 `tag_type_interactive_show` |
| `tag_type_stunt`（特技/特效） | 与 `tag_type_stunt_show` 重复 | 合并到 `tag_type_stunt_show` |
| `tag_dish_type_snack_food`（小吃） | 与 `tag_snack` 重复 | 合并到 `tag_snack` |

重命名 1 个标签：

| 标签 | 旧名称 | 新名称 |
|------|--------|--------|
| `tag_crowd_afternoon` | 下午/巡游时段 | 下午时段 |

---

#### 四、模板优化

- 列表页：shows 列表只显示类型标签，不再显示区域标签
- 新增 `getTypeTag()`：从 tags 中提取 `attraction_type` 分类标签
- 新增 `getTypeIcon()`：从 tags 中提取类型图标映射
- 新增 `dishRestaurantName()`：菜品→餐厅名称
- `renderEntityLinks()` 新增 `icon` 参数
- 移除 `toListPage()`、`SINGULAR` 映射

---

#### 五、新增脚本

| 脚本 | 用途 |
|------|------|
| `scripts/migrate_type_to_tags.py` | type_id → tags 迁移 |
| `scripts/cleanup_tags.py` | 标签去重清理 |

---

## 3.0.0 — 2026-04-08

### v2 → v3 数据 Schema 统一

消除所有不一致，使数据完全结构化、利于链接和复用。

**数据规模变化**：warnings 39 → 34 条（删除 5 条重复）；标签 51 → 46 条（3.1.0 清理后）

---

#### 一、园区字段统一：`zone_id` → `zone_ids`

所有实体的园区引用统一为 `zone_ids: string[]`（数组），即使只有一个园区也用数组。

| 实体 | v2 | v3 |
|------|----|----|
| attractions | `zone_id: "tag_zone_harry"` (string) | `zone_ids: ["tag_zone_harry"]` (array) |
| restaurants | `zone_id: "tag_zone_harry"` (string) | `zone_ids: ["tag_zone_harry"]` (array) |
| dishes | `zone_id: "tag_zone_harry"` (string/null) | `zone_ids: ["tag_zone_harry"]` (array) |
| shows | `zone_ids: [...]` (array) | 不变 |

dishes 中 `zone_id` 为 null 的 2 条记录，通过 `restaurant_ids` 推断所属园区。

---

#### 二、标签字段统一：`taste_tags` → `tags`

| 实体 | v2 | v3 |
|------|----|----|
| dishes | `taste_tags: ["tag_taste_sweet"]` | `tags: ["tag_taste_sweet"]` |
| 其他 7 类实体 | `tags: [...]` | 不变 |

---

#### 三、warnings.json 清洗

**ID 规范化**：消除 `warn_warn_*` 双重前缀，统一为 `warn_{category}_{编号}`。

| 旧 ID 模式 | 新 ID 模式 | 数量 |
|-----------|-----------|------|
| `warn_attr_01` ~ `warn_attr_07` | 不变 | 7 |
| `warn_show_01` | 不变 | 1 |
| `warn_warn_shoes_01` | `warn_prep_shoes_01` | 1 |
| `warn_warn_food_smell_02` | `warn_prep_food_02` | 1 |
| `warn_warn_prohibited_03` ~ `09` | `warn_prep_prohibited_03` ~ `09` | 7 |
| `warn_warn_dining_16` ~ `25` | `warn_dining_16` ~ `25` | 10 |
| `warn_warn_route_26` ~ `27` | `warn_route_26` ~ `27` | 2 |
| `warn_warn_timing_28` ~ `30` | `warn_timing_28` ~ `30` | 3 |
| `warn_warn_mental_31` | `warn_mental_31` | 1 |
| `warn_warn_shopping_32` | `warn_shopping_32` | 1 |
| `warn_warn_attractions_10` ~ `15` | **删除**（与 warn_attr 重复） | 6 |

**删除 5 条重复 warning**（内容与已有 warn_attr_* 完全相同）。

**修正 9 条餐饮 warning 的 zone 标签**（全部错误标为 `tag_zone_harry`，按实际关联修正）。

---

#### 四、孤儿 warning 关联

v2 中 25 条 `warn_warn_*` warning 不被任何实体的 `warning_ids` 引用。v3 中：

- 通过 `attraction_ids`/`show_ids`/`restaurant_ids` 反向填充到对应实体的 `warning_ids`
- 无直接实体关联的通用 warning 归入 `preparations.warning_ids`
- **restaurants 新增 `warning_ids` 字段**（v2 中餐厅没有此字段）

---

#### 五、warnings.json 新增 `zone_ids` 字段

每条 warning 新增 `zone_ids: string[]`，从 `tags` 中提取 zone 类标签独立存放，便于按园区筛选。

---

#### 六、价格字段统一

`preparations.json` 中 `ticket_prices.express_pass.options[].price` 类型统一：

| v2 | v3 |
|----|----|
| `"100元起"` (string) | `{"value": 100, "note": "元起"}` (object) |
| `200` (number) | `{"value": 200, "note": "元"}` (object) |

---

#### 七、文件结构重组

```
v2 结构（版本目录包含所有内容）：
  v1/data/ + v1/docs/
  v2/data/ + v2/docs/ + v2/generator/ + v2/output/

v3 结构（数据分版本，代码统一）：
  data/v1/          ← 历史数据
  data/v2/          ← 历史数据
  data/v3/          ← 当前数据（统一 schema）
  generator/        ← 生成脚本 + 模板
  output/           ← 最终产物
  docs/             ← 项目文档
  scripts/          ← 数据迁移 + 校验工具
```

---

## 2.0.0 — 2026-04-08

### v1 → v2 数据关系化

**核心变化**：从"数据内嵌、文本引用"升级为"数据独立、ID 引用"。7 个 JSON 文件扩展为 13 个。

---

#### 一、新增 6 个独立数据文件

| 新增文件 | 数量 | 来源 |
|----------|------|------|
| reviews.json | 101 条评价 | 从 attractions/shows/restaurants/dishes 的内嵌数组提取 |
| opinions.json | 24 条观点 | 从各实体的内嵌数组提取 |
| meta.json | 1 组元数据 | 新建：园区信息 + 源文件索引 |
| tags.json | 51 标签（11 分类） | 新建：全局标签字典 |
| shortcuts.json | 3 条秘密小道 | 新建 |
| preparations.json | 8 模块 | 新建：整合行前准备信息 |

---

#### 二、核心架构变化：内嵌 → 引用

v1 将 reviews/opinions/warnings 直接嵌在父实体内部；v2 全部提取为独立实体，父实体只保留 ID 引用数组。

**attractions.json**：

```json
// v1 — 内嵌对象
{
  "experience_reviews": [
    {"content": "很刺激！", "sentiment": "positive", "source_files": ["md_04a"]}
  ],
  "opinions": [
    {"id": "op_tb_must", "stance": "pro", "claim": "必刷项目", "reasoning": "..."}
  ],
  "warnings": [
    {"content": "非第一批不要冲", "severity": "high", "related_tags": [...]}
  ]
}

// v2 — ID 引用
{
  "review_ids": ["rev_attr_01", "rev_attr_02"],
  "opinion_ids": ["op_tb_must"],
  "warning_ids": ["warn_attr_01"]
}
```

**restaurants.json**：

```json
// v1 — 菜名文本引用
{"recommended_dishes": ["烤鸡排骨拼盘", "黄油啤酒"]}

// v2 — ID 引用
{"recommended_dish_ids": ["dish_roast_chicken_ribs", "dish_butter_beer"]}
```

**dishes.json**：

```json
// v1 — 内嵌
{"reviews": [...], "opinions": [...]}

// v2 — ID 引用
{"review_ids": [...], "opinion_ids": [...]}
```

**shows.json**：

```json
// v1 — 内嵌 + 格式不统一
{
  "warnings": [{...}],
  "opinions": [{...}],  // 仅 3 个演出有
  "tips": [{"content": "...", "source_files": [...]}]  // 前4个为对象数组
}

// v2 — ID 引用 + 格式统一
{
  "warning_ids": [...],
  "opinion_ids": [...],  // 所有演出都有（无关联为空数组）
  "review_ids": [],       // 新增，全部为空数组
  "tips": ["纯文本提示"]   // 统一为纯字符串数组
}
```

---

#### 三、字段命名规范化

**引用字段统一加 `_id` / `_ids` 后缀**：

| v1 | v2 | 说明 |
|----|----|------|
| `zone` (attractions) | `zone_id` | 单值引用加 `_id` |
| `zone` (restaurants) | `zone_id` | 单值引用加 `_id` |
| `zone` (dishes) | `zone_id` | 单值引用加 `_id` |
| `zone` (shows) | `zone_ids` | 单值→多值数组（巡游跨越多园区） |
| `type` (attractions) | `type_id` | 单值引用加 `_id` |
| `type` (shows) | `type_id` | 单值引用加 `_id` |
| `related_attractions` (tips) | `attraction_ids` | 统一命名 |
| `recommended_dishes` (restaurants) | `recommended_dish_ids` | 文本→ID 引用 |
| `attraction_id` (行程) | `attraction_ids` | 单值→多值数组 |
| `show_id` (行程) | `show_ids` | 单值→多值数组 |
| `restaurant_id` (行程) | `restaurant_ids` | 单值→多值数组 |

**布尔字段统一加 `is_` 前缀**：

| v1 | v2 |
|----|----|
| `locker.required: true` | `locker.is_required: true` |
| `queue_strategy.first_batch.recommended: true` | `queue_strategy.first_batch.is_recommended: true` |
| `queue_strategy.non_first_batch.recommended: true` | `queue_strategy.non_first_batch.is_recommended: true` |

**关联字段从可选变为必填**（无关联时为空数组 `[]`）：
- tips 的 `related_attractions`（可选，仅 5 个 tip 有）→ `attraction_ids`（必填，所有 tip 都有）
- 行程项的 `attraction_id`/`show_id`/`restaurant_id`（可选）→ `attraction_ids`/`show_ids`/`restaurant_ids`（必填）
- shows 的 `highlights`（可选，仅 11 个演出有）→ `highlights`（必填，无值为空数组）
- shows 的 `location`（可选，仅 11 个演出有）→ `location`（必填，无值为 null）

---

#### 四、顶层冗余字段清理

v1 在多个文件顶层放置了全局概览字段，v2 中全部移除：

| 文件 | 移除字段 | 内容 | 去向 |
|------|---------|------|------|
| attractions.json | `ranking_overview` | 排名概览字符串 | 移除（已在各项目 ranking 字段中） |
| attractions.json | `mental_preparation` | 心理准备字符串数组 | 移除（已在 tips.json 中） |
| attractions.json | `locker_summary` | 存包概览对象数组 | 移除（已在各项目 locker 字段中） |
| restaurants.json | `overall_review` | 总体评价文本 | 移除（已在 reviews.json 中） |
| restaurants.json | `money_saving_tips[]` | 省钱技巧数组 | 移除（已在 tips.json 中） |
| shows.json | `show_selection_guide[]` | 演出选择推荐 | 移除（冗余信息） |
| shows.json | `general_tips[]` | 通用演出提示 | 移除（已在各 show.tips 中） |

---

#### 五、warnings.json 结构彻底重构

从**两层嵌套**（分类 → 条目列表）变为**完全扁平**（每条 warning 独立实体）。

```json
// v1 — 分类嵌套（9 个分类，每个分类含 items 数组）
{
  "warnings": [
    {
      "id": "warn_shoes",
      "category": "穿鞋避雷",
      "tags": ["tag_clothing"],
      "items": [
        {"content": "一定要穿运动鞋", "severity": "high", "alternative": "...", "source_files": [...]}
      ]
    }
  ]
}

// v2 — 扁平列表（39 条独立 warning）
{
  "warnings": [
    {
      "id": "warn_attr_01",
      "category": "项目避雷",
      "content": "非第一批不要冲禁忌之旅",
      "severity": "high",
      "alternative": "下午花车巡游时去玩",
      "alternative_details": null,
      "tags": ["tag_time_saving"],
      "attraction_ids": ["attr_forbidden_journey"],
      "restaurant_ids": [],
      "show_ids": [],
      "shortcut_ids": [],
      "source_files": ["md_04a"]
    }
  ]
}
```

关键变化：
- ID 从分类级（`warn_shoes`）变为条目级（`warn_attr_01`）
- 消除 `items` 嵌套，每条 warning 独立
- 新增多维度外键：`attraction_ids`、`restaurant_ids`、`show_ids`、`shortcut_ids`
- 新增 `alternative_details` 字段
- 移除 `related_attraction`（单值）和 `related_tags`，统一为 `tags` + `*_ids`

---

#### 六、新增维度信息

| 实体 | 新增字段 | 类型 | 说明 |
|------|---------|------|------|
| attractions | `duration_minutes` | number/null | 项目时长（分钟），v1 仅在 queue_strategy.schedule 内出现一次，v2 提升为每个项目的顶层字段 |
| attractions | `height_requirement` | object/null | 身高限制（`{min_cm, max_cm, note}`），v1 不存在 |
| shows | `location` | string/null | 具体演出位置，v1 中 11 个演出已有（可选），v2 改为必填 |
| restaurants | `location` | string/null | 具体餐厅位置，v1 中 3 个餐厅已有（可选），v2 改为必填 |
| tips | `opinion_ids` | string[] | 关联观点引用，v1 不存在 |

---

#### 七、新增 tags.json 全局标签字典

v1 中标签以文本形式散落在各实体的 `tags` 数组中，没有集中定义。v2 新建 `tags.json`，提供 11 个分类、51 个标签的统一字典：

```json
{
  "categories": [
    {"id": "zone", "name": "园区", "description": "所属园区"},
    {"id": "attraction_type", "name": "项目类型", "description": "游乐项目类型"},
    {"id": "intensity", "name": "刺激程度", "description": "项目刺激等级"},
    {"id": "timing", "name": "时间策略", "description": "推荐游玩时段"},
    {"id": "facility", "name": "设施相关", "description": "存包、拍照等设施"},
    {"id": "audience", "name": "适合人群", "description": "目标受众"},
    {"id": "utility", "name": "实用标签", "description": "省钱省时等"},
    {"id": "meta_tag", "name": "元标签", "description": "数据层面的标记"},
    {"id": "taste", "name": "口味", "description": "菜品口味偏好"},
    {"id": "dish_type", "name": "菜品类型", "description": "菜品/饮品的食物类型"},
    {"id": "preparation", "name": "行前准备", "description": "入园前的准备事项"}
  ],
  "tags": [
    {"id": "tag_zone_harry", "name": "哈利波特区", "category": "zone", "description": "哈利波特魔法世界园区"},
    {"id": "tag_type_ride", "name": "骑乘项目", "category": "attraction_type", "description": "需要排队乘坐的游乐项目"},
    ...
  ]
}
```

所有实体的 `tags[]` 统一引用 `tag_id`，前端通过 `tags.json` 查找标签名、分类、描述。

---

#### 八、新增 meta.json 全局元数据

```json
{
  "last_updated": "2026-04-08",
  "park": {
    "name": "北京环球度假区",
    "name_en": "Universal Studios Beijing",
    "location": "北京市通州区",
    "opening_time": "09:00",
    "closing_time": {"weekday": "20:00", "weekend_holiday": "21:00"},
    "entry_deadline": {"weekday": "19:00", "weekend_holiday": "20:00"},
    "zones": ["哈利波特区", "小黄人区", "侏罗纪区", "变形金刚区", "功夫熊猫区", "水世界", "好莱坞", "城市大道"]
  },
  "version": "2.0.0",
  "source_files": [
    {"id": "src_img_01", "filename": "微信图片_xxx.jpg", "type": "image", "description": "年卡攻略"},
    {"id": "md_04a", "filename": "哈利波特园区.md", "type": "markdown", "description": "哈利波特园区攻略"},
    ...
  ]
}
```

---

#### 九、新增 preparations.json 行前准备百科

v1 中行前准备信息散落在 tips.json 和 warnings.json 中。v2 新建 `preparations.json`，整合为 8 个结构化模块：

```json
{
  "version": "2.0.0",
  "last_updated": "2026-04-08",
  "ticket_prices": {...},
  "parking": {...},
  "locker": {...},
  "rental": {...},
  "park_rules": {...},
  "transportation": {...},
  "clothing": {...},
  "essential_items": [...],
  "prohibited_items": [...],
  "pre_trip_checklist": [...],
  "best_dates": {...},
  "crowd_estimation": {...}
}
```

---

#### 十、新增 shortcuts.json 秘密小道

v1 中捷径信息隐含在 warnings.json 的路线避雷分类中。v2 独立为 `shortcuts.json`：

```json
{
  "shortcuts": [
    {
      "id": "shortcut_01",
      "name": "小黄人区穿行",
      "from": "变形金刚区",
      "to": "小黄人区",
      "route": "通过变形金刚区内部通道...",
      "savings": "节省 10 分钟步行",
      "avoid_mistake": "不要走外面大路",
      "condition": "需在园区开放时间",
      "tags": ["tag_time_saving"],
      "source_files": ["md_03"]
    }
  ]
}
```

---

## v1.x — 2026-04-06

### 初始数据结构

**7 个 JSON 文件**：attractions、shows、restaurants、dishes、tips、warnings、itineraries

**核心特征**：
- reviews/opinions/warnings 内嵌在各实体内部（非独立文件）
- warnings 按分类嵌套（category → items[]），ID 为分类级
- shows 的 tips 格式不统一（前 4 个为对象数组，后 11 个为纯字符串数组）
- 跨实体引用不统一（混用单值 `zone`/`type`、文本匹配 `recommended_dishes: ["菜名"]`、可选数组）
- 关联字段为可选（有值才出现，无值则缺失）
- 无标签字典（tags 以文本散落在各实体中）
- 无全局元数据（园区信息、源文件索引缺失）
- attractions.json 顶层含冗余全局字段（`ranking_overview`、`mental_preparation`、`locker_summary`）
- restaurants.json 顶层含冗余字段（`overall_review`、`money_saving_tips[]`）
- shows.json 顶层含冗余字段（`show_selection_guide[]`、`general_tips[]`）
- 行前准备信息散落在 tips.json 和 warnings.json 中，无独立结构化文件

**数据规模**：17 项目、15 演出、15 餐厅、40 菜品、14 技巧、39 避雷、2 行程
