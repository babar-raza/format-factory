"""
tests/python/dogfood/test_dogfood_image_remaining_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-52
Dogfood export: PBM + PGM + PPM remaining uncovered analytics -> write as NDJSON -> verify.
PBM uses: pbm_black_density, pbm_diagonal, pbm_has_any_white, pbm_is_landscape,
          pbm_is_square, pbm_max_dimension, pbm_max_row_black_count, pbm_min_dimension.
PGM uses: pgm_aspect_ratio, pgm_brightness_range, pgm_diagonal, pgm_has_any_zero,
          pgm_is_all_bright, pgm_is_landscape, pgm_max_dimension, pgm_min_dimension.
PPM uses: ppm_has_pure_black, ppm_has_pure_white, ppm_is_landscape,
          ppm_max_channel_sum, ppm_max_dimension, ppm_min_channel_sum.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_black_density, pbm_diagonal, pbm_has_any_white,
    pbm_is_landscape, pbm_is_square, pbm_max_dimension,
    pbm_max_row_black_count, pbm_min_dimension,
)
from pgm.pgm_parser import (
    pgm_aspect_ratio, pgm_brightness_range, pgm_diagonal,
    pgm_has_any_zero, pgm_is_all_bright, pgm_is_landscape,
    pgm_max_dimension, pgm_min_dimension,
)
from ppm.ppm_parser import (
    ppm_has_pure_black, ppm_has_pure_white, ppm_is_landscape,
    ppm_max_channel_sum, ppm_max_dimension, ppm_min_channel_sum,
)
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


class TestImageRemainingAnalyticsNdjsonExport:
    """PBM + PGM + PPM remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_pbm_remaining_basics(self):
        s1 = str(_PBM_DIR / "1x1-black.pbm")
        s2 = str(_PBM_DIR / "2x2-checker.pbm")
        assert pbm_black_density(s1) == 1.0
        assert pbm_has_any_white(s1) is False
        assert pbm_is_square(s1) is True
        assert pbm_max_dimension(s1) == 1
        assert pbm_min_dimension(s1) == 1
        assert pbm_max_row_black_count(s1) == 1
        assert pbm_black_density(s2) == 0.5
        assert pbm_has_any_white(s2) is True
        assert pbm_max_dimension(s2) == 2

    def test_pgm_remaining_basics(self):
        s1 = str(_PGM_DIR / "1x1-white.pgm")
        s2 = str(_PGM_DIR / "2x2-gradient.pgm")
        assert pgm_aspect_ratio(s1) == 1.0
        assert pgm_brightness_range(s1) == 0
        assert pgm_has_any_zero(s1) is False
        assert pgm_is_all_bright(s1) is True
        assert pgm_max_dimension(s1) == 1
        assert pgm_min_dimension(s1) == 1
        assert pgm_brightness_range(s2) == 255
        assert pgm_has_any_zero(s2) is True
        assert pgm_is_all_bright(s2) is False
        assert pgm_max_dimension(s2) == 2

    def test_ppm_remaining_basics(self):
        s1 = str(_PPM_DIR / "1x1-red.ppm")
        s2 = str(_PPM_DIR / "2x2-rgbw.ppm")
        assert ppm_has_pure_black(s1) is False
        assert ppm_has_pure_white(s1) is False
        assert ppm_max_channel_sum(s1) == 255
        assert ppm_min_channel_sum(s1) == 255
        assert ppm_max_dimension(s1) == 1
        assert ppm_has_pure_white(s2) is True
        assert ppm_max_channel_sum(s2) == 765
        assert ppm_max_dimension(s2) == 2

    def test_pbm_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            records.append({
                "file": f.name,
                "black_density": pbm_black_density(path),
                "diagonal": pbm_diagonal(path),
                "has_any_white": pbm_has_any_white(path),
                "is_landscape": pbm_is_landscape(path),
                "is_square": pbm_is_square(path),
                "max_dimension": pbm_max_dimension(path),
                "max_row_black_count": pbm_max_row_black_count(path),
                "min_dimension": pbm_min_dimension(path),
                "source_format": "pbm",
            })
        dest = tmp_path / "pbm-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 2

    def test_pgm_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pgm_files():
            path = str(f)
            records.append({
                "file": f.name,
                "aspect_ratio": pgm_aspect_ratio(path),
                "brightness_range": pgm_brightness_range(path),
                "diagonal": pgm_diagonal(path),
                "has_any_zero": pgm_has_any_zero(path),
                "is_all_bright": pgm_is_all_bright(path),
                "is_landscape": pgm_is_landscape(path),
                "max_dimension": pgm_max_dimension(path),
                "min_dimension": pgm_min_dimension(path),
                "source_format": "pgm",
            })
        dest = tmp_path / "pgm-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ppm_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_ppm_files():
            path = str(f)
            records.append({
                "file": f.name,
                "has_pure_black": ppm_has_pure_black(path),
                "has_pure_white": ppm_has_pure_white(path),
                "is_landscape": ppm_is_landscape(path),
                "max_channel_sum": ppm_max_channel_sum(path),
                "max_dimension": ppm_max_dimension(path),
                "min_channel_sum": ppm_min_channel_sum(path),
                "source_format": "ppm",
            })
        dest = tmp_path / "ppm-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 2

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            records.append({
                "file": f.name,
                "black_density": pbm_black_density(path),
                "is_square": pbm_is_square(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["black_density"] == back["black_density"]
            assert orig["is_square"] == back["is_square"]

    def test_json_lines_valid(self, tmp_path):
        s_pbm = str(_PBM_DIR / "1x1-black.pbm")
        s_pgm = str(_PGM_DIR / "1x1-white.pgm")
        s_ppm = str(_PPM_DIR / "1x1-red.ppm")
        records = [
            {"file": "1x1-black.pbm", "black_density": pbm_black_density(s_pbm), "format": "pbm"},
            {"file": "1x1-white.pgm", "aspect_ratio": pgm_aspect_ratio(s_pgm), "format": "pgm"},
            {"file": "1x1-red.ppm", "max_channel_sum": ppm_max_channel_sum(s_ppm), "format": "ppm"},
        ]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
