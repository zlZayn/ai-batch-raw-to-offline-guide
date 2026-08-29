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
# 1. 定位到项目根目录 AI-batch-raw-to-offline-guide（命令见根 README.md「快速开始」）
#    本目录不单独装环境，全部命令在项目根目录执行

# 2. 验证数据完整性
uv run python scripts/schema_validator.py

# 3. 生成 HTML
uv run python generator/schema_generator.py

# 生成结果在项目根 output/guide.html
```

> 提示：更精确的用法是给生成器指定数据目录，见根 docs/usage.md 与 generator/README.md（--data-dir 参数）。

## 数据说明

数据文件遵循根目录 `schema.json` 定义的 Schema 规范。

如需自定义模板，把模板文件放在任意目录（如 `my_templates/`）后，用生成器的 `--template-dir` 指向该目录（生成器只认参数指定的单个模板目录，无自动回退）：
