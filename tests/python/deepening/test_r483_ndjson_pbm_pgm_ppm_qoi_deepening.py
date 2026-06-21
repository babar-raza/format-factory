"""Sprint R483 — NDJSON/PBM/PGM/PPM/QOI _times_nine composite analytics tests."""
import json, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_record_count_times_nine, ndjson_unique_key_count_times_nine
from src.python.pbm.pbm_parser import pbm_total_pixels_times_nine, pbm_file_size_times_nine
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_nine, pgm_file_size_times_nine
from src.python.ppm.ppm_parser import ppm_file_size_times_nine, ppm_unique_pixel_count_times_nine
from src.python.qoi.qoi_parser import qoi_pixel_count_times_nine, qoi_file_size_times_nine

SAMPLES = _REPO / "samples" / "by-format"

def _ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in [{"a": 1}, {"a": 2, "b": 3}]) + "\n")
    return str(p)

class TestNdjsonRecordCountTimesNine:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_nine(_ndjson_file(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_nine(_ndjson_file(tmp_path)) >= 0
    def test_divisible(self, tmp_path):
        assert ndjson_record_count_times_nine(_ndjson_file(tmp_path)) % 9 == 0

class TestNdjsonUniqueKeyCountTimesNine:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_unique_key_count_times_nine(_ndjson_file(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_unique_key_count_times_nine(_ndjson_file(tmp_path)) >= 0
    def test_divisible(self, tmp_path):
        assert ndjson_unique_key_count_times_nine(_ndjson_file(tmp_path)) % 9 == 0

class TestPbmTotalPixelsTimesNine:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_nine(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_nine(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_nine(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) % 9 == 0

class TestPbmFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_times_nine(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")), int)
    def test_non_negative(self):
        assert pbm_file_size_times_nine(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) >= 0
    def test_divisible(self):
        assert pbm_file_size_times_nine(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) % 9 == 0

class TestPgmTotalPixelCountTimesNine:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_nine(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_nine(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_nine(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) % 9 == 0

class TestPgmFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_times_nine(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")), int)
    def test_non_negative(self):
        assert pgm_file_size_times_nine(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) >= 0
    def test_divisible(self):
        assert pgm_file_size_times_nine(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) % 9 == 0

class TestPpmFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_times_nine(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")), int)
    def test_non_negative(self):
        assert ppm_file_size_times_nine(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) >= 0
    def test_divisible(self):
        assert ppm_file_size_times_nine(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) % 9 == 0

class TestPpmUniquePixelCountTimesNine:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_nine(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_nine(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_nine(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) % 9 == 0

class TestQoiPixelCountTimesNine:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_nine(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_nine(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_nine(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) % 9 == 0

class TestQoiFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_times_nine(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")), int)
    def test_non_negative(self):
        assert qoi_file_size_times_nine(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) >= 0
    def test_divisible(self):
        assert qoi_file_size_times_nine(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) % 9 == 0
