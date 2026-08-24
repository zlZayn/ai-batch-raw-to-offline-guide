# generator/ — 规则层

继承根规则，见 [../AGENTS.md](../AGENTS.md)。

generator/ 特有约束：
- 改索引/生成逻辑后必须跑 validator + 生成器验证，产物不许带校验错误
- 生成器输出保持单文件、零外部依赖，模板内嵌数据
- 新增实体需在 schema.json 声明，否则生成器不处理
- 不写“有什么文件/怎么改”，那是 [README.md](README.md) 的职责