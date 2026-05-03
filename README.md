# 北京环球影城攻略 — 离线交互版

一个手机端离线网页应用，打开即可查阅全部攻略，无需网络。专为园区内手机信号差或无网络的场景设计。

## 快速使用

打开 `output/guide.html` 即可使用，无需安装、无需联网、无需服务器。微信发送、AirDrop、文件传输均可分享。

## 功能详情

### 首页

- **9宫格快速导航**：项目、演出、餐厅、行程、技巧、避雷、小道、标签、行前准备
- **Top5 排名柱状图**：评分最高的 5 个项目，渐变色条 + 星级，可点击跳转详情
- **自动轮播**：3 页内容（技巧 / 避雷 / 菜品），每 5 秒切换，支持触摸滑动

### 游乐项目（17个）

- 列表页按排名排序，支持按园区筛选（7 个园区 + 全部）
- 详情页：身高限制、时长、室内/室外、湿身提示、单人通道、官方拍照、排队策略、存包指南、座位建议、评价、观点、避雷、关联信息

### 演出推荐（15场）

- 列表页支持按园区筛选
- 详情页：语言、季节限定、时间表、亮点、巡游路线、观看技巧

### 餐厅与菜品（15家餐厅 + 40道菜品）

- 餐厅列表显示人均价格，详情页：人均、营业时间、室内/室外、推荐菜品、评价
- 菜品列表显示价格，详情页：价格、口味标签、替代菜品、评价

### 标签索引（47个标签，11个分类）

- 按分类浏览，点击标签查看所有关联内容

### 行程方案（2套一日游）

- 时间轴布局，项目/餐厅/演出名称可点击跳转

### 隐藏技巧（14条） / 避雷提醒（33条） / 秘密小道（3条）

### 行前准备

- 交通指南、票价与优速通、停车与寄存、租赁服务、穿着建议、必带物品、禁带清单

## 文件结构

```
北京环球影城攻略/
├── data/v3/                        ← 结构化数据（13 个 JSON）
│   ├── attractions.json             ← 17 个游乐项目
│   ├── shows.json                   ← 15 场演出
│   ├── restaurants.json             ← 15 家餐厅
│   ├── dishes.json                  ← 40 道菜品
│   ├── tips.json                    ← 14 条技巧
│   ├── warnings.json                ← 33 条避雷
│   ├── itineraries.json             ← 2 套行程
│   ├── shortcuts.json               ← 3 条小道
│   ├── reviews.json                 ← 101 条评价
│   ├── opinions.json                ← 24 条观点
│   ├── tags.json                    ← 47 个标签（11 分类）
│   ├── preparations.json            ← 行前准备
│   └── meta.json                    ← 源文件索引
├── generator/                       ← HTML 生成器
│   ├── generate_guide.py            ← 生成脚本（Jinja2）
│   └── guide_template.html          ← 页面模板
├── scripts/                         ← 工具脚本
│   ├── ci.py                        ← CI 管线（校验+生成+验证）
│   ├── analyze_data.py              ← 数据结构分析（生成图表+JSON）
│   └── export_xlsx.py               ← 导出 Excel
├── output/                          ← 生成产物
│   ├── guide.html                   ← 攻略主页（~350KB）
│   ├── v3_data.xlsx                 ← Excel 导出
│   └── data_analysis/               ← 数据分析图表
├── docs/                            ← 项目文档
│   ├── design.md                    ← 产品设计
│   └── workflow.md                  ← 技术实现
├── src/                             ← 原始素材（16 份 .md）
├── changelog.md                     ← 变更日志
└── README.md                        ← 本文件
```

## 常用命令

```bash
# 完整 CI（数据校验 → 生成 HTML → 生成后验证）
python scripts/ci.py

# 仅重新生成 HTML
python generator/generate_guide.py

# 导出 Excel
python scripts/export_xlsx.py

# 数据结构分析（生成图表到 output/data_analysis/）
python scripts/analyze_data.py
```

依赖：Python 3.6+、Jinja2（`pip install jinja2`）。

## 文档索引

| 文档 | 路径 | 内容 |
|------|------|------|
| **产品设计** | `docs/design.md` | 信息架构、数据关联关系、视觉设计规范、交互决策 |
| **技术实现** | `docs/workflow.md` | 生成流程、索引算法、前端路由/筛选/轮播系统 |
| **变更日志** | `changelog.md` | 版本时间线 + 数据结构演进 |
