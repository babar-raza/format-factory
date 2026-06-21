"""Sprint R691 — NDJSON/PBM/PGM/PPM/QOI _times_sixty_one composite analytics tests."""
import sys, pathlib, json
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ndjson.ndjson_codec import ndjson_record_count_times_sixty_one, ndjson_unique_key_count_times_sixty_one
from src.python.pbm.pbm_parser import pbm_total_pixels_times_sixty_one, pbm_file_size_bytes_times_sixty_one
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_sixty_one, pgm_file_size_bytes_times_sixty_one
from src.python.ppm.ppm_parser import ppm_file_size_bytes_times_sixty_one, ppm_unique_pixel_count_times_sixty_one
from src.python.qoi.qoi_parser import qoi_pixel_count_times_sixty_one, qoi_file_size_bytes_times_sixty_one
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

class TestNdjsonRecordCountTimesSixtyOne:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_record_count_times_sixty_one(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_record_count_times_sixty_one(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_record_count_times_sixty_one(ndjson_file) % 61 == 0
class TestNdjsonUniqueKeyCountTimesSixtyOne:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_unique_key_count_times_sixty_one(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_unique_key_count_times_sixty_one(ndjson_file) >= 0
    def test_divisible(self, ndjson_file):
        assert ndjson_unique_key_count_times_sixty_one(ndjson_file) % 61 == 0
class TestPbmTotalPixelsTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_sixty_one(_PBM), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_sixty_one(_PBM) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_sixty_one(_PBM) % 61 == 0
class TestPbmFileSizeBytesTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_bytes_times_sixty_one(_PBM), int)
    def test_non_negative(self):
        assert pbm_file_size_bytes_times_sixty_one(_PBM) >= 0
    def test_divisible(self):
        assert pbm_file_size_bytes_times_sixty_one(_PBM) % 61 == 0
class TestPgmTotalPixelCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_sixty_one(_PGM), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_sixty_one(_PGM) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_sixty_one(_PGM) % 61 == 0
class TestPgmFileSizeBytesTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_bytes_times_sixty_one(_PGM), int)
    def test_non_negative(self):
        assert pgm_file_size_bytes_times_sixty_one(_PGM) >= 0
    def test_divisible(self):
        assert pgm_file_size_bytes_times_sixty_one(_PGM) % 61 == 0
class TestPpmFileSizeBytesTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_bytes_times_sixty_one(_PPM), int)
    def test_non_negative(self):
        assert ppm_file_size_bytes_times_sixty_one(_PPM) >= 0
    def test_divisible(self):
        assert ppm_file_size_bytes_times_sixty_one(_PPM) % 61 == 0
class TestPpmUniquePixelCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_sixty_one(_PPM), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_sixty_one(_PPM) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_sixty_one(_PPM) % 61 == 0
class TestQoiPixelCountTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_sixty_one(_QOI), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_sixty_one(_QOI) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_sixty_one(_QOI) % 61 == 0
class TestQoiFileSizeBytesTimesSixtyOne:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_bytes_times_sixty_one(_QOI), int)
    def test_non_negative(self):
        assert qoi_file_size_bytes_times_sixty_one(_QOI) >= 0
    def test_divisible(self):
        assert qoi_file_size_bytes_times_sixty_one(_QOI) % 61 == 0
