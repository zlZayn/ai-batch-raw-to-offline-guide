# Design — 北京环球影城攻略离线H5

## 1. 产品定位

一个**单HTML文件**的离线手机网页，打开即用，无需网络、无需安装。用户在园区内随时查阅攻略，通过点击导航快速找到所需信息。

**核心场景**：园区内手机信号差或无网络时，仍能完整使用所有功能。

**数据规模**：内嵌全量结构化数据（17项目、15演出、15餐厅、40菜品、14技巧、33避雷、47标签11分类、101评价、24观点），最终产物 `guide.html` 约 350KB，微信均可直接发送。

## 2. 技术选型

| 层 | 选型 | 理由 |
|---|------|------|
| 产物 | 单HTML文件 | 零依赖、100%离线、微信可发，一个文件搞定 |
| 数据注入 | JSON内嵌到`<script>` | 全量数据内嵌，无需外部请求，加载即用 |
| CSS | 手写移动端优先 | 数据量小无需框架，CSS变量管理主题 |
| JS | 纯Vanilla JS | hash路由SPA，无框架依赖，产物体积可控 |
| 模板 | Jinja2 | Python生态标准，自动转义安全 |
| 离线方案 | 纯静态 | 单文件已100%离线，无需Service Worker |

**为什么选单HTML**：园区内无网络是核心痛点，单文件方案彻底消除网络依赖。所有CSS/JS/JSON内嵌，一个文件搞定，微信发送、AirDrop、文件传输均可使用。

**为什么不用框架**：数据量小（350KB），引入React/Vue反而增加体积和复杂度。Vanilla JS + Jinja2模板足以支撑23个路由的SPA，且产物更小、加载更快。

## 3. 信息架构

### 3.1 数据资产表

| 实体 | 数量 | JSON文件 | 列表页 | 详情页 |
|------|------|---------|--------|--------|
| 游乐项目 | 17 | attractions.json | `#attractions`（按园区筛选） | `#attraction/{id}` |
| 演出 | 15 | shows.json | `#shows`（按园区筛选） | `#show/{id}` |
| 餐厅 | 15 | restaurants.json | `#restaurants`（按园区筛选） | `#restaurant/{id}` |
| 菜品 | 40 | dishes.json | `#dishes`（按园区筛选） | `#dish/{id}` |
| 评价 | 101 | reviews.json | 无独立列表页 | 无独立详情页 |
| 观点 | 24 | opinions.json | 无独立列表页 | 无独立详情页 |
| 秘密小道 | 3 | shortcuts.json | `#shortcuts`（卡片内联） | `#shortcut/{id}` |
| 行程方案 | 2 | itineraries.json | `#itineraries` | `#itinerary/{id}` |
| 隐藏技巧 | 14 | tips.json | `#tips` | `#tip/{id}` |
| 避雷 | 33 | warnings.json | `#warnings`（按严重度排序） | `#warning/{id}` |
| 行前准备 | 8模块 | preparations.json | `#preparations`（模块入口） | `#preparation/{section}` |
| 标签 | 47（11分类） | tags.json | `#tags`（按分类展示） | `#tag/{id}`（关联所有实体） |
| 元数据 | 1组 | meta.json | 无 | 无 |

### 3.2 数据关联关系

```
tags.json (全局标签字典，47标签、11分类)
  ├── 11个分类：zone / attraction_type / intensity / timing / facility / audience / utility / meta_tag / taste / dish_type / preparation
  └── 所有实体的 tags[] 统一引用 tag_id（tags 是唯一标签来源，无 type_id 字段）

reviews.json (独立评价实体，101条)
  ├── 从 attractions/shows/restaurants/dishes 中提取
  └── 通过 review_ids 数组被各实体引用

opinions.json (独立观点实体，24条)
  ├── 从各实体中提取
  └── 通过 opinion_ids 数组被各实体引用

attractions ←── itineraries.time_slots[].items[].attraction_ids
            ←── warnings[].attraction_ids
            ←── tips.attraction_ids
            ←── reviews / opinions（通过 review_ids / opinion_ids）
            └── zone_ids[]（数组，统一格式）

shows       ←── itineraries.time_slots[].items[].show_ids
            ←── warnings[].show_ids
            ←── reviews / opinions（通过 review_ids / opinion_ids）
            └── zone_ids[]（数组，支持跨园区）

restaurants ←── itineraries.time_slots[].items[].restaurant_ids
            ←── warnings[].restaurant_ids
            ←── dishes.restaurant_ids（菜品→餐厅）
            ←── reviews / opinions（通过 review_ids / opinion_ids）
            └── zone_ids[]（数组，统一格式）

dishes      ←── restaurants.recommended_dish_ids（ID引用）
            ←── dishes.alternatives[].dish_id（菜品间替代关系）
            ←── reviews / opinions（通过 review_ids / opinion_ids）
            └── zone_ids[]（数组，统一格式）

shortcuts   ←── warnings[].shortcut_ids

warnings.json (扁平结构，33条)
  ├── 通过 warning_ids 数组被各实体引用
  ├── zone_ids[] 独立存放所属园区
  └── 不再嵌套 items，每条 warning 独立
```

### 3.3 统一 Schema 规范（v3）

所有实体遵循统一的字段命名规范：

| 规范 | 说明 |
|------|------|
| `zone_ids: string[]` | 园区归属统一为数组，即使只有一个园区 |
| `tags: string[]` | 标签统一字段名（dishes 不再使用 taste_tags；attractions/shows 不再有 type_id，类型标签统一在 tags 中） |
| `warning_ids: string[]` | 关联避雷（attractions/shows/restaurants/preparations） |
| `review_ids: string[]` | 关联评论 |
| `opinion_ids: string[]` | 关联观点 |
| `{type}_ids: string[]` | 所有跨实体引用统一为数组模式 |

## 4. 索引设计

### 4.1 tag_index（标签→实体）

**结构**：`tag_id → { entity_type: [entity_ids] }`

遍历所有8种实体（attractions/shows/restaurants/dishes/shortcuts/tips/warnings/itineraries）的 `tags[]` 字段，按标签分组。

**用途**：支撑标签云页面的计数展示，以及标签详情页（`#tag/{id}`）按实体类型分区块展示所有关联内容。

### 4.2 zone_index（园区→实体）

**结构**：`zone_tag_id → { entity_type: [entity_ids] }`

按实体的 `zone_ids` 字段分组，覆盖有明确园区归属的实体。

**用途**：列表页的园区筛选功能，以及详情页底部"同园区推荐"区域。

### 4.3 backrefs（反向引用）

**结构**：`entity_id → { tips: [], warnings: [], itineraries: [] }`

从 tips、warnings、itineraries 中提取对实体的引用关系，反向建立索引。

**用途**：详情页底部"关联信息"区域，让用户从任意实体找到引用它的技巧、避雷、行程。

### 4.4 alternative_index（替代关系）

**结构**：`entity_id → [{type, entity_id, name, reason}]`

从 warnings 的 `alternatives[]` 和 dishes 的 `alternatives[]` 中提取替代关系。

**用途**：详情页底部展示替代选择，如避雷中推荐的替代餐厅/菜品，以及菜品详情中的口味相近/平价替代选项。

## 5. 页面结构

### 5.1 布局

```
┌─────────────────────────┐
│  环球攻略   [按标签查找]  │  ← 固定顶栏（毛玻璃）
├─────────────────────────┤
│  面包屑导航（非首页）     │  ← 二级结构，可点击回溯
├─────────────────────────┤
│                         │
│     #app 内容区          │  ← hash路由切换
│     (可滚动区域)         │
│                         │
├─────────────────────────┤
│ 首页 项目 餐厅 演出 更多  │  ← 固定底栏（毛玻璃），5个tab
└─────────────────────────┘
```

底栏5个tab：首页 / 项目 / 餐厅 / 演出 / 更多。当前页图标高亮（玫红色 + 底部指示条）。详情页自动高亮对应tab（如 `restaurant/xxx` 高亮"餐厅"）。

### 5.2 路由表

| #路由 | 页面 | 渲染函数 | 说明 |
|-------|------|---------|------|
| `#home` | 首页 | `renderHome` | 9宫格入口 + Top5柱状图 + 自动轮播 + 心理准备 |
| `#attractions` | 项目列表 | `renderAttractionList` | 按园区筛选，按排名排序 |
| `#attractions/{id}` | 项目详情 | `renderAttractionDetail` | 排队/存包/座位/评价 + 关联信息 |
| `#shows` | 演出列表 | `renderShowList` | 按园区筛选，显示类型标签 |
| `#shows/{id}` | 演出详情 | `renderShowDetail` | 时间/路线/技巧/注意事项 + 关联信息 |
| `#show_schedule` | 演出时间轴 | `renderShowSchedule` | 按时间排序所有场次，按上/下/晚分组 |
| `#restaurants` | 餐厅列表 | `renderRestaurantList` | 按园区筛选 + 省钱技巧 |
| `#restaurants/{id}` | 餐厅详情 | `renderRestaurantDetail` | 推荐菜品/评价/省钱技巧 + 关联信息 |
| `#dishes` | 菜品列表 | `renderDishList` | 按园区筛选，40道菜品 |
| `#dishes/{id}` | 菜品详情 | `renderDishDetail` | 口味标签/评价/对立观点/替代菜品 + 关联信息 |
| `#itineraries` | 行程列表 | `renderItineraryList` | 2版行程方案 |
| `#itineraries/{id}` | 行程详情 | `renderItineraryDetail` | 时间轴布局，项目可点击跳转 |
| `#tips` | 技巧列表 | `renderTipList` | 14条隐藏技巧 |
| `#tips/{id}` | 技巧详情 | `renderTipDetail` | 内容/对立观点/关联项目 |
| `#warnings` | 避雷列表 | `renderWarningList` | 按严重度排序（high→medium→low），含替代方案 |
| `#warnings/{id}` | 避雷详情 | `renderWarningDetail` | 避雷详情 + 关联实体 + 替代方案 |
| `#preparations` | 行前准备主页 | `renderPreparations` | 8个模块入口卡片 |
| `#preparations/{section}` | 行前准备子页 | `renderPreparationDetail` | 交通/穿衣/物品/日期/清单/票价/停车/租赁 |
| `#shortcuts` | 秘密小道列表 | `renderShortcutList` | 3条捷径，卡片内联展示 |
| `#shortcuts/{id}` | 秘密小道详情 | `renderShortcutDetail` | 路线/节省/避坑/条件 + 关联信息 |
| `#tags` | 标签云 | `renderTagCloud` | 按11个分类展示47个标签及计数 |
| `#tags/{id}` | 标签详情 | `renderTagContent` | 该标签关联的所有实体，按类型分区块 |
| `#more` | 更多 | `renderMore` | 行程/标签/技巧/避雷/小道/行前入口 |

### 5.3 面包屑导航

所有非首页页面顶部自动显示面包屑，由 `PAGE_META` 定义路径层级：

```
首页 / 游乐项目 / 哈利波特与禁忌之旅
首页 / 演出 / 演出时间轴
首页 / 餐厅 / 菜品 / 奶昔
首页 / 行前准备 / 交通指南
首页 / 标签 / 高刺激
```

- 二级结构：列表页 → 首页，详情页 → 列表页 → 首页
- 路径中每一级都可点击跳转（蓝色）
- 当前页（最后一项）为黑色加粗，不可点击
- 白底圆角卡片容器，轻阴影

## 6. 视觉设计

### 6.1 设计原则

- **移动端优先**：针对手机屏幕优化，适配iPhone安全区（`env(safe-area-inset-bottom)`）
- **暗色模式无关**：iOS系统灰白底色（`#f2f2f7`），卡片白底，无需暗色模式
- **毛玻璃质感**：顶栏底栏使用 `backdrop-filter: saturate(180%) blur(20px)`，85%透明度
- **点击操作**：全部通过点击完成，无需打字输入
- **视觉层次**：通过字重、颜色、间距、阴影区分信息层级
- **实体类型色彩**：8种实体各有主题色，通过左侧色条和详情页头部色条区分

### 6.2 色彩系统

所有颜色通过CSS变量统一管理，`:root` 中定义：

| 变量 | 值 | 用途 |
|------|-----|------|
| `--bg` | `#f2f2f7` | 页面背景（iOS系统灰） |
| `--card` | `#fff` | 卡片/面板背景 |
| `--text` | `#1c1c1e` | 主文字（iOS黑） |
| `--sub` | `#8e8e93` | 副文字（iOS灰） |
| `--border` | `#e5e5ea` | 边框/分隔符 |
| `--green` | `#34c759` | 成功/正面/低严重度 |
| `--orange` | `#ff9500` | 警告/中严重度 |
| `--red` | `#ff3b30` | 危险/负面/高严重度 |
| `--yellow` | `#f1c40f` | 评分星星 |
| `--glass-bg` | `rgba(255,255,255,.85)` | 毛玻璃背景 |
| `--glass-border` | `rgba(0,0,0,.08)` | 毛玻璃边框 |
| `--divider` | `rgba(0,0,0,.04)` | 轻分隔线 |
| `--shadow-color` | `rgba(0,0,0,.06)` | 阴影颜色 |
| `--shadow` | `0 1px 4px rgba(0,0,0,.06)` | 统一阴影 |
| `--radius` | `14px` | 统一圆角 |

**中性色**（非实体内容：链接、面包屑、时间轴、关联区、轮播等）：

| 变量 | 值 | 用途 |
|------|-----|------|
| `--neutral` | `#3a3a3c` | 中性文字/边框（深灰） |
| `--neutral-light` | `rgba(0,0,0,.04)` | 中性浅背景 |
| `--neutral-border` | `rgba(0,0,0,.15)` | 中性边框 |
| `--opinion-bg` | `linear-gradient(135deg, #f9f9fb, #f5f5f7)` | 对立观点背景 |
| `--relations-bg` | `linear-gradient(135deg, #f9f9fb, #f5f5f7)` | 关联区背景 |

**实体类型主题色**（详情页/列表页自动通过 `--section-color` 继承）：

| 变量 | 值 | 实体 |
|------|-----|------|
| `--c-attraction` | `#007aff` | 项目 - 蓝 |
| `--c-show` | `#af52de` | 演出 - 紫 |
| `--c-restaurant` | `#ff9500` | 餐厅 - 橙 |
| `--c-dish` | `#ff9500` | 菜品 - 橙（与餐厅同色系） |
| `--c-tip` | `#34c759` | 技巧 - 绿 |
| `--c-warning` | `#ff3b30` | 避雷 - 红 |
| `--c-shortcut` | `#8e8e93` | 小道 - 灰（中性） |
| `--c-itinerary` | `#5856d6` | 行程 - 靛蓝 |

**颜色设计原则**：实体内容用彩色区分，非实体内容统一黑白灰。详情页/列表页通过 `--section-color` wrapper 自动继承实体色，内部元素（section-title 竖线、时间轴、关联区等）用 `var(--section-color, var(--neutral))` 自动跟随。

**标签云按分类着色**：

| 标签分类 | 背景色 | 文字色 |
|---------|--------|--------|
| zone（园区） | 橙色10%透明度 | `--orange` |
| intensity（刺激度） | 红色8%透明度 | `--red` |
| audience（受众） | 紫色8%透明度 | `--c-show` |
| utility（实用） | 绿色8%透明度 | `--green` |
| taste（口味） | 橙色8%透明度 | `--orange` |
| meta_tag（元标签） | 中性浅背景 | `--neutral` |

### 6.3 组件样式表

| 组件 | 样式 |
|------|------|
| 顶栏 | 固定顶部56px，毛玻璃（saturate(180%) blur(20px)），85%透明度，极细边框；Logo黑色加粗文字 |
| 底栏 | 固定底部64px，毛玻璃同顶栏，5个tab均分；当前页黑色高亮(font-weight:600) + 底部2.5px指示条；适配iPhone安全区 |
| 卡片 | 白底，14px圆角，统一阴影（`0 1px 4px rgba(0,0,0,.06)`），16px内边距 |
| 列表项 | 白底卡片，左侧3px实体类型色条，按压微缩放（`scale(.985)`），右侧`›`箭头，长文本省略号 |
| 9宫格 | 3列网格，数字32px灰色加粗，padding 22px，按压微缩放（scale(.96)） |
| Top5柱状图 | 白底卡片内，每行：排名号+名称(130px)+渐变进度条（内嵌星级+评分），5种渐变色区分，可点击跳转 |
| 技巧网格 | 2列网格，左侧绿色边条，emoji图标+标题+摘要（2行截断），按压微缩放 |
| 菜品网格 | 2列网格（与技巧网格同布局），左侧橙色边条，emoji评价图标+菜名+餐厅名 |
| 轮播 | 3页（技巧/避雷/菜品），每页3行2列网格，5秒自动切换，触摸滑动支持，切后台随机刷新内容，底部灰色圆点指示器 |
| 筛选栏 | 横向排列的胶囊按钮组，激活态黑色填充+投影，用于项目/餐厅/演出/菜品列表的园区筛选 |
| 标签 | 圆角胶囊（20px），按分类着色（zone橙/intensity红/audience紫/utility绿/taste橙/meta_tag灰），12px字重500 |
| 可点击标签 | 在标签基础上加中性色细边框，按压加深背景 |
| 评分 | 金色星星14px（★☆） |
| 严重度 | 红(`sev-high`)/橙(`sev-medium`)/绿(`sev-low`)三色文字标签 |
| 对立观点 | 左侧3px实体色竖线 + 灰色渐变背景，正方绿色/反方红色立场标签 |
| 时间轴 | 实体色渐变竖线 + 双层圆点，可点击项实体色文字（自动继承 `--section-color`） |
| 演出时间轴 | 按上/下/晚分组，分组标题13px灰色带底部分隔线；场次卡片：左侧20px紫色时间 + 演出名称+园区+时长，可点击跳转详情 |
| 关联区 | 灰色渐变背景，分三层展示：同园区内容→替代选择→反向索引（技巧/避雷/行程），所有项可点击带箭头 |
| 可点击文字 | 深灰色文字+`›`箭头（`.wc-link`），用于避雷列表中的关联跳转 |
| 面包屑 | 白底圆角卡片（10px圆角），深灰色可点击项，黑色加粗当前页，`/`分隔，13px |
| 详情页头部 | 白底卡片，左侧4px实体类型色条，22px标题+14px副标题+标签 |
| 分区标题 | 15px加粗，左侧3px实体色竖线（自动继承 `--section-color`，无 wrapper 时 fallback 灰色），10px左内边距 |
| 空状态 | 居中48px上下内边距，灰色14px文字 |

### 6.4 字体排版

```
字体栈：-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display",
        "Segoe UI", Roboto, "Helvetica Neue", sans-serif
正文字号：15px，行高：1.65
标题h2：22px，字重700，字间距-0.5px
标题h3：16px，字重600，字间距-0.2px
标题h4：15px，字重600，字间距-0.1px
副文字：13px，颜色#8e8e93
标签文字：12px，字重500
面包屑：13px
```

## 7. 约束与决策

### 为什么选单HTML

园区内无网络是核心痛点。单文件方案彻底消除网络依赖——所有CSS、JS、JSON内嵌于一个HTML文件，产物约350KB。可通过微信发送、AirDrop、文件传输等方式分享，接收方打开即用，无需安装任何东西。

### 为什么不用前端框架

数据量小（350KB），引入React/Vue反而增加体积和复杂度。Vanilla JS + Jinja2模板足以支撑23个路由的SPA，且产物更小、加载更快、无构建步骤。Jinja2在构建时完成模板渲染，运行时零开销。

### 数据更新策略

数据以JSON文件形式存放在 `data/v3/` 目录，结构清晰、易于编辑。修改JSON后运行 `python scripts/ci.py` 即可自动校验数据完整性并重新生成 `guide.html`。这种"数据与模板分离"的设计让非技术人员也能更新攻略内容。

### 其他决策

- **不支持拼音搜索**：用户输入中文即可，通过标签点击导航，无需键盘输入
- **不内嵌图片**：当前数据无图片引用，保持产物体积最小
- **对立观点不合并不隐藏**：用引用块分别展示正反方，让用户自行判断
- **iPhone适配**：底栏使用 `env(safe-area-inset-bottom)` 适配刘海屏
