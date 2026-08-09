"""UBL-UPGRADE-001 -- detect older UBL versions and migrate to the stable
profile.

MUST (SAL-UBL-OBL-7B16479ACBBC8EFC): "Detect older specification versions
where practical; migrate via explicit transforms producing a migration
report; never label a document as the target version without structural
migration and validation."

SAL-UBL-7546731B76606EC0 (a direct structural diff of the acquired OASIS
UBL 2.1 and UBL 2.3 release packages) proves that for 65 of the 91 UBL 2.3
root document types, every schema difference between 2.1 and 2.3 is
additive/relaxing only -- never a removal, reordering, or tightening.
SAL-UBL-F90975267B9AE315 proves the analogous fact for 81 of the 91 UBL
2.3 root document types between UBL 2.2 and 2.3. ``migrate_document()`` is
grounded directly in these two facts, not invented: it supports ONLY the
2.1-to-2.3 and 2.2-to-2.3 directions, and ONLY the root types each
respective fact covers, refusing everything else rather than guessing.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import UblValidationError, load
from format_factory.ubl.migration import MigrationReport, migrate_document

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice_bytes(*, version: str | None = "2.1", duplicate_version: bool = False) -> bytes:
    version_field = ""
    if version is not None:
        version_field = f"<cbc:UBLVersionID>{version}</cbc:UBLVersionID>"
        if duplicate_version:
            version_field += f"<cbc:UBLVersionID>{version}</cbc:UBLVersionID>"
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        f"{version_field}"
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        '<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>http://x.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
        '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
        "</Invoice>"
    ).encode()


def _business_card_2_1_ineligible_bytes() -> bytes:
    """A root type declaring UBLVersionID 2.1 but whose own root type is
    genuinely NOT in MIGRATABLE_2_1_ROOT_NAMES -- ``BusinessCard`` never
    had a UBL 2.1 maindoc schema at all (confirmed directly against the
    acquired UBL 2.1 release package, not assumed)."""
    ns = "urn:oasis:names:specification:ubl:schema:xsd:BusinessCard-2"
    return (
        f'<BusinessCard xmlns="{ns}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:UBLVersionID>2.1</cbc:UBLVersionID>"
        "<cbc:ID>BC-001</cbc:ID>"
        "</BusinessCard>"
    ).encode()


def _import_customs_declaration_2_2_ineligible_bytes() -> bytes:
    """A root type declaring UBLVersionID 2.2 but whose own root type is
    genuinely NOT in MIGRATABLE_2_2_ROOT_NAMES -- ``ImportCustomsDeclaration``
    never had a UBL 2.2 maindoc schema at all (confirmed directly against
    the acquired UBL 2.2 release package, not assumed)."""
    ns = "urn:oasis:names:specification:ubl:schema:xsd:ImportCustomsDeclaration-2"
    return (
        f'<ImportCustomsDeclaration xmlns="{ns}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:UBLVersionID>2.2</cbc:UBLVersionID>"
        "<cbc:ID>ICD-001</cbc:ID>"
        "</ImportCustomsDeclaration>"
    ).encode()


def test_migrate_document_relabels_a_valid_2_1_invoice_and_produces_a_report():
    document = load(_invoice_bytes(version="2.1"))
    migrated, report = migrate_document(document)

    assert migrated.declared_version == "2.3"
    assert isinstance(report, MigrationReport)
    assert report.root_name == "Invoice"
    assert report.source_version == "2.1"
    assert report.target_version == "2.3"


def test_migrate_document_result_passes_stable_2_3_validation():
    from format_factory.ubl import validate

    document = load(_invoice_bytes(version="2.1"))
    migrated, _ = migrate_document(document)

    report = validate(migrated)
    assert report.is_valid, report.diagnostics


def test_migrate_document_does_not_mutate_the_original_document():
    document = load(_invoice_bytes(version="2.1"))
    migrate_document(document)

    assert document.declared_version == "2.1"


def test_migrate_document_refuses_a_document_declaring_an_unsupported_version():
    document = load(_invoice_bytes(version="2.0"))
    with pytest.raises(UblValidationError, match="2.0"):
        migrate_document(document)


def test_migrate_document_refuses_a_document_with_no_declared_version():
    document = load(_invoice_bytes(version=None))
    with pytest.raises(UblValidationError):
        migrate_document(document)


def test_migrate_document_refuses_a_root_type_not_covered_by_the_structural_diff():
    document = load(_business_card_2_1_ineligible_bytes())
    with pytest.raises(UblValidationError, match="BusinessCard"):
        migrate_document(document)


def test_migrate_document_refuses_rather_than_silently_relabels_when_the_result_would_fail_validation():
    document = load(_invoice_bytes(version="2.1", duplicate_version=True))
    with pytest.raises(UblValidationError, match="validation"):
        migrate_document(document)


def test_migrate_document_never_labels_the_original_input_document_object_itself():
    document = load(_invoice_bytes(version="2.1", duplicate_version=True))
    try:
        migrate_document(document)
    except UblValidationError:
        pass
    assert document.declared_version == "2.1"


def test_migrate_document_relabels_a_valid_2_2_invoice_and_produces_a_report():
    document = load(_invoice_bytes(version="2.2"))
    migrated, report = migrate_document(document)

    assert migrated.declared_version == "2.3"
    assert isinstance(report, MigrationReport)
    assert report.root_name == "Invoice"
    assert report.source_version == "2.2"
    assert report.target_version == "2.3"


def test_migrate_document_2_2_result_passes_stable_2_3_validation():
    from format_factory.ubl import validate

    document = load(_invoice_bytes(version="2.2"))
    migrated, _ = migrate_document(document)

    report = validate(migrated)
    assert report.is_valid, report.diagnostics


def test_migrate_document_refuses_a_2_2_root_type_not_covered_by_the_structural_diff():
    document = load(_import_customs_declaration_2_2_ineligible_bytes())
    with pytest.raises(UblValidationError, match="ImportCustomsDeclaration"):
        migrate_document(document)


def test_migrate_document_refuses_rather_than_silently_relabels_a_2_2_document_when_the_result_would_fail_validation():
    document = load(_invoice_bytes(version="2.2", duplicate_version=True))
    with pytest.raises(UblValidationError, match="validation"):
        migrate_document(document)
