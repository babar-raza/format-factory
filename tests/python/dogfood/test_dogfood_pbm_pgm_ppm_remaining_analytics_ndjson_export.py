"""
tests/python/dogfood/test_dogfood_pbm_pgm_ppm_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-80
Dogfood export: PBM+PGM+PPM remaining analytics -> write as NDJSON -> verify.
PBM uses: pbm_perimeter, pbm_black_pixel_count.
PGM uses: pgm_dimension_ratio, pgm_is_square.
PPM uses: ppm_dimension_ratio, ppm_is_square.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm import pbm_perimeter, pbm_black_pixel_count
from pgm import pgm_dimension_ratio, pgm_is_square
from ppm import ppm_dimension_ratio, ppm_is_square
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _valid_pbm_files():
    return sorted(_PBM_DIR.glob("*.pbm"))


def _valid_pgm_files():
    return sorted(_PGM_DIR.glob("*.pgm"))


def _valid_ppm_files():
    return sorted(_PPM_DIR.glob("*.ppm"))


class TestPbmPgmPpmRemainingAnalyticsNdjsonExport:
    """PBM+PGM+PPM remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_pbm_remaining_basics(self):
        sample = str(next(_PBM_DIR.glob("*.pbm")))
        perimeter = pbm_perimeter(sample)
        black_count = pbm_black_pixel_count(sample)
        assert perimeter >= 0
        assert black_count >= 0

    def test_pgm_ppm_remaining_basics(self):
        pgm_sample = str(next(_PGM_DIR.glob("*.pgm")))
        ppm_sample = str(next(_PPM_DIR.glob("*.ppm")))
        pgm_ratio = pgm_dimension_ratio(pgm_sample)
        pgm_sq = pgm_is_square(pgm_sample)
        ppm_ratio = ppm_dimension_ratio(ppm_sample)
        ppm_sq = ppm_is_square(ppm_sample)
        assert isinstance(pgm_ratio, float)
        assert isinstance(pgm_sq, bool)
        assert isinstance(ppm_ratio, float)
        assert isinstance(ppm_sq, bool)

    def test_pbm_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            perimeter = pbm_perimeter(path)
            black_count = pbm_black_pixel_count(path)
            assert perimeter >= 0, f"pbm_perimeter must be >= 0 for {f.name}"
            assert black_count >= 0, f"pbm_black_pixel_count must be >= 0 for {f.name}"
            records.append({
                "file": f.name,
                "perimeter": perimeter,
                "black_pixel_count": black_count,
                "source_format": "pbm",
            })
        dest = tmp_path / "pbm-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_pgm_ppm_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = str(f)
            ratio = pgm_dimension_ratio(path)
            is_sq = pgm_is_square(path)
            assert isinstance(ratio, float), f"pgm_dimension_ratio must be float for {f.name}"
            assert isinstance(is_sq, bool), f"pgm_is_square must be bool for {f.name}"
            records.append({"file": f.name, "dimension_ratio": ratio, "is_square": is_sq, "source_format": "pgm"})
        for f in _valid_ppm_files():
            path = str(f)
            ratio = ppm_dimension_ratio(path)
            is_sq = ppm_is_square(path)
            assert isinstance(ratio, float), f"ppm_dimension_ratio must be float for {f.name}"
            assert isinstance(is_sq, bool), f"ppm_is_square must be bool for {f.name}"
            records.append({"file": f.name, "dimension_ratio": ratio, "is_square": is_sq, "source_format": "ppm"})
        dest = tmp_path / "pgm-ppm-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 6

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            perimeter = pbm_perimeter(path)
            black_count = pbm_black_pixel_count(path)
            records.append({"file": f.name, "perimeter": perimeter, "black_pixel_count": black_count})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["perimeter"] == back["perimeter"]
            assert orig["black_pixel_count"] == back["black_pixel_count"]

    def test_json_lines_valid(self, tmp_path):
        pbm_sample = str(next(_PBM_DIR.glob("*.pbm")))
        pgm_sample = str(next(_PGM_DIR.glob("*.pgm")))
        records = [
            {"file": "sample.pbm", "perimeter": pbm_perimeter(pbm_sample), "format": "pbm"},
            {"file": "sample.pgm", "dimension_ratio": pgm_dimension_ratio(pgm_sample), "format": "pgm"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
