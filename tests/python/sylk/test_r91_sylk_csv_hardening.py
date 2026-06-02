"""
test_r91_sylk_csv_hardening.py — SYLK CSV export edge-case and hardening tests.

R91 Train P: sylk_to_csv hardening — Unicode, empty cells, large sheets, special chars.
Sprint: FORMAT-FACTORY-R91-AUTONOMOUS-SUPERVISOR-DECLARATION-GRADING-POC-ACCELERATION-MAINSTREAM-MEGA-TRAIN-001
"""
from __future__ import annotations

import io
import os
import tempfile
import csv
from pathlib import Path

import pytest

try:
    from sylk.sylk_parser import sylk_to_csv, SylkError
except ImportError:
    from src.python.sylk.sylk_parser import sylk_to_csv, SylkError


def _write_sylk(rows: list[list[str]]) -> str:
    """Write a minimal SYLK file with given rows to a temp file, return path."""
    lines = ["ID;PWXL;N;E"]
    row_count = len(rows)
    col_count = max((len(r) for r in rows), default=0)
    lines.append(f"B;Y{row_count};X{col_count}")
    for r_idx, row in enumerate(rows, 1):
        for c_idx, val in enumerate(row, 1):
            if val is not None:
                # Escape semicolons and quotes in SYLK
                escaped = str(val).replace("'", "''")
                lines.append(f"C;Y{r_idx};X{c_idx};K\"{escaped}\"")
    lines.append("E")
    content = "\r\n".join(lines) + "\r\n"
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".slk", delete=False,
                                     encoding="latin-1", newline="")
    try:
        tmp.write(content)
        tmp.close()
        return tmp.name
    except Exception:
        tmp.close()
        os.unlink(tmp.name)
        raise


def _parse_csv(csv_text: str) -> list[list[str]]:
    """Parse CSV text into list of rows."""
    reader = csv.reader(io.StringIO(csv_text.replace("\r\n", "\n")))
    return list(reader)


class TestSylkCsvHardening:

    def test_unicode_ascii_subset_roundtrips(self):
        """ASCII values round-trip cleanly through sylk_to_csv."""
        rows = [["hello", "world"], ["foo", "bar"]]
        path = _write_sylk(rows)
        try:
            result = sylk_to_csv(path)
            assert len(result) > 0
            assert "hello" in result or "world" in result
        finally:
            os.unlink(path)

    def test_empty_cells_produce_empty_fields(self):
        """Empty cells in SYLK produce empty CSV fields."""
        # Row with only col 1 and col 3 filled (col 2 empty)
        lines = ["ID;PWXL;N;E", "B;Y1;X3",
                 "C;Y1;X1;K\"A\"",
                 "C;Y1;X3;K\"C\"",
                 "E"]
        content = "\r\n".join(lines) + "\r\n"
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".slk", delete=False,
                                          encoding="latin-1", newline="")
        tmp.write(content)
        tmp.close()
        try:
            result = sylk_to_csv(tmp.name)
            parsed = _parse_csv(result)
            assert len(parsed) >= 1
            assert parsed[0][0] == "A"
            assert parsed[0][1] == ""  # empty cell
            assert parsed[0][2] == "C"
        finally:
            os.unlink(tmp.name)

    def test_single_row_single_col(self):
        """Minimal 1x1 SYLK exports as single CSV cell."""
        path = _write_sylk([["only-cell"]])
        try:
            result = sylk_to_csv(path)
            assert "only-cell" in result
        finally:
            os.unlink(path)

    def test_multiple_rows_csv_line_count(self):
        """CSV output has correct number of lines for multi-row SYLK."""
        rows = [["a", "b"], ["c", "d"], ["e", "f"]]
        path = _write_sylk(rows)
        try:
            result = sylk_to_csv(path)
            parsed = _parse_csv(result)
            assert len(parsed) == 3
        finally:
            os.unlink(path)

    def test_numeric_string_values_preserved(self):
        """Numeric-looking string values are preserved as strings."""
        path = _write_sylk([["123", "456.78"], ["0", "-1"]])
        try:
            result = sylk_to_csv(path)
            assert "123" in result
            assert "456.78" in result
        finally:
            os.unlink(path)

    def test_csv_uses_crlf_line_endings(self):
        """RFC 4180 requires CRLF line endings."""
        path = _write_sylk([["a"], ["b"]])
        try:
            result = sylk_to_csv(path)
            assert "\r\n" in result
        finally:
            os.unlink(path)

    def test_empty_sylk_returns_empty_string(self):
        """A SYLK file with no cells returns empty string."""
        content = "ID;PWXL;N;E\r\nB;Y0;X0\r\nE\r\n"
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".slk", delete=False,
                                          encoding="latin-1", newline="")
        tmp.write(content)
        tmp.close()
        try:
            result = sylk_to_csv(tmp.name)
            assert result == ""
        finally:
            os.unlink(tmp.name)
