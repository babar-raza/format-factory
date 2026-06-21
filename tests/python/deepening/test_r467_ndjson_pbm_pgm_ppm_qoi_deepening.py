"""Sprint R467 — NDJSON/PBM/PGM/PPM/QOI round 13 deepening (_times_five)."""
import json, os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.ndjson.ndjson_codec import ndjson_record_count_times_five, ndjson_unique_key_count_times_five
from src.python.pbm.pbm_parser import pbm_total_pixels_times_five, pbm_file_size_times_five
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_five, pgm_file_size_times_five
from src.python.ppm.ppm_parser import ppm_file_size_times_five, ppm_unique_pixel_count_times_five
from src.python.qoi.qoi_parser import qoi_pixel_count_times_five, qoi_file_size_times_five


# --- NDJSON ---
class TestNdjsonRecordCountTimesFive:
    def test_returns_int(self, tmp_path):
        f = tmp_path / "test.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n" + json.dumps({"b": 2}) + "\n")
        assert isinstance(ndjson_record_count_times_five(str(f)), int)

    def test_non_negative(self, tmp_path):
        f = tmp_path / "test.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_record_count_times_five(str(f)) >= 0

    def test_divisible_by_five(self, tmp_path):
        f = tmp_path / "test.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n" + json.dumps({"b": 2}) + "\n")
        assert ndjson_record_count_times_five(str(f)) % 5 == 0


class TestNdjsonUniqueKeyCountTimesFive:
    def test_returns_int(self, tmp_path):
        f = tmp_path / "test.ndjson"
        f.write_text(json.dumps({"x": 1}) + "\n")
        assert isinstance(ndjson_unique_key_count_times_five(str(f)), int)

    def test_non_negative(self, tmp_path):
        f = tmp_path / "test.ndjson"
        f.write_text(json.dumps({"x": 1}) + "\n")
        assert ndjson_unique_key_count_times_five(str(f)) >= 0

    def test_divisible_by_five(self, tmp_path):
        f = tmp_path / "test.ndjson"
        f.write_text(json.dumps({"x": 1, "y": 2}) + "\n")
        assert ndjson_unique_key_count_times_five(str(f)) % 5 == 0


# --- PBM ---
class TestPbmTotalPixelsTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert isinstance(pbm_total_pixels_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_total_pixels_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_total_pixels_times_five(p) % 5 == 0


class TestPbmFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert isinstance(pbm_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_file_size_times_five(p) % 5 == 0


# --- PGM ---
class TestPgmTotalPixelCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert isinstance(pgm_total_pixel_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_total_pixel_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_total_pixel_count_times_five(p) % 5 == 0


class TestPgmFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert isinstance(pgm_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_file_size_times_five(p) % 5 == 0


# --- PPM ---
class TestPpmFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert isinstance(ppm_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_file_size_times_five(p) % 5 == 0


class TestPpmUniquePixelCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert isinstance(ppm_unique_pixel_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_unique_pixel_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_unique_pixel_count_times_five(p) % 5 == 0


# --- QOI ---
class TestQoiPixelCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert isinstance(qoi_pixel_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_pixel_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_pixel_count_times_five(p) % 5 == 0


class TestQoiFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert isinstance(qoi_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_file_size_times_five(p) % 5 == 0
