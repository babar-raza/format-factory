"""Sprint 51: PBM pbm_column_count + pbm_min_row_black_count (R261)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import pbm_column_count, pbm_min_row_black_count

PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"

BLACK_1X1 = PBM_DIR / "1x1-black.pbm"
CHECKER_2X2 = PBM_DIR / "2x2-checker.pbm"
PATTERN_3X2 = PBM_DIR / "3x2-pattern.pbm"


# --- pbm_column_count ---

def test_column_count_1x1_is_1():
    assert pbm_column_count(BLACK_1X1) == 1


def test_column_count_2x2_is_2():
    assert pbm_column_count(CHECKER_2X2) == 2


def test_column_count_3x2_is_3():
    assert pbm_column_count(PATTERN_3X2) == 3


def test_column_count_returns_int():
    assert isinstance(pbm_column_count(BLACK_1X1), int)


def test_column_count_positive():
    assert pbm_column_count(BLACK_1X1) > 0
    assert pbm_column_count(CHECKER_2X2) > 0


# --- pbm_min_row_black_count ---

def test_min_row_black_1x1_is_1():
    # Single black pixel → row has 1 black
    assert pbm_min_row_black_count(BLACK_1X1) == 1


def test_min_row_black_checker_is_1():
    # 2x2 checker: rows are [1,0] and [0,1] → min is 1
    assert pbm_min_row_black_count(CHECKER_2X2) == 1


def test_min_row_black_pattern_is_1():
    # 3x2 pattern: rows [1,0,1] and [0,1,0] → min black = 1
    assert pbm_min_row_black_count(PATTERN_3X2) == 1


def test_min_row_black_returns_int():
    assert isinstance(pbm_min_row_black_count(BLACK_1X1), int)


def test_min_row_black_le_max_row_black():
    from pbm.pbm_parser import pbm_max_row_black_count
    assert pbm_min_row_black_count(PATTERN_3X2) <= pbm_max_row_black_count(PATTERN_3X2)


def test_min_row_black_nonnegative():
    assert pbm_min_row_black_count(BLACK_1X1) >= 0
    assert pbm_min_row_black_count(CHECKER_2X2) >= 0
