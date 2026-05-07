"""
基于 Schema 的通用 HTML 生成器
自动根据 schema.json 构建索引并渲染模板
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATE_DIR = os.path.join(BASE_DIR, "generator")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.json")


class SchemaGenerator:
    def __init__(self, data_dir: str = None):
        self.schema = self._load_schema()
        self.data = {}
        self.maps = {}  # ID -> 对象映射
        self.indexes = {}  # 各种索引
        self.data_dir = data_dir or DATA_DIR
        self.template_dir = TEMPLATE_DIR
        self.output_dir = OUTPUT_DIR

    def _load_schema(self) -> dict:
        schema_path = SCHEMA_PATH
        if not os.path.exists(schema_path):
            schema_path = os.path.join(BASE_DIR, "schema.json")
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_json(self, filename: str):
        with open(os.path.join(self.data_dir, filename), "r", encoding="utf-8") as f:
            return json.load(f)

    def load_all_data(self):
        """加载所有数据文件（按旧版顺序加载以保持输出一致）"""
        # 旧版 _ENTITY_TYPES 顺序: attractions, shows, restaurants, dishes, tips, warnings, shortcuts, itineraries
        # 加上其他实体: meta, tags, reviews, opinions, preparations
        entity_order = [
            "attractions", "shows", "restaurants", "dishes",
            "tips", "warnings", "shortcuts", "itineraries",
            "meta", "tags", "reviews", "opinions", "preparations"
        ]

        for entity_type in entity_order:
            if entity_type not in self.schema["entities"]:
                continue
            filename = f"{entity_type}.json"
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                self.data[entity_type] = self._load_json(filename)
            else:
                self.data[entity_type] = {}

    def build_maps(self):
        """构建 ID -> 对象 查找表（与旧版 generate_guide.py 逻辑一致）"""
        # 旧版 _ENTITY_TYPES = ["attractions", "shows", "restaurants", "dishes", "tips", "warnings", "shortcuts", "itineraries"]
        entity_types = ["attractions", "shows", "restaurants", "dishes", "tips", "warnings", "shortcuts", "itineraries"]

        for entity_type in entity_types:
            if entity_type not in self.data:
                continue

            collection = self.data[entity_type].get(entity_type, [])
            self.maps[entity_type] = {item["id"]: item for item in collection}

        # reviews 按 target_id 索引
        reviews_by_target = defaultdict(list)
        for r in self.data.get("reviews", {}).get("reviews", []):
            reviews_by_target[r["target_id"]].append(r)
        self.maps["reviews_by_target"] = dict(reviews_by_target)

        # opinions 按 target_id 索引
        opinions_by_target = defaultdict(list)
        for o in self.data.get("opinions", {}).get("opinions", []):
            opinions_by_target[o["target_id"]].append(o)
        self.maps["opinions_by_target"] = dict(opinions_by_target)

        # warnings 按 target_id 索引
        warnings_by_target = defaultdict(list)
        for w in self.data.get("warnings", {}).get("warnings", []):
            for field in ("attraction_ids", "show_ids", "restaurant_ids", "shortcut_ids"):
                for eid in w.get(field, []):
                    warnings_by_target[eid].append(w)
        self.maps["warnings_by_target"] = dict(warnings_by_target)

    def build_indexes(self):
        """根据 Schema 构建所有索引"""
        # 使用与旧版一致的 tag_index 和 zone_index 构建方式
        self._build_tag_and_zone_indexes()

    def _build_tag_and_zone_indexes(self):
        """构建 tag_index 和 zone_index（与旧版 generate_guide.py 逻辑一致）"""
        # 识别园区标签 ID
        zone_tag_ids = {
            t["id"] for t in self.data.get("tags", {}).get("tags", [])
            if t.get("category") == "zone"
        }

        tag_index = defaultdict(lambda: defaultdict(list))
        zone_index = defaultdict(lambda: defaultdict(list))

        # 遍历所有实体集合，构建 tag 和 zone 索引
        entity_collections = {
            "attractions": self.data.get("attractions", {}).get("attractions", []),
            "shows": self.data.get("shows", {}).get("shows", []),
            "restaurants": self.data.get("restaurants", {}).get("restaurants", []),
            "dishes": self.data.get("dishes", {}).get("dishes", []),
            "shortcuts": self.data.get("shortcuts", {}).get("shortcuts", []),
            "tips": self.data.get("tips", {}).get("tips", []),
            "warnings": self.data.get("warnings", {}).get("warnings", []),
            "itineraries": self.data.get("itineraries", {}).get("itineraries", []),
        }

        for entity_type, entities in entity_collections.items():
            for entity in entities:
                eid = entity["id"]
                # tag 索引
                for tag_id in entity.get("tags", []):
                    tag_index[tag_id][entity_type].append(eid)
                # zone 索引：zone_id（单值）和 zone_ids（多值）统一索引
                for zid in self._iter_zone_ids(entity):
                    if zid in zone_tag_ids:
                        zone_index[zid][entity_type].append(eid)

        self.indexes["tag_index"] = self._to_plain(tag_index)
        self.indexes["zone_index"] = self._to_plain(zone_index)

    def _iter_zone_ids(self, entity):
        """从实体中提取所有 zone ID（兼容 zone_id 单值和 zone_ids 多值）"""
        if entity.get("zone_id"):
            yield entity["zone_id"]
        for zid in entity.get("zone_ids", []):
            yield zid

    def _build_backref_index(self, config: dict) -> dict:
        """构建反向引用索引"""
        from_entity = config["from"]
        by_field = config["by"]

        index = defaultdict(list)
        items = self._get_items(from_entity)

        for item in items:
            # 处理多字段反向（如 warnings_by_target）
            if isinstance(by_field, list):
                for field in by_field:
                    target_ids = item.get(field, [])
                    if not isinstance(target_ids, list):
                        target_ids = [target_ids] if target_ids else []
                    for target_id in target_ids:
                        index[target_id].append(self._summarize_item(item, from_entity))
            else:
                # 单字段反向（如 target_id）
                target_id = item.get(by_field)
                if target_id:
                    index[target_id].append(self._summarize_item(item, from_entity))

        return dict(index)

    def _build_auto_index(self, config: dict) -> dict:
        """构建自动索引（如 tag_index, zone_index）"""
        source = config["source"]  # "entities.*.tags"
        group_by = config.get("groupBy", "entityType")

        index = defaultdict(lambda: defaultdict(list))

        # 解析 source 路径
        # entities.*.tags 表示遍历所有实体的 tags 字段
        if source.startswith("entities.*."):
            field_name = source.split(".")[-1]

            for entity_type, config in self.schema["entities"].items():
                if entity_type not in self.data:
                    continue

                items = self._get_items(entity_type)
                for item in items:
                    ref_ids = item.get(field_name, [])
                    if not isinstance(ref_ids, list):
                        ref_ids = [ref_ids] if ref_ids else []

                    for ref_id in ref_ids:
                        if group_by == "entityType":
                            index[ref_id][entity_type].append(item["id"])

        return self._to_plain(index)

    def _build_field_indexes(self):
        """从字段定义中构建额外的索引"""
        for entity_type, config in self.schema["entities"].items():
            fields = config.get("fields", {})

            for field_name, field_schema in fields.items():
                index_name = field_schema.get("index")
                if not index_name:
                    continue

                # 如果索引已存在，跳过
                if index_name in self.indexes:
                    continue

                # 构建字段索引
                index = defaultdict(lambda: defaultdict(list))
                items = self._get_items(entity_type)

                for item in items:
                    ref_ids = item.get(field_name, [])
                    if not isinstance(ref_ids, list):
                        ref_ids = [ref_ids] if ref_ids else []

                    for ref_id in ref_ids:
                        index[ref_id][entity_type].append(item["id"])

                self.indexes[index_name] = self._to_plain(index)

    def _get_items(self, entity_type: str) -> list:
        """获取实体列表"""
        data_obj = self.data.get(entity_type, {})

        if self.schema["entities"][entity_type].get("singleton"):
            return [data_obj] if data_obj else []

        if entity_type in data_obj:
            return data_obj[entity_type]

        return data_obj.get(entity_type, [])

    def _summarize_item(self, item: dict, entity_type: str) -> dict:
        """为反向引用创建摘要对象"""
        summary = {"id": item.get("id"), "type": entity_type}

        # 根据实体类型添加关键字段
        if "name" in item:
            summary["name"] = item["name"]
        if "title" in item:
            summary["title"] = item["title"]
        if "content" in item:
            summary["content"] = item["content"][:50] if item["content"] else ""
        if "severity" in item:
            summary["severity"] = item["severity"]
        if "sentiment" in item:
            summary["sentiment"] = item["sentiment"]
        if "rating" in item:
            summary["rating"] = item["rating"]

        return summary

    def _to_plain(self, d):
        """将 defaultdict 转为普通 dict"""
        if isinstance(d, defaultdict):
            return {k: self._to_plain(v) for k, v in d.items()}
        if isinstance(d, dict):
            return {k: self._to_plain(v) for k, v in d.items()}
        return d

    def _build_backrefs(self) -> dict:
        """构建反向引用索引（与旧版 generate_guide.py 逻辑一致）"""
        from collections import defaultdict

        # 初始化 backrefs，所有实体都有这四个字段
        backrefs = defaultdict(lambda: {
            "tips": [], "warnings": [], "reviews": [], "itineraries": []
        })

        # 1. tips → attractions
        for tip in self.data.get("tips", {}).get("tips", []):
            for attr_id in tip.get("attraction_ids", []):
                backrefs[attr_id]["tips"].append({
                    "id": tip.get("id"),
                    "title": tip.get("title", "")
                })

        # 2. warnings → 各实体 (从 warnings_by_target map 构建)
        # 注意：使用 self.maps 而不是 self.indexes，因为 maps 包含完整的 warning 对象
        warnings_by_target = self.maps.get("warnings_by_target", {})
        for entity_id, warnings in warnings_by_target.items():
            for w in warnings:
                backrefs[entity_id]["warnings"].append({
                    "id": w.get("id"),
                    "content": w.get("content", ""),
                    "severity": w.get("severity", "medium"),
                    "category": w.get("category", ""),
                    "alternative": w.get("alternative", ""),
                })

        # 3. reviews → 各实体 (从 reviews_by_target map 构建)
        reviews_by_target = self.maps.get("reviews_by_target", {})
        for target_id, reviews in reviews_by_target.items():
            for r in reviews:
                backrefs[target_id]["reviews"].append({
                    "id": r.get("id"),
                    "title": r.get("title", ""),
                    "rating": r.get("rating"),
                })

        # 4. itineraries → 各实体
        for itin in self.data.get("itineraries", {}).get("itineraries", []):
            itin_id = itin.get("id")
            itin_name = itin.get("name", "")

            for slot in itin.get("time_slots", []):
                for item in slot.get("items", []):
                    entry = {
                        "id": itin_id,
                        "name": itin_name,
                        "time": item.get("time"),
                        "action": item.get("action", ""),
                    }
                    for field in ("attraction_ids", "show_ids", "restaurant_ids"):
                        for ref_id in item.get(field, []):
                            backrefs[ref_id]["itineraries"].append(entry)

        return self._to_plain(backrefs)

    def _build_alternative_index(self) -> dict:
        """构建替代选择索引（与旧版 generate_guide.py 逻辑一致）"""
        alt_index = {}

        # 1. 从 warnings 的替代关系构建
        for w in self.data.get("warnings", {}).get("warnings", []):
            source_ids = (
                w.get("attraction_ids", [])
                + w.get("restaurant_ids", [])
                + w.get("show_ids", [])
                + w.get("shortcut_ids", [])
            )
            if w.get("alternative"):
                for sid in source_ids:
                    if sid not in alt_index:
                        alt_index[sid] = []
                    alt_index[sid].append({
                        "type": "warning",
                        "entity_id": w.get("id"),
                        "name": "",
                        "reason": w.get("alternative"),
                    })

        # 2. 从 dishes 的 alternatives 构建
        for dish in self.data.get("dishes", {}).get("dishes", []):
            for alt in dish.get("alternatives", []):
                if dish.get("id") not in alt_index:
                    alt_index[dish["id"]] = []
                alt_index[dish["id"]].append({
                    "type": "dish",
                    "entity_id": alt.get("dish_id", ""),
                    "name": "",
                    "reason": alt.get("note", ""),
                    "alt_type": alt.get("type", ""),
                })

        return alt_index

    def render_html(self, template_name: str = "guide_template.html", output_name: str = "guide.html"):
        """渲染 HTML"""
        # 构建与旧版兼容的 _indexes
        # 旧版模板期望: DATA._indexes 包含 tag_index, zone_index, backrefs, alternative_index

        # 构建 tag_index 和 zone_index（如果还没有的话）
        if "tag_index" not in self.indexes:
            self._build_tag_and_zone_indexes()

        # 构建 backrefs（从 itineraries 构建）
        self.indexes["backrefs"] = self._build_backrefs()

        # 构建 alternative_index（从 warnings 构建）
        self.indexes["alternative_index"] = self._build_alternative_index()

        # 将 maps 和 indexes 注入 data
        self.data["_maps"] = self.maps
        self.data["_indexes"] = self.indexes

        env = Environment(loader=FileSystemLoader(self.template_dir), autoescape=True)
        template = env.get_template(template_name)

        data_blob = json.dumps(self.data, ensure_ascii=False, indent=None, separators=(",", ":"))
        indexes_blob = json.dumps(self.indexes, ensure_ascii=False, indent=None, separators=(",", ":"))

        # 北京时间
        beijing_tz = timezone(timedelta(hours=8))
        now_beijing = datetime.now(beijing_tz)

        html = template.render(
            data_blob=data_blob,
            indexes_blob=indexes_blob,
            generated_at=now_beijing.strftime("%Y-%m-%d %H:%M"),
            schema=self.schema,  # 注入 schema 供模板参考
        )

        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        size_kb = os.path.getsize(output_path) / 1024
        print(f"生成完成: {output_path} ({size_kb:.1f} KB)")
        return output_path

    def update_meta(self):
        """自动更新 meta.json 的 last_updated"""
        beijing_tz = timezone(timedelta(hours=8))
        today = datetime.now(beijing_tz).strftime("%Y-%m-%d")

        meta_path = os.path.join(self.data_dir, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            if meta.get("last_updated") != today:
                meta["last_updated"] = today
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, ensure_ascii=False, indent=2)
                print(f"已更新 meta.json last_updated → {today}")

    def run(self, template_name: str = "guide_template.html", output_name: str = "guide.html"):
        """完整生成流程"""
        print("加载数据...")
        self.load_all_data()

        print("更新元数据...")
        self.update_meta()

        print("构建查找表...")
        self.build_maps()

        print("构建索引...")
        self.build_indexes()

        print("渲染 HTML...")
        output_path = self.render_html(template_name, output_name)

        return output_path


def main():
    """命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description="Schema 驱动的 HTML 生成器")
    parser.add_argument("--data-dir", "-d", help="数据目录路径（默认: ./data）")
    parser.add_argument("--template-dir", "-t", help="模板目录路径（默认: ./generator）")
    parser.add_argument("--output-dir", "-o", help="输出目录路径（默认: ./output）")
    parser.add_argument("--template", default="guide_template.html", help="模板文件名")
    parser.add_argument("--output", default="guide.html", help="输出文件名")
    args = parser.parse_args()

    generator = SchemaGenerator(data_dir=args.data_dir)
    if args.template_dir:
        generator.template_dir = os.path.abspath(args.template_dir)
    if args.output_dir:
        generator.output_dir = os.path.abspath(args.output_dir)
    generator.run(template_name=args.template, output_name=args.output)


if __name__ == "__main__":
    main()
