"""
test_dogfood_ndjson_tsv_pipeline.py -- NDJSON->TSV cross-format dogfood.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-7
Tests NDJSON records written to NDJSON then consumed by TSV-equivalent logic.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    pluck,
    group_by,
)


_RECORDS = [
    {"dept": "eng", "name": "Alice", "score": "90"},
    {"dept": "eng", "name": "Carol", "score": "85"},
    {"dept": "mkt", "name": "Bob", "score": "75"},
]


def _make_src(tmp_path):
    p = tmp_path / "data.ndjson"
    p.write_bytes(to_jsonl_str(_RECORDS).encode())
    return p


def test_pluck_names(tmp_path):
    src = _make_src(tmp_path)
    names = pluck(src, "name")
    assert names == ["Alice", "Carol", "Bob"]


def test_group_by_dept_count(tmp_path):
    src = _make_src(tmp_path)
    groups = group_by(src, "dept")
    assert len(groups["eng"]) == 2
    assert len(groups["mkt"]) == 1


def test_pluck_scores_are_strings(tmp_path):
    src = _make_src(tmp_path)
    scores = pluck(src, "score")
    # Scores stored as strings in this data
    assert all(isinstance(s, str) for s in scores)
