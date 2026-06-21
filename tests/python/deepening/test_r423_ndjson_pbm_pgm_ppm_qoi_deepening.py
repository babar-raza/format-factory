"""Tests for 10 new analytics: NDJSON/PBM/PGM/PPM/QOI deepening sprint R423."""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    ndjson_record_count_squared,
    ndjson_key_count_plus_record_count,
    ndjson_record_count,
    ndjson_unique_key_count,
)

from src.python.pbm.pbm_parser import (
    pbm_total_pixel_count_squared,
    pbm_width_times_height,
    pbm_total_pixel_count,
)

from src.python.pgm.pgm_parser import (
    pgm_total_pixel_count_squared,
    pgm_width_times_height,
    pgm_total_pixel_count,
)

from src.python.ppm.ppm_parser import (
    ppm_pixel_count_squared,
    ppm_width_times_height,
    ppm_pixel_count,
)

from src.python.qoi.qoi_parser import (
    qoi_pixel_count_squared,
    qoi_width_times_height,
    qoi_pixel_count,
)

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "1x1-red.ppm"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi"


def _ndjson_path(tmp_path):
    p = tmp_path / "test.ndjson"
    lines = [json.dumps({"a": 1, "b": "x"}), json.dumps({"a": 2, "c": True})]
    p.write_text("\n".join(lines) + "\n")
    return p


class TestNdjsonRecordCountSquared:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_squared(str(_ndjson_path(tmp_path))), int)

    def test_matches_formula(self, tmp_path):
        p = _ndjson_path(tmp_path)
        rc = ndjson_record_count(str(p))
        assert ndjson_record_count_squared(str(p)) == rc * rc

    def test_positive(self, tmp_path):
        assert ndjson_record_count_squared(str(_ndjson_path(tmp_path))) >= 1


class TestNdjsonKeyCountPlusRecordCount:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_key_count_plus_record_count(str(_ndjson_path(tmp_path))), int)

    def test_matches_sum(self, tmp_path):
        p = _ndjson_path(tmp_path)
        assert ndjson_key_count_plus_record_count(str(p)) == ndjson_unique_key_count(str(p)) + ndjson_record_count(str(p))

    def test_positive(self, tmp_path):
        assert ndjson_key_count_plus_record_count(str(_ndjson_path(tmp_path))) >= 1


class TestPbmTotalPixelCountSquared:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixel_count_squared(_PBM), int)

    def test_matches_formula(self):
        tp = pbm_total_pixel_count(_PBM)
        assert pbm_total_pixel_count_squared(_PBM) == tp * tp

    def test_positive(self):
        assert pbm_total_pixel_count_squared(_PBM) >= 1


class TestPbmWidthTimesHeight:
    def test_returns_int(self):
        assert isinstance(pbm_width_times_height(_PBM), int)

    def test_equals_total_pixels(self):
        assert pbm_width_times_height(_PBM) == pbm_total_pixel_count(_PBM)

    def test_positive(self):
        assert pbm_width_times_height(_PBM) >= 1


class TestPgmTotalPixelCountSquared:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_squared(_PGM), int)

    def test_matches_formula(self):
        tp = pgm_total_pixel_count(_PGM)
        assert pgm_total_pixel_count_squared(_PGM) == tp * tp

    def test_positive(self):
        assert pgm_total_pixel_count_squared(_PGM) >= 1


class TestPgmWidthTimesHeight:
    def test_returns_int(self):
        assert isinstance(pgm_width_times_height(_PGM), int)

    def test_equals_total_pixels(self):
        assert pgm_width_times_height(_PGM) == pgm_total_pixel_count(_PGM)

    def test_positive(self):
        assert pgm_width_times_height(_PGM) >= 1


class TestPpmPixelCountSquared:
    def test_returns_int(self):
        assert isinstance(ppm_pixel_count_squared(_PPM), int)

    def test_matches_formula(self):
        pc = ppm_pixel_count(_PPM)
        assert ppm_pixel_count_squared(_PPM) == pc * pc

    def test_positive(self):
        assert ppm_pixel_count_squared(_PPM) >= 1


class TestPpmWidthTimesHeight:
    def test_returns_int(self):
        assert isinstance(ppm_width_times_height(_PPM), int)

    def test_equals_pixel_count(self):
        assert ppm_width_times_height(_PPM) == ppm_pixel_count(_PPM)

    def test_positive(self):
        assert ppm_width_times_height(_PPM) >= 1


class TestQoiPixelCountSquared:
    def test_returns_int(self):
        assert isinstance(qoi_pixel_count_squared(_QOI), int)

    def test_matches_formula(self):
        pc = qoi_pixel_count(_QOI)
        assert qoi_pixel_count_squared(_QOI) == pc * pc

    def test_positive(self):
        assert qoi_pixel_count_squared(_QOI) >= 1


class TestQoiWidthTimesHeight:
    def test_returns_int(self):
        assert isinstance(qoi_width_times_height(_QOI), int)

    def test_equals_pixel_count(self):
        assert qoi_width_times_height(_QOI) == qoi_pixel_count(_QOI)

    def test_positive(self):
        assert qoi_width_times_height(_QOI) >= 1
