"""Print entity count per JSON file. Usage:
python scripts/stats.py
python scripts/stats.py <path/to/data_v3>
"""

import json, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data", "v3")

if len(sys.argv) > 1:
    DATA_DIR = os.path.join(BASE, sys.argv[1])
if not os.path.isdir(DATA_DIR):
    print(f"[ERR] {DATA_DIR} not found")
    sys.exit(1)

files = sorted(f for f in os.listdir(DATA_DIR) if f.endswith(".json"))
total = 0
for fname in files:
    with open(os.path.join(DATA_DIR, fname), "rb") as f:
        data = json.load(f)
    counts = {k: len(v) for k, v in data.items() if isinstance(v, list)}
    n = sum(counts.values())
    total += n
    label = fname.replace(".json", "")

    if len(counts) == 1:
        key = list(counts.keys())[0]
        if key == label:
            print(f"  {label:20s} {n:>4}")
        else:
            print(f"  {label:20s} {n:>4}  ({key})")
    else:
        details = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"  {label:20s} {n:>4}  [{details}]")

print(f"  {'─' * 20} ────")
print(f"  {'Total':20s} {total:>4}")
