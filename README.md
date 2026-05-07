# AI 驱动的离线攻略生成器

> **一句话介绍：** 把碎片化的非结构化素材（笔记、截图、口述）丢给 AI，自动炼制成一个可交互的离线 HTML 攻略页面——无需联网、无需服务器、打开即用。

**在线预览：** [https://zlzayn.github.io/ai-batch-raw-to-offline-guide/](https://zlzayn.github.io/ai-batch-raw-to-offline-guide/)

---

## 创作故事

之前去 **香港迪士尼** 和 **珠海长隆海洋王国** 时被折磨得不轻——小红书上的攻略东拼西凑，截图存了一堆，现场信号差到刷不出页面，排着队只能干等。那时就在想：**为什么没有一个离线就能用的全景攻略？**

所以去 **北京环球影城**之前，我决定先把这事做了——把所有项目排名、餐厅评价、隐藏技巧、避雷提醒全部整理成结构化数据，写了一个手机端离线网页。带着这个工具去的环球影城，亲测好用。

做完后我发现，这套数据结构和页面模板其实不限于环球影城——换一套数据，上海迪士尼、成都美食地图、甚至个人影单推荐都能用。于是我把它改造成了一个 **AI 驱动的生成流水线**：你只要提供素材，告诉 AI 想做什么，一个可交互的离线网页就自动生成了。Schema 驱动的验证系统会全程校验数据完整性，不会漏掉任何引用关系。

这就是这个项目的完整故事：从一个自己用的小工具，变成一套任何人（哪怕不懂代码）都能用的攻略生成器。**一个去之前就做好了的工具。**

---

## 核心亮点

1. **单文件离线** — 一个 HTML 带走全部攻略，无需网络、无需安装、无需服务器
2. **全域双向链接** — 看任何详情页，关联的项目/演出/餐厅/技巧/避雷一键跳转
3. **正反方观点并排** — 不是平均分，而是同时展示优点和缺点的真实评价
4. **动态轮播刷新** — 每次切回页面，技巧/避雷/菜品都会随机刷新
5. **标签跨类型聚合** — 点一个标签，能同时搜出项目+演出+餐厅+菜品+技巧+避雷

---

## 使用场景

1. 园区内无信号时随时查阅
2. 出发前规划最佳游玩路线
3. 排队时看隐藏技巧和小道
4. 选餐厅不想踩雷先翻评价
5. 纠结玩哪个看排名和正反方观点

---

## 快速开始

### 方式一：直接打开（已有生成产物）

如果你已经拿到了 `output/guide.html`（或根目录的 `index.html`）：

- **手机**：用微信/文件管理器打开，添加到桌面像 App 一样使用
- **电脑**：双击直接用浏览器打开
- **分享**：AirDrop、微信发送、网盘分享均可，对方打开就能用

### 方式二：从源码生成

> 注意：`output/` 目录被 `.gitignore` 排除，**clone 下来后默认没有生成产物**，需要手动生成。

```bash
# 1. 安装依赖
pip install jinja2

# 2. 验证数据完整性
python scripts/schema_validator.py

# 3. 生成攻略页面
python generator/schema_generator.py

# 生成成功后，打开 output/guide.html 即可预览
```

### 方式三：GitHub Pages 在线访问

本项目已配置 GitHub Actions 自动部署，访问：

[https://zlzayn.github.io/ai-batch-raw-to-offline-guide/](https://zlzayn.github.io/ai-batch-raw-to-offline-guide/)

> 根目录的 `index.html` 是 `output/guide.html` 的副本，专门用于 GitHub Pages 托管。

---

## 项目结构

```
ai-batch-raw-to-offline-guide/
│
├── schema.json                       ← Schema 定义（实体、字段、关系）
│
├── data/                             ← 结构化数据层（13 个 JSON）
│   ├── meta.json                     ← 项目元信息、源文件索引
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
│   ├── tags.json                     ← 标签（11 个分类）
│   └── preparations.json             ← 行前准备
│
├── generator/                        ← HTML 生成器
│   ├── schema_generator.py           ← Schema 驱动生成脚本
│   └── guide_template.html           ← 页面模板（可自定义）
│
├── scripts/                          ← 工具脚本
│   ├── schema_validator.py           ← Schema 驱动数据验证
│   ├── analyze_data.py               ← 数据结构分析（图表 + JSON 报告）
│   ├── export_xlsx.py                ← 导出 Excel
│   └── stats.py                      ← 数据统计
│
├── output/                           ← 生成产物（被 .gitignore 排除，需手动生成）
│   ├── guide.html                    ← 攻略主页（单文件离线版）
│   ├── v3_data.xlsx                  ← Excel 导出
│   └── data_analysis/                ← 数据分析图表
│
├── projects/                         ← 其他主题项目（示例/测试）
│   └── 上海迪士尼攻略/               ← 上海迪士尼数据（换主题验证用例）
│       ├── data/                     ← 上海迪士尼结构化数据
│       ├── _raw_research.md          ← 原始研究素材
│       └── README.md                 ← 使用说明（复用根目录脚本）
│
├── docs/                             ← 项目文档
│   ├── usage.md                      ← AI 使用教程（换主题全流程指南）
│   ├── design.md                     ← 产品设计：信息架构、视觉规范
│   └── workflow.md                   ← 技术实现：生成流水线、索引算法
│
├── src/                              ← 原始素材（Markdown 笔记）
├── index.html                        ← GitHub Pages 入口（output/guide.html 的副本）
├── .github/workflows/static.yml      ← GitHub Actions 自动部署配置
├── VERIFICATION_REPORT.md            ← Schema 系统验证报告
├── changelog.md                      ← 变更日志
└── README.md                         ← 本文件
```

---

## 换主题教程

想把这个项目改成**上海迪士尼攻略**、**成都美食地图**、**个人影单推荐**？

不需要写代码，全程 AI 协作。详细教程见：

**[docs/usage.md](docs/usage.md)** — AI 驱动的「素材 → 交互式网页」生成流水线使用指南

教程包含：
- 三步上手流程
- AI 工作规范（可直接复制发给 AI）
- 三种使用场景（换主题 / 减实体 / 全新定制）
- Schema 定义与修改规则
- 数据验证与修复循环

---

## 常用命令

```bash
# 验证数据完整性（基于 Schema）
python scripts/schema_validator.py

# 生成 HTML（Schema 驱动）
python generator/schema_generator.py

# 导出 Excel
python scripts/export_xlsx.py

# 数据结构分析（生成图表到 output/data_analysis/）
python scripts/analyze_data.py

# 数据统计
python scripts/stats.py
```

**依赖：** Python 3.6+、`pip install jinja2`

---

## 架构说明

本项目采用 **Schema 驱动架构**：

1. **Schema 定义** (`schema.json`) - 声明式定义实体类型、字段、引用关系
2. **数据验证** (`schema_validator.py`) - 基于 Schema 自动验证数据完整性
3. **索引生成** (`schema_generator.py`) - 基于 Schema 自动构建双向链接索引
4. **模板渲染** (`guide_template.html`) - 可自定义的展示层

**优势：**
- 修改数据结构只需更新 Schema，验证和生成自动适应
- 双向链接由系统自动维护，无需人工干预
- 模板与数据解耦，可自由定制展示方式

---

## 文档索引

| 文档 | 路径 | 内容 | 适合谁看 |
|------|------|------|---------|
| **AI 使用教程** | `docs/usage.md` | 换主题全流程、AI 工作规范、验证修复指南 | 想用 AI 生成新主题的人 |
| **产品设计** | `docs/design.md` | 信息架构、数据关联关系、视觉设计规范 | AI 改样式时参考 |
| **技术实现** | `docs/workflow.md` | 生成流水线、索引算法、前端路由/筛选/轮播 | AI 改功能时参考 |
| **验证报告** | `VERIFICATION_REPORT.md` | Schema 系统验证方法、测试结果 | 关注可靠性的人 |
| **变更日志** | `changelog.md` | Schema 版本演进、数据结构变更历史 | 关注历史的人 |

---

## 技术栈

- **Schema 层**：JSON Schema（声明式数据结构定义）
- **数据层**：JSON 文件（按实体类型组织）
- **验证层**：Python Schema 验证器（引用完整性、双向一致性）
- **生成层**：Python + Jinja2（Schema 驱动模板渲染）
- **展示层**：原生 HTML/CSS/JS（单文件离线、零依赖）
- **部署层**：GitHub Actions → GitHub Pages

---

> 全栈独立开发：一个人负责从项目架构、数据设计、前端交互到 AI 生成流水线的全部设计与实现。
