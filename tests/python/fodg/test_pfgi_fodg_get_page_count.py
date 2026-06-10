"""Tests for fodg.fodg_codec.get_page_count() — PFGI Sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import create_fodg, add_page, get_page_count


def test_empty_model_returns_zero():
    model = {"pages": []}
    assert get_page_count(model) == 0


def test_single_page_returns_one():
    model = create_fodg([{"name": "Page1"}])
    assert get_page_count(model) == 1


def test_two_pages_returns_two():
    model = create_fodg([{"name": "P1"}, {"name": "P2"}])
    assert get_page_count(model) == 2


def test_add_page_increments_count():
    model = create_fodg([{"name": "Page1"}])
    model = add_page(model, "Page2")
    assert get_page_count(model) == 2


def test_missing_pages_key_returns_zero():
    model = {}
    assert get_page_count(model) == 0


def test_returns_int():
    model = create_fodg([{"name": "P"}])
    assert isinstance(get_page_count(model), int)


def test_three_pages():
    model = create_fodg([{"name": "A"}, {"name": "B"}, {"name": "C"}])
    assert get_page_count(model) == 3
