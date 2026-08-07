"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-DOCTYPES-001 / UBL-VALIDATE-001 /
UBL-REF-001 / UBL-SIGN-001 -- cac:AllowanceCharge cardinality and element
order, the 14th component added to the already-modeled cardinality/order
cluster (events 216-223, 231).

MUST (SAL-UBL-OBL-03AF3A7D3A76F362 and cross-capability duplicates):
"full schema and cardinality validation" -- narrowed further this slice.
MUST (SAL-UBL-OBL-3B43504E9C74003C and cross-capability duplicates):
"child elements ... must appear in the order declared by the schema
sequence model" -- narrowed further this slice.

Read directly from the pinned OASIS UBL 2.3 CommonAggregateComponents
schema (AllowanceChargeType): ChargeIndicator (1) and
AllowanceChargeReasonCode/Amount (0..1) are maxOccurs=1, in that declared
order, matching this package's own AllowanceCharge.charge_indicator/
reason_code/amount fields. AllowanceChargeReason is deliberately excluded
from both checks -- the schema declares it minOccurs=0 maxOccurs=UNBOUNDED
(genuinely repeatable), even though this package's own AllowanceCharge.
reason field models only the first occurrence as a singular value, the
same model-scoping question already documented for PaymentMeans.PaymentID
and Response.Description elsewhere in this cluster.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblWriteError, dumps, loads, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_INVOICE_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"


def _invoice_with(allowance_body: str) -> bytes:
    return (
        f'<Invoice xmlns="{_INVOICE_NS}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<cac:AllowanceCharge>{allowance_body}</cac:AllowanceCharge>"
        f"</Invoice>"
    ).encode()


_VALID_BODY = (
    "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
    "<cbc:AllowanceChargeReasonCode>95</cbc:AllowanceChargeReasonCode>"
    '<cbc:Amount currencyID="EUR">1.00</cbc:Amount>'
)


def test_a_well_formed_allowance_charge_validates_cleanly() -> None:
    document = loads(_invoice_with(_VALID_BODY))

    report = validate(document)

    assert report.is_valid is True


def test_a_duplicate_charge_indicator_is_a_cardinality_violation() -> None:
    body = (
        "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
        "<cbc:ChargeIndicator>false</cbc:ChargeIndicator>"
        '<cbc:Amount currencyID="EUR">1.00</cbc:Amount>'
    )
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_duplicate_amount_is_a_cardinality_violation() -> None:
    body = (
        "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
        '<cbc:Amount currencyID="EUR">1.00</cbc:Amount>'
        '<cbc:Amount currencyID="EUR">2.00</cbc:Amount>'
    )
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_amount_before_charge_indicator_is_an_order_violation() -> None:
    body = '<cbc:Amount currencyID="EUR">1.00</cbc:Amount><cbc:ChargeIndicator>true</cbc:ChargeIndicator>'
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.order.violation" for item in report.diagnostics)


def test_reason_code_after_amount_is_an_order_violation() -> None:
    body = (
        "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
        '<cbc:Amount currencyID="EUR">1.00</cbc:Amount>'
        "<cbc:AllowanceChargeReasonCode>95</cbc:AllowanceChargeReasonCode>"
    )
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.order.violation" for item in report.diagnostics)


def test_a_repeated_allowance_charge_reason_is_not_flagged_as_a_duplicate() -> None:
    """AllowanceChargeReason is genuinely repeatable (maxOccurs=UNBOUNDED)
    per the schema -- multiple occurrences must not be treated as a
    cardinality violation."""
    body = (
        "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
        "<cbc:AllowanceChargeReason>Volume discount</cbc:AllowanceChargeReason>"
        "<cbc:AllowanceChargeReason>Loyalty discount</cbc:AllowanceChargeReason>"
        '<cbc:Amount currencyID="EUR">1.00</cbc:Amount>'
    )
    document = loads(_invoice_with(body))

    report = validate(document)

    assert report.is_valid is True


def test_dumps_refuses_a_document_with_an_out_of_order_allowance_charge() -> None:
    body = '<cbc:Amount currencyID="EUR">1.00</cbc:Amount><cbc:ChargeIndicator>true</cbc:ChargeIndicator>'
    document = loads(_invoice_with(body))

    with pytest.raises(UblWriteError, match="ChargeIndicator"):
        dumps(document)


def test_dumps_writes_a_well_formed_allowance_charge_without_incident() -> None:
    document = loads(_invoice_with(_VALID_BODY))

    out = dumps(document)

    assert b"cac:AllowanceCharge" in out
