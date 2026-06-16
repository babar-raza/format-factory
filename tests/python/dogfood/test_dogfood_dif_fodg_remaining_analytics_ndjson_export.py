"""
tests/python/dogfood/test_dogfood_dif_fodg_remaining_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-55
Dogfood export: DIF + FODG remaining uncovered analytics -> NDJSON -> verify.
DIF uses: dif_all_numeric_column, dif_avg_cell_length, dif_data_density,
          dif_is_rectangular, dif_is_single_column, dif_max_string_length.
FODG uses: fodg_max_text_per_page, fodg_shape_to_page_variance.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_all_numeric_column, dif_avg_cell_length, dif_data_density,
    dif_is_rectangular, dif_is_single_column, dif_max_string_length,
)
from fodg.fodg_codec import fodg_max_text_per_page, fodg_shape_to_page_variance
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


class TestDifFodgRemainingAnalyticsNdjsonExport:
    """DIF + FODG remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_dif_remaining_basics(self):
        s_min = str(_DIF_DIR / "minimal-2x2.dif")
        s_num = str(_DIF_DIR / "numeric-row.dif")
        s_single = str(_DIF_DIR / "single-cell.dif")
        assert dif_avg_cell_length(s_min) == 4.5
        assert dif_data_density(s_min) == 1.0
        assert dif_is_rectangular(s_min) is True
        assert dif_is_single_column(s_min) is False
        assert dif_max_string_length(s_min) == 7
        assert dif_all_numeric_column(s_min, 0) is False
        assert dif_all_numeric_column(s_num, 0) is True
        assert dif_avg_cell_length(s_num) == 3.0
        assert dif_is_single_column(s_num) is False
        assert dif_is_single_column(s_single) is True
        assert dif_all_numeric_column(s_single, 0) is True

    def test_fodg_remaining_basics(self):
        s_empty = str(_FODG_DIR / "empty-page.fodg")
        s_minimal = str(_FODG_DIR / "minimal-drawing.fodg")
        s_shapes = str(_FODG_DIR / "shapes-basic.fodg")
        assert fodg_max_text_per_page(s_empty) == 0
        assert fodg_shape_to_page_variance(s_empty) == 0.0
        assert fodg_max_text_per_page(s_minimal) == 9
        assert fodg_max_text_per_page(s_shapes) == 11

    def test_dif_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            records.append({
                "file": f.name,
                "avg_cell_length": dif_avg_cell_length(path),
                "data_density": dif_data_density(path),
                "is_rectangular": dif_is_rectangular(path),
                "is_single_column": dif_is_single_column(path),
                "max_string_length": dif_max_string_length(path),
                "all_numeric_col0": dif_all_numeric_column(path, 0),
                "source_format": "dif",
            })
        dest = tmp_path / "dif-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 3

    def test_fodg_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodg_files():
            path = str(f)
            max_text = fodg_max_text_per_page(path)
            variance = fodg_shape_to_page_variance(path)
            assert isinstance(max_text, (int, float)), f"max_text_per_page must be numeric for {f.name}"
            assert isinstance(variance, float), f"shape_to_page_variance must be float for {f.name}"
            records.append({
                "file": f.name,
                "max_text_per_page": max_text,
                "shape_to_page_variance": variance,
                "source_format": "fodg",
            })
        dest = tmp_path / "fodg-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_dif_files():
            path = str(f)
            records.append({
                "file": f.name,
                "data_density": dif_data_density(path),
                "is_rectangular": dif_is_rectangular(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["data_density"] == back["data_density"]
            assert orig["is_rectangular"] == back["is_rectangular"]

    def test_json_lines_valid(self, tmp_path):
        s_dif = str(_DIF_DIR / "minimal-2x2.dif")
        s_fodg = str(_FODG_DIR / "shapes-basic.fodg")
        records = [
            {"file": "minimal-2x2.dif", "data_density": dif_data_density(s_dif), "format": "dif"},
            {"file": "shapes-basic.fodg", "max_text_per_page": fodg_max_text_per_page(s_fodg), "format": "fodg"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
