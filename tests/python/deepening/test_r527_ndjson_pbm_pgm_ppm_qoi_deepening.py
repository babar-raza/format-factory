"""Sprint R527 — NDJSON/PBM/PGM/PPM/QOI _times_twenty composite analytics tests."""
import sys, pathlib, json
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ndjson.ndjson_codec import ndjson_record_count_times_twenty, ndjson_unique_key_count_times_twenty
from src.python.pbm.pbm_parser import pbm_total_pixels_times_twenty, pbm_file_size_bytes_times_twenty
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_twenty, pgm_file_size_bytes_times_twenty
from src.python.ppm.ppm_parser import ppm_file_size_bytes_times_twenty, ppm_unique_pixel_count_times_twenty
from src.python.qoi.qoi_parser import qoi_pixel_count_times_twenty, qoi_file_size_bytes_times_twenty
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

class TestNdjsonRecordCountTimesTwenty:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_record_count_times_twenty(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_record_count_times_twenty(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_record_count_times_twenty(ndjson_file) % 20 == 0
class TestNdjsonUniqueKeyCountTimesTwenty:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_unique_key_count_times_twenty(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_unique_key_count_times_twenty(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_unique_key_count_times_twenty(ndjson_file) % 20 == 0
class TestPbmTotalPixelsTimesTwenty:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_twenty(_PBM), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_twenty(_PBM) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_twenty(_PBM) % 20 == 0
class TestPbmFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_bytes_times_twenty(_PBM), int)
    def test_non_negative(self):
        assert pbm_file_size_bytes_times_twenty(_PBM) >= 0
    def test_divisible(self):
        assert pbm_file_size_bytes_times_twenty(_PBM) % 20 == 0
class TestPgmTotalPixelCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_twenty(_PGM), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_twenty(_PGM) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_twenty(_PGM) % 20 == 0
class TestPgmFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_bytes_times_twenty(_PGM), int)
    def test_non_negative(self):
        assert pgm_file_size_bytes_times_twenty(_PGM) >= 0
    def test_divisible(self):
        assert pgm_file_size_bytes_times_twenty(_PGM) % 20 == 0
class TestPpmFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_bytes_times_twenty(_PPM), int)
    def test_non_negative(self):
        assert ppm_file_size_bytes_times_twenty(_PPM) >= 0
    def test_divisible(self):
        assert ppm_file_size_bytes_times_twenty(_PPM) % 20 == 0
class TestPpmUniquePixelCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_twenty(_PPM), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_twenty(_PPM) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_twenty(_PPM) % 20 == 0
class TestQoiPixelCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_twenty(_QOI), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_twenty(_QOI) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_twenty(_QOI) % 20 == 0
class TestQoiFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_bytes_times_twenty(_QOI), int)
    def test_non_negative(self):
        assert qoi_file_size_bytes_times_twenty(_QOI) >= 0
    def test_divisible(self):
        assert qoi_file_size_bytes_times_twenty(_QOI) % 20 == 0
