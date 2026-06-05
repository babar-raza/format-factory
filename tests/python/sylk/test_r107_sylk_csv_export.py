# R107 Wave 3: SYLK CSV export hardening
# 9 tests — CSV export via file path, data integrity, edge cases

import importlib
import os
import tempfile
import pytest

sylk = importlib.import_module("sylk")

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "sylk")


def _write_sylk(content: str) -> str:
    """Write SYLK content to a temp file and return the path."""
    with tempfile.NamedTemporaryFile(suffix=".slk", delete=False, mode="w", encoding="utf-8") as f:
        f.write(content)
        return f.name


class TestSylkCsvExport:
    """SYLK to CSV export via file path."""

    def test_basic_csv_export(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K42\nC;X2;Y1;K99\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            assert "42" in csv
            assert "99" in csv
        finally:
            os.unlink(path)

    def test_single_cell_csv(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K7\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            assert "7" in csv
        finally:
            os.unlink(path)

    def test_multiple_rows(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K1\nC;X1;Y2;K2\nC;X1;Y3;K3\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            lines = [l for l in csv.strip().split("\n") if l.strip()]
            assert len(lines) >= 3
        finally:
            os.unlink(path)

    def test_multiple_columns(self):
        path = _write_sylk('ID;P\nC;X1;Y1;K"a"\nC;X2;Y1;K"b"\nE')
        try:
            csv = sylk.sylk_to_csv(path)
            assert "a" in csv
            assert "b" in csv
        finally:
            os.unlink(path)

    def test_numeric_preserved(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K3.14\nE")
        try:
            csv = sylk.sylk_to_csv(path)
            assert "3.14" in csv
        finally:
            os.unlink(path)

    def test_string_preserved(self):
        path = _write_sylk('ID;P\nC;X1;Y1;K"test string"\nE')
        try:
            csv = sylk.sylk_to_csv(path)
            assert "test string" in csv
        finally:
            os.unlink(path)

    def test_parse_returns_dict(self):
        path = _write_sylk("ID;P\nC;X1;Y1;K42\nE")
        try:
            result = sylk.parse_sylk(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_sample_file_if_exists(self):
        if not os.path.isdir(SAMPLES_DIR):
            pytest.skip("No SYLK sample directory")
        samples = [f for f in os.listdir(SAMPLES_DIR) if f.endswith((".slk", ".sylk"))]
        if not samples:
            pytest.skip("No SYLK sample files")
        path = os.path.join(SAMPLES_DIR, samples[0])
        csv = sylk.sylk_to_csv(path)
        assert isinstance(csv, str)

    def test_nonexistent_file_raises(self):
        with pytest.raises(Exception):
            sylk.sylk_to_csv("/nonexistent/file.slk")
