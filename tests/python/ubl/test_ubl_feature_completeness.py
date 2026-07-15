"""Tests for the UBL feature-completeness sprint (2026-07-15).

Covers the five confirmed features from this pass:
  - FACT-UBL-101: cac:TaxTotal / cac:TaxSubtotal (VAT breakdown)
  - FACT-UBL-102: cac:LegalMonetaryTotal
  - FACT-UBL-103: full party depth (postal address, VAT/tax scheme,
    legal entity, contact, Peppol endpoint id)
  - FACT-UBL-104: write-side party round-trip bug fix
  - FACT-UBL-105: CreditNote document type

Each test asserts real parsed/written values, not merely "no exception
raised" -- amounts, IDs, and party fields are checked directly.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ubl.exceptions import UblWriteError
from ubl.ubl_codec import load_ubl, probe_ubl, write_ubl

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl"
VALID_DIR = SAMPLES / "valid"


class TestTaxTotalParsing:
    """FACT-UBL-101."""

    def test_tax_total_parsed_from_invoice_full_depth(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        tax_total = model["tax_total"]
        assert tax_total["tax_amount"] == "21.00"
        assert len(tax_total["tax_subtotals"]) == 1
        subtotal = tax_total["tax_subtotals"][0]
        assert subtotal["taxable_amount"] == "100.00"
        assert subtotal["tax_amount"] == "21.00"
        assert subtotal["tax_category_id"] == "S"
        assert subtotal["tax_percent"] == "21"
        assert subtotal["tax_scheme_id"] == "VAT"

    def test_minimal_invoice_has_no_tax_total(self):
        """Documents without cac:TaxTotal must not fabricate the key."""
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert "tax_total" not in model

    def test_tax_total_roundtrip(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "roundtrip.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
        assert reloaded["tax_total"] == model["tax_total"]

    def test_creditnote_tax_total_parsed(self):
        model = load_ubl(VALID_DIR / "creditnote-with-totals.xml")
        assert model["tax_total"]["tax_amount"] == "4.20"
        assert model["tax_total"]["tax_subtotals"][0]["tax_percent"] == "21"


class TestLegalMonetaryTotalParsing:
    """FACT-UBL-102."""

    def test_monetary_total_parsed_from_invoice_full_depth(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        mt = model["monetary_total"]
        assert mt["line_extension_amount"] == "100.00"
        assert mt["tax_exclusive_amount"] == "100.00"
        assert mt["tax_inclusive_amount"] == "121.00"
        assert mt["payable_amount"] == "121.00"

    def test_minimal_invoice_has_no_monetary_total(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert "monetary_total" not in model

    def test_monetary_total_roundtrip(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "roundtrip.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
        assert reloaded["monetary_total"] == model["monetary_total"]

    def test_creditnote_monetary_total_roundtrip(self):
        model = load_ubl(VALID_DIR / "creditnote-with-totals.xml")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "cn_roundtrip.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
        assert reloaded["monetary_total"] == model["monetary_total"]


class TestFullPartyDepth:
    """FACT-UBL-103."""

    def test_supplier_postal_address(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        addr = model["supplier"]["postal_address"]
        assert addr["street_name"] == "Main St 1"
        assert addr["city_name"] == "Springfield"
        assert addr["postal_zone"] == "12345"
        assert addr["country_code"] == "DE"

    def test_supplier_party_tax_scheme(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        scheme = model["supplier"]["party_tax_scheme"]
        assert scheme["company_id"] == "DE123456789"
        assert scheme["tax_scheme_id"] == "VAT"

    def test_supplier_party_legal_entity(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        entity = model["supplier"]["party_legal_entity"]
        assert entity["registration_name"] == "Acme Corp GmbH"
        assert entity["company_id"] == "HRB123456"

    def test_supplier_contact(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        contact = model["supplier"]["contact"]
        assert contact["name"] == "Jane Doe"
        assert contact["telephone"] == "+49-30-1234567"
        assert contact["email"] == "jane@acme.example"

    def test_supplier_endpoint_id(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        assert model["supplier"]["endpoint_id"] == "5412345000013"
        assert model["supplier"]["endpoint_scheme_id"] == "0088"

    def test_customer_full_depth_present(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        customer = model["customer"]
        assert customer["postal_address"]["city_name"] == "Metropolis"
        assert customer["party_tax_scheme"]["company_id"] == "US987654321"
        assert customer["party_legal_entity"]["registration_name"] == "Buyer Inc LLC"
        assert customer["contact"]["email"] == "john@buyer.example"
        assert customer["endpoint_id"] == "5412345000099"

    def test_minimal_invoice_party_has_only_name(self):
        """Existing minimal samples have name-only parties -- no depth fields
        should be fabricated when the source XML doesn't carry them."""
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        supplier = model["supplier"]
        assert supplier["name"] == "Acme Corp"
        assert "postal_address" not in supplier
        assert "party_tax_scheme" not in supplier
        assert "party_legal_entity" not in supplier
        assert "contact" not in supplier
        assert "endpoint_id" not in supplier

    def test_full_party_depth_roundtrip(self):
        model = load_ubl(VALID_DIR / "invoice-full-depth.xml")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "party_roundtrip.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
        assert reloaded["supplier"] == model["supplier"]
        assert reloaded["customer"] == model["customer"]


class TestWriteSidePartyRoundtripFix:
    """FACT-UBL-104: write_ubl must re-emit party data load_ubl parsed.

    Prior to this fix, write_ubl emitted only ID, IssueDate,
    DocumentCurrencyCode, and lines -- AccountingSupplierParty /
    AccountingCustomerParty / BuyerCustomerParty / SellerSupplierParty were
    silently dropped even though load_ubl parsed them.
    """

    def test_minimal_invoice_party_names_survive_roundtrip(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        assert model["supplier"]["name"] == "Acme Corp"
        assert model["customer"]["name"] == "Buyer Inc"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "written.xml"
            written_xml = write_ubl(model, dest)
            reloaded = load_ubl(dest)
        # The raw XML string must actually contain the party wrapper elements.
        assert "AccountingSupplierParty" in written_xml
        assert "AccountingCustomerParty" in written_xml
        assert reloaded["supplier"]["name"] == "Acme Corp"
        assert reloaded["customer"]["name"] == "Buyer Inc"

    def test_order_buyer_seller_survive_roundtrip(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        assert model["buyer"]["name"] == "Buyer Inc"
        assert model["seller"]["name"] == "Seller Corp"
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "order_written.xml"
            written_xml = write_ubl(model, dest)
            reloaded = load_ubl(dest)
        assert "BuyerCustomerParty" in written_xml
        assert "SellerSupplierParty" in written_xml
        assert reloaded["buyer"]["name"] == "Buyer Inc"
        assert reloaded["seller"]["name"] == "Seller Corp"

    def test_empty_party_does_not_emit_empty_wrapper(self):
        """No party data in the model -> no empty party wrapper emitted."""
        model = {
            "document_type": "Invoice",
            "id": "INV-EMPTY",
            "issue_date": "2026-07-15",
            "lines": [],
        }
        result = write_ubl(model)
        assert "AccountingSupplierParty" not in result
        assert "AccountingCustomerParty" not in result


class TestCreditNoteDocumentType:
    """FACT-UBL-105."""

    def test_probe_minimal_creditnote(self):
        assert probe_ubl(VALID_DIR / "minimal-creditnote.xml") is True

    def test_load_minimal_creditnote_document_type(self):
        model = load_ubl(VALID_DIR / "minimal-creditnote.xml")
        assert model["document_type"] == "CreditNote"

    def test_load_minimal_creditnote_fields(self):
        model = load_ubl(VALID_DIR / "minimal-creditnote.xml")
        assert model["id"] == "CN-001"
        assert model["issue_date"] == "2026-07-15"
        assert model["currency"] == "USD"
        assert model["supplier"]["name"] == "Acme Corp"
        assert model["customer"]["name"] == "Buyer Inc"

    def test_load_creditnote_line_uses_credited_quantity(self):
        model = load_ubl(VALID_DIR / "minimal-creditnote.xml")
        line = model["lines"][0]
        assert line["id"] == "1"
        assert line["quantity"] == "2"
        assert line["amount"] == "20.00"
        assert line["item_name"] == "Widget"

    def test_creditnote_with_totals_fields(self):
        model = load_ubl(VALID_DIR / "creditnote-with-totals.xml")
        assert model["document_type"] == "CreditNote"
        assert model["tax_total"]["tax_amount"] == "4.20"
        assert model["monetary_total"]["payable_amount"] == "24.20"

    def test_creditnote_roundtrip(self):
        model = load_ubl(VALID_DIR / "creditnote-with-totals.xml")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "cn_full_roundtrip.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
        assert reloaded["document_type"] == "CreditNote"
        assert reloaded["id"] == model["id"]
        assert reloaded["tax_total"] == model["tax_total"]
        assert reloaded["monetary_total"] == model["monetary_total"]
        assert reloaded["lines"] == model["lines"]

    def test_write_creditnote_from_scratch(self):
        model = {
            "document_type": "CreditNote",
            "id": "CN-SCRATCH-1",
            "issue_date": "2026-07-15",
            "currency": "GBP",
            "supplier": {"name": "Scratch Supplier"},
            "customer": {"name": "Scratch Customer"},
            "lines": [{"id": "1", "quantity": "3", "amount": "9.00", "item_name": "Item"}],
        }
        result = write_ubl(model)
        assert "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2" in result
        assert "CN-SCRATCH-1" in result
        assert "CreditedQuantity" in result
        reloaded = load_ubl(result.encode("utf-8"))
        assert reloaded["document_type"] == "CreditNote"
        assert reloaded["lines"][0]["quantity"] == "3"
        assert reloaded["supplier"]["name"] == "Scratch Supplier"

    def test_unsupported_document_type_raises_on_write(self):
        model = {"document_type": "DespatchAdvice", "id": "X"}
        with pytest.raises(UblWriteError):
            write_ubl(model)
