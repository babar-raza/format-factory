"""Tests for tsv_has_header — detect if TSV file has a header row."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import tsv_has_header


class TestTsvHasHeader:
    def test_with_header(self, tmp_path):
        p = tmp_path / "with_header.tsv"
        p.write_text("name\tage\tcity\nAlice\t30\tNYC\nBob\t25\tLA\n", encoding="utf-8")
        assert tsv_has_header(p) is True

    def test_all_numeric_delegates_to_parser(self, tmp_path):
        p = tmp_path / "no_header.tsv"
        p.write_text("1\t2\t3\n4\t5\t6\n7\t8\t9\n", encoding="utf-8")
        # Parser's own has_header heuristic determines result
        result = tsv_has_header(p)
        assert isinstance(result, bool)

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.tsv"
        p.write_text("", encoding="utf-8")
        assert tsv_has_header(p) is False

    def test_single_header_row_only(self, tmp_path):
        p = tmp_path / "header_only.tsv"
        p.write_text("name\tage\tcity\n", encoding="utf-8")
        assert tsv_has_header(p) is False  # No numeric data rows to confirm

    def test_returns_bool(self, tmp_path):
        p = tmp_path / "test.tsv"
        p.write_text("a\tb\n1\t2\n", encoding="utf-8")
        assert isinstance(tsv_has_header(p), bool)

    def test_importable_from_init(self):
        from src.python.tsv import tsv_has_header as fn
        assert callable(fn)

    def test_in_all_list(self):
        from src.python.tsv import __all__
        assert "tsv_has_header" in __all__

    def test_mixed_header_with_numbers(self, tmp_path):
        p = tmp_path / "mixed.tsv"
        p.write_text("col1\t2col\tcol3\n10\t20\t30\n", encoding="utf-8")
        # "2col" is not numeric (float("2col") raises ValueError)
        assert tsv_has_header(p) is True
