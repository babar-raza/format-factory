"""R84 Train N: Tests for sylk_to_csv export function."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from sylk.sylk_parser import sylk_to_csv, SylkError

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "sylk")


class TestSylkToCsv:
    def test_minimal_2x2_produces_csv(self):
        csv_text = sylk_to_csv(os.path.join(SAMPLES, "valid", "minimal-2x2.slk"))
        assert isinstance(csv_text, str)
        assert len(csv_text) > 0

    def test_csv_has_crlf_line_endings(self):
        csv_text = sylk_to_csv(os.path.join(SAMPLES, "valid", "minimal-2x2.slk"))
        assert "\r\n" in csv_text

    def test_single_cell_produces_one_row(self):
        csv_text = sylk_to_csv(os.path.join(SAMPLES, "valid", "single-cell.slk"))
        lines = [l for l in csv_text.split("\r\n") if l]
        assert len(lines) == 1

    def test_numeric_row_csv_contains_numbers(self):
        csv_text = sylk_to_csv(os.path.join(SAMPLES, "valid", "numeric-row.slk"))
        # Should contain digit characters
        assert any(c.isdigit() for c in csv_text)

    def test_csv_fields_count_matches_columns(self):
        csv_text = sylk_to_csv(os.path.join(SAMPLES, "valid", "minimal-2x2.slk"))
        lines = [l for l in csv_text.split("\r\n") if l]
        for line in lines:
            fields = line.split(",")
            assert len(fields) == 2  # 2x2 grid has 2 columns

    def test_missing_file_raises_sylk_error(self):
        with pytest.raises(SylkError):
            sylk_to_csv("/nonexistent/path/file.slk")

    def test_invalid_file_raises_sylk_error(self):
        with pytest.raises(SylkError):
            sylk_to_csv(os.path.join(SAMPLES, "invalid", "missing-id-record.slk"))

    def test_roundtrip_values_preserved(self):
        """Values from single-cell fixture should appear in CSV output."""
        from sylk.sylk_parser import parse_sylk_strict
        doc = parse_sylk_strict(os.path.join(SAMPLES, "valid", "single-cell.slk"))
        csv_text = sylk_to_csv(os.path.join(SAMPLES, "valid", "single-cell.slk"))
        assert str(doc.cells[0].value) in csv_text
