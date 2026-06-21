"""Sprint R447 — NDJSON/PBM/PGM/PPM/QOI round 8 deepening tests."""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_file_size_times_two, ndjson_unique_key_count_squared, ndjson_file_size_bytes, ndjson_unique_key_count
from src.python.pbm import pbm_file_size_times_two, pbm_transition_count_squared, pbm_file_size_bytes, pbm_transition_count
from src.python.pgm import pgm_file_size_times_two, pgm_dark_pixel_count_squared, pgm_file_size_bytes, pgm_dark_pixel_count
from src.python.ppm import ppm_file_size_times_two, ppm_red_dominant_count_squared, ppm_file_size_bytes, ppm_red_dominant_count
from src.python.qoi import qoi_file_size_times_two, qoi_height_squared, qoi_file_size_bytes, qoi_height

SAMPLES = _REPO / "samples" / "by-format"
PBM_SAMPLE = SAMPLES / "pbm" / "valid" / "1x1-black.pbm"
PGM_SAMPLE = SAMPLES / "pgm" / "valid" / "1x1-white.pgm"
PPM_SAMPLE = SAMPLES / "ppm" / "valid" / "1x1-red.ppm"
QOI_SAMPLE = SAMPLES / "qoi" / "valid" / "1x1-red.qoi"


def _ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text(json.dumps({"a": 1, "b": "x"}) + "\n" + json.dumps({"a": 2, "c": True}) + "\n")
    return p


# --- NDJSON: ndjson_file_size_times_two ---
class TestNdjsonFileSizeTimesTwo:
    def test_returns_int(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert isinstance(ndjson_file_size_times_two(p), int)

    def test_is_double_file_size(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert ndjson_file_size_times_two(p) == ndjson_file_size_bytes(p) * 2

    def test_positive(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert ndjson_file_size_times_two(p) > 0


# --- NDJSON: ndjson_unique_key_count_squared ---
class TestNdjsonUniqueKeyCountSquared:
    def test_returns_int(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert isinstance(ndjson_unique_key_count_squared(p), int)

    def test_is_square(self, tmp_path):
        p = _ndjson_file(tmp_path)
        uk = ndjson_unique_key_count(p)
        assert ndjson_unique_key_count_squared(p) == uk * uk

    def test_non_negative(self, tmp_path):
        p = _ndjson_file(tmp_path)
        assert ndjson_unique_key_count_squared(p) >= 0


# --- PBM: pbm_file_size_times_two ---
class TestPbmFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_times_two(PBM_SAMPLE), int)

    def test_is_double_file_size(self):
        assert pbm_file_size_times_two(PBM_SAMPLE) == pbm_file_size_bytes(PBM_SAMPLE) * 2

    def test_positive(self):
        assert pbm_file_size_times_two(PBM_SAMPLE) > 0


# --- PBM: pbm_transition_count_squared ---
class TestPbmTransitionCountSquared:
    def test_returns_int(self):
        assert isinstance(pbm_transition_count_squared(PBM_SAMPLE), int)

    def test_is_square(self):
        tc = pbm_transition_count(PBM_SAMPLE)
        assert pbm_transition_count_squared(PBM_SAMPLE) == tc * tc

    def test_non_negative(self):
        assert pbm_transition_count_squared(PBM_SAMPLE) >= 0


# --- PGM: pgm_file_size_times_two ---
class TestPgmFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_times_two(PGM_SAMPLE), int)

    def test_is_double_file_size(self):
        assert pgm_file_size_times_two(PGM_SAMPLE) == pgm_file_size_bytes(PGM_SAMPLE) * 2

    def test_positive(self):
        assert pgm_file_size_times_two(PGM_SAMPLE) > 0


# --- PGM: pgm_dark_pixel_count_squared ---
class TestPgmDarkPixelCountSquared:
    def test_returns_int(self):
        assert isinstance(pgm_dark_pixel_count_squared(PGM_SAMPLE), int)

    def test_is_square(self):
        dp = pgm_dark_pixel_count(PGM_SAMPLE)
        assert pgm_dark_pixel_count_squared(PGM_SAMPLE) == dp * dp

    def test_non_negative(self):
        assert pgm_dark_pixel_count_squared(PGM_SAMPLE) >= 0


# --- PPM: ppm_file_size_times_two ---
class TestPpmFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_times_two(PPM_SAMPLE), int)

    def test_is_double_file_size(self):
        assert ppm_file_size_times_two(PPM_SAMPLE) == ppm_file_size_bytes(PPM_SAMPLE) * 2

    def test_positive(self):
        assert ppm_file_size_times_two(PPM_SAMPLE) > 0


# --- PPM: ppm_red_dominant_count_squared ---
class TestPpmRedDominantCountSquared:
    def test_returns_int(self):
        assert isinstance(ppm_red_dominant_count_squared(PPM_SAMPLE), int)

    def test_is_square(self):
        rd = ppm_red_dominant_count(PPM_SAMPLE)
        assert ppm_red_dominant_count_squared(PPM_SAMPLE) == rd * rd

    def test_non_negative(self):
        assert ppm_red_dominant_count_squared(PPM_SAMPLE) >= 0


# --- QOI: qoi_file_size_times_two ---
class TestQoiFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(qoi_file_size_times_two(QOI_SAMPLE), int)

    def test_is_double_file_size(self):
        assert qoi_file_size_times_two(QOI_SAMPLE) == qoi_file_size_bytes(QOI_SAMPLE) * 2

    def test_positive(self):
        assert qoi_file_size_times_two(QOI_SAMPLE) > 0


# --- QOI: qoi_height_squared ---
class TestQoiHeightSquared:
    def test_returns_int(self):
        assert isinstance(qoi_height_squared(QOI_SAMPLE), int)

    def test_is_square(self):
        h = qoi_height(QOI_SAMPLE)
        assert qoi_height_squared(QOI_SAMPLE) == h * h

    def test_positive(self):
        assert qoi_height_squared(QOI_SAMPLE) > 0
