# 环球攻略指南生成器 — 使用教程

## 这是什么？

一套基于此项目改造的、AI 驱动的「素材 → 交互式网页」生成流水线。

**你不需要写代码、不需要手写 JSON、不需要理解技术细节。**

你只需要做三件事：

1. 把项目文件夹发给 AI
2. 告诉 AI 你想做什么
3. 审核结果

其余全部由 AI 完成。

---

## 全局概览：这份文档怎么用

这份文档里有两类内容，用途完全不同：

| 标识 | 谁看 | 用途 |
|:--|:--|:--|
| 普通文字 | **你（用户）** | 理解流程、知道自己在干什么 |
| `📋 复制发给 AI` 代码块 | **AI** | 你复制后粘贴给 AI 的指令 |

**你的阅读路径：**

1. 先读「一、三步上手」— 知道整体要做什么
2. 再读「二、角色分工」— 明白你负责什么、AI 负责什么
3. 找到第三节中标记为 `📋 复制发给 AI` 的代码块 — **完整复制**
4. 把复制的内容发给 AI — 之后就是对话协作了

---

## 一、三步上手

### 第 1 步：打开 AI 编程助手，把整个项目文件夹发过去

> 这是给用户看的操作说明

使用支持**读写项目文件 + 执行命令**的 AI 编程助手（也叫 AI Agent / IDE 工具），例如：

| AI 助手 | 说明 |
|--------|------|
| **Trae**（字节跳动） | 免费，支持上传项目文件夹，能读文件、改文件、执行终端命令 |
| **Cursor** | 支持 Copilot++ 模式，能直接操作项目文件 |
| **Claude**（Anthropic） | 支持拖拽项目文件夹，代码能力强 |
| **Codex**（OpenAI） | 专门的编程 Agent |
| **Windsurf**（前 Codeium） | 支持 Cascade 模式自动改代码 |

不要用只能聊天的普通对话窗口。你需要的是一个**能直接读写你电脑上文件并运行命令的 AI 工具**。

**关键能力检查：你用的工具必须同时满足**

1. 能读取/写入项目中的文件
2. 能在终端执行 `python scripts/ci.py` 这样的命令
3. 上下文窗口够大（装得下整个项目）

**操作方法：**
- 在 AI 助手中新建一个对话 / 打开一个工作区
- 导入或拖入本项目的根文件夹（就是包含 `data/`、`generator/`、`scripts/` 的那个文件夹）
- 确认 AI 能看到完整的目录结构

### 第 2 步：把下面的规范发给 AI

> 这是给用户看的操作说明

找到第三节的 `📋 复制发给 AI` 代码块，完整复制里面的所有内容，发送给你的 AI 对话窗口。

这段内容是写给 AI 看的工作规范。它告诉 AI：
- 应该先读取哪些文件
- 数据格式要求是什么
- 改代码时必须联动修改哪些地方
- 出错了该怎么修

### 第 3 步：跟 AI 对话

> 这是给用户看的流程说明

之后就是自然语言对话：

```
你说："我想做一个上海迪士尼攻略"
  → AI 读文件 → 问你几个问题

你回答问题 / 提供素材
  → AI 提取数据 → 写入 JSON 文件

AI 自动运行校验命令
  → 通过 → 生成网页 → 打开看效果 → 完成
  → 失败 → AI 自动修复 → 重跑 → 循环直到通过
```

---

## 二、角色分工

> 这是给用户看的参考表

| | 你（人） | AI |
|--|---------|----|
| **做什么** | 决策、提供素材、审核结果、确认方案 | 读写数据、改代码、跑命令、修报错 |
| **不做什么** | 不手写 JSON、不记字段名、不改代码、不碰终端 | 不擅自拍板（方案需你确认） |
| **沟通方式** | 自然语言说中文就行 | 自然语言 + 执行技术操作 |

一句话总结：**你是产品经理，AI 是你的全栈工程师。**

---

## 三、AI 工作规范

> 下面这个代码块是核心。
> **你要做的：从 `📋` 开始，一直复制到 `📋` 结束，完整粘贴给 AI。**

> **AI 收到后会做什么：**
> 按照这套规范去读取项目文件、提取数据、修改代码、运行校验、生成最终页面。

```markdown 📋 复制发给 AI — AI 规范全文 📋
# 你的角色

你是一个专业的技术执行者。用户想基于「环球攻略指南」项目做一个新的交互式指南网页。
你的职责是：从素材中提取结构化数据 → 按规范填入 JSON → 必要时改代码/模板/校验规则 → 运行 CI 确保 → 产出可用的离线 HTML 页面。

---

# 第零步：读取全部上下文（强制，不可跳过）

在你做任何事之前，必须依次读取以下 12 个文件。**每读一个都要确认自己理解了它的内容和作用。**

## 必读清单

| # | 文件 | 为什么要读 |
|---|------|-----------|
| 1 | `docs/usage.md` | 工作流程和规范（就是本文件） |
| 2 | `data/v3/meta.json` | 项目元信息配置结构 |
| 3 | `data/v3/attractions.json` | **最关键的参考**——字段最复杂、嵌套最深，其他实体都参考它的模式 |
| 4 | `data/v3/restaurants.json` | 餐厅实体的真实字段名和结构 |
| 5 | `data/v3/dishes.json` | 菜品及替代关系（alternatives）的结构 |
| 6 | `data/v3/tips.json` | 技巧如何引用其他实体 |
| 7 | `data/v3/warnings.json` | 避雷如何同时关联多种实体 |
| 8 | `data/v3/tags.json` | 标签分类体系（有 categories + tags 双层结构） |
| 9 | `data/v3/shows.json`, `shortcuts.json`, `itineraries.json`, `reviews.json`, `opinions.json`, `preparations.json` | 其余全部数据文件 |
| 10 | `generator/generate_guide.py` | 数据加载逻辑、索引构建逻辑、如何传给模板 |
| 11 | `generator/guide_template.html` | 每个字段在页面上怎么渲染（render 函数） |
| 12 | `scripts/ci.py` | 校验规则——什么数据合法、什么不合法 |

**缺少任何一个都会导致生成的数据无法通过校验或页面渲染异常。**

## 读完后自检（确保真正读懂了）

回答以下问题。如果不确定任何一个答案，回去重读对应文件：

- `_ENTITY_TYPES` 列表包含哪几种类型？
- attractions 的 `height_requirement` 是字符串还是对象？有哪些子字段？
- `locker` / `queue_strategy` / `seat_advice` 分别是什么结构？
- warnings 怎么同时关联 attraction / show / restaurant / shortcut？
- dishes 的 `alternatives` 是简单 ID 数组还是对象数组？里面有什么字段？
- tags.json 有没有顶层 `categories` 数组？和 `tags` 数组什么关系？
- reviews / opinions 用什么字段指向目标实体？（entity_id 还是 target_id？）
- `build_bidirectional_index()` 里硬编码了哪些字段名？
- guide_template.html 有几个 render 函数？各渲染哪种实体？

**原则：不要猜测字段名。以现有 JSON 文件中的实际字段名为唯一标准。**

---

# Phase 1：确认需求

向用户确认四件事：

1. **主题** — "上海迪士尼攻略"？ "成都美食地图"？还是别的？
2. **素材** — Markdown 笔记？ 截图？ 备忘录文本？ 还是你直接口述？
3. **实体类型** — 从现有 8 种主实体中选择需要的（attractions, shows, restaurants, dishes, tips, warnings, shortcuts, itineraries）
4. **是否需要改动结构** — 只换数据？还是要增减实体类型或字段？

给出方案后 **等待用户确认再动手**。不跳过确认环节。

---

# Phase 2：按真实字段结构提取数据

> 以下是每种实体的完整字段定义。
> 这些字段名来自 data/v3/*.json 的实际内容，不是概括。
> 提取数据时必须严格使用这些字段名。

## attractions（游乐项目）

```json
{
  "id": "attr_xxx",
  "name": "名称",
  "subtype": "子类型描述",
  "rating": 5,
  "ranking": 1,
  "tags": ["tag_xxx"],
  "locker": {
    "timing": "存包时机",
    "phone_allowed": true,
    "pickup_location": "取包位置",
    "notes": "详细说明",
    "is_required": true
  },
  "queue_strategy": {
    "first_batch": {"description": "...", "is_recommended": true},
    "non_first_batch": {"description": "...", "is_recommended": false},
    "best_timing": "最佳时段",
    "threshold_minutes": 30,
    "threshold_rule": "排队阈值规则"
  },
  "seat_advice": [
    {"position": "位置", "experience": "体验", "how_to_get": "获取方法"}
  ],
  "source_files": ["src_xxx"],
  "review_ids": ["rev_xxx"],
  "opinion_ids": ["opi_xxx"],
  "warning_ids": ["warn_xxx"],
  "duration_minutes": 5,
  "height_requirement": {
    "min_cm": 122,
    "max_cm": null,
    "note": "备注"
  },
  "zone_ids": ["tag_zone_xxx"],
  "indoor": true,
  "water_splash": false,
  "single_rider": false,
  "has_photo": true
}
```

## restaurants（餐厅）

```json
{
  "id": "rest_xxx",
  "name": "名称",
  "tags": ["tag_xxx"],
  "source_files": ["src_xxx"],
  "recommended_dish_ids": ["dish_xxx"],
  "location": "位置描述",
  "review_ids": ["rev_xxx"],
  "opinion_ids": ["opi_xxx"],
  "zone_ids": ["tag_zone_xxx"],
  "warning_ids": ["warn_xxx"],
  "average_price": 120,
  "indoor": true,
  "business_hours": "10:00-20:30"
}
```

## dishes（菜品）

```json
{
  "id": "dish_xxx",
  "name": "菜名",
  "restaurant_ids": ["rest_xxx"],
  "alternatives": [
    {"dish_id": "dish_yyy", "type": "similar_taste 或 budget_alternative", "note": "说明"}
  ],
  "source_files": ["src_xxx"],
  "review_ids": ["rev_xxx"],
  "opinion_ids": ["opi_xxx"],
  "tags": ["tag_xxx"],
  "zone_ids": ["tag_zone_xxx"],
  "price": 168,
  "is_seasonal": false
}
```

## tips（技巧）

```json
{
  "id": "tip_xxx",
  "category": "分类名称",
  "title": "标题",
  "content": "详细内容",
  "tags": ["tag_xxx"],
  "source_files": ["src_xxx"],
  "attraction_ids": ["attr_xxx"],
  "opinion_ids": []
}
```

## warnings（避雷）

```json
{
  "id": "warn_xxx",
  "category": "分类",
  "content": "避雷内容",
  "severity": "high / medium / low",
  "alternative": "替代方案（无则 null）",
  "alternative_details": null,
  "tags": ["tag_xxx"],
  "attraction_ids": ["attr_xxx"],
  "restaurant_ids": [],
  "show_ids": [],
  "shortcut_ids": [],
  "source_files": ["src_xxx"],
  "zone_ids": ["tag_zone_xxx"]
}
```

## tags（标签）

> 注意：结构与普通实体不同，有 categories 和 tags 两层

```json
{
  "version": "3.2.0",
  "categories": [
    {"id": "zone", "name": "园区", "description": "所属园区"},
    {"id": "attraction_type", "name": "项目类型", ...}
  ],
  "tags": [
    {"id": "tag_zone_harry", "name": "哈利波特区", "category": "zone", "color": "#..."}
  ]
}
```

## reviews（评价）

```json
{
  "id": "rev_attr_01",
  "target_type": "attraction",
  "target_id": "attr_forbidden_journey",
  "content": "评价内容",
  "sentiment": "positive",
  "source_files": ["md_xxx"]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `target_type` | string | 目标实体类型（attraction/show/restaurant/dish） |
| `target_id` | string | 目标实体 ID |
| `content` | string | 评价内容 |
| `sentiment` | string | 情感倾向：positive/negative/neutral |

## opinions（观点）

```json
{
  "id": "op_xxx",
  "target_type": "attraction",
  "target_id": "attr_xxx",
  "stance": "pro",
  "claim": "观点主张",
  "reasoning": "论证理由",
  "source_files": ["md_xxx"]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `target_type` | string | 目标实体类型 |
| `target_id` | string | 目标实体 ID |
| `stance` | string | 立场：pro（正方）/ contra（反方） |
| `claim` | string | 观点主张（一句话） |
| `reasoning` | string | 详细论证理由 |

## 其余实体

shows / shortcuts / itineraries / preparations — 请直接读取 `data/v3/` 下对应文件作为参考。**不要假设字段名，必须与现有文件一致。**

## ID 命名规范

格式：`{前缀}_{有意义的英文标识}`

| 类型 | 格式 | 示例 |
|------|------|------|
| attractions | `attr_` + 标识 | `attr_forbidden_journey`, `attr_dd_space_mountain` |
| restaurants | `rest_` + 标识 | `rest_three_broomsticks` |
| dishes | `dish_` + 标识 | `dish_roast_chicken_ribs` |
| shows | `show_` + 标识 | `show_universal_parade` |
| tips | `tip_` + 标识 | `tip_toilet_card` |
| warnings | `warn_` + 标识 | `warn_attr_01`, `warn_dining_16` |
| shortcuts | `shortcut_` + 标识 | `shortcut_backstage_01` |
| itineraries | `itin_` + 标识 | `itin_full_day_01` |
| reviews | `rev_` + 目标缩写 + 编号 | `rev_attr_01`, `rev_rest_03` |
| opinions | `opi_` + 标识 | `opi_tb_must` |
| tags | `tag_` + 分类_标识 | `tag_zone_harry`, `tag_time_saving` |

ID 在整个项目中全局唯一，不可重复。

## 引用关系规范（极其关键）

1. **被引用的 ID 必须存在** — 所有 `_ids` 字段中的值必须在目标 JSON 文件中找得到
2. **双向关系必须一致**：
   - restaurant.recommended_dish_ids 含 dish X → dish.restaurant_ids 必含该 restaurant
   - dish.alternatives[].dish_id 必须是真实存在的 dish ID
   - warning 的 attraction_ids / restaurant_ids / show_ids / shortcut_ids 都必须是真实 ID
3. **标签引用** — entity.tags 和 entity.zone_ids 中引用的 tag ID，必须在 tags.json 的 tags 数组中存在
4. **标签分类** — tag.category 的值必须在 tags.json 的 categories 数组中有对应 id

---

# Phase 3：联动修改规则（最重要！违反必出错）

这套系统有 4 个组件通过字段名紧密耦合。**改其中一个必须检查其余三个。**

组件关系：

```
data/v3/*.json          ← 数据（声明了有哪些字段）
     ↕ 字段名必须一致
generate_guide.py       ← 生成器（读取这些字段、构建索引）
     ↕ 变量名必须一致  
guide_template.html      ← 模板（渲染这些字段到页面）
     ↕ 校验规则必须匹配
scripts/ci.py            ← CI（检查这些字段的合法性）
```

下面按场景列出具体要改什么。

## 场景 A：只换数据不改结构（最常见）

比如把环球影城换成迪士尼，8 种实体类型不变。

**只改 data/v3/ 下的文件** —— 替换数据内容即可。

不需要改 generate_guide.py / guide_template.html / ci.py。

## 场景 B：去掉某些实体类型

比如用户说"我不需要 shows 和 shortcuts"。

需要**同步改 4 个地方**：

**(1) data/v3/**
- 清空 shows.json 和 shortcuts.json 的内容（保留空壳或删掉实体数组）

**(2) generator/generate_guide.py**
- 从 `_ENTITY_TYPES` 列表中删掉 `"shows"` 和 `"shortcuts"`
- 从 `build_bidirectional_index()` 的 `entity_collections` 中删掉对应项
- 如果有代码硬编码遍历 show_ids / shortcut_ids（warnings 索引构建处），清理掉
- **搜索整个文件，确认没有遗漏引用**

**(3) generator/guide_template.html**
- 删掉 `renderShowList()` 和 `renderShowDetail()` 函数
- 删掉 `renderShortcutList()` 和 `renderShortcutDetail()` 函数
- 修改首页导航网格（减少对应入口）
- 删掉路由（hash change handler）中的对应 case
- **搜索整个文件，确认没有遗漏调用**

**(4) scripts/ci.py**
- 去掉对 shows / shortcuts 的字段完整性检查
- 去掉 ID 格式校验中的对应前缀
- 去掉双向链接一致性检查中的对应关系
- 检查是否有交叉校验依赖这两个类型

**改完立刻跑 `python scripts/ci.py` 验证。**

## 场景 C：新增实体类型

比如用户说"我要加一个 shopping（购物）"。

需要**同步改 4 个地方**：

**(1) 新建 data/v3/shopping.json**
```json
{
  "version": "3.2.0",
  "last_updated": "2026-xx-xx",
  "shopping": [
    {
      "id": "shop_xx",
      "name": "店铺名称",
      "tags": ["tag_xxx"],
      "zone_ids": ["tag_zone_xxx"],
      "其他字段": "..."
    }
  ]
}
```
字段设计参考 attractions 或 restaurants 的模式。

**(2) generator/generate_guide.py**
- `_ENTITY_TYPES` 加 `"shopping"`
- `load_all_data()` 加 shopping 的加载
- `build_lookup_maps()` 会自动处理（因为遍历 _ENTITY_TYPES）
- `build_bidirectional_index()` 的 `entity_collections` 加 shopping
- 如果 tips/warnings/reviews 要关联 shopping，在 backrefs 构建逻辑中加对应处理

**(3) generator/guide_template.html**
- 新增 `renderShoppingList()` 函数（参照 renderAttractionList 的模式）
- 新增 `renderShoppingDetail()` 函数（参照 renderAttractionDetail 的模式）
- 首页导航网格加 shopping 入口
- 路由加 shopping 的 case

**(4) scripts/ci.py**
- 加 shopping 的字段完整性校验
- 加 ID 格式校验
- 加引用完整性校验
- 加双向链接一致性检查（`bidir_checks` 列表新增一组正向→反向校验）

**改完立刻跑 `python scripts/ci.py` 验证。**

## 场景 D：给某实体增加/删除字段

比如"attractions 要加 ticket_price 字段"。

**(1) data/v3/attractions.json** — 每个对象加上 `"ticket_price": 99`
**(2) guide_template.html** — renderAttractionDetail() 中加上渲染新字段的 HTML
**(3) （可选）ci.py** — 如果要对新字段加校验

**如果删除字段**：同样要在模板中移除对应的 `{{ }}` 渲染，否则 Jinja2 报 undefined 错误导致生成失败。

## 场景 E：只调样式

比如"换个颜色"。

只改 guide_template.html 的 CSS 变量（`:root` 部分）。不动数据、不动 Python。

---

# Phase 4：CI 校验

运行：`python scripts/ci.py`

- ✅ 全 PASS → 进入 Phase 5
- ❌ 有 FAILED → 进入修复循环

## 修复循环（最多自修复 3 轮）

1. 逐条阅读错误信息
2. 定位到具体文件和字段
3. 修复
4. 重跑 `python scripts/ci.py`
5. 如仍有错误 → 重复

**3 轮后仍有未修复错误 → 停止，向用户报告完整错误日志，说明哪些需要用户确认事实信息。**

---

# Phase 5：预览与迭代

让用户打开 `output/guide.html` 预览。根据反馈调整。

**每次调整后（无论改数据还是代码），都必须重跑 `python scripts/ci.py` 直到全 PASS。**

---

# 最高优先级原则（违反任一条都导致失败）

1. **字段名精确匹配** — JSON 中的字段名、Python 代码中的键名、模板中的变量名、CI 中的校验字段，四者必须完全一致。以现有 data/v3/*.json 为唯一标准
2. **改动必联动** — 改数据结构时必须同步检查并修改 generate_guide.py + guide_template.html + ci.py。漏一个就报错
3. **每次改完必跑 CI** — 任何修改后必须执行 `python scripts/ci.py` 并看到全 PASS
4. **不确定就不编** — 不确定的数据写 null 或问用户
5. **保持一致** — 同一项目中区域缩写、ID 风格统一
6. **报错原样呈现** — CI 失败时把完整输出贴给用户，不总结不简化
```markdown 📋 AI 规范结束 📋

> 以上是完整的 AI 规范。
> **你现在需要做的就是：复制上面从 📋 到 📋 的全部内容，粘贴给 AI。**

---

## 四、三种使用场景

### 场景 1：换主题，不改结构（最简）

适合：另一个游乐园、类似的多分类攻略

**你需要做的：**

1. 上传项目文件夹给 AI
2. 复制第三节 `📋 复制发给 AI` 的内容发给 AI
3. 对 AI 说：

```
我想做一个上海迪士尼攻略。素材在 src/ 目录下。请开始吧。
```

4. 等 AI 处理完毕，打开 `output/guide.html` 看效果
5. 有问题就告诉 AI，让它修

### 场景 2：减掉一些实体类型

适合：美食地图（只要餐厅+菜品+技巧）、读书笔记（只要书+评价）

**你需要做的：**

1. 上传项目文件夹给 AI
2. 复制第三节 `📋 复制发给 AI` 的内容发给 AI
3. 对 AI 说：

```
我想做一个成都美食地图。
只需要 restaurants / dishes / tips / warnings / tags 这几种。
不需要 attractions / shows / shortcuts / itineraries。
素材我贴给你看。
```

4. AI 会按照「场景 B：去掉某些实体类型」的规则同步改 4 类文件
5. AI 给出方案 → 你确认 → AI 执行 → 你预览

### 场景 3：全新主题（最大改动）

适合：电影数据库、书单推荐等完全不同的东西

**你需要做的：**

1. 上传项目文件夹给 AI
2. 复制第三节 `📋 复制发给 AI` 的内容发给 AI
3. 对 AI 说：

```
我想做一个个人影单推荐页面。
需要的实体是：movies(电影)、directors(导演)、actors(演员)、reviews(影评)。
字段跟现在的完全不一样。
请你改造整个项目来适配。
```

4. AI 按「场景 C：新增实体类型」的规则新建实体、改代码、改模板、改 CI
5. 全程你只需要审核方案和数据准确性

---

## 五、常用命令

> 这个代码块是给你参考的。一般情况下 AI 会自动执行这些命令。

```bash
# 完整流程：校验 → 生成 HTML → 验证产物
python scripts/ci.py

# 仅生成 HTML（跳过校验，不推荐跳过）
python generator/generate_guide.py

# 导出 Excel
python scripts/export_xlsx.py

# 数据分析（生成图表）
python scripts/analyze_data.py
```

---

## 六、文件总览

> 帮你快速找到东西在哪

```
环球攻略指南html/
│
├── data/v3/                          ← ★ 数据层（AI 读写数据的地方）
│   ├── meta.json                     ← 项目名称、园区配置
│   ├── attractions.json              ← 游乐项目
│   ├── shows.json                    ← 演出
│   ├── restaurants.json              ← 餐厅
│   ├── dishes.json                   ← 菜品
│   ├── tips.json                     ← 技巧
│   ├── warnings.json                 ← 避雷
│   ├── shortcuts.json                ← 小道
│   ├── itineraries.json              ← 行程
│   ├── reviews.json                  ← 评价
│   ├── opinions.json                 ← 观点
│   ├── tags.json                     ← 标签（有分类体系）
│   └── preparations.json             ← 行前准备
│
├── generator/
│   ├── generate_guide.py             ← 生成器（改实体时 AI 要改这里）
│   └── guide_template.html           ← 页面模板（改样式/字段时 AI 要改这里）
│
├── scripts/
│   ├── ci.py                         ← CI 守门员（改实体时 AI 要改这里）
│   ├── analyze_data.py               ← 分析工具
│   └── export_xlsx.py                ← 导出工具
│
├── output/                           ← ★ 最终产物在这里
│   ├── guide.html                    ← 你的攻略网页（打开即用）
│   └── v3_data.xlsx                  ← Excel 版
│
└── src/                              ← 你的原始素材放这
```

**四个组件的联动关系：**

```
data/v3/*.json (数据)        ← 声明字段
     ↕ 字段名必须完全一致
generate_guide.py (生成器)   ← 读取字段、建索引
     ↕ 注入变量名必须一致
guide_template.html (模板)   ← 渲染字段到页面
     ↕ 校验规则必须匹配数据
scripts/ci.py (守门员)       ← 检查字段合法性

→ 这是一个整体，改一处必须检查其余三处
```

---

## 七：为什么不会乱？

你可能担心：让 AI 自由发挥，数据会不会一团糟？

答案是不会。因为有 **CI 脚本作为不可绕过的守门员**。

工作流程中有这道安全网：

```
AI 写入数据 / 修改代码
        ↓
  python scripts/ci.py   ← 强制检查（写在代码里的硬规则）
        ↓
    ├─ ✅ 全 PASS  →  生成 HTML  →  成功
    └─ ❌ 有 FAIL  →  AI 必须修  →  重跑  →  循环直到 PASS
```

CI 具体检查的内容：

| 检查项 | 说明 |
|--------|------|
| ID 格式 | 每个 id 是否符合 `{前缀}_{标识}` 格式 |
| 引用完整性 | A 引用了 B 的 id，B 必须真实存在（无悬空引用） |
| 字段完整性 | 必需字段不能少，数据类型不能错 |
| 双向一致性 | A 关联 B，B 也必须关联 A |

这些规则写在 `scripts/ci.py` 的代码里，**不是靠 AI 自觉遵守**。AI 写错了就会被拦截。

所以本质上是：你在有安全网的环境里和 AI 自由协作，CI 永远不会放过错误。

---

## 八、常见问题

### 我不懂编程能用吗？

能。全程不需写一行代码、不需打开终端。只需说话、看结果、提意见。

### 用哪个 AI 好？

推荐同时满足这三个条件的：

1. 能上传整个项目文件夹（Claude 支持）
2. 能执行终端命令（跑 python scripts/ci.py）
3. 上下文够长（装下全部代码 + 数据 + 教程 + 你的对话）

### AI 生成的数据准确吗？

取决于两点：

1. **素材质量** — 你的笔记越详细越结构化，AI 提取越准
2. **你的审核** — 你是领域专家，一眼就能看出明显错误

建议流程：AI 出初稿 → 你快速浏览一遍 → 把错误列出来 → AI 批量修复。

### CI 一直报错怎么办？

把完整报错日志贴给 AI，再加上这句：

> "这是 ci.py 的报错。逐条定位到具体文件和字段修复，然后重跑 python scripts/ci.py。循环直到全 PASS。"

3 轮还修不好时，AI 应该来找你确认事实性信息。

### 能做游乐园以外的东西吗？

可以。第四节的三种场景覆盖了从易到难的全部情况：
- 场景 1：换汤不换药（5 分钟）
- 场景 2：减掉不需要的类型（15 分钟）
- 场景 3：全新定制（30 分钟以内）

### 为什么反复强调"联动修改"?

因为这四个组件靠字段名紧密绑定在一起：

```
JSON 写了 rating  →  模板就必须用 {{ entity.rating }}
                 →  CI 就必须检查 rating 存不存在

如果你把 JSON 改成 score 但忘了改模板
  → Jinja2 渲染时报 undefined → 生成失败

如果你改了模板但忘了改 CI
  → CI 不会检查 score 的合法性 → 质量失控
```

**所以改任何一处，必须检查其余三处。这就是为什么规范里列出了每种场景下 4 个文件分别要改什么。**

---

## 九、进阶文档

| 文档 | 路径 | 内容 | 谁会去看 |
|------|------|------|---------|
| 产品设计 | docs/design.md | 信息架构、数据关系模型、视觉规范 | AI 改样式时参考 |
| 技术实现 | docs/workflow.md | 生成流水线、索引算法、前端路由筛选 | AI 改功能时参考 |
| 变更日志 | changelog.md | Schema 版本演进历史 | 关注历史的人 |
