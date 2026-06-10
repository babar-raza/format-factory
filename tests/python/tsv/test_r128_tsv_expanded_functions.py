"""Tests for expanded TSV functions added in capability-layer-full-hardening sprint.

Covers: get_column, write_tsv_strict, get_row, validate_headers, count_rows,
        to_csv, deduplicate_rows, get_row_by_key
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest
from src.python.tsv.tsv_parser import (
    get_column,
    write_tsv_strict,
    get_row,
    validate_headers,
    count_rows,
    to_csv,
    deduplicate_rows,
    get_row_by_key,
    TsvError,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_TSV = b"name\tage\tcity\nAlice\t30\tLondon\nBob\t25\tParis\nCarol\t30\tLondon\n"
DUP_TSV = b"name\tscore\nAlice\t90\nBob\t80\nAlice\t90\nBob\t80\nCarol\t70\n"


# ---------------------------------------------------------------------------
# get_column tests
# ---------------------------------------------------------------------------

def test_get_column_returns_column_values():
    values = get_column(SAMPLE_TSV, "name")
    assert values == ["Alice", "Bob", "Carol"]


def test_get_column_returns_second_column():
    values = get_column(SAMPLE_TSV, "age")
    assert values == ["30", "25", "30"]


def test_get_column_missing_column_returns_empty():
    values = get_column(SAMPLE_TSV, "nonexistent")
    assert values == []


def test_get_column_from_file(tmp_path):
    f = tmp_path / "data.tsv"
    f.write_bytes(SAMPLE_TSV)
    values = get_column(str(f), "city")
    assert values == ["London", "Paris", "London"]


# ---------------------------------------------------------------------------
# write_tsv_strict tests
# ---------------------------------------------------------------------------

def test_write_tsv_strict_writes_clean_data(tmp_path):
    dest = tmp_path / "out.tsv"
    headers = ["a", "b"]
    rows = [["1", "2"], ["3", "4"]]
    write_tsv_strict(rows, dest, headers=headers)
    content = dest.read_text(encoding="utf-8")
    assert "a\tb" in content
    assert "1\t2" in content


def test_write_tsv_strict_raises_on_tab_in_cell(tmp_path):
    dest = tmp_path / "bad.tsv"
    rows = [["hello\tworld", "ok"]]
    with pytest.raises(TsvError, match="tab"):
        write_tsv_strict(rows, dest)


def test_write_tsv_strict_raises_on_newline_in_cell(tmp_path):
    dest = tmp_path / "bad.tsv"
    rows = [["line1\nline2", "ok"]]
    with pytest.raises(TsvError, match="newline"):
        write_tsv_strict(rows, dest)


def test_write_tsv_strict_no_headers_ok(tmp_path):
    dest = tmp_path / "noheader.tsv"
    rows = [["x", "y"], ["a", "b"]]
    write_tsv_strict(rows, dest)
    content = dest.read_text(encoding="utf-8")
    assert "x\ty" in content


# ---------------------------------------------------------------------------
# get_row tests
# ---------------------------------------------------------------------------

def test_get_row_first_data_row():
    row = get_row(SAMPLE_TSV, 0)
    assert row == ["Alice", "30", "London"]


def test_get_row_second_data_row():
    row = get_row(SAMPLE_TSV, 1)
    assert row == ["Bob", "25", "Paris"]


def test_get_row_out_of_range_raises():
    with pytest.raises(IndexError):
        get_row(SAMPLE_TSV, 99)


def test_get_row_negative_index_raises():
    with pytest.raises(IndexError):
        get_row(SAMPLE_TSV, -1)


# ---------------------------------------------------------------------------
# validate_headers tests
# ---------------------------------------------------------------------------

def test_validate_headers_exact_match():
    result = validate_headers(SAMPLE_TSV, ["name", "age", "city"])
    assert result["valid"] is True
    assert result["missing"] == []
    assert result["extra"] == []


def test_validate_headers_missing_header():
    result = validate_headers(SAMPLE_TSV, ["name", "age", "city", "country"])
    assert result["valid"] is False
    assert "country" in result["missing"]


def test_validate_headers_extra_header():
    result = validate_headers(SAMPLE_TSV, ["name"])
    assert result["valid"] is False
    assert "age" in result["extra"]
    assert "city" in result["extra"]


def test_validate_headers_returns_actual():
    result = validate_headers(SAMPLE_TSV, ["name", "age", "city"])
    assert result["actual"] == ["name", "age", "city"]


# ---------------------------------------------------------------------------
# count_rows tests
# ---------------------------------------------------------------------------

def test_count_rows_with_header():
    count = count_rows(SAMPLE_TSV)
    assert count == 3


def test_count_rows_empty():
    count = count_rows(b"")
    assert count == 0


def test_count_rows_from_file(tmp_path):
    f = tmp_path / "data.tsv"
    f.write_bytes(SAMPLE_TSV)
    assert count_rows(str(f)) == 3


def test_count_rows_duplicates_counted():
    count = count_rows(DUP_TSV)
    assert count == 5


# ---------------------------------------------------------------------------
# to_csv tests
# ---------------------------------------------------------------------------

def test_to_csv_basic():
    csv_str = to_csv(SAMPLE_TSV)
    assert "name,age,city" in csv_str
    assert "Alice,30,London" in csv_str


def test_to_csv_contains_all_rows():
    csv_str = to_csv(SAMPLE_TSV)
    assert "Bob,25,Paris" in csv_str
    assert "Carol,30,London" in csv_str


def test_to_csv_quotes_commas():
    data = b"name\taddress\nAlice\t123 Main, Apt 4\n"
    csv_str = to_csv(data)
    assert '"123 Main, Apt 4"' in csv_str


def test_to_csv_uses_crlf_endings():
    csv_str = to_csv(SAMPLE_TSV)
    assert "\r\n" in csv_str


# ---------------------------------------------------------------------------
# deduplicate_rows tests
# ---------------------------------------------------------------------------

def test_deduplicate_rows_removes_duplicates():
    rows = deduplicate_rows(DUP_TSV)
    assert len(rows) == 3


def test_deduplicate_rows_preserves_order():
    rows = deduplicate_rows(DUP_TSV)
    assert rows[0] == ["Alice", "90"]
    assert rows[1] == ["Bob", "80"]
    assert rows[2] == ["Carol", "70"]


def test_deduplicate_rows_no_duplicates_unchanged():
    rows = deduplicate_rows(SAMPLE_TSV)
    assert len(rows) == 3


def test_deduplicate_rows_all_same():
    data = b"name\tval\nA\t1\nA\t1\nA\t1\n"
    rows = deduplicate_rows(data)
    assert len(rows) == 1
    assert rows[0] == ["A", "1"]


# ---------------------------------------------------------------------------
# get_row_by_key tests
# ---------------------------------------------------------------------------

def test_get_row_by_key_finds_row():
    row = get_row_by_key(SAMPLE_TSV, "name", "Bob")
    assert row == ["Bob", "25", "Paris"]


def test_get_row_by_key_returns_none_when_not_found():
    row = get_row_by_key(SAMPLE_TSV, "name", "Dave")
    assert row is None


def test_get_row_by_key_missing_column_raises():
    with pytest.raises(TsvError, match="country"):
        get_row_by_key(SAMPLE_TSV, "country", "UK")


def test_get_row_by_key_returns_first_match():
    row = get_row_by_key(SAMPLE_TSV, "age", "30")
    assert row == ["Alice", "30", "London"]
