"""Sprint R679 — NDJSON/PBM/PGM/PPM/QOI _times_fifty_eight composite analytics tests."""
import sys, pathlib, json
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ndjson.ndjson_codec import ndjson_record_count_times_fifty_eight, ndjson_unique_key_count_times_fifty_eight
from src.python.pbm.pbm_parser import pbm_total_pixels_times_fifty_eight, pbm_file_size_bytes_times_fifty_eight
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_fifty_eight, pgm_file_size_bytes_times_fifty_eight
from src.python.ppm.ppm_parser import ppm_file_size_bytes_times_fifty_eight, ppm_unique_pixel_count_times_fifty_eight
from src.python.qoi.qoi_parser import qoi_pixel_count_times_fifty_eight, qoi_file_size_bytes_times_fifty_eight
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

class TestNdjsonRecordCountTimesFiftyEight:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_record_count_times_fifty_eight(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_record_count_times_fifty_eight(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_record_count_times_fifty_eight(ndjson_file) % 58 == 0
class TestNdjsonUniqueKeyCountTimesFiftyEight:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_unique_key_count_times_fifty_eight(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_unique_key_count_times_fifty_eight(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_unique_key_count_times_fifty_eight(ndjson_file) % 58 == 0
class TestPbmTotalPixelsTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_fifty_eight(_PBM), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_fifty_eight(_PBM) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_fifty_eight(_PBM) % 58 == 0
class TestPbmFileSizeBytesTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_bytes_times_fifty_eight(_PBM), int)
    def test_non_negative(self):
        assert pbm_file_size_bytes_times_fifty_eight(_PBM) >= 0
    def test_divisible(self):
        assert pbm_file_size_bytes_times_fifty_eight(_PBM) % 58 == 0
class TestPgmTotalPixelCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_fifty_eight(_PGM), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_fifty_eight(_PGM) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_fifty_eight(_PGM) % 58 == 0
class TestPgmFileSizeBytesTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_bytes_times_fifty_eight(_PGM), int)
    def test_non_negative(self):
        assert pgm_file_size_bytes_times_fifty_eight(_PGM) >= 0
    def test_divisible(self):
        assert pgm_file_size_bytes_times_fifty_eight(_PGM) % 58 == 0
class TestPpmFileSizeBytesTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_bytes_times_fifty_eight(_PPM), int)
    def test_non_negative(self):
        assert ppm_file_size_bytes_times_fifty_eight(_PPM) >= 0
    def test_divisible(self):
        assert ppm_file_size_bytes_times_fifty_eight(_PPM) % 58 == 0
class TestPpmUniquePixelCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_fifty_eight(_PPM), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_fifty_eight(_PPM) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_fifty_eight(_PPM) % 58 == 0
class TestQoiPixelCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_fifty_eight(_QOI), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_fifty_eight(_QOI) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_fifty_eight(_QOI) % 58 == 0
class TestQoiFileSizeBytesTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_bytes_times_fifty_eight(_QOI), int)
    def test_non_negative(self):
        assert qoi_file_size_bytes_times_fifty_eight(_QOI) >= 0
    def test_divisible(self):
        assert qoi_file_size_bytes_times_fifty_eight(_QOI) % 58 == 0
