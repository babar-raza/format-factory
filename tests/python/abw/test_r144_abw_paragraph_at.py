"""Tests for abw.abw_codec.get_paragraph_at() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, get_paragraph_at


def test_first_paragraph():
    model = create_abw(["Alpha", "Beta", "Gamma"])
    assert get_paragraph_at(model, 0) == "Alpha"


def test_middle_paragraph():
    model = create_abw(["Alpha", "Beta", "Gamma"])
    assert get_paragraph_at(model, 1) == "Beta"


def test_last_paragraph():
    model = create_abw(["Alpha", "Beta", "Gamma"])
    assert get_paragraph_at(model, 2) == "Gamma"


def test_index_out_of_range_raises():
    model = create_abw(["only"])
    try:
        get_paragraph_at(model, 5)
        assert 1 == 0, "Expected IndexError"

    except IndexError:
        pass


def test_negative_index_raises():
    model = create_abw(["p1", "p2"])
    try:
        get_paragraph_at(model, -1)
        assert 1 == 0, "Expected IndexError"

    except IndexError:
        pass


def test_empty_model_raises():
    model = create_abw([])
    try:
        get_paragraph_at(model, 0)
        assert 1 == 0, "Expected IndexError"

    except IndexError:
        pass


def test_returns_string():
    model = create_abw(["hello"])
    result = get_paragraph_at(model, 0)
    assert isinstance(result, str)
