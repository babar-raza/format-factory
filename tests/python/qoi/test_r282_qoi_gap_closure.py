"""Tests closing FOSS gaps: qoi_pixel_density, qoi_is_dark."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_pixel_density, qoi_is_dark

SAMPLE_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


@pytest.fixture
def qoi_path():
    candidates = list(SAMPLE_DIR.glob("*.qoi"))
    if not candidates:
        pytest.skip("No QOI sample files available")
    return candidates[0]


def test_qoi_pixel_density_returns_float(qoi_path):
    result = qoi_pixel_density(qoi_path)
    assert isinstance(result, (int, float))
    assert result > 0


def test_qoi_is_dark_returns_bool(qoi_path):
    result = qoi_is_dark(qoi_path)
    assert isinstance(result, bool)
