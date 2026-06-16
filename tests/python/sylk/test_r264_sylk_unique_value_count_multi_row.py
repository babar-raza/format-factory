"""Sprint 54: SYLK sylk_unique_value_count + sylk_is_multi_row (R264)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import sylk_unique_value_count, sylk_is_multi_row

SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"

MINIMAL = SYLK_DIR / "minimal-2x2.slk"
NUMERIC = SYLK_DIR / "numeric-row.slk"
SINGLE = SYLK_DIR / "single-cell.slk"


# --- sylk_unique_value_count ---

def test_unique_value_count_minimal_is_4():
    assert sylk_unique_value_count(MINIMAL) == 4


def test_unique_value_count_numeric_is_3():
    assert sylk_unique_value_count(NUMERIC) == 3


def test_unique_value_count_single_is_1():
    assert sylk_unique_value_count(SINGLE) == 1


def test_unique_value_count_returns_int():
    assert isinstance(sylk_unique_value_count(MINIMAL), int)


def test_unique_value_count_nonnegative():
    assert sylk_unique_value_count(MINIMAL) >= 0
    assert sylk_unique_value_count(SINGLE) >= 0


# --- sylk_is_multi_row ---

def test_is_multi_row_minimal_returns_true():
    # minimal-2x2 has rows 1 and 2
    assert sylk_is_multi_row(MINIMAL) is True


def test_is_multi_row_numeric_returns_false():
    # numeric-row has only 1 row
    assert sylk_is_multi_row(NUMERIC) is False


def test_is_multi_row_single_returns_false():
    assert sylk_is_multi_row(SINGLE) is False


def test_is_multi_row_returns_bool_minimal():
    assert isinstance(sylk_is_multi_row(MINIMAL), bool)


def test_is_multi_row_returns_bool_numeric():
    assert isinstance(sylk_is_multi_row(NUMERIC), bool)
