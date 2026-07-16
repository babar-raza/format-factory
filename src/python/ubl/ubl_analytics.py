"""UBL document analytics — statistics derived from parsed UBL documents.

Each function operates on a freshly re-parsed model dict obtained via
load_ubl(source); no pre-built domain model object is required. No I/O
beyond the load_ubl() call itself.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Union

from .ubl_codec import load_ubl

SourceType = Union[str, Path, bytes]

spec_qname = "ubl:invoice"
spec_fact_ref = "FACT-UBL-002"

# Absolute tolerance for the arithmetic sanity checks in
# check_tax_consistency() -- real-world documents carry 2-decimal currency
# amounts as decimal strings; this absorbs ordinary rounding without masking
# a genuine mismatch (which is typically off by whole units or more).
_TAX_CHECK_TOLERANCE = 0.02


def ubl_total_line_count(source: SourceType) -> int:
    """Return the count of line items in the document.

    Works for both Invoice (cac:InvoiceLine) and Order (cac:OrderLine)
    document types, since load_ubl() normalizes both to a "lines" list.

    Spec: Invoice/Order mandatory line items (FACT-UBL-002)
    """
    model = load_ubl(source)
    return len(model.get("lines", []))


def ubl_supplier_name(source: SourceType) -> str | None:
    """Return the supplier party name if present, else None.

    Only Invoice documents carry a "supplier" key (cac:AccountingSupplierParty).
    Order documents and Invoices missing the supplier element return None.

    Spec: cac:AccountingSupplierParty / cac:PartyName / cbc:Name (FACT-UBL-002)
    """
    model = load_ubl(source)
    supplier = model.get("supplier")
    if not supplier:
        return None
    name = supplier.get("name", "")
    return name if name else None


def ubl_document_type_summary(source: SourceType) -> dict[str, Any]:
    """Return a summary dict describing the document's type and line count.

    Return shape: {"document_type": str, "line_count": int}.

    Spec: UBL document type is determined by the root element's namespace
    (Invoice-2, Order-2, ...) (FACT-UBL-001)
    """
    model = load_ubl(source)
    return {
        "document_type": model.get("document_type", ""),
        "line_count": len(model.get("lines", [])),
    }


def _to_float(value: Any) -> float | None:
    """Best-effort float coercion; returns None instead of raising."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def check_tax_consistency(model: dict[str, Any]) -> list[str]:
    """Non-authoritative arithmetic sanity check over a UBL model's tax and
    monetary totals. Returns a list of human-readable inconsistency
    descriptions (empty list = no inconsistency found).

    TC-S6P4-PROD-003 (select-6 Phase 4, closes D3): the ubl codec transcribes
    tax/monetary values, it does not compute or validate them (see
    ubl_codec.py's module docstring). This function is the closest thing to
    a "does this document add up" check the codec offers, and it is
    intentionally narrow:

    - Each cac:TaxSubtotal's TaxAmount is compared against
      TaxableAmount * Percent / 100, when all three fields are present.
    - The sum of subtotal TaxAmounts is compared against the TaxTotal's own
      TaxAmount, when subtotals exist.
    - PayableAmount is compared against TaxInclusiveAmount, ONLY as an
      informational note (not a mismatch) when they differ -- this model
      does not capture prepaid amounts, allowances, or charges, so a real
      document may legitimately differ here for reasons this function
      cannot see. It is reported as `INFO:` so callers can tell it apart
      from a genuine arithmetic error.

    This is a sanity check, not a validator: it proves nothing about
    schema or Peppol BIS 3.0 compliance (see
    reports/spec-coverage/ubl-deferred.json for that explicit scope
    boundary), and a clean result here is not proof of a "valid" invoice.

    TC-S6P4-FINAL-001f (select-6 Phase 4 final re-audit): moved here from
    ubl_codec.py, which had grown past the 800 LOC cap
    (validate_source_architecture GOV_BLOCK); re-exported from
    ubl_codec.check_tax_consistency for API compatibility.
    """
    issues: list[str] = []
    tax_total = model.get("tax_total") or {}
    monetary_total = model.get("monetary_total") or {}

    subtotal_sum = 0.0
    have_subtotal_sum = False
    for i, subtotal in enumerate(tax_total.get("tax_subtotals", [])):
        taxable = _to_float(subtotal.get("taxable_amount"))
        percent = _to_float(subtotal.get("tax_percent"))
        tax_amount = _to_float(subtotal.get("tax_amount"))
        if taxable is not None and percent is not None and tax_amount is not None:
            expected = round(taxable * percent / 100.0, 2)
            if abs(expected - tax_amount) > _TAX_CHECK_TOLERANCE:
                issues.append(
                    f"TaxSubtotal[{i}]: TaxAmount={tax_amount} does not match "
                    f"TaxableAmount({taxable}) * Percent({percent})/100 = {expected}"
                )
        if tax_amount is not None:
            subtotal_sum += tax_amount
            have_subtotal_sum = True

    total_tax_amount = _to_float(tax_total.get("tax_amount"))
    if have_subtotal_sum and total_tax_amount is not None:
        if abs(subtotal_sum - total_tax_amount) > _TAX_CHECK_TOLERANCE:
            issues.append(
                f"TaxTotal.TaxAmount={total_tax_amount} does not match the sum of "
                f"TaxSubtotal amounts ({round(subtotal_sum, 2)})"
            )

    payable = _to_float(monetary_total.get("payable_amount"))
    tax_inclusive = _to_float(monetary_total.get("tax_inclusive_amount"))
    if payable is not None and tax_inclusive is not None:
        if abs(payable - tax_inclusive) > _TAX_CHECK_TOLERANCE:
            issues.append(
                f"INFO: PayableAmount={payable} differs from TaxInclusiveAmount="
                f"{tax_inclusive} (this model does not track prepaid amounts, "
                f"allowances, or charges, so this may be legitimate)"
            )

    return issues
