"""Sprint R479 — NDJSON/PBM/PGM/PPM/QOI _times_eight composite analytics tests."""
import json, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_record_count_times_eight, ndjson_unique_key_count_times_eight
from src.python.pbm.pbm_parser import pbm_total_pixels_times_eight, pbm_file_size_times_eight
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_eight, pgm_file_size_times_eight
from src.python.ppm.ppm_parser import ppm_file_size_times_eight, ppm_unique_pixel_count_times_eight
from src.python.qoi.qoi_parser import qoi_pixel_count_times_eight, qoi_file_size_times_eight

SAMPLES = _REPO / "samples" / "by-format"

def _ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in [{"a": 1}, {"a": 2, "b": 3}]) + "\n")
    return str(p)

# --- NDJSON ---
class TestNdjsonRecordCountTimesEight:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_eight(_ndjson_file(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_eight(_ndjson_file(tmp_path)) >= 0
    def test_divisible(self, tmp_path):
        assert ndjson_record_count_times_eight(_ndjson_file(tmp_path)) % 8 == 0

class TestNdjsonUniqueKeyCountTimesEight:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_unique_key_count_times_eight(_ndjson_file(tmp_path)), int)
    def test_non_negative(self, tmp_path):
        assert ndjson_unique_key_count_times_eight(_ndjson_file(tmp_path)) >= 0
    def test_divisible(self, tmp_path):
        assert ndjson_unique_key_count_times_eight(_ndjson_file(tmp_path)) % 8 == 0

# --- PBM ---
class TestPbmTotalPixelsTimesEight:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_eight(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_eight(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) >= 0
    def test_divisible(self):
        assert pbm_total_pixels_times_eight(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) % 8 == 0

class TestPbmFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_times_eight(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")), int)
    def test_non_negative(self):
        assert pbm_file_size_times_eight(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) >= 0
    def test_divisible(self):
        assert pbm_file_size_times_eight(str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")) % 8 == 0

# --- PGM ---
class TestPgmTotalPixelCountTimesEight:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_eight(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_eight(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) >= 0
    def test_divisible(self):
        assert pgm_total_pixel_count_times_eight(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) % 8 == 0

class TestPgmFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_times_eight(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")), int)
    def test_non_negative(self):
        assert pgm_file_size_times_eight(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) >= 0
    def test_divisible(self):
        assert pgm_file_size_times_eight(str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")) % 8 == 0

# --- PPM ---
class TestPpmFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_times_eight(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")), int)
    def test_non_negative(self):
        assert ppm_file_size_times_eight(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) >= 0
    def test_divisible(self):
        assert ppm_file_size_times_eight(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) % 8 == 0

class TestPpmUniquePixelCountTimesEight:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_eight(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_eight(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) >= 0
    def test_divisible(self):
        assert ppm_unique_pixel_count_times_eight(str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")) % 8 == 0

# --- QOI ---
class TestQoiPixelCountTimesEight:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_eight(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")), int)
    def test_non_negative(self):
        assert qoi_pixel_count_times_eight(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) >= 0
    def test_divisible(self):
        assert qoi_pixel_count_times_eight(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) % 8 == 0

class TestQoiFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_times_eight(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")), int)
    def test_non_negative(self):
        assert qoi_file_size_times_eight(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) >= 0
    def test_divisible(self):
        assert qoi_file_size_times_eight(str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")) % 8 == 0
