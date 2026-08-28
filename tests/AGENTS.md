# tests/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

tests/ 特有约束：
- schema 冒烟是数据规范闸门：改 schema.json 或 data/ 后必须 uv run pytest
- 快照计数（311/779/234）漂移即失败，先报告维护者，不擅自改断言
- 新增测试必须在本目录 [README.md](README.md) 登记
- 不写"有什么文件/怎么改"，那是 [README.md](README.md) 的职责