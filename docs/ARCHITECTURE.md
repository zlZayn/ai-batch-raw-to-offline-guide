# ai-batch-raw-to-offline-guide 架构说明

## 一句话定位
- 把碎片化非结构化素材炼成单文件离线 HTML 攻略的 Schema 驱动流水线

## 设计哲学
- Schema 是唯一契约：数据定义（schema.json）同时驱动验证与生成，改结构只改一处
- 单文件离线：产物是一个零依赖 HTML，打开即用
- 关联靠系统算：双向链接与索引由生成器从 ID 引用自动构建，不手写

## 关键决策
- Schema 驱动架构（v3）：schema.json 声明 13 种实体 + 字段 + 引用 + 反向引用规则；validator 与 generator 都只读它
- 一切皆 ID 引用：实体间只存 ID（如 review_ids），杜绝文本内嵌，单点修改
- ID 自描述前缀：attr_ / rest_ / dish_ / tip_ / warn_ / tag_ 等，前缀表类型、后缀表内容
- 子项目复用：projects/ 下新主题复用根目录脚本，靠 --data-dir 等参数切换
- Python 侧 uv 管理：pyproject.toml + uv.lock + .python-version（3.12.10）
- Node 侧仅截图工具：package.json 依赖 puppeteer，仅供开发，不参与产物

## 数据流
- src/（非结构化素材）→ 按 Schema 结构化 → data/（13 个 JSON）→ schema_validator.py 校验 → schema_generator.py 构建索引并渲染 → output/guide.html（单文件）

## 契约
- schema.json 是数据结构唯一来源，validator 与 generator 都读取
- data/ 下 JSON 文件名与 schema 的 entities 键一一对应；实体集合以自身名为键
- 生成器输出 output/guide.html（被 .gitignore 排除，需手动生成）
- index.html 是 output/guide.html 的副本，供 GitHub Pages 托管
- meta.json 的 last_updated 用北京时间（UTC+8）
- GitHub Actions：static.yml 跑 validator → generator → 部署 Pages

## 防错清单
- 改 schema.json 字段/引用 → 同步修改 data/ 数据，跑 validator
- 改生成器索引逻辑 → 跑 validator + 重新生成，并核对输出
- 改模板 → 重新生成，检查渲染结果
- 文档与代码不一致 → 先跑 check-links.py，再按 README（怎么用）/本文档（为什么）分层归位

## 文档约定
- README 讲“是什么、怎么用”；AGENTS.md 讲“在这里怎么工作”；本文档讲“为什么”
- 分层与引用约定：见根 [AGENTS.md](../AGENTS.md) 与子目录双件

## 参考
- 技术实现细节 → [workflow.md](workflow.md)
- 产品设计与视觉规范 → [design.md](design.md)
- 用户教程 → [usage.md](usage.md)
- 变更历史 → [changelog.md](../changelog.md)（数据演进记录）