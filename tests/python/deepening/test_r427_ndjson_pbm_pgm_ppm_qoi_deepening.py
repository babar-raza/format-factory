"""Sprint R427 — NDJSON/PBM/PGM/PPM/QOI deepening round 3."""
import sys, pathlib, json, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    ndjson_string_field_count_squared, ndjson_record_count_plus_key_count,
    ndjson_string_field_count, ndjson_record_count, ndjson_unique_key_count,
)
from src.python.pbm.pbm_parser import (
    pbm_black_pixel_count_squared, pbm_white_plus_black_count,
    pbm_black_pixel_count, pbm_white_pixel_count,
)
from src.python.pgm.pgm_parser import (
    pgm_pixel_sum_squared, pgm_width_plus_height, pgm_pixel_sum, parse_pgm_strict,
)
from src.python.ppm.ppm_parser import (
    ppm_red_channel_sum_squared, ppm_width_plus_height, parse_ppm_strict,
)
from src.python.qoi.qoi_parser import (
    qoi_channel_count_squared, qoi_width_plus_height, parse_qoi_strict,
)

_SAMPLES = _REPO / "samples" / "by-format"
_PBM = _SAMPLES / "pbm" / "valid" / "2x2-checker.pbm"
_PGM = _SAMPLES / "pgm" / "valid" / "2x2-gradient.pgm"
_PPM = _SAMPLES / "ppm" / "valid" / "1x1-red.ppm"
_QOI = _SAMPLES / "qoi" / "valid" / "1x1-red.qoi"


# === NDJSON ===
def _ndjson_source(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text('{"a": "hello", "b": 1}\n{"a": "world", "c": true}\n')
    return str(p)


class TestNdjsonStringFieldCountSquared:
    def test_returns_int(self, tmp_path):
        src = _ndjson_source(tmp_path)
        assert isinstance(ndjson_string_field_count_squared(src), int)

    def test_equals_square(self, tmp_path):
        src = _ndjson_source(tmp_path)
        sc = ndjson_string_field_count(src)
        assert ndjson_string_field_count_squared(src) == sc * sc

    def test_non_negative(self, tmp_path):
        src = _ndjson_source(tmp_path)
        assert ndjson_string_field_count_squared(src) >= 0


class TestNdjsonRecordCountPlusKeyCount:
    def test_returns_int(self, tmp_path):
        src = _ndjson_source(tmp_path)
        assert isinstance(ndjson_record_count_plus_key_count(src), int)

    def test_equals_sum(self, tmp_path):
        src = _ndjson_source(tmp_path)
        assert ndjson_record_count_plus_key_count(src) == ndjson_record_count(src) + ndjson_unique_key_count(src)

    def test_exceeds_record_count(self, tmp_path):
        src = _ndjson_source(tmp_path)
        assert ndjson_record_count_plus_key_count(src) >= ndjson_record_count(src)


# === PBM ===
class TestPbmBlackPixelCountSquared:
    def test_returns_int(self):
        assert isinstance(pbm_black_pixel_count_squared(_PBM), int)

    def test_equals_square(self):
        bc = pbm_black_pixel_count(_PBM)
        assert pbm_black_pixel_count_squared(_PBM) == bc * bc

    def test_non_negative(self):
        assert pbm_black_pixel_count_squared(_PBM) >= 0


class TestPbmWhitePlusBlackCount:
    def test_returns_int(self):
        assert isinstance(pbm_white_plus_black_count(_PBM), int)

    def test_equals_sum(self):
        assert pbm_white_plus_black_count(_PBM) == pbm_white_pixel_count(_PBM) + pbm_black_pixel_count(_PBM)

    def test_equals_total(self):
        from src.python.pbm.pbm_parser import pbm_total_pixel_count
        assert pbm_white_plus_black_count(_PBM) == pbm_total_pixel_count(_PBM)


# === PGM ===
class TestPgmPixelSumSquared:
    def test_returns_int(self):
        assert isinstance(pgm_pixel_sum_squared(_PGM), int)

    def test_equals_square(self):
        ps = pgm_pixel_sum(_PGM)
        assert pgm_pixel_sum_squared(_PGM) == ps * ps

    def test_non_negative(self):
        assert pgm_pixel_sum_squared(_PGM) >= 0


class TestPgmWidthPlusHeight:
    def test_returns_int(self):
        assert isinstance(pgm_width_plus_height(_PGM), int)

    def test_equals_sum(self):
        img = parse_pgm_strict(_PGM)
        assert pgm_width_plus_height(_PGM) == img.width + img.height

    def test_positive(self):
        assert pgm_width_plus_height(_PGM) > 0


# === PPM ===
class TestPpmRedChannelSumSquared:
    def test_returns_int(self):
        assert isinstance(ppm_red_channel_sum_squared(_PPM), int)

    def test_equals_square(self):
        img = parse_ppm_strict(_PPM)
        s = sum(r for r, g, b in img.pixels)
        assert ppm_red_channel_sum_squared(_PPM) == s * s

    def test_non_negative(self):
        assert ppm_red_channel_sum_squared(_PPM) >= 0


class TestPpmWidthPlusHeight:
    def test_returns_int(self):
        assert isinstance(ppm_width_plus_height(_PPM), int)

    def test_equals_sum(self):
        img = parse_ppm_strict(_PPM)
        assert ppm_width_plus_height(_PPM) == img.width + img.height

    def test_positive(self):
        assert ppm_width_plus_height(_PPM) > 0


# === QOI ===
class TestQoiChannelCountSquared:
    def test_returns_int(self):
        assert isinstance(qoi_channel_count_squared(_QOI), int)

    def test_equals_square(self):
        img = parse_qoi_strict(_QOI)
        assert qoi_channel_count_squared(_QOI) == img.channels * img.channels

    def test_positive(self):
        assert qoi_channel_count_squared(_QOI) > 0


class TestQoiWidthPlusHeight:
    def test_returns_int(self):
        assert isinstance(qoi_width_plus_height(_QOI), int)

    def test_equals_sum(self):
        img = parse_qoi_strict(_QOI)
        assert qoi_width_plus_height(_QOI) == img.width + img.height

    def test_positive(self):
        assert qoi_width_plus_height(_QOI) > 0
