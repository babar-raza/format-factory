"""
tests/python/dogfood/test_dogfood_pgm_saturation_dark_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-66
Dogfood export: PGM parse -> saturation/dark analytics -> write as NDJSON -> verify.
Uses: pgm_has_any_saturated, pgm_is_all_dark, grayscale_variance,
pgm_total_pixel_count, pgm_average_brightness, pgm_standard_deviation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm import (
    pgm_has_any_saturated,
    pgm_is_all_dark,
    grayscale_variance,
    pgm_total_pixel_count,
    pgm_average_brightness,
    pgm_standard_deviation,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _valid_pgm_files():
    return sorted(_PGM_DIR.glob("*.pgm"))


class TestPgmSaturationDarkAnalyticsNdjsonExport:
    """PGM -> saturation/dark analytics -> NDJSON export -> roundtrip verification."""

    def test_saturation_and_dark_basics(self):
        sample = str(next(_PGM_DIR.glob("*.pgm")))
        has_sat = pgm_has_any_saturated(sample)
        is_dark = pgm_is_all_dark(sample)
        variance = grayscale_variance(sample)
        assert isinstance(has_sat, bool)
        assert isinstance(is_dark, bool)
        assert isinstance(variance, float)

    def test_pixel_stats_basics(self):
        sample = str(next(_PGM_DIR.glob("*.pgm")))
        total = pgm_total_pixel_count(sample)
        avg = pgm_average_brightness(sample)
        std = pgm_standard_deviation(sample)
        assert total >= 0
        assert isinstance(avg, float)
        assert isinstance(std, float)

    def test_saturation_dark_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = str(f)
            has_sat = pgm_has_any_saturated(path)
            is_dark = pgm_is_all_dark(path)
            variance = grayscale_variance(path)
            total = pgm_total_pixel_count(path)
            avg = pgm_average_brightness(path)
            std = pgm_standard_deviation(path)
            assert isinstance(has_sat, bool), f"pgm_has_any_saturated must be bool for {f.name}"
            assert isinstance(is_dark, bool), f"pgm_is_all_dark must be bool for {f.name}"
            assert isinstance(variance, float), f"grayscale_variance must be float for {f.name}"
            assert total >= 0, f"pgm_total_pixel_count must be >= 0 for {f.name}"
            assert isinstance(avg, float), f"pgm_average_brightness must be float for {f.name}"
            assert isinstance(std, float), f"pgm_standard_deviation must be float for {f.name}"
            records.append({
                "file": f.name,
                "has_any_saturated": has_sat,
                "is_all_dark": is_dark,
                "grayscale_variance": variance,
                "total_pixel_count": total,
                "average_brightness": avg,
                "standard_deviation": std,
                "source_format": "pgm",
            })
        dest = tmp_path / "pgm-saturation-dark.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = str(f)
            has_sat = pgm_has_any_saturated(path)
            variance = grayscale_variance(path)
            records.append({
                "file": f.name,
                "has_any_saturated": has_sat,
                "grayscale_variance": variance,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["has_any_saturated"] == back["has_any_saturated"]
            assert orig["grayscale_variance"] == back["grayscale_variance"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_PGM_DIR.glob("*.pgm")))
        has_sat = pgm_has_any_saturated(sample)
        is_dark = pgm_is_all_dark(sample)
        records = [{"file": "sample.pgm", "has_any_saturated": has_sat, "is_all_dark": is_dark}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_dark_variance_export(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = str(f)
            is_dark = pgm_is_all_dark(path)
            variance = grayscale_variance(path)
            has_sat = pgm_has_any_saturated(path)
            assert isinstance(is_dark, bool)
            assert isinstance(variance, float)
            assert isinstance(has_sat, bool)
            records.append({
                "file": f.name,
                "is_all_dark": is_dark,
                "grayscale_variance": variance,
                "has_any_saturated": has_sat,
                "format": "pgm",
            })
        dest = tmp_path / "dark-variance.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "pgm" for r in loaded)
        assert all(isinstance(r["is_all_dark"], bool) for r in loaded)
