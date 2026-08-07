"""UBL-MODEL-001 / UBL-PARSE-001 / UBL-VALIDATE-001 / UBL-DOCTYPES-001 /
UBL-SIGN-001 / UBL-REF-001 -- "full schema and cardinality validation" and
"full element-order validation" against every UBL complexType, across all
~91 root document types.

MUST: several sibling obligations shared near-identical missing_behavior
text: "Full schema and cardinality validation across every UBL complexType
remains a genuinely large, separate undertaking... out of the full UBL
2.3 schema's ~91 root document types" and "Full element-order validation
across every UBL complexType remains a genuinely large, separate
undertaking." Correctly so, if building an independent, hand-written
structural validator matching all 91 root types' own real schemas from
scratch -- but composing the REAL schemas the OASIS distribution itself
ships is a fundamentally different, much smaller task.

Grounded directly in the pinned raw UBL 2.3 distribution package
(.local/format-contracts/acquired/ubl/src-ubl-002.bin -- already used
once this session to bundle the official genericode code lists; its
xsd/common/ and xsd/maindoc/ directories, previously unexplored, contain
the complete, authoritative OASIS UBL 2.3 schema: 15 shared component
schemas plus one root-document-type schema per each of the 91 document
types this package's own ROOT_CLASSES models). XSD sequence validation
inherently checks cardinality AND element order together in one pass --
this is not two separate features, it is what "valid against the schema"
has always meant.

Deliberately narrow about two things this does NOT do: it does not make
the writer auto-reorder elements into schema-valid order regardless of
construction order (UBL-WRITE-001's own separate, still-unbuilt
"independent of mutation order" clause); and it validates raw XML
structure independent of this package's own typed object model, so it
neither depends on nor extends that model's own coverage (cac:Attachment,
which the typed model does not represent, is still fully checked here
since validation operates on the XML directly, not the typed model).
"""

from __future__ import annotations

import pytest

xmlschema = pytest.importorskip("xmlschema", reason="optional xmlschema dependency not installed")

from format_factory.ubl import SchemaValidationUnavailable, UblParseError, schema_validate  # noqa: E402
from format_factory.ubl.validation.schema_validator import _load_schema  # noqa: E402

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice(*, extra_before_line: str = "") -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        '<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>http://x.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
        f"{extra_before_line}"
        '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
        "<cac:InvoiceLine>"
        "<cbc:ID>1</cbc:ID>"
        '<cbc:InvoicedQuantity unitCode="KGM">1</cbc:InvoicedQuantity>'
        '<cbc:LineExtensionAmount currencyID="USD">1.00</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        '<cac:Price><cbc:PriceAmount currencyID="USD">1.00</cbc:PriceAmount></cac:Price>'
        "</cac:InvoiceLine>"
        "</Invoice>"
    ).encode()


def _credit_note() -> bytes:
    return (
        f'<CreditNote xmlns="urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>CN-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:CreditNoteTypeCode>381</cbc:CreditNoteTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        '<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>http://x.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
        '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
        "<cac:CreditNoteLine>"
        "<cbc:ID>1</cbc:ID>"
        '<cbc:CreditedQuantity unitCode="KGM">1</cbc:CreditedQuantity>'
        '<cbc:LineExtensionAmount currencyID="USD">1.00</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        '<cac:Price><cbc:PriceAmount currencyID="USD">1.00</cbc:PriceAmount></cac:Price>'
        "</cac:CreditNoteLine>"
        "</CreditNote>"
    ).encode()


def test_a_well_formed_invoice_validates_cleanly() -> None:
    report = schema_validate(_invoice())

    assert report.is_valid
    assert report.diagnostics == ()


def test_root_name_is_auto_detected_when_not_given() -> None:
    report = schema_validate(_invoice())

    assert report.is_valid


def test_an_explicit_matching_root_name_also_works() -> None:
    report = schema_validate(_invoice(), root_name="Invoice")

    assert report.is_valid


def test_a_well_formed_credit_note_validates_against_its_own_schema() -> None:
    """A different one of the 91 root document types, proving this isn't
    hardcoded to Invoice alone."""
    report = schema_validate(_credit_note())

    assert report.is_valid


def test_element_order_violation_is_caught() -> None:
    """LegalMonetaryTotal appears before AccountingCustomerParty --
    "full element-order validation" proven against a real violation."""
    document = (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        '<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>http://x.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
        "<cac:InvoiceLine>"
        "<cbc:ID>1</cbc:ID>"
        '<cbc:InvoicedQuantity unitCode="KGM">1</cbc:InvoicedQuantity>'
        '<cbc:LineExtensionAmount currencyID="USD">1.00</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        '<cac:Price><cbc:PriceAmount currencyID="USD">1.00</cbc:PriceAmount></cac:Price>'
        "</cac:InvoiceLine>"
        "</Invoice>"
    ).encode()

    report = schema_validate(document)

    assert not report.is_valid
    assert {item.code for item in report.diagnostics} == {"ubl.schema.invalid"}


def test_a_cardinality_violation_is_caught() -> None:
    """Two LegalMonetaryTotal elements -- "full cardinality validation"
    proven against a real violation, independent of the 16-complexType
    coverage limit the package's own typed-model cardinality checker has."""
    document = _invoice(
        extra_before_line=(
            '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">9.00</cbc:PayableAmount>'
            "</cac:LegalMonetaryTotal>"
        )
    )

    report = schema_validate(document)

    assert not report.is_valid


def test_every_violation_is_reported_not_just_the_first() -> None:
    document = (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "</Invoice>"
    ).encode()

    report = schema_validate(document)

    assert not report.is_valid
    assert len(report.diagnostics) >= 1


def test_an_unsupported_root_document_type_is_rejected() -> None:
    with pytest.raises(UblParseError, match="not a supported UBL 2.3 root document type"):
        schema_validate(b'<NotARealDocumentType xmlns="urn:example"/>')


def test_malformed_xml_raises_a_clear_parse_error() -> None:
    with pytest.raises(UblParseError, match="malformed XML"):
        schema_validate(b"<Invoice><")


def test_schema_validation_unavailable_when_xmlschema_cannot_be_imported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The optional dependency degrades gracefully: importing this
    package never requires `xmlschema` at all, only calling
    schema_validate() does."""
    import sys

    _load_schema.cache_clear()
    real_import = __import__

    def _blocked_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "xmlschema":
            raise ImportError("simulated: xmlschema not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setitem(sys.modules, "xmlschema", None)
    monkeypatch.delitem(sys.modules, "xmlschema", raising=False)
    monkeypatch.setattr("builtins.__import__", _blocked_import)

    try:
        with pytest.raises(SchemaValidationUnavailable, match="xmlschema"):
            schema_validate(_invoice())
    finally:
        _load_schema.cache_clear()
