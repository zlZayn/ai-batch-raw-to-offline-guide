# 上海迪士尼攻略

本项目使用根目录的 Schema 驱动架构生成离线攻略页面。

## 项目结构

```
上海迪士尼攻略/
├── data/                    ← 结构化数据（13 个 JSON 文件）
│   ├── meta.json
│   ├── attractions.json
│   ├── shows.json
│   ├── restaurants.json
│   ├── dishes.json
│   ├── tips.json
│   ├── warnings.json
│   ├── shortcuts.json
│   ├── itineraries.json
│   ├── reviews.json
│   ├── opinions.json
│   ├── tags.json
│   └── preparations.json
│
├── _raw_research.md         ← 原始研究素材
└── README.md                ← 本文件
```

## 使用方法

本项目复用根目录的 Schema 驱动脚本：

```bash
# 1. 进入项目根目录
cd /workspace

# 2. 验证数据完整性
python scripts/schema_validator.py

# 3. 生成 HTML
python generator/schema_generator.py

# 生成结果在 output/guide.html
```

## 数据说明

数据文件遵循根目录 `schema.json` 定义的 Schema 规范。

如需自定义模板，可在本项目创建 `generator/guide_template.html`，
生成器会优先使用项目内的模板，否则使用根目录的默认模板。
