"""Tests for tsv_max_numeric_value and tsv_has_empty_rows (Sprint 39)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_max_numeric_value, tsv_has_empty_rows

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")   # Alice\t30 / Bob\t25 -> max=30.0
_MULTI = str(_DIR / "multi-column.tsv")     # has 95.5 as max numeric
_SINGLE = str(_DIR / "single-cell.tsv")     # 42 -> max=42.0


def _write_tsv(tmp_path, content: str) -> str:
    p = tmp_path / "test.tsv"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestTsvMaxNumericValue:
    def test_return_type_for_numeric_file(self):
        result = tsv_max_numeric_value(_MINIMAL)
        assert isinstance(result, float)

    def test_exact_30_for_minimal(self):
        # minimal-2x2.tsv: Alice\t30 / Bob\t25 -> max=30.0
        assert tsv_max_numeric_value(_MINIMAL) == 30.0

    def test_exact_42_for_single(self):
        assert tsv_max_numeric_value(_SINGLE) == 42.0

    def test_exact_95_5_for_multi(self):
        # multi-column.tsv has max numeric 95.5
        assert tsv_max_numeric_value(_MULTI) == 95.5

    def test_none_for_text_only(self, tmp_path):
        p = _write_tsv(tmp_path, "Alice\tBob\nCarol\tDave\n")
        assert tsv_max_numeric_value(p) is None

    def test_none_for_empty_file(self, tmp_path):
        p = _write_tsv(tmp_path, "")
        assert tsv_max_numeric_value(p) is None

    def test_consistent_across_calls(self):
        assert tsv_max_numeric_value(_MINIMAL) == tsv_max_numeric_value(_MINIMAL)


class TestTsvHasEmptyRows:
    def test_return_type(self):
        assert isinstance(tsv_has_empty_rows(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert tsv_has_empty_rows(_MINIMAL) is False

    def test_false_for_single(self):
        assert tsv_has_empty_rows(_SINGLE) is False

    def test_true_for_blank_row(self, tmp_path):
        p = _write_tsv(tmp_path, "Alice\t30\n\t\nBob\t25\n")
        assert tsv_has_empty_rows(p) is True

    def test_true_for_empty_line(self, tmp_path):
        p = _write_tsv(tmp_path, "Alice\t30\n\nBob\t25\n")
        assert tsv_has_empty_rows(p) is True

    def test_consistent_across_calls(self):
        assert tsv_has_empty_rows(_MINIMAL) == tsv_has_empty_rows(_MINIMAL)
