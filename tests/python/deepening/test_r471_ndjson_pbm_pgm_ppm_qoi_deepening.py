"""Sprint R471 — NDJSON/PBM/PGM/PPM/QOI _times_six composite analytics tests."""
import json, pathlib, sys, tempfile

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.ndjson.ndjson_codec import ndjson_record_count_times_six, ndjson_unique_key_count_times_six
from src.python.pbm.pbm_parser import pbm_total_pixels_times_six, pbm_file_size_times_six
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_six, pgm_file_size_times_six
from src.python.ppm.ppm_parser import ppm_file_size_times_six, ppm_unique_pixel_count_times_six
from src.python.qoi.qoi_parser import qoi_pixel_count_times_six, qoi_file_size_times_six

# --- NDJSON (tmp_path fixtures) ---
def _ndjson_tmp(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in [{"a": 1}, {"a": 2, "b": 3}]) + "\n")
    return str(p)

class TestNdjsonRecordCountTimesSix:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_six(_ndjson_tmp(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_six(_ndjson_tmp(tmp_path)) >= 0
    def test_divisible_by_six(self, tmp_path):
        assert ndjson_record_count_times_six(_ndjson_tmp(tmp_path)) % 6 == 0

class TestNdjsonUniqueKeyCountTimesSix:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_unique_key_count_times_six(_ndjson_tmp(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_unique_key_count_times_six(_ndjson_tmp(tmp_path)) >= 0
    def test_divisible_by_six(self, tmp_path):
        assert ndjson_unique_key_count_times_six(_ndjson_tmp(tmp_path)) % 6 == 0

# --- PBM ---
class TestPbmTotalPixelsTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert isinstance(pbm_total_pixels_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_total_pixels_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_total_pixels_times_six(p) % 6 == 0

class TestPbmFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert isinstance(pbm_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_file_size_times_six(p) % 6 == 0

# --- PGM ---
class TestPgmTotalPixelCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert isinstance(pgm_total_pixel_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_total_pixel_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_total_pixel_count_times_six(p) % 6 == 0

class TestPgmFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert isinstance(pgm_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_file_size_times_six(p) % 6 == 0

# --- PPM ---
class TestPpmFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert isinstance(ppm_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_file_size_times_six(p) % 6 == 0

class TestPpmUniquePixelCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert isinstance(ppm_unique_pixel_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_unique_pixel_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_unique_pixel_count_times_six(p) % 6 == 0

# --- QOI ---
class TestQoiPixelCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert isinstance(qoi_pixel_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_pixel_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_pixel_count_times_six(p) % 6 == 0

class TestQoiFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert isinstance(qoi_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_file_size_times_six(p) % 6 == 0
