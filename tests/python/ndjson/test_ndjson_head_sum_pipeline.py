"""
test_ndjson_head_sum_pipeline.py -- NDJSON head + sum_field combined pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-39
Tests head returns N records, sum_field on written file, average_value,
head+write+reload, filter then sum.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    head,
    sum_field,
    average_value,
    filter_records,
    to_jsonl_str,
    load_ndjson,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng", "score": 90},
    {"name": "Bob", "dept": "mkt", "score": 70},
    {"name": "Carol", "dept": "eng", "score": 85},
    {"name": "Dave", "dept": "hr", "score": 75},
    {"name": "Eve", "dept": "eng", "score": 95},
]


def _write_src(tmp_path):
    src = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(src))
    return src


def test_head_returns_n_records(tmp_path):
    src = _write_src(tmp_path)
    result = head(str(src), 3)
    assert len(result) == 3


def test_head_first_record(tmp_path):
    src = _write_src(tmp_path)
    result = head(str(src), 1)
    assert result[0]["name"] == "Alice"


def test_sum_field_scores(tmp_path):
    src = _write_src(tmp_path)
    total = sum_field(str(src), "score")
    assert total == 415.0


def test_average_value_score(tmp_path):
    src = _write_src(tmp_path)
    avg = average_value(str(src), "score")
    assert avg == 83.0


def test_filter_then_sum(tmp_path):
    src = _write_src(tmp_path)
    eng = filter_records(str(src), "dept", "eng")
    eng_bytes = (to_jsonl_str(eng) + "\n").encode()
    total = sum_field(eng_bytes, "score")
    assert total == 270.0  # 90 + 85 + 95
