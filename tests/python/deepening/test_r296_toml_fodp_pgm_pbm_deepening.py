"""Sprint 66 — TOML / FODP / PGM / PBM product deepening (R296).

Tests 8 new analytics functions:
  TOML: toml_is_flat, toml_total_value_count
  FODP: fodp_max_notes_length, fodp_slide_count_is_one
  PGM: pgm_row_count, pgm_is_portrait
  PBM: pbm_is_portrait, pbm_pixel_density
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_is_flat, toml_total_value_count
from src.python.fodp import fodp_max_notes_length, fodp_slide_count_is_one
from src.python.pgm import pgm_row_count, pgm_is_portrait
from src.python.pbm import pbm_is_portrait, pbm_pixel_density

_TOML = b'enabled = true\nname = "test"\n[section]\nkey = "value"\ncount = 42\n'
_TOML_FLAT = b'enabled = true\nname = "test"\n'
_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "3x2-pattern.pbm"


class TestTomlIsFlat:
    def test_returns_bool(self):
        assert isinstance(toml_is_flat(_TOML), bool)

    def test_flat_true(self):
        assert toml_is_flat(_TOML_FLAT) is True

    def test_nested_false(self):
        assert toml_is_flat(_TOML) is False


class TestTomlTotalValueCount:
    def test_returns_int(self):
        assert isinstance(toml_total_value_count(_TOML), int)

    def test_positive(self):
        assert toml_total_value_count(_TOML) > 0


class TestFodpMaxNotesLength:
    def test_returns_int(self):
        assert isinstance(fodp_max_notes_length(_FODP), int)

    def test_nonnegative(self):
        assert fodp_max_notes_length(_FODP) >= 0


class TestFodpSlideCountIsOne:
    def test_returns_bool(self):
        assert isinstance(fodp_slide_count_is_one(_FODP), bool)


class TestPgmRowCount:
    def test_returns_int(self):
        assert isinstance(pgm_row_count(_PGM), int)

    def test_positive(self):
        assert pgm_row_count(_PGM) > 0


class TestPgmIsPortrait:
    def test_returns_bool(self):
        assert isinstance(pgm_is_portrait(_PGM), bool)


class TestPbmIsPortrait:
    def test_returns_bool(self):
        assert isinstance(pbm_is_portrait(_PBM), bool)


class TestPbmPixelDensity:
    def test_returns_float(self):
        assert isinstance(pbm_pixel_density(_PBM), (int, float))

    def test_positive(self):
        assert pbm_pixel_density(_PBM) > 0.0
