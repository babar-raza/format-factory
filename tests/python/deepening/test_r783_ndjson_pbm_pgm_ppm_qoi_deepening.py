"""Sprint R783 — NDJSON/PBM/PGM/PPM/QOI _times_eighty_four composite analytics tests."""
import sys, pathlib, json
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ndjson.ndjson_codec import ndjson_record_count_times_eighty_four, ndjson_unique_key_count_times_eighty_four
from src.python.pbm.pbm_parser import pbm_total_pixels_times_eighty_four, pbm_file_size_bytes_times_eighty_four
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_eighty_four, pgm_file_size_bytes_times_eighty_four
from src.python.ppm.ppm_parser import ppm_file_size_bytes_times_eighty_four, ppm_unique_pixel_count_times_eighty_four
from src.python.qoi.qoi_parser import qoi_pixel_count_times_eighty_four, qoi_file_size_bytes_times_eighty_four
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

class TestNdjsonRecordCountTimesEightyFour:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_record_count_times_eighty_four(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_record_count_times_eighty_four(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_record_count_times_eighty_four(ndjson_file) % 84 == 0
class TestNdjsonUniqueKeyCountTimesEightyFour:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_unique_key_count_times_eighty_four(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_unique_key_count_times_eighty_four(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_unique_key_count_times_eighty_four(ndjson_file) % 84 == 0
class TestPbmTotalPixelsTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_eighty_four(_PBM), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_eighty_four(_PBM) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_eighty_four(_PBM) % 84 == 0
class TestPbmFileSizeBytesTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_bytes_times_eighty_four(_PBM), int)
    def test_non_negative(self):
        assert pbm_file_size_bytes_times_eighty_four(_PBM) >= 0
    def test_divisible(self):
        assert pbm_file_size_bytes_times_eighty_four(_PBM) % 84 == 0
class TestPgmTotalPixelCountTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_eighty_four(_PGM), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_eighty_four(_PGM) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_eighty_four(_PGM) % 84 == 0
class TestPgmFileSizeBytesTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_bytes_times_eighty_four(_PGM), int)
    def test_non_negative(self):
        assert pgm_file_size_bytes_times_eighty_four(_PGM) >= 0
    def test_divisible(self):
        assert pgm_file_size_bytes_times_eighty_four(_PGM) % 84 == 0
class TestPpmFileSizeBytesTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_bytes_times_eighty_four(_PPM), int)
    def test_non_negative(self):
        assert ppm_file_size_bytes_times_eighty_four(_PPM) >= 0
    def test_divisible(self):
        assert ppm_file_size_bytes_times_eighty_four(_PPM) % 84 == 0
class TestPpmUniquePixelCountTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_eighty_four(_PPM), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_eighty_four(_PPM) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_eighty_four(_PPM) % 84 == 0
class TestQoiPixelCountTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_eighty_four(_QOI), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_eighty_four(_QOI) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_eighty_four(_QOI) % 84 == 0
class TestQoiFileSizeBytesTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_bytes_times_eighty_four(_QOI), int)
    def test_non_negative(self):
        assert qoi_file_size_bytes_times_eighty_four(_QOI) >= 0
    def test_divisible(self):
        assert qoi_file_size_bytes_times_eighty_four(_QOI) % 84 == 0
