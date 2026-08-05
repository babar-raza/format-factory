"""Temporal projection, plus cac:AllowanceCharge, cac:Price and cac:PaymentMeans.

Two things in one slice, because they share a cause. The temporal types built in
the previous slice had the same defect the money types had before their own
projection layer: correct, and unreachable from a parsed document. A
`cbc:IssueDate` still came back as untyped text, which is where a caller
re-introduces exactly the lexical loss the types exist to prevent.

The remaining aggregates the contract names are built alongside:

  "cac:AllowanceCharge is an aggregate component type with a charge indicator,
   reason codes, and amount elements applied at document or line level"
  "cac:Price is an aggregate component type carrying cbc:PriceAmount and
   quantity-basis elements for unit pricing"
  "cac:PaymentMeans is an aggregate component type carrying payment means codes,
   due dates, and payee financial account elements"
"""

from __future__ import annotations

import pytest

from format_factory.ubl import (
    AllowanceCharge,
    Amount,
    Code,
    PaymentMeans,
    Price,
    Quantity,
    UblDate,
    UblDateTime,
    UblValidationError,
    XmlNode,
    allowance_charge_of,
    date_of,
    date_time_of,
    find,
    loads,
    payment_means_of,
    price_of,
    time_of,
    to_node,
)

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

DOC = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="{CBC}" xmlns:cac="{CAC}">
<cbc:IssueDate>2026-08-05</cbc:IssueDate>
<cbc:IssueTime>10:30:00Z</cbc:IssueTime>
<cac:AllowanceCharge>
  <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
  <cbc:AllowanceChargeReasonCode listID="UNCL5189">95</cbc:AllowanceChargeReasonCode>
  <cbc:Amount currencyID="EUR">2.50</cbc:Amount>
</cac:AllowanceCharge>
<cac:Price>
  <cbc:PriceAmount currencyID="EUR">12.50</cbc:PriceAmount>
  <cbc:BaseQuantity unitCode="KGM">1</cbc:BaseQuantity>
</cac:Price>
<cac:PaymentMeans>
  <cbc:PaymentMeansCode listID="UNCL4461">30</cbc:PaymentMeansCode>
  <cbc:PaymentDueDate>2026-09-04</cbc:PaymentDueDate>
</cac:PaymentMeans>
</Invoice>""".encode("utf-8")


@pytest.fixture
def doc():
    return loads(DOC).root


# ── Temporal projection ────────────────────────────────────────────────────


def test_an_issue_date_projects_to_a_typed_date(doc) -> None:
    """Previously this came back as untyped text, which is exactly where a
    caller re-introduces the lexical loss UblDate exists to prevent."""
    issued = date_of(find(doc, "IssueDate"))

    assert issued == UblDate("2026-08-05")
    assert str(issued) == "2026-08-05"


def test_an_issue_time_projects_and_keeps_its_zone(doc) -> None:
    issued = time_of(find(doc, "IssueTime"))

    assert str(issued) == "10:30:00Z"
    assert issued.has_timezone is True


def test_a_date_time_projects_and_keeps_its_exact_lexical_form() -> None:
    node = XmlNode.create("{" + CBC + "}IssueInstant", text="2026-08-05T10:30:00.000+02:00")

    assert str(date_time_of(node)) == "2026-08-05T10:30:00.000+02:00"


def test_projecting_a_missing_temporal_element_is_refused() -> None:
    with pytest.raises(UblValidationError):
        date_of(None)  # type: ignore[arg-type]


def test_a_malformed_date_in_a_document_is_refused_not_coerced() -> None:
    node = XmlNode.create("{" + CBC + "}IssueDate", text="05/08/2026")

    with pytest.raises(UblValidationError):
        date_of(node)


def test_surrounding_whitespace_in_the_element_is_tolerated(doc) -> None:
    """XML pretty-printing routinely adds whitespace around element text; that
    is a transport artefact, not part of the lexical value."""
    node = XmlNode.create("{" + CBC + "}IssueDate", text="\n  2026-08-05\n")

    assert str(date_of(node)) == "2026-08-05"


def test_temporal_values_project_back_to_nodes() -> None:
    node = to_node("{" + CBC + "}IssueDate", UblDate("2026-08-05"))

    assert node.text == "2026-08-05"
    assert node.attributes == ()


def test_a_date_time_round_trips_through_the_projection_layer() -> None:
    original = UblDateTime("2026-08-05T10:30:00.000+02:00")

    assert date_time_of(to_node("{" + CBC + "}X", original)) == original


# ── cac:AllowanceCharge ────────────────────────────────────────────────────


def test_an_allowance_charge_projects_with_its_indicator_and_amount(doc) -> None:
    charge = allowance_charge_of(find(doc, "AllowanceCharge"))

    assert charge.charge_indicator is False
    assert charge.amount == Amount("2.50", "EUR")
    assert charge.reason_code == Code("95", list_id="UNCL5189")


def test_the_charge_indicator_distinguishes_a_charge_from_an_allowance() -> None:
    """A charge adds and an allowance subtracts. Getting the boolean wrong
    inverts the sign of a line on the invoice, so the two spellings XSD permits
    are both handled and anything else is refused."""
    for text, expected in (("true", True), ("1", True), ("false", False), ("0", False)):
        node = XmlNode.create(
            "{" + CAC + "}AllowanceCharge",
            children=(
                XmlNode.create("{" + CBC + "}ChargeIndicator", text=text),
                XmlNode.create("{" + CBC + "}Amount", attributes={"currencyID": "EUR"}, text="1.00"),
            ),
        )
        assert allowance_charge_of(node).charge_indicator is expected


def test_an_ambiguous_charge_indicator_is_refused() -> None:
    """"yes" is not an xsd:boolean. Guessing would silently flip a sign."""
    node = XmlNode.create(
        "{" + CAC + "}AllowanceCharge",
        children=(
            XmlNode.create("{" + CBC + "}ChargeIndicator", text="yes"),
            XmlNode.create("{" + CBC + "}Amount", attributes={"currencyID": "EUR"}, text="1.00"),
        ),
    )

    with pytest.raises(UblValidationError):
        allowance_charge_of(node)


def test_an_allowance_charge_requires_an_indicator_and_amount() -> None:
    with pytest.raises(UblValidationError):
        AllowanceCharge(charge_indicator=None, amount=Amount("1.00", "EUR"))  # type: ignore[arg-type]


# ── cac:Price ──────────────────────────────────────────────────────────────


def test_a_price_projects_with_its_base_quantity(doc) -> None:
    price = price_of(find(doc, "Price"))

    assert price.price_amount == Amount("12.50", "EUR")
    assert price.base_quantity == Quantity("1", "KGM")


def test_a_price_requires_an_amount() -> None:
    with pytest.raises(UblValidationError):
        Price(price_amount=None)  # type: ignore[arg-type]


def test_a_base_quantity_is_optional() -> None:
    """Unit pricing without a stated basis is valid; defaulting it to 1 would
    assert a basis the document never gave."""
    price = Price(price_amount=Amount("12.50", "EUR"))

    assert price.base_quantity is None


# ── cac:PaymentMeans ───────────────────────────────────────────────────────


def test_payment_means_projects_with_its_code_and_due_date(doc) -> None:
    means = payment_means_of(find(doc, "PaymentMeans"))

    assert means.payment_means_code == Code("30", list_id="UNCL4461")
    assert means.payment_due_date == UblDate("2026-09-04")


def test_payment_means_requires_a_code() -> None:
    with pytest.raises(UblValidationError):
        PaymentMeans(payment_means_code=None)  # type: ignore[arg-type]


def test_a_payment_due_date_is_optional() -> None:
    means = PaymentMeans(payment_means_code=Code("30"))

    assert means.payment_due_date is None


def test_a_malformed_due_date_is_refused() -> None:
    node = XmlNode.create(
        "{" + CAC + "}PaymentMeans",
        children=(
            XmlNode.create("{" + CBC + "}PaymentMeansCode", text="30"),
            XmlNode.create("{" + CBC + "}PaymentDueDate", text="soon"),
        ),
    )

    with pytest.raises(UblValidationError):
        payment_means_of(node)


def test_a_well_formed_document_projects_all_three_aggregates(doc) -> None:
    """Control: the rejection tests above must not be passing because the
    projections reject everything."""
    assert allowance_charge_of(find(doc, "AllowanceCharge")).amount.currency_id == "EUR"
    assert price_of(find(doc, "Price")).price_amount.currency_id == "EUR"
    assert payment_means_of(find(doc, "PaymentMeans")).payment_means_code.value == "30"
