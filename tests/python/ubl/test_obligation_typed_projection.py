"""UBL-VALUES-001, second half: typed values reachable from a parsed document.

The value types were correct but unreachable: an Invoice parsed from XML yielded
untyped `XmlNode` text, so a caller wanting the invoice total still had to pull
a string out and build a Decimal themselves -- which is exactly where the float
the specification forbids gets introduced.

This projects between the lossless `XmlNode` tree and the typed values, in both
directions, carrying the supplementary attributes across:

  "retain currencyID, unitCode, and scheme attributes through edits"
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from format_factory.ubl import (
    Amount,
    Identifier,
    Quantity,
    UblValidationError,
    XmlNode,
    amount_of,
    binary_object_of,
    code_of,
    find,
    find_all,
    identifier_of,
    loads,
    local_name,
    quantity_of,
    to_node,
)

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

INVOICE = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="{CBC}" xmlns:cac="{CAC}">
<cbc:ID schemeID="GS1" schemeAgencyID="9">INV-001</cbc:ID>
<cbc:DocumentCurrencyCode listID="ISO4217">EUR</cbc:DocumentCurrencyCode>
<cac:InvoiceLine>
  <cbc:ID>1</cbc:ID>
  <cbc:InvoicedQuantity unitCode="KGM">2.5</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="EUR">25.00</cbc:LineExtensionAmount>
</cac:InvoiceLine>
<cac:InvoiceLine>
  <cbc:ID>2</cbc:ID>
  <cbc:InvoicedQuantity unitCode="LTR">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="EUR">4.99</cbc:LineExtensionAmount>
</cac:InvoiceLine>
</Invoice>""".encode("utf-8")


@pytest.fixture
def invoice() -> XmlNode:
    return loads(INVOICE).root


# ── Navigating the tree by local name ──────────────────────────────────────


def test_local_name_strips_the_namespace(invoice: XmlNode) -> None:
    assert local_name(invoice.qname) == "Invoice"
    assert local_name("{" + CBC + "}ID") == "ID"
    assert local_name("Unqualified") == "Unqualified"


def test_find_locates_a_child_by_local_name(invoice: XmlNode) -> None:
    """Callers should not have to spell Clark notation to reach cbc:ID."""
    node = find(invoice, "ID")

    assert node is not None and node.text == "INV-001"


def test_find_returns_none_when_absent(invoice: XmlNode) -> None:
    assert find(invoice, "NoSuchElement") is None


def test_find_all_returns_every_match_in_document_order(invoice: XmlNode) -> None:
    lines = find_all(invoice, "InvoiceLine")

    assert len(lines) == 2
    assert [find(line, "ID").text for line in lines] == ["1", "2"]


# ── Projecting XML into typed values ───────────────────────────────────────


def test_an_amount_element_projects_to_an_amount(invoice: XmlNode) -> None:
    line = find_all(invoice, "InvoiceLine")[0]

    amount = amount_of(find(line, "LineExtensionAmount"))

    assert amount == Amount("25.00", "EUR")
    assert amount.value == Decimal("25.00")


def test_a_quantity_element_projects_with_its_unit_code(invoice: XmlNode) -> None:
    line = find_all(invoice, "InvoiceLine")[0]

    quantity = quantity_of(find(line, "InvoicedQuantity"))

    assert quantity == Quantity("2.5", "KGM")


def test_an_id_element_projects_with_its_scheme_attributes(invoice: XmlNode) -> None:
    identifier = identifier_of(find(invoice, "ID"))

    assert identifier == Identifier("INV-001", scheme_id="GS1", scheme_agency_id="9")


def test_a_code_element_projects_with_its_list_attributes(invoice: XmlNode) -> None:
    code = code_of(find(invoice, "DocumentCurrencyCode"))

    assert code.value == "EUR" and code.list_id == "ISO4217"


def test_an_amount_without_a_currency_id_is_refused(invoice: XmlNode) -> None:
    """The specification requires currencyID on amount-typed components. A
    projection that defaulted it would invent a currency the document never
    stated -- the single most dangerous thing this layer could do."""
    bare = XmlNode.create("{" + CBC + "}LineExtensionAmount", text="25.00")

    with pytest.raises(UblValidationError) as raised:
        amount_of(bare)

    assert "currency" in str(raised.value).lower()


def test_projecting_a_non_numeric_amount_is_refused() -> None:
    node = XmlNode.create(
        "{" + CBC + "}LineExtensionAmount", attributes={"currencyID": "EUR"}, text="abc"
    )

    with pytest.raises(UblValidationError):
        amount_of(node)


def test_projecting_a_missing_node_is_refused() -> None:
    """`find` returns None for an absent element; passing that straight into a
    projection is the obvious caller mistake, so it fails loudly."""
    with pytest.raises(UblValidationError):
        amount_of(None)  # type: ignore[arg-type]


def test_a_binary_object_projects_with_its_mime_code() -> None:
    node = XmlNode.create(
        "{" + CBC + "}EmbeddedDocumentBinaryObject",
        attributes={"mimeCode": "application/pdf", "filename": "invoice.pdf"},
        text="aGVsbG8=",
    )

    attachment = binary_object_of(node)

    assert attachment.data == b"hello"
    assert attachment.mime_code == "application/pdf"
    assert attachment.filename == "invoice.pdf"


# ── The whole point: totalling an invoice without touching a float ─────────


def test_line_amounts_sum_exactly(invoice: XmlNode) -> None:
    """What this layer exists for. Before it, reaching the total meant pulling
    strings out of XmlNode and building Decimals by hand -- or reaching for
    float, which the specification forbids."""
    lines = find_all(invoice, "InvoiceLine")

    total = amount_of(find(lines[0], "LineExtensionAmount"))
    for line in lines[1:]:
        total = total + amount_of(find(line, "LineExtensionAmount"))

    assert total == Amount("29.99", "EUR")


# ── Projecting typed values back to XML ────────────────────────────────────


def test_an_amount_projects_back_to_a_node_with_its_currency() -> None:
    node = to_node("{" + CBC + "}LineExtensionAmount", Amount("25.00", "EUR"))

    assert node.text == "25.00"
    assert dict(node.attributes)["currencyID"] == "EUR"


def test_a_quantity_projects_back_with_its_unit_code() -> None:
    node = to_node("{" + CBC + "}InvoicedQuantity", Quantity("2.5", "KGM"))

    assert node.text == "2.5"
    assert dict(node.attributes)["unitCode"] == "KGM"


def test_a_quantity_without_a_unit_code_emits_no_attribute() -> None:
    """unitCode is optional; emitting an empty one would assert a unit of
    measure the document never had."""
    node = to_node("{" + CBC + "}InvoicedQuantity", Quantity("2.5"))

    assert node.attributes == ()


def test_an_identifier_projects_back_with_its_scheme_attributes() -> None:
    node = to_node("{" + CBC + "}ID", Identifier("INV-001", scheme_id="GS1"))

    assert node.text == "INV-001"
    assert dict(node.attributes)["schemeID"] == "GS1"


def test_projection_round_trips_without_losing_attributes(invoice: XmlNode) -> None:
    """The obligation is that supplementary attributes survive EDITS, so the
    round trip through the typed layer must not drop them."""
    original = find(invoice, "ID")

    rebuilt = to_node(original.qname, identifier_of(original))

    assert rebuilt.text == original.text
    assert dict(rebuilt.attributes) == dict(original.attributes)


def test_an_amount_round_trips_through_the_typed_layer(invoice: XmlNode) -> None:
    original = find(find_all(invoice, "InvoiceLine")[0], "LineExtensionAmount")

    rebuilt = to_node(original.qname, amount_of(original))

    assert rebuilt.text == original.text
    assert dict(rebuilt.attributes) == dict(original.attributes)


def test_to_node_refuses_a_type_it_does_not_model() -> None:
    """Silently stringifying an unknown value would put unvalidated text into a
    business document."""
    with pytest.raises(UblValidationError):
        to_node("{" + CBC + "}Something", object())  # type: ignore[arg-type]
