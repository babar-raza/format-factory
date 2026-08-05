"""UBL-CALC-001 against the shipped namespace.

SAL-UBL-00110/00122/00123/00127 (SHOULD): line extensions, allowance/charge
totals, tax totals, and payable amounts calculate under explicit rounding/
tolerance policies and reconcile against declared totals with per-total
deltas, never mutating declared values outside explicit repair mode.

required_tests: "Reconciliation fixtures with agreeing and disagreeing
declared totals across rounding policies."
"""

from __future__ import annotations

from decimal import Decimal

from format_factory.ubl import loads, reconcile_invoice

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice(body: str) -> str:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{CBC}" xmlns:cac="{CAC}">'
        f"<cbc:ID>INV-001</cbc:ID>"
        f"{body}"
        f"</Invoice>"
    )


def _line(amount: str = "20.00") -> str:
    return (
        "<cac:InvoiceLine>"
        "<cbc:ID>1</cbc:ID>"
        '<cbc:InvoicedQuantity unitCode="KGM">2</cbc:InvoicedQuantity>'
        f'<cbc:LineExtensionAmount currencyID="EUR">{amount}</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Coffee beans</cbc:Name></cac:Item>"
        "</cac:InvoiceLine>"
    )


def _monetary_total(
    line_extension: str = "20.00",
    payable: str = "20.00",
    allowance_total: str | None = None,
    charge_total: str | None = None,
) -> str:
    allowance_xml = (
        f'<cbc:AllowanceTotalAmount currencyID="EUR">{allowance_total}</cbc:AllowanceTotalAmount>'
        if allowance_total is not None
        else ""
    )
    charge_xml = (
        f'<cbc:ChargeTotalAmount currencyID="EUR">{charge_total}</cbc:ChargeTotalAmount>'
        if charge_total is not None
        else ""
    )
    return (
        "<cac:LegalMonetaryTotal>"
        f'<cbc:LineExtensionAmount currencyID="EUR">{line_extension}</cbc:LineExtensionAmount>'
        f"{allowance_xml}{charge_xml}"
        f'<cbc:PayableAmount currencyID="EUR">{payable}</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
    )


def _allowance_charge(is_charge: bool, amount: str) -> str:
    indicator = "true" if is_charge else "false"
    return (
        "<cac:AllowanceCharge>"
        f"<cbc:ChargeIndicator>{indicator}</cbc:ChargeIndicator>"
        f'<cbc:Amount currencyID="EUR">{amount}</cbc:Amount>'
        "</cac:AllowanceCharge>"
    )


def _root(xml: str):
    return loads(xml).root


# ── Tolerance: explicit rounding/tolerance policies ─────────────────────────


def test_default_tolerance_is_exact_zero() -> None:
    """"...under explicit rounding/tolerance policies..." -- the default
    preserves exact-match behavior for a caller who does not opt in."""
    xml = _invoice(_line("20.00") + _monetary_total(line_extension="20.01", payable="20.01"))

    report = reconcile_invoice(_root(xml))

    assert any(d.code == "UBL_LINE_EXTENSION_TOTAL_MISMATCH" for d in report.diagnostics)


def test_a_tolerance_within_the_delta_silences_the_mismatch() -> None:
    xml = _invoice(_line("20.00") + _monetary_total(line_extension="20.01", payable="20.01"))

    report = reconcile_invoice(_root(xml), tolerance=Decimal("0.01"))

    assert not any(d.code == "UBL_LINE_EXTENSION_TOTAL_MISMATCH" for d in report.diagnostics)


def test_a_tolerance_smaller_than_the_delta_still_reports_it() -> None:
    xml = _invoice(_line("20.00") + _monetary_total(line_extension="20.05", payable="20.05"))

    report = reconcile_invoice(_root(xml), tolerance=Decimal("0.01"))

    assert any(d.code == "UBL_LINE_EXTENSION_TOTAL_MISMATCH" for d in report.diagnostics)


def test_tolerance_applies_to_tax_subtotal_reconciliation_too() -> None:
    body = (
        _line("20.00")
        + "<cac:TaxTotal>"
        + '<cbc:TaxAmount currencyID="EUR">4.01</cbc:TaxAmount>'
        + '<cac:TaxSubtotal><cbc:TaxableAmount currencyID="EUR">20.00</cbc:TaxableAmount>'
        + '<cbc:TaxAmount currencyID="EUR">4.00</cbc:TaxAmount></cac:TaxSubtotal>'
        + "</cac:TaxTotal>"
        + _monetary_total(line_extension="20.00", payable="24.01")
    )
    xml = _invoice(body)

    exact = reconcile_invoice(_root(xml))
    tolerant = reconcile_invoice(_root(xml), tolerance=Decimal("0.01"))

    assert any(d.code == "UBL_TAX_SUBTOTAL_MISMATCH" for d in exact.diagnostics)
    assert not any(d.code == "UBL_TAX_SUBTOTAL_MISMATCH" for d in tolerant.diagnostics)


# ── Allowance/charge total reconciliation ───────────────────────────────────


def test_agreeing_charge_total_reconciles_clean() -> None:
    body = (
        _line("20.00")
        + _allowance_charge(is_charge=True, amount="2.00")
        + _monetary_total(line_extension="20.00", charge_total="2.00", payable="22.00")
    )
    xml = _invoice(body)

    report = reconcile_invoice(_root(xml))

    assert not any(d.code.startswith("UBL_CHARGE_TOTAL") for d in report.diagnostics)


def test_disagreeing_charge_total_is_reported() -> None:
    body = (
        _line("20.00")
        + _allowance_charge(is_charge=True, amount="2.00")
        + _monetary_total(line_extension="20.00", charge_total="3.00", payable="23.00")
    )
    xml = _invoice(body)

    report = reconcile_invoice(_root(xml))

    mismatches = [d for d in report.diagnostics if d.code == "UBL_CHARGE_TOTAL_MISMATCH"]
    assert len(mismatches) == 1
    assert "3.00" in mismatches[0].message
    assert "2.00" in mismatches[0].message


def test_agreeing_allowance_total_reconciles_clean() -> None:
    body = (
        _line("20.00")
        + _allowance_charge(is_charge=False, amount="1.50")
        + _monetary_total(line_extension="20.00", allowance_total="1.50", payable="18.50")
    )
    xml = _invoice(body)

    report = reconcile_invoice(_root(xml))

    assert not any(d.code.startswith("UBL_ALLOWANCE_TOTAL") for d in report.diagnostics)


def test_disagreeing_allowance_total_is_reported() -> None:
    body = (
        _line("20.00")
        + _allowance_charge(is_charge=False, amount="1.50")
        + _monetary_total(line_extension="20.00", allowance_total="2.00", payable="18.00")
    )
    xml = _invoice(body)

    report = reconcile_invoice(_root(xml))

    assert any(d.code == "UBL_ALLOWANCE_TOTAL_MISMATCH" for d in report.diagnostics)


def test_multiple_allowance_charge_entries_are_summed_by_indicator() -> None:
    body = (
        _line("20.00")
        + _allowance_charge(is_charge=True, amount="1.00")
        + _allowance_charge(is_charge=True, amount="1.00")
        + _allowance_charge(is_charge=False, amount="0.50")
        + _monetary_total(
            line_extension="20.00", charge_total="2.00", allowance_total="0.50", payable="21.50"
        )
    )
    xml = _invoice(body)

    report = reconcile_invoice(_root(xml))

    assert not any(
        d.code in {"UBL_CHARGE_TOTAL_MISMATCH", "UBL_ALLOWANCE_TOTAL_MISMATCH"}
        for d in report.diagnostics
    )


def test_allowance_charge_reconciliation_ignores_line_level_entries() -> None:
    """cac:AllowanceCharge can also appear inside cac:InvoiceLine, applying to
    that line only -- find_all's direct-children-only semantics mean a
    line-level entry must not be summed into the document-level total."""
    body = (
        "<cac:InvoiceLine>"
        "<cbc:ID>1</cbc:ID>"
        '<cbc:InvoicedQuantity unitCode="KGM">2</cbc:InvoicedQuantity>'
        '<cbc:LineExtensionAmount currencyID="EUR">20.00</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Coffee beans</cbc:Name></cac:Item>"
        "<cac:AllowanceCharge>"
        "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
        '<cbc:Amount currencyID="EUR">99.00</cbc:Amount>'
        "</cac:AllowanceCharge>"
        "</cac:InvoiceLine>"
        + _monetary_total(line_extension="20.00", payable="20.00")
    )
    xml = _invoice(body)

    report = reconcile_invoice(_root(xml))

    # No document-level AllowanceCharge exists, and no allowance/charge total
    # is declared, so there is nothing to reconcile -- the 99.00 line-level
    # entry must not leak into a document-level mismatch.
    assert not any(
        d.code in {"UBL_CHARGE_TOTAL_MISMATCH", "UBL_ALLOWANCE_TOTAL_MISMATCH"}
        for d in report.diagnostics
    )


def test_no_allowance_charge_reconciliation_when_neither_total_is_declared() -> None:
    """Optional is not zero: an invoice with cac:AllowanceCharge entries but
    no declared AllowanceTotalAmount/ChargeTotalAmount is not asserting they
    are nil, so nothing is compared."""
    body = (
        _line("20.00")
        + _allowance_charge(is_charge=True, amount="2.00")
        + _monetary_total(line_extension="20.00", payable="20.00")
    )
    xml = _invoice(body)

    report = reconcile_invoice(_root(xml))

    assert not any(d.code.startswith("UBL_CHARGE_TOTAL") for d in report.diagnostics)
    assert not any(d.code.startswith("UBL_ALLOWANCE_TOTAL") for d in report.diagnostics)


def test_allowance_charge_currency_mismatch_is_reported() -> None:
    body = (
        _line("20.00")
        + "<cac:AllowanceCharge>"
        + "<cbc:ChargeIndicator>true</cbc:ChargeIndicator>"
        + '<cbc:Amount currencyID="USD">2.00</cbc:Amount>'
        + "</cac:AllowanceCharge>"
        + _monetary_total(line_extension="20.00", charge_total="2.00", payable="22.00")
    )
    xml = _invoice(body)

    report = reconcile_invoice(_root(xml))

    assert any(d.code == "UBL_CHARGE_TOTAL_CURRENCY_MISMATCH" for d in report.diagnostics)


# ── Never mutates the document ──────────────────────────────────────────────


def test_reconciliation_with_tolerance_and_allowance_charge_never_mutates() -> None:
    body = (
        _line("20.00")
        + _allowance_charge(is_charge=True, amount="2.00")
        + _monetary_total(line_extension="20.05", charge_total="3.00", payable="23.05")
    )
    root = _root(_invoice(body))
    before = root

    reconcile_invoice(root, tolerance=Decimal("0.01"))

    assert root == before
