"""Tests for ubl_analytics.py — statistics derived from parsed UBL documents.

Each function is exercised against the real fixtures in
samples/by-format/ubl/{valid,invalid}/ — no synthetic-only sample files.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ubl.exceptions import UblParseError
from ubl.ubl_analytics import (
    ubl_document_type_summary,
    ubl_supplier_name,
    ubl_total_line_count,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"


class TestUblTotalLineCount:
    def test_minimal_invoice_one_line(self):
        assert ubl_total_line_count(VALID_DIR / "minimal-invoice.xml") == 1

    def test_multi_line_invoice_three_lines(self):
        assert ubl_total_line_count(VALID_DIR / "multi-line-invoice.xml") == 3

    def test_minimal_order_one_line(self):
        assert ubl_total_line_count(VALID_DIR / "minimal-order.xml") == 1

    def test_missing_mandatory_zero_lines(self):
        """Edge case: document with no InvoiceLine elements at all."""
        assert ubl_total_line_count(INVALID_DIR / "missing-mandatory.xml") == 0

    def test_accepts_str_path(self):
        assert ubl_total_line_count(str(VALID_DIR / "minimal-invoice.xml")) == 1

    def test_accepts_path_object(self):
        assert ubl_total_line_count(Path(VALID_DIR / "minimal-invoice.xml")) == 1

    def test_accepts_bytes_source(self):
        data = (VALID_DIR / "multi-line-invoice.xml").read_bytes()
        assert ubl_total_line_count(data) == 3

    def test_raises_on_non_ubl_xml(self):
        with pytest.raises(UblParseError):
            ubl_total_line_count(b'<?xml version="1.0"?><root/>')

    def test_raises_on_malformed_xml(self):
        with pytest.raises(UblParseError):
            ubl_total_line_count(b"<not>closed xml")

    def test_return_type_is_int(self):
        result = ubl_total_line_count(VALID_DIR / "minimal-invoice.xml")
        assert isinstance(result, int)


class TestUblSupplierName:
    def test_minimal_invoice_supplier(self):
        assert ubl_supplier_name(VALID_DIR / "minimal-invoice.xml") == "Acme Corp"

    def test_multi_line_invoice_supplier(self):
        assert ubl_supplier_name(VALID_DIR / "multi-line-invoice.xml") == "Supplier GmbH"

    def test_missing_mandatory_no_supplier(self):
        """Edge case: Invoice document with no AccountingSupplierParty element."""
        assert ubl_supplier_name(INVALID_DIR / "missing-mandatory.xml") is None

    def test_order_document_has_no_supplier_key(self):
        """Edge case: Order documents use buyer/seller, not supplier."""
        assert ubl_supplier_name(VALID_DIR / "minimal-order.xml") is None

    def test_accepts_bytes_source(self):
        data = (VALID_DIR / "minimal-invoice.xml").read_bytes()
        assert ubl_supplier_name(data) == "Acme Corp"

    def test_accepts_path_object(self):
        assert ubl_supplier_name(Path(VALID_DIR / "minimal-invoice.xml")) == "Acme Corp"

    def test_raises_on_non_ubl_xml(self):
        with pytest.raises(UblParseError):
            ubl_supplier_name(b'<?xml version="1.0"?><root/>')

    def test_raises_on_malformed_xml(self):
        with pytest.raises(UblParseError):
            ubl_supplier_name(b"<not>closed xml")

    def test_return_type_is_str_or_none(self):
        result = ubl_supplier_name(VALID_DIR / "minimal-invoice.xml")
        assert isinstance(result, str)


class TestUblDocumentTypeSummary:
    def test_minimal_invoice_summary(self):
        summary = ubl_document_type_summary(VALID_DIR / "minimal-invoice.xml")
        assert summary == {"document_type": "Invoice", "line_count": 1}

    def test_multi_line_invoice_summary(self):
        summary = ubl_document_type_summary(VALID_DIR / "multi-line-invoice.xml")
        assert summary == {"document_type": "Invoice", "line_count": 3}

    def test_minimal_order_summary(self):
        summary = ubl_document_type_summary(VALID_DIR / "minimal-order.xml")
        assert summary == {"document_type": "Order", "line_count": 1}

    def test_missing_mandatory_summary_zero_lines(self):
        """Edge case: document with an empty lines list still summarizes cleanly."""
        summary = ubl_document_type_summary(INVALID_DIR / "missing-mandatory.xml")
        assert summary == {"document_type": "Invoice", "line_count": 0}

    def test_returns_dict(self):
        summary = ubl_document_type_summary(VALID_DIR / "minimal-invoice.xml")
        assert isinstance(summary, dict)

    def test_keys_are_exact(self):
        summary = ubl_document_type_summary(VALID_DIR / "minimal-invoice.xml")
        assert set(summary.keys()) == {"document_type", "line_count"}

    def test_accepts_bytes_source(self):
        data = (VALID_DIR / "minimal-order.xml").read_bytes()
        summary = ubl_document_type_summary(data)
        assert summary["document_type"] == "Order"

    def test_raises_on_non_ubl_xml(self):
        with pytest.raises(UblParseError):
            ubl_document_type_summary(b'<?xml version="1.0"?><root/>')

    def test_raises_on_malformed_xml(self):
        with pytest.raises(UblParseError):
            ubl_document_type_summary(b"<not>closed xml")
