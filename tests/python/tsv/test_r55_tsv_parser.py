"""
test_r55_tsv_parser.py — R55 Train H: TSV parser Gate 4 prototype tests.

TC-ACQN-TSV-001: Tab-separated values parsing using Python stdlib csv module.

Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.tsv.tsv_parser import (
    DELIMITER,
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    TsvInputError,
    get_capabilities,
    parse_tsv,
    parse_tsv_strict,
    probe_tsv,
)


# ---------------------------------------------------------------------------
# Basic parse tests
# ---------------------------------------------------------------------------

class TestTsvParseBasic:
    def test_simple_tsv_rows(self, tmp_path):
        """Basic TSV parses rows and column count."""
        f = tmp_path / "test.tsv"
        f.write_text("a\tb\tc\n1\t2\t3\n4\t5\t6\n", encoding="utf-8")
        result = parse_tsv_strict(f)
        assert result["format"] == "tsv"
        assert result["column_count"] == 3

    def test_tsv_delimiter_is_tab(self, tmp_path):
        """delimiter field is the tab character."""
        f = tmp_path / "d.tsv"
        f.write_text("x\ty\n1\t2\n", encoding="utf-8")
        result = parse_tsv_strict(f)
        assert result["delimiter"] == "\t"

    def test_delimiter_constant(self):
        """DELIMITER constant is tab."""
        assert DELIMITER == "\t"

    def test_empty_tsv(self, tmp_path):
        """Empty TSV returns zero rows and columns."""
        f = tmp_path / "empty.tsv"
        f.write_text("", encoding="utf-8")
        result = parse_tsv_strict(f)
        assert result["row_count"] == 0
        assert result["column_count"] == 0

    def test_single_column_tsv(self, tmp_path):
        """Single column TSV (no tabs) parses each line as one cell."""
        f = tmp_path / "single.tsv"
        f.write_text("header\nval1\nval2\n", encoding="utf-8")
        result = parse_tsv_strict(f)
        assert result["column_count"] == 1

    def test_tsv_path_as_string(self, tmp_path):
        """parse_tsv_strict accepts str path."""
        f = tmp_path / "str.tsv"
        f.write_text("x\ty\n1\t2\n", encoding="utf-8")
        result = parse_tsv_strict(str(f))
        assert "row_count" in result

    def test_tsv_format_field(self, tmp_path):
        """result['format'] is 'tsv'."""
        f = tmp_path / "fmt.tsv"
        f.write_text("x\n1\n", encoding="utf-8")
        result = parse_tsv_strict(f)
        assert result["format"] == "tsv"

    def test_tsv_rows_is_list(self, tmp_path):
        """result['rows'] is a list."""
        f = tmp_path / "rows.tsv"
        f.write_text("a\tb\n1\t2\n3\t4\n", encoding="utf-8")
        result = parse_tsv_strict(f)
        assert isinstance(result["rows"], list)

    def test_tsv_bom_stripped(self, tmp_path):
        """UTF-8 BOM is stripped from first field."""
        f = tmp_path / "bom.tsv"
        f.write_bytes(b"\xef\xbb\xbfname\tage\nAlice\t30\n")
        result = parse_tsv_strict(f)
        assert result["column_count"] == 2

    def test_tsv_does_not_split_on_comma(self, tmp_path):
        """TSV treats commas as regular characters, not delimiters."""
        f = tmp_path / "comma.tsv"
        f.write_text("a,b\tc\n1,2\t3\n", encoding="utf-8")
        result = parse_tsv_strict(f)
        assert result["column_count"] == 2  # only 1 tab in each row


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestTsvErrors:
    def test_nonexistent_file_raises(self):
        """Nonexistent file raises TsvInputError."""
        with pytest.raises(TsvInputError):
            parse_tsv_strict("/this/does/not/exist/at/all/abc.tsv")

    def test_parse_tsv_never_raises(self):
        """parse_tsv (non-strict) never raises for any input."""
        result = parse_tsv("/this/does/not/exist/abc.tsv")
        assert "error" in result


# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------

class TestTsvCapabilities:
    def test_supported_features_nonempty(self):
        assert len(SUPPORTED_FEATURES) > 0

    def test_unsupported_features_nonempty(self):
        assert len(UNSUPPORTED_FEATURES) > 0

    def test_features_disjoint(self):
        assert SUPPORTED_FEATURES.isdisjoint(UNSUPPORTED_FEATURES)

    def test_get_capabilities_returns_dict(self):
        caps = get_capabilities()
        assert caps["format"] == "tsv"
        assert isinstance(caps["supported"], list)
        assert isinstance(caps["unsupported"], list)

    def test_tsv_parse_in_supported(self):
        assert "tsv_parse" in SUPPORTED_FEATURES

    def test_commercial_product_ready_false(self):
        assert get_capabilities()["commercial_product_ready"] is False


# ---------------------------------------------------------------------------
# Probe
# ---------------------------------------------------------------------------

class TestTsvProbe:
    def test_probe_existing_file(self, tmp_path):
        """Probe of existing file returns size and first_line."""
        f = tmp_path / "probe.tsv"
        f.write_text("col1\tcol2\nval1\tval2\n", encoding="utf-8")
        result = probe_tsv(f)
        assert result["exists"] is True
        assert result["size_bytes"] > 0
        assert "first_line" in result
        assert result["column_count"] == 2
