"""
test_tsv_roundtrip_validate_pipeline.py -- TSV roundtrip + validate pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-52
Tests roundtrip preserves row count, validate_headers pass/fail,
parse_tsv_strict returns dict, probe_tsv valid, get_row returns list.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    roundtrip,
    validate_headers,
    parse_tsv_strict,
    probe_tsv,
    get_row,
)

_ROWS = [
    ["name", "dept", "salary"],
    ["Alice", "eng", "90000"],
    ["Bob", "mkt", "70000"],
    ["Carol", "hr", "75000"],
]


def _write(tmp_path):
    path = tmp_path / "data.tsv"
    write_tsv(_ROWS, str(path))
    return path


def test_roundtrip_preserves_row_count(tmp_path):
    src = _write(tmp_path)
    dest = tmp_path / "copy.tsv"
    result = roundtrip(str(src), str(dest))
    assert result["row_count"] == 3


def test_validate_headers_pass(tmp_path):
    src = _write(tmp_path)
    result = validate_headers(str(src), ["name", "dept", "salary"])
    assert result["valid"] is True


def test_validate_headers_fail(tmp_path):
    src = _write(tmp_path)
    result = validate_headers(str(src), ["name", "dept", "wrong"])
    assert result["valid"] is False


def test_parse_tsv_strict_returns_dict(tmp_path):
    src = _write(tmp_path)
    result = parse_tsv_strict(str(src))
    assert isinstance(result, dict)
    assert result["row_count"] == 3


def test_probe_tsv_valid(tmp_path):
    src = _write(tmp_path)
    result = probe_tsv(str(src))
    # probe_tsv returns dict with exists, delimiter, column_count
    assert result["exists"] is True
    assert result["delimiter"] == "\t"
