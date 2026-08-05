"""UBL-VALUES-001 — business value types with supplementary attributes.

The rule this module exists to enforce is absolute:

  "Represent monetary amounts and quantities with decimal arithmetic and retain
   currencyID, unitCode, and scheme attributes through edits, with explicit
   rounding policies for any calculation - binary floating point is never
   acceptable for money."

Three design decisions follow from it, and each is a refusal rather than a
convenience:

* **Floats are rejected at construction.** Accepting one and converting would
  bake in the representation error the rule forbids — `0.1` is not `0.1` in
  binary, and by the time it reaches an invoice total the error is unattributable.
* **Arithmetic never rounds.** Multiplication keeps full precision so the caller
  chooses when and how to round. `HALF_UP` and `HALF_EVEN` disagree on 1.005,
  and a library that picked one silently would be picking a tax outcome.
* **Values are immutable.** The obligation says attributes must survive *edits*;
  an edit therefore produces a new value carrying them rather than mutating one
  in place where a `currencyID` can be dropped.
"""

from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from decimal import ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP
from enum import Enum
from typing import Union

from ..errors import UblValidationError

#: ISO 4217 alphabetic codes are exactly three uppercase letters. This checks
#: the shape only -- asserting a code is *assigned* would need a currency
#: register this library does not ship, and claiming it without one would be
#: the kind of unfounded validation that is worse than none.
_ISO_4217 = re.compile(r"^[A-Z]{3}$")

#: Anything that can become an exact Decimal. `float` is deliberately absent.
DecimalLike = Union[Decimal, int, str]


class Rounding(Enum):
    """Named rounding policies, so a calculation states which one it used."""

    HALF_UP = ROUND_HALF_UP
    HALF_EVEN = ROUND_HALF_EVEN
    UP = ROUND_UP
    DOWN = ROUND_DOWN
    CEILING = ROUND_CEILING
    FLOOR = ROUND_FLOOR


def _to_decimal(value: DecimalLike, *, label: str) -> Decimal:
    if isinstance(value, float):
        raise UblValidationError(
            f"{label} was given a float ({value!r}); binary floating point is "
            "never acceptable for UBL monetary or quantity values. Pass a "
            "Decimal, an int, or a string such as '12.34'."
        )
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, str)):
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise UblValidationError(f"{label} is not a valid decimal: {value!r}") from exc
    raise UblValidationError(
        f"{label} must be a Decimal, int or string, got {type(value).__name__}"
    )


def _normalized_string(raw: str, *, label: str) -> str:
    """XSD `normalizedString`: each tab, line feed and carriage return becomes a
    single space.

    It does **not** collapse runs of spaces and does not strip — that is
    `xsd:token`, a different type. Conflating them would silently alter data a
    document asserted.
    """
    if not isinstance(raw, str):
        raise UblValidationError(f"{label} must be a string, got {type(raw).__name__}")
    return raw.replace("\t", " ").replace("\r", " ").replace("\n", " ")


@dataclass(frozen=True)
class Amount:
    """A monetary amount: an exact decimal plus its required ISO 4217 currency."""

    value: Decimal
    currency_id: str

    def __init__(self, value: DecimalLike, currency_id: str) -> None:
        amount = _to_decimal(value, label="Amount")
        if not isinstance(currency_id, str) or not _ISO_4217.match(currency_id):
            raise UblValidationError(
                f"Amount requires a currencyID of three uppercase letters "
                f"identifying an ISO 4217 currency, got {currency_id!r}"
            )
        object.__setattr__(self, "value", amount)
        object.__setattr__(self, "currency_id", currency_id)

    def _require_same_currency(self, other: "Amount", operation: str) -> None:
        if self.currency_id != other.currency_id:
            raise UblValidationError(
                f"cannot {operation} {self.currency_id} and {other.currency_id} "
                "amounts: there is no exchange rate in the document, and "
                "returning a number anyway would produce a wrong total that "
                "looks right"
            )

    def __add__(self, other: "Amount") -> "Amount":
        self._require_same_currency(other, "add")
        return Amount(self.value + other.value, self.currency_id)

    def __sub__(self, other: "Amount") -> "Amount":
        self._require_same_currency(other, "subtract")
        return Amount(self.value - other.value, self.currency_id)

    def __mul__(self, factor: "Quantity | DecimalLike") -> "Amount":
        """Multiply by a quantity or a plain decimal. Precision is kept in full;
        rounding is the caller's explicit step."""
        multiplier = factor.value if isinstance(factor, Quantity) else _to_decimal(
            factor, label="Amount multiplier"
        )
        return Amount(self.value * multiplier, self.currency_id)

    def round_to(self, places: int, rounding: Rounding) -> "Amount":
        """Round to `places` decimal places under a named policy.

        The policy is required. HALF_UP and HALF_EVEN disagree on 1.005, so a
        default would be this library quietly choosing a business outcome.
        """
        if not isinstance(rounding, Rounding):
            raise UblValidationError(
                "rounding must be an explicit Rounding policy; there is no default"
            )
        quantum = Decimal(1).scaleb(-places)
        return Amount(self.value.quantize(quantum, rounding=rounding.value), self.currency_id)


@dataclass(frozen=True)
class Quantity:
    """A quantity: an exact decimal plus an optional unit of measure.

    `unitCode` is optional where `currencyID` is required; the asymmetry is the
    specification's, not an oversight here.
    """

    value: Decimal
    unit_code: str | None = None

    def __init__(self, value: DecimalLike, unit_code: str | None = None) -> None:
        object.__setattr__(self, "value", _to_decimal(value, label="Quantity"))
        if unit_code is not None and not str(unit_code).strip():
            raise UblValidationError("Quantity unitCode, when present, must not be blank")
        object.__setattr__(self, "unit_code", unit_code)


@dataclass(frozen=True)
class Code:
    """A code value with optional list identification.

    The base UBL XSD does not enumerate business code values, so this preserves
    what the document said rather than validating against a list it does not have.
    """

    value: str
    list_id: str | None = None
    list_agency_id: str | None = None
    list_version_id: str | None = None

    def __init__(
        self,
        value: str,
        list_id: str | None = None,
        list_agency_id: str | None = None,
        list_version_id: str | None = None,
    ) -> None:
        normalized = _normalized_string(value, label="Code")
        if not normalized:
            raise UblValidationError("Code value must not be empty")
        object.__setattr__(self, "value", normalized)
        object.__setattr__(self, "list_id", list_id)
        object.__setattr__(self, "list_agency_id", list_agency_id)
        object.__setattr__(self, "list_version_id", list_version_id)


@dataclass(frozen=True)
class Identifier:
    """`cbc:ID` — an identifier with optional scheme attributes."""

    value: str
    scheme_id: str | None = None
    scheme_agency_id: str | None = None

    def __init__(
        self,
        value: str,
        scheme_id: str | None = None,
        scheme_agency_id: str | None = None,
    ) -> None:
        normalized = _normalized_string(value, label="Identifier")
        if not normalized.strip():
            raise UblValidationError("Identifier value must not be blank")
        object.__setattr__(self, "value", normalized)
        object.__setattr__(self, "scheme_id", scheme_id)
        object.__setattr__(self, "scheme_agency_id", scheme_agency_id)


@dataclass(frozen=True)
class BinaryObject:
    """An embedded document. `mimeCode` is required by the UBL UDT.

    An attachment whose type is unknown cannot be safely handled downstream, so
    the requirement is enforced rather than defaulted.
    """

    data: bytes
    mime_code: str
    filename: str | None = None

    def __init__(self, data: bytes, mime_code: str, filename: str | None = None) -> None:
        if not isinstance(data, (bytes, bytearray)):
            raise UblValidationError(
                f"BinaryObject data must be bytes, got {type(data).__name__}"
            )
        if not isinstance(mime_code, str) or not mime_code.strip():
            raise UblValidationError(
                "BinaryObject requires a mimeCode; it is mandatory in the UBL "
                "unqualified data type, because a consumer cannot safely handle "
                "an attachment of unknown type"
            )
        object.__setattr__(self, "data", bytes(data))
        object.__setattr__(self, "mime_code", mime_code)
        object.__setattr__(self, "filename", filename)

    def to_base64(self) -> str:
        return base64.b64encode(self.data).decode("ascii")

    @classmethod
    def from_base64(
        cls, encoded: str, mime_code: str, filename: str | None = None
    ) -> "BinaryObject":
        try:
            data = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise UblValidationError(
                f"BinaryObject content is not valid base64: {exc}"
            ) from exc
        return cls(data, mime_code, filename)


__all__ = [
    "Amount",
    "BinaryObject",
    "Code",
    "DecimalLike",
    "Identifier",
    "Quantity",
    "Rounding",
]
