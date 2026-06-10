"""Public API smoke tests — verify all 9 product functions are importable from packages.

Uses sys.path.insert(0, str(_REPO)) + src.python.<pkg> to avoid
collision with test directories that share package names.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))


# --- Previous 4 functions ---

def test_tsv_average_column_from_package():
    from src.python.tsv import average_column_tsv
    assert callable(average_column_tsv)


def test_gnumeric_get_row_values_from_package():
    from src.python.gnumeric import get_row_values
    assert callable(get_row_values)


def test_abw_text_stats_from_package():
    from src.python.abw import text_stats
    assert callable(text_stats)


def test_fodg_get_page_count_from_package():
    from src.python.fodg import get_page_count
    assert callable(get_page_count)


# --- New 5 functions ---

def test_tsv_median_column_from_package():
    from src.python.tsv import median_column_tsv
    assert callable(median_column_tsv)


def test_tsv_std_column_from_package():
    from src.python.tsv import std_column_tsv
    assert callable(std_column_tsv)


def test_gnumeric_get_column_values_from_package():
    from src.python.gnumeric import get_column_values
    assert callable(get_column_values)


def test_abw_export_to_plain_text_from_package():
    from src.python.abw import export_to_plain_text
    assert callable(export_to_plain_text)


def test_fodg_find_text_from_package():
    from src.python.fodg import find_text
    assert callable(find_text)
