"""
test_tsv_headers_validate_pipeline.py -- TSV get_headers + validate_headers pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-106
Tests get_headers returns list, has name/dept/score, validate_headers valid=True for match,
validate_headers valid=False for mismatch, validate_headers has missing key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv_strict,
    get_headers,
    validate_headers,
)

_HEADERS = ["name", "dept", "score"]
_DATA = b"name\tdept\tscore\nAlice\teng\t90\nBob\thr\t75\n"


def _make_file(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv_strict(
        [["Alice", "eng", "90"], ["Bob", "hr", "75"]],
        dest,
        headers=_HEADERS,
    )
    return dest


def test_get_headers_returns_list(tmp_path):
    dest = _make_file(tmp_path)
    headers = get_headers(dest)
    assert isinstance(headers, list)


def test_get_headers_has_expected(tmp_path):
    dest = _make_file(tmp_path)
    headers = get_headers(dest)
    assert "name" in headers
    assert "dept" in headers
    assert "score" in headers


def test_validate_headers_valid_match():
    result = validate_headers(_DATA, ["name", "dept", "score"])
    assert result["valid"] is True


def test_validate_headers_invalid_mismatch():
    result = validate_headers(_DATA, ["name", "dept", "rank"])
    assert result["valid"] is False


def test_validate_headers_has_missing_key():
    result = validate_headers(_DATA, ["name", "dept", "rank"])
    assert "missing" in result
