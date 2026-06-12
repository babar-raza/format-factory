"""
test_r162_toml_count_section.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22-001
Added: 2026-06-12

Tests for TOML count_values_in_section function.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.toml.toml_codec import count_values_in_section


class TestCountValuesInSection:
    def test_empty_section(self):
        src = b"[section]\n"
        assert count_values_in_section(src, "section") == 0

    def test_one_key(self):
        src = b"[section]\nfoo = 1\n"
        assert count_values_in_section(src, "section") == 1

    def test_three_keys(self):
        src = b"[section]\nfoo = 1\nbar = 2\nbaz = 3\n"
        assert count_values_in_section(src, "section") == 3

    def test_missing_section_returns_zero(self):
        src = b"[other]\nfoo = 1\n"
        assert count_values_in_section(src, "missing") == 0

    def test_top_level_key_not_counted_as_section(self):
        src = b"top_key = 42\n"
        assert count_values_in_section(src, "top_key") == 0

    def test_returns_int(self):
        src = b"[s]\na = 1\nb = 2\n"
        result = count_values_in_section(src, "s")
        assert isinstance(result, int)
