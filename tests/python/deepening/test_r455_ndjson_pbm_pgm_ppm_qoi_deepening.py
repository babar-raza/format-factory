"""Sprint R455 — NDJSON/PBM/PGM/PPM/QOI round 10 deepening tests."""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_total_value_count_times_three, ndjson_unique_key_count_times_three, ndjson_total_value_count, ndjson_unique_key_count
from src.python.pbm import pbm_file_size_times_three, pbm_total_pixels_times_three, pbm_file_size_bytes, pbm_total_pixels
from src.python.pgm import pgm_file_size_times_three, pgm_total_pixel_count_times_three, pgm_file_size_bytes, pgm_total_pixel_count
from src.python.ppm import ppm_file_size_times_three, ppm_unique_pixel_count_times_three, ppm_file_size_bytes, ppm_unique_pixel_count
from src.python.qoi import qoi_file_size_times_three, qoi_pixel_count_times_three, qoi_file_size_bytes, qoi_pixel_count

SAMPLES = _REPO / "samples" / "by-format"
PBM_SAMPLE = SAMPLES / "pbm" / "valid" / "1x1-black.pbm"
PGM_SAMPLE = SAMPLES / "pgm" / "valid" / "1x1-white.pgm"
PPM_SAMPLE = SAMPLES / "ppm" / "valid" / "1x1-red.ppm"
QOI_SAMPLE = SAMPLES / "qoi" / "valid" / "1x1-red.qoi"


def _ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]) + "\n")
    return p


class TestNdjsonTotalValueCountTimesThree:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_total_value_count_times_three(_ndjson_file(tmp_path)), int)
    def test_is_triple(self, tmp_path):
        f = _ndjson_file(tmp_path)
        assert ndjson_total_value_count_times_three(f) == ndjson_total_value_count(f) * 3
    def test_non_negative(self, tmp_path):
        assert ndjson_total_value_count_times_three(_ndjson_file(tmp_path)) >= 0


class TestNdjsonUniqueKeyCountTimesThree:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_unique_key_count_times_three(_ndjson_file(tmp_path)), int)
    def test_is_triple(self, tmp_path):
        f = _ndjson_file(tmp_path)
        assert ndjson_unique_key_count_times_three(f) == ndjson_unique_key_count(f) * 3
    def test_non_negative(self, tmp_path):
        assert ndjson_unique_key_count_times_three(_ndjson_file(tmp_path)) >= 0


class TestPbmFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_times_three(PBM_SAMPLE), int)
    def test_is_triple(self):
        assert pbm_file_size_times_three(PBM_SAMPLE) == pbm_file_size_bytes(PBM_SAMPLE) * 3
    def test_non_negative(self):
        assert pbm_file_size_times_three(PBM_SAMPLE) >= 0


class TestPbmTotalPixelsTimesThree:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_three(PBM_SAMPLE), int)
    def test_is_triple(self):
        assert pbm_total_pixels_times_three(PBM_SAMPLE) == pbm_total_pixels(PBM_SAMPLE) * 3
    def test_non_negative(self):
        assert pbm_total_pixels_times_three(PBM_SAMPLE) >= 0


class TestPgmFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_times_three(PGM_SAMPLE), int)
    def test_is_triple(self):
        assert pgm_file_size_times_three(PGM_SAMPLE) == pgm_file_size_bytes(PGM_SAMPLE) * 3
    def test_non_negative(self):
        assert pgm_file_size_times_three(PGM_SAMPLE) >= 0


class TestPgmTotalPixelCountTimesThree:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_three(PGM_SAMPLE), int)
    def test_is_triple(self):
        assert pgm_total_pixel_count_times_three(PGM_SAMPLE) == pgm_total_pixel_count(PGM_SAMPLE) * 3
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_three(PGM_SAMPLE) >= 0


class TestPpmFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_times_three(PPM_SAMPLE), int)
    def test_is_triple(self):
        assert ppm_file_size_times_three(PPM_SAMPLE) == ppm_file_size_bytes(PPM_SAMPLE) * 3
    def test_non_negative(self):
        assert ppm_file_size_times_three(PPM_SAMPLE) >= 0


class TestPpmUniquePixelCountTimesThree:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_three(PPM_SAMPLE), int)
    def test_is_triple(self):
        assert ppm_unique_pixel_count_times_three(PPM_SAMPLE) == ppm_unique_pixel_count(PPM_SAMPLE) * 3
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_three(PPM_SAMPLE) >= 0


class TestQoiFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_times_three(QOI_SAMPLE), int)
    def test_is_triple(self):
        assert qoi_file_size_times_three(QOI_SAMPLE) == qoi_file_size_bytes(QOI_SAMPLE) * 3
    def test_non_negative(self):
        assert qoi_file_size_times_three(QOI_SAMPLE) >= 0


class TestQoiPixelCountTimesThree:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_three(QOI_SAMPLE), int)
    def test_is_triple(self):
        assert qoi_pixel_count_times_three(QOI_SAMPLE) == qoi_pixel_count(QOI_SAMPLE) * 3
    def test_non_negative(self):
        assert qoi_pixel_count_times_three(QOI_SAMPLE) >= 0
