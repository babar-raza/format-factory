"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-DOCTYPES-001 / UBL-VALIDATE-001 /
UBL-REF-001 -- cardinality validation, extended to PaymentMeans/
PayeeFinancialAccount.

MUST (SAL-UBL-OBL-03AF3A7D3A76F362 and its cross-capability duplicates):
"UBL document schemas are W3C XML Schema definitions and conforming
documents must be valid against the maindoc schema of their declared
type."

This extends the cardinality-validation slice already proven for
cac:Party/cac:PostalAddress/cac:Contact to cac:PaymentMeans and
cac:PayeeFinancialAccount, the same package's other already-typed
aggregate components. Every field's exact cardinality is read directly
from the pinned OASIS UBL 2.3 CommonAggregateComponents schema
(xsd/common/UBL-CommonAggregateComponents-2.3.xsd, PaymentMeansType and
FinancialAccountType complexTypes, read from the pinned release ZIP).

PaymentMeans.PaymentID is deliberately excluded from this check even
though it is a modeled field: the schema declares it minOccurs=0
maxOccurs=UNBOUNDED (genuinely repeatable), unlike PaymentMeansCode/
PaymentDueDate/PayeeFinancialAccount, which are all maxOccurs=1. Proven
directly below, not merely assumed.
"""

from __future__ import annotations

import pytest
from format_factory.ubl import UblWriteError, XmlNode, dumps, loads, validate

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice_with_payment_means(payment_means_body: str) -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"<cac:PaymentMeans>{payment_means_body}</cac:PaymentMeans>"
        f"</Invoice>"
    ).encode()


# ── cac:PaymentMeans: PaymentMeansCode/PaymentDueDate/PayeeFinancialAccount
#    are each 0..1 (PaymentMeansCode is 1..1) in the schema ────────────────


def test_a_payment_means_with_a_single_code_validates_cleanly() -> None:
    body = "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is True


def test_two_payment_means_codes_is_a_cardinality_violation() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cbc:PaymentMeansCode>31</cbc:PaymentMeansCode>"
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_two_payment_due_dates_is_a_cardinality_violation() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cbc:PaymentDueDate>2024-01-01</cbc:PaymentDueDate>"
        "<cbc:PaymentDueDate>2024-02-01</cbc:PaymentDueDate>"
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_two_payee_financial_accounts_is_a_cardinality_violation() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cac:PayeeFinancialAccount><cbc:ID>ACC1</cbc:ID></cac:PayeeFinancialAccount>"
        "<cac:PayeeFinancialAccount><cbc:ID>ACC2</cbc:ID></cac:PayeeFinancialAccount>"
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_multiple_payment_ids_are_not_a_violation_the_schema_declares_them_repeatable() -> None:
    """PaymentID is minOccurs=0 maxOccurs=UNBOUNDED in PaymentMeansType --
    genuinely different from the maxOccurs=1 fields above, proven directly
    rather than assumed uniform."""
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cbc:PaymentID>REF-1</cbc:PaymentID>"
        "<cbc:PaymentID>REF-2</cbc:PaymentID>"
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is True


# ── cac:PaymentMeans element order: PaymentMeansCode/PaymentDueDate/
#    PayeeFinancialAccount, in that schema-declared order ─────────────────


def test_payment_means_fields_in_declared_order_validate_cleanly() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cbc:PaymentDueDate>2024-01-01</cbc:PaymentDueDate>"
        '<cac:PayeeFinancialAccount><cbc:ID>ACC1</cbc:ID></cac:PayeeFinancialAccount>'
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is True


def test_payee_financial_account_before_payment_due_date_is_an_order_violation() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        '<cac:PayeeFinancialAccount><cbc:ID>ACC1</cbc:ID></cac:PayeeFinancialAccount>'
        "<cbc:PaymentDueDate>2024-01-01</cbc:PaymentDueDate>"
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.order.violation" for item in report.diagnostics)


def test_dumps_refuses_a_document_with_an_out_of_order_payment_means() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        '<cac:PayeeFinancialAccount><cbc:ID>ACC1</cbc:ID></cac:PayeeFinancialAccount>'
        "<cbc:PaymentDueDate>2024-01-01</cbc:PaymentDueDate>"
    )
    document = loads(_invoice_with_payment_means(body))

    with pytest.raises(UblWriteError, match="PaymentDueDate"):
        dumps(document)


def test_dumps_writes_a_well_formed_payment_means_without_incident() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cbc:PaymentDueDate>2024-01-01</cbc:PaymentDueDate>"
        '<cac:PayeeFinancialAccount><cbc:ID>ACC1</cbc:ID></cac:PayeeFinancialAccount>'
    )
    document = loads(_invoice_with_payment_means(body))

    out = dumps(document)

    assert b"PaymentMeansCode" in out


# ── cac:PayeeFinancialAccount: ID/Name/CurrencyCode are each 0..1 ──────────


def test_a_financial_account_with_two_currency_codes_is_a_cardinality_violation() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cac:PayeeFinancialAccount>"
        "<cbc:CurrencyCode>USD</cbc:CurrencyCode>"
        "<cbc:CurrencyCode>EUR</cbc:CurrencyCode>"
        "</cac:PayeeFinancialAccount>"
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_financial_account_with_two_names_is_a_cardinality_violation() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cac:PayeeFinancialAccount>"
        "<cbc:Name>Primary</cbc:Name>"
        "<cbc:Name>Secondary</cbc:Name>"
        "</cac:PayeeFinancialAccount>"
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is False
    assert any(item.code == "ubl.cardinality.exceeded" for item in report.diagnostics)


def test_a_financial_account_with_one_of_each_field_validates_cleanly() -> None:
    body = (
        "<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>"
        "<cac:PayeeFinancialAccount>"
        "<cbc:ID>ACC1</cbc:ID>"
        "<cbc:Name>Primary</cbc:Name>"
        "<cbc:CurrencyCode>USD</cbc:CurrencyCode>"
        "</cac:PayeeFinancialAccount>"
    )

    report = validate(loads(_invoice_with_payment_means(body)))

    assert report.is_valid is True
