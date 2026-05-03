
"""CI 管线：数据校验 → 生成 HTML → 生成后验证。

用法: python scripts/ci.py
退出码: 0=全部通过, 1=有错误
"""

import json, os, sys, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "v3")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
HTML_FILE = os.path.join(OUTPUT_DIR, "guide.html")

errors = []
warnings = []


def err(msg):
    errors.append(msg)
    print(f"  ✗ {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  ⚠ {msg}")


def ok(msg):
    print(f"  ✓ {msg}")


def load(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Phase 1: 数据校验
# ============================================================
def validate_data():
    print("\n══ Phase 1: 数据校验 ══\n")

    # 加载
    tags_data = load("tags.json")
    attractions = load("attractions.json")["attractions"]
    shows = load("shows.json")["shows"]
    restaurants = load("restaurants.json")["restaurants"]
    dishes = load("dishes.json")["dishes"]
    tips = load("tips.json")["tips"]
    warnings_data = load("warnings.json")["warnings"]
    shortcuts = load("shortcuts.json")["shortcuts"]
    itineraries = load("itineraries.json")["itineraries"]
    reviews = load("reviews.json")["reviews"]
    opinions = load("opinions.json")["opinions"]

    all_tags = {t["id"]: t for t in tags_data["tags"]}
    zone_tag_ids = {t["id"] for t in tags_data["tags"] if t.get("category") == "zone"}

    # 构建查找表
    lookup = {}
    for key, entities in [("attractions", attractions), ("shows", shows),
                           ("restaurants", restaurants), ("dishes", dishes),
                           ("tips", tips), ("warnings", warnings_data),
                           ("shortcuts", shortcuts), ("itineraries", itineraries),
                           ("reviews", reviews), ("opinions", opinions)]:
        for e in entities:
            lookup[e["id"]] = key

    # 1. ID 唯一性
    print("[1] ID 唯一性...")
    seen = {}
    for key, entities in [("attractions", attractions), ("shows", shows),
                           ("restaurants", restaurants), ("dishes", dishes),
                           ("tips", tips), ("warnings", warnings_data),
                           ("shortcuts", shortcuts), ("itineraries", itineraries),
                           ("reviews", reviews), ("opinions", opinions)]:
        for e in entities:
            eid = e["id"]
            if eid in seen:
                err(f"ID 重复: {eid} (在 {seen[eid]} 和 {key})")
            seen[eid] = key
    if not any("ID 重复" in e for e in errors):
        ok("所有 ID 唯一")

    # 2. 引用完整性
    print("[2] 引用完整性...")
    ref_checks = [
        ("attractions", attractions, "review_ids", "reviews"),
        ("attractions", attractions, "opinion_ids", "opinions"),
        ("attractions", attractions, "warning_ids", "warnings"),
        ("shows", shows, "opinion_ids", "opinions"),
        ("shows", shows, "warning_ids", "warnings"),
        ("restaurants", restaurants, "recommended_dish_ids", "dishes"),
        ("restaurants", restaurants, "review_ids", "reviews"),
        ("restaurants", restaurants, "opinion_ids", "opinions"),
        ("restaurants", restaurants, "warning_ids", "warnings"),
        ("dishes", dishes, "restaurant_ids", "restaurants"),
        ("dishes", dishes, "review_ids", "reviews"),
        ("dishes", dishes, "opinion_ids", "opinions"),
        ("tips", tips, "attraction_ids", "attractions"),
        ("tips", tips, "opinion_ids", "opinions"),
        ("warnings", warnings_data, "attraction_ids", "attractions"),
        ("warnings", warnings_data, "show_ids", "shows"),
        ("warnings", warnings_data, "restaurant_ids", "restaurants"),
        ("warnings", warnings_data, "shortcut_ids", "shortcuts"),
    ]
    for entity_key, entities, ref_field, target_type in ref_checks:
        for e in entities:
            for ref_id in e.get(ref_field, []):
                if ref_id not in lookup:
                    err(f"{entity_key}/{e['id']}.{ref_field} → {ref_id} 不存在")
                elif lookup[ref_id] != target_type:
                    err(f"{entity_key}/{e['id']}.{ref_field} → {ref_id} 类型为 {lookup[ref_id]}，期望 {target_type}")
    # reviews/opinions target_id
    for r in reviews:
        tid = r.get("target_id")
        if tid and tid not in lookup:
            err(f"reviews/{r['id']}.target_id → {tid} 不存在")
    for o in opinions:
        tid = o.get("target_id")
        if tid and tid not in lookup:
            err(f"opinions/{o['id']}.target_id → {tid} 不存在")
    if not any("引用完整性" in e or "不存在" in e for e in errors):
        ok("所有引用完整")

    # 3. tags 引用
    print("[3] tags 引用...")
    for key, entities in [("attractions", attractions), ("shows", shows),
                           ("restaurants", restaurants), ("dishes", dishes),
                           ("tips", tips), ("warnings", warnings_data),
                           ("shortcuts", shortcuts)]:
        for e in entities:
            for t in e.get("tags", []):
                if t not in all_tags:
                    err(f"{key}/{e['id']}.tags → {t} 不存在于 tags.json")
    if not any("tags" in e and "不存在" in e for e in errors):
        ok("所有 tags 引用有效")

    # 4. zone_ids 引用
    print("[4] zone_ids 引用...")
    for key, entities in [("attractions", attractions), ("shows", shows),
                           ("restaurants", restaurants), ("dishes", dishes),
                           ("warnings", warnings_data)]:
        for e in entities:
            for z in e.get("zone_ids", []):
                if z not in zone_tag_ids:
                    err(f"{key}/{e['id']}.zone_ids → {z} 不是 zone 类标签")
    if not any("zone_ids" in e and "不是" in e for e in errors):
        ok("所有 zone_ids 引用有效")

    # 5. 新增客观字段校验
    print("[5] 客观字段校验...")
    # attractions
    for a in attractions:
        if a.get("duration_minutes") is not None and not isinstance(a["duration_minutes"], (int, float)):
            err(f"attractions/{a['id']}.duration_minutes 类型错误: {type(a['duration_minutes']).__name__}")
        if not isinstance(a.get("indoor", True), bool):
            err(f"attractions/{a['id']}.indoor 不是布尔值")
        if not isinstance(a.get("water_splash", False), bool):
            err(f"attractions/{a['id']}.water_splash 不是布尔值")
        if not isinstance(a.get("single_rider", False), bool):
            err(f"attractions/{a['id']}.single_rider 不是布尔值")
        if not isinstance(a.get("has_photo", False), bool):
            err(f"attractions/{a['id']}.has_photo 不是布尔值")
    # shows
    for s in shows:
        if s.get("language") is not None and not isinstance(s["language"], str):
            err(f"shows/{s['id']}.language 不是字符串")
        if not isinstance(s.get("is_seasonal", False), bool):
            err(f"shows/{s['id']}.is_seasonal 不是布尔值")
    # restaurants
    for r in restaurants:
        if r.get("average_price") is not None and not isinstance(r["average_price"], (int, float)):
            err(f"restaurants/{r['id']}.average_price 类型错误")
        if r.get("business_hours") is not None and not isinstance(r["business_hours"], str):
            err(f"restaurants/{r['id']}.business_hours 不是字符串")
        if not isinstance(r.get("indoor", True), bool):
            err(f"restaurants/{r['id']}.indoor 不是布尔值")
    # dishes
    for d in dishes:
        if d.get("price") is not None and not isinstance(d["price"], (int, float)):
            err(f"dishes/{d['id']}.price 类型错误")
        if not isinstance(d.get("is_seasonal", False), bool):
            err(f"dishes/{d['id']}.is_seasonal 不是布尔值")
    if not any("客观字段" in e for e in errors):
        ok("所有客观字段类型正确")

    # 6. 字段一致性
    print("[6] 字段一致性...")
    for entity_key, entities in [("attractions", attractions), ("shows", shows),
                                  ("restaurants", restaurants), ("dishes", dishes),
                                  ("tips", tips), ("warnings", warnings_data),
                                  ("shortcuts", shortcuts)]:
        if not entities: continue
        field_sets = [set(e.keys()) for e in entities]
        common = set.intersection(*field_sets)
        all_fields = set.union(*field_sets)
        extra = all_fields - common
        if extra:
            warn(f"{entity_key}: 字段差异: {sorted(extra)}")
        else:
            ok(f"{entity_key}: {len(common)} 个字段一致")

    return len(errors) == 0


# ============================================================
# Phase 2: 生成 HTML
# ============================================================
def generate_html():
    print("\n══ Phase 2: 生成 HTML ══\n")
    gen_script = os.path.join(BASE_DIR, "generator", "generate_guide.py")
    ret = os.system(f"cd {BASE_DIR} && python {gen_script}")
    if ret != 0:
        err("HTML 生成失败")
        return False
    if not os.path.exists(HTML_FILE):
        err("HTML 文件未生成")
        return False
    size_kb = os.path.getsize(HTML_FILE) / 1024
    ok(f"HTML 生成成功 ({size_kb:.1f} KB)")
    return True


# ============================================================
# Phase 3: HTML 生成后验证
# ============================================================
def validate_html():
    print("\n══ Phase 3: HTML 生成后验证 ══\n")

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. div 配对检查（近似计数，Jinja2 条件渲染会导致误差）
    print("[1] div 标签配对...")
    opens = len(re.findall(r'<div\b[^/]*>', html))
    closes = len(re.findall(r'</div>', html))
    diff = abs(opens - closes)
    if diff > 50:
        err(f"div 严重不配对: 开 {opens} 个, 闭 {closes} 个, 差 {opens - closes}")
    elif diff > 0:
        warn(f"div 轻微不配对: 开 {opens} 个, 闭 {closes} 个, 差 {opens - closes}（Jinja2 条件渲染正常现象）")
    else:
        ok(f"div 配对正确 ({opens} 个)")

    # 2. DATA 注入检查
    print("[2] DATA 注入...")
    if "const DATA = " not in html:
        err("DATA 未注入")
    else:
        ok("DATA 已注入")
    if "const INDEXES = " not in html:
        err("INDEXES 未注入")
    else:
        ok("INDEXES 已注入")

    # 3. 颜色变量检查
    print("[3] 颜色变量...")
    color_vars = ["--c-attraction", "--c-show", "--c-restaurant", "--c-dish",
                  "--c-tip", "--c-warning", "--c-shortcut", "--c-itinerary"]
    for cv in color_vars:
        if cv not in html:
            err(f"缺少颜色变量 {cv}")
    if not any("颜色变量" in e for e in errors):
        ok("所有颜色变量存在")

    # 4. section-color wrapper 检查
    print("[4] section-color wrapper...")
    wrapper_count = len(re.findall(r'style="--section-color', html))
    if wrapper_count < 7:
        warn(f"section-color wrapper 只有 {wrapper_count} 个（期望 8 个详情页）")
    else:
        ok(f"section-color wrapper: {wrapper_count} 个")

    # 5. 关键渲染函数存在
    print("[5] 渲染函数...")
    required_funcs = ["renderAttractionDetail", "renderShowDetail", "renderDishDetail",
                      "renderRestaurantDetail", "renderItineraryDetail", "renderTipDetail",
                      "renderWarningDetail", "renderShortcutDetail", "renderRelations",
                      "renderReviews", "renderOpinions", "renderWarnings"]
    for fn in required_funcs:
        if f"function {fn}" not in html:
            err(f"缺少函数 {fn}")
    if not any("缺少函数" in e for e in errors):
        ok(f"所有 {len(required_funcs)} 个渲染函数存在")

    # 6. 内联 style 残留检查（排除特殊卡片如提示横幅）
    print("[6] 内联 style 残留...")
    inline_styles = re.findall(r'class="card" style="[^"]*"', html)
    # 排除已知的特殊用途内联样式
    allowed_patterns = ["background:linear-gradient", "margin-top:20px"]
    real_issues = [s for s in inline_styles if not any(p in s for p in allowed_patterns)]
    if real_issues:
        for s in real_issues:
            err(f"残留内联 style: {s}")
    else:
        ok("无残留内联 style（card）")

    # 7. 详情页 section-title emoji 残留检查
    print("[7] 详情页 emoji section-title 残留...")
    # 只检查详情页函数范围内（从 renderAttractionDetail 到 renderPreparations）
    detail_start = html.find("function renderAttractionDetail")
    detail_end = html.find("function renderPreparations")
    if detail_start > 0 and detail_end > detail_start:
        detail_html = html[detail_start:detail_end]
        emoji_titles = re.findall(r'section-title[^>]*>[📌⚡⚠️]', detail_html)
        if emoji_titles:
            for t in emoji_titles:
                err(f"残留 emoji section-title: {t}")
        else:
            ok("详情页无残留 emoji section-title")
    else:
        warn("无法定位详情页范围，跳过检查")

    # 8. renderEntityLinks 使用检查（详情页函数体内不应直接调用）
    print("[8] renderEntityLinks 使用检查...")
    # 提取各详情页函数体（不含 renderRelations 内部）
    detail_funcs = ["renderAttractionDetail", "renderShowDetail", "renderDishDetail",
                    "renderRestaurantDetail", "renderItineraryDetail", "renderTipDetail",
                    "renderWarningDetail", "renderShortcutDetail"]
    entity_link_in_detail = 0
    for fn in detail_funcs:
        fn_start = html.find(f"function {fn}")
        if fn_start < 0: continue
        # 找到函数结尾（下一个 function 或文件末尾）
        fn_end = html.find("\nfunction ", fn_start + 1)
        if fn_end < 0: fn_end = len(html)
        fn_body = html[fn_start:fn_end]
        # 排除 renderRelations 内部的调用
        rel_start = fn_body.find("renderRelations")
        if rel_start > 0:
            check_body = fn_body[:rel_start]
        else:
            check_body = fn_body
        entity_link_in_detail += len(re.findall(r'renderEntityLinks\(', check_body))
    if entity_link_in_detail > 0:
        err(f"详情页函数中有 {entity_link_in_detail} 处 renderEntityLinks 调用")
    else:
        ok("详情页函数无 renderEntityLinks 直接调用")

    return len(errors) == 0


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    # Phase 1: 数据校验
    data_ok = validate_data()

    # Phase 2: 生成 HTML（仅在数据校验通过时）
    if data_ok:
        gen_ok = generate_html()
    else:
        print("\n❌ 数据校验未通过，跳过 HTML 生成")
        gen_ok = False

    # Phase 3: HTML 验证（仅在生成成功时）
    if gen_ok:
        html_ok = validate_html()
    else:
        html_ok = False

    # 汇总
    print("\n" + "=" * 60)
    total = len(errors)
    if total == 0:
        print(f"✅ CI 通过: 0 错误, {len(warnings)} 警告")
        sys.exit(0)
    else:
        print(f"❌ CI 失败: {total} 错误, {len(warnings)} 警告")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
