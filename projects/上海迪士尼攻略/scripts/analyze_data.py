
"""v3 数据结构分析：字段覆盖率、值域、稀疏性、命名规范、数值统计。"""

import json, os, math
from collections import Counter, defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'v3')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output', 'data_analysis')
os.makedirs(OUT_DIR, exist_ok=True)

def load(fname):
    with open(os.path.join(DATA_DIR, fname), 'r', encoding='utf-8') as f:
        return json.load(f)

def bar_svg(data_pairs, title, width=600, height=300):
    if not data_pairs:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><text x="{width//2}" y="{height//2}" text-anchor="middle">无数据</text></svg>'
    colors = ['#4E79A7','#F28E2B','#E15759','#76B7B2','#59A14F','#EDC948','#B07AA1','#FF9DA7','#9C755F','#BAB0AC']
    max_val = max(v for _, v in data_pairs)
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    lines.append(f'<text x="{width//2}" y="25" text-anchor="middle" font-size="16" font-weight="bold">{title}</text>')
    bar_h = min(24, (height - 60) // len(data_pairs) - 4)
    gap = bar_h + 4
    label_w = 220
    bar_area = width - label_w - 60
    for i, (label, val) in enumerate(data_pairs):
        y = 45 + i * gap
        bw = (val / max_val * bar_area) if max_val > 0 else 0
        c = colors[i % len(colors)]
        lines.append(f'<text x="{label_w-5}" y="{y+bar_h-4}" text-anchor="end" font-size="12">{label}</text>')
        lines.append(f'<rect x="{label_w}" y="{y}" width="{bw}" height="{bar_h}" fill="{c}" rx="3"/>')
        lines.append(f'<text x="{label_w+bw+5}" y="{y+bar_h-4}" font-size="11">{val}</text>')
    lines.append('</svg>')
    return '\n'.join(lines)

def pie_svg(data_pairs, title, width=500, height=320):
    total = sum(v for _, v in data_pairs)
    if total == 0:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><text x="{width//2}" y="{height//2}" text-anchor="middle">无数据</text></svg>'
    colors = ['#4E79A7','#F28E2B','#E15759','#76B7B2','#59A14F','#EDC948','#B07AA1','#FF9DA7','#9C755F','#BAB0AC']
    cx, cy, r = 160, 160, 120
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    lines.append(f'<text x="{width//2}" y="25" text-anchor="middle" font-size="16" font-weight="bold">{title}</text>')
    start = -90
    for i, (label, val) in enumerate(data_pairs):
        angle = val / total * 360
        if angle < 0.1: continue
        end = start + angle
        x1 = cx + r * math.cos(math.radians(start))
        y1 = cy + r * math.sin(math.radians(start))
        x2 = cx + r * math.cos(math.radians(end))
        y2 = cy + r * math.sin(math.radians(end))
        large = 1 if angle > 180 else 0
        lines.append(f'<path d="M{cx},{cy} L{x1},{y1} A{r},{r} 0 {large},1 {x2},{y2} Z" fill="{colors[i%len(colors)]}" stroke="white" stroke-width="2"/>')
        start = end
    lx, ly = 320, 50
    for i, (label, val) in enumerate(data_pairs):
        pct = val / total * 100
        lines.append(f'<rect x="{lx}" y="{ly}" width="14" height="14" fill="{colors[i%len(colors)]}" rx="2"/>')
        lines.append(f'<text x="{lx+20}" y="{ly+12}" font-size="12">{label} ({val}, {pct:.0f}%)</text>')
        ly += 22
    lines.append('</svg>')
    return '\n'.join(lines)

def heatmap_svg(matrix, row_labels, col_labels, title, width=700, height=400):
    """字段覆盖率热力图。matrix: [[pct, ...], ...]"""
    colors_map = lambda v: '#4E79A7' if v >= 80 else '#F28E2B' if v >= 50 else '#E15759' if v >= 25 else '#D9D9D9'
    n_rows = len(matrix)
    n_cols = len(matrix[0]) if matrix else 0
    cell_w = min(80, (width - 150) // max(n_cols, 1))
    cell_h = min(30, (height - 80) // max(n_rows, 1))
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    lines.append(f'<text x="{width//2}" y="25" text-anchor="middle" font-size="16" font-weight="bold">{title}</text>')
    # 列头
    for j, cl in enumerate(col_labels):
        x = 150 + j * cell_w
        lines.append(f'<text x="{x+cell_w//2}" y="50" text-anchor="middle" font-size="10" font-weight="bold">{cl}</text>')
    # 行
    for i, rl in enumerate(row_labels):
        y = 65 + i * cell_h
        lines.append(f'<text x="145" y="{y+cell_h//2+4}" text-anchor="end" font-size="11">{rl}</text>')
        for j in range(n_cols):
            x = 150 + j * cell_w
            v = matrix[i][j] if j < len(matrix[i]) else 0
            c = colors_map(v)
            lines.append(f'<rect x="{x}" y="{y}" width="{cell_w-2}" height="{cell_h-2}" fill="{c}" rx="3"/>')
            lines.append(f'<text x="{x+cell_w//2}" y="{y+cell_h//2+4}" text-anchor="middle" font-size="10" fill="white" font-weight="bold">{v}%</text>')
    lines.append('</svg>')
    return '\n'.join(lines)

# ============================================================
# 加载数据
# ============================================================
print('加载数据...')
tags_data = load('tags.json')
meta = load('meta.json')
attractions = load('attractions.json')
shows = load('shows.json')
restaurants = load('restaurants.json')
dishes = load('dishes.json')
tips = load('tips.json')
warnings = load('warnings.json')
itineraries = load('itineraries.json')
shortcuts = load('shortcuts.json')
reviews = load('reviews.json')
opinions = load('opinions.json')
preparations = load('preparations.json')

all_tag_defs = {t['id']: t for t in tags_data.get('tags', [])}
all_tag_names = {t['id']: t['name'] for t in tags_data.get('tags', [])}
cat_names = {c['id']: c['name'] for c in tags_data.get('categories', [])}

entity_files = [
    ('attractions', attractions), ('shows', shows), ('restaurants', restaurants),
    ('dishes', dishes), ('tips', tips), ('warnings', warnings),
    ('itineraries', itineraries), ('shortcuts', shortcuts),
    ('reviews', reviews), ('opinions', opinions),
]
entity_map = {ek: ed.get(ek, []) for ek, ed in entity_files}

# ============================================================
# 1. 全局字段覆盖率热力图
# ============================================================
print('[1] 字段覆盖率热力图...')

# 定义每个实体的关注字段
field_defs = {
    'attractions': ['id','name','zone_ids','tags','duration_minutes','indoor','water_splash',
                   'single_rider','height_requirement','locker','queue_strategy',
                   'seat_advice','review_ids','opinion_ids','warning_ids'],
    'shows': ['id','name','zone_ids','tags','location','schedule','language','is_seasonal',
              'highlights','tips','route','opinion_ids','warning_ids'],
    'restaurants': ['id','name','zone_ids','tags','location','average_price','indoor',
                    'recommended_dish_ids','review_ids','opinion_ids','warning_ids'],
    'dishes': ['id','name','restaurant_ids','zone_ids','tags','price','alternatives',
               'review_ids','opinion_ids'],
    'tips': ['id','category','title','content','tags','attraction_ids','opinion_ids'],
    'warnings': ['id','category','content','severity','alternative','alternative_details',
                 'tags','zone_ids','attraction_ids','show_ids','restaurant_ids','shortcut_ids'],
    'itineraries': ['id','name','description','tags','time_slots'],
    'shortcuts': ['id','name','from','to','route','savings','avoid_mistake','condition','tags'],
    'reviews': ['id','target_type','target_id','content','sentiment'],
    'opinions': ['id','target_type','target_id','stance','claim','reasoning'],
}

def calc_fill_rate(entities, field_path):
    """计算字段非空率。"""
    filled = 0
    for e in entities:
        parts = field_path.split('.')
        val = e
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                val = None
                break
        if val is not None and val != '' and val != []:
            filled += 1
    return round(filled / len(entities) * 100) if entities else 0

# 构建热力图数据：行=实体类型，列=字段类型
col_groups = ['ID/名称', '关联', '标签/分类', '位置', '价格/数值', '描述/内容', '引用']
row_labels = []
col_labels = []
matrix = []

for entity_key, field_list in field_defs.items():
    entities = entity_map.get(entity_key, [])

    row = []
    for f in field_list:
        rate = calc_fill_rate(entities, f)
        row.append(rate)
    matrix.append(row)
    row_labels.append(entity_key)

# 取所有字段名作为列标签
all_fields = []
for fl in field_defs.values():
    all_fields.extend(fl)
col_labels = all_fields

# 热力图太大，只取关键字段
key_fields = ['id','name','zone_ids','tags','location','price','average_price',
              'duration_minutes','indoor','water_splash','single_rider','language',
              'is_seasonal','severity','alternative','review_ids','opinion_ids','warning_ids',
              'attraction_ids','restaurant_ids','show_ids','content','description']
key_matrix = []
key_labels = []
for entity_key, field_list in field_defs.items():
    entities = entity_map.get(entity_key, [])
    row = []
    for f in key_fields:
        if f in field_list:
            row.append(calc_fill_rate(entities, f))
        else:
            row.append(-1)  # 不适用
    key_matrix.append(row)
    key_labels.append(entity_key)

with open(os.path.join(OUT_DIR, '01_field_coverage_heatmap.svg'), 'w', encoding='utf-8') as f:
    f.write(heatmap_svg(key_matrix, key_labels, key_fields, '字段覆盖率热力图（-1=不适用）', width=900, height=350))

# ============================================================
# 2. 数值字段统计
# ============================================================
print('[2] 数值字段统计...')

numeric_stats = {}
numeric_fields = {
    'attractions.duration_minutes': [],
    'attractions.height_requirement.min_cm': [],
    'restaurants.average_price': [],
    'dishes.price': [],
    'warnings.severity_score': [],  # high=3, medium=2, low=1
}
for a in attractions['attractions']:
    d = a.get('duration_minutes')
    if d is not None: numeric_fields['attractions.duration_minutes'].append(d)
    h = a.get('height_requirement')
    if h and isinstance(h, dict) and h.get('min_cm'): numeric_fields['attractions.height_requirement.min_cm'].append(h['min_cm'])
for r in restaurants['restaurants']:
    p = r.get('average_price')
    if p is not None: numeric_fields['restaurants.average_price'].append(p)
for d in dishes['dishes']:
    p = d.get('price')
    if p is not None: numeric_fields['dishes.price'].append(p)
sev_map = {'high': 3, 'medium': 2, 'low': 1}
for w in warnings['warnings']:
    s = sev_map.get(w.get('severity'), 0)
    numeric_fields['warnings.severity_score'].append(s)

stats_report = []
for field, values in numeric_fields.items():
    if not values: continue
    stats = {
        'field': field,
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'mean': round(sum(values)/len(values), 1),
        'median': sorted(values)[len(values)//2],
        'std': round((sum((v - sum(values)/len(values))**2 for v in values)/len(values))**0.5, 1),
    }
    stats_report.append(stats)
    print(f"  {field}: min={stats['min']}, max={stats['max']}, mean={stats['mean']}, median={stats['median']}")

# 数值分布图
price_vals = numeric_fields.get('dishes.price', [])
if price_vals:
    bins = {'≤30': 0, '31-50': 0, '51-80': 0, '81-100': 0, '101-150': 0, '>150': 0}
    for p in price_vals:
        if p <= 30: bins['≤30'] += 1
        elif p <= 50: bins['31-50'] += 1
        elif p <= 80: bins['51-80'] += 1
        elif p <= 100: bins['81-100'] += 1
        elif p <= 150: bins['101-150'] += 1
        else: bins['>150'] += 1
    with open(os.path.join(OUT_DIR, '02_dish_price_histogram.svg'), 'w', encoding='utf-8') as f:
        f.write(bar_svg(list(bins.items()), '菜品价格分布', width=500, height=220))

dur_vals = numeric_fields.get('attractions.duration_minutes', [])
if dur_vals:
    bins = {'1-2min': 0, '3-5min': 0, '6-10min': 0, '15+min': 0}
    for d in dur_vals:
        if d <= 2: bins['1-2min'] += 1
        elif d <= 5: bins['3-5min'] += 1
        elif d <= 10: bins['6-10min'] += 1
        else: bins['15+min'] += 1
    with open(os.path.join(OUT_DIR, '02_duration_histogram.svg'), 'w', encoding='utf-8') as f:
        f.write(bar_svg(list(bins.items()), '项目时长分布', width=500, height=200))

height_vals = numeric_fields.get('attractions.height_requirement.min_cm', [])
if height_vals:
    bins = {'无限制': 0, '100-110cm': 0, '120-132cm': 0}
    # 无限制的不在 height_vals 中，单独统计
    no_limit = sum(1 for a in attractions['attractions'] if not a.get('height_requirement'))
    for h in height_vals:
        if h <= 110: bins['100-110cm'] += 1
        else: bins['120-132cm'] += 1
    bins['无限制'] = no_limit
    with open(os.path.join(OUT_DIR, '02_height_histogram.svg'), 'w', encoding='utf-8') as f:
        f.write(bar_svg(list(bins.items()), '身高限制分布', width=500, height=200))

# ============================================================
# 3. 字段类型分布
# ============================================================
print('[3] 字段类型分布...')

type_counts = Counter()  # string, number, boolean, array, object, null
depth_counts = Counter()  # 标量 vs 嵌套

for entity_key, data in entity_files:
    entities = data.get(entity_key, [])
    for e in entities:
        for k, v in e.items():
            if v is None:
                type_counts['null'] += 1
            elif isinstance(v, bool):
                type_counts['boolean'] += 1
            elif isinstance(v, (int, float)):
                type_counts['number'] += 1
            elif isinstance(v, str):
                type_counts['string'] += 1
            elif isinstance(v, list):
                type_counts['array'] += 1
                depth_counts['array'] += 1
            elif isinstance(v, dict):
                type_counts['object'] += 1
                depth_counts['object'] += 1
            else:
                type_counts['other'] += 1

with open(os.path.join(OUT_DIR, '03_field_type_distribution.svg'), 'w', encoding='utf-8') as f:
    f.write(pie_svg(list(type_counts.items()), '字段值类型分布'))

# ============================================================
# 4. 数组字段长度分布
# ============================================================
print('[4] 数组字段长度分布...')

array_lengths = defaultdict(list)
array_field_map = {
    'zone_ids': [], 'tags': [], 'review_ids': [], 'opinion_ids': [],
    'warning_ids': [], 'attraction_ids': [], 'show_ids': [],
    'restaurant_ids': [], 'shortcut_ids': [], 'recommended_dish_ids': [],
    'source_files': [], 'highlights': [], 'tips': [],
}

for entity_key, data in entity_files:
    for e in data.get(entity_key, []):
        for f in array_field_map:
            v = e.get(f)
            if isinstance(v, list):
                array_field_map[f].append(len(v))

array_len_stats = {}
for f, lengths in array_field_map.items():
    if lengths:
        array_len_stats[f] = {
            'min': min(lengths), 'max': max(lengths),
            'mean': round(sum(lengths)/len(lengths), 1),
            'zero_count': lengths.count(0),
            'total': len(lengths),
        }

# 空数组率
empty_array_rates = []
for f, lengths in array_field_map.items():
    if lengths:
        rate = round(lengths.count(0) / len(lengths) * 100)
        empty_array_rates.append((f, rate))
empty_array_rates.sort(key=lambda x: -x[1])
with open(os.path.join(OUT_DIR, '04_empty_array_rate.svg'), 'w', encoding='utf-8') as f:
    f.write(bar_svg([(f, r) for f, r in empty_array_rates if r > 0], '数组字段空值率（%）', width=600, height=max(200, len([x for x in empty_array_rates if x[1]>0])*28+60)))

# ============================================================
# 5. 字符串字段长度分布
# ============================================================
print('[5] 字符串字段长度分布...')

str_field_lengths = defaultdict(list)
str_fields = ['name', 'content', 'description', 'alternative', 'route', 'claim', 'reasoning', 'title']
for entity_key, data in entity_files:
    for e in data.get(entity_key, []):
        for f in str_fields:
            v = e.get(f)
            if isinstance(v, str):
                str_field_lengths[f'{entity_key}.{f}'].append(len(v))

str_len_stats = {}
for f, lengths in str_field_lengths.items():
    if lengths:
        str_len_stats[f] = {
            'min': min(lengths), 'max': max(lengths),
            'mean': round(sum(lengths)/len(lengths), 1),
            'empty': lengths.count(0),
        }

# 内容长度分布（所有 content 字段合并）
all_content_lens = []
for entity_key, data in entity_files:
    for e in data.get(entity_key, []):
        for f in ['content', 'description', 'claim', 'reasoning']:
            v = e.get(f)
            if isinstance(v, str):
                all_content_lens.append(len(v))
if all_content_lens:
    bins = {'0': 0, '1-20': 0, '21-50': 0, '51-100': 0, '101-200': 0, '200+': 0}
    for l in all_content_lens:
        if l == 0: bins['0'] += 1
        elif l <= 20: bins['1-20'] += 1
        elif l <= 50: bins['21-50'] += 1
        elif l <= 100: bins['51-100'] += 1
        elif l <= 200: bins['101-200'] += 1
        else: bins['200+'] += 1
    with open(os.path.join(OUT_DIR, '05_content_length_distribution.svg'), 'w', encoding='utf-8') as f:
        f.write(bar_svg(list(bins.items()), '文本字段长度分布（所有 content/description/claim）', width=500, height=220))

# ============================================================
# 6. ID 命名规范分析
# ============================================================
print('[6] ID 命名规范分析...')

id_patterns = Counter()
all_ids = []
for entity_key, data in entity_files:
    for e in data.get(entity_key, []):
        eid = e.get('id', '')
        if eid:
            all_ids.append((entity_key, eid))
            parts = eid.split('_')
            if len(parts) >= 1:
                id_patterns[parts[0]] += 1

with open(os.path.join(OUT_DIR, '06_id_prefix_distribution.svg'), 'w', encoding='utf-8') as f:
    f.write(bar_svg(list(id_patterns.most_common()), 'ID 前缀分布', width=500, height=350))

# ID 长度分布
id_lens = Counter(len(eid) for _, eid in all_ids)
with open(os.path.join(OUT_DIR, '06_id_length_distribution.svg'), 'w', encoding='utf-8') as f:
    f.write(bar_svg(sorted(id_lens.items()), 'ID 长度分布', width=500, height=200))

# ============================================================
# 7. 引用字段分析
# ============================================================
print('[7] 引用字段分析...')

ref_field_stats = []
ref_fields = [
    ('attractions', 'review_ids', 'reviews'), ('attractions', 'opinion_ids', 'opinions'),
    ('attractions', 'warning_ids', 'warnings'),
    ('shows', 'opinion_ids', 'opinions'), ('shows', 'warning_ids', 'warnings'),
    ('restaurants', 'recommended_dish_ids', 'dishes'),
    ('restaurants', 'review_ids', 'reviews'), ('restaurants', 'opinion_ids', 'opinions'),
    ('restaurants', 'warning_ids', 'warnings'),
    ('dishes', 'restaurant_ids', 'restaurants'),
    ('dishes', 'review_ids', 'reviews'), ('dishes', 'opinion_ids', 'opinions'),
    ('tips', 'attraction_ids', 'attractions'), ('tips', 'opinion_ids', 'opinions'),
    ('warnings', 'attraction_ids', 'attractions'), ('warnings', 'show_ids', 'shows'),
    ('warnings', 'restaurant_ids', 'restaurants'), ('warnings', 'shortcut_ids', 'shortcuts'),
    ('reviews', 'target_id', 'target'),
    ('opinions', 'target_id', 'target'),
]

for entity_key, ref_field, target_type in ref_fields:
    entities = entity_map.get(entity_key, [])
    if not entities: continue
    lengths = []
    for e in entities:
        if not isinstance(e, dict): continue
        v = e.get(ref_field)
        if isinstance(v, list):
            lengths.append(len(v))
        elif isinstance(v, str):
            lengths.append(1 if v else 0)
    if lengths:
        ref_field_stats.append({
            'from': entity_key,
            'field': ref_field,
            'to': target_type,
            'entities': len(entities),
            'with_ref': sum(1 for l in lengths if l > 0),
            'total_refs': sum(lengths),
            'avg_refs': round(sum(lengths)/len(lengths), 1),
            'max_refs': max(lengths),
        })

# 引用密度图
ref_density = [(f"{s['from']}.{s['field']}→{s['to']}", s['avg_refs']) for s in ref_field_stats]
ref_density.sort(key=lambda x: -x[1])
with open(os.path.join(OUT_DIR, '07_ref_density.svg'), 'w', encoding='utf-8') as f:
    f.write(bar_svg(ref_density[:20], '引用字段平均引用数', width=600, height=560))

# ============================================================
# 8. 嵌套深度分析
# ============================================================
print('[8] 嵌套深度分析...')

def max_depth(obj, d=0):
    if isinstance(obj, dict):
        if not obj: return d
        return max(max_depth(v, d+1) for v in obj.values())
    elif isinstance(obj, list):
        if not obj: return d
        return max(max_depth(v, d+1) for v in obj)
    return d

depth_stats = {}
for entity_key, data in entity_files:
    entities = data.get(entity_key, [])
    if not entities: continue
    depths = [max_depth(e) for e in entities]
    depth_stats[entity_key] = {
        'max_depth': max(depths),
        'avg_depth': round(sum(depths)/len(depths), 1),
    }

with open(os.path.join(OUT_DIR, '08_nesting_depth.svg'), 'w', encoding='utf-8') as f:
    f.write(bar_svg([(k, v['max_depth']) for k, v in depth_stats.items()], '各实体最大嵌套深度', width=500, height=280))

# ============================================================
# 9. 数据规模概览
# ============================================================
print('[9] 数据规模概览...')

scale_data = {}
for entity_key, data in entity_files:
    entities = data.get(entity_key, [])
    if entities:
        # 估算 JSON 大小
        raw = json.dumps(entities, ensure_ascii=False)
        scale_data[entity_key] = {
            'count': len(entities),
            'fields': len(entities[0].keys()) if entities else 0,
            'size_bytes': len(raw.encode('utf-8')),
            'size_kb': round(len(raw.encode('utf-8')) / 1024, 1),
        }

with open(os.path.join(OUT_DIR, '09_entity_size.svg'), 'w', encoding='utf-8') as f:
    f.write(bar_svg([(k, v['size_kb']) for k, v in scale_data.items()], '各实体 JSON 大小 (KB)', width=500, height=320))

with open(os.path.join(OUT_DIR, '09_entity_field_count.svg'), 'w', encoding='utf-8') as f:
    f.write(bar_svg([(k, v['fields']) for k, v in scale_data.items()], '各实体字段数量', width=500, height=320))

# ============================================================
# 写 JSON 报告
# ============================================================
print('[10] 写 JSON 报告...')

report = {
    '数值字段统计': stats_report,
    '字段类型分布': dict(type_counts),
    '数组空值率': {f: r for f, r in empty_array_rates},
    '数组长度统计': array_len_stats,
    '文本长度统计': str_len_stats,
    'ID前缀分布': dict(id_patterns),
    '引用字段统计': ref_field_stats,
    '嵌套深度': depth_stats,
    '数据规模': scale_data,
}

with open(os.path.join(OUT_DIR, 'report.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f'\n完成！产出保存在: {OUT_DIR}')
for fname in sorted(os.listdir(OUT_DIR)):
    fpath = os.path.join(OUT_DIR, fname)
    size = os.path.getsize(fpath)
    print(f'  {fname}: {size/1024:.1f} KB')
