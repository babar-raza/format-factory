"""Roundtrip tests for tsv_writer.py — TC-W4-001."""
from __future__ import annotations

import pytest
from pathlib import Path
from tsv.tsv_writer import write_tsv, write_tsv_str, TsvWriteError
from tsv.tsv_parser import parse_tsv_strict


def test_write_tsv_str_rows_only():
    rows = [["Alice", "30"], ["Bob", "25"]]
    out = write_tsv_str(rows)
    lines = out.strip().split("\n")
    assert lines[0] == "Alice\t30"
    assert lines[1] == "Bob\t25"


def test_write_tsv_str_with_headers():
    rows = [["Alice", "30"]]
    out = write_tsv_str(rows, headers=["Name", "Age"])
    lines = out.strip().split("\n")
    assert lines[0] == "Name\tAge"
    assert lines[1] == "Alice\t30"


def test_write_tsv_str_empty_rows():
    out = write_tsv_str([])
    assert out == ""


def test_write_tsv_tab_in_value_raises():
    with pytest.raises(TsvWriteError, match="tab"):
        write_tsv_str([["value\twith\ttabs"]])


def test_write_tsv_roundtrip(tmp_path):
    rows = [["Alpha", "1", "true"], ["Beta", "2", "false"]]
    headers = ["Name", "Count", "Active"]
    path = tmp_path / "out.tsv"
    write_tsv(rows, path, headers=headers)
    result = parse_tsv_strict(str(path))
    assert result.get("format") == "tsv"
    returned_rows = result.get("rows", [])
    assert returned_rows[0] == ["Alpha", "1", "true"]
    assert returned_rows[1] == ["Beta", "2", "false"]


def test_write_tsv_none_value_serialized_as_empty():
    out = write_tsv_str([[None, "value"]])
    # Use rstrip (not strip) to preserve leading tabs for empty fields
    line = out.rstrip("\n").split("\n")[0]
    parts = line.split("\t")
    assert parts[0] == ""   # None → empty string
    assert parts[1] == "value"
