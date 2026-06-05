# R107 Wave 3: PPM write+parse roundtrip and PGM parse hardening
# 10 tests — write, parse metadata, probe, error handling

import importlib
import os
import tempfile
import pytest

ppm = importlib.import_module("ppm")
pgm = importlib.import_module("pgm")

PGM_SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "pgm")
PGM_VALID = os.path.join(PGM_SAMPLES, "valid")


def _get_pgm_sample():
    for d in [PGM_VALID, PGM_SAMPLES]:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith(".pgm"):
                    return os.path.join(d, f)
    pytest.skip("No PGM sample files")


class TestPpmWriteAndPgmParse:
    """PPM write roundtrip and PGM parse verification."""

    def test_ppm_write_creates_file(self):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
        path = tempfile.mktemp(suffix=".ppm")
        try:
            ppm.write_ppm(pixels, 2, 2, 255, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            if os.path.exists(path): os.unlink(path)

    def test_ppm_roundtrip_metadata(self):
        pixels = [(100, 200, 50), (10, 20, 30)]
        path = tempfile.mktemp(suffix=".ppm")
        try:
            ppm.write_ppm(pixels, 2, 1, 255, path)
            result = ppm.parse_ppm(path)
            assert result["ok"] is True
            assert result["width"] == 2
            assert result["height"] == 1
            assert result["maxval"] == 255
        finally:
            if os.path.exists(path): os.unlink(path)

    def test_ppm_single_pixel(self):
        path = tempfile.mktemp(suffix=".ppm")
        try:
            ppm.write_ppm([(128, 64, 32)], 1, 1, 255, path)
            result = ppm.parse_ppm(path)
            assert result["ok"] is True
            assert result["pixel_count"] == 1
        finally:
            if os.path.exists(path): os.unlink(path)

    def test_ppm_maxval_15(self):
        path = tempfile.mktemp(suffix=".ppm")
        try:
            ppm.write_ppm([(15, 0, 7), (0, 15, 8)], 2, 1, 15, path)
            result = ppm.parse_ppm(path)
            assert result["maxval"] == 15
        finally:
            if os.path.exists(path): os.unlink(path)

    def test_ppm_file_header(self):
        path = tempfile.mktemp(suffix=".ppm")
        try:
            ppm.write_ppm([(0, 0, 0)], 1, 1, 255, path)
            with open(path, "r") as f:
                header = f.read(2)
            assert header == "P3"
        finally:
            if os.path.exists(path): os.unlink(path)

    def test_ppm_probe(self):
        path = tempfile.mktemp(suffix=".ppm")
        try:
            ppm.write_ppm([(255, 0, 0)], 1, 1, 255, path)
            result = ppm.probe_ppm(path)
            assert isinstance(result, dict)
        finally:
            if os.path.exists(path): os.unlink(path)

    def test_ppm_nonexistent_parse(self):
        result = ppm.parse_ppm("/nonexistent/file.ppm")
        assert result.get("ok") is False

    def test_pgm_parse_valid(self):
        path = _get_pgm_sample()
        result = pgm.parse_pgm(path)
        assert result.get("ok") is True
        assert result["width"] > 0

    def test_pgm_probe(self):
        path = _get_pgm_sample()
        result = pgm.probe_pgm(path)
        assert isinstance(result, dict)

    def test_pgm_nonexistent_parse(self):
        result = pgm.parse_pgm("/nonexistent/file.pgm")
        assert result.get("ok") is False
