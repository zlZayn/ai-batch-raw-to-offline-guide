"""schema_validator 冒烟测试：核心校验必须全过，计数与基线快照一致。

计数基线（2026-08-24 实跑）：唯一ID 311 / 有效引用 779 / 双向链接 234。
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "schema_validator.py"

spec = importlib.util.spec_from_file_location("schema_validator", VALIDATOR_PATH)
schema_validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schema_validator)


def _run_validation():
    """加载 data/ 并跑完整验证，返回 (validator, ok, errors)。"""
    validator = schema_validator.SchemaValidator(data_dir=str(ROOT / "data"))
    validator.load_all_data()
    ok, errors, _ = validator.validate_all()
    return validator, ok, errors


def test_validation_passes():
    """校验必须通过且无错误。"""
    _, ok, errors = _run_validation()
    assert ok
    assert errors == []


def test_snapshot_counts():
    """计数与基线条数一致，漂移即失败。"""
    validator, ok, _ = _run_validation()
    assert ok
    assert validator.stats["唯一ID数"] == 311
    assert validator.stats["有效引用数"] == 779
    assert validator.stats["双向链接数"] == 234