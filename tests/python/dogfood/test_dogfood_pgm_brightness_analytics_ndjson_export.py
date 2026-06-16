"""
tests/python/dogfood/test_dogfood_pgm_brightness_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-45
Dogfood export: PGM parse -> brightness/distribution analytics -> write as NDJSON -> verify.
Uses: pgm_dark_pixel_count, pgm_brightness_quartiles, pgm_is_uniform,
pgm_max_pixel_value, pgm_min_pixel_value, pgm_average_brightness.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import (
    pgm_dark_pixel_count,
    pgm_brightness_quartiles,
    pgm_is_uniform,
    pgm_max_pixel_value,
    pgm_min_pixel_value,
    pgm_average_brightness,
    pgm_total_pixel_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_pgm_files():
    return sorted(_PGM_DIR.glob("*.pgm"))


class TestPgmBrightnessAnalyticsNdjsonExport:
    """PGM -> brightness/distribution analytics -> NDJSON export -> roundtrip verification."""

    def test_dark_pixel_count_and_uniform(self):
        sample = _ap(next(_PGM_DIR.glob("*.pgm")))
        dark = pgm_dark_pixel_count(sample)
        is_uni = pgm_is_uniform(sample)
        assert dark >= 0
        assert isinstance(is_uni, bool)

    def test_brightness_quartiles(self):
        sample = _ap(next(_PGM_DIR.glob("*.pgm")))
        q = pgm_brightness_quartiles(sample)
        assert isinstance(q, dict)
        assert len(q) > 0

    def test_brightness_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = _ap(f)
            dark = pgm_dark_pixel_count(path)
            q = pgm_brightness_quartiles(path)
            is_uni = pgm_is_uniform(path)
            max_pv = pgm_max_pixel_value(path)
            min_pv = pgm_min_pixel_value(path)
            avg = pgm_average_brightness(path)
            total = pgm_total_pixel_count(path)
            assert dark >= 0, f"dark_pixel_count must be >= 0 for {f.name}"
            assert isinstance(q, dict), f"brightness_quartiles must be dict for {f.name}"
            assert isinstance(is_uni, bool), f"is_uniform must be bool for {f.name}"
            assert max_pv >= 0, f"max_pixel_value must be >= 0 for {f.name}"
            assert min_pv >= 0, f"min_pixel_value must be >= 0 for {f.name}"
            assert min_pv <= max_pv, f"min <= max pixel value for {f.name}"
            assert avg >= 0.0, f"average_brightness must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "dark_pixel_count": dark,
                "is_uniform": is_uni,
                "max_pixel_value": max_pv,
                "min_pixel_value": min_pv,
                "average_brightness": avg,
                "total_pixels": total,
                "source_format": "pgm",
            })
        dest = tmp_path / "pgm-brightness.ndjson"
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
                "max_pixel_value": pgm_max_pixel_value(path),
                "min_pixel_value": pgm_min_pixel_value(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["max_pixel_value"] == back["max_pixel_value"]
            assert orig["min_pixel_value"] == back["min_pixel_value"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_PGM_DIR.glob("*.pgm")))
        records = [{"file": "sample.pgm", "average_brightness": pgm_average_brightness(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_dark_uniform_export(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = _ap(f)
            dark = pgm_dark_pixel_count(path)
            is_uni = pgm_is_uniform(path)
            avg = pgm_average_brightness(path)
            assert dark >= 0
            assert isinstance(is_uni, bool)
            assert avg >= 0.0
            records.append({
                "file": f.name,
                "dark_pixel_count": dark,
                "is_uniform": is_uni,
                "average_brightness": avg,
                "format": "pgm",
            })
        dest = tmp_path / "dark-uniform.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "pgm" for r in loaded)
        assert all(r["dark_pixel_count"] >= 0 for r in loaded)
