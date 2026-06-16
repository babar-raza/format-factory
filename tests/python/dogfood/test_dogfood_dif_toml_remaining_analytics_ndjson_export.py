"""
tests/python/dogfood/test_dogfood_dif_toml_remaining_analytics_ndjson_export.py

Dogfood export: DIF remaining (min_cell_length, has_string_cells, max_numeric_value,
min_numeric_value) + TOML remaining (table_count, total_keys, has_tables, has_lists,
is_empty, string_density) -> NDJSON -> verify.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_min_cell_length,
    dif_has_string_cells,
    dif_max_numeric_value,
    dif_min_numeric_value,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

# Load TOML codec via importlib (stdlib 'toml' conflict)
_toml_spec = importlib.util.spec_from_file_location(
    "toml_codec", str(_REPO / "src" / "python" / "toml" / "toml_codec.py")
)
_toml = importlib.util.module_from_spec(_toml_spec)
_toml_spec.loader.exec_module(_toml)
toml_table_count = _toml.toml_table_count
toml_total_keys = _toml.toml_total_keys
toml_has_tables = _toml.toml_has_tables
toml_has_lists = _toml.toml_has_lists
toml_is_empty = _toml.toml_is_empty
toml_string_density = _toml.toml_string_density

_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"

# Inline TOML byte samples
_TOML_SECTIONS = b"[section]\nkey1 = \"val\"\nkey2 = 42\n[section.sub]\nnested = true\n"
_TOML_STRINGS = b"key1 = \"hello\"\nkey2 = \"world\"\n"
_TOML_MIXED = b"a = 1\nb = 2.0\nc = \"three\"\n"
_TOML_LISTS = b"nums = [1, 2, 3]\n"
_TOML_EMPTY = b""


def test_dif_min_cell_length_and_string_cells(tmp_path):
    path_2x2 = str(_DIF / "minimal-2x2.dif")
    path_num = str(_DIF / "numeric-row.dif")
    assert dif_min_cell_length(path_2x2) == 1
    assert dif_has_string_cells(path_2x2) is True
    assert dif_has_string_cells(path_num) is False
    records = [
        {"file": "minimal-2x2.dif", "dif_min_cell_length": 1, "dif_has_string_cells": True},
        {"file": "numeric-row.dif", "dif_has_string_cells": False},
    ]
    out = tmp_path / "dif_remaining.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["dif_min_cell_length"] == 1
    assert rows[0]["dif_has_string_cells"] is True
    assert rows[1]["dif_has_string_cells"] is False


def test_dif_max_min_numeric_value(tmp_path):
    path_num = str(_DIF / "numeric-row.dif")
    assert dif_max_numeric_value(path_num) == 3.0
    assert dif_min_numeric_value(path_num) == 1.0
    records = [
        {"file": "numeric-row.dif", "dif_max_numeric_value": 3.0, "dif_min_numeric_value": 1.0},
    ]
    out = tmp_path / "dif_numeric.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["dif_max_numeric_value"] == 3.0
    assert rows[0]["dif_min_numeric_value"] == 1.0


def test_toml_table_count_and_total_keys(tmp_path):
    assert toml_table_count(_TOML_SECTIONS) == 1
    assert toml_total_keys(_TOML_SECTIONS) == 1
    records = [
        {"toml_table_count": 1, "toml_total_keys": 1},
    ]
    out = tmp_path / "toml_tables.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["toml_table_count"] == 1
    assert rows[0]["toml_total_keys"] == 1


def test_toml_has_tables_and_lists(tmp_path):
    assert toml_has_tables(_TOML_SECTIONS) is True
    assert toml_has_tables(_TOML_STRINGS) is False
    assert toml_has_lists(_TOML_LISTS) is True
    assert toml_has_lists(_TOML_SECTIONS) is False
    records = [
        {"sample": "sections", "has_tables": True, "has_lists": False},
        {"sample": "strings", "has_tables": False},
        {"sample": "lists", "has_lists": True},
    ]
    out = tmp_path / "toml_bool.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["has_tables"] is True
    assert rows[2]["has_lists"] is True


def test_toml_is_empty_and_string_density(tmp_path):
    assert toml_is_empty(_TOML_EMPTY) is True
    assert toml_is_empty(_TOML_SECTIONS) is False
    assert toml_string_density(_TOML_STRINGS) == 1.0
    assert round(toml_string_density(_TOML_MIXED), 4) == round(1 / 3, 4)
    records = [
        {"sample": "empty", "toml_is_empty": True, "toml_string_density": None},
        {"sample": "strings", "toml_is_empty": False, "toml_string_density": 1.0},
        {"sample": "mixed", "toml_is_empty": False, "toml_string_density": toml_string_density(_TOML_MIXED)},
    ]
    out = tmp_path / "toml_density.ndjson"
    write_ndjson(records, str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["toml_is_empty"] is True
    assert rows[1]["toml_string_density"] == 1.0
