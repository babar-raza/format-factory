"""
tests/python/dogfood/test_dogfood_pgm_saturation_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-51
Dogfood export: PGM parse -> saturation/zero analytics -> write as NDJSON -> verify.
Uses: pgm_saturated_pixel_count, pgm_zero_pixel_count, pgm_pixel_sum,
pgm_nonzero_pixel_ratio, pgm_total_pixel_count, pgm_average_brightness.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import (
    pgm_saturated_pixel_count,
    pgm_zero_pixel_count,
    pgm_pixel_sum,
    pgm_nonzero_pixel_ratio,
    pgm_total_pixel_count,
    pgm_average_brightness,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson


_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"


def _ap(f):
    return os.path.abspath(str(f))


def _valid_pgm_files():
    return sorted(_PGM_DIR.glob("*.pgm"))


class TestPgmSaturationAnalyticsNdjsonExport:
    """PGM -> saturation/zero pixel analytics -> NDJSON export -> roundtrip verification."""

    def test_saturated_and_zero_counts(self):
        sample = _ap(next(_PGM_DIR.glob("*.pgm")))
        saturated = pgm_saturated_pixel_count(sample)
        zero_count = pgm_zero_pixel_count(sample)
        assert saturated >= 0
        assert zero_count >= 0

    def test_pixel_sum_and_nonzero_ratio(self):
        sample = _ap(next(_PGM_DIR.glob("*.pgm")))
        pixel_sum = pgm_pixel_sum(sample)
        nonzero_ratio = pgm_nonzero_pixel_ratio(sample)
        total = pgm_total_pixel_count(sample)
        avg = pgm_average_brightness(sample)
        assert pixel_sum >= 0
        assert 0.0 <= nonzero_ratio <= 1.0
        assert total >= 0
        assert avg >= 0.0

    def test_saturation_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = _ap(f)
            saturated = pgm_saturated_pixel_count(path)
            zero_count = pgm_zero_pixel_count(path)
            pixel_sum = pgm_pixel_sum(path)
            nonzero_ratio = pgm_nonzero_pixel_ratio(path)
            total = pgm_total_pixel_count(path)
            avg = pgm_average_brightness(path)
            assert saturated >= 0, f"saturated_pixel_count must be >= 0 for {f.name}"
            assert zero_count >= 0, f"zero_pixel_count must be >= 0 for {f.name}"
            assert pixel_sum >= 0, f"pixel_sum must be >= 0 for {f.name}"
            assert 0.0 <= nonzero_ratio <= 1.0, f"nonzero_pixel_ratio must be in [0,1] for {f.name}"
            assert total >= 0, f"total_pixel_count must be >= 0 for {f.name}"
            assert avg >= 0.0, f"average_brightness must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "saturated_pixel_count": saturated,
                "zero_pixel_count": zero_count,
                "pixel_sum": pixel_sum,
                "nonzero_pixel_ratio": nonzero_ratio,
                "total_pixel_count": total,
                "average_brightness": avg,
                "source_format": "pgm",
            })
        dest = tmp_path / "pgm-saturation.ndjson"
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
                "saturated_pixel_count": pgm_saturated_pixel_count(path),
                "zero_pixel_count": pgm_zero_pixel_count(path),
                "total_pixel_count": pgm_total_pixel_count(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["saturated_pixel_count"] == back["saturated_pixel_count"]
            assert orig["zero_pixel_count"] == back["zero_pixel_count"]

    def test_json_lines_valid(self, tmp_path):
        sample = _ap(next(_PGM_DIR.glob("*.pgm")))
        records = [{"file": "sample.pgm", "saturated": pgm_saturated_pixel_count(sample)}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_zero_sum_export(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = _ap(f)
            zero_count = pgm_zero_pixel_count(path)
            pixel_sum = pgm_pixel_sum(path)
            nonzero_ratio = pgm_nonzero_pixel_ratio(path)
            assert zero_count >= 0
            assert pixel_sum >= 0
            assert 0.0 <= nonzero_ratio <= 1.0
            records.append({
                "file": f.name,
                "zero_pixel_count": zero_count,
                "pixel_sum": pixel_sum,
                "nonzero_pixel_ratio": nonzero_ratio,
                "format": "pgm",
            })
        dest = tmp_path / "zero-sum.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "pgm" for r in loaded)
        assert all(r["zero_pixel_count"] >= 0 for r in loaded)
