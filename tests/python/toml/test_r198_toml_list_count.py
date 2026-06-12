"""
Tests for toml_list_count — sprint product-deepening-rnext67.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from src.python.toml.toml_codec import toml_list_count

TOML_TWO_LISTS = b"""\
ports = [8080, 9090]
hosts = ["a", "b", "c"]
name = "test"
count = 42

[section]
items = [1, 2, 3]
"""

TOML_NO_LISTS = b"""\
name = "test"
count = 42
flag = true
"""

TOML_ONE_LIST = b"""\
tags = ["alpha", "beta"]
version = "1.0"
"""


def test_import():
    assert callable(toml_list_count)


def test_two_top_level_lists():
    result = toml_list_count(TOML_TWO_LISTS)
    assert result == 2


def test_no_lists_returns_zero():
    result = toml_list_count(TOML_NO_LISTS)
    assert result == 0


def test_one_list():
    result = toml_list_count(TOML_ONE_LIST)
    assert result == 1


def test_returns_int():
    result = toml_list_count(TOML_NO_LISTS)
    assert isinstance(result, int)


def test_result_nonnegative():
    result = toml_list_count(TOML_TWO_LISTS)
    assert result >= 0
