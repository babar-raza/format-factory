"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-DOCTYPES-001 / UBL-VALIDATE-001 /
UBL-REF-001 / UBL-SIGN-001 -- cac:Item and cac:Price cardinality and
element order, the 15th and 16th components added to the already-modeled
cardinality/order cluster (events 216-223, 231, 238).

MUST (SAL-UBL-OBL-03AF3A7D3A76F362 and cross-capability duplicates):
"full schema and cardinality validation" -- narrowed further this slice.
MUST (SAL-UBL-OBL-3B43504E9C74003C and cross-capability duplicates):
"child elements ... must appear in the order declared by the schema
sequence model" -- narrowed further this slice.

Read directly from the pinned OASIS UBL 2.3 CommonAggregateComponents
schema:

  ItemType declares Name as maxOccurs=1, matching this package's own
  Item.name field -- the type's only single-occurrence child this package
  models at all. Item.identifiers/classification_codes are deliberately
  excluded, matching the exclusion already documented for this cluster:
  ItemType has no direct cbc:ID or cbc:CommodityClassification child at
  all, a genuinely separate, unresolved model-field-mapping question.

  PriceType declares PriceAmount (1, required) and BaseQuantity (0..1) as
  maxOccurs=1, matching this package's own Price.price_amount/
  base_quantity fields exactly, in that declared order.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblWriteError, dumps, loads, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_INVOICE_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"


def _invoice_with(body: str) -> bytes:
    return (
        f'<Invoice xmlns="{_INVOICE_NS}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"{body}"
        f"</Invoice>"
    ).encode()


# ── cac:Item ─────────────────────────────────────────────────────────────


def test_an_item_with_a_single_name_validates_cleanly() -> None:
    document = loads(_invoice_with("<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"))

    report = validate(document)

    assert report.is_valid is True


def test_an_item_with_two_names_is_a_cardinality_violation() -> None:
    body = "<cac:Item><cbc:Name>Widget</cbc:Name><cbc:Name>Gadget</cbc:Name></cac:Item>"
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


# ── cac:Price ────────────────────────────────────────────────────────────

_VALID_PRICE_BODY = (
    '<cac:Price><cbc:PriceAmount currencyID="EUR">1.00</cbc:PriceAmount>'
    '<cbc:BaseQuantity unitCode="EA">1</cbc:BaseQuantity></cac:Price>'
)


def test_a_well_formed_price_validates_cleanly() -> None:
    document = loads(_invoice_with(_VALID_PRICE_BODY))

    report = validate(document)

    assert report.is_valid is True


def test_a_duplicate_price_amount_is_a_cardinality_violation() -> None:
    body = (
        '<cac:Price><cbc:PriceAmount currencyID="EUR">1.00</cbc:PriceAmount>'
        '<cbc:PriceAmount currencyID="EUR">2.00</cbc:PriceAmount></cac:Price>'
    )
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_duplicate_base_quantity_is_a_cardinality_violation() -> None:
    body = (
        '<cac:Price><cbc:PriceAmount currencyID="EUR">1.00</cbc:PriceAmount>'
        '<cbc:BaseQuantity unitCode="EA">1</cbc:BaseQuantity>'
        '<cbc:BaseQuantity unitCode="EA">2</cbc:BaseQuantity></cac:Price>'
    )
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_base_quantity_before_price_amount_is_an_order_violation() -> None:
    body = (
        '<cac:Price><cbc:BaseQuantity unitCode="EA">1</cbc:BaseQuantity>'
        '<cbc:PriceAmount currencyID="EUR">1.00</cbc:PriceAmount></cac:Price>'
    )
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.order.violation" for item in report.diagnostics)


def test_dumps_refuses_a_document_with_an_out_of_order_price() -> None:
    body = (
        '<cac:Price><cbc:BaseQuantity unitCode="EA">1</cbc:BaseQuantity>'
        '<cbc:PriceAmount currencyID="EUR">1.00</cbc:PriceAmount></cac:Price>'
    )
    document = loads(_invoice_with(body))

    with pytest.raises(UblWriteError, match="PriceAmount"):
        dumps(document)


def test_dumps_writes_a_well_formed_item_and_price_without_incident() -> None:
    body = "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>" + _VALID_PRICE_BODY
    document = loads(_invoice_with(body))

    out = dumps(document)

    assert b"cac:Item" in out
    assert b"cac:Price" in out
