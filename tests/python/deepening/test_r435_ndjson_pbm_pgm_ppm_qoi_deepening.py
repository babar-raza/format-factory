"""Sprint R435 — product deepening round 5 for NDJSON/PBM/PGM/PPM/QOI.

New analytics:
  NDJSON: ndjson_record_count_times_two, ndjson_bool_field_count_squared
  PBM:    pbm_white_pixel_count_squared, pbm_height_times_two
  PGM:    pgm_unique_pixel_count_squared, pgm_height_times_two
  PPM:    ppm_unique_pixel_count_squared, ppm_height_times_two
  QOI:    qoi_file_size_squared, qoi_height_times_two
"""
import sys, pathlib, json, tempfile

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

# ── NDJSON ───────────────────────────────────────────────────────────
from src.python.ndjson.ndjson_codec import (
    ndjson_record_count_times_two,
    ndjson_bool_field_count_squared,
    ndjson_record_count,
    ndjson_bool_field_count,
)


class TestNdjsonRecordCountTimesTwo:
    def test_basic(self, tmp_path):
        p = tmp_path / "test.ndjson"
        p.write_text('{"a":1}\n{"a":2}\n')
        rc = ndjson_record_count(str(p))
        assert ndjson_record_count_times_two(str(p)) == rc * 2

    def test_type(self, tmp_path):
        p = tmp_path / "test.ndjson"
        p.write_text('{"a":1}\n')
        assert isinstance(ndjson_record_count_times_two(str(p)), int)

    def test_nonneg(self, tmp_path):
        p = tmp_path / "test.ndjson"
        p.write_text('{"a":1}\n')
        assert ndjson_record_count_times_two(str(p)) >= 0


class TestNdjsonBoolFieldCountSquared:
    def test_basic(self, tmp_path):
        p = tmp_path / "test.ndjson"
        p.write_text('{"a":true,"b":false}\n')
        bc = ndjson_bool_field_count(str(p))
        assert ndjson_bool_field_count_squared(str(p)) == bc * bc

    def test_type(self, tmp_path):
        p = tmp_path / "test.ndjson"
        p.write_text('{"a":1}\n')
        assert isinstance(ndjson_bool_field_count_squared(str(p)), int)

    def test_nonneg(self, tmp_path):
        p = tmp_path / "test.ndjson"
        p.write_text('{"a":1}\n')
        assert ndjson_bool_field_count_squared(str(p)) >= 0


# ── PBM ──────────────────────────────────────────────────────────────
from src.python.pbm.pbm_parser import (
    pbm_white_pixel_count_squared,
    pbm_height_times_two,
    pbm_white_pixel_count,
    parse_pbm_strict,
)

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


class TestPbmWhitePixelCountSquared:
    def test_minimal(self):
        p = _PBM / "1x1-black.pbm"
        wc = pbm_white_pixel_count(p)
        assert pbm_white_pixel_count_squared(p) == wc * wc

    def test_type(self):
        assert isinstance(pbm_white_pixel_count_squared(_PBM / "1x1-black.pbm"), int)

    def test_nonneg(self):
        assert pbm_white_pixel_count_squared(_PBM / "1x1-black.pbm") >= 0


class TestPbmHeightTimesTwo:
    def test_minimal(self):
        p = _PBM / "1x1-black.pbm"
        h = parse_pbm_strict(p).height
        assert pbm_height_times_two(p) == h * 2

    def test_type(self):
        assert isinstance(pbm_height_times_two(_PBM / "1x1-black.pbm"), int)

    def test_nonneg(self):
        assert pbm_height_times_two(_PBM / "1x1-black.pbm") >= 0


# ── PGM ──────────────────────────────────────────────────────────────
from src.python.pgm.pgm_parser import (
    pgm_unique_pixel_count_squared,
    pgm_height_times_two,
    pgm_unique_pixel_count,
    parse_pgm_strict,
)

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestPgmUniquePixelCountSquared:
    def test_minimal(self):
        p = _PGM / "1x1-white.pgm"
        uc = pgm_unique_pixel_count(p)
        assert pgm_unique_pixel_count_squared(p) == uc * uc

    def test_type(self):
        assert isinstance(pgm_unique_pixel_count_squared(_PGM / "1x1-white.pgm"), int)

    def test_nonneg(self):
        assert pgm_unique_pixel_count_squared(_PGM / "1x1-white.pgm") >= 0


class TestPgmHeightTimesTwo:
    def test_minimal(self):
        p = _PGM / "1x1-white.pgm"
        h = parse_pgm_strict(p).height
        assert pgm_height_times_two(p) == h * 2

    def test_type(self):
        assert isinstance(pgm_height_times_two(_PGM / "1x1-white.pgm"), int)

    def test_nonneg(self):
        assert pgm_height_times_two(_PGM / "1x1-white.pgm") >= 0


# ── PPM ──────────────────────────────────────────────────────────────
from src.python.ppm.ppm_parser import (
    ppm_unique_pixel_count_squared,
    ppm_height_times_two,
    ppm_unique_pixel_count,
    parse_ppm_strict,
)

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPpmUniquePixelCountSquared:
    def test_minimal(self):
        p = _PPM / "1x1-red.ppm"
        uc = ppm_unique_pixel_count(p)
        assert ppm_unique_pixel_count_squared(p) == uc * uc

    def test_type(self):
        assert isinstance(ppm_unique_pixel_count_squared(_PPM / "1x1-red.ppm"), int)

    def test_nonneg(self):
        assert ppm_unique_pixel_count_squared(_PPM / "1x1-red.ppm") >= 0


class TestPpmHeightTimesTwo:
    def test_minimal(self):
        p = _PPM / "1x1-red.ppm"
        h = parse_ppm_strict(p).height
        assert ppm_height_times_two(p) == h * 2

    def test_type(self):
        assert isinstance(ppm_height_times_two(_PPM / "1x1-red.ppm"), int)

    def test_nonneg(self):
        assert ppm_height_times_two(_PPM / "1x1-red.ppm") >= 0


# ── QOI ──────────────────────────────────────────────────────────────
from src.python.qoi.qoi_parser import (
    qoi_file_size_squared,
    qoi_height_times_two,
    qoi_file_size_bytes,
    parse_qoi_strict,
)

_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


class TestQoiFileSizeSquared:
    def test_minimal(self):
        p = _QOI / "1x1-red.qoi"
        fs = qoi_file_size_bytes(p)
        assert qoi_file_size_squared(p) == fs * fs

    def test_type(self):
        assert isinstance(qoi_file_size_squared(_QOI / "1x1-red.qoi"), int)

    def test_nonneg(self):
        assert qoi_file_size_squared(_QOI / "1x1-red.qoi") >= 0


class TestQoiHeightTimesTwo:
    def test_minimal(self):
        p = _QOI / "1x1-red.qoi"
        h = parse_qoi_strict(p).height
        assert qoi_height_times_two(p) == h * 2

    def test_type(self):
        assert isinstance(qoi_height_times_two(_QOI / "1x1-red.qoi"), int)

    def test_nonneg(self):
        assert qoi_height_times_two(_QOI / "1x1-red.qoi") >= 0
