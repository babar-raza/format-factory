"""Sprint R439 — NDJSON/PBM/PGM/PPM/QOI deepening round 6.

Functions under test (10 total, 2 per format):
  NDJSON: ndjson_null_field_count_squared, ndjson_unique_key_count_times_two
  PBM:    pbm_width_times_two, pbm_file_size_squared
  PGM:    pgm_width_times_two, pgm_file_size_squared
  PPM:    ppm_width_times_two, ppm_file_size_squared
  QOI:    qoi_width_times_two, qoi_pixel_count_squared
"""
import json, pathlib, sys, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# --- sample paths ---
_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "1x1-black.pbm"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "1x1-white.pgm"
_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "1x1-red.ppm"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi"

# ── NDJSON (tmp_path fixtures) ───────────────────────────────────────
from src.python.ndjson.ndjson_codec import (
    ndjson_null_field_count,
    ndjson_unique_key_count,
    ndjson_null_field_count_squared,
    ndjson_unique_key_count_times_two,
)

@pytest.fixture
def ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text(
        json.dumps({"a": 1, "b": None, "c": "x"}) + "\n"
        + json.dumps({"a": None, "b": 2, "c": None}) + "\n"
    )
    return p

class TestNdjsonNullFieldCountSquared:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_null_field_count_squared(ndjson_file), int)
    def test_square_of_base(self, ndjson_file):
        nc = ndjson_null_field_count(ndjson_file)
        assert ndjson_null_field_count_squared(ndjson_file) == nc * nc
    def test_non_negative(self, ndjson_file):
        assert ndjson_null_field_count_squared(ndjson_file) >= 0

class TestNdjsonUniqueKeyCountTimesTwo:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_unique_key_count_times_two(ndjson_file), int)
    def test_double_of_base(self, ndjson_file):
        assert ndjson_unique_key_count_times_two(ndjson_file) == ndjson_unique_key_count(ndjson_file) * 2
    def test_positive(self, ndjson_file):
        assert ndjson_unique_key_count_times_two(ndjson_file) > 0

# ── PBM ──────────────────────────────────────────────────────────────
from src.python.pbm.pbm_parser import (
    parse_pbm_strict,
    pbm_file_size_bytes,
    pbm_width_times_two,
    pbm_file_size_squared,
)

class TestPbmWidthTimesTwo:
    def test_returns_int(self):
        assert isinstance(pbm_width_times_two(_PBM), int)
    def test_double_of_base(self):
        assert pbm_width_times_two(_PBM) == parse_pbm_strict(_PBM).width * 2
    def test_positive(self):
        assert pbm_width_times_two(_PBM) > 0

class TestPbmFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_squared(_PBM), int)
    def test_square_of_base(self):
        fs = pbm_file_size_bytes(_PBM)
        assert pbm_file_size_squared(_PBM) == fs * fs
    def test_positive(self):
        assert pbm_file_size_squared(_PBM) > 0

# ── PGM ──────────────────────────────────────────────────────────────
from src.python.pgm.pgm_parser import (
    parse_pgm_strict,
    pgm_file_size_bytes,
    pgm_width_times_two,
    pgm_file_size_squared,
)

class TestPgmWidthTimesTwo:
    def test_returns_int(self):
        assert isinstance(pgm_width_times_two(_PGM), int)
    def test_double_of_base(self):
        assert pgm_width_times_two(_PGM) == parse_pgm_strict(_PGM).width * 2
    def test_positive(self):
        assert pgm_width_times_two(_PGM) > 0

class TestPgmFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_squared(_PGM), int)
    def test_square_of_base(self):
        fs = pgm_file_size_bytes(_PGM)
        assert pgm_file_size_squared(_PGM) == fs * fs
    def test_positive(self):
        assert pgm_file_size_squared(_PGM) > 0

# ── PPM ──────────────────────────────────────────────────────────────
from src.python.ppm.ppm_parser import (
    parse_ppm_strict,
    ppm_file_size_bytes,
    ppm_width_times_two,
    ppm_file_size_squared,
)

class TestPpmWidthTimesTwo:
    def test_returns_int(self):
        assert isinstance(ppm_width_times_two(_PPM), int)
    def test_double_of_base(self):
        assert ppm_width_times_two(_PPM) == parse_ppm_strict(_PPM).width * 2
    def test_positive(self):
        assert ppm_width_times_two(_PPM) > 0

class TestPpmFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_squared(_PPM), int)
    def test_square_of_base(self):
        fs = ppm_file_size_bytes(_PPM)
        assert ppm_file_size_squared(_PPM) == fs * fs
    def test_positive(self):
        assert ppm_file_size_squared(_PPM) > 0

# ── QOI ──────────────────────────────────────────────────────────────
from src.python.qoi.qoi_parser import (
    parse_qoi_strict,
    qoi_pixel_count,
    qoi_width_times_two,
    qoi_pixel_count_squared,
)

class TestQoiWidthTimesTwo:
    def test_returns_int(self):
        assert isinstance(qoi_width_times_two(_QOI), int)
    def test_double_of_base(self):
        assert qoi_width_times_two(_QOI) == parse_qoi_strict(_QOI).width * 2
    def test_positive(self):
        assert qoi_width_times_two(_QOI) > 0

class TestQoiPixelCountSquared:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_squared(_QOI), int)
    def test_square_of_base(self):
        pc = qoi_pixel_count(_QOI)
        assert qoi_pixel_count_squared(_QOI) == pc * pc
    def test_non_negative(self):
        assert qoi_pixel_count_squared(_QOI) >= 0
