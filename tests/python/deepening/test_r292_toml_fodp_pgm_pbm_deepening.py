"""Sprint 62 — TOML / FODP / PGM / PBM product deepening (R292).

Tests 8 new analytics functions:
  TOML: toml_has_booleans, toml_key_count_per_table
  FODP: fodp_avg_title_length, fodp_is_text_heavy
  PGM: pgm_is_wide, pgm_pixel_density
  PBM: pbm_is_tall, pbm_is_wide
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_has_booleans, toml_key_count_per_table
from src.python.fodp import fodp_avg_title_length, fodp_is_text_heavy
from src.python.pgm import pgm_is_wide, pgm_pixel_density
from src.python.pbm import pbm_is_tall, pbm_is_wide

_TOML = b'[section]\nkey = "value"\nenabled = true\n'
_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"


class TestTomlHasBooleans:
    def test_returns_bool(self):
        assert isinstance(toml_has_booleans(_TOML), bool)

    def test_has_true(self):
        assert toml_has_booleans(b'enabled = true\nname = "test"\n') is True

    def test_no_booleans(self):
        assert toml_has_booleans(b'name = "test"\n') is False


class TestTomlKeyCountPerTable:
    def test_returns_list(self):
        result = toml_key_count_per_table(_TOML)
        assert isinstance(result, list)

    def test_section_keys(self):
        result = toml_key_count_per_table(_TOML)
        assert len(result) >= 1


class TestFodpAvgTitleLength:
    def test_returns_float(self):
        assert isinstance(fodp_avg_title_length(_FODP), (int, float))

    def test_nonnegative(self):
        assert fodp_avg_title_length(_FODP) >= 0.0


class TestFodpIsTextHeavy:
    def test_returns_bool(self):
        assert isinstance(fodp_is_text_heavy(_FODP), bool)


class TestPgmIsWide:
    def test_returns_bool(self):
        assert isinstance(pgm_is_wide(_PGM), bool)

    def test_2x2_not_wide(self):
        assert pgm_is_wide(_PGM) is False


class TestPgmPixelDensity:
    def test_returns_float(self):
        assert isinstance(pgm_pixel_density(_PGM), (int, float))

    def test_positive(self):
        assert pgm_pixel_density(_PGM) > 0.0


class TestPbmIsTall:
    def test_returns_bool(self):
        assert isinstance(pbm_is_tall(_PBM), bool)

    def test_2x2_not_tall(self):
        assert pbm_is_tall(_PBM) is False


class TestPbmIsWide:
    def test_returns_bool(self):
        assert isinstance(pbm_is_wide(_PBM), bool)

    def test_2x2_not_wide(self):
        assert pbm_is_wide(_PBM) is False
