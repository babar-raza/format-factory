"""
tests/python/dogfood/test_dogfood_qoi_xcf_gnumeric_remaining_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-53
Dogfood export: QOI + XCF + Gnumeric remaining uncovered analytics -> NDJSON -> verify.
QOI uses: qoi_area, qoi_channel_range, qoi_diagonal, qoi_has_any_black,
          qoi_has_any_white, qoi_max_channel_average, qoi_min_channel_average,
          qoi_min_dimension.
XCF uses: xcf_canvas_area, xcf_has_multiple_layers, xcf_max_dimension,
          xcf_max_layer_dimension, xcf_min_dimension, xcf_min_layer_dimension.
Gnumeric uses: gnumeric_avg_row_count, gnumeric_nonempty_density.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    qoi_area, qoi_channel_range, qoi_diagonal, qoi_has_any_black,
    qoi_has_any_white, qoi_max_channel_average, qoi_min_channel_average,
    qoi_min_dimension,
)
from xcf.xcf_parser import (
    xcf_canvas_area, xcf_has_multiple_layers, xcf_max_dimension,
    xcf_max_layer_dimension, xcf_min_dimension, xcf_min_layer_dimension,
)
from gnumeric.gnumeric_codec import gnumeric_avg_row_count, gnumeric_nonempty_density
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _valid_qoi_files():
    return sorted(_QOI_DIR.glob("*.qoi"))


def _valid_xcf_files():
    return sorted(_XCF_DIR.glob("*.xcf"))


def _valid_gnumeric_files():
    return sorted(_GNUMERIC_DIR.glob("*.gnumeric"))


class TestQoiXcfGnumericRemainingAnalyticsNdjsonExport:
    """QOI + XCF + Gnumeric remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_qoi_remaining_basics(self):
        s1 = str(_QOI_DIR / "1x1-red.qoi")
        s2 = str(_QOI_DIR / "2x2-black.qoi")
        assert qoi_area(s1) == 1
        assert qoi_channel_range(s1) == 255.0
        assert qoi_has_any_black(s1) is False
        assert qoi_has_any_white(s1) is False
        assert qoi_max_channel_average(s1) == 255.0
        assert qoi_min_channel_average(s1) == 0.0
        assert qoi_min_dimension(s1) == 1
        assert qoi_area(s2) == 4
        assert qoi_channel_range(s2) == 0.0
        assert qoi_has_any_black(s2) is True

    def test_xcf_remaining_basics(self):
        s1 = str(_XCF_DIR / "1x1-red-rgb.xcf")
        s3 = str(_XCF_DIR / "2x2-gray.xcf")
        assert xcf_canvas_area(s1) == 1
        assert xcf_has_multiple_layers(s1) is False
        assert xcf_max_dimension(s1) == 1
        assert xcf_max_layer_dimension(s1) == 1
        assert xcf_min_dimension(s1) == 1
        assert xcf_min_layer_dimension(s1) == 1
        assert xcf_canvas_area(s3) == 4
        assert xcf_max_dimension(s3) == 2
        assert xcf_min_dimension(s3) == 2

    def test_gnumeric_remaining_basics(self):
        s_empty = str(_GNUMERIC_DIR / "empty-sheet.gnumeric")
        s_minimal = str(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        assert gnumeric_avg_row_count(s_empty) == 0.0
        assert gnumeric_nonempty_density(s_empty) == 0.0
        assert isinstance(gnumeric_avg_row_count(s_minimal), float)
        assert gnumeric_nonempty_density(s_minimal) == 1.0

    def test_qoi_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = str(f)
            records.append({
                "file": f.name,
                "area": qoi_area(path),
                "channel_range": qoi_channel_range(path),
                "diagonal": round(qoi_diagonal(path), 4),
                "has_any_black": qoi_has_any_black(path),
                "has_any_white": qoi_has_any_white(path),
                "max_channel_average": qoi_max_channel_average(path),
                "min_channel_average": qoi_min_channel_average(path),
                "min_dimension": qoi_min_dimension(path),
                "source_format": "qoi",
            })
        dest = tmp_path / "qoi-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 3

    def test_xcf_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = str(f)
            records.append({
                "file": f.name,
                "canvas_area": xcf_canvas_area(path),
                "has_multiple_layers": xcf_has_multiple_layers(path),
                "max_dimension": xcf_max_dimension(path),
                "max_layer_dimension": xcf_max_layer_dimension(path),
                "min_dimension": xcf_min_dimension(path),
                "min_layer_dimension": xcf_min_layer_dimension(path),
                "source_format": "xcf",
            })
        dest = tmp_path / "xcf-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 3

    def test_gnumeric_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_gnumeric_files():
            path = str(f)
            records.append({
                "file": f.name,
                "avg_row_count": gnumeric_avg_row_count(path),
                "nonempty_density": gnumeric_nonempty_density(path),
                "source_format": "gnumeric",
            })
        dest = tmp_path / "gnumeric-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_qoi_files():
            path = str(f)
            records.append({
                "file": f.name,
                "area": qoi_area(path),
                "has_any_black": qoi_has_any_black(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["area"] == back["area"]
            assert orig["has_any_black"] == back["has_any_black"]

    def test_json_lines_valid(self, tmp_path):
        s_qoi = str(_QOI_DIR / "1x1-red.qoi")
        s_xcf = str(_XCF_DIR / "1x1-red-rgb.xcf")
        s_gnu = str(_GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
        records = [
            {"file": "1x1-red.qoi", "area": qoi_area(s_qoi), "format": "qoi"},
            {"file": "1x1-red-rgb.xcf", "canvas_area": xcf_canvas_area(s_xcf), "format": "xcf"},
            {"file": "minimal-spreadsheet.gnumeric", "nonempty_density": gnumeric_nonempty_density(s_gnu), "format": "gnumeric"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
