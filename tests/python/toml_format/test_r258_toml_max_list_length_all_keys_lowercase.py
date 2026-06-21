"""Tests for TOML gap closure batch 3 (Sprint 40).

Closes:
  GAP-TOML-FOSS-TOML_MAX_LIS-001  (Toml Max List Length)
  GAP-TOML-FOSS-TOML_ALL_KEY-001  (Toml All Keys Lowercase)
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_all_keys_lowercase, toml_max_list_length


@pytest.fixture
def list_file(tmp_path):
    """TOML file with a list of length 3."""
    path = tmp_path / "lists.toml"
    path.write_text('tags = ["web", "api", "rest"]\nname = "alice"\n')
    return str(path)


@pytest.fixture
def two_lists_file(tmp_path):
    """TOML file with two lists."""
    path = tmp_path / "two_lists.toml"
    path.write_text("a = [1, 2]\nb = [3]\n")
    return str(path)


@pytest.fixture
def no_list_file(tmp_path):
    """TOML file with no lists."""
    path = tmp_path / "no_list.toml"
    path.write_text("name = \"alice\"\nage = 30\n")
    return str(path)


@pytest.fixture
def uppercase_keys_file(tmp_path):
    """TOML file with a mixed-case key."""
    path = tmp_path / "upper.toml"
    path.write_text("Name = \"alice\"\nage = 30\n")
    return str(path)


class TestTomlMaxListLength:
    def test_return_type(self, list_file):
        assert isinstance(toml_max_list_length(list_file), int)

    def test_exact_3_for_list_of_3(self, list_file):
        assert toml_max_list_length(list_file) == 3

    def test_exact_2_for_two_lists(self, two_lists_file):
        # max([2, 1]) = 2
        assert toml_max_list_length(two_lists_file) == 2

    def test_zero_for_no_lists(self, no_list_file):
        assert toml_max_list_length(no_list_file) == 0

    def test_nonnegative(self, no_list_file):
        assert toml_max_list_length(no_list_file) >= 0

    def test_consistent_across_calls(self, list_file):
        assert toml_max_list_length(list_file) == toml_max_list_length(list_file)


class TestTomlAllKeysLowercase:
    def test_return_type(self, no_list_file):
        assert isinstance(toml_all_keys_lowercase(no_list_file), bool)

    def test_true_for_all_lowercase(self, no_list_file):
        assert toml_all_keys_lowercase(no_list_file) is True

    def test_false_for_uppercase_key(self, uppercase_keys_file):
        assert toml_all_keys_lowercase(uppercase_keys_file) is False

    def test_consistent_across_calls(self, no_list_file):
        assert toml_all_keys_lowercase(no_list_file) == toml_all_keys_lowercase(no_list_file)
