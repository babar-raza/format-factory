"""UBL-EDIT-001 -- line-scoped CRUD with schema-order preservation and an
explicit reference-rewrite map.

MUST (SAL-UBL-OBL-237188D47391391E): "CRUD for core business components
with schema-order preservation; edits cannot produce elements the schema
forbids at that position." -- narrowed to lines, the category the sibling
obligation names explicitly (see lines.py's own module docstring for the
honest scope boundary).

MUST (SAL-UBL-OBL-AF5263F0FC7036B9): "Line insertion, removal, movement,
and renumbering maintain referential integrity via an explicit
reference-rewrite map."
"""

from __future__ import annotations

from pathlib import Path

import pytest

from format_factory.ubl import UblValidationError, load, validate
from format_factory.ubl.lines import add_line, move_line, remove_line, renumber_lines
from format_factory.ubl.model import XmlNode

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_CBC_NS = f"{{{_CBC}}}"
_CAC_NS = f"{{{_CAC}}}"


def _invoice_bytes(*, lines: str) -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
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
    return XmlNode.create(
        f"{_CAC_NS}InvoiceLine",
        children=(
            XmlNode.create(f"{_CBC_NS}ID", text=line_id),
            XmlNode.create(f"{_CBC_NS}InvoicedQuantity", attributes={"unitCode": "KGM"}, text="1"),
            XmlNode.create(f"{_CBC_NS}LineExtensionAmount", attributes={"currencyID": "USD"}, text="1.00"),
            XmlNode.create(f"{_CAC_NS}Item", children=(XmlNode.create(f"{_CBC_NS}Name", text="Gadget"),)),
        ),
    )


def _line_ids(document: object) -> list[str]:
    return [
        next(gc.text for gc in child.children if gc.qname == f"{_CBC_NS}ID")
        for child in document.root.children  # type: ignore[attr-defined]
        if child.qname == f"{_CAC_NS}InvoiceLine"
    ]


def _load(tmp_path: Path, xml: bytes):
    source = tmp_path / "doc.xml"
    source.write_bytes(xml)
    return load(source)


def test_add_line_appends_after_the_last_existing_line_and_stays_valid(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1")))

    edited = add_line(document, _line_node("2"))

    assert _line_ids(edited) == ["1", "2"]
    assert validate(edited).is_valid is True


def test_add_line_refuses_a_line_id_that_duplicates_an_existing_line(tmp_path: Path) -> None:
    # Regression guard: the base chassis validate() alone has no duplicate-
    # line-id check (that lives in the referential layer built for
    # validate_all() at FF6-EVENT-000296) -- add_line's own before/after
    # comparison must include it directly, or this silently introduces a
    # referential-integrity violation the obligation's own wording forbids.
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1")))

    with pytest.raises(UblValidationError, match="not unique"):
        add_line(document, _line_node("1"))


def test_add_line_to_a_document_with_no_existing_lines(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=""))

    edited = add_line(document, _line_node("1"))

    assert _line_ids(edited) == ["1"]
    assert validate(edited).is_valid is True


def test_remove_line_deletes_the_matching_line_only(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1") + _line_xml("2")))

    edited = remove_line(document, "1")

    assert _line_ids(edited) == ["2"]
    assert validate(edited).is_valid is True


def test_remove_line_raises_for_an_unmatched_id(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1")))

    with pytest.raises(UblValidationError, match="no line with id"):
        remove_line(document, "999")


def test_move_line_reorders_among_lines_only(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1") + _line_xml("2") + _line_xml("3")))

    edited = move_line(document, "3", to_index=0)

    assert _line_ids(edited) == ["3", "1", "2"]
    assert validate(edited).is_valid is True


def test_move_line_raises_for_an_out_of_range_index(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1") + _line_xml("2")))

    with pytest.raises(UblValidationError, match="out of range"):
        move_line(document, "1", to_index=5)


def test_renumber_lines_rewrites_ids_and_returns_the_map(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1") + _line_xml("2")))

    edited, id_map = renumber_lines(document, {"1": "100", "2": "200"})

    assert _line_ids(edited) == ["100", "200"]
    assert id_map == {"1": "100", "2": "200"}
    assert validate(edited).is_valid is True


def test_renumber_lines_raises_when_two_lines_map_to_the_same_new_id(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1") + _line_xml("2")))

    with pytest.raises(UblValidationError, match="same new id"):
        renumber_lines(document, {"1": "9", "2": "9"})


def test_renumber_lines_raises_when_the_target_id_collides_with_an_unrenamed_line(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1") + _line_xml("2")))

    with pytest.raises(UblValidationError, match="collide"):
        renumber_lines(document, {"1": "2"})


def test_renumber_lines_raises_for_an_id_not_present_in_the_document(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1")))

    with pytest.raises(UblValidationError, match="not present"):
        renumber_lines(document, {"999": "5"})


def test_edits_compose_add_then_move_then_renumber_then_remove(tmp_path: Path) -> None:
    document = _load(tmp_path, _invoice_bytes(lines=_line_xml("1")))

    document = add_line(document, _line_node("2"))
    document = move_line(document, "2", to_index=0)
    document, _ = renumber_lines(document, {"1": "100", "2": "200"})
    document = remove_line(document, "200")

    assert _line_ids(document) == ["100"]
    assert validate(document).is_valid is True
