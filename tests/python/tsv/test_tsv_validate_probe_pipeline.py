"""
test_tsv_validate_probe_pipeline.py -- TSV validate + probe pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-64
Tests validate_headers pass, validate_headers fail, probe_tsv exists,
probe_tsv delimiter, parse_tsv_strict returns dict.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    validate_headers,
    probe_tsv,
    parse_tsv_strict,
    write_tsv,
)

_TSV_DATA = b"name\tdept\tscore\nAlice\teng\t90\nBob\tmkt\t70\n"


def test_validate_headers_pass():
    result = validate_headers(_TSV_DATA, ["name", "dept", "score"])
    assert result["valid"] is True


def test_validate_headers_fail():
    result = validate_headers(_TSV_DATA, ["name", "missing_col"])
    assert result["valid"] is False


def test_probe_tsv_exists(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv([["Alice", "eng", "90"]], str(dest), headers=["name", "dept", "score"])
    result = probe_tsv(str(dest))
    assert result["exists"] is True


def test_probe_tsv_delimiter(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv([["Alice", "eng", "90"]], str(dest), headers=["name", "dept", "score"])
    result = probe_tsv(str(dest))
    assert result["delimiter"] == "\t"


def test_parse_tsv_strict_returns_dict(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv([["Alice", "eng", "90"]], str(dest), headers=["name", "dept", "score"])
    result = parse_tsv_strict(str(dest))
    assert isinstance(result, dict)
    assert "headers" in result
