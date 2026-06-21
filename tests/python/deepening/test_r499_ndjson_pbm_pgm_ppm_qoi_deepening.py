"""Sprint R499 — NDJSON/PBM/PGM/PPM/QOI _times_thirteen composite analytics tests."""
import json, sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ndjson.ndjson_codec import ndjson_record_count_times_thirteen, ndjson_unique_key_count_times_thirteen
from src.python.pbm.pbm_parser import pbm_total_pixels_times_thirteen, pbm_file_size_bytes_times_thirteen
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_thirteen, pgm_file_size_bytes_times_thirteen
from src.python.ppm.ppm_parser import ppm_file_size_bytes_times_thirteen, ppm_unique_pixel_count_times_thirteen
from src.python.qoi.qoi_parser import qoi_pixel_count_times_thirteen, qoi_file_size_bytes_times_thirteen
SAMPLES = _REPO / "samples" / "by-format"
_PBM = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
_PGM = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
_PPM = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
_QOI = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
def _ndjson_tmp(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join([json.dumps({"a": 1, "b": "x"}), json.dumps({"a": 2, "b": "y"})]) + "\n")
    return str(p)

class TestNdjsonRecordCountTimesThirteen:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_thirteen(_ndjson_tmp(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_thirteen(_ndjson_tmp(tmp_path)) >= 0
    def test_divisible(self, tmp_path):
        assert ndjson_record_count_times_thirteen(_ndjson_tmp(tmp_path)) % 13 == 0

class TestNdjsonUniqueKeyCountTimesThirteen:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_unique_key_count_times_thirteen(_ndjson_tmp(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_unique_key_count_times_thirteen(_ndjson_tmp(tmp_path)) >= 0
    def test_divisible(self, tmp_path):
        assert ndjson_unique_key_count_times_thirteen(_ndjson_tmp(tmp_path)) % 13 == 0

class TestPbmTotalPixelsTimesThirteen:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_thirteen(_PBM), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_thirteen(_PBM) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_thirteen(_PBM) % 13 == 0

class TestPbmFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_bytes_times_thirteen(_PBM), int)
    def test_non_negative(self):
        assert pbm_file_size_bytes_times_thirteen(_PBM) >= 0
    def test_divisible(self):
        assert pbm_file_size_bytes_times_thirteen(_PBM) % 13 == 0

class TestPgmTotalPixelCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_thirteen(_PGM), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_thirteen(_PGM) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_thirteen(_PGM) % 13 == 0

class TestPgmFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_bytes_times_thirteen(_PGM), int)
    def test_non_negative(self):
        assert pgm_file_size_bytes_times_thirteen(_PGM) >= 0
    def test_divisible(self):
        assert pgm_file_size_bytes_times_thirteen(_PGM) % 13 == 0

class TestPpmFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_bytes_times_thirteen(_PPM), int)
    def test_non_negative(self):
        assert ppm_file_size_bytes_times_thirteen(_PPM) >= 0
    def test_divisible(self):
        assert ppm_file_size_bytes_times_thirteen(_PPM) % 13 == 0

class TestPpmUniquePixelCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_thirteen(_PPM), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_thirteen(_PPM) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_thirteen(_PPM) % 13 == 0

class TestQoiPixelCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_thirteen(_QOI), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_thirteen(_QOI) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_thirteen(_QOI) % 13 == 0

class TestQoiFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_bytes_times_thirteen(_QOI), int)
    def test_non_negative(self):
        assert qoi_file_size_bytes_times_thirteen(_QOI) >= 0
    def test_divisible(self):
        assert qoi_file_size_bytes_times_thirteen(_QOI) % 13 == 0
