"""Sprint 143 — TSV tsv_string_field_ratio/tsv_word_density + ABW abw_shortest_paragraph_length/abw_word_density."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_string_field_ratio, tsv_word_density
from src.python.abw.abw_codec import abw_shortest_paragraph_length, abw_word_density

TSV = _REPO / "samples" / "by-format" / "tsv"
ABW = _REPO / "samples" / "by-format" / "abw"

# --- TSV tsv_string_field_ratio ---

class TestTsvStringFieldRatio:
    def test_minimal_returns_float(self):
        assert isinstance(tsv_string_field_ratio(TSV / "minimal-2x2.tsv"), float)

    def test_minimal_value(self):
        assert abs(tsv_string_field_ratio(TSV / "minimal-2x2.tsv") - 0.5) < 0.01

    def test_multi_column_value(self):
        assert abs(tsv_string_field_ratio(TSV / "multi-column.tsv") - 0.5) < 0.01

    def test_single_cell_value(self):
        assert tsv_string_field_ratio(TSV / "single-cell.tsv") == 0.0

    def test_range_zero_to_one(self):
        for f in TSV.glob("*.tsv"):
            v = tsv_string_field_ratio(f)
            assert 0.0 <= v <= 1.0, f"{f.name}: {v}"

# --- TSV tsv_word_density ---

class TestTsvWordDensity:
    def test_minimal_returns_float(self):
        assert isinstance(tsv_word_density(TSV / "minimal-2x2.tsv"), float)

    def test_minimal_value(self):
        assert abs(tsv_word_density(TSV / "minimal-2x2.tsv") - 0.1429) < 0.01

    def test_multi_column_value(self):
        assert abs(tsv_word_density(TSV / "multi-column.tsv") - 0.1404) < 0.01

    def test_single_cell_value(self):
        assert abs(tsv_word_density(TSV / "single-cell.tsv") - 0.0909) < 0.01

    def test_positive_for_nonempty(self):
        for f in TSV.glob("*.tsv"):
            assert tsv_word_density(f) > 0, f"{f.name}"

# --- ABW abw_shortest_paragraph_length ---

class TestAbwShortestParagraphLength:
    def test_minimal_returns_int(self):
        assert isinstance(abw_shortest_paragraph_length(ABW / "minimal-document.abw"), int)

    def test_minimal_value(self):
        assert abw_shortest_paragraph_length(ABW / "minimal-document.abw") == 5

    def test_two_paragraphs_value(self):
        assert abw_shortest_paragraph_length(ABW / "two-paragraphs.abw") == 16

    def test_empty_section_value(self):
        assert abw_shortest_paragraph_length(ABW / "empty-section.abw") == 0

    def test_non_negative(self):
        for f in ABW.glob("*.abw"):
            assert abw_shortest_paragraph_length(f) >= 0, f"{f.name}"

# --- ABW abw_word_density ---

class TestAbwWordDensity:
    def test_minimal_returns_float(self):
        assert isinstance(abw_word_density(ABW / "minimal-document.abw"), float)

    def test_minimal_value(self):
        assert abs(abw_word_density(ABW / "minimal-document.abw") - 0.00352) < 0.001

    def test_two_paragraphs_value(self):
        assert abs(abw_word_density(ABW / "two-paragraphs.abw") - 0.01084) < 0.001

    def test_empty_section_value(self):
        assert abw_word_density(ABW / "empty-section.abw") == 0.0

    def test_non_negative(self):
        for f in ABW.glob("*.abw"):
            assert abw_word_density(f) >= 0.0, f"{f.name}"
