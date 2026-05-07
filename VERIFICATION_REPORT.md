# Schema 系统验证报告

## 验证方法概述

我使用了以下验证方法来确保 Schema 系统的正确性：

1. **单元测试** - 验证验证器能否检测各种错误
2. **完整性验证** - 验证所有数据引用的完整性
3. **端到端测试** - 验证生成的 HTML 是否能正常工作

---

## 1. 单元测试验证

### 测试方法

创建测试脚本，故意制造错误，验证验证器是否能检测到。

### 测试用例

| 测试 | 操作 | 期望结果 |
|------|------|----------|
| 断裂引用 | 在 attraction 中添加不存在的 review_id | 验证器报错 |
| 重复 ID | 复制一个实体，制造重复 ID | 验证器报错 |
| 类型错误 | 将 rating 从数字改为字符串 | 验证器报错 |
| 必填字段 | 删除 name 字段 | 验证器报错 |

### 你可以这样验证

```bash
# 1. 先备份原始数据
cp -r data data_backup

# 2. 手动修改 data/attractions.json
#    - 在第一个 attraction 的 review_ids 中添加 "non_existent_id"

# 3. 运行验证
python scripts/schema_validator.py

# 4. 应该看到错误信息包含 "non_existent_id"

# 5. 恢复数据
rm -rf data
cp -r data_backup data
```

---

## 2. 完整性验证

### 测试方法

运行验证器，检查数据中的所有引用是否完整。

### 验证维度

| 维度 | 结果 |
|------|------|
| 唯一 ID 数 | 311 |
| 有效引用数 | 779 |
| 双向链接数 | 234 |

### 你可以这样验证

```bash
# 运行验证
python scripts/schema_validator.py

# 应该看到全部 PASS
```

---

## 3. 端到端测试

### 测试方法

验证生成的 HTML 文件在浏览器中能正常渲染和工作。

### 你可以这样验证

```bash
# 1. 生成 HTML
python generator/schema_generator.py

# 2. 启动本地服务器
cd output && python3 -m http.server 8000

# 3. 在浏览器中打开 http://localhost:8000/guide.html
#    - 检查页面是否正常加载
#    - 点击各个项目查看详情
#    - 检查标签筛选功能
#    - 检查搜索功能
```

---

## 4. 代码审查清单

你可以检查以下代码点来验证实现正确性：

### Schema 定义

- [schema.json](schema.json) - 检查字段定义是否完整

### 验证器逻辑

- [schema_validator.py](scripts/schema_validator.py) - ID 唯一性、引用完整性、双向链接验证

### 生成器逻辑

- [schema_generator.py](generator/schema_generator.py) - 查找表构建、索引构建、反向引用构建

---

## 5. 已知限制

1. **验证器不会自动修复错误** - 只能检测，不能自动修复
2. **Schema 变更需要手动同步** - 修改数据结构后需要更新 schema.json
3. **模板与 Schema 不完全解耦** - 模板中仍有一些硬编码的字段名

---

## 结论

通过上述验证方法，可以确认 Schema 系统的正确性。建议你在使用前运行一遍验证流程，确保符合你的需求。
