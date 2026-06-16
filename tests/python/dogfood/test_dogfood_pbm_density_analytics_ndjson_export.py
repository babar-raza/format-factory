"""
tests/python/dogfood/test_dogfood_pbm_density_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-33
Dogfood export: PBM parse -> density/aspect analytics -> write as NDJSON -> verify.
Uses deeper PBM analytics: white_pixel_ratio, aspect_ratio, white_density,
row_black_counts, column_black_counts, total_pixel_count, is_binary.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import (
    pbm_white_pixel_ratio,
    pbm_aspect_ratio,
    pbm_white_density,
    pbm_row_black_counts,
    pbm_column_black_counts,
    pbm_total_pixel_count,
    pbm_is_binary,
    pbm_black_pixel_ratio,
    pbm_dimensions,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_pbm_files():
    return sorted(_PBM_DIR.glob("*.pbm"))


class TestPbmDensityAnalyticsNdjsonExport:
    """PBM -> density/aspect analytics -> NDJSON export -> roundtrip verification."""

    def test_density_ratios(self):
        sample = _ap(_PBM_DIR / "2x2-checker.pbm")
        wpr = pbm_white_pixel_ratio(sample)
        bpr = pbm_black_pixel_ratio(sample)
        wd = pbm_white_density(sample)
        assert 0.0 <= wpr <= 1.0
        assert 0.0 <= bpr <= 1.0
        assert 0.0 <= wd <= 1.0

    def test_aspect_and_binary(self):
        sample = _ap(_PBM_DIR / "2x2-checker.pbm")
        ar = pbm_aspect_ratio(sample)
        is_bin = pbm_is_binary(sample)
        total = pbm_total_pixel_count(sample)
        assert ar > 0.0
        assert isinstance(is_bin, bool)
        assert total >= 1

    def test_density_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = _ap(f)
            wpr = pbm_white_pixel_ratio(path)
            bpr = pbm_black_pixel_ratio(path)
            wd = pbm_white_density(path)
            ar = pbm_aspect_ratio(path)
            total = pbm_total_pixel_count(path)
            row_counts = pbm_row_black_counts(path)
            col_counts = pbm_column_black_counts(path)
            dims = pbm_dimensions(path)
            assert 0.0 <= wpr <= 1.0, f"white_pixel_ratio out of range for {f.name}"
            assert 0.0 <= bpr <= 1.0, f"black_pixel_ratio out of range for {f.name}"
            assert 0.0 <= wd <= 1.0, f"white_density out of range for {f.name}"
            assert ar > 0.0, f"aspect_ratio must be > 0 for {f.name}"
            assert total >= 1, f"total_pixel_count must be >= 1 for {f.name}"
            assert isinstance(row_counts, list), f"row_black_counts must be list for {f.name}"
            assert isinstance(col_counts, list), f"column_black_counts must be list for {f.name}"
            records.append({
                "file": f.name,
                "white_pixel_ratio": wpr,
                "black_pixel_ratio": bpr,
                "white_density": wd,
                "aspect_ratio": ar,
                "total_pixels": total,
                "row_count": len(row_counts),
                "col_count": len(col_counts),
                "width": dims.get("width", dims[0] if isinstance(dims, (list, tuple)) else 0),
                "source_format": "pbm",
            })
        dest = tmp_path / "pbm-density.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "white_pixel_ratio": pbm_white_pixel_ratio(path),
                "total_pixels": pbm_total_pixel_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["total_pixels"] == back["total_pixels"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_PBM_DIR / "2x2-checker.pbm")
        records = [{"file": "2x2-checker.pbm", "white_density": pbm_white_density(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_aspect_ratio_export(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = _ap(f)
            ar = pbm_aspect_ratio(path)
            wpr = pbm_white_pixel_ratio(path)
            assert ar > 0.0, f"aspect_ratio must be > 0 for {f.name}"
            assert 0.0 <= wpr <= 1.0, f"white_pixel_ratio out of range for {f.name}"
            records.append({
                "file": f.name,
                "aspect_ratio": ar,
                "white_pixel_ratio": wpr,
                "format": "pbm",
            })
        dest = tmp_path / "aspect.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "pbm" for r in loaded)
        assert all(r["aspect_ratio"] > 0.0 for r in loaded)
