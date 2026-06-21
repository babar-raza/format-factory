"""Sprint R475 — NDJSON/PBM/PGM/PPM/QOI _times_seven composite analytics tests."""
import json, pathlib, sys

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.ndjson.ndjson_codec import ndjson_record_count_times_seven, ndjson_unique_key_count_times_seven
from src.python.pbm.pbm_parser import pbm_total_pixels_times_seven, pbm_file_size_times_seven
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_seven, pgm_file_size_times_seven
from src.python.ppm.ppm_parser import ppm_file_size_times_seven, ppm_unique_pixel_count_times_seven
from src.python.qoi.qoi_parser import qoi_pixel_count_times_seven, qoi_file_size_times_seven

def _ndjson_tmp(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in [{"a": 1}, {"a": 2, "b": 3}]) + "\n")
    return str(p)

class TestNdjsonRecordCountTimesSeven:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_seven(_ndjson_tmp(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_seven(_ndjson_tmp(tmp_path)) >= 0
    def test_divisible_by_seven(self, tmp_path):
        assert ndjson_record_count_times_seven(_ndjson_tmp(tmp_path)) % 7 == 0

class TestNdjsonUniqueKeyCountTimesSeven:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_unique_key_count_times_seven(_ndjson_tmp(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_unique_key_count_times_seven(_ndjson_tmp(tmp_path)) >= 0
    def test_divisible_by_seven(self, tmp_path):
        assert ndjson_unique_key_count_times_seven(_ndjson_tmp(tmp_path)) % 7 == 0

class TestPbmTotalPixelsTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert isinstance(pbm_total_pixels_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_total_pixels_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_total_pixels_times_seven(p) % 7 == 0

class TestPbmFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert isinstance(pbm_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
        assert pbm_file_size_times_seven(p) % 7 == 0

class TestPgmTotalPixelCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert isinstance(pgm_total_pixel_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_total_pixel_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_total_pixel_count_times_seven(p) % 7 == 0

class TestPgmFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert isinstance(pgm_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
        assert pgm_file_size_times_seven(p) % 7 == 0

class TestPpmFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert isinstance(ppm_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_file_size_times_seven(p) % 7 == 0

class TestPpmUniquePixelCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert isinstance(ppm_unique_pixel_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_unique_pixel_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
        assert ppm_unique_pixel_count_times_seven(p) % 7 == 0

class TestQoiPixelCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert isinstance(qoi_pixel_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_pixel_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_pixel_count_times_seven(p) % 7 == 0

class TestQoiFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert isinstance(qoi_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
        assert qoi_file_size_times_seven(p) % 7 == 0
