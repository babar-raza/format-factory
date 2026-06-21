"""Sprint R431 — product deepening round 3 for NDJSON/PBM/PGM/PPM/QOI.

New analytics:
  NDJSON: ndjson_total_key_count_squared, ndjson_avg_numeric_squared
  PBM:    pbm_row_count_squared, pbm_file_size_plus_width
  PGM:    pgm_pixel_count_squared, pgm_file_size_plus_width
  PPM:    ppm_total_pixel_count_squared, ppm_avg_red_squared
  QOI:    qoi_total_pixel_count_squared, qoi_avg_red_squared
"""
import sys, pathlib, json, tempfile

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

# ── NDJSON ───────────────────────────────────────────────────────────
from src.python.ndjson.ndjson_codec import (
    ndjson_total_key_count_squared,
    ndjson_avg_numeric_squared,
    ndjson_unique_key_count,
    ndjson_avg_numeric_value,
)


@pytest.fixture
def ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text('{"a":1,"b":"x"}\n{"a":2,"c":3}\n')
    return str(p)


class TestNdjsonTotalKeyCountSquared:
    def test_basic(self, ndjson_file):
        kc = ndjson_unique_key_count(ndjson_file)
        assert ndjson_total_key_count_squared(ndjson_file) == kc * kc

    def test_type(self, ndjson_file):
        assert isinstance(ndjson_total_key_count_squared(ndjson_file), int)

    def test_nonneg(self, ndjson_file):
        assert ndjson_total_key_count_squared(ndjson_file) >= 0


class TestNdjsonAvgNumericSquared:
    def test_basic(self, ndjson_file):
        avg = ndjson_avg_numeric_value(ndjson_file)
        assert ndjson_avg_numeric_squared(ndjson_file) == pytest.approx(avg * avg)

    def test_type(self, ndjson_file):
        assert isinstance(ndjson_avg_numeric_squared(ndjson_file), float)

    def test_nonneg(self, ndjson_file):
        assert ndjson_avg_numeric_squared(ndjson_file) >= 0.0


# ── PBM ──────────────────────────────────────────────────────────────
from src.python.pbm.pbm_parser import (
    pbm_row_count_squared,
    pbm_file_size_plus_width,
    pbm_file_size_bytes,
    parse_pbm_strict,
)

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


class TestPbmRowCountSquared:
    def test_minimal(self):
        p = _PBM / "1x1-black.pbm"
        img = parse_pbm_strict(p)
        assert pbm_row_count_squared(p) == img.height ** 2

    def test_type(self):
        p = _PBM / "1x1-black.pbm"
        assert isinstance(pbm_row_count_squared(p), int)

    def test_nonneg(self):
        p = _PBM / "1x1-black.pbm"
        assert pbm_row_count_squared(p) >= 0


class TestPbmFileSizePlusWidth:
    def test_minimal(self):
        p = _PBM / "1x1-black.pbm"
        expected = pbm_file_size_bytes(p) + parse_pbm_strict(p).width
        assert pbm_file_size_plus_width(p) == expected

    def test_type(self):
        p = _PBM / "1x1-black.pbm"
        assert isinstance(pbm_file_size_plus_width(p), int)

    def test_positive(self):
        p = _PBM / "1x1-black.pbm"
        assert pbm_file_size_plus_width(p) > 0


# ── PGM ──────────────────────────────────────────────────────────────
from src.python.pgm.pgm_parser import (
    pgm_pixel_count_squared,
    pgm_file_size_plus_width,
    pgm_file_size_bytes,
    parse_pgm_strict,
)

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestPgmPixelCountSquared:
    def test_minimal(self):
        p = _PGM / "1x1-white.pgm"
        img = parse_pgm_strict(p)
        pc = img.width * img.height
        assert pgm_pixel_count_squared(p) == pc * pc

    def test_type(self):
        p = _PGM / "1x1-white.pgm"
        assert isinstance(pgm_pixel_count_squared(p), int)

    def test_nonneg(self):
        p = _PGM / "1x1-white.pgm"
        assert pgm_pixel_count_squared(p) >= 0


class TestPgmFileSizePlusWidth:
    def test_minimal(self):
        p = _PGM / "1x1-white.pgm"
        expected = pgm_file_size_bytes(p) + parse_pgm_strict(p).width
        assert pgm_file_size_plus_width(p) == expected

    def test_type(self):
        p = _PGM / "1x1-white.pgm"
        assert isinstance(pgm_file_size_plus_width(p), int)

    def test_positive(self):
        p = _PGM / "1x1-white.pgm"
        assert pgm_file_size_plus_width(p) > 0


# ── PPM ──────────────────────────────────────────────────────────────
from src.python.ppm.ppm_parser import (
    ppm_total_pixel_count_squared,
    ppm_avg_red_squared,
    ppm_avg_red_channel,
    parse_ppm_strict,
)

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPpmTotalPixelCountSquared:
    def test_minimal(self):
        p = _PPM / "1x1-red.ppm"
        img = parse_ppm_strict(p)
        pc = img.width * img.height
        assert ppm_total_pixel_count_squared(p) == pc * pc

    def test_type(self):
        p = _PPM / "1x1-red.ppm"
        assert isinstance(ppm_total_pixel_count_squared(p), int)

    def test_nonneg(self):
        p = _PPM / "1x1-red.ppm"
        assert ppm_total_pixel_count_squared(p) >= 0


class TestPpmAvgRedSquared:
    def test_minimal(self):
        p = _PPM / "1x1-red.ppm"
        avg = ppm_avg_red_channel(p)
        assert ppm_avg_red_squared(p) == pytest.approx(avg * avg)

    def test_type(self):
        p = _PPM / "1x1-red.ppm"
        assert isinstance(ppm_avg_red_squared(p), float)

    def test_nonneg(self):
        p = _PPM / "1x1-red.ppm"
        assert ppm_avg_red_squared(p) >= 0.0


# ── QOI ──────────────────────────────────────────────────────────────
from src.python.qoi.qoi_parser import (
    qoi_total_pixel_count_squared,
    qoi_avg_red_squared,
    qoi_avg_red_channel,
    parse_qoi_strict,
)

_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestQoiTotalPixelCountSquared:
    def test_minimal(self):
        p = _QOI / "1x1-red.qoi"
        img = parse_qoi_strict(p)
        pc = img.width * img.height
        assert qoi_total_pixel_count_squared(p) == pc * pc

    def test_type(self):
        p = _QOI / "1x1-red.qoi"
        assert isinstance(qoi_total_pixel_count_squared(p), int)

    def test_nonneg(self):
        p = _QOI / "1x1-red.qoi"
        assert qoi_total_pixel_count_squared(p) >= 0


class TestQoiAvgRedSquared:
    def test_minimal(self):
        p = _QOI / "1x1-red.qoi"
        avg = qoi_avg_red_channel(p)
        assert qoi_avg_red_squared(p) == pytest.approx(avg * avg)

    def test_type(self):
        p = _QOI / "1x1-red.qoi"
        assert isinstance(qoi_avg_red_squared(p), float)

    def test_nonneg(self):
        p = _QOI / "1x1-red.qoi"
        assert qoi_avg_red_squared(p) >= 0.0
