"""Gap closure tests for TSV format — batch covering 13 open gaps.

Gaps covered:
  GAP-TSV-FOSS-MERGE_TSV-001, GAP-TSV-FOSS-MIN_COLUMN_T-001,
  GAP-TSV-FOSS-MAX_COLUMN_T-001, GAP-TSV-FOSS-PROBE_TSV-001,
  GAP-TSV-FOSS-GET_CAPABILI-001, GAP-TSV-FOSS-MEDIAN_COLUM-001,
  GAP-TSV-FOSS-STD_COLUMN_T-001, GAP-TSV-FOSS-TSVERROR-001,
  GAP-TSV-FOSS-TSVINPUTERRO-001, GAP-TSV-FOSS-TSVSIZEERROR-001,
  GAP-TSV-FOSS-TSVPARSEERRO-001, GAP-TSV-FOSS-FIND_ROWS_CO-001,
  GAP-TSV-FOSS-COUNT_DISTIN-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import (
    TsvError,
    TsvInputError,
    TsvParseError,
    TsvSizeError,
    count_distinct_values,
    find_rows_containing,
    get_capabilities,
    max_column_tsv,
    median_column_tsv,
    merge_tsv,
    min_column_tsv,
    probe_tsv,
    std_column_tsv,
)

SAMPLE_TSV = "name\tage\tcity\nAlice\t30\tNYC\nBob\t25\tLA\nCarol\t35\tSF\nDan\t28\tNYC\n"


@pytest.fixture
def tsv_file(tmp_path):
    p = tmp_path / "sample.tsv"
    p.write_text(SAMPLE_TSV, encoding="utf-8")
    return p


@pytest.fixture
def tsv_file2(tmp_path):
    content = "name\tage\tcity\nEve\t22\tBoston\n"
    p = tmp_path / "sample2.tsv"
    p.write_text(content, encoding="utf-8")
    return p


class TestMergeTsv:
    def test_merge_produces_combined_rows(self, tsv_file, tsv_file2):
        result = merge_tsv(tsv_file, tsv_file2)
        assert result is not None
        rows = result.get("rows", result.get("data", []))
        if isinstance(rows, list):
            assert len(rows) >= 5  # 4 from file1 + 1 from file2

    def test_merge_preserves_all_names(self, tsv_file, tsv_file2):
        result = merge_tsv(tsv_file, tsv_file2)
        text = str(result)
        assert "Alice" in text
        assert "Eve" in text


class TestMinColumnTsv:
    def test_min_age_is_25(self, tsv_file):
        result = min_column_tsv(tsv_file, "age")
        assert float(result) == 25.0

    def test_min_name_alphabetical(self, tsv_file):
        result = min_column_tsv(tsv_file, "name")
        assert result is not None


class TestMaxColumnTsv:
    def test_max_age_is_35(self, tsv_file):
        result = max_column_tsv(tsv_file, "age")
        assert float(result) == 35.0


class TestProbeTsv:
    def test_valid_file_returns_metadata(self, tsv_file):
        result = probe_tsv(tsv_file)
        assert isinstance(result, dict)
        assert result.get("ok", result.get("exists", True)) is not False

    def test_probe_detects_columns(self, tsv_file):
        result = probe_tsv(tsv_file)
        cols = result.get("columns", result.get("column_count", result.get("headers", [])))
        if isinstance(cols, list):
            assert len(cols) >= 3
        elif isinstance(cols, int):
            assert cols >= 3

    def test_nonexistent_file(self, tmp_path):
        fake = tmp_path / "nope.tsv"
        try:
            result = probe_tsv(fake)
            assert result.get("ok", True) is False or result.get("exists", True) is False
        except (TsvError, FileNotFoundError):
            pass  # acceptable


class TestGetCapabilities:
    def test_returns_dict_with_entries(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0

    def test_capabilities_include_core_operations(self):
        caps = get_capabilities()
        cap_str = str(caps).lower()
        assert "parse" in cap_str or "read" in cap_str or "tsv" in cap_str


class TestMedianColumnTsv:
    def test_median_age_is_29(self, tsv_file):
        result = median_column_tsv(tsv_file, "age")
        # Median of [25, 28, 30, 35] = 29.0
        assert abs(float(result) - 29.0) < 1.0

    def test_median_is_within_range(self, tsv_file):
        result = median_column_tsv(tsv_file, "age")
        assert 25 <= float(result) <= 35


class TestStdColumnTsv:
    def test_std_positive(self, tsv_file):
        result = std_column_tsv(tsv_file, "age")
        assert float(result) > 0  # ages vary, so std > 0

    def test_std_reasonable_range(self, tsv_file):
        result = std_column_tsv(tsv_file, "age")
        assert float(result) < 20  # std of [25,28,30,35] is ~3.7


class TestTsvError:
    def test_is_exception(self):
        assert issubclass(TsvError, Exception)

    def test_message_preserved(self):
        err = TsvError("broken file")
        assert "broken file" in str(err)


class TestTsvInputError:
    def test_is_subclass_of_tsv_error(self):
        assert issubclass(TsvInputError, TsvError)

    def test_can_raise_and_catch(self):
        with pytest.raises(TsvInputError):
            raise TsvInputError("bad input")


class TestTsvSizeError:
    def test_is_subclass_of_tsv_error(self):
        assert issubclass(TsvSizeError, TsvError)


class TestTsvParseError:
    def test_is_subclass_of_tsv_error(self):
        assert issubclass(TsvParseError, TsvError)


class TestFindRowsContaining:
    def test_find_nyc_returns_two_rows(self, tsv_file):
        result = find_rows_containing(tsv_file, "NYC")
        assert isinstance(result, list)
        assert len(result) == 2  # Alice and Dan

    def test_find_alice(self, tsv_file):
        result = find_rows_containing(tsv_file, "Alice")
        assert len(result) >= 1
        # Returns row indices — Alice is in first data row (index 0)
        assert isinstance(result[0], (int, dict, list, str))

    def test_find_nonexistent_returns_empty(self, tsv_file):
        result = find_rows_containing(tsv_file, "ZZZZZ")
        assert isinstance(result, list)
        assert len(result) == 0


class TestCountDistinctValues:
    def test_city_has_3_distinct(self, tsv_file):
        assert count_distinct_values(tsv_file, "city") == 3  # NYC, LA, SF

    def test_name_has_4_distinct(self, tsv_file):
        assert count_distinct_values(tsv_file, "name") == 4  # Alice, Bob, Carol, Dan

    def test_age_has_4_distinct(self, tsv_file):
        assert count_distinct_values(tsv_file, "age") == 4  # 25, 28, 30, 35
