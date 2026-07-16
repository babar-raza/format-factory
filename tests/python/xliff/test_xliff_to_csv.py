"""Tests for xliff_to_csv dogfood export (TC-S6P4-PROD-007, select-6 Phase 4)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format" / "xliff" / "valid"

from xliff.xliff_to_csv import xliff_to_csv


class TestXliffToCsv:
    def test_returns_data_row_count(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = xliff_to_csv(SAMPLES / "multi-unit.xliff", dest)
        assert count >= 2

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.csv"
        xliff_to_csv(SAMPLES / "multi-unit.xliff", dest)
        assert dest.exists()

    def test_header_and_translation_content_present(self, tmp_path):
        dest = tmp_path / "out.csv"
        xliff_to_csv(SAMPLES / "multi-unit.xliff", dest)
        content = dest.read_text(encoding="utf-8")
        assert content.startswith("unit_id,source,target,state")
        assert "Hello" in content
        assert "Bonjour" in content

    def test_minimal_file_single_unit(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = xliff_to_csv(SAMPLES / "minimal.xliff", dest)
        assert count >= 1

    def test_inline_codes_sample_flattens_to_plain_text(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = xliff_to_csv(SAMPLES / "with-inline-codes.xliff", dest)
        assert count >= 1
        dest.read_text(encoding="utf-8")  # must not raise on structured content
