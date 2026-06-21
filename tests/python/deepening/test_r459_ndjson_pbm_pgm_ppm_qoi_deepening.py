"""Sprint R459 — NDJSON/PBM/PGM/PPM/QOI round 11 deepening tests."""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_record_count_times_four, ndjson_string_field_count_times_four, ndjson_record_count, ndjson_string_field_count
from src.python.pbm import pbm_width_times_four, pbm_height_times_four, pbm_width, pbm_height
from src.python.pgm import pgm_width_times_four, pgm_height_times_four, pgm_width, pgm_height
from src.python.ppm import ppm_width_times_four, ppm_height_times_four, ppm_width, ppm_height
from src.python.qoi import qoi_width_times_four, qoi_height_times_four, qoi_width, qoi_height

SAMPLES = _REPO / "samples" / "by-format"
PBM_SAMPLE = SAMPLES / "pbm" / "valid" / "1x1-black.pbm"
PGM_SAMPLE = SAMPLES / "pgm" / "valid" / "1x1-white.pgm"
PPM_SAMPLE = SAMPLES / "ppm" / "valid" / "1x1-red.ppm"
QOI_SAMPLE = SAMPLES / "qoi" / "valid" / "1x1-red.qoi"


def _ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]) + "\n")
    return p


class TestNdjsonRecordCountTimesFour:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_four(_ndjson_file(tmp_path)), int)
    def test_is_quadruple(self, tmp_path):
        f = _ndjson_file(tmp_path)
        assert ndjson_record_count_times_four(f) == ndjson_record_count(f) * 4
    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_four(_ndjson_file(tmp_path)) >= 0


class TestNdjsonStringFieldCountTimesFour:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_string_field_count_times_four(_ndjson_file(tmp_path)), int)
    def test_is_quadruple(self, tmp_path):
        f = _ndjson_file(tmp_path)
        assert ndjson_string_field_count_times_four(f) == ndjson_string_field_count(f) * 4
    def test_non_negative(self, tmp_path):
        assert ndjson_string_field_count_times_four(_ndjson_file(tmp_path)) >= 0


class TestPbmWidthTimesFour:
    def test_returns_int(self):
        assert isinstance(pbm_width_times_four(PBM_SAMPLE), int)
    def test_is_quadruple(self):
        assert pbm_width_times_four(PBM_SAMPLE) == pbm_width(PBM_SAMPLE) * 4
    def test_non_negative(self):
        assert pbm_width_times_four(PBM_SAMPLE) >= 0


class TestPbmHeightTimesFour:
    def test_returns_int(self):
        assert isinstance(pbm_height_times_four(PBM_SAMPLE), int)
    def test_is_quadruple(self):
        assert pbm_height_times_four(PBM_SAMPLE) == pbm_height(PBM_SAMPLE) * 4
    def test_non_negative(self):
        assert pbm_height_times_four(PBM_SAMPLE) >= 0


class TestPgmWidthTimesFour:
    def test_returns_int(self):
        assert isinstance(pgm_width_times_four(PGM_SAMPLE), int)
    def test_is_quadruple(self):
        assert pgm_width_times_four(PGM_SAMPLE) == pgm_width(PGM_SAMPLE) * 4
    def test_non_negative(self):
        assert pgm_width_times_four(PGM_SAMPLE) >= 0


class TestPgmHeightTimesFour:
    def test_returns_int(self):
        assert isinstance(pgm_height_times_four(PGM_SAMPLE), int)
    def test_is_quadruple(self):
        assert pgm_height_times_four(PGM_SAMPLE) == pgm_height(PGM_SAMPLE) * 4
    def test_non_negative(self):
        assert pgm_height_times_four(PGM_SAMPLE) >= 0


class TestPpmWidthTimesFour:
    def test_returns_int(self):
        assert isinstance(ppm_width_times_four(PPM_SAMPLE), int)
    def test_is_quadruple(self):
        assert ppm_width_times_four(PPM_SAMPLE) == ppm_width(PPM_SAMPLE) * 4
    def test_non_negative(self):
        assert ppm_width_times_four(PPM_SAMPLE) >= 0


class TestPpmHeightTimesFour:
    def test_returns_int(self):
        assert isinstance(ppm_height_times_four(PPM_SAMPLE), int)
    def test_is_quadruple(self):
        assert ppm_height_times_four(PPM_SAMPLE) == ppm_height(PPM_SAMPLE) * 4
    def test_non_negative(self):
        assert ppm_height_times_four(PPM_SAMPLE) >= 0


class TestQoiWidthTimesFour:
    def test_returns_int(self):
        assert isinstance(qoi_width_times_four(QOI_SAMPLE), int)
    def test_is_quadruple(self):
        assert qoi_width_times_four(QOI_SAMPLE) == qoi_width(QOI_SAMPLE) * 4
    def test_non_negative(self):
        assert qoi_width_times_four(QOI_SAMPLE) >= 0


class TestQoiHeightTimesFour:
    def test_returns_int(self):
        assert isinstance(qoi_height_times_four(QOI_SAMPLE), int)
    def test_is_quadruple(self):
        assert qoi_height_times_four(QOI_SAMPLE) == qoi_height(QOI_SAMPLE) * 4
    def test_non_negative(self):
        assert qoi_height_times_four(QOI_SAMPLE) >= 0
