"""UBL-WRITE-001 -- write elements in schema-valid order independent of
mutation order.

MUST (SAL-UBL-OBL-4BD9BBC9F974C175, third clause): "write elements in
schema-valid order independent of mutation order." validator.
reorder_for_schema_order() (wired into dumps()/dump() at
FF6-EVENT-000286) permutes only the positions already occupied by an
already-modeled, order-checked field (_ORDER_CHECKED_COMPONENTS -- the
same ground truth _order_diagnostics validates against) into their
schema-declared relative sequence.

Deliberately narrow, matching _order_diagnostics's own scope exactly:
covers only relative order among these already-modeled fields, not every
child of every UBL complexType -- an unknown/unmodeled child is never
moved, regardless of where it sits relative to known-order siblings.
"""

from __future__ import annotations

from format_factory.ubl import dumps, loads, reorder_for_schema_order, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_INVOICE_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"


def _invoice_with_party(party_body: str) -> bytes:
    return (
        f'<Invoice xmlns="{_INVOICE_NS}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<cac:AccountingSupplierParty><cac:Party>{party_body}</cac:Party>"
        f"</cac:AccountingSupplierParty>"
        f"</Invoice>"
    ).encode()


def test_an_already_correctly_ordered_document_is_returned_unchanged() -> None:
    """A no-op reorder must not even produce a new node -- proves this is a
    conditional transform, not an unconditional rebuild that could
    introduce spurious diffs."""
    document = loads(
        _invoice_with_party(
            '<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>'
            "<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
        )
    )

    reordered = reorder_for_schema_order(document)

    assert reordered is document


def test_reordering_is_idempotent() -> None:
    document = loads(
        _invoice_with_party(
            "<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
            '<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>'
        )
    )

    once = reorder_for_schema_order(document)
    twice = reorder_for_schema_order(once)

    assert twice is once
    assert dumps(once) == dumps(twice)


def test_an_unmodeled_sibling_stays_in_place_between_two_reordered_fields() -> None:
    """The known-order fields (PostalAddress, Contact) are permuted among
    THEIR OWN positions only; an unrecognized element interleaved between
    them is never touched or moved."""
    document = loads(
        _invoice_with_party(
            "<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
            '<ext:Vendor xmlns:ext="urn:example:vendor">acme</ext:Vendor>'
            '<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>'
        )
    )

    reordered = reorder_for_schema_order(document)
    # children[0] is cbc:ID; children[1] is cac:AccountingSupplierParty.
    party = reordered.root.children[1].children[0]
    local_names = [child.qname.rsplit("}", 1)[-1] for child in party.children]

    assert local_names == ["PostalAddress", "Vendor", "Contact"]


def test_reordering_a_nested_order_checked_component_inside_another() -> None:
    """LegalMonetaryTotal (6 order-checked fields) nested inside a normal
    document structure reorders independently of its own container."""
    body = (
        '<cac:LegalMonetaryTotal>'
        '<cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        '<cbc:LineExtensionAmount currencyID="USD">1.00</cbc:LineExtensionAmount>'
        "</cac:LegalMonetaryTotal>"
    )
    document = loads(
        (
            f'<Invoice xmlns="{_INVOICE_NS}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
            f"<cbc:ID>INV-001</cbc:ID>{body}</Invoice>"
        ).encode()
    )

    reordered = reorder_for_schema_order(document)
    total = reordered.root.children[1]
    local_names = [child.qname.rsplit("}", 1)[-1] for child in total.children]

    assert local_names == ["LineExtensionAmount", "PayableAmount"]


def test_reordered_output_validates_cleanly_where_the_original_did_not() -> None:
    document = loads(
        _invoice_with_party(
            "<cac:Contact><cbc:Name>Y</cbc:Name></cac:Contact>"
            '<cac:PostalAddress><cbc:CityName>X</cbc:CityName></cac:PostalAddress>'
        )
    )

    assert validate(document).is_valid is False

    reordered = reorder_for_schema_order(document)

    assert validate(reordered).is_valid is True
