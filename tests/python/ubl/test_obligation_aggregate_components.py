"""UBL-MODEL-001 — shared aggregate components as typed composites.

  "Represent shared aggregate components as typed composites and basic
   components as typed values retaining lexical form where round-trip fidelity
   requires it."
  "Reflect schema element order, cardinality, and optionality in the model so
   invalid structures are diagnosable at edit time."

The aggregates this builds are the ones the contract names:

  "cac:InvoiceLine is an aggregate component type carrying cbc:ID,
   cbc:InvoicedQuantity, cbc:LineExtensionAmount, and a cac:Item element"
  "cac:Item is an aggregate component type describing traded items with names,
   identification schemes, and classification code elements"
  "cac:LegalMonetaryTotal is an aggregate component type carrying line
   extension, tax-inclusive, allowance, charge, and payable amount elements"
  "cac:TaxTotal is an aggregate component type carrying cbc:TaxAmount and nested
   cac:TaxSubtotal elements per tax category"

One rule shapes the whole design:

  "UBL AmountType is decimal and requires currencyID; aggregate definitions
   document line extension, tax, and payable amounts, but the XSD does not
   encode cross-field arithmetic reconciliation."

So reconciliation is offered as an explicit, *reporting* operation. A library
that silently corrected a total would be rewriting a business document to match
its own arithmetic, and one that raised would reject real invoices that are
legitimately rounded differently.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import (
    Amount,
    Identifier,
    InvoiceLine,
    Item,
    LegalMonetaryTotal,
    Quantity,
    TaxSubtotal,
    TaxTotal,
    UblValidationError,
    invoice_line_of,
    legal_monetary_total_of,
    loads,
    reconcile_invoice,
    tax_total_of,
)

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

INVOICE = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="{CBC}" xmlns:cac="{CAC}">
<cbc:ID>INV-001</cbc:ID>
<cac:InvoiceLine>
  <cbc:ID>1</cbc:ID>
  <cbc:InvoicedQuantity unitCode="KGM">2</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="EUR">20.00</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Coffee beans</cbc:Name></cac:Item>
</cac:InvoiceLine>
<cac:InvoiceLine>
  <cbc:ID>2</cbc:ID>
  <cbc:InvoicedQuantity unitCode="LTR">1</cbc:InvoicedQuantity>
  <cbc:LineExtensionAmount currencyID="EUR">5.00</cbc:LineExtensionAmount>
  <cac:Item><cbc:Name>Milk</cbc:Name></cac:Item>
</cac:InvoiceLine>
<cac:TaxTotal>
  <cbc:TaxAmount currencyID="EUR">5.00</cbc:TaxAmount>
  <cac:TaxSubtotal>
    <cbc:TaxableAmount currencyID="EUR">25.00</cbc:TaxableAmount>
    <cbc:TaxAmount currencyID="EUR">5.00</cbc:TaxAmount>
  </cac:TaxSubtotal>
</cac:TaxTotal>
<cac:LegalMonetaryTotal>
  <cbc:LineExtensionAmount currencyID="EUR">25.00</cbc:LineExtensionAmount>
  <cbc:TaxInclusiveAmount currencyID="EUR">30.00</cbc:TaxInclusiveAmount>
  <cbc:PayableAmount currencyID="EUR">30.00</cbc:PayableAmount>
</cac:LegalMonetaryTotal>
</Invoice>""".encode("utf-8")


@pytest.fixture
def invoice():
    return loads(INVOICE).root


# ── Cardinality is enforced, so invalid structures are diagnosable ─────────


def test_an_invoice_line_carries_its_four_required_components() -> None:
    line = InvoiceLine(
        id=Identifier("1"),
        invoiced_quantity=Quantity("2", "KGM"),
        line_extension_amount=Amount("20.00", "EUR"),
        item=Item(name="Coffee beans"),
    )

    assert line.id.value == "1"
    assert line.line_extension_amount == Amount("20.00", "EUR")
    assert line.item.name == "Coffee beans"


@pytest.mark.parametrize("omitted", ["id", "invoiced_quantity", "line_extension_amount", "item"])
def test_an_invoice_line_refuses_a_missing_required_component(omitted: str) -> None:
    """"Reflect schema element order, cardinality, and optionality ... so
    invalid structures are diagnosable at edit time." Constructing an incomplete
    line must fail where it is built, not later where it is serialized."""
    fields = {
        "id": Identifier("1"),
        "invoiced_quantity": Quantity("2"),
        "line_extension_amount": Amount("20.00", "EUR"),
        "item": Item(name="Coffee beans"),
    }
    fields[omitted] = None

    with pytest.raises(UblValidationError) as raised:
        InvoiceLine(**fields)  # type: ignore[arg-type]

    assert omitted.replace("_", "") in str(raised.value).lower().replace("_", "").replace(" ", "")


def test_an_item_requires_a_name() -> None:
    with pytest.raises(UblValidationError):
        Item(name="")


def test_an_item_carries_optional_identifiers_and_classification_codes() -> None:
    item = Item(
        name="Coffee beans",
        identifiers=(Identifier("SKU-9", scheme_id="GS1"),),
        classification_codes=(),
    )

    assert item.identifiers[0].scheme_id == "GS1"
    assert item.classification_codes == ()


def test_a_legal_monetary_total_requires_line_extension_and_payable() -> None:
    with pytest.raises(UblValidationError):
        LegalMonetaryTotal(line_extension_amount=Amount("25.00", "EUR"), payable_amount=None)  # type: ignore[arg-type]


def test_a_tax_total_requires_a_tax_amount() -> None:
    with pytest.raises(UblValidationError):
        TaxTotal(tax_amount=None)  # type: ignore[arg-type]


# ── Projection from a real document ────────────────────────────────────────


def test_invoice_lines_project_from_xml(invoice) -> None:
    from format_factory.ubl import find_all

    lines = [invoice_line_of(node) for node in find_all(invoice, "InvoiceLine")]

    assert [line.id.value for line in lines] == ["1", "2"]
    assert lines[0].item.name == "Coffee beans"
    assert lines[0].invoiced_quantity == Quantity("2", "KGM")
    assert lines[1].line_extension_amount == Amount("5.00", "EUR")


def test_a_tax_total_projects_with_its_subtotals(invoice) -> None:
    from format_factory.ubl import find

    total = tax_total_of(find(invoice, "TaxTotal"))

    assert total.tax_amount == Amount("5.00", "EUR")
    assert len(total.subtotals) == 1
    assert total.subtotals[0].taxable_amount == Amount("25.00", "EUR")


def test_a_legal_monetary_total_projects_its_optional_amounts(invoice) -> None:
    from format_factory.ubl import find

    total = legal_monetary_total_of(find(invoice, "LegalMonetaryTotal"))

    assert total.line_extension_amount == Amount("25.00", "EUR")
    assert total.tax_inclusive_amount == Amount("30.00", "EUR")
    assert total.allowance_total_amount is None


def test_projecting_a_line_missing_its_item_is_refused() -> None:
    broken = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
     xmlns:cbc="{CBC}" xmlns:cac="{CAC}">
    <cac:InvoiceLine>
      <cbc:ID>1</cbc:ID>
      <cbc:InvoicedQuantity>2</cbc:InvoicedQuantity>
      <cbc:LineExtensionAmount currencyID="EUR">20.00</cbc:LineExtensionAmount>
    </cac:InvoiceLine>
    </Invoice>""".encode("utf-8")
    from format_factory.ubl import find

    with pytest.raises(UblValidationError):
        invoice_line_of(find(loads(broken).root, "InvoiceLine"))


# ── Reconciliation reports; it never fixes and never raises ────────────────


def test_a_consistent_invoice_reconciles_clean(invoice) -> None:
    """The control. Without it, a reconciler that reported problems
    unconditionally would look identical to one that works."""
    report = reconcile_invoice(invoice)

    assert report.is_valid is True
    assert report.diagnostics == ()


def test_a_line_total_mismatch_is_reported(invoice) -> None:
    """"the XSD does not encode cross-field arithmetic reconciliation" -- so
    this is exactly the class of error schema validation cannot catch, and the
    reason to offer it at all."""
    wrong = INVOICE.replace(
        b'<cbc:LineExtensionAmount currencyID="EUR">25.00</cbc:LineExtensionAmount>',
        b'<cbc:LineExtensionAmount currencyID="EUR">99.00</cbc:LineExtensionAmount>',
    )

    report = reconcile_invoice(loads(wrong).root)

    assert report.is_valid is False
    assert any("LINE_EXTENSION" in d.code for d in report.diagnostics)


def test_a_tax_subtotal_mismatch_is_reported() -> None:
    wrong = INVOICE.replace(
        b"<cbc:TaxAmount currencyID=\"EUR\">5.00</cbc:TaxAmount>\n  <cac:TaxSubtotal>",
        b"<cbc:TaxAmount currencyID=\"EUR\">7.00</cbc:TaxAmount>\n  <cac:TaxSubtotal>",
    )

    report = reconcile_invoice(loads(wrong).root)

    assert any("TAX" in d.code for d in report.diagnostics)


def test_reconciliation_does_not_alter_the_document(invoice) -> None:
    """A library that silently corrected a total would be rewriting a business
    document to match its own arithmetic."""
    before = invoice

    reconcile_invoice(invoice)

    assert invoice == before


def test_reconciliation_reports_rather_than_raising() -> None:
    """Real invoices are legitimately rounded in ways a naive sum disagrees
    with, so a mismatch is a finding for a human, not a parse failure."""
    wrong = INVOICE.replace(b">25.00<", b">99.00<")

    report = reconcile_invoice(loads(wrong).root)  # must not raise

    assert report.is_valid is False


def test_a_currency_mismatch_across_lines_is_reported() -> None:
    """Summing across currencies is meaningless, so it is reported instead of
    attempted."""
    mixed = INVOICE.replace(
        b'<cbc:LineExtensionAmount currencyID="EUR">5.00</cbc:LineExtensionAmount>',
        b'<cbc:LineExtensionAmount currencyID="USD">5.00</cbc:LineExtensionAmount>',
    )

    report = reconcile_invoice(loads(mixed).root)

    assert any("CURRENCY" in d.code for d in report.diagnostics)


def test_an_invoice_without_totals_reconciles_without_complaint() -> None:
    """Absent optional aggregates are not errors -- only present-and-wrong ones
    are. A reconciler that demanded totals would reject valid documents."""
    minimal = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
     xmlns:cbc="{CBC}" xmlns:cac="{CAC}"><cbc:ID>X</cbc:ID></Invoice>""".encode("utf-8")

    report = reconcile_invoice(loads(minimal).root)

    assert report.is_valid is True
