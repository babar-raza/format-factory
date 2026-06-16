"""Tests for FOSS gap closure batch: 5 new functions across CSV, DIF, QOI, TSV.

Sprint: GAP-CLOSURE-SPRINT5-20260616
Closes: GAP-CSV-FOSS-CSV_ALL_ROWS-001, GAP-DIF-FOSS-DIF_ALL_NUME-001,
        GAP-QOI-FOSS-QOI_AVG_RGB_-001, GAP-QOI-FOSS-QOI_RED_DOMI-001,
        GAP-TSV-FOSS-TSV_ALL_ROWS-001
"""
import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


# --- CSV: csv_all_rows ---

class TestCsvAllRows:
    def test_returns_list(self):
        from src.python.csv.csv_parser import csv_all_rows
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        Path(path).write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
        try:
            result = csv_all_rows(path)
            assert isinstance(result, list)
            assert len(result) == 2
        finally:
            os.unlink(path)

    def test_row_contents(self):
        from src.python.csv.csv_parser import csv_all_rows
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        Path(path).write_text("x,y\nhello,world\n", encoding="utf-8")
        try:
            rows = csv_all_rows(path)
            assert any(row == ["hello", "world"] for row in rows)
        finally:
            os.unlink(path)

    def test_empty_file(self):
        from src.python.csv.csv_parser import csv_all_rows
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        Path(path).write_text("", encoding="utf-8")
        try:
            rows = csv_all_rows(path)
            assert isinstance(rows, list)
        finally:
            os.unlink(path)


# --- DIF: dif_all_numeric_column ---

class TestDifAllNumericColumn:
    def _dif_sample(self):
        files = sorted((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))
        assert files, "No DIF samples"
        return str(files[0])

    def test_returns_bool(self):
        from dif import dif_all_numeric_column
        result = dif_all_numeric_column(self._dif_sample(), 0)
        assert isinstance(result, bool)

    def test_col_zero(self):
        from dif import dif_all_numeric_column
        result = dif_all_numeric_column(self._dif_sample(), 0)
        assert result is True or result is False

    def test_high_col_index(self):
        from dif import dif_all_numeric_column
        result = dif_all_numeric_column(self._dif_sample(), 999)
        assert result is True  # vacuously true — no cells at that index

    def test_consistent_with_all_numeric(self):
        from dif import dif_all_numeric_column, dif_all_numeric, dif_column_count
        path = self._dif_sample()
        whole = dif_all_numeric(path)
        ncols = dif_column_count(path)
        per_col = all(dif_all_numeric_column(path, i) for i in range(ncols))
        # If every column is all-numeric, the whole file should be too
        if per_col:
            assert whole is True

    def test_string_column_returns_false(self):
        from dif import dif_all_numeric_column, parse_dif_strict
        path = self._dif_sample()
        doc = parse_dif_strict(path)
        # Find a column with any non-numeric value
        for col_idx in range(len(doc.rows[0]) if doc.rows else 0):
            has_string = False
            for row in doc.rows:
                if col_idx < len(row):
                    val = str(row[col_idx].value).strip() if row[col_idx].value else ""
                    if val:
                        try:
                            float(val)
                        except (ValueError, TypeError):
                            has_string = True
                            break
            if has_string:
                assert dif_all_numeric_column(path, col_idx) is False
                return
        # If no string column found, test is vacuously valid


# --- QOI: qoi_avg_rgb, qoi_red_dominant ---

class TestQoiAvgRgb:
    def _qoi_sample(self):
        files = sorted((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
        assert files, "No QOI samples"
        return str(files[0])

    def test_returns_tuple(self):
        from qoi import qoi_avg_rgb
        result = qoi_avg_rgb(self._qoi_sample())
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_values_nonnegative(self):
        from qoi import qoi_avg_rgb
        r, g, b = qoi_avg_rgb(self._qoi_sample())
        assert r >= 0.0 and g >= 0.0 and b >= 0.0

    def test_values_within_range(self):
        from qoi import qoi_avg_rgb
        r, g, b = qoi_avg_rgb(self._qoi_sample())
        assert r <= 255.0 and g <= 255.0 and b <= 255.0


class TestQoiRedDominant:
    def _qoi_sample(self):
        files = sorted((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
        assert files, "No QOI samples"
        return str(files[0])

    def test_returns_bool(self):
        from qoi import qoi_red_dominant
        result = qoi_red_dominant(self._qoi_sample())
        assert isinstance(result, bool)

    def test_consistent_with_avg_rgb(self):
        from qoi import qoi_avg_rgb, qoi_red_dominant
        r, g, b = qoi_avg_rgb(self._qoi_sample())
        rd = qoi_red_dominant(self._qoi_sample())
        if r > g and r > b:
            assert rd is True
        else:
            assert rd is False


# --- TSV: tsv_all_rows ---

class TestTsvAllRows:
    def test_returns_list(self):
        from tsv import tsv_all_rows
        fd, path = tempfile.mkstemp(suffix=".tsv")
        os.close(fd)
        Path(path).write_text("a\tb\n1\t2\n3\t4\n", encoding="utf-8")
        try:
            result = tsv_all_rows(path)
            assert isinstance(result, list)
            assert len(result) == 2
        finally:
            os.unlink(path)

    def test_row_contents(self):
        from tsv import tsv_all_rows
        fd, path = tempfile.mkstemp(suffix=".tsv")
        os.close(fd)
        Path(path).write_text("x\ty\nhello\tworld\n", encoding="utf-8")
        try:
            rows = tsv_all_rows(path)
            assert rows[0] == ["hello", "world"]
        finally:
            os.unlink(path)

    def test_single_row(self):
        from tsv import tsv_all_rows
        fd, path = tempfile.mkstemp(suffix=".tsv")
        os.close(fd)
        Path(path).write_text("col\nval\n", encoding="utf-8")
        try:
            rows = tsv_all_rows(path)
            assert len(rows) == 1
        finally:
            os.unlink(path)

    def test_each_row_is_list(self):
        from tsv import tsv_all_rows
        fd, path = tempfile.mkstemp(suffix=".tsv")
        os.close(fd)
        Path(path).write_text("a\tb\n1\t2\n3\t4\n", encoding="utf-8")
        try:
            rows = tsv_all_rows(path)
            for row in rows:
                assert isinstance(row, list)
        finally:
            os.unlink(path)

    def test_tab_splitting(self):
        from tsv import tsv_all_rows
        fd, path = tempfile.mkstemp(suffix=".tsv")
        os.close(fd)
        Path(path).write_text("h1\th2\th3\nA\tB\tC\n", encoding="utf-8")
        try:
            rows = tsv_all_rows(path)
            data_row = [r for r in rows if "A" in r]
            assert len(data_row) == 1
            assert len(data_row[0]) == 3
        finally:
            os.unlink(path)
