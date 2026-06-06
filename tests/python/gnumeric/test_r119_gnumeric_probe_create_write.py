"""
Tests for probe_gnumeric, create_gnumeric, write_gnumeric.

Sprint: FORMAT-FACTORY-AUTONOMOUS-FILE-FORMAT-ACQUISITION-MEGA-TRAIN-001
Tasks: h8-probe-gnumeric-001, h9-gnumeric-create-001, h9-gnumeric-write-001

Run from repo root (with PYTHONPATH set):
    python -m pytest tests/python/gnumeric/test_r119_gnumeric_probe_create_write.py -v
"""

from __future__ import annotations

import gzip
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "gnumeric"

from gnumeric.gnumeric_codec import (
    GnumericError,
    load,
    probe_gnumeric,
    create_gnumeric,
    write_gnumeric,
)
import gnumeric as gnumeric_pkg


# ---------------------------------------------------------------------------
# 1. probe_gnumeric — importable and exported
# ---------------------------------------------------------------------------

def test_probe_gnumeric_importable():
    from gnumeric.gnumeric_codec import probe_gnumeric as p
    assert callable(p)


def test_probe_gnumeric_in_init():
    assert hasattr(gnumeric_pkg, "probe_gnumeric")


def test_probe_gnumeric_in_all():
    assert "probe_gnumeric" in gnumeric_pkg.__all__


# ---------------------------------------------------------------------------
# 2. probe_gnumeric — valid inputs
# ---------------------------------------------------------------------------

def test_probe_gnumeric_valid_file():
    sample = SAMPLES_DIR / "minimal-spreadsheet.gnumeric"
    if not sample.exists():
        pytest.skip("sample file not found")
    assert probe_gnumeric(sample) is True


def test_probe_gnumeric_valid_path_str():
    sample = SAMPLES_DIR / "minimal-spreadsheet.gnumeric"
    if not sample.exists():
        pytest.skip("sample file not found")
    assert probe_gnumeric(str(sample)) is True


def test_probe_gnumeric_valid_bytes(tmp_path):
    model = create_gnumeric([{"name": "S1", "rows": [["a", "b"]]}])
    out = tmp_path / "t.gnumeric"
    write_gnumeric(model, out)
    assert probe_gnumeric(out.read_bytes()) is True


def test_probe_gnumeric_roundtrip_create_write(tmp_path):
    model = create_gnumeric([{"name": "Sheet1", "rows": [["x", "y"], ["1", "2"]]}])
    out = tmp_path / "rt.gnumeric"
    write_gnumeric(model, out)
    assert probe_gnumeric(out) is True


# ---------------------------------------------------------------------------
# 3. probe_gnumeric — invalid inputs
# ---------------------------------------------------------------------------

def test_probe_gnumeric_rejects_json_bytes():
    assert probe_gnumeric(b'{"not": "gnumeric"}') is False


def test_probe_gnumeric_rejects_plain_xml():
    xml = b'<?xml version="1.0"?><root><child>text</child></root>'
    assert probe_gnumeric(xml) is False


def test_probe_gnumeric_rejects_empty_bytes():
    assert probe_gnumeric(b"") is False


def test_probe_gnumeric_rejects_abw_bytes():
    abw = b'<?xml version="1.0"?><abiword template="false" version="1.0"><section><p>hi</p></section></abiword>'
    assert probe_gnumeric(abw) is False


def test_probe_gnumeric_rejects_nonexistent(tmp_path):
    assert probe_gnumeric(tmp_path / "does_not_exist.gnumeric") is False


def test_probe_gnumeric_returns_bool_true(tmp_path):
    model = create_gnumeric([{"name": "S", "rows": [["v"]]}])
    out = tmp_path / "b.gnumeric"
    write_gnumeric(model, out)
    result = probe_gnumeric(out)
    assert isinstance(result, bool)
    assert result is True


def test_probe_gnumeric_returns_bool_false():
    result = probe_gnumeric(b"not-gnumeric")
    assert isinstance(result, bool)
    assert result is False


def test_probe_gnumeric_does_not_mutate_file(tmp_path):
    model = create_gnumeric([{"name": "S", "rows": [["v"]]}])
    out = tmp_path / "m.gnumeric"
    write_gnumeric(model, out)
    before = out.read_bytes()
    probe_gnumeric(out)
    after = out.read_bytes()
    assert before == after


# ---------------------------------------------------------------------------
# 4. create_gnumeric — basic model structure
# ---------------------------------------------------------------------------

def test_create_gnumeric_importable():
    from gnumeric.gnumeric_codec import create_gnumeric as c
    assert callable(c)


def test_create_gnumeric_in_init():
    assert hasattr(gnumeric_pkg, "create_gnumeric")


def test_create_gnumeric_in_all():
    assert "create_gnumeric" in gnumeric_pkg.__all__


def test_create_gnumeric_is_gnumeric_flag():
    model = create_gnumeric([])
    assert model["is_gnumeric"] is True


def test_create_gnumeric_empty_sheets():
    model = create_gnumeric([])
    assert model["sheet_count"] == 0
    assert model["sheets"] == []
    assert model["cell_count"] == 0


def test_create_gnumeric_single_sheet():
    model = create_gnumeric([{"name": "Data", "rows": [["A", "B"], ["1", "2"]]}])
    assert model["sheet_count"] == 1
    assert model["sheets"][0]["name"] == "Data"
    assert model["cell_count"] == 4


def test_create_gnumeric_multi_sheet():
    model = create_gnumeric([
        {"name": "S1", "rows": [["x"]]},
        {"name": "S2", "rows": [["y"], ["z"]]},
    ])
    assert model["sheet_count"] == 2
    assert model["cell_count"] == 3


def test_create_gnumeric_default_sheet_name():
    model = create_gnumeric([{"rows": [["v"]]}])
    assert model["sheets"][0]["name"] == "Sheet1"


def test_create_gnumeric_cell_grid_contains_values():
    model = create_gnumeric([{"name": "S", "rows": [["hello", "world"]]}])
    grid = model["sheets"][0]["cell_grid"]
    assert grid[(0, 0)] == "hello"
    assert grid[(0, 1)] == "world"


def test_create_gnumeric_cell_values_list():
    model = create_gnumeric([{"name": "S", "rows": [["a", "b"], ["c", ""]]}])
    cv = model["sheets"][0]["cell_values"]
    assert "a" in cv
    assert "b" in cv
    assert "c" in cv


def test_create_gnumeric_none_cell_becomes_empty():
    model = create_gnumeric([{"name": "S", "rows": [[None, "x"]]}])
    grid = model["sheets"][0]["cell_grid"]
    assert grid[(0, 0)] == ""
    assert grid[(0, 1)] == "x"


# ---------------------------------------------------------------------------
# 5. write_gnumeric — serialization
# ---------------------------------------------------------------------------

def test_write_gnumeric_importable():
    from gnumeric.gnumeric_codec import write_gnumeric as w
    assert callable(w)


def test_write_gnumeric_in_init():
    assert hasattr(gnumeric_pkg, "write_gnumeric")


def test_write_gnumeric_in_all():
    assert "write_gnumeric" in gnumeric_pkg.__all__


def test_write_gnumeric_creates_file(tmp_path):
    model = create_gnumeric([{"name": "S", "rows": [["v"]]}])
    out = tmp_path / "out.gnumeric"
    write_gnumeric(model, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_write_gnumeric_file_is_gzip(tmp_path):
    model = create_gnumeric([{"name": "S", "rows": [["v"]]}])
    out = tmp_path / "out.gnumeric"
    write_gnumeric(model, out)
    data = out.read_bytes()
    assert data[:2] == b"\x1f\x8b"


def test_write_gnumeric_contains_gnumeric_namespace(tmp_path):
    model = create_gnumeric([{"name": "S", "rows": [["v"]]}])
    out = tmp_path / "out.gnumeric"
    write_gnumeric(model, out)
    xml = gzip.decompress(out.read_bytes()).decode("utf-8")
    assert "gnumeric.org" in xml


def test_write_gnumeric_accepts_path_str(tmp_path):
    model = create_gnumeric([{"name": "S", "rows": [["v"]]}])
    out = tmp_path / "out.gnumeric"
    write_gnumeric(model, str(out))
    assert out.exists()


def test_write_gnumeric_invalid_model_raises():
    with pytest.raises(GnumericError):
        write_gnumeric({"is_gnumeric": False}, "/tmp/bad.gnumeric")


def test_write_gnumeric_non_dict_model_raises():
    with pytest.raises(GnumericError):
        write_gnumeric("not a dict", "/tmp/bad.gnumeric")


# ---------------------------------------------------------------------------
# 6. Roundtrip: create → write → load
# ---------------------------------------------------------------------------

def test_roundtrip_sheet_count(tmp_path):
    model = create_gnumeric([
        {"name": "Alpha", "rows": [["a", "b"]]},
        {"name": "Beta", "rows": [["x"]]},
    ])
    out = tmp_path / "rt.gnumeric"
    write_gnumeric(model, out)
    loaded = load(out)
    assert loaded["sheet_count"] == 2


def test_roundtrip_cell_values_preserved(tmp_path):
    rows = [["Name", "Score"], ["Alice", "95"], ["Bob", "87"]]
    model = create_gnumeric([{"name": "Results", "rows": rows}])
    out = tmp_path / "results.gnumeric"
    write_gnumeric(model, out)
    loaded = load(out)
    assert loaded["sheets"][0]["name"] == "Results"
    values = loaded["sheets"][0]["cell_values"]
    assert "Alice" in values
    assert "95" in values


def test_roundtrip_probe_passes(tmp_path):
    model = create_gnumeric([{"name": "S", "rows": [["data"]]}])
    out = tmp_path / "probe.gnumeric"
    write_gnumeric(model, out)
    assert probe_gnumeric(out) is True


def test_roundtrip_cell_count_matches(tmp_path):
    rows = [["a", "b", "c"], ["d", "e", "f"]]
    model = create_gnumeric([{"name": "S", "rows": rows}])
    out = tmp_path / "count.gnumeric"
    write_gnumeric(model, out)
    loaded = load(out)
    # 6 non-empty cells
    assert loaded["cell_count"] == 6
