"""
tests/python/dogfood/test_dogfood_xcf_tsv_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-79
Dogfood export: XCF + TSV remaining analytics -> write as NDJSON -> verify.
XCF uses: xcf_total_layer_pixels, xcf_is_single_layer.
TSV uses: tsv_max_numeric_value, tsv_has_empty_rows, tsv_is_rectangular, tsv_empty_cell_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import xcf_total_layer_pixels, xcf_is_single_layer
from tsv import tsv_max_numeric_value, tsv_has_empty_rows, tsv_is_rectangular, tsv_empty_cell_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _valid_xcf_files():
    return sorted(_XCF_DIR.glob("*.xcf"))


def _valid_tsv_files():
    return sorted(_TSV_DIR.glob("*.tsv"))


class TestXcfTsvRemainingAnalyticsNdjsonExport:
    """XCF + TSV remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_xcf_remaining_basics(self):
        sample = str(next(_XCF_DIR.glob("*.xcf")))
        total_pixels = xcf_total_layer_pixels(sample)
        is_single = xcf_is_single_layer(sample)
        assert total_pixels >= 0
        assert isinstance(is_single, bool)

    def test_tsv_remaining_basics(self):
        sample = str(next(_TSV_DIR.glob("*.tsv")))
        max_num = tsv_max_numeric_value(sample)
        has_empty = tsv_has_empty_rows(sample)
        is_rect = tsv_is_rectangular(sample)
        empty_cells = tsv_empty_cell_count(sample)
        assert max_num is None or isinstance(max_num, (int, float))
        assert isinstance(has_empty, bool)
        assert isinstance(is_rect, bool)
        assert empty_cells >= 0

    def test_xcf_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = str(f)
            total_pixels = xcf_total_layer_pixels(path)
            is_single = xcf_is_single_layer(path)
            assert total_pixels >= 0, f"xcf_total_layer_pixels must be >= 0 for {f.name}"
            assert isinstance(is_single, bool), f"xcf_is_single_layer must be bool for {f.name}"
            records.append({
                "file": f.name,
                "total_layer_pixels": total_pixels,
                "is_single_layer": is_single,
                "source_format": "xcf",
            })
        dest = tmp_path / "xcf-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_tsv_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_tsv_files():
            path = str(f)
            max_num = tsv_max_numeric_value(path)
            has_empty = tsv_has_empty_rows(path)
            is_rect = tsv_is_rectangular(path)
            empty_cells = tsv_empty_cell_count(path)
            assert max_num is None or isinstance(max_num, (int, float)), f"tsv_max_numeric_value must be numeric or None for {f.name}"
            assert isinstance(has_empty, bool), f"tsv_has_empty_rows must be bool for {f.name}"
            assert isinstance(is_rect, bool), f"tsv_is_rectangular must be bool for {f.name}"
            assert empty_cells >= 0, f"tsv_empty_cell_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "max_numeric_value": float(max_num) if max_num is not None else 0.0,
                "has_empty_rows": has_empty,
                "is_rectangular": is_rect,
                "empty_cell_count": empty_cells,
                "source_format": "tsv",
            })
        dest = tmp_path / "tsv-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_xcf_files():
            path = str(f)
            total_pixels = xcf_total_layer_pixels(path)
            is_single = xcf_is_single_layer(path)
            records.append({
                "file": f.name,
                "total_layer_pixels": total_pixels,
                "is_single_layer": is_single,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_layer_pixels"] == back["total_layer_pixels"]
            assert orig["is_single_layer"] == back["is_single_layer"]

    def test_json_lines_valid(self, tmp_path):
        xcf_sample = str(next(_XCF_DIR.glob("*.xcf")))
        tsv_sample = str(next(_TSV_DIR.glob("*.tsv")))
        total_pixels = xcf_total_layer_pixels(xcf_sample)
        is_rect = tsv_is_rectangular(tsv_sample)
        records = [
            {"file": "sample.xcf", "total_layer_pixels": total_pixels, "format": "xcf"},
            {"file": "sample.tsv", "is_rectangular": is_rect, "format": "tsv"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
