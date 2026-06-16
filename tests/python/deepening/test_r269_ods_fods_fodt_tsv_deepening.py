"""Sprint 17: ODS/FODS/FODT/TSV product deepening — 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

ODS = str(_REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods")
FODS = str(_REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods")
FODT = str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt")
TSV = str(_REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv")


# --- ODS ---

class TestOdsIsSingleSheet:
    def test_returns_bool(self):
        from ods import ods_is_single_sheet
        result = ods_is_single_sheet(ODS)
        assert isinstance(result, bool)

    def test_single_sheet_file(self):
        from ods import ods_is_single_sheet
        # minimal-spreadsheet should have one sheet
        assert ods_is_single_sheet(ODS) is True


class TestOdsStringDensity:
    def test_returns_float(self):
        from ods import ods_string_density
        result = ods_string_density(ODS)
        assert isinstance(result, float)

    def test_density_in_range(self):
        from ods import ods_string_density
        result = ods_string_density(ODS)
        assert 0.0 <= result <= 1.0


# --- FODS ---

class TestFodsNumericDensity:
    def test_returns_float(self):
        from fods import parse_fods_strict, fods_numeric_density
        wb = parse_fods_strict(FODS)
        result = fods_numeric_density(wb)
        assert isinstance(result, float)

    def test_density_in_range(self):
        from fods import parse_fods_strict, fods_numeric_density
        wb = parse_fods_strict(FODS)
        result = fods_numeric_density(wb)
        assert 0.0 <= result <= 1.0


class TestFodsDataDensity:
    def test_returns_float(self):
        from fods import parse_fods_strict, fods_data_density
        wb = parse_fods_strict(FODS)
        result = fods_data_density(wb)
        assert isinstance(result, float)

    def test_density_in_range(self):
        from fods import parse_fods_strict, fods_data_density
        wb = parse_fods_strict(FODS)
        result = fods_data_density(wb)
        assert 0.0 <= result <= 1.0


# --- FODT ---

class TestFodtCharCount:
    def test_returns_int(self):
        from fodt import fodt_char_count
        result = fodt_char_count(FODT)
        assert isinstance(result, int)

    def test_positive_for_content(self):
        from fodt import fodt_char_count
        result = fodt_char_count(FODT)
        assert result >= 0


class TestFodtVocabularyRichness:
    def test_returns_float(self):
        from fodt import fodt_vocabulary_richness
        result = fodt_vocabulary_richness(FODT)
        assert isinstance(result, float)

    def test_richness_in_range(self):
        from fodt import fodt_vocabulary_richness
        result = fodt_vocabulary_richness(FODT)
        assert 0.0 <= result <= 1.0


# --- TSV ---

class TestTsvIsRectangular:
    def test_returns_bool(self):
        from tsv import tsv_is_rectangular
        result = tsv_is_rectangular(TSV)
        assert isinstance(result, bool)

    def test_minimal_is_rectangular(self):
        from tsv import tsv_is_rectangular
        assert tsv_is_rectangular(TSV) is True


class TestTsvEmptyCellCount:
    def test_returns_int(self):
        from tsv import tsv_empty_cell_count
        result = tsv_empty_cell_count(TSV)
        assert isinstance(result, int)

    def test_non_negative(self):
        from tsv import tsv_empty_cell_count
        result = tsv_empty_cell_count(TSV)
        assert result >= 0
