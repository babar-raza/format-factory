"""Sprint R487 — NDJSON/PBM/PGM/PPM/QOI _times_ten composite analytics tests."""
import json, sys, pathlib, tempfile

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_record_count_times_ten, ndjson_unique_key_count_times_ten
from src.python.pbm.pbm_parser import pbm_total_pixels_times_ten, pbm_file_size_times_ten
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_ten, pgm_file_size_times_ten
from src.python.ppm.ppm_parser import ppm_file_size_times_ten, ppm_unique_pixel_count_times_ten
from src.python.qoi.qoi_parser import qoi_pixel_count_times_ten, qoi_file_size_times_ten

SAMPLES = _REPO / "samples" / "by-format"

def _ndjson_tmp(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join([json.dumps({"a": 1, "b": "x"}), json.dumps({"a": 2, "b": "y"})]) + "\n")
    return str(p)

class TestNdjsonRecordCountTimesTen:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_ten(_ndjson_tmp(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_ten(_ndjson_tmp(tmp_path)) >= 0
    def test_divisible(self, tmp_path):
        assert ndjson_record_count_times_ten(_ndjson_tmp(tmp_path)) % 10 == 0

class TestNdjsonUniqueKeyCountTimesTen:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_unique_key_count_times_ten(_ndjson_tmp(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_unique_key_count_times_ten(_ndjson_tmp(tmp_path)) >= 0
    def test_divisible(self, tmp_path):
        assert ndjson_unique_key_count_times_ten(_ndjson_tmp(tmp_path)) % 10 == 0

class TestPbmTotalPixelsTimesTen:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_ten(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_ten(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_ten(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) % 10 == 0

class TestPbmFileSizeTimesTen:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_times_ten(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")), int)
    def test_non_negative(self):
        assert pbm_file_size_times_ten(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) >= 0
    def test_divisible(self):
        assert pbm_file_size_times_ten(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) % 10 == 0

class TestPgmTotalPixelCountTimesTen:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_ten(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_ten(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_ten(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) % 10 == 0

class TestPgmFileSizeTimesTen:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_times_ten(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")), int)
    def test_non_negative(self):
        assert pgm_file_size_times_ten(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) >= 0
    def test_divisible(self):
        assert pgm_file_size_times_ten(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) % 10 == 0

class TestPpmFileSizeTimesTen:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_times_ten(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")), int)
    def test_non_negative(self):
        assert ppm_file_size_times_ten(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) >= 0
    def test_divisible(self):
        assert ppm_file_size_times_ten(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) % 10 == 0

class TestPpmUniquePixelCountTimesTen:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_ten(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_ten(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_ten(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) % 10 == 0

class TestQoiPixelCountTimesTen:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_ten(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_ten(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_ten(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) % 10 == 0

class TestQoiFileSizeTimesTen:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_times_ten(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")), int)
    def test_non_negative(self):
        assert qoi_file_size_times_ten(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) >= 0
    def test_divisible(self):
        assert qoi_file_size_times_ten(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) % 10 == 0
