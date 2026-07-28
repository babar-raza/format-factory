"""Tests for csv_stats extension functions (ext3 batch)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import parse_csv
from src.python.ff_csv.csv_stats import (
    csv_row_count,
    csv_column_count,
    csv_delimiter,
    csv_is_empty,
    csv_has_data_rows,
    csv_first_header,
)

SAMPLES = Path("samples/by-format/csv")
MINIMAL = SAMPLES / "minimal-2x2.csv"
SINGLE = SAMPLES / "single-cell.csv"
QUOTED = SAMPLES / "quoted-fields.csv"


def _doc(path):
    return parse_csv(str(path))


# --- csv_row_count ---

def test_row_count_minimal():
    assert csv_row_count(_doc(MINIMAL)) == 2


def test_row_count_returns_int():
    assert isinstance(csv_row_count(_doc(MINIMAL)), int)


def test_row_count_single():
    result = csv_row_count(_doc(SINGLE))
    assert isinstance(result, int)


# --- csv_column_count ---

def test_column_count_minimal():
    assert csv_column_count(_doc(MINIMAL)) == 2


def test_column_count_returns_int():
    assert isinstance(csv_column_count(_doc(MINIMAL)), int)


# --- csv_delimiter ---

def test_delimiter_minimal_comma():
    assert csv_delimiter(_doc(MINIMAL)) == ","


def test_delimiter_returns_str():
    assert isinstance(csv_delimiter(_doc(MINIMAL)), str)


def test_delimiter_quoted():
    result = csv_delimiter(_doc(QUOTED))
    assert isinstance(result, str)


# --- csv_is_empty ---

def test_is_empty_minimal_false():
    assert csv_is_empty(_doc(MINIMAL)) is False


def test_is_empty_returns_bool():
    assert isinstance(csv_is_empty(_doc(MINIMAL)), bool)


# --- csv_has_data_rows ---

def test_has_data_rows_minimal_true():
    assert csv_has_data_rows(_doc(MINIMAL)) is True


def test_has_data_rows_returns_bool():
    assert isinstance(csv_has_data_rows(_doc(MINIMAL)), bool)


def test_has_data_rows_single():
    assert csv_has_data_rows(_doc(SINGLE)) is True


# --- csv_first_header ---

def test_first_header_minimal_nonempty():
    result = csv_first_header(_doc(MINIMAL))
    assert isinstance(result, str)
    assert len(result) > 0


def test_first_header_returns_str():
    assert isinstance(csv_first_header(_doc(MINIMAL)), str)
