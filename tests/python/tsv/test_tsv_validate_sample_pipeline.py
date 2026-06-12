"""
test_tsv_validate_sample_pipeline.py -- TSV validate_headers + sample_rows pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-91
Tests validate_headers returns dict, validate_headers valid for correct headers,
sample_rows returns dict, sample_rows count=2, validate_headers invalid for wrong headers.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import validate_headers, sample_rows

_TSV_DATA = b"name\tdept\tscore\nAlice\teng\t85\nBob\thr\t72\nCarol\teng\t91\nDave\thr\t68\n"


def test_validate_headers_returns_dict(tmp_path):
    result = validate_headers(_TSV_DATA, ["name", "dept", "score"])
    assert isinstance(result, dict)


def test_validate_headers_valid_correct(tmp_path):
    result = validate_headers(_TSV_DATA, ["name", "dept", "score"])
    assert result.get("valid") is True


def test_sample_rows_returns_dict(tmp_path):
    result = sample_rows(_TSV_DATA, 2)
    assert isinstance(result, dict)
    assert "rows" in result


def test_sample_rows_count(tmp_path):
    result = sample_rows(_TSV_DATA, 2)
    assert len(result["rows"]) == 2


def test_validate_headers_invalid_wrong(tmp_path):
    result = validate_headers(_TSV_DATA, ["x", "y", "z"])
    assert result.get("valid") is False
