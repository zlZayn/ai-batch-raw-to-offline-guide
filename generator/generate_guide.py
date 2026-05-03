
"""北京环球影城攻略 - 双向索引离线H5生成器 (v3 版本)

直接使用 v3 范式化 JSON。
模板通过 DATA._maps 和 INDEXES 访问查找表与索引。
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "v3")
TEMPLATE_DIR = os.path.join(BASE_DIR, "generator")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "guide.html")

# 需要构建 ID→对象 Map 的实体类型
_ENTITY_TYPES = ["attractions", "shows", "restaurants", "dishes", "tips", "warnings", "shortcuts", "itineraries"]


def _load_json(filename):
    with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_data():
    """加载全部 14 个 v3 JSON 文件。"""
    return {
        "meta": _load_json("meta.json"),
        "tags": _load_json("tags.json"),
        "attractions": _load_json("attractions.json"),
        "shows": _load_json("shows.json"),
        "restaurants": _load_json("restaurants.json"),
        "shortcuts": _load_json("shortcuts.json"),
        "itineraries": _load_json("itineraries.json"),
        "tips": _load_json("tips.json"),
        "warnings": _load_json("warnings.json"),
        "preparations": _load_json("preparations.json"),
        "dishes": _load_json("dishes.json"),
        "reviews": _load_json("reviews.json"),
        "opinions": _load_json("opinions.json"),
    }


def build_lookup_maps(data):
    """构建 ID→对象 的快速查找表。

    maps 结构:
      - attractions/shows/restaurants/dishes/tips/shortcuts: {id → object}
      - reviews_by_target: {target_id → [review]}
      - opinions_by_target: {target_id → [opinion]}
      - warnings_by_target: {entity_id → [warning]}
      - warnings_flat: {warning_id → warning}
    """
    maps = {}

    # 实体 ID→对象
    for entity_type in _ENTITY_TYPES:
        collection = data[entity_type].get(entity_type, [])
        maps[entity_type] = {item["id"]: item for item in collection}

    # reviews 按 target_id 索引
    reviews_by_target = defaultdict(list)
    for r in data["reviews"].get("reviews", []):
        reviews_by_target[r["target_id"]].append(r)
    maps["reviews_by_target"] = dict(reviews_by_target)

    # opinions 按 target_id 索引
    opinions_by_target = defaultdict(list)
    for o in data["opinions"].get("opinions", []):
        opinions_by_target[o["target_id"]].append(o)
    maps["opinions_by_target"] = dict(opinions_by_target)

    # warnings 按 target_id 索引（覆盖 attraction_ids / show_ids / restaurant_ids / shortcut_ids）
    warnings_by_target = defaultdict(list)
    for w in data["warnings"].get("warnings", []):
        for field in ("attraction_ids", "show_ids", "restaurant_ids", "shortcut_ids"):
            for eid in w.get(field, []):
                warnings_by_target[eid].append(w)
    maps["warnings_by_target"] = dict(warnings_by_target)

    return maps


def _to_plain(d):
    """递归将 defaultdict 转为普通 dict，以便 JSON 序列化。"""
    if isinstance(d, defaultdict):
        return {k: _to_plain(v) for k, v in d.items()}
    if isinstance(d, dict):
        return {k: _to_plain(v) for k, v in d.items()}
    return d


def build_bidirectional_index(data, maps):
    """构建双向索引。

    返回:
      - tag_index: {tag_id → {entity_type → [entity_id]}}
      - zone_index: {zone_id → {entity_type → [entity_id]}}
      - backrefs: {entity_id → {tips, warnings, reviews, itineraries}}
      - alternative_index: {entity_id → [alternative]}
    """
    # 识别园区标签 ID
    zone_tag_ids = {
        t["id"] for t in data["tags"].get("tags", []) if t.get("category") == "zone"
    }

    tag_index = defaultdict(lambda: defaultdict(list))
    zone_index = defaultdict(lambda: defaultdict(list))

    # 遍历所有实体集合，构建 tag 和 zone 索引
    entity_collections = {
        "attractions": data["attractions"].get("attractions", []),
        "shows": data["shows"].get("shows", []),
        "restaurants": data["restaurants"].get("restaurants", []),
        "dishes": data["dishes"].get("dishes", []),
        "shortcuts": data["shortcuts"].get("shortcuts", []),
        "tips": data["tips"].get("tips", []),
        "warnings": data["warnings"].get("warnings", []),
        "itineraries": data["itineraries"].get("itineraries", []),
    }

    for entity_type, entities in entity_collections.items():
        for entity in entities:
            eid = entity["id"]
            # tag 索引
            for tag_id in entity.get("tags", []):
                tag_index[tag_id][entity_type].append(eid)
            # zone 索引：zone_id（单值）和 zone_ids（多值）统一索引
            for zid in _iter_zone_ids(entity):
                if zid in zone_tag_ids:
                    zone_index[zid][entity_type].append(eid)

    # 反向引用索引
    backrefs = defaultdict(lambda: {
        "tips": [], "warnings": [], "reviews": [], "itineraries": []
    })

    # tips → attractions
    for tip in data["tips"].get("tips", []):
        for attr_id in tip.get("attraction_ids", []):
            backrefs[attr_id]["tips"].append({
                "id": tip["id"], "title": tip.get("title", "")
            })

    # warnings → 各实体 (从 warnings_by_target map 构建)
    for entity_id, warnings in maps["warnings_by_target"].items():
        for w in warnings:
            backrefs[entity_id]["warnings"].append({
                "id": w["id"],
                "content": w.get("content", ""),
                "severity": w.get("severity", "medium"),
                "category": w.get("category", ""),
                "alternative": w.get("alternative", ""),
            })

    # reviews → 各实体 (从 reviews_by_target map 构建)
    for target_id, reviews in maps["reviews_by_target"].items():
        for r in reviews:
            backrefs[target_id]["reviews"].append({
                "id": r["id"],
                "title": r.get("title", ""),
                "rating": r.get("rating"),
            })

    # itineraries → 各实体 (字段: attraction_ids / show_ids / restaurant_ids)
    for itin in data["itineraries"].get("itineraries", []):
        for slot in itin.get("time_slots", []):
            for item in slot.get("items", []):
                entry = {
                    "id": itin["id"],
                    "name": itin.get("name", ""),
                    "time": item.get("time"),
                    "action": item.get("action", ""),
                }
                for field in ("attraction_ids", "show_ids", "restaurant_ids"):
                    for ref_id in item.get(field, []):
                        backrefs[ref_id]["itineraries"].append(entry)

    # 替代关系索引
    alternative_index = defaultdict(list)

    # 从 warnings 的替代关系构建
    for w in data["warnings"].get("warnings", []):
        source_ids = (
            w.get("attraction_ids", [])
            + w.get("restaurant_ids", [])
            + w.get("show_ids", [])
            + w.get("shortcut_ids", [])
        )
        if w.get("alternative"):
            for sid in source_ids:
                alternative_index[sid].append({
                    "type": "warning",
                    "entity_id": w["id"],
                    "name": "",
                    "reason": w["alternative"],
                })

    # 从 dishes 的 alternatives 构建
    for dish in data["dishes"].get("dishes", []):
        for alt in dish.get("alternatives", []):
            alternative_index[dish["id"]].append({
                "type": "dish",
                "entity_id": alt.get("dish_id", ""),
                "name": "",
                "reason": alt.get("note", ""),
                "alt_type": alt.get("type", ""),
            })

    return _to_plain({
        "tag_index": tag_index,
        "zone_index": zone_index,
        "backrefs": backrefs,
        "alternative_index": alternative_index,
    })


def _iter_zone_ids(entity):
    """从实体中提取所有 zone ID（兼容 zone_id 单值和 zone_ids 多值）。"""
    if entity.get("zone_id"):
        yield entity["zone_id"]
    for zid in entity.get("zone_ids", []):
        yield zid


def render_html(data, maps, indexes):
    """将数据 + maps + indexes 序列化后注入模板渲染。"""
    # 将 maps 和 indexes 注入 data，模板通过 DATA._maps / DATA._indexes 访问
    data["_maps"] = maps
    data["_indexes"] = indexes

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    template = env.get_template("guide_template.html")

    data_blob = json.dumps(data, ensure_ascii=False, indent=None, separators=(",", ":"))
    indexes_blob = json.dumps(indexes, ensure_ascii=False, indent=None, separators=(",", ":"))

    # 北京时间（UTC+8）
    beijing_tz = timezone(timedelta(hours=8))
    now_beijing = datetime.now(beijing_tz)

    html = template.render(
        data_blob=data_blob,
        indexes_blob=indexes_blob,
        generated_at=now_beijing.strftime("%Y-%m-%d %H:%M"),
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"生成完成: {OUTPUT_FILE} ({size_kb:.1f} KB)")


def main():
    print("加载数据...")
    data = load_all_data()

    # 自动更新 meta.json 的 last_updated 为当天日期（北京时间）
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).strftime("%Y-%m-%d")
    meta_path = os.path.join(DATA_DIR, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        if meta.get("last_updated") != today:
            meta["last_updated"] = today
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            print(f"已更新 meta.json last_updated → {today}")

    print("构建查找表...")
    maps = build_lookup_maps(data)

    print("构建双向索引...")
    indexes = build_bidirectional_index(data, maps)

    print("渲染HTML...")
    render_html(data, maps, indexes)


if __name__ == "__main__":
    main()
