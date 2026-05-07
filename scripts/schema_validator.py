"""Schema-driven data validator. Usage:
python scripts/schema_validator.py
python scripts/schema_validator.py <path/to/data>
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Any, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "data")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.json")


class SchemaValidator:
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        self.schema = self._load_schema()
        self.data = {}
        self.lookup = {}  # id -> (entity_type, entity)
        self.errors = []
        self.warnings = []
        self.stats = {}

    def _load_schema(self) -> Dict:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_json(self, filename: str) -> Any:
        with open(os.path.join(self.data_dir, filename), "r", encoding="utf-8") as f:
            return json.load(f)

    def load_all_data(self):
        """加载所有数据文件"""
        for entity_type in self.schema["entities"].keys():
            filename = f"{entity_type}.json"
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                self.data[entity_type] = self._load_json(filename)
            else:
                self.data[entity_type] = {}

    def build_lookup(self):
        """构建 ID 查找表"""
        self.lookup = {}
        duplicates = []

        for entity_type, config in self.schema["entities"].items():
            if entity_type not in self.data:
                continue

            data_obj = self.data[entity_type]

            # 处理单例实体（如 meta, preparations）
            if config.get("singleton"):
                continue

            # 处理数组型实体
            items_key = entity_type
            if items_key in data_obj:
                items = data_obj[items_key]
            else:
                # 处理 tags 这种嵌套结构
                items = data_obj.get(entity_type, [])

            for item in items:
                if "id" in item:
                    eid = item["id"]
                    if eid in self.lookup:
                        duplicates.append(f"ID 重复: {eid} (在 {self.lookup[eid][0]} 和 {entity_type})")
                    else:
                        self.lookup[eid] = (entity_type, item)

        return duplicates

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """执行所有验证"""
        self.errors = []
        self.warnings = []
        self.stats = {}

        # build_lookup 返回重复 ID 错误
        duplicates = self.build_lookup()
        if duplicates:
            self.errors.extend(duplicates)
        else:
            self.stats["唯一ID数"] = len(self.lookup)

        self._validate_references()
        self._validate_backrefs()
        self._validate_field_types()
        self._validate_required_fields()

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_references(self):
        """验证引用完整性"""
        ref_count = 0
        broken_refs = []

        for entity_type, config in self.schema["entities"].items():
            if entity_type not in self.data:
                continue

            items = self._get_items(entity_type)
            fields = config.get("fields", {})

            for item in items:
                for field_name, field_schema in fields.items():
                    if not field_schema.get("ref"):
                        continue

                    ref_value = item.get(field_name)
                    if not ref_value:
                        continue

                    ref_targets = field_schema["ref"].split(",")

                    # 处理数组引用
                    if isinstance(ref_value, list):
                        for ref_id in ref_value:
                            ref_count += 1
                            if not self._check_ref_exists(ref_id, ref_targets):
                                broken_refs.append(
                                    f"{entity_type}/{item.get('id', 'unknown')}.{field_name} -> {ref_id} 不存在"
                                )
                    # 处理单值引用
                    elif isinstance(ref_value, str):
                        ref_count += 1
                        if not self._check_ref_exists(ref_value, ref_targets):
                            broken_refs.append(
                                f"{entity_type}/{item.get('id', 'unknown')}.{field_name} -> {ref_value} 不存在"
                            )

        if broken_refs:
            self.errors.extend(broken_refs)
        else:
            self.stats["有效引用数"] = ref_count

    def _check_ref_exists(self, ref_id: str, target_types: List[str]) -> bool:
        """检查引用是否存在"""
        if ref_id in self.lookup:
            actual_type = self.lookup[ref_id][0]
            # 处理 tags.tags 这种嵌套路径
            for target in target_types:
                if target == actual_type or target.startswith(f"{actual_type}."):
                    return True
        return False

    def _validate_backrefs(self):
        """验证双向链接一致性"""
        backref_checks = []

        for entity_type, config in self.schema["entities"].items():
            items = self._get_items(entity_type)
            fields = config.get("fields", {})

            for item in items:
                for field_name, field_schema in fields.items():
                    backref_field = field_schema.get("backref")
                    if not backref_field:
                        continue

                    ref_ids = item.get(field_name, [])
                    if not isinstance(ref_ids, list):
                        ref_ids = [ref_ids] if ref_ids else []

                    for ref_id in ref_ids:
                        if ref_id not in self.lookup:
                            continue

                        ref_type, ref_item = self.lookup[ref_id]
                        backref_checks.append({
                            "source_type": entity_type,
                            "source_id": item.get("id"),
                            "source_field": field_name,
                            "target_type": ref_type,
                            "target_id": ref_id,
                            "backref_field": backref_field,
                            "target_item": ref_item
                        })

        inconsistent = []
        for check in backref_checks:
            target_item = check["target_item"]
            backref_field = check["backref_field"]
            source_id = check["source_id"]

            # 处理 target_id 单值反向
            if backref_field == "target_id":
                actual = target_item.get(backref_field)
                if actual != source_id:
                    inconsistent.append(
                        f"{check['source_type']}/{source_id}.{check['source_field']} -> "
                        f"{check['target_id']} 的 target_id 指向 {actual}，期望 {source_id}"
                    )
            # 处理数组反向
            else:
                backref_values = target_item.get(backref_field, [])
                if not isinstance(backref_values, list):
                    backref_values = [backref_values] if backref_values else []

                if source_id not in backref_values:
                    inconsistent.append(
                        f"{check['source_type']}/{source_id}.{check['source_field']} -> "
                        f"{check['target_id']}，但 {check['target_id']}.{backref_field} 不含 {source_id}"
                    )

        if inconsistent:
            self.errors.extend(inconsistent)
        else:
            self.stats["双向链接数"] = len(backref_checks)

    def _validate_field_types(self):
        """验证字段类型"""
        type_errors = []

        for entity_type, config in self.schema["entities"].items():
            items = self._get_items(entity_type)
            fields = config.get("fields", {})

            for item in items:
                for field_name, field_schema in fields.items():
                    value = item.get(field_name)
                    if value is None:
                        continue

                    expected_type = field_schema.get("type")
                    if not expected_type:
                        continue

                    # 类型检查
                    if expected_type == "string" and not isinstance(value, str):
                        type_errors.append(
                            f"{entity_type}/{item.get('id', 'unknown')}.{field_name} 应为字符串，实际是 {type(value).__name__}"
                        )
                    elif expected_type == "number" and not isinstance(value, (int, float)):
                        type_errors.append(
                            f"{entity_type}/{item.get('id', 'unknown')}.{field_name} 应为数字，实际是 {type(value).__name__}"
                        )
                    elif expected_type == "boolean" and not isinstance(value, bool):
                        type_errors.append(
                            f"{entity_type}/{item.get('id', 'unknown')}.{field_name} 应为布尔值，实际是 {type(value).__name__}"
                        )
                    elif expected_type == "array" and not isinstance(value, list):
                        type_errors.append(
                            f"{entity_type}/{item.get('id', 'unknown')}.{field_name} 应为数组，实际是 {type(value).__name__}"
                        )

                    # 枚举检查
                    enum_values = field_schema.get("enum")
                    if enum_values and value in enum_values:
                        if value not in enum_values:
                            type_errors.append(
                                f"{entity_type}/{item.get('id', 'unknown')}.{field_name} 值 {value} 不在允许范围内 {enum_values}"
                            )

        if type_errors:
            self.errors.extend(type_errors)

    def _validate_required_fields(self):
        """验证必填字段"""
        missing = []

        for entity_type, config in self.schema["entities"].items():
            items = self._get_items(entity_type)
            fields = config.get("fields", {})

            for item in items:
                for field_name, field_schema in fields.items():
                    if field_schema.get("required") and field_name not in item:
                        missing.append(
                            f"{entity_type}/{item.get('id', 'unknown')} 缺少必填字段 {field_name}"
                        )

        if missing:
            self.errors.extend(missing)

    def _get_items(self, entity_type: str) -> List[Dict]:
        """获取实体列表"""
        data_obj = self.data.get(entity_type, {})

        # 处理单例
        if self.schema["entities"][entity_type].get("singleton"):
            return [data_obj] if data_obj else []

        # 处理数组型
        if entity_type in data_obj:
            return data_obj[entity_type]

        # 处理 tags 这种嵌套结构
        return data_obj.get(entity_type, [])

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats


def main():
    """命令行入口。Usage:
    python scripts/schema_validator.py
    python scripts/schema_validator.py <path/to/data>
    """
    import sys
    data_dir = DEFAULT_DATA_DIR
    if len(sys.argv) > 1:
        data_dir = os.path.join(BASE_DIR, sys.argv[1])
    if not os.path.isdir(data_dir):
        print(f"[ERR] {data_dir} not found")
        sys.exit(1)

    validator = SchemaValidator(data_dir=data_dir)
    validator.load_all_data()
    validator.build_lookup()

    print("\n--- Schema 数据验证 ---\n")

    ok, errors, warnings = validator.validate_all()
    stats = validator.get_stats()

    for key, value in stats.items():
        print(f"  [STAT] {key}: {value}")

    if errors:
        print(f"\n  发现 {len(errors)} 个错误:")
        for e in errors[:20]:  # 最多显示 20 个
            print(f"    [ERR] {e}")
        if len(errors) > 20:
            print(f"    ... 还有 {len(errors) - 20} 个错误")

    if warnings:
        print(f"\n  发现 {len(warnings)} 个警告:")
        for w in warnings[:10]:
            print(f"    [WARN] {w}")

    if ok:
        print("\n  [PASS] 所有验证通过")
        return 0
    else:
        print(f"\n  [FAIL] 验证失败，共 {len(errors)} 个错误")
        return 1


if __name__ == "__main__":
    main()
