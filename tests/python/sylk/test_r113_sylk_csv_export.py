"""R113 FOSS: SYLK to CSV export workflow."""
import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from sylk.sylk_parser import parse_sylk, parse_sylk_strict, write_sylk, SylkDocument, SylkCell, sylk_to_csv


class TestR113SylkCsvExport:
    def _make_doc(self, rows_data):
        cells = []
        for r, row in enumerate(rows_data):
            for c, val in enumerate(row):
                if val != "":
                    try:
                        numeric_val = float(val)
                        cells.append(SylkCell(row=r + 1, col=c + 1, value=numeric_val, value_type="numeric"))
                    except (ValueError, TypeError):
                        cells.append(SylkCell(row=r + 1, col=c + 1, value=str(val), value_type="string"))
        num_rows = len(rows_data)
        num_cols = max((len(row) for row in rows_data), default=0)
        return SylkDocument(cells=cells, rows=num_rows, cols=num_cols)

    def test_write_then_csv_export(self):
        doc = self._make_doc([["Name", "Age"], ["Alice", "30"], ["Bob", "25"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            csv = sylk_to_csv(path)
            assert "Alice" in csv
            assert "Bob" in csv
        finally:
            os.unlink(path)

    def test_csv_export_contains_all_values(self):
        doc = self._make_doc([["X", "Y"], ["1", "2"], ["3", "4"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            csv = sylk_to_csv(path)
            for val in ["X", "Y", "1", "2", "3", "4"]:
                assert val in csv
        finally:
            os.unlink(path)

    def test_csv_export_single_cell(self):
        doc = self._make_doc([["Solo"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            csv = sylk_to_csv(path)
            assert "Solo" in csv
        finally:
            os.unlink(path)

    def test_csv_export_empty_doc(self):
        doc = SylkDocument(cells=[], rows=0, cols=0)
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            csv = sylk_to_csv(path)
            assert isinstance(csv, str)
        finally:
            os.unlink(path)

    def test_csv_export_numeric_values(self):
        doc = self._make_doc([["Value"], ["42.5"], ["100"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            csv = sylk_to_csv(path)
            assert "42.5" in csv or "42" in csv
        finally:
            os.unlink(path)

    def test_parse_then_csv_roundtrip(self):
        doc = self._make_doc([["A", "B"], ["C", "D"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            result = parse_sylk(path)
            assert result["ok"] is True
            csv = sylk_to_csv(path)
            assert len(csv) > 0
        finally:
            os.unlink(path)

    def test_csv_export_large_grid(self):
        rows = [[f"R{r}C{c}" for c in range(5)] for r in range(10)]
        doc = self._make_doc(rows)
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            csv = sylk_to_csv(path)
            assert "R0C0" in csv
            assert "R9C4" in csv
        finally:
            os.unlink(path)

    def test_csv_has_newlines(self):
        doc = self._make_doc([["A"], ["B"], ["C"]])
        with tempfile.NamedTemporaryFile(suffix=".sylk", delete=False, mode="w") as f:
            path = f.name
        try:
            write_sylk(doc, path)
            csv = sylk_to_csv(path)
            assert "\n" in csv or "\r" in csv
        finally:
            os.unlink(path)
