"""
tests/python/dogfood/test_dogfood_multiformat_pixel_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-33
Dogfood export: Cross-format PBM+PGM+PPM pixel analytics -> write as NDJSON -> verify.
Unified pixel inventory: total_pixels, aspect_ratio, format_family="image".
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import (
    pbm_total_pixel_count,
    pbm_aspect_ratio as pbm_ar,
    pbm_black_pixel_ratio,
)
from src.python.pgm.pgm_parser import (
    pgm_total_pixel_count,
    pgm_average_brightness,
    pgm_dynamic_range,
)
from src.python.ppm.ppm_parser import (
    ppm_pixel_count,
    ppm_aspect_ratio,
    ppm_saturation_estimate,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


class TestMultiformatPixelNdjsonExport:
    """PBM+PGM+PPM -> unified pixel analytics -> NDJSON export -> roundtrip."""

    def test_pbm_pixel_basics(self):
        sample = _ap(_PBM_DIR / "2x2-checker.pbm")
        total = pbm_total_pixel_count(sample)
        ar = pbm_ar(sample)
        assert total >= 1
        assert ar > 0.0

    def test_pgm_pixel_basics(self):
        sample = _ap(_PGM_DIR / "2x2-gradient.pgm")
        total = pgm_total_pixel_count(sample)
        avg = pgm_average_brightness(sample)
        assert total >= 1
        assert avg >= 0.0

    def test_pixel_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in sorted(_PBM_DIR.glob("*.pbm")):
            path = _ap(f)
            total = pbm_total_pixel_count(path)
            ar = pbm_ar(path)
            density = pbm_black_pixel_ratio(path)
            assert total >= 1
            assert ar > 0.0
            assert 0.0 <= density <= 1.0
            records.append({
                "file": f.name,
                "format": "pbm",
                "format_family": "image",
                "total_pixels": total,
                "aspect_ratio": ar,
                "primary_density": density,
            })
        for f in sorted(_PGM_DIR.glob("*.pgm")):
            path = _ap(f)
            total = pgm_total_pixel_count(path)
            avg = pgm_average_brightness(path)
            dr = pgm_dynamic_range(path)
            assert total >= 1
            assert avg >= 0.0
            records.append({
                "file": f.name,
                "format": "pgm",
                "format_family": "image",
                "total_pixels": total,
                "avg_brightness": avg,
                "dynamic_range": dr,
            })
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            path = _ap(f)
            total = ppm_pixel_count(path)
            ar = ppm_aspect_ratio(path)
            sat = ppm_saturation_estimate(path)
            assert total >= 1
            assert ar > 0.0
            assert sat >= 0.0
            records.append({
                "file": f.name,
                "format": "ppm",
                "format_family": "image",
                "total_pixels": total,
                "aspect_ratio": ar,
                "saturation_estimate": sat,
            })
        dest = tmp_path / "pixel-multiformat.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 9
        assert all(r["format_family"] == "image" for r in records)

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in sorted(_PBM_DIR.glob("*.pbm")):
            records.append({"file": f.name, "format": "pbm", "total_pixels": pbm_total_pixel_count(_ap(f))})
        for f in sorted(_PGM_DIR.glob("*.pgm")):
            records.append({"file": f.name, "format": "pgm", "total_pixels": pgm_total_pixel_count(_ap(f))})
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            records.append({"file": f.name, "format": "ppm", "total_pixels": ppm_pixel_count(_ap(f))})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["format"] == back["format"]
            assert orig["total_pixels"] == back["total_pixels"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(_PBM_DIR / "1x1-black.pbm")
        records = [{"file": "1x1-black.pbm", "format": "pbm", "total_pixels": pbm_total_pixel_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_format_family_export(self, tmp_path):
        records = []
        for f in sorted(_PBM_DIR.glob("*.pbm")):
            records.append({"file": f.name, "format": "pbm", "format_family": "image",
                            "total_pixels": pbm_total_pixel_count(_ap(f))})
        for f in sorted(_PGM_DIR.glob("*.pgm")):
            records.append({"file": f.name, "format": "pgm", "format_family": "image",
                            "total_pixels": pgm_total_pixel_count(_ap(f))})
        for f in sorted(_PPM_DIR.glob("*.ppm")):
            records.append({"file": f.name, "format": "ppm", "format_family": "image",
                            "total_pixels": ppm_pixel_count(_ap(f))})
        dest = tmp_path / "families.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 9
        assert all(r["format_family"] == "image" for r in loaded)
        assert all(r["total_pixels"] >= 1 for r in loaded)
        formats_seen = {r["format"] for r in loaded}
        assert "pbm" in formats_seen
        assert "pgm" in formats_seen
        assert "ppm" in formats_seen
