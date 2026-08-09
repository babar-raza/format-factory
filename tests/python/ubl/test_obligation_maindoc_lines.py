"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-VALIDATE-001 / UBL-DOCTYPES-001 /
UBL-EDIT-001 / UBL-REF-001 / UBL-VALUES-001 -- the maindoc-specific line
and response aggregates (cac:OrderLine, cac:CreditNoteLine,
cac:DespatchLine, cac:DocumentResponse), a 23-way cross-capability
duplicate spanning 5 distinct rule_texts (one per document type).

MUST: "A UBL Order document ... with order lines carried as cac:OrderLine
aggregate components" (Order, 2 rule_text variants, 10 obligations total).
MUST: "A UBL CreditNote document ... with cac:CreditNoteLine aggregates
for its lines" (5 obligations).
MUST: "A UBL DespatchAdvice document ... carrying cac:DespatchLine
aggregates" (4 obligations).
MUST: "A UBL ApplicationResponse document ... carrying cac:DocumentResponse
aggregates for business-level acknowledgement" (4 obligations).

Before this slice: none of OrderLine, CreditNoteLine, DespatchLine, or
DocumentResponse had any model representation -- confirmed by grepping the
model package (zero hits for each class name). Unblocked the same way
events 193/194 unblocked PaymentMeans.payee_financial_account and
Party/PostalAddress: reading the pinned OASIS UBL 2.3 release package's
own vendored XSD directly (xsd/common/UBL-CommonAggregateComponents-2.3.xsd,
extracted from the ZIP, not a SAL-fact paraphrase or memory). See
model/lines.py's own module docstring for the exact scope boundary
(identifying/quantity/amount fields plus required nested aggregates,
mirroring InvoiceLine's existing precedent; each type's remaining 8-30
optional delivery/warranty/pricing-reference fields are not modeled).
"""

from __future__ import annotations

import pytest

from format_factory.ubl import (
    Amount,
    Code,
    CreditNoteLine,
    DespatchLine,
    DocumentReference,
    DocumentResponse,
    Identifier,
    Item,
    LineItem,
    OrderLine,
    Quantity,
    Response,
    UblValidationError,
    XmlNode,
    credit_note_line_of,
    despatch_line_of,
    document_response_of,
    line_item_of,
    order_line_of,
)

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _leaf(local: str, text: str, **attrs: str) -> XmlNode:
    return XmlNode.create("{" + CBC + "}" + local, text=text, attributes=attrs)


def _cac(local: str, children: tuple[XmlNode, ...]) -> XmlNode:
    return XmlNode.create("{" + CAC + "}" + local, children=children)


def _item_node(name: str = "Widget") -> XmlNode:
    return _cac("Item", (_leaf("Name", name),))


# ── cac:LineItem / cac:OrderLine ────────────────────────────────────────


def _line_item_node() -> XmlNode:
    return _cac(
        "LineItem",
        (
            _leaf("ID", "1"),
            _leaf("Quantity", "5"),
            _leaf("LineExtensionAmount", "50.00", currencyID="EUR"),
            _item_node(),
        ),
    )


def test_line_item_projects_with_its_fields() -> None:
    line_item = line_item_of(_line_item_node())

    assert line_item == LineItem(
        id=Identifier("1"),
        item=Item(name="Widget"),
        quantity=Quantity("5"),
        line_extension_amount=Amount("50.00", "EUR"),
    )


def test_order_line_projects_with_its_line_item() -> None:
    order_line = order_line_of(_cac("OrderLine", (_line_item_node(),)))

    assert order_line == OrderLine(line_item=line_item_of(_line_item_node()))


def test_order_line_requires_a_line_item() -> None:
    with pytest.raises(UblValidationError):
        order_line_of(_cac("OrderLine", ()))


def test_line_item_requires_an_item() -> None:
    with pytest.raises(UblValidationError):
        line_item_of(_cac("LineItem", (_leaf("ID", "1"),)))


# ── cac:CreditNoteLine ───────────────────────────────────────────────────


def test_credit_note_line_projects_with_its_fields() -> None:
    node = _cac(
        "CreditNoteLine",
        (
            _leaf("ID", "1"),
            _leaf("CreditedQuantity", "2"),
            _leaf("LineExtensionAmount", "20.00", currencyID="EUR"),
            _item_node(),
        ),
    )

    line = credit_note_line_of(node)

    assert line == CreditNoteLine(
        id=Identifier("1"),
        credited_quantity=Quantity("2"),
        line_extension_amount=Amount("20.00", "EUR"),
        item=Item(name="Widget"),
    )


def test_credit_note_line_requires_only_an_id() -> None:
    """Unlike InvoiceLine, CreditNoteLineType makes quantity, amount, and
    item all optional (minOccurs="0") per the pinned XSD -- only cbc:ID is
    required (minOccurs="1")."""
    line = credit_note_line_of(_cac("CreditNoteLine", (_leaf("ID", "2"),)))

    assert line == CreditNoteLine(id=Identifier("2"))


def test_credit_note_line_requires_an_id() -> None:
    with pytest.raises(UblValidationError):
        credit_note_line_of(_cac("CreditNoteLine", ()))


# ── cac:DespatchLine ─────────────────────────────────────────────────────


def test_despatch_line_projects_with_its_fields() -> None:
    node = _cac(
        "DespatchLine",
        (_leaf("ID", "1"), _leaf("DeliveredQuantity", "3"), _item_node()),
    )

    line = despatch_line_of(node)

    assert line == DespatchLine(
        id=Identifier("1"), item=Item(name="Widget"), delivered_quantity=Quantity("3")
    )


def test_despatch_line_requires_an_item() -> None:
    with pytest.raises(UblValidationError):
        despatch_line_of(_cac("DespatchLine", (_leaf("ID", "1"),)))


def test_despatch_line_requires_an_id() -> None:
    with pytest.raises(UblValidationError):
        despatch_line_of(_cac("DespatchLine", (_item_node(),)))


def test_a_spoofed_id_sibling_from_an_unrelated_namespace_is_not_projected() -> None:
    """FF6-EVENT-000484: despatch_line_of() now uses find_qname() internally
    (UBL-PARSE-001's own namespace-precise primitive, wave 3 of the ~79
    disclosed find()/find_all() call sites) -- proven directly that a
    same-local-name ID sibling from an attacker-controlled namespace is
    correctly ignored rather than shadowing the real cbc:ID value."""
    evil = "urn:evil:attacker:namespace"
    node = _cac(
        "DespatchLine",
        (
            XmlNode.create(f"{{{evil}}}ID", text="SPOOFED-999"),
            _leaf("ID", "1"),
            _item_node(),
        ),
    )

    line = despatch_line_of(node)

    assert line.id == Identifier("1")


# ── cac:DocumentResponse ─────────────────────────────────────────────────


def test_document_response_projects_with_response_and_document_references() -> None:
    node = _cac(
        "DocumentResponse",
        (
            _cac("Response", (_leaf("ResponseCode", "AP"), _leaf("Description", "Accepted"))),
            _cac("DocumentReference", (_leaf("ID", "INV-001"),)),
        ),
    )

    response = document_response_of(node)

    assert response == DocumentResponse(
        response=Response(response_code=Code("AP"), description="Accepted"),
        document_references=(DocumentReference(id=Identifier("INV-001")),),
    )


def test_document_response_requires_a_response() -> None:
    with pytest.raises(UblValidationError):
        document_response_of(_cac("DocumentResponse", ()))


def test_document_response_with_multiple_document_references() -> None:
    node = _cac(
        "DocumentResponse",
        (
            _cac("Response", (_leaf("ResponseCode", "AP"),)),
            _cac("DocumentReference", (_leaf("ID", "A"),)),
            _cac("DocumentReference", (_leaf("ID", "B"),)),
        ),
    )

    response = document_response_of(node)

    assert [ref.id.value for ref in response.document_references] == ["A", "B"]


# ── Through the real document pipeline ──────────────────────────────────


def test_an_order_line_survives_a_real_document_round_trip() -> None:
    from format_factory.ubl import dumps, find, loads

    source = (
        f'<Order xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2" '
        f'xmlns:cbc="{CBC}" xmlns:cac="{CAC}">'
        f"<cbc:ID>ORD-001</cbc:ID>"
        f"<cac:OrderLine>"
        f"<cac:LineItem>"
        f"<cbc:ID>1</cbc:ID>"
        f"<cbc:Quantity>5</cbc:Quantity>"
        f"<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        f"</cac:LineItem>"
        f"</cac:OrderLine>"
        f"</Order>"
    ).encode()

    original = loads(source)
    reloaded = loads(dumps(original))

    order_line = order_line_of(find(reloaded.root, "OrderLine"))
    assert order_line.line_item.id.value == "1"
    assert order_line.line_item.quantity == Quantity("5")
    assert order_line.line_item.item.name == "Widget"
