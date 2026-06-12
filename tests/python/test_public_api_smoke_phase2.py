"""
Public API smoke tests for Phase 2 product integration.
Verifies search_text, append_rows, and flatten_records are importable
through their package paths and behave correctly.

Sprint: FORMAT-FACTORY-SELF-HEALING-PRODUCT-DEEPENING-RNEXT
Run ID: format-factory-self-healing-product-deepening-rnext-20260611-2000

Note: ABW uses src/python path (abw package not shadowed).
      TSV and NDJSON use full src.python.* path to avoid tests/python shadow.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from abw import search_text  # noqa: E402
from src.python.tsv.tsv_parser import append_rows  # noqa: E402
from src.python.ndjson.ndjson_codec import flatten_records  # noqa: E402


# --- ABW search_text ---

def test_abw_search_text_importable_from_package():
    assert callable(search_text)


def test_abw_search_text_via_package_returns_indices():
    model = {"paragraphs": ["hello world", "foo bar", "hello again"]}
    result = search_text(model, "hello")
    assert result == [0, 2]


def test_abw_search_text_no_match_returns_empty():
    model = {"paragraphs": ["alpha", "beta"]}
    assert search_text(model, "gamma") == []


def test_abw_search_text_in_all():
    import abw
    assert "search_text" in abw.__all__


# --- TSV append_rows ---

def test_tsv_append_rows_importable():
    assert callable(append_rows)


def test_tsv_append_rows_adds_rows():
    data = {"headers": ["a", "b"], "rows": [["1", "2"]], "row_count": 1}
    result = append_rows(data, [["3", "4"]])
    assert result["rows"] == [["1", "2"], ["3", "4"]]
    assert result["row_count"] == 2


def test_tsv_append_rows_in_package_all():
    from src.python.tsv import __all__ as tsv_all
    assert "append_rows" in tsv_all


# --- NDJSON flatten_records ---

def test_ndjson_flatten_records_importable():
    assert callable(flatten_records)


def test_ndjson_flatten_records_flattens_nested():
    records = [{"user": {"id": 1, "name": "Alice"}, "score": 95}]
    result = flatten_records(records)
    assert result == [{"user_id": 1, "user_name": "Alice", "score": 95}]


def test_ndjson_flatten_records_flat_unchanged():
    records = [{"a": 1, "b": 2}]
    assert flatten_records(records) == [{"a": 1, "b": 2}]


def test_ndjson_flatten_records_in_package_all():
    from src.python.ndjson import __all__ as ndjson_all
    assert "flatten_records" in ndjson_all
