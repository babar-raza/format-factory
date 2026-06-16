"""Sprint 21: DIF/SYLK/ABW/FODS product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

DIF = str(next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif")))
SYLK = str(next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk")))
ABW = str(_REPO / "samples" / "by-format" / "abw" / "minimal-document.abw")
FODS = str(_REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods")


# --- DIF ---

class TestDifMinNumericValue:
    def test_returns_numeric_or_none(self):
        from dif import dif_min_numeric_value
        result = dif_min_numeric_value(DIF)
        assert result is None or isinstance(result, (int, float))


class TestDifIsRectangular:
    def test_returns_bool(self):
        from dif import dif_is_rectangular
        assert isinstance(dif_is_rectangular(DIF), bool)


# --- SYLK ---

class TestSylkUniqueColumnCount:
    def test_returns_int(self):
        from sylk import sylk_unique_column_count
        assert isinstance(sylk_unique_column_count(SYLK), int)

    def test_non_negative(self):
        from sylk import sylk_unique_column_count
        assert sylk_unique_column_count(SYLK) >= 0


class TestSylkHasNumericCells:
    def test_returns_bool(self):
        from sylk import sylk_has_numeric_cells
        assert isinstance(sylk_has_numeric_cells(SYLK), bool)


# --- ABW ---

class TestAbwAverageParagraphLength:
    def test_returns_float(self):
        from abw import abw_average_paragraph_length
        assert isinstance(abw_average_paragraph_length(ABW), float)

    def test_non_negative(self):
        from abw import abw_average_paragraph_length
        assert abw_average_paragraph_length(ABW) >= 0.0


class TestAbwIsEmpty:
    def test_returns_bool(self):
        from abw import abw_is_empty
        assert isinstance(abw_is_empty(ABW), bool)


# --- FODS ---

class TestFodsStringDensity:
    def test_returns_float(self):
        from fods import parse_fods_strict, fods_string_density
        wb = parse_fods_strict(FODS)
        assert isinstance(fods_string_density(wb), float)

    def test_density_in_range(self):
        from fods import parse_fods_strict, fods_string_density
        wb = parse_fods_strict(FODS)
        assert 0.0 <= fods_string_density(wb) <= 1.0


class TestFodsIsSingleSheet:
    def test_returns_bool(self):
        from fods import parse_fods_strict, fods_is_single_sheet
        wb = parse_fods_strict(FODS)
        assert isinstance(fods_is_single_sheet(wb), bool)
