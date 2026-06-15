"""Tests for ppm_is_binary — detect P6 (binary) vs P3 (ASCII) PPM format."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_is_binary, PpmError

SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPpmIsBinary:
    def test_p6_file_returns_true(self, tmp_path):
        p = tmp_path / "binary.ppm"
        # P6 header + 1x1 RGB pixel (3 bytes)
        p.write_bytes(b"P6\n1 1\n255\n\xff\x00\x00")
        assert ppm_is_binary(p) is True

    def test_p3_file_returns_false(self, tmp_path):
        p = tmp_path / "ascii.ppm"
        p.write_text("P3\n1 1\n255\n255 0 0\n", encoding="utf-8")
        assert ppm_is_binary(p) is False

    def test_returns_bool(self, tmp_path):
        p = tmp_path / "test.ppm"
        p.write_bytes(b"P6\n1 1\n255\n\x00\x00\x00")
        assert isinstance(ppm_is_binary(p), bool)

    def test_invalid_magic_raises(self, tmp_path):
        p = tmp_path / "bad.ppm"
        p.write_bytes(b"P9\n1 1\n255\n")
        with pytest.raises(PpmError):
            ppm_is_binary(p)

    def test_importable_from_init(self):
        from src.python.ppm import ppm_is_binary as fn
        assert callable(fn)

    def test_in_all_list(self):
        from src.python.ppm import __all__
        assert "ppm_is_binary" in __all__

    def test_on_real_samples(self):
        if not SAMPLES.exists():
            pytest.skip("No PPM samples")
        files = list(SAMPLES.glob("*.ppm"))
        if not files:
            pytest.skip("No .ppm files")
        for f in files:
            result = ppm_is_binary(f)
            assert isinstance(result, bool), f"Non-bool for {f.name}"
