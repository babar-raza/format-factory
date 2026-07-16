"""Tests for ubl_to_csv dogfood export (TC-S6P4-PROD-007, select-6 Phase 4)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format" / "ubl" / "valid"

from ubl.ubl_to_csv import ubl_to_csv


class TestUblToCsv:
    def test_returns_data_row_count(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = ubl_to_csv(SAMPLES / "multi-line-invoice.xml", dest)
        assert count == 3

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.csv"
        ubl_to_csv(SAMPLES / "multi-line-invoice.xml", dest)
        assert dest.exists()

    def test_header_and_line_item_content_present(self, tmp_path):
        dest = tmp_path / "out.csv"
        ubl_to_csv(SAMPLES / "multi-line-invoice.xml", dest)
        content = dest.read_text(encoding="utf-8")
        assert content.startswith("id,quantity,amount,item_name")
        assert "Bolt" in content
        assert "Nut" in content
        assert "Washer" in content

    def test_minimal_invoice_zero_or_more_lines(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = ubl_to_csv(SAMPLES / "minimal-invoice.xml", dest)
        assert count >= 0

    def test_minimal_order_lines(self, tmp_path):
        dest = tmp_path / "out.csv"
        count = ubl_to_csv(SAMPLES / "minimal-order.xml", dest)
        assert count >= 0
        assert dest.exists()
