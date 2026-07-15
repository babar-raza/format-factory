"""L1 unit tests — parser field-level correctness for valid UBL input.

Complements TestProbe/TestLoad in test_ubl_codec.py with per-field
assertions (currency, party names, individual line-item fields) that
those higher-level tests do not cover directly.
"""

from __future__ import annotations

from pathlib import Path

from ubl.ubl_codec import load_ubl

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl"
VALID_DIR = SAMPLES / "valid"


class TestInvoiceFieldParsing:
    def test_load_invoice_currency(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert model["currency"] == "USD"

    def test_load_invoice_issue_date(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert model["issue_date"] == "2026-07-14"

    def test_load_invoice_returns_dict(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert isinstance(model, dict)

    def test_load_invoice_customer_name(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert model["customer"]["name"] == "Buyer Inc"

    def test_load_multi_line_invoice_currency(self):
        model = load_ubl(VALID_DIR / "multi-line-invoice.xml")
        assert model["currency"] == "EUR"

    def test_load_invoice_line_item_fields(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        line = model["lines"][0]
        assert line["id"] == "1"
        assert line["quantity"] == "10"
        assert line["amount"] == "100.00"
        assert line["item_name"] == "Widget"


class TestOrderFieldParsing:
    def test_load_order_buyer_name(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        assert model["buyer"]["name"] == "Buyer Inc"

    def test_load_order_seller_name(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        assert model["seller"]["name"] == "Seller Corp"

    def test_load_order_issue_date(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        assert model["issue_date"] == "2026-07-14"

    def test_load_order_line_item_fields(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        line = model["lines"][0]
        assert line["id"] == "1"
        assert line["quantity"] == "5"
        assert line["item_name"] == "Gadget"
        # Order lines carry no "amount" key (unlike Invoice lines).
        assert "amount" not in line
