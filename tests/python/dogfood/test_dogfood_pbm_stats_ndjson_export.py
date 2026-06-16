"""
tests/python/dogfood/test_dogfood_pbm_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-13
Dogfood export: PBM parse -> extract pixel stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm import parse_pbm, get_dimensions, image_pixel_stats, black_pixel_ratio
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


class TestPbmStatsNdjsonExport:
    """PBM -> pixel stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_pbm_sample(self):
        sample = str(_PBM_DIR / "2x2-checker.pbm")
        img = parse_pbm(sample)
        assert isinstance(img, dict)

    def test_extract_pixel_stats(self):
        sample = str(_PBM_DIR / "2x2-checker.pbm")
        stats = image_pixel_stats(sample)
        assert stats["ok"] is True
        assert stats["total_pixels"] == 4

    def test_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_PBM_DIR.glob("*.pbm")):
            stats = image_pixel_stats(str(f))
            dims = get_dimensions(str(f))
            records.append({
                "file": f.name,
                "width": dims[0],
                "height": dims[1],
                "black_count": stats["black_count"],
                "white_count": stats["white_count"],
                "total_pixels": stats["total_pixels"],
                "source_format": "pbm",
            })
        dest = tmp_path / "pbm-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_PBM_DIR.glob("*.pbm")):
            stats = image_pixel_stats(str(f))
            records.append({
                "file": f.name,
                "black_count": stats["black_count"],
                "white_count": stats["white_count"],
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["black_count"] == back["black_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_PBM_DIR / "1x1-black.pbm")
        stats = image_pixel_stats(sample)
        records = [{"file": "1x1-black.pbm", "density": stats["black_density"]}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_black_ratio_in_export(self, tmp_path):
        records = []
        for f in sorted(_PBM_DIR.glob("*.pbm")):
            ratio = black_pixel_ratio(str(f))
            records.append({
                "file": f.name,
                "black_ratio": ratio,
                "format": "pbm",
            })
        dest = tmp_path / "ratio.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(0 <= r["black_ratio"] <= 1.0 for r in loaded)
