"""
tests/python/dogfood/test_dogfood_pgm_stats_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-18
Dogfood export: PGM parse -> extract grayscale stats -> write as NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm import (
    parse_pgm,
    get_dimensions,
    pixel_count,
    average_gray,
    pgm_max_pixel_value,
    pgm_min_pixel_value,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestPgmStatsNdjsonExport:
    """PGM -> grayscale stats extraction -> NDJSON export -> roundtrip verification."""

    def test_parse_pgm_sample(self):
        sample = str(_PGM_DIR / "1x1-white.pgm")
        img = parse_pgm(sample)
        assert isinstance(img, dict)

    def test_extract_dimensions(self):
        sample = str(_PGM_DIR / "2x2-gradient.pgm")
        dims = get_dimensions(sample)
        assert dims[0] >= 1
        assert dims[1] >= 1

    def test_gray_stats_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_PGM_DIR.glob("*.pgm")):
            dims = get_dimensions(str(f))
            records.append({
                "file": f.name,
                "width": dims[0],
                "height": dims[1],
                "pixels": pixel_count(str(f)),
                "avg_gray": average_gray(str(f)),
                "max_value": pgm_max_pixel_value(str(f)),
                "min_value": pgm_min_pixel_value(str(f)),
                "source_format": "pgm",
            })
        dest = tmp_path / "pgm-stats.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_PGM_DIR.glob("*.pgm")):
            records.append({
                "file": f.name,
                "pixels": pixel_count(str(f)),
                "avg_gray": average_gray(str(f)),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["pixels"] == back["pixels"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_PGM_DIR / "1x1-white.pgm")
        records = [{"file": "1x1-white.pgm", "pixels": pixel_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_contrast_range_in_export(self, tmp_path):
        records = []
        for f in sorted(_PGM_DIR.glob("*.pgm")):
            max_v = pgm_max_pixel_value(str(f))
            min_v = pgm_min_pixel_value(str(f))
            records.append({
                "file": f.name,
                "contrast_range": max_v - min_v,
                "format": "pgm",
            })
        dest = tmp_path / "contrast.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "pgm" for r in loaded)
