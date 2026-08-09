"""UBL-MODEL-001 — shared aggregate components as typed composites.

The aggregates here are the ones the contract names: `cac:Item`,
`cac:InvoiceLine`, `cac:TaxSubtotal`, `cac:TaxTotal` and
`cac:LegalMonetaryTotal`. Required components are enforced at construction, so
an invalid structure fails where it is built rather than later where it is
serialized — that is what "diagnosable at edit time" asks for.

Reconciliation is the interesting decision. The contract is explicit that

  "the XSD does not encode cross-field arithmetic reconciliation"

so this module offers it as an explicit **reporting** operation and nothing
more. It does not correct totals, because a library that silently rewrote a
payable amount to match its own arithmetic would be altering a business
document. It does not raise either, because real invoices are legitimately
rounded in ways a naive sum disagrees with, and rejecting them at parse time
would make the library unusable against genuine data. A mismatch is a finding
for a human.

`reconcile_invoice`'s `tolerance` parameter is exactly the "under explicit
rounding/tolerance policies" clause UBL-CALC-001 asks for: a caller in a
regime where totals round to two decimal places passes a tolerance that
absorbs it, rather than the library picking a rounding policy on their
behalf. The default is exact (zero tolerance), so an existing caller's
behavior is unchanged unless they opt in.

Payable-amount reconciliation is a deliberate gap, not an oversight: the
correct formula is `PayableAmount = TaxInclusiveAmount - PrepaidAmount +
PayableRoundingAmount`, and neither cbc:PrepaidAmount nor
cbc:PayableRoundingAmount is modeled anywhere in this package yet. Checking
`PayableAmount == TaxInclusiveAmount` without them would flag every invoice
that legitimately declares a prepayment as a mismatch -- a false positive on
real, correct data, which is worse than not checking at all. This is
recorded as the honest remaining gap rather than an approximate formula that
would be systematically wrong.

UBL-PARSE-001 (FF6-EVENT-000485): every lookup here is namespace-precise via
`find_qname`/`find_all_qname`, not `find`/`find_all`'s own local-name-only
matching -- wave 4 of the ~79 disclosed call sites (wave 1: reference.py;
wave 2: charges.py; wave 3: lines.py). Every field's own namespace was
confirmed directly against the pinned OASIS UBL 2.3 schema
(InvoiceLineType/TaxSubtotalType/TaxTotalType/TaxCategoryType/
MonetaryTotalType, via a live xmlschema introspection) before migrating.
The one exception is `Item.identifiers`/`Item.classification_codes`'s own
`find_all(node, "ID")`/`find_all(node, "CommodityClassification")` lookups:
`ItemType`'s real schema has no direct cbc:ID or cbc:CommodityClassification
child at all (confirmed by the same introspection; item identification is
always wrapped in aggregates like cac:BuyersItemIdentification, and
CommodityClassification is itself a cac: aggregate, not a leaf) -- an
already-disclosed, pre-existing model-field-mapping gap (see
test_obligation_aggregates_cardinality_validation.py and
test_obligation_item_and_price_cardinality_and_order_validation.py's own
module docstrings) this migration does not attempt to resolve. No test
exercises that path via a real document, so it is migrated to the CBC
namespace, matching this codebase's own existing "cbc:ID"/
"cbc:CommodityClassification" documentation of it, preserving exact current
behavior without asserting a new schema-conformance claim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from format_factory.core import Diagnostic, Severity, ValidationReport

from ..errors import UblValidationError
from .document import XmlNode
from .typed import amount_of, code_of, find_all_qname, find_qname, identifier_of, quantity_of
from .values import Amount, Code, Identifier, Quantity

_CBC_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _cbc(node: XmlNode, name: str) -> XmlNode | None:
    return find_qname(node, _CBC_NAMESPACE, name)


def _cbc_all(node: XmlNode, name: str) -> tuple[XmlNode, ...]:
    return find_all_qname(node, _CBC_NAMESPACE, name)


def _cac(node: XmlNode, name: str) -> XmlNode | None:
    return find_qname(node, _CAC_NAMESPACE, name)


def _cac_all(node: XmlNode, name: str) -> tuple[XmlNode, ...]:
    return find_all_qname(node, _CAC_NAMESPACE, name)


def _require(value: object, name: str, owner: str) -> None:
    if value is None:
        raise UblValidationError(
            f"{owner} requires {name}; the UBL aggregate definition makes it "
            "mandatory, and an incomplete structure should fail where it is "
            "built rather than where it is serialized"
        )


@dataclass(frozen=True)
class Item:
    """`cac:Item` — a traded item."""

    name: str
    identifiers: tuple[Identifier, ...] = ()
    classification_codes: tuple[Code, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise UblValidationError("cac:Item requires a non-empty cbc:Name")


@dataclass(frozen=True)
class InvoiceLine:
    """`cac:InvoiceLine` — carries cbc:ID, cbc:InvoicedQuantity,
    cbc:LineExtensionAmount and a cac:Item."""

    id: Identifier
    invoiced_quantity: Quantity
    line_extension_amount: Amount
    item: Item

    def __post_init__(self) -> None:
        _require(self.id, "cbc:ID", "cac:InvoiceLine")
        _require(self.invoiced_quantity, "cbc:InvoicedQuantity", "cac:InvoiceLine")
        _require(self.line_extension_amount, "cbc:LineExtensionAmount", "cac:InvoiceLine")
        _require(self.item, "a cac:Item", "cac:InvoiceLine")


@dataclass(frozen=True)
class TaxSubtotal:
    """`cac:TaxSubtotal` — one tax category's taxable and tax amounts."""

    taxable_amount: Amount
    tax_amount: Amount
    category_code: Code | None = None

    def __post_init__(self) -> None:
        _require(self.taxable_amount, "cbc:TaxableAmount", "cac:TaxSubtotal")
        _require(self.tax_amount, "cbc:TaxAmount", "cac:TaxSubtotal")


@dataclass(frozen=True)
class TaxTotal:
    """`cac:TaxTotal` — cbc:TaxAmount plus nested cac:TaxSubtotal per category."""

    tax_amount: Amount
    subtotals: tuple[TaxSubtotal, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require(self.tax_amount, "cbc:TaxAmount", "cac:TaxTotal")


@dataclass(frozen=True)
class LegalMonetaryTotal:
    """`cac:LegalMonetaryTotal` — document-level monetary totals.

    Line extension and payable are required; the tax-exclusive, tax-inclusive,
    allowance and charge amounts are optional, and absent is not the same as
    zero — a document that omits an allowance total is not asserting it is nil.
    """

    line_extension_amount: Amount
    payable_amount: Amount
    tax_exclusive_amount: Amount | None = None
    tax_inclusive_amount: Amount | None = None
    allowance_total_amount: Amount | None = None
    charge_total_amount: Amount | None = None

    def __post_init__(self) -> None:
        _require(self.line_extension_amount, "cbc:LineExtensionAmount", "cac:LegalMonetaryTotal")
        _require(self.payable_amount, "cbc:PayableAmount", "cac:LegalMonetaryTotal")


# ── Projection from the lossless tree ──────────────────────────────────────


def item_of(node: XmlNode | None) -> Item:
    if node is None:
        raise UblValidationError("cannot project a missing element into a cac:Item")
    name = _cbc(node, "Name")
    if name is None:
        raise UblValidationError("cac:Item has no cbc:Name")
    return Item(
        name=name.text,
        identifiers=tuple(identifier_of(child) for child in _cbc_all(node, "ID")),
        classification_codes=tuple(
            code_of(child) for child in _cbc_all(node, "CommodityClassification")
        ),
    )


def invoice_line_of(node: XmlNode | None) -> InvoiceLine:
    if node is None:
        raise UblValidationError("cannot project a missing element into a cac:InvoiceLine")
    item = _cac(node, "Item")
    if item is None:
        raise UblValidationError("cac:InvoiceLine has no cac:Item")
    return InvoiceLine(
        id=identifier_of(_cbc(node, "ID")),
        invoiced_quantity=quantity_of(_cbc(node, "InvoicedQuantity")),
        line_extension_amount=amount_of(_cbc(node, "LineExtensionAmount")),
        item=item_of(item),
    )


def tax_subtotal_of(node: XmlNode | None) -> TaxSubtotal:
    if node is None:
        raise UblValidationError("cannot project a missing element into a cac:TaxSubtotal")
    category = _cac(node, "TaxCategory")
    category_id = _cbc(category, "ID") if category is not None else None
    return TaxSubtotal(
        taxable_amount=amount_of(_cbc(node, "TaxableAmount")),
        tax_amount=amount_of(_cbc(node, "TaxAmount")),
        category_code=code_of(category_id) if category_id is not None else None,
    )


def tax_total_of(node: XmlNode | None) -> TaxTotal:
    if node is None:
        raise UblValidationError("cannot project a missing element into a cac:TaxTotal")
    return TaxTotal(
        tax_amount=amount_of(_cbc(node, "TaxAmount")),
        subtotals=tuple(tax_subtotal_of(child) for child in _cac_all(node, "TaxSubtotal")),
    )


def _optional_amount(node: XmlNode, name: str) -> Amount | None:
    child = _cbc(node, name)
    return amount_of(child) if child is not None else None


def legal_monetary_total_of(node: XmlNode | None) -> LegalMonetaryTotal:
    if node is None:
        raise UblValidationError(
            "cannot project a missing element into a cac:LegalMonetaryTotal"
        )
    return LegalMonetaryTotal(
        line_extension_amount=amount_of(_cbc(node, "LineExtensionAmount")),
        payable_amount=amount_of(_cbc(node, "PayableAmount")),
        tax_exclusive_amount=_optional_amount(node, "TaxExclusiveAmount"),
        tax_inclusive_amount=_optional_amount(node, "TaxInclusiveAmount"),
        allowance_total_amount=_optional_amount(node, "AllowanceTotalAmount"),
        charge_total_amount=_optional_amount(node, "ChargeTotalAmount"),
    )


# ── Reconciliation: report only ────────────────────────────────────────────


def reconcile_invoice(
    root: XmlNode, *, tolerance: Decimal = Decimal(0)
) -> ValidationReport:
    """Check the cross-field arithmetic the XSD cannot express.

    `tolerance` is an explicit rounding/tolerance policy: a delta whose
    absolute value is within it is not reported. The default of zero
    preserves exact-match behavior for a caller who does not opt in.

    Returns findings. Never mutates the document and never raises: an absent
    aggregate is not an error, only a present-and-inconsistent one is.
    """
    found: list[Diagnostic] = []

    line_nodes = _cac_all(root, "InvoiceLine")
    lines: list[InvoiceLine] = []
    for node in line_nodes:
        try:
            lines.append(invoice_line_of(node))
        except UblValidationError as exc:
            found.append(
                Diagnostic(
                    code="UBL_INVOICE_LINE_INVALID",
                    message=str(exc),
                    severity=Severity.ERROR,
                )
            )

    line_sum: Amount | None = None
    if lines:
        currencies = {line.line_extension_amount.currency_id for line in lines}
        if len(currencies) > 1:
            found.append(
                Diagnostic(
                    code="UBL_LINE_CURRENCY_MISMATCH",
                    message=(
                        "invoice lines use more than one currency "
                        f"({sorted(currencies)}); their extension amounts cannot be "
                        "summed without an exchange rate the document does not carry"
                    ),
                    severity=Severity.ERROR,
                )
            )
        else:
            line_sum = lines[0].line_extension_amount
            for line in lines[1:]:
                line_sum = line_sum + line.line_extension_amount

    monetary_node = _cac(root, "LegalMonetaryTotal")
    if monetary_node is not None and line_sum is not None:
        try:
            monetary = legal_monetary_total_of(monetary_node)
        except UblValidationError as exc:
            found.append(
                Diagnostic(
                    code="UBL_LEGAL_MONETARY_TOTAL_INVALID",
                    message=str(exc),
                    severity=Severity.ERROR,
                )
            )
        else:
            declared = monetary.line_extension_amount
            if declared.currency_id != line_sum.currency_id:
                found.append(
                    Diagnostic(
                        code="UBL_LINE_EXTENSION_CURRENCY_MISMATCH",
                        message=(
                            f"cac:LegalMonetaryTotal declares {declared.currency_id} "
                            f"but the invoice lines are in {line_sum.currency_id}"
                        ),
                        severity=Severity.ERROR,
                    )
                )
            elif abs(declared.value - line_sum.value) > tolerance:
                found.append(
                    Diagnostic(
                        code="UBL_LINE_EXTENSION_TOTAL_MISMATCH",
                        message=(
                            f"cac:LegalMonetaryTotal declares a line extension of "
                            f"{declared.value} {declared.currency_id}, but the "
                            f"{len(lines)} invoice lines sum to {line_sum.value} "
                            f"(tolerance {tolerance})"
                        ),
                        severity=Severity.ERROR,
                    )
                )

    for node in _cac_all(root, "TaxTotal"):
        try:
            total = tax_total_of(node)
        except UblValidationError as exc:
            found.append(
                Diagnostic(
                    code="UBL_TAX_TOTAL_INVALID", message=str(exc), severity=Severity.ERROR
                )
            )
            continue
        if not total.subtotals:
            continue
        currencies = {subtotal.tax_amount.currency_id for subtotal in total.subtotals}
        if len(currencies) > 1 or total.tax_amount.currency_id not in currencies:
            found.append(
                Diagnostic(
                    code="UBL_TAX_CURRENCY_MISMATCH",
                    message=(
                        "cac:TaxTotal and its subtotals do not agree on a single "
                        f"currency: total {total.tax_amount.currency_id}, subtotals "
                        f"{sorted(currencies)}"
                    ),
                    severity=Severity.ERROR,
                )
            )
            continue
        subtotal_sum = total.subtotals[0].tax_amount
        for subtotal in total.subtotals[1:]:
            subtotal_sum = subtotal_sum + subtotal.tax_amount
        if abs(subtotal_sum.value - total.tax_amount.value) > tolerance:
            found.append(
                Diagnostic(
                    code="UBL_TAX_SUBTOTAL_MISMATCH",
                    message=(
                        f"cac:TaxTotal declares {total.tax_amount.value} "
                        f"{total.tax_amount.currency_id} but its "
                        f"{len(total.subtotals)} subtotals sum to {subtotal_sum.value} "
                        f"(tolerance {tolerance})"
                    ),
                    severity=Severity.ERROR,
                )
            )

    _reconcile_allowance_charge_totals(root, monetary_node, tolerance, found)

    return ValidationReport(diagnostics=tuple(found))


def _reconcile_allowance_charge_totals(
    root: XmlNode,
    monetary_node: XmlNode | None,
    tolerance: Decimal,
    found: list[Diagnostic],
) -> None:
    """Sum document-level cac:AllowanceCharge amounts by indicator and
    compare against cac:LegalMonetaryTotal's declared allowance/charge
    totals, when both the summed and the declared side exist.

    Local import: charges.py imports `_require` from this module, so a
    module-level import here would be circular.
    """
    if monetary_node is None:
        return
    from .charges import allowance_charge_of

    allowance_charge_nodes = _cac_all(root, "AllowanceCharge")
    if not allowance_charge_nodes:
        return

    try:
        monetary = legal_monetary_total_of(monetary_node)
    except UblValidationError:
        return  # already reported as UBL_LEGAL_MONETARY_TOTAL_INVALID above

    allowances: list[Amount] = []
    charges: list[Amount] = []
    for node in allowance_charge_nodes:
        try:
            entry = allowance_charge_of(node)
        except UblValidationError as exc:
            found.append(
                Diagnostic(
                    code="UBL_ALLOWANCE_CHARGE_INVALID",
                    message=str(exc),
                    severity=Severity.ERROR,
                )
            )
            continue
        (charges if entry.is_charge else allowances).append(entry.amount)

    def _reconcile_one(
        entries: list[Amount], declared: Amount | None, label: str, base_code: str
    ) -> None:
        if declared is None or not entries:
            return
        total = entries[0]
        for entry in entries[1:]:
            total = total + entry
        if declared.currency_id != total.currency_id:
            found.append(
                Diagnostic(
                    code=f"{base_code}_CURRENCY_MISMATCH",
                    message=(
                        f"cac:LegalMonetaryTotal declares {label} in "
                        f"{declared.currency_id} but the cac:AllowanceCharge "
                        f"entries are in {total.currency_id}"
                    ),
                    severity=Severity.ERROR,
                )
            )
            return
        if abs(declared.value - total.value) > tolerance:
            found.append(
                Diagnostic(
                    code=f"{base_code}_MISMATCH",
                    message=(
                        f"cac:LegalMonetaryTotal declares {label} of "
                        f"{declared.value} {declared.currency_id}, but the "
                        f"document-level cac:AllowanceCharge entries sum to "
                        f"{total.value} (tolerance {tolerance})"
                    ),
                    severity=Severity.ERROR,
                )
            )

    _reconcile_one(
        allowances,
        monetary.allowance_total_amount,
        "an allowance total",
        "UBL_ALLOWANCE_TOTAL",
    )
    _reconcile_one(
        charges,
        monetary.charge_total_amount,
        "a charge total",
        "UBL_CHARGE_TOTAL",
    )


__all__ = [
    "InvoiceLine",
    "Item",
    "LegalMonetaryTotal",
    "TaxSubtotal",
    "TaxTotal",
    "invoice_line_of",
    "item_of",
    "legal_monetary_total_of",
    "reconcile_invoice",
    "tax_subtotal_of",
    "tax_total_of",
]
