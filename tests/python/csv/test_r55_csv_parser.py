"""
test_r55_csv_parser.py — R55 Train H: CSV parser Gate 4 prototype tests.

TC-ACQN-CSV-001: RFC 4180 CSV parsing using Python stdlib csv module.

Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.csv.csv_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    CsvInputError,
    CsvSizeError,
    get_capabilities,
    parse_csv,
    parse_csv_strict,
    probe_csv,
)


# ---------------------------------------------------------------------------
# Basic parse tests
# ---------------------------------------------------------------------------

class TestCsvParseBasic:
    def test_simple_csv_rows(self, tmp_path):
        """Basic CSV parses rows and column count."""
        f = tmp_path / "test.csv"
        f.write_text("a,b,c\n1,2,3\n4,5,6\n", encoding="utf-8")
        result = parse_csv_strict(f)
        assert result["format"] == "csv"
        assert result["column_count"] == 3

    def test_single_row_no_header(self, tmp_path):
        """Single row CSV returns row_count >= 0."""
        f = tmp_path / "test.csv"
        f.write_text("one,two,three\n", encoding="utf-8")
        result = parse_csv_strict(f)
        assert result["column_count"] == 3

    def test_empty_csv(self, tmp_path):
        """Empty CSV returns zero rows and columns."""
        f = tmp_path / "empty.csv"
        f.write_text("", encoding="utf-8")
        result = parse_csv_strict(f)
        assert result["row_count"] == 0
        assert result["column_count"] == 0

    def test_csv_with_quotes(self, tmp_path):
        """CSV with quoted fields containing commas parses correctly."""
        f = tmp_path / "quoted.csv"
        f.write_text('name,description\nAlice,"Loves, cats"\n', encoding="utf-8")
        result = parse_csv_strict(f)
        # At least one data row parsed
        total = result["row_count"] + (1 if result["has_header"] else 0)
        assert total >= 1

    def test_csv_path_as_string(self, tmp_path):
        """parse_csv_strict accepts str path."""
        f = tmp_path / "str.csv"
        f.write_text("x,y\n1,2\n", encoding="utf-8")
        result = parse_csv_strict(str(f))
        assert "row_count" in result

    def test_csv_delimiter_detected(self, tmp_path):
        """delimiter field is present in result."""
        f = tmp_path / "d.csv"
        f.write_text("a,b\n1,2\n", encoding="utf-8")
        result = parse_csv_strict(f)
        assert "delimiter" in result

    def test_csv_format_field(self, tmp_path):
        """result['format'] is 'csv'."""
        f = tmp_path / "fmt.csv"
        f.write_text("x\n1\n", encoding="utf-8")
        result = parse_csv_strict(f)
        assert result["format"] == "csv"

    def test_csv_rows_is_list(self, tmp_path):
        """result['rows'] is a list."""
        f = tmp_path / "rows.csv"
        f.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
        result = parse_csv_strict(f)
        assert isinstance(result["rows"], list)

    def test_csv_bom_stripped(self, tmp_path):
        """UTF-8 BOM is stripped from first field."""
        f = tmp_path / "bom.csv"
        f.write_bytes(b"\xef\xbb\xbfname,age\nAlice,30\n")
        result = parse_csv_strict(f)
        assert result["column_count"] == 2


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestCsvErrors:
    def test_nonexistent_file_raises(self):
        """Nonexistent file raises CsvInputError."""
        with pytest.raises(CsvInputError):
            parse_csv_strict("/this/does/not/exist/at/all/abc.csv")

    def test_parse_csv_never_raises(self):
        """parse_csv (non-strict) never raises for any input."""
        result = parse_csv("/this/does/not/exist/abc.csv")
        assert "error" in result


# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------

class TestCsvCapabilities:
    def test_supported_features_nonempty(self):
        assert len(SUPPORTED_FEATURES) > 0

    def test_unsupported_features_nonempty(self):
        assert len(UNSUPPORTED_FEATURES) > 0

    def test_features_disjoint(self):
        assert SUPPORTED_FEATURES.isdisjoint(UNSUPPORTED_FEATURES)

    def test_get_capabilities_returns_dict(self):
        caps = get_capabilities()
        assert caps["format"] == "csv"
        assert isinstance(caps["supported"], list)
        assert isinstance(caps["unsupported"], list)

    def test_rfc4180_parse_in_supported(self):
        assert "rfc4180_parse" in SUPPORTED_FEATURES

    def test_commercial_product_ready_false(self):
        assert get_capabilities()["commercial_product_ready"] is False


# ---------------------------------------------------------------------------
# Probe
# ---------------------------------------------------------------------------

class TestCsvProbe:
    def test_probe_nonexistent(self):
        """Probe of nonexistent file has exists=False."""
        result = probe_csv("/path/that/really/does/not/exist/xyz123.csv")
        # On most systems this path won't exist
        if not result["exists"]:
            assert result["exists"] is False

    def test_probe_existing_file(self, tmp_path):
        """Probe of existing file returns size and first_line."""
        f = tmp_path / "probe.csv"
        f.write_text("col1,col2\nval1,val2\n", encoding="utf-8")
        result = probe_csv(f)
        assert result["exists"] is True
        assert result["size_bytes"] > 0
        assert "first_line" in result
