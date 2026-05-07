# Workflow — 攻略离线H5生成流程

## 概述

Schema 驱动架构：
- `schema.json` 定义数据结构
- `generator/schema_generator.py` 读取 Schema 生成索引
- Jinja2模板 `generator/guide_template.html` 渲染
- 输出单HTML文件 `output/guide.html`

## 流程图

```
schema.json (Schema定义)
      │
      ▼
data/*.json (13个JSON文件)
      │
      ▼
┌─ schema_generator.py ─────────────────┐
│  1. load_all_data()                   │
│  2. build_maps()                      │  ← ID→对象 Map 构建
│  3. build_indexes()                   │
│     ├─ tag_index                      │
│     ├─ zone_index                     │
│     ├─ backrefs                       │
│     └─ alternative_index              │
│  4. _to_plain() + json.dumps()        │
│  5. Jinja2 render(guide_template.html)│
└───────────────────────────────────────┘
      │
      ▼
output/guide.html (~350KB)
```

## 步骤详解

### 步骤1：加载数据

`load_all_data()` 加载 `data/` 目录下13个JSON文件，返回字典：

```python
{
    "meta", "tags", "attractions", "shows", "restaurants",
    "shortcuts", "itineraries", "tips", "warnings", "preparations",
    "dishes", "reviews", "opinions"
}
```

### 步骤2：构建查找映射

`build_maps()` 为 8 种实体类型构建 ID→对象 Map，实现 O(1) 查找：

```python
maps = {
    "attractions": {id: attraction, ...},
    "shows": {id: show, ...},
    "restaurants": {id: restaurant, ...},
    "dishes": {id: dish, ...},
    "tips": {id: tip, ...},
    "shortcuts": {id: shortcut, ...},
    "warnings": {id: warning, ...},
    "itineraries": {id: itinerary, ...},
    "reviews_by_target": {target_id: [reviews], ...},
    "opinions_by_target": {target_id: [opinions], ...},
    "warnings_by_target": {target_id: [warnings], ...},
}
```

这些 Map 被序列化后注入模板，前端通过 `find(id, type)` 函数实现 O(1) 实体查找。

### 步骤3：构建索引

`build_indexes()` 返回包含4个索引的字典。

#### 3.1 tag_index

遍历8类实体（attractions/shows/restaurants/dishes/shortcuts/tips/warnings/itineraries），按每个实体的 `tags[]` 字段建索引。

输出结构：

```
{tag_id: {entity_type: [entity_ids]}}
```

#### 3.2 zone_index

遍历有 `zone_ids` 字段的实体，按 `zone_ids[]` 数组中的每个元素分组。

输出结构：

```
{zone_tag_id: {entity_type: [entity_ids]}}
```

#### 3.3 backrefs

从3个数据源中提取对实体的反向引用：

| 数据源 | 提取字段 | 提取内容 |
|--------|---------|---------|
| `tips[].attraction_ids` | `attraction_id` | `{id, title}` |
| `warnings[].attraction_ids` / `show_ids` / `restaurant_ids` / `shortcut_ids` | 各实体 ID | `{content, severity, category}` |
| `itineraries[].time_slots[].items[]` | `attraction_ids/show_ids/restaurant_ids` | `{id, name, time, action}` |

输出结构：

```
{entity_id: {tips: [...], warnings: [...], itineraries: [...]}}
```

#### 3.4 alternative_index

从两个数据源提取替代关系：

- `warnings[].alternative` → `{type, entity_id, name, reason}`
- `dishes[].alternatives[]` → `{type: "dish", entity_id, name: "", reason: note, alt_type}`

输出结构：

```
{entity_id: [{type, entity_id, name, reason}]}
```

### 步骤4：序列化

内部 `_to_plain()` 递归将 `defaultdict` 转换为普通 `dict`，然后：

```python
data_blob = json.dumps(data, ensure_ascii=False, indent=None, separators=(",", ":"))
indexes_blob = json.dumps(indexes, ensure_ascii=False, indent=None, separators=(",", ":"))
```

### 步骤5：模板渲染

Jinja2渲染 `guide_template.html`，通过 `{{ data_blob | safe }}` 和 `{{ indexes_blob | safe }}` 注入到 `<script>` 标签中的 `DATA` 和 `INDEXES` 全局变量。使用 `| safe` 而非 `| tojson | safe`，避免双重序列化。

### 步骤6：输出

写入 `output/guide.html`，打印文件大小。

## 前端运行时

### 路由系统

hash路由。`router()` 解析 `location.hash`，按 `/` 分割得到 `page` 和 `param`，查 `DETAIL`/`LIST` 映射调用对应渲染函数。路由统一使用复数类型名（如 `attractions/{id}` 而非 `attraction/{id}`），无需单复数映射。非首页自动拼接 `breadcrumb()` 结果。共23个路由：

```
DETAIL = { attractions, shows, restaurants, dishes, itineraries, tips, warnings, shortcuts, tags, preparations }
LIST = { home, attractions, shows, show_schedule, restaurants, dishes, itineraries, tips, warnings, shortcuts, tags, preparations, more }
```

### 筛选系统

统一状态管理：`const filters = { attractions: 'all', shows: 'all', restaurants: 'all', dishes: 'all' }`，通过 `setFilter()` 工厂函数创建筛选器。

| 筛选器 | 影响的渲染函数 |
|--------|--------------|
| `setAttrFilter` | `renderAttractionList()` |
| `setShowFilter` | `renderShowList()` |
| `setRestFilter` | `renderRestaurantList()` |
| `setDishFilter` | `renderDishList()` |

筛选逻辑：按 `zone_ids` 或 `tags` 匹配。

### 轮播系统

- `startCarousel()` — 启动定时器，每5秒调用 `shuffleCarouselContent()`
- `stopCarousel()` — 清除定时器
- `shuffleCarouselContent()` — 随机选取并展示轮播内容
- `hashchange` 时先 `stopCarousel()`，若回到首页则 `startCarousel()`
- `visibilitychange` 时暂停/恢复

### 面包屑系统

`PAGE_META` 定义22个路由的 `label` 和 `parent` 父子关系。`breadcrumb(page, param)` 构建路径链：从当前路由沿 parent 链追溯到 home，详情页通过 parent 直接映射到列表页（统一复数类型名），最后一项用 `bc-here` 样式，其余用 `bc-item` 可点击样式。

### 渲染函数清单

| 函数 | 路由 | 说明 |
|------|------|------|
| `renderHome()` | `home` | 首页：9宫格 + Top5 + 轮播 + 心理准备 |
| `renderStatGrid()` | — | 首页子组件：9宫格导航 |
| `renderTop5Chart()` | — | 首页子组件：排名柱状图 |
| `buildCarouselSlides()` | — | 首页子组件：轮播数据构建 |
| `renderCarousel(slides)` | — | 首页子组件：轮播容器渲染 |
| `renderSlideContent(s)` | — | 首页子组件：单页轮播内容 |
| `renderFallbackSections(slides)` | — | 首页子组件：无轮播时的降级展示 |
| `renderMentalPrep()` | — | 首页子组件：心理准备 |
| `renderAttractionList()` | `attractions` | 项目列表，支持园区筛选 |
| `renderAttractionDetail(id)` | `attractions/:id` | 项目详情 + backrefs |
| `renderShowList()` | `shows` | 演出列表，支持园区筛选 |
| `renderShowDetail(id)` | `shows/:id` | 演出详情 + backrefs |
| `renderShowSchedule()` | `show_schedule` | 演出时间轴视图 |
| `renderRestaurantList()` | `restaurants` | 餐厅列表，支持园区筛选 |
| `renderRestaurantDetail(id)` | `restaurants/:id` | 餐厅详情 + backrefs |
| `renderDishList()` | `dishes` | 菜品列表，支持园区筛选 |
| `renderDishDetail(id)` | `dishes/:id` | 菜品详情 + alternative_index |
| `renderItineraryList()` | `itineraries` | 行程列表 |
| `renderItineraryDetail(id)` | `itineraries/:id` | 行程详情（time_slots时间线） |
| `renderTipList()` | `tips` | 技巧列表 |
| `renderTipDetail(id)` | `tips/:id` | 技巧详情 + 关联项目 |
| `renderWarningList()` | `warnings` | 避雷列表（按严重度排序） |
| `renderWarningDetail(id)` | `warnings/:id` | 避雷详情 + 关联实体 |
| `renderPreparations()` | `preparations` | 行前准备主页（8模块入口） |
| `renderPreparationDetail(section)` | `preparations/:section` | 行前准备子页（配置表驱动） |
| `renderShortcutList()` | `shortcuts` | 秘密小道列表 |
| `renderShortcutDetail(id)` | `shortcuts/:id` | 秘密小道详情 |
| `renderTagCloud()` | `tags` | 标签云 |
| `renderTagContent(tagId)` | `tags/:tagId` | 标签下的所有实体 |
| `renderMore()` | `more` | 更多页面 |

### 通用渲染函数

| 函数 | 作用 |
|------|------|
| `renderReviews(entityId)` | 渲染评价区块（按情感分组） |
| `renderOpinions(entityId)` | 渲染对立观点区块 |
| `renderWarnings(entityId)` | 渲染关联避雷区块（按严重度排序） |
| `renderFilterBar(filterValue, filterFnName)` | 渲染园区筛选按钮组 |
| `renderEntityLinks(title, type, ids, nameField, icon)` | 渲染实体链接列表（支持自定义图标） |

### 关键辅助函数

| 函数 | 作用 |
|------|------|
| `find(id, type)` | 基于 Map 的统一实体查找（O(1)） |
| `tagLookup(tagId)` | tag_id → 标签名（可点击，带分类样式） |
| `tagsHtml(tagIds, clickable)` | 标签ID数组 → HTML胶囊 |
| `zonesHtml(zoneIds)` | 园区ID数组 → 园区名称HTML |
| `getTypeTag(tags)` | 从 tags 中提取类型标签（attraction_type 分类） |
| `getTypeIcon(tags)` | 从 tags 中提取类型图标 |
| `dishRestaurantName(dish)` | 菜品 → 所属餐厅名称 |
| `renderRelations(entityId)` | 渲染关联区（同园区 + backrefs） |
| `resolveEntityName(page, id)` | 路由+ID → 实体显示名 |
| `resolveEntityZone(entityId)` | 实体ID → 所属园区zone_tag_id |
| `categoryLookup(catId)` | category_id → 分类名 |
| `starsHtml(rating)` | 评分 → 星级字符串 |
| `severityHtml(sev)` | 严重度 → 彩色标签 |
| `severityIcon(sev)` | 严重度 → emoji图标 |
| `sortBySeverity(a, b)` | 按严重度排序比较函数 |

## 数据更新流程

```bash
# 验证数据完整性（基于 Schema）
python scripts/schema_validator.py

# 生成攻略主页
python generator/schema_generator.py
```

## 工具脚本

- `scripts/schema_validator.py` — Schema 驱动数据验证
- `scripts/analyze_data.py` — 数据结构分析
- `scripts/export_xlsx.py` — 导出 Excel
- `scripts/stats.py` — 数据统计

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.6+ | 运行生成脚本 |
| Jinja2 | 3.x | HTML模板渲染 |

安装：`pip install jinja2`

## 产物规格

| 属性 | 值 |
|------|-----|
| 文件格式 | 单HTML文件 |
| 文件大小 | ~350 KB |
| 字符编码 | UTF-8 |
| 外部依赖 | 无（CSS/JS/JSON全部内嵌） |
| 离线可用 | 是 |
| 浏览器兼容 | 现代浏览器 + 微信内置浏览器 |
