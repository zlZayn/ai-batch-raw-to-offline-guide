# scripts/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

scripts/ 特有约束：
- 每个脚本可从项目根目录独立运行：uv run python scripts/<name>.py
- 新增脚本必须在本目录 [README.md](README.md) 登记，否则视为未维护
- 分析/导出脚本不得写入 data/ 数据文件
- 不写“有什么文件/怎么改”，那是 [README.md](README.md) 的职责