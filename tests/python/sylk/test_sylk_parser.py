"""Gate 4 prototype tests for SYLK parser."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from sylk.sylk_parser import (
    parse_sylk_strict, parse_sylk, probe_sylk,
    SylkError, SylkInvalidFormatError,
)

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "sylk")


class TestSylkParser:
    def test_parse_minimal_2x2(self):
        doc = parse_sylk_strict(os.path.join(SAMPLES, "valid", "minimal-2x2.slk"))
        assert doc.rows == 2
        assert doc.cols == 2
        assert len(doc.cells) == 4

    def test_parse_single_cell(self):
        doc = parse_sylk_strict(os.path.join(SAMPLES, "valid", "single-cell.slk"))
        assert doc.rows == 1
        assert doc.cols == 1
        assert len(doc.cells) == 1
        assert doc.cells[0].value == 99

    def test_parse_numeric_row(self):
        doc = parse_sylk_strict(os.path.join(SAMPLES, "valid", "numeric-row.slk"))
        assert doc.rows == 1
        assert doc.cols == 3
        values = [c.value for c in doc.cells]
        assert values == [1, 2, 3]

    def test_invalid_missing_id(self):
        with pytest.raises(SylkInvalidFormatError):
            parse_sylk_strict(os.path.join(SAMPLES, "invalid", "missing-id-record.slk"))

    def test_file_not_found(self):
        with pytest.raises(SylkError):
            parse_sylk_strict("/nonexistent/path.slk")

    def test_dict_api_success(self):
        result = parse_sylk(os.path.join(SAMPLES, "valid", "single-cell.slk"))
        assert result["ok"] is True
        assert result["rows"] == 1
        assert result["cols"] == 1
        assert result["cell_count"] == 1

    def test_dict_api_failure(self):
        result = parse_sylk(os.path.join(SAMPLES, "invalid", "missing-id-record.slk"))
        assert result["ok"] is False

    def test_probe_valid(self):
        result = probe_sylk(os.path.join(SAMPLES, "valid", "minimal-2x2.slk"))
        assert result["valid_header"] is True
        assert result["id_line"].startswith("ID")

    def test_probe_invalid(self):
        result = probe_sylk(os.path.join(SAMPLES, "invalid", "missing-id-record.slk"))
        assert result["valid_header"] is False

    def test_probe_nonexistent(self):
        result = probe_sylk("/nonexistent/path.slk")
        assert result["exists"] is False
