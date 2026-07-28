"""Tests for R1234: TsvDocument row count scale classification properties.

Properties under test:
    is_large         — row_count > 10000
    is_tiny          — row_count <= 5
    has_uniform_rows — all rows have column_count columns; True for empty docs

spec_fact_ref: SAL-TSV-00001
"""

import pytest
from tsv.models import TsvDocument


def _make_doc(row_count: int, col_count: int = 3, has_header: bool = True,
              jagged: bool = False) -> TsvDocument:
    """Build a TsvDocument stub with the given dimensions."""
    headers = [f"col{i}" for i in range(col_count)] if has_header else []
    if jagged:
        rows = [[f"v{r}c{c}" for c in range(col_count)] for r in range(row_count - 1)]
        rows.append(["extra"] * (col_count + 1))
    else:
        rows = [[f"v{r}c{c}" for c in range(col_count)] for r in range(row_count)]
    data = {
        "headers": headers,
        "rows": rows,
        "row_count": len(rows),
        "has_header": has_header,
        "path": "test.tsv",
    }
    return TsvDocument(data)


# ── is_large ──────────────────────────────────────────────────────────────────

class TestIsLarge:
    def test_over_10000_rows_is_large(self):
        doc = _make_doc(10001)
        assert doc.is_large is True

    def test_exactly_10000_not_large(self):
        doc = _make_doc(10000)
        assert doc.is_large is False

    def test_below_10000_not_large(self):
        doc = _make_doc(5000)
        assert doc.is_large is False

    def test_empty_not_large(self):
        doc = _make_doc(0)
        assert doc.is_large is False

    def test_single_row_not_large(self):
        doc = _make_doc(1)
        assert doc.is_large is False


# ── is_tiny ───────────────────────────────────────────────────────────────────

class TestIsTiny:
    def test_empty_is_tiny(self):
        doc = _make_doc(0)
        assert doc.is_tiny is True

    def test_single_row_is_tiny(self):
        doc = _make_doc(1)
        assert doc.is_tiny is True

    def test_five_rows_is_tiny(self):
        doc = _make_doc(5)
        assert doc.is_tiny is True

    def test_six_rows_not_tiny(self):
        doc = _make_doc(6)
        assert doc.is_tiny is False

    def test_large_doc_not_tiny(self):
        doc = _make_doc(1000)
        assert doc.is_tiny is False


# ── has_uniform_rows ──────────────────────────────────────────────────────────

class TestHasUniformRows:
    def test_empty_doc_is_uniform(self):
        doc = _make_doc(0)
        assert doc.has_uniform_rows is True

    def test_uniform_rows_all_match(self):
        doc = _make_doc(10, col_count=4)
        assert doc.has_uniform_rows is True

    def test_jagged_rows_not_uniform(self):
        doc = _make_doc(5, col_count=3, jagged=True)
        assert doc.has_uniform_rows is False

    def test_single_row_is_uniform(self):
        doc = _make_doc(1, col_count=2)
        assert doc.has_uniform_rows is True

    def test_large_uniform_doc(self):
        doc = _make_doc(100, col_count=10)
        assert doc.has_uniform_rows is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_tiny_is_not_large(self):
        doc = _make_doc(3)
        assert doc.is_tiny is True
        assert doc.is_large is False

    def test_medium_neither_tiny_nor_large(self):
        doc = _make_doc(1000)
        assert doc.is_tiny is False
        assert doc.is_large is False

    def test_tiny_uniform_doc(self):
        doc = _make_doc(3, col_count=5)
        assert doc.is_tiny is True
        assert doc.has_uniform_rows is True
