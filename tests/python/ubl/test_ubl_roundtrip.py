"""UBL roundtrip tests — load → write → reload identity verification.

Exercises all three document types (Invoice, CreditNote, Order) and all
sample fixtures through the roundtrip() function. Verifies that the model
survives a full serialization cycle without data loss.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ubl import load_ubl, write_ubl, roundtrip

SAMPLES = Path(_REPO / "samples" / "by-format" / "ubl" / "valid")


def _roundtrip_model(sample_name: str) -> tuple[dict, dict]:
    src = SAMPLES / sample_name
    original = load_ubl(src)
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        reloaded = roundtrip(src, tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    return original, reloaded


class TestInvoiceRoundtrip:
    def test_minimal_invoice_identity(self):
        orig, rt = _roundtrip_model("minimal-invoice.xml")
        assert rt["document_type"] == orig["document_type"] == "Invoice"
        assert rt["id"] == orig["id"]
        assert rt["issue_date"] == orig["issue_date"]
        assert rt["currency"] == orig["currency"]
        assert len(rt["lines"]) == len(orig["lines"])

    def test_multi_line_invoice_preserves_lines(self):
        orig, rt = _roundtrip_model("multi-line-invoice.xml")
        assert len(rt["lines"]) == len(orig["lines"])
        for orig_line, rt_line in zip(orig["lines"], rt["lines"]):
            assert rt_line["id"] == orig_line["id"]
            assert rt_line["item_name"] == orig_line["item_name"]
            assert rt_line["quantity"] == orig_line["quantity"]
            assert rt_line["amount"] == orig_line["amount"]

    def test_full_depth_invoice_party_data(self):
        orig, rt = _roundtrip_model("invoice-full-depth.xml")
        assert rt["supplier"]["name"] == orig["supplier"]["name"]
        assert rt["customer"]["name"] == orig["customer"]["name"]
        for party_key in ("supplier", "customer"):
            orig_party = orig[party_key]
            rt_party = rt[party_key]
            if orig_party.get("endpoint_id"):
                assert rt_party["endpoint_id"] == orig_party["endpoint_id"]
            if orig_party.get("postal_address"):
                assert rt_party["postal_address"] == orig_party["postal_address"]

    def test_invoice_tax_total_roundtrip(self):
        orig, rt = _roundtrip_model("invoice-full-depth.xml")
        if "tax_total" in orig:
            assert "tax_total" in rt
            assert rt["tax_total"]["tax_amount"] == orig["tax_total"]["tax_amount"]

    def test_invoice_monetary_total_roundtrip(self):
        orig, rt = _roundtrip_model("invoice-full-depth.xml")
        if "monetary_total" in orig:
            assert "monetary_total" in rt
            assert rt["monetary_total"]["payable_amount"] == orig["monetary_total"]["payable_amount"]


class TestCreditNoteRoundtrip:
    def test_minimal_creditnote_identity(self):
        orig, rt = _roundtrip_model("minimal-creditnote.xml")
        assert rt["document_type"] == orig["document_type"] == "CreditNote"
        assert rt["id"] == orig["id"]
        assert rt["issue_date"] == orig["issue_date"]
        assert len(rt["lines"]) == len(orig["lines"])

    def test_creditnote_with_totals(self):
        orig, rt = _roundtrip_model("creditnote-with-totals.xml")
        assert rt["document_type"] == "CreditNote"
        if "tax_total" in orig:
            assert "tax_total" in rt
        if "monetary_total" in orig:
            assert "monetary_total" in rt


class TestOrderRoundtrip:
    def test_minimal_order_identity(self):
        orig, rt = _roundtrip_model("minimal-order.xml")
        assert rt["document_type"] == orig["document_type"] == "Order"
        assert rt["id"] == orig["id"]
        assert rt["issue_date"] == orig["issue_date"]
        assert len(rt["lines"]) == len(orig["lines"])

    def test_order_party_data(self):
        orig, rt = _roundtrip_model("minimal-order.xml")
        if "buyer" in orig:
            assert rt["buyer"]["name"] == orig["buyer"]["name"]
        if "seller" in orig:
            assert rt["seller"]["name"] == orig["seller"]["name"]


class TestWriteToString:
    def test_write_returns_xml_string(self):
        model = load_ubl(SAMPLES / "minimal-invoice.xml")
        xml_str = write_ubl(model)
        assert isinstance(xml_str, str)
        assert "Invoice" in xml_str

    def test_write_string_is_valid_xml(self):
        import xml.etree.ElementTree as ET
        model = load_ubl(SAMPLES / "minimal-invoice.xml")
        xml_str = write_ubl(model)
        root = ET.fromstring(xml_str)
        assert root is not None


class TestAllSamplesRoundtrip:
    @pytest.mark.parametrize("sample", [
        "minimal-invoice.xml",
        "multi-line-invoice.xml",
        "invoice-full-depth.xml",
        "minimal-creditnote.xml",
        "creditnote-with-totals.xml",
        "minimal-order.xml",
    ])
    def test_all_samples_survive_roundtrip(self, sample):
        if not (SAMPLES / sample).exists():
            pytest.skip(f"Sample {sample} not found")
        orig, rt = _roundtrip_model(sample)
        assert rt["document_type"] == orig["document_type"]
        assert rt["id"] == orig["id"]
        assert len(rt.get("lines", [])) == len(orig.get("lines", []))
