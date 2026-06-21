"""
Sprint ff-idempotent-spec-to-feature-swarm-20260617 — NDJSON, FODG, TSV analytics deepening.
Tests for eighty_nine variants.
"""
import sys
import json
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_record_count_times_eighty_nine, ndjson_unique_key_count_times_eighty_nine
from src.python.fodg import fodg_shape_count_times_eighty_nine, fodg_text_count_times_eighty_nine
from src.python.tsv import tsv_row_count_times_eighty_nine, tsv_file_size_bytes_times_eighty_nine

_FODG = str(_REPO / "samples/by-format/fodg/minimal-drawing.fodg")
_FODG2 = str(_REPO / "samples/by-format/fodg/shapes-basic.fodg")
_TSV = str(_REPO / "samples/by-format/tsv/minimal-2x2.tsv")
_TSV2 = str(_REPO / "samples/by-format/tsv/multi-column.tsv")


@pytest.fixture
def ndjson_file(tmp_path):
    p = tmp_path / "test.ndjson"
    records = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}, {"a": 3, "b": "z"}]
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return str(p)


class TestNdjsonRecordCountTimesEightyNine:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_record_count_times_eighty_nine(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_record_count_times_eighty_nine(ndjson_file) >= 0
    def test_divisible_by_89(self, ndjson_file):
        assert ndjson_record_count_times_eighty_nine(ndjson_file) % 89 == 0
    def test_three_records_gives_267(self, ndjson_file):
        assert ndjson_record_count_times_eighty_nine(ndjson_file) == 3 * 89


class TestNdjsonUniqueKeyCountTimesEightyNine:
    def test_returns_int(self, ndjson_file):
        assert isinstance(ndjson_unique_key_count_times_eighty_nine(ndjson_file), int)
    def test_non_negative(self, ndjson_file):
        assert ndjson_unique_key_count_times_eighty_nine(ndjson_file) >= 0
    def test_divisible_by_89(self, ndjson_file):
        assert ndjson_unique_key_count_times_eighty_nine(ndjson_file) % 89 == 0


class TestFodgShapeCountTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(fodg_shape_count_times_eighty_nine(_FODG), int)
    def test_non_negative(self):
        assert fodg_shape_count_times_eighty_nine(_FODG) >= 0
    def test_divisible_by_89(self):
        assert fodg_shape_count_times_eighty_nine(_FODG) % 89 == 0


class TestFodgTextCountTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(fodg_text_count_times_eighty_nine(_FODG), int)
    def test_non_negative(self):
        assert fodg_text_count_times_eighty_nine(_FODG) >= 0
    def test_divisible_by_89(self):
        assert fodg_text_count_times_eighty_nine(_FODG) % 89 == 0


class TestTsvRowCountTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_eighty_nine(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_eighty_nine(_TSV) >= 0
    def test_divisible_by_89(self):
        assert tsv_row_count_times_eighty_nine(_TSV) % 89 == 0


class TestTsvFileSizeBytesTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_eighty_nine(_TSV), int)
    def test_positive(self):
        assert tsv_file_size_bytes_times_eighty_nine(_TSV) > 0
    def test_divisible_by_89(self):
        assert tsv_file_size_bytes_times_eighty_nine(_TSV) % 89 == 0
    def test_multi_col_gte_minimal(self):
        assert tsv_file_size_bytes_times_eighty_nine(_TSV2) >= tsv_file_size_bytes_times_eighty_nine(_TSV)
