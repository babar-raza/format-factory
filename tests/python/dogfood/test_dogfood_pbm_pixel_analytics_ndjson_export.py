"""
tests/python/dogfood/test_dogfood_pbm_pixel_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-50
Dogfood export: PBM parse -> pixel analytics -> write as NDJSON -> verify.
Uses: pbm_all_black, pbm_all_white, pbm_white_pixel_count, pbm_dimensions,
pbm_total_pixel_count, pbm_black_pixel_ratio.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import (
    pbm_all_black,
    pbm_all_white,
    pbm_white_pixel_count,
    pbm_dimensions,
    pbm_total_pixel_count,
    pbm_black_pixel_ratio,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


def _valid_pbm_files():
    return sorted(_PBM_DIR.glob("*.pbm"))


class TestPbmPixelAnalyticsNdjsonExport:
    """PBM -> pixel analytics -> NDJSON export -> roundtrip verification."""

    def test_all_black_and_all_white(self):
        sample = str(next(_PBM_DIR.glob("*.pbm")))
        all_black = pbm_all_black(sample)
        all_white = pbm_all_white(sample)
        assert isinstance(all_black, bool)
        assert isinstance(all_white, bool)

    def test_white_pixel_count_and_dims(self):
        sample = str(next(_PBM_DIR.glob("*.pbm")))
        white_count = pbm_white_pixel_count(sample)
        dims = pbm_dimensions(sample)
        total = pbm_total_pixel_count(sample)
        ratio = pbm_black_pixel_ratio(sample)
        assert white_count >= 0
        assert isinstance(dims, dict)
        assert total >= 0
        assert 0.0 <= ratio <= 1.0

    def test_pixel_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            all_black = pbm_all_black(path)
            all_white = pbm_all_white(path)
            white_count = pbm_white_pixel_count(path)
            dims = pbm_dimensions(path)
            total = pbm_total_pixel_count(path)
            ratio = pbm_black_pixel_ratio(path)
            assert isinstance(all_black, bool), f"all_black must be bool for {f.name}"
            assert isinstance(all_white, bool), f"all_white must be bool for {f.name}"
            assert white_count >= 0, f"white_pixel_count must be >= 0 for {f.name}"
            assert isinstance(dims, dict), f"dimensions must be dict for {f.name}"
            assert total >= 0, f"total_pixel_count must be >= 0 for {f.name}"
            assert 0.0 <= ratio <= 1.0, f"black_pixel_ratio must be in [0,1] for {f.name}"
            records.append({
                "file": f.name,
                "all_black": all_black,
                "all_white": all_white,
                "white_pixel_count": white_count,
                "width": dims.get("width", 0),
                "height": dims.get("height", 0),
                "total_pixel_count": total,
                "black_pixel_ratio": ratio,
                "source_format": "pbm",
            })
        dest = tmp_path / "pbm-pixel-analytics.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            records.append({
                "file": f.name,
                "white_pixel_count": pbm_white_pixel_count(path),
                "total_pixel_count": pbm_total_pixel_count(path),
                "black_pixel_ratio": pbm_black_pixel_ratio(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["white_pixel_count"] == back["white_pixel_count"]
            assert orig["total_pixel_count"] == back["total_pixel_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_PBM_DIR.glob("*.pbm")))
        records = [{"file": "sample.pbm", "all_black": pbm_all_black(sample), "all_white": pbm_all_white(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_black_white_export(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            all_black = pbm_all_black(path)
            all_white = pbm_all_white(path)
            white_count = pbm_white_pixel_count(path)
            assert isinstance(all_black, bool)
            assert isinstance(all_white, bool)
            assert white_count >= 0
            records.append({
                "file": f.name,
                "all_black": all_black,
                "all_white": all_white,
                "white_pixel_count": white_count,
                "format": "pbm",
            })
        dest = tmp_path / "black-white.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "pbm" for r in loaded)
        assert all(r["white_pixel_count"] >= 0 for r in loaded)
