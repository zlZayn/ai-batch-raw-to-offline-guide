# 决策：Schema 版本演进入册（v1 → v2 → v3）（2026-08-28）

已实施：已实施

## 问题
- 项目经历 v1 → v2 → v3 三次结构迭代，决策从未入册
- changelog.md 记录事实，但不记录「为什么这样设计、否掉过什么」

## 决策
- 版本体系以 changelog.md 为编年史（v1.x → 2.0.0 → 3.0.0 → 3.1.0 → 3.2.0/3.3.0 → 3.4.0，2026-04-06 起）
- v1：单文件夹平铺（v1/data + v1/docs），无 Schema
- v2：多目录（data/docs/generator/output 分版本目录），开始半结构化
- v3（当前）：Schema 驱动 + 数据扁平化，13 实体、ID 引用、双向链接由系统自动构建
- 当前文档以 v3 为唯一事实源；v1/v2 仅存在于 changelog 历史
- 版本号现状：meta/tags.json 内 version 仍写 3.2.0，schema.json 的 $schema 写 guide-data-schema-v1——三处不同步，属已知遗留，不强行统一（避免破坏数据校验）

## 替代方案（强制）
- 强行统一三处版本号：数据文件 version 字段被 validator/模板引用，改值有回归风险，收益仅是表面一致
- 不写本记录：迭代决策继续丢失，「为什么 v3 是 ID 引用」无人能答

## 影响
- 收益：v1→v2→v3 的设计动机有据可查；新维护者不必翻 changelog 猜
- 代价：本记录不改变任何文件，仅沉淀事实
- 关联：[changelog.md](../../changelog.md)