"""Sprint R491 — NDJSON/PBM/PGM/PPM/QOI _times_eleven composite analytics tests."""
import json
import sys
import pathlib
import tempfile

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import ndjson_record_count_times_eleven, ndjson_unique_key_count_times_eleven
from src.python.pbm.pbm_parser import pbm_total_pixels_times_eleven, pbm_file_size_bytes_times_eleven
from src.python.pgm.pgm_parser import pgm_total_pixel_count_times_eleven, pgm_file_size_bytes_times_eleven
from src.python.ppm.ppm_parser import ppm_file_size_bytes_times_eleven, ppm_unique_pixel_count_times_eleven
from src.python.qoi.qoi_parser import qoi_pixel_count_times_eleven, qoi_file_size_bytes_times_eleven

SAMPLES = _REPO / "samples" / "by-format"
_PBM = str(SAMPLES / "pbm" / "valid" / "1x1-black.pbm")
_PGM = str(SAMPLES / "pgm" / "valid" / "1x1-white.pgm")
_PPM = str(SAMPLES / "ppm" / "valid" / "1x1-red.ppm")
_QOI = str(SAMPLES / "qoi" / "valid" / "1x1-red.qoi")


def _ndjson_tmp(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join([json.dumps({"a": 1, "b": "x"}), json.dumps({"a": 2, "b": "y"})]) + "\n")
    return str(p)


class TestNdjsonRecordCountTimesEleven:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_eleven(_ndjson_tmp(tmp_path)), int)

    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_eleven(_ndjson_tmp(tmp_path)) >= 0

    def test_divisible(self, tmp_path):
        assert ndjson_record_count_times_eleven(_ndjson_tmp(tmp_path)) % 11 == 0


class TestNdjsonUniqueKeyCountTimesEleven:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_unique_key_count_times_eleven(_ndjson_tmp(tmp_path)), int)

    def test_non_negative(self, tmp_path):
        assert ndjson_unique_key_count_times_eleven(_ndjson_tmp(tmp_path)) >= 0

    def test_divisible(self, tmp_path):
        assert ndjson_unique_key_count_times_eleven(_ndjson_tmp(tmp_path)) % 11 == 0


class TestPbmTotalPixelsTimesEleven:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_eleven(_PBM), int)

    def test_non_negative(self):
        assert pbm_total_pixels_times_eleven(_PBM) >= 0

    def test_divisible(self):
        assert pbm_total_pixels_times_eleven(_PBM) % 11 == 0


class TestPbmFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_bytes_times_eleven(_PBM), int)

    def test_non_negative(self):
        assert pbm_file_size_bytes_times_eleven(_PBM) >= 0

    def test_divisible(self):
        assert pbm_file_size_bytes_times_eleven(_PBM) % 11 == 0


class TestPgmTotalPixelCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_eleven(_PGM), int)

    def test_non_negative(self):
        assert pgm_total_pixel_count_times_eleven(_PGM) >= 0

    def test_divisible(self):
        assert pgm_total_pixel_count_times_eleven(_PGM) % 11 == 0


class TestPgmFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_bytes_times_eleven(_PGM), int)

    def test_non_negative(self):
        assert pgm_file_size_bytes_times_eleven(_PGM) >= 0

    def test_divisible(self):
        assert pgm_file_size_bytes_times_eleven(_PGM) % 11 == 0


class TestPpmFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_bytes_times_eleven(_PPM), int)

    def test_non_negative(self):
        assert ppm_file_size_bytes_times_eleven(_PPM) >= 0

    def test_divisible(self):
        assert ppm_file_size_bytes_times_eleven(_PPM) % 11 == 0


class TestPpmUniquePixelCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_eleven(_PPM), int)

    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_eleven(_PPM) >= 0

    def test_divisible(self):
        assert ppm_unique_pixel_count_times_eleven(_PPM) % 11 == 0


class TestQoiPixelCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_times_eleven(_QOI), int)

    def test_non_negative(self):
        assert qoi_pixel_count_times_eleven(_QOI) >= 0

    def test_divisible(self):
        assert qoi_pixel_count_times_eleven(_QOI) % 11 == 0


class TestQoiFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_bytes_times_eleven(_QOI), int)

    def test_non_negative(self):
        assert qoi_file_size_bytes_times_eleven(_QOI) >= 0

    def test_divisible(self):
        assert qoi_file_size_bytes_times_eleven(_QOI) % 11 == 0
