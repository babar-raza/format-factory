"""Sprint R463 — NDJSON/PBM/PGM/PPM/QOI round 12 deepening (_times_four continued)."""
import json, os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.ndjson import ndjson_file_size_times_four, ndjson_unique_key_count_times_four
from src.python.pbm import pbm_file_size_times_four, pbm_total_pixels_times_four
from src.python.pgm import pgm_file_size_times_four, pgm_total_pixel_count_times_four
from src.python.ppm import ppm_file_size_times_four, ppm_unique_pixel_count_times_four
from src.python.qoi import qoi_file_size_times_four, qoi_pixel_count_times_four


def _ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text(json.dumps({"a": 1, "b": "x"}) + "\n" + json.dumps({"a": 2, "c": "y"}) + "\n")
    return str(p)


# --- NDJSON ---
class TestNdjsonFileSizeTimesFour:
    def test_returns_int(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert isinstance(ndjson_file_size_times_four(p), int)

    def test_equals_four_times_size(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert ndjson_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert ndjson_file_size_times_four(p) > 0


class TestNdjsonUniqueKeyCountTimesFour:
    def test_returns_int(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert isinstance(ndjson_unique_key_count_times_four(p), int)

    def test_non_negative(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert ndjson_unique_key_count_times_four(p) >= 0

    def test_divisible_by_four(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert ndjson_unique_key_count_times_four(p) % 4 == 0


# --- PBM ---
class TestPbmFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert isinstance(pbm_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_file_size_times_four(p) > 0


class TestPbmTotalPixelsTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert isinstance(pbm_total_pixels_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_total_pixels_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_total_pixels_times_four(p) % 4 == 0


# --- PGM ---
class TestPgmFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert isinstance(pgm_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_file_size_times_four(p) > 0


class TestPgmTotalPixelCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert isinstance(pgm_total_pixel_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_total_pixel_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_total_pixel_count_times_four(p) % 4 == 0


# --- PPM ---
class TestPpmFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert isinstance(ppm_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_file_size_times_four(p) > 0


class TestPpmUniquePixelCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert isinstance(ppm_unique_pixel_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_unique_pixel_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_unique_pixel_count_times_four(p) % 4 == 0


# --- QOI ---
class TestQoiFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert isinstance(qoi_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_file_size_times_four(p) > 0


class TestQoiPixelCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert isinstance(qoi_pixel_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_pixel_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_pixel_count_times_four(p) % 4 == 0
