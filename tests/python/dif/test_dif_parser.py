"""Gate 4 prototype tests for DIF parser."""

import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import pytest
from dif.dif_parser import (
    DifDocument,
    DifError,
    DifInvalidFormatError,
    DifSizeError,
    parse_dif,
    parse_dif_strict,
    probe_dif,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "dif"


class TestDifParserValidSamples:
    """Parse tests against valid DIF samples."""

    def test_minimal_2x2(self):
        doc = parse_dif_strict(SAMPLES / "valid" / "minimal-2x2.dif")
        assert isinstance(doc, DifDocument)
        assert doc.title == "minimal"
        assert doc.vectors == 2
        assert doc.tuples == 2
        assert len(doc.rows) >= 1

    def test_single_cell(self):
        doc = parse_dif_strict(SAMPLES / "valid" / "single-cell.dif")
        assert doc.title == "single-cell"
        assert doc.vectors == 1
        assert len(doc.rows) >= 1

    def test_numeric_row(self):
        doc = parse_dif_strict(SAMPLES / "valid" / "numeric-row.dif")
        assert doc.title == "numeric-row"
        assert doc.vectors == 3
        assert len(doc.rows) >= 1
        values = [c.value for c in doc.rows[0] if c.value_type == "numeric"]
        assert values == [1.0, 2.0, 3.0]


class TestDifParserInvalid:
    """Tests for invalid inputs."""

    def test_missing_table_header(self):
        with pytest.raises(DifInvalidFormatError):
            parse_dif_strict(SAMPLES / "invalid" / "missing-table-header.dif")

    def test_nonexistent_file(self):
        result = parse_dif("/nonexistent/file.dif")
        assert result["ok"] is False

    def test_empty_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".dif", delete=False, mode="w")
        tmp.close()
        with pytest.raises(DifInvalidFormatError):
            parse_dif_strict(tmp.name)


class TestDifDictOutput:
    """Tests for dict output structure."""

    def test_dict_has_expected_keys(self):
        result = parse_dif(SAMPLES / "valid" / "minimal-2x2.dif")
        assert result["ok"] is True
        assert "title" in result
        assert "vectors" in result
        assert "tuples" in result
        assert "row_count" in result

    def test_error_dict_has_expected_keys(self):
        result = parse_dif("/nonexistent_path_that_does_not_exist_anywhere")
        assert result["ok"] is False
        assert "error" in result


class TestDifProbe:
    """Tests for probe_dif."""

    def test_probe_valid(self):
        result = probe_dif(SAMPLES / "valid" / "minimal-2x2.dif")
        assert result["valid_header"] is True
        assert result["title"] == "minimal"

    def test_probe_nonexistent(self):
        result = probe_dif("/nonexistent_path_that_does_not_exist_anywhere")
        assert result["exists"] is False
