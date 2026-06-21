"""Sprint 135 — TSV numeric_ratio/is_all_numeric, ABW bytes_per_char/is_empty_document."""
import sys, pathlib, pytest
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.tsv.tsv_parser import tsv_numeric_ratio, tsv_is_all_numeric
from src.python.abw.abw_codec import abw_bytes_per_char, abw_is_empty_document

T1 = str(_REPO / "samples/by-format/tsv/minimal-2x2.tsv")
T2 = str(_REPO / "samples/by-format/tsv/multi-column.tsv")
T3 = str(_REPO / "samples/by-format/tsv/single-cell.tsv")
A1 = str(_REPO / "samples/by-format/abw/minimal-document.abw")
A2 = str(_REPO / "samples/by-format/abw/two-paragraphs.abw")
A3 = str(_REPO / "samples/by-format/abw/empty-section.abw")

class TestTsvNumericRatio:
    def test_minimal(self):
        assert tsv_numeric_ratio(T1) == 0.5
    def test_multi(self):
        assert tsv_numeric_ratio(T2) == 0.5
    def test_single(self):
        assert tsv_numeric_ratio(T3) == 1.0
    def test_return_type(self):
        assert isinstance(tsv_numeric_ratio(T1), float)
    def test_bounded(self):
        assert 0.0 <= tsv_numeric_ratio(T1) <= 1.0

class TestTsvIsAllNumeric:
    def test_minimal(self):
        assert tsv_is_all_numeric(T1) is False
    def test_multi(self):
        assert tsv_is_all_numeric(T2) is False
    def test_single(self):
        assert tsv_is_all_numeric(T3) is True
    def test_return_type(self):
        assert isinstance(tsv_is_all_numeric(T1), bool)
    def test_consistency(self):
        assert tsv_is_all_numeric(T3) == (tsv_numeric_ratio(T3) == 1.0)

class TestAbwBytesPerChar:
    def test_minimal(self):
        assert abw_bytes_per_char(A1) == 56.8
    def test_two_para(self):
        assert abs(abw_bytes_per_char(A2) - 11.1818) < 0.01
    def test_empty(self):
        assert abw_bytes_per_char(A3) == 0.0
    def test_return_type(self):
        assert isinstance(abw_bytes_per_char(A1), float)
    def test_positive(self):
        assert abw_bytes_per_char(A1) > 0

class TestAbwIsEmptyDocument:
    def test_minimal(self):
        assert abw_is_empty_document(A1) is False
    def test_two_para(self):
        assert abw_is_empty_document(A2) is False
    def test_empty(self):
        assert abw_is_empty_document(A3) is True
    def test_return_type(self):
        assert isinstance(abw_is_empty_document(A1), bool)
    def test_consistency(self):
        assert abw_is_empty_document(A3) == (abw_bytes_per_char(A3) == 0.0)
