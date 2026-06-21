"""Sprint R426 — CSV/TSV/DIF/SYLK/ABW deepening: column_count_squared, total_cells_plus_column_count variants."""
import sys, pathlib, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_column_count_squared, csv_total_cells_plus_column_count, csv_column_count, csv_total_field_count
from src.python.tsv.tsv_parser import tsv_column_count_squared, tsv_total_cells_plus_column_count, tsv_column_count, tsv_total_field_count
from src.python.dif.dif_parser import dif_column_count_squared, dif_total_cells_plus_column_count, dif_column_count, dif_total_cell_count
from src.python.sylk.sylk_parser import sylk_row_count_squared, sylk_total_cells_plus_column_count, parse_sylk_strict
from src.python.abw.abw_codec import abw_char_count_squared, abw_total_words_plus_char_count, abw_total_char_count, abw_word_count

_SAMPLES = _REPO / "samples" / "by-format"
_CSV = _SAMPLES / "csv" / "minimal-2x2.csv"
_TSV = _SAMPLES / "tsv" / "minimal-2x2.tsv"
_DIF = _SAMPLES / "dif" / "valid" / "minimal-2x2.dif"
_SYLK = _SAMPLES / "sylk" / "valid" / "minimal-2x2.slk"
_ABW = _SAMPLES / "abw" / "minimal-document.abw"


# === CSV ===
class TestCsvColumnCountSquared:
    def test_returns_int(self):
        assert isinstance(csv_column_count_squared(_CSV), int)

    def test_equals_square(self):
        cc = csv_column_count(_CSV)
        assert csv_column_count_squared(_CSV) == cc * cc

    def test_non_negative(self):
        assert csv_column_count_squared(_CSV) >= 0


class TestCsvTotalCellsPlusColumnCount:
    def test_returns_int(self):
        assert isinstance(csv_total_cells_plus_column_count(_CSV), int)

    def test_equals_sum(self):
        assert csv_total_cells_plus_column_count(_CSV) == csv_total_field_count(_CSV) + csv_column_count(_CSV)

    def test_exceeds_column_count(self):
        assert csv_total_cells_plus_column_count(_CSV) >= csv_column_count(_CSV)


# === TSV ===
class TestTsvColumnCountSquared:
    def test_returns_int(self):
        assert isinstance(tsv_column_count_squared(_TSV), int)

    def test_equals_square(self):
        cc = tsv_column_count(_TSV)
        assert tsv_column_count_squared(_TSV) == cc * cc

    def test_non_negative(self):
        assert tsv_column_count_squared(_TSV) >= 0


class TestTsvTotalCellsPlusColumnCount:
    def test_returns_int(self):
        assert isinstance(tsv_total_cells_plus_column_count(_TSV), int)

    def test_equals_sum(self):
        assert tsv_total_cells_plus_column_count(_TSV) == tsv_total_field_count(_TSV) + tsv_column_count(_TSV)

    def test_exceeds_column_count(self):
        assert tsv_total_cells_plus_column_count(_TSV) >= tsv_column_count(_TSV)


# === DIF ===
class TestDifColumnCountSquared:
    def test_returns_int(self):
        assert isinstance(dif_column_count_squared(_DIF), int)

    def test_equals_square(self):
        cc = dif_column_count(_DIF)
        assert dif_column_count_squared(_DIF) == cc * cc

    def test_non_negative(self):
        assert dif_column_count_squared(_DIF) >= 0


class TestDifTotalCellsPlusColumnCount:
    def test_returns_int(self):
        assert isinstance(dif_total_cells_plus_column_count(_DIF), int)

    def test_equals_sum(self):
        assert dif_total_cells_plus_column_count(_DIF) == dif_total_cell_count(_DIF) + dif_column_count(_DIF)

    def test_exceeds_column_count(self):
        assert dif_total_cells_plus_column_count(_DIF) >= dif_column_count(_DIF)


# === SYLK ===
class TestSylkRowCountSquared:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_squared(_SYLK), int)

    def test_equals_square(self):
        doc = parse_sylk_strict(_SYLK)
        rc = len({c.row for c in doc.cells})
        assert sylk_row_count_squared(_SYLK) == rc * rc

    def test_non_negative(self):
        assert sylk_row_count_squared(_SYLK) >= 0


class TestSylkTotalCellsPlusColumnCount:
    def test_returns_int(self):
        assert isinstance(sylk_total_cells_plus_column_count(_SYLK), int)

    def test_equals_sum(self):
        doc = parse_sylk_strict(_SYLK)
        cols = len({c.col for c in doc.cells})
        assert sylk_total_cells_plus_column_count(_SYLK) == len(doc.cells) + cols

    def test_exceeds_column_count(self):
        doc = parse_sylk_strict(_SYLK)
        cols = len({c.col for c in doc.cells})
        assert sylk_total_cells_plus_column_count(_SYLK) >= cols


# === ABW ===
class TestAbwCharCountSquared:
    def test_returns_int(self):
        assert isinstance(abw_char_count_squared(_ABW), int)

    def test_equals_square(self):
        cc = abw_total_char_count(_ABW)
        assert abw_char_count_squared(_ABW) == cc * cc

    def test_non_negative(self):
        assert abw_char_count_squared(_ABW) >= 0


class TestAbwTotalWordsPlusCharCount:
    def test_returns_int(self):
        assert isinstance(abw_total_words_plus_char_count(_ABW), int)

    def test_equals_sum(self):
        assert abw_total_words_plus_char_count(_ABW) == abw_word_count(_ABW) + abw_total_char_count(_ABW)

    def test_exceeds_char_count(self):
        assert abw_total_words_plus_char_count(_ABW) >= abw_total_char_count(_ABW)
