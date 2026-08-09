"""cac:AllowanceCharge, cac:Price and cac:PaymentMeans.

The remaining aggregates the contract names:

  "cac:AllowanceCharge is an aggregate component type with a charge indicator,
   reason codes, and amount elements applied at document or line level"
  "cac:Price is an aggregate component type carrying cbc:PriceAmount and
   quantity-basis elements for unit pricing"
  "cac:PaymentMeans is an aggregate component type carrying payment means codes,
   due dates, and payee financial account elements"

The charge indicator deserves its own note: a charge adds and an allowance
subtracts, so misreading that boolean inverts the sign of a line on the invoice.
Both spellings XSD permits for `xsd:boolean` are accepted and anything else is
refused rather than guessed.

UBL-PARSE-001 (FF6-EVENT-000483): every lookup here is namespace-precise via
`find_qname`, not `find`'s own local-name-only matching -- wave 2 of the ~84
disclosed `find()`/`find_all()` call sites (wave 1: reference.py,
FF6-EVENT-000482). Each field's own namespace was confirmed directly against
the pinned OASIS UBL 2.3 schema (AllowanceChargeType/PriceType/
PaymentMeansType/FinancialAccountType, via a live xmlschema introspection)
before migrating, not assumed from convention: every leaf field used here is
CommonBasicComponents, EXCEPT `PayeeFinancialAccount`
(CommonAggregateComponents -- confirmed a genuine exception, not an oversight,
since it is itself an aggregate, not a simple value).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import UblValidationError
from .aggregates import _require
from .document import XmlNode
from .temporal import UblDate
from .typed import amount_of, code_of, find_qname, identifier_of, local_name, quantity_of
from .values import Amount, Code, Identifier, Quantity

#: xsd:boolean has exactly four lexical forms. "yes"/"no" are not among them.
_TRUE = frozenset({"true", "1"})
_FALSE = frozenset({"false", "0"})

_CBC_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _cbc(node: XmlNode, name: str) -> XmlNode | None:
    return find_qname(node, _CBC_NAMESPACE, name)


def _cac(node: XmlNode, name: str) -> XmlNode | None:
    return find_qname(node, _CAC_NAMESPACE, name)


def _boolean(node: XmlNode | None, owner: str) -> bool:
    if node is None:
        raise UblValidationError(f"{owner} requires a cbc:ChargeIndicator")
    text = node.text.strip()
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    raise UblValidationError(
        f"{owner} has a cbc:ChargeIndicator of {node.text!r}; xsd:boolean permits "
        "only 'true', 'false', '1' and '0'. Guessing would invert the sign of a "
        "line on the invoice."
    )


@dataclass(frozen=True)
class AllowanceCharge:
    """A document- or line-level allowance (subtracts) or charge (adds)."""

    charge_indicator: bool
    amount: Amount
    reason_code: Code | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.charge_indicator, bool):
            raise UblValidationError(
                "cac:AllowanceCharge requires a boolean cbc:ChargeIndicator"
            )
        _require(self.amount, "cbc:Amount", "cac:AllowanceCharge")

    @property
    def is_charge(self) -> bool:
        return self.charge_indicator

    @property
    def is_allowance(self) -> bool:
        return not self.charge_indicator


@dataclass(frozen=True)
class Price:
    """Unit pricing. The quantity basis is optional; defaulting it to 1 would
    assert a basis the document never gave."""

    price_amount: Amount
    base_quantity: Quantity | None = None

    def __post_init__(self) -> None:
        _require(self.price_amount, "cbc:PriceAmount", "cac:Price")


@dataclass(frozen=True)
class FinancialAccount:
    """`cac:PayeeFinancialAccount` / `cac:PayerFinancialAccount` -- a bank
    account referenced by a payment means (`FinancialAccountType`,
    UBL-CommonAggregateComponents-2.3.xsd). `FinancialInstitutionBranch` and
    `Country`, the type's two nested aggregates, are not modeled here --
    unlike the leaf fields below, they are themselves full aggregates the
    contract does not separately name, so preserving them generically
    (rather than inventing a typed model this obligation never asked for)
    is the honest scope."""

    id: Identifier | None = None
    name: str | None = None
    currency_code: Code | None = None


@dataclass(frozen=True)
class PaymentMeans:
    """How payment is to be made, and by when."""

    payment_means_code: Code
    payment_due_date: UblDate | None = None
    payment_id: Code | None = None
    payee_financial_account: FinancialAccount | None = None

    def __post_init__(self) -> None:
        _require(self.payment_means_code, "cbc:PaymentMeansCode", "cac:PaymentMeans")


def allowance_charge_of(node: XmlNode | None) -> AllowanceCharge:
    if node is None:
        raise UblValidationError(
            "cannot project a missing element into a cac:AllowanceCharge"
        )
    reason_code = _cbc(node, "AllowanceChargeReasonCode")
    reason = _cbc(node, "AllowanceChargeReason")
    return AllowanceCharge(
        charge_indicator=_boolean(_cbc(node, "ChargeIndicator"), "cac:AllowanceCharge"),
        amount=amount_of(_cbc(node, "Amount")),
        reason_code=code_of(reason_code) if reason_code is not None else None,
        reason=reason.text if reason is not None else None,
    )


def price_of(node: XmlNode | None) -> Price:
    if node is None:
        raise UblValidationError("cannot project a missing element into a cac:Price")
    basis = _cbc(node, "BaseQuantity")
    return Price(
        price_amount=amount_of(_cbc(node, "PriceAmount")),
        base_quantity=quantity_of(basis) if basis is not None else None,
    )


def financial_account_of(node: XmlNode | None) -> FinancialAccount | None:
    """Absent per its own optional cardinality (`minOccurs="0"`), not an error."""
    if node is None:
        return None
    identifier = _cbc(node, "ID")
    name = _cbc(node, "Name")
    currency = _cbc(node, "CurrencyCode")
    return FinancialAccount(
        id=identifier_of(identifier) if identifier is not None else None,
        name=name.text.strip() if name is not None else None,
        currency_code=code_of(currency) if currency is not None else None,
    )


def payment_means_of(node: XmlNode | None) -> PaymentMeans:
    if node is None:
        raise UblValidationError(
            "cannot project a missing element into a cac:PaymentMeans"
        )
    due = _cbc(node, "PaymentDueDate")
    identifier = _cbc(node, "PaymentID")
    code = _cbc(node, "PaymentMeansCode")
    if code is None:
        raise UblValidationError(
            f"<{local_name(node.qname)}> has no cbc:PaymentMeansCode"
        )
    return PaymentMeans(
        payment_means_code=code_of(code),
        payment_due_date=UblDate(due.text.strip()) if due is not None else None,
        payment_id=code_of(identifier) if identifier is not None else None,
        payee_financial_account=financial_account_of(_cac(node, "PayeeFinancialAccount")),
    )


__all__ = [
    "AllowanceCharge",
    "FinancialAccount",
    "PaymentMeans",
    "Price",
    "allowance_charge_of",
    "financial_account_of",
    "payment_means_of",
    "price_of",
]
