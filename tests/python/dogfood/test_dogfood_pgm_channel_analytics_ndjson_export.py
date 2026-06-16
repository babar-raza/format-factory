"""
tests/python/dogfood/test_dogfood_pgm_channel_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-32
Dogfood export: PGM parse -> grayscale depth analytics -> write as NDJSON -> verify.
Uses deeper PGM analytics: contrast_range, dynamic_range, bright_pixel_ratio,
nonzero_pixel_ratio, median_pixel_value, pixel_sum.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import (
    pgm_contrast_range,
    pgm_dynamic_range,
    pgm_bright_pixel_ratio,
    pgm_nonzero_pixel_ratio,
    pgm_median_pixel_value,
    pgm_pixel_sum,
    pgm_total_pixel_count,
    pgm_average_brightness,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_pgm_files():
    return sorted(_PGM_DIR.glob("*.pgm"))


class TestPgmChannelAnalyticsNdjsonExport:
    """PGM -> grayscale depth analytics -> NDJSON export -> roundtrip verification."""

    def test_contrast_range(self):
        sample = _ap(_PGM_DIR / "2x2-gradient.pgm")
        cr = pgm_contrast_range(sample)
        assert isinstance(cr, (int, float))
        assert cr >= 0

    def test_depth_metrics(self):
        sample = _ap(_PGM_DIR / "2x2-gradient.pgm")
        dr = pgm_dynamic_range(sample)
        bpr = pgm_bright_pixel_ratio(sample)
        npr = pgm_nonzero_pixel_ratio(sample)
        assert dr >= 0
        assert 0.0 <= bpr <= 1.0
        assert 0.0 <= npr <= 1.0

    def test_depth_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = _ap(f)
            cr = pgm_contrast_range(path)
            dr = pgm_dynamic_range(path)
            bpr = pgm_bright_pixel_ratio(path)
            npr = pgm_nonzero_pixel_ratio(path)
            med = pgm_median_pixel_value(path)
            psum = pgm_pixel_sum(path)
            total = pgm_total_pixel_count(path)
            assert total >= 1, f"total_pixels must be >= 1 for {f.name}"
            assert 0.0 <= bpr <= 1.0, f"bright_pixel_ratio out of range for {f.name}"
            assert 0.0 <= npr <= 1.0, f"nonzero_pixel_ratio out of range for {f.name}"
            assert psum >= 0, f"pixel_sum must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "contrast_range": cr,
                "dynamic_range": dr,
                "bright_pixel_ratio": bpr,
                "nonzero_pixel_ratio": npr,
                "median_pixel_value": med,
                "pixel_sum": psum,
                "total_pixels": total,
                "source_format": "pgm",
            })
        dest = tmp_path / "pgm-depth.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = _ap(f)
            records.append({
                "file": f.name,
                "dynamic_range": pgm_dynamic_range(path),
                "pixel_sum": pgm_pixel_sum(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["pixel_sum"] == back["pixel_sum"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_PGM_DIR / "2x2-gradient.pgm")
        records = [{"file": "2x2-gradient.pgm", "pixel_sum": pgm_pixel_sum(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_brightness_analytics_export(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = _ap(f)
            avg = pgm_average_brightness(path)
            med = pgm_median_pixel_value(path)
            assert avg >= 0.0, f"average_brightness must be >= 0 for {f.name}"
            assert med >= 0, f"median must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "average_brightness": avg,
                "median_pixel_value": med,
                "format": "pgm",
            })
        dest = tmp_path / "brightness.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "pgm" for r in loaded)
        assert all(r["average_brightness"] >= 0.0 for r in loaded)
