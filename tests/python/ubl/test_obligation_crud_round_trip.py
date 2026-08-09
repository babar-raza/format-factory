"""UBL-EDIT-001 -- every documented CRUD mutation proven by a real
dump()-then-reload round trip.

MUST (SAL-UBL-OBL-237188D47391391E): "CRUD for core business components
with schema-order preservation; edits cannot produce elements the schema
forbids at that position." Release gate: "Every documented mutation
proven by round-trip tests."

The 6 existing CRUD test files (test_obligation_line_crud.py,
test_obligation_party_replacement.py, test_obligation_component_update.py,
test_obligation_component_create_adjacent.py,
test_obligation_component_removal.py,
test_obligation_component_first_occurrence_insertion.py) each verify their
own mutation's IN-MEMORY correctness thoroughly, but none of them call
dumps()/dump() at all -- confirmed directly by grep before writing this
file, not assumed. A document that is correct in memory but never proven
to survive real serialization and reload is not what "round-trip tests"
means; this file closes exactly that gap for all 8 documented mutations
(add_line, remove_line, move_line, renumber_lines, replace_party,
update_component, add_component -- both the already-has-an-occurrence and
first-occurrence paths -- and remove_component), each via a genuine
dumps()-then-load() cycle on real bytes, not an in-memory shortcut.
"""

from __future__ import annotations

from format_factory.ubl import UblDocument, dumps, load, validate
from format_factory.ubl.components import (
    add_component,
    remove_component,
    replace_party,
    update_component,
)
from format_factory.ubl.lines import add_line, move_line, remove_line, renumber_lines
from format_factory.ubl.model import XmlNode

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice_bytes(*, lines: str = "", payment_means: str = "") -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        f"{payment_means}"
        '<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>http://x.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
        '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
        f"{lines}"
        "</Invoice>"
    ).encode()


def _line_xml(line_id: str) -> str:
    return (
        "<cac:InvoiceLine>"
        f"<cbc:ID>{line_id}</cbc:ID>"
        '<cbc:InvoicedQuantity unitCode="KGM">1</cbc:InvoicedQuantity>'
        '<cbc:LineExtensionAmount currencyID="USD">1.00</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        "</cac:InvoiceLine>"
    )


def _line_node(line_id: str) -> XmlNode:
    doc = load(_invoice_bytes(lines=_line_xml(line_id)))
    return next(c for c in doc.root.children if c.qname.endswith("InvoiceLine"))


def _payment_means_xml(code: str) -> str:
    return f"<cac:PaymentMeans><cbc:PaymentMeansCode>{code}</cbc:PaymentMeansCode></cac:PaymentMeans>"


def _payment_means_node(code: str) -> XmlNode:
    doc = load(_invoice_bytes(payment_means=_payment_means_xml(code)))
    return next(c for c in doc.root.children if c.qname.endswith("PaymentMeans"))


def _party_node(website: str) -> XmlNode:
    doc = load(_invoice_bytes())
    party = next(
        c for c in doc.root.children if c.qname.endswith("AccountingSupplierParty")
    ).children[0]
    return XmlNode(
        qname=party.qname,
        children=(XmlNode(qname=f"{{{_CBC}}}WebsiteURI", text=website),),
    )


def _dumped_and_reloaded(document: UblDocument) -> UblDocument:
    return load(dumps(document))


def test_add_line_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes(lines=_line_xml("1")))
    edited = add_line(document, _line_node("2"))

    reloaded = _dumped_and_reloaded(edited)
    ids = [
        c.children[0].text
        for c in reloaded.root.children
        if c.qname.endswith("InvoiceLine")
    ]
    assert ids == ["1", "2"]
    assert validate(reloaded).is_valid


def test_remove_line_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes(lines=_line_xml("1") + _line_xml("2")))
    edited = remove_line(document, line_id="1")

    reloaded = _dumped_and_reloaded(edited)
    ids = [
        c.children[0].text
        for c in reloaded.root.children
        if c.qname.endswith("InvoiceLine")
    ]
    assert ids == ["2"]
    assert validate(reloaded).is_valid


def test_move_line_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes(lines=_line_xml("1") + _line_xml("2")))
    edited = move_line(document, line_id="2", to_index=0)

    reloaded = _dumped_and_reloaded(edited)
    ids = [
        c.children[0].text
        for c in reloaded.root.children
        if c.qname.endswith("InvoiceLine")
    ]
    assert ids == ["2", "1"]
    assert validate(reloaded).is_valid


def test_renumber_lines_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes(lines=_line_xml("1")))
    edited, id_map = renumber_lines(document, {"1": "INV-1"})

    reloaded = _dumped_and_reloaded(edited)
    ids = [
        c.children[0].text
        for c in reloaded.root.children
        if c.qname.endswith("InvoiceLine")
    ]
    assert ids == ["INV-1"]
    assert id_map == {"1": "INV-1"}
    assert validate(reloaded).is_valid


def test_replace_party_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes())
    edited = replace_party(
        document, role="AccountingSupplierParty", new_party=_party_node("http://new.example")
    )

    reloaded = _dumped_and_reloaded(edited)
    supplier = next(
        c for c in reloaded.root.children if c.qname.endswith("AccountingSupplierParty")
    )
    website = supplier.children[0].children[0]
    assert website.text == "http://new.example"
    assert validate(reloaded).is_valid


def test_update_component_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes(payment_means=_payment_means_xml("10")))
    edited = update_component(
        document,
        component_name="PaymentMeans",
        index=0,
        new_component=_payment_means_node("30"),
    )

    reloaded = _dumped_and_reloaded(edited)
    payment_means = next(c for c in reloaded.root.children if c.qname.endswith("PaymentMeans"))
    assert payment_means.children[0].text == "30"
    assert validate(reloaded).is_valid


def test_add_component_additional_occurrence_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes(payment_means=_payment_means_xml("10")))
    edited = add_component(
        document, component_name="PaymentMeans", new_component=_payment_means_node("30")
    )

    reloaded = _dumped_and_reloaded(edited)
    codes = [
        c.children[0].text for c in reloaded.root.children if c.qname.endswith("PaymentMeans")
    ]
    assert codes == ["10", "30"]
    assert validate(reloaded).is_valid


def test_add_component_first_occurrence_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes())
    edited = add_component(
        document, component_name="PaymentMeans", new_component=_payment_means_node("42")
    )

    reloaded = _dumped_and_reloaded(edited)
    payment_means = [
        c for c in reloaded.root.children if c.qname.endswith("PaymentMeans")
    ]
    assert len(payment_means) == 1
    assert payment_means[0].children[0].text == "42"
    assert validate(reloaded).is_valid


def test_remove_component_survives_a_real_dump_and_reload() -> None:
    document = load(_invoice_bytes(payment_means=_payment_means_xml("10")))
    edited = remove_component(document, component_name="PaymentMeans", index=0)

    reloaded = _dumped_and_reloaded(edited)
    payment_means = [
        c for c in reloaded.root.children if c.qname.endswith("PaymentMeans")
    ]
    assert payment_means == []
    assert validate(reloaded).is_valid
