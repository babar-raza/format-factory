"""Sprint R451 — NDJSON/PBM/PGM/PPM/QOI round 9 deepening tests."""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_width_times_three, pbm_height_times_three, pbm_width, pbm_height
from src.python.pgm import pgm_width_times_three, pgm_height_times_three, pgm_width, pgm_height
from src.python.ppm import ppm_width_times_three, ppm_height_times_three, ppm_width, ppm_height
from src.python.qoi import qoi_width_times_three, qoi_height_times_three, qoi_width, qoi_height
from src.python.ndjson import ndjson_record_count_times_three, ndjson_string_field_count_times_three, ndjson_record_count, ndjson_string_field_count

SAMPLES = _REPO / "samples" / "by-format"
PBM_SAMPLE = SAMPLES / "pbm" / "valid" / "1x1-black.pbm"
PGM_SAMPLE = SAMPLES / "pgm" / "valid" / "1x1-white.pgm"
PPM_SAMPLE = SAMPLES / "ppm" / "valid" / "1x1-red.ppm"
QOI_SAMPLE = SAMPLES / "qoi" / "valid" / "1x1-red.qoi"


def _ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    p.write_text("\n".join(json.dumps(r) for r in [
        {"name": "alice", "age": 30},
        {"name": "bob", "age": 25},
        {"name": "carol", "age": 35},
    ]) + "\n")
    return p


class TestNdjsonRecordCountTimesThree:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_record_count_times_three(_ndjson_file(tmp_path)), int)
    def test_is_triple(self, tmp_path):
        f = _ndjson_file(tmp_path)
        assert ndjson_record_count_times_three(f) == ndjson_record_count(f) * 3
    def test_non_negative(self, tmp_path):
        assert ndjson_record_count_times_three(_ndjson_file(tmp_path)) >= 0


class TestNdjsonStringFieldCountTimesThree:
    def test_returns_int(self, tmp_path):
        assert isinstance(ndjson_string_field_count_times_three(_ndjson_file(tmp_path)), int)
    def test_is_triple(self, tmp_path):
        f = _ndjson_file(tmp_path)
        assert ndjson_string_field_count_times_three(f) == ndjson_string_field_count(f) * 3
    def test_non_negative(self, tmp_path):
        assert ndjson_string_field_count_times_three(_ndjson_file(tmp_path)) >= 0


class TestPbmWidthTimesThree:
    def test_returns_int(self):
        assert isinstance(pbm_width_times_three(PBM_SAMPLE), int)
    def test_is_triple(self):
        assert pbm_width_times_three(PBM_SAMPLE) == pbm_width(PBM_SAMPLE) * 3
    def test_non_negative(self):
        assert pbm_width_times_three(PBM_SAMPLE) >= 0


class TestPbmHeightTimesThree:
    def test_returns_int(self):
        assert isinstance(pbm_height_times_three(PBM_SAMPLE), int)
    def test_is_triple(self):
        assert pbm_height_times_three(PBM_SAMPLE) == pbm_height(PBM_SAMPLE) * 3
    def test_non_negative(self):
        assert pbm_height_times_three(PBM_SAMPLE) >= 0


class TestPgmWidthTimesThree:
    def test_returns_int(self):
        assert isinstance(pgm_width_times_three(PGM_SAMPLE), int)
    def test_is_triple(self):
        assert pgm_width_times_three(PGM_SAMPLE) == pgm_width(PGM_SAMPLE) * 3
    def test_non_negative(self):
        assert pgm_width_times_three(PGM_SAMPLE) >= 0


class TestPgmHeightTimesThree:
    def test_returns_int(self):
        assert isinstance(pgm_height_times_three(PGM_SAMPLE), int)
    def test_is_triple(self):
        assert pgm_height_times_three(PGM_SAMPLE) == pgm_height(PGM_SAMPLE) * 3
    def test_non_negative(self):
        assert pgm_height_times_three(PGM_SAMPLE) >= 0


class TestPpmWidthTimesThree:
    def test_returns_int(self):
        assert isinstance(ppm_width_times_three(PPM_SAMPLE), int)
    def test_is_triple(self):
        assert ppm_width_times_three(PPM_SAMPLE) == ppm_width(PPM_SAMPLE) * 3
    def test_non_negative(self):
        assert ppm_width_times_three(PPM_SAMPLE) >= 0


class TestPpmHeightTimesThree:
    def test_returns_int(self):
        assert isinstance(ppm_height_times_three(PPM_SAMPLE), int)
    def test_is_triple(self):
        assert ppm_height_times_three(PPM_SAMPLE) == ppm_height(PPM_SAMPLE) * 3
    def test_non_negative(self):
        assert ppm_height_times_three(PPM_SAMPLE) >= 0


class TestQoiWidthTimesThree:
    def test_returns_int(self):
        assert isinstance(qoi_width_times_three(QOI_SAMPLE), int)
    def test_is_triple(self):
        assert qoi_width_times_three(QOI_SAMPLE) == qoi_width(QOI_SAMPLE) * 3
    def test_non_negative(self):
        assert qoi_width_times_three(QOI_SAMPLE) >= 0


class TestQoiHeightTimesThree:
    def test_returns_int(self):
        assert isinstance(qoi_height_times_three(QOI_SAMPLE), int)
    def test_is_triple(self):
        assert qoi_height_times_three(QOI_SAMPLE) == qoi_height(QOI_SAMPLE) * 3
    def test_non_negative(self):
        assert qoi_height_times_three(QOI_SAMPLE) >= 0
