"""UBL-VALUES-001 — business value types with supplementary attributes.

The binding sentence in this capability is absolute:

  "Represent monetary amounts and quantities with decimal arithmetic and retain
   currencyID, unitCode, and scheme attributes through edits, with explicit
   rounding policies for any calculation - binary floating point is never
   acceptable for money."

Before this module existed, `Decimal` did not appear anywhere in the UBL
package, and none of the typed components its obligations name existed. The
package could carry an invoice through XML and back, but it could not add two
amounts without a caller reaching for `float`.

Other rules quoted where they bind:

  "Amount-typed basic components require a currencyID attribute identifying the
   ISO 4217 currency of the value"
  "Quantity-typed basic components carry an optional unitCode attribute
   identifying the unit of measure"
  "UBL CodeType values are normalized strings with optional listID and related
   list-identification attributes"
  "cbc:ID is a basic component element of UDT IdentifierType carrying optional
   schemeID and schemeAgencyID attributes"
  "cbc:EmbeddedDocumentBinaryObject restricts UDT BinaryObjectType, whose value
   is base64Binary and whose mimeCode attribute is required in the UBL UDT."
"""

from __future__ import annotations

import base64
import hashlib
from decimal import Decimal

import pytest

from format_factory.ubl import (
    Amount,
    BinaryObject,
    Code,
    Identifier,
    Quantity,
    Rounding,
    UblValidationError,
)


# ── Money is decimal, never binary floating point ──────────────────────────


def test_an_amount_holds_an_exact_decimal() -> None:
    amount = Amount("12.34", "EUR")

    assert amount.value == Decimal("12.34")
    assert amount.currency_id == "EUR"


def test_constructing_an_amount_from_a_float_is_refused() -> None:
    """"binary floating point is never acceptable for money." Accepting a float
    and converting it would silently bake in the representation error the rule
    exists to prevent -- 0.1 is not 0.1 in binary."""
    with pytest.raises(UblValidationError) as raised:
        Amount(12.34, "EUR")  # type: ignore[arg-type]

    assert "float" in str(raised.value).lower()


def test_decimal_addition_is_exact_where_float_would_not_be() -> None:
    """The canonical demonstration: 0.1 + 0.2 == 0.3 exactly in decimal, and
    does not in binary floating point."""
    total = Amount("0.10", "EUR") + Amount("0.20", "EUR")

    assert total.value == Decimal("0.30")
    assert float(0.1) + float(0.2) != float(0.3)  # the failure being avoided


def test_repeated_addition_does_not_drift() -> None:
    """Ten cents added ten times is exactly one euro. In binary it is not."""
    total = Amount("0", "EUR")
    for _ in range(10):
        total = total + Amount("0.10", "EUR")

    assert total.value == Decimal("1.00")


def test_scale_is_preserved_rather_than_normalized() -> None:
    """An invoice that says 10.00 must not be rewritten as 10. The trailing zero
    carries the precision the document asserted."""
    assert str(Amount("10.00", "EUR").value) == "10.00"
    assert str(Amount("10.0", "EUR").value) == "10.0"


# ── currencyID is required and meaningful ──────────────────────────────────


def test_an_amount_requires_a_currency() -> None:
    """"Amount-typed basic components require a currencyID attribute" -- an
    amount without one is not a quantity of money, it is a bare number."""
    with pytest.raises(UblValidationError) as raised:
        Amount("10.00", "")

    assert "currency" in str(raised.value).lower()


@pytest.mark.parametrize("bad", ["eur", "EU", "EURO", "E1R", "12 ", "€"])
def test_currency_must_look_like_an_iso_4217_code(bad: str) -> None:
    """"identifying the ISO 4217 currency" -- three uppercase letters. This does
    not verify the code is *assigned*, only that it is well-formed; claiming
    otherwise would need a currency register this library does not ship."""
    with pytest.raises(UblValidationError):
        Amount("10.00", bad)


def test_amounts_in_different_currencies_cannot_be_added() -> None:
    """The single most valuable thing this type does. Adding EUR to USD is
    meaningless without a rate, and a library that silently returned 30 would
    produce a wrong invoice that looks right."""
    with pytest.raises(UblValidationError) as raised:
        Amount("10.00", "EUR") + Amount("20.00", "USD")

    assert "EUR" in str(raised.value) and "USD" in str(raised.value)


def test_subtraction_enforces_the_same_currency_rule() -> None:
    with pytest.raises(UblValidationError):
        Amount("10.00", "EUR") - Amount("1.00", "GBP")


def test_amounts_in_the_same_currency_subtract() -> None:
    assert (Amount("10.00", "EUR") - Amount("2.50", "EUR")).value == Decimal("7.50")


# ── Rounding is explicit, never implicit ───────────────────────────────────


def test_arithmetic_never_rounds_on_its_own() -> None:
    """"explicit rounding policies for any calculation" -- multiplication keeps
    full precision, so the caller decides when and how to round rather than
    discovering a bank's rule was applied for them."""
    line = Amount("0.335", "EUR") * Decimal("3")

    assert line.value == Decimal("1.005")


def test_rounding_requires_a_named_policy() -> None:
    rounded = Amount("1.005", "EUR").round_to(2, Rounding.HALF_UP)

    assert rounded.value == Decimal("1.01")


def test_rounding_policies_differ_and_the_choice_is_the_callers() -> None:
    """HALF_UP and HALF_EVEN disagree on exactly this value. That disagreement
    is why the policy cannot have a silent default."""
    amount = Amount("1.005", "EUR")

    assert amount.round_to(2, Rounding.HALF_UP).value == Decimal("1.01")
    assert amount.round_to(2, Rounding.HALF_EVEN).value == Decimal("1.00")


def test_rounding_preserves_the_currency() -> None:
    assert Amount("1.005", "GBP").round_to(2, Rounding.HALF_UP).currency_id == "GBP"


# ── Quantity ───────────────────────────────────────────────────────────────


def test_a_quantity_carries_an_optional_unit_code() -> None:
    """"Quantity-typed basic components carry an OPTIONAL unitCode attribute" --
    optional, unlike currencyID, and the asymmetry is deliberate."""
    assert Quantity("5", "KGM").unit_code == "KGM"
    assert Quantity("5").unit_code is None


def test_a_quantity_also_refuses_floats() -> None:
    with pytest.raises(UblValidationError):
        Quantity(2.5)  # type: ignore[arg-type]


def test_an_amount_multiplied_by_a_quantity_keeps_the_currency() -> None:
    line_total = Amount("2.50", "EUR") * Quantity("4")

    assert line_total.value == Decimal("10.00")
    assert line_total.currency_id == "EUR"


# ── Code: normalized strings with list identification ──────────────────────


def test_a_code_preserves_its_list_attributes() -> None:
    code = Code("380", list_id="UNCL1001", list_agency_id="6", list_version_id="D08B")

    assert (code.value, code.list_id, code.list_agency_id, code.list_version_id) == (
        "380",
        "UNCL1001",
        "6",
        "D08B",
    )


@pytest.mark.parametrize(
    "raw,expected",
    [("a\tb", "a b"), ("a\nb", "a b"), ("a\rb", "a b"), ("a\r\nb", "a  b")],
)
def test_code_values_are_normalized_strings(raw: str, expected: str) -> None:
    """XSD normalizedString replaces each tab, line feed and carriage return
    with a single space. It does NOT collapse runs or strip -- that is
    xsd:token, a different type, and conflating them would silently alter data."""
    assert Code(raw).value == expected


def test_code_normalization_does_not_collapse_or_strip() -> None:
    """The control for the rule above: proving this is normalizedString and not
    token, since a token implementation would pass the tests above too."""
    assert Code("  a   b  ").value == "  a   b  "


def test_an_empty_code_is_refused() -> None:
    with pytest.raises(UblValidationError):
        Code("")


# ── Identifier ─────────────────────────────────────────────────────────────


def test_an_identifier_preserves_its_scheme_attributes() -> None:
    identifier = Identifier("INV-001", scheme_id="GS1", scheme_agency_id="9")

    assert identifier.value == "INV-001"
    assert identifier.scheme_id == "GS1"
    assert identifier.scheme_agency_id == "9"


def test_identifier_scheme_attributes_are_optional() -> None:
    identifier = Identifier("INV-001")

    assert identifier.scheme_id is None and identifier.scheme_agency_id is None


def test_an_empty_identifier_is_refused() -> None:
    with pytest.raises(UblValidationError):
        Identifier("   ")


# ── BinaryObject: base64 with a required mimeCode ──────────────────────────


def test_a_binary_object_requires_a_mime_code() -> None:
    """"whose mimeCode attribute is REQUIRED in the UBL UDT" -- an attachment
    whose type is unknown cannot be safely handled by a consumer."""
    with pytest.raises(UblValidationError) as raised:
        BinaryObject(b"payload", "")

    assert "mime" in str(raised.value).lower()


def test_a_binary_object_round_trips_through_base64() -> None:
    payload = b"\x00\x01\x02 binary \xff\xfe"
    attachment = BinaryObject(payload, "application/pdf")

    assert attachment.to_base64() == base64.b64encode(payload).decode("ascii")
    assert BinaryObject.from_base64(attachment.to_base64(), "application/pdf").data == payload


def test_binary_object_rejects_malformed_base64() -> None:
    with pytest.raises(UblValidationError):
        BinaryObject.from_base64("not valid base64!!!", "application/pdf")


def test_binary_object_preserves_its_filename_when_given() -> None:
    attachment = BinaryObject(b"x", "text/plain", filename="notes.txt")

    assert attachment.filename == "notes.txt"


def test_binary_object_exposes_a_sha256_checksum_of_its_raw_bytes() -> None:
    """UBL-EXT-001: "expose their media types and checksums without
    decoding side effects." mime_code (media type) was already exposed;
    checksum is the raw SHA-256 digest of the stored bytes."""
    payload = b"\x00\x01\x02 binary \xff\xfe"
    attachment = BinaryObject(payload, "application/pdf")

    assert attachment.checksum == hashlib.sha256(payload).hexdigest()


def test_binary_object_checksum_differs_for_different_content() -> None:
    first = BinaryObject(b"content one", "text/plain")
    second = BinaryObject(b"content two", "text/plain")

    assert first.checksum != second.checksum


def test_binary_object_checksum_is_independent_of_mime_code() -> None:
    """The checksum hashes the raw bytes only -- never anything decoded or
    interpreted from the declared media type, since the attachment is
    untrusted data this package never evaluates."""
    payload = b"same bytes regardless of declared type"

    as_pdf = BinaryObject(payload, "application/pdf")
    as_text = BinaryObject(payload, "text/plain")

    assert as_pdf.checksum == as_text.checksum


# ── Values are immutable, so attributes survive edits ──────────────────────


def test_amounts_are_immutable() -> None:
    """"retain currencyID, unitCode, and scheme attributes THROUGH EDITS."
    Immutability is how: an edit produces a new value carrying the attributes
    rather than mutating one in place and possibly dropping them."""
    amount = Amount("10.00", "EUR")

    with pytest.raises(Exception):
        amount.value = Decimal("99")  # type: ignore[misc]


def test_arithmetic_returns_new_values_and_leaves_operands_untouched() -> None:
    original = Amount("10.00", "EUR")

    result = original + Amount("5.00", "EUR")

    assert result.value == Decimal("15.00")
    assert original.value == Decimal("10.00")


def test_equality_accounts_for_the_supplementary_attributes() -> None:
    """Ten euros is not ten dollars, and a comparison that ignored currency
    would make that mistake silently."""
    assert Amount("10.00", "EUR") == Amount("10.00", "EUR")
    assert Amount("10.00", "EUR") != Amount("10.00", "USD")
    assert Quantity("5", "KGM") != Quantity("5", "LTR")
