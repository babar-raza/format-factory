"""Tests for TSV append_row capability (gap: GAP-TSV-FOSS-APPEND_ROW-001).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-VERIFICATION-PRODUCT-AUTONOMY-MEGA-SPRINT
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.tsv.tsv_parser import append_row, load_tsv, write_tsv, TsvError


def test_append_row_to_existing_file(tmp_path):
    """append_row adds a row to an existing TSV file."""
    f = tmp_path / "data.tsv"
    write_tsv([["a", "b"], ["c", "d"]], f, headers=["x", "y"])
    append_row(f, ["e", "f"])
    result = load_tsv(f)
    assert result["row_count"] == 3
    assert result["rows"][-1] == ["e", "f"]


def test_append_row_creates_file_if_missing(tmp_path):
    """append_row creates the file if it does not exist."""
    f = tmp_path / "new.tsv"
    assert not f.exists()
    append_row(f, ["hello", "world"])
    assert f.exists()
    content = f.read_text(encoding="utf-8")
    assert "hello\tworld" in content


def test_append_row_multiple_calls(tmp_path):
    """Multiple append_row calls accumulate rows."""
    f = tmp_path / "acc.tsv"
    append_row(f, ["r1c1", "r1c2"])
    append_row(f, ["r2c1", "r2c2"])
    append_row(f, ["r3c1", "r3c2"])
    lines = f.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    assert lines[0] == "r1c1\tr1c2"
    assert lines[2] == "r3c1\tr3c2"


def test_append_row_escapes_tabs_and_newlines(tmp_path):
    """Tab and newline chars within values are replaced with spaces."""
    f = tmp_path / "esc.tsv"
    append_row(f, ["col\twith\ttabs", "col\nwith\nnewlines"])
    line = f.read_text(encoding="utf-8").strip()
    assert "\t" not in line.split("\t", 1)[0]  # first field has no tabs
    fields = line.split("\t")
    assert len(fields) == 2
    assert "\n" not in fields[1]


def test_append_row_empty_row(tmp_path):
    """append_row handles an empty row (single newline)."""
    f = tmp_path / "empty.tsv"
    append_row(f, [])
    content = f.read_text(encoding="utf-8")
    assert content == "\n"


def test_append_row_single_value(tmp_path):
    """append_row with a single-element row."""
    f = tmp_path / "single.tsv"
    append_row(f, ["only"])
    content = f.read_text(encoding="utf-8").strip()
    assert content == "only"


def test_append_row_non_string_values(tmp_path):
    """append_row coerces non-string values via str()."""
    f = tmp_path / "nums.tsv"
    append_row(f, [1, 2.5, True, None])
    line = f.read_text(encoding="utf-8").strip()
    assert line == "1\t2.5\tTrue\tNone"


def test_append_row_preserves_existing_content(tmp_path):
    """append_row does not overwrite existing file content."""
    f = tmp_path / "preserve.tsv"
    f.write_text("header1\theader2\nval1\tval2\n", encoding="utf-8")
    append_row(f, ["newval1", "newval2"])
    lines = f.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    assert lines[0] == "header1\theader2"
    assert lines[2] == "newval1\tnewval2"


def test_append_row_unicode(tmp_path):
    """append_row handles unicode values correctly."""
    f = tmp_path / "unicode.tsv"
    append_row(f, ["日本語", "中文", "한국어"])
    line = f.read_text(encoding="utf-8").strip()
    assert line == "日本語\t中文\t한국어"
