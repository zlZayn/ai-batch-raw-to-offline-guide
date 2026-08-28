# 决策：内容完整性与测试闸门（2026-08-28）

已实施：已实施

## 问题
- 索引失真：f7abef1 前 src/00_总索引.md 引用不存在的 10_小红书补充 目录，作品集.md 份数（16）与 src/ 实际（15 内容 + 1 索引）不符
- 验证空白：dd36944 前项目无自动化测试，验证口径依赖手动跑 validator

## 决策
- 索引与数字以实际文件系统、schema.json 为准，发现失真即修
- tests/ 是数据规范闸门：test_schema_validator.py 断言 311/779/234，改 schema.json 必须 uv run pytest
- src/、projects/、data/、output/、images/ 是内容/素材/产物目录，不建双件

## 替代方案（强制）
- 索引保留原样并记入待办：失真继续误导读者，待办滞后等于不修
- 不补测试保持 0 collected：验证口径空白，schema.json 回归无法被发现
- src/、projects/ 也建双件：素材目录无规则可约束，规则层成为空壳噪音

## 影响
- 收益：索引可信、验证可自动化、文档网络两跳可达（tests/ → 根 AGENTS.md → ARCHITECTURE）
- 代价：数字断言随数据变化需同步更新；漂移即失败属预期信号
- 关联：[根 AGENTS.md](../../AGENTS.md) · [tests/README.md](../../tests/README.md)