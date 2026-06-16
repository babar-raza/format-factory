"""Sprint 54: CSV csv_max_field_count + csv_is_multi_row (R264)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
# Avoid stdlib csv conflict
import importlib
for mod in list(sys.modules.keys()):
    if mod == "csv" or mod.startswith("csv."):
        del sys.modules[mod]

from csv.csv_parser import csv_max_field_count, csv_is_multi_row

CSV_DIR = _REPO / "samples" / "by-format" / "csv"

MINIMAL = CSV_DIR / "minimal-2x2.csv"
SINGLE = CSV_DIR / "single-cell.csv"
QUOTED = CSV_DIR / "quoted-fields.csv"


# --- csv_max_field_count ---

def test_max_field_count_minimal_is_2():
    assert csv_max_field_count(MINIMAL) == 2


def test_max_field_count_single_is_1():
    assert csv_max_field_count(SINGLE) == 1


def test_max_field_count_quoted_is_3():
    assert csv_max_field_count(QUOTED) == 3


def test_max_field_count_returns_int():
    assert isinstance(csv_max_field_count(MINIMAL), int)


def test_max_field_count_positive():
    assert csv_max_field_count(MINIMAL) > 0
    assert csv_max_field_count(QUOTED) > 0


# --- csv_is_multi_row ---

def test_is_multi_row_minimal_returns_true():
    # 2 data rows
    assert csv_is_multi_row(MINIMAL) is True


def test_is_multi_row_single_returns_false():
    # 1 data row
    assert csv_is_multi_row(SINGLE) is False


def test_is_multi_row_quoted_returns_true():
    # 2 data rows
    assert csv_is_multi_row(QUOTED) is True


def test_is_multi_row_returns_bool():
    result = csv_is_multi_row(MINIMAL)
    assert isinstance(result, bool)


def test_is_multi_row_false_single():
    result = csv_is_multi_row(SINGLE)
    assert isinstance(result, bool)
    assert result is False
