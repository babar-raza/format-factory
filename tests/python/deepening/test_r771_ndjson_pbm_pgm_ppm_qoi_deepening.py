"""Sprint R771 — NDJSON/PBM/PGM/PPM/QOI _times_eighty_one composite analytics tests."""
import sys, pathlib, json
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ndjson.ndjson_codec import ndjson_record_count_times_eighty_one, ndjson_unique_key_count_times_eighty_one
from src.python.pbm.pbm_parser import pbm_total_pixels_times_eighty_one, pbm_file_size_bytes_times_eighty_one
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_eighty_one, pgm_file_size_bytes_times_eighty_one
from src.python.ppm.ppm_parser import ppm_file_size_bytes_times_eighty_one, ppm_unique_pixel_count_times_eighty_one
from src.python.qoi.qoi_parser import qoi_pixel_count_times_eighty_one, qoi_file_size_bytes_times_eighty_one
SAMPLES = _REPO / "samples" / "by-format"
_PBM = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
_PGM = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
_PPM = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
_QOI = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")
import pytest
@pytest.fixture
def ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in [{"a": 1, "b": "x"}, {"a": 2, "c": "y"}]) + "\n")
    return str(p)

class TestNdjsonRecordCountTimesEightyOne:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_record_count_times_eighty_one(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_record_count_times_eighty_one(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_record_count_times_eighty_one(ndjson_file) % 81 == 0
class TestNdjsonUniqueKeyCountTimesEightyOne:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_unique_key_count_times_eighty_one(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_unique_key_count_times_eighty_one(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_unique_key_count_times_eighty_one(ndjson_file) % 81 == 0
class TestPbmTotalPixelsTimesEightyOne:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_eighty_one(_PBM), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_eighty_one(_PBM) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_eighty_one(_PBM) % 81 == 0
class TestPbmFileSizeBytesTimesEightyOne:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_bytes_times_eighty_one(_PBM), int)
    def test_non_negative(self):
        assert pbm_file_size_bytes_times_eighty_one(_PBM) >= 0
    def test_divisible(self):
        assert pbm_file_size_bytes_times_eighty_one(_PBM) % 81 == 0
class TestPgmTotalPixelCountTimesEightyOne:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_eighty_one(_PGM), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_eighty_one(_PGM) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_eighty_one(_PGM) % 81 == 0
class TestPgmFileSizeBytesTimesEightyOne:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_bytes_times_eighty_one(_PGM), int)
    def test_non_negative(self):
        assert pgm_file_size_bytes_times_eighty_one(_PGM) >= 0
    def test_divisible(self):
        assert pgm_file_size_bytes_times_eighty_one(_PGM) % 81 == 0
class TestPpmFileSizeBytesTimesEightyOne:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_bytes_times_eighty_one(_PPM), int)
    def test_non_negative(self):
        assert ppm_file_size_bytes_times_eighty_one(_PPM) >= 0
    def test_divisible(self):
        assert ppm_file_size_bytes_times_eighty_one(_PPM) % 81 == 0
class TestPpmUniquePixelCountTimesEightyOne:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_eighty_one(_PPM), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_eighty_one(_PPM) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_eighty_one(_PPM) % 81 == 0
class TestQoiPixelCountTimesEightyOne:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_eighty_one(_QOI), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_eighty_one(_QOI) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_eighty_one(_QOI) % 81 == 0
class TestQoiFileSizeBytesTimesEightyOne:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_bytes_times_eighty_one(_QOI), int)
    def test_non_negative(self):
        assert qoi_file_size_bytes_times_eighty_one(_QOI) >= 0
    def test_divisible(self):
        assert qoi_file_size_bytes_times_eighty_one(_QOI) % 81 == 0
