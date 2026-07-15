"""Tests for the ubl.Compat facade layer — UblInvoice, UblOrder, UblLineItem.

Each facade subclasses a spec/ stub class and binds spec_qname/spec_fact_ref/
namespace_uri to match the corresponding entry in shared/qname-registry/ubl.yaml.
"""

from __future__ import annotations

from ubl.Compat import UblCreditNote, UblInvoice, UblLineItem, UblOrder
from ubl.spec.document.credit_note import CreditNote as SpecCreditNote
from ubl.spec.document.invoice import Invoice as SpecInvoice
from ubl.spec.document.line_item import LineItem as SpecLineItem
from ubl.spec.document.order import Order as SpecOrder
from ubl.ubl_codec import load_ubl

import pathlib

SAMPLES = pathlib.Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl"
VALID_DIR = SAMPLES / "valid"


class TestUblInvoiceFacade:
    def test_spec_qname_matches_registry(self):
        assert UblInvoice.spec_qname == "ubl:invoice"

    def test_spec_fact_ref_matches_registry(self):
        assert UblInvoice.spec_fact_ref == "FACT-UBL-002"

    def test_namespace_uri_matches_registry(self):
        assert (
            UblInvoice.namespace_uri
            == "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
        )

    def test_subclasses_spec_stub(self):
        assert issubclass(UblInvoice, SpecInvoice)

    def test_instantiation_from_loaded_model(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        facade = UblInvoice(model)
        assert facade.doc_id == "INV-001"
        assert facade.currency == "USD"

    def test_to_dict_returns_copy(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        facade = UblInvoice(model)
        as_dict = facade.to_dict()
        assert as_dict == model
        assert as_dict is not model

    def test_repr(self):
        facade = UblInvoice({"id": "INV-999"})
        assert repr(facade) == "Invoice(id='INV-999')"


class TestUblCreditNoteFacade:
    def test_spec_qname_matches_registry(self):
        assert UblCreditNote.spec_qname == "ubl:credit-note"

    def test_spec_fact_ref_matches_registry(self):
        assert UblCreditNote.spec_fact_ref == "FACT-UBL-105"

    def test_namespace_uri_matches_registry(self):
        assert (
            UblCreditNote.namespace_uri
            == "urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2"
        )

    def test_subclasses_spec_stub(self):
        assert issubclass(UblCreditNote, SpecCreditNote)

    def test_instantiation_from_loaded_model(self):
        model = load_ubl(VALID_DIR / "minimal-creditnote.xml")
        facade = UblCreditNote(model)
        assert facade.doc_id == "CN-001"
        assert facade.currency == "USD"
        assert facade.supplier["name"] == "Acme Corp"

    def test_tax_and_monetary_totals_from_loaded_model(self):
        model = load_ubl(VALID_DIR / "creditnote-with-totals.xml")
        facade = UblCreditNote(model)
        assert facade.tax_total["tax_amount"] == "4.20"
        assert facade.monetary_total["payable_amount"] == "24.20"

    def test_to_dict_returns_copy(self):
        model = load_ubl(VALID_DIR / "minimal-creditnote.xml")
        facade = UblCreditNote(model)
        as_dict = facade.to_dict()
        assert as_dict == model
        assert as_dict is not model

    def test_repr(self):
        facade = UblCreditNote({"id": "CN-999"})
        assert repr(facade) == "CreditNote(id='CN-999')"


class TestUblOrderFacade:
    def test_spec_qname_matches_registry(self):
        assert UblOrder.spec_qname == "ubl:order"

    def test_spec_fact_ref_matches_registry(self):
        assert UblOrder.spec_fact_ref == "FACT-UBL-001"

    def test_namespace_uri_matches_registry(self):
        assert (
            UblOrder.namespace_uri
            == "urn:oasis:names:specification:ubl:schema:xsd:Order-2"
        )

    def test_subclasses_spec_stub(self):
        assert issubclass(UblOrder, SpecOrder)

    def test_instantiation_from_loaded_model(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        facade = UblOrder(model)
        assert facade.doc_id == "ORD-001"
        assert len(facade.lines) == 1

    def test_to_dict_returns_copy(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        facade = UblOrder(model)
        as_dict = facade.to_dict()
        assert as_dict == model
        assert as_dict is not model


class TestUblLineItemFacade:
    def test_spec_qname_matches_registry(self):
        assert UblLineItem.spec_qname == "ubl:line-item"

    def test_spec_fact_ref_matches_registry(self):
        assert UblLineItem.spec_fact_ref == "FACT-UBL-002"

    def test_namespace_uri_matches_registry(self):
        assert (
            UblLineItem.namespace_uri
            == "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        )

    def test_subclasses_spec_stub(self):
        assert issubclass(UblLineItem, SpecLineItem)

    def test_instantiation_from_invoice_line(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        line = UblLineItem(model["lines"][0])
        assert line.line_id == "1"
        assert line.item_name == "Widget"
        assert line.quantity == "10"
        assert line.amount == "100.00"

    def test_instantiation_from_order_line(self):
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        line = UblLineItem(model["lines"][0])
        assert line.line_id == "1"
        assert line.item_name == "Gadget"
        # Order lines have no "amount" key — must default cleanly.
        assert line.amount == ""

    def test_repr(self):
        line = UblLineItem({"id": "L1", "item_name": "Bolt"})
        assert repr(line) == "LineItem(id='L1', item_name='Bolt')"


class TestFacadeNamesOnSpecStubs:
    def test_invoice_spec_facade_names(self):
        assert SpecInvoice.facade_names == ["UblInvoice"]

    def test_credit_note_spec_facade_names(self):
        assert SpecCreditNote.facade_names == ["UblCreditNote"]

    def test_order_spec_facade_names(self):
        assert SpecOrder.facade_names == ["UblOrder"]

    def test_line_item_spec_facade_names(self):
        assert SpecLineItem.facade_names == ["UblLineItem"]
