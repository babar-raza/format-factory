"""Tests closing FOSS gap: fodg_min_text_per_page."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_min_text_per_page

SAMPLE_DIR = _REPO / "samples" / "by-format" / "fodg"


@pytest.fixture
def fodg_path():
    candidates = list(SAMPLE_DIR.glob("*.fodg"))
    if not candidates:
        pytest.skip("No FODG sample files available")
    return candidates[0]


def test_fodg_min_text_per_page_returns_number(fodg_path):
    result = fodg_min_text_per_page(fodg_path)
    assert isinstance(result, (int, float))
    assert result >= 0
