"""Sprint 51: FODT fodt_nonempty_paragraph_count + fodt_char_density (R261)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_nonempty_paragraph_count, fodt_char_density

FODT_DIR = _REPO / "samples" / "by-format" / "fodt"

MINIMAL = FODT_DIR / "minimal-document.fodt"
HEADINGS = FODT_DIR / "headings-and-paragraphs.fodt"
LIST = FODT_DIR / "list-basic.fodt"


# --- fodt_nonempty_paragraph_count ---

def test_nonempty_para_count_minimal_is_1():
    assert fodt_nonempty_paragraph_count(MINIMAL) == 1


def test_nonempty_para_count_headings_is_4():
    assert fodt_nonempty_paragraph_count(HEADINGS) == 4


def test_nonempty_para_count_list_is_2():
    assert fodt_nonempty_paragraph_count(LIST) == 2


def test_nonempty_para_count_returns_int_minimal():
    result = fodt_nonempty_paragraph_count(MINIMAL)
    assert isinstance(result, int)


def test_nonempty_para_count_nonnegative():
    assert fodt_nonempty_paragraph_count(MINIMAL) >= 0
    assert fodt_nonempty_paragraph_count(HEADINGS) >= 0


# --- fodt_char_density ---

def test_char_density_minimal():
    result = fodt_char_density(MINIMAL)
    assert abs(result - 6.5) < 0.01


def test_char_density_headings():
    result = fodt_char_density(HEADINGS)
    # 237 chars / 44 words ≈ 5.39
    assert abs(result - 5.39) < 0.01


def test_char_density_list():
    result = fodt_char_density(LIST)
    # 42 chars / 6 words = 7.0
    assert abs(result - 7.0) < 0.01


def test_char_density_returns_float():
    result = fodt_char_density(MINIMAL)
    assert isinstance(result, float)


def test_char_density_positive():
    assert fodt_char_density(MINIMAL) > 0.0
    assert fodt_char_density(HEADINGS) > 0.0
    assert fodt_char_density(LIST) > 0.0
