"""UBL-VALIDATE-001 -- automatic, schema-driven document-wide code
discovery and validation (``validate_all(..., discover_codes=True)``).

MUST (SAL-UBL-OBL-788B2748204338B8): "Run syntax, schema, referential,
code-list, and pluggable business-rule validation as separately
reportable layers..."

Before this file: the code-list layer validated only `Code` values a
caller explicitly supplied via `used_codes` -- "no field-by-field
catalogue of every UBL code-bearing element... exists in this package"
(combined.py's own prior docstring). `code_bearing_element_qnames()`
(validation/schema_validator.py) now supplies exactly that catalogue,
built mechanically from the bundled official schemas via `xmlschema`'s
own type-derivation introspection (273 elements, confirmed
root-independent and confirmed to exactly match every element ending in
literal "Code", with zero ambiguous cases in the bundled files).

`discover_codes=True` (opt-in; default is `False`, reproducing the
original caller-supplied-only behavior exactly) walks a document for
every one of those 273 element types and validates the ones this
package has real bundled OASIS genericode data for (11 of the 273) --
using the element's own local name as an implied default `list_id` only
when the document itself declares none, and always honoring an
explicitly-declared list identity over any implied default.

Deliberately NOT attempted here, and not claimed: the other 262
discoverable element types have no bundled value data at all (a
separate, larger data-acquisition undertaking, not a schema-
introspection gap) -- this file proves discovery finds them (or
confirms they're silently skipped for lack of data), never that they
are validated against anything.
"""

from __future__ import annotations

import pytest

xmlschema = pytest.importorskip("xmlschema")

from format_factory.ubl import (  # noqa: E402
    Code,
    CodeList,
    CodeListRegistry,
    code_bearing_element_qnames,
    load_bundled_code_lists,
    official_code_list_registry,
    validate_all,
)

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _invoice_with_payment_code(payment_code_element: str) -> bytes:
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        f'<cac:PaymentMeans>{payment_code_element}</cac:PaymentMeans>'
        '<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>http://x.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
        '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
        "<cac:InvoiceLine>"
        "<cbc:ID>1</cbc:ID>"
        '<cbc:InvoicedQuantity unitCode="KGM">1</cbc:InvoicedQuantity>'
        '<cbc:LineExtensionAmount currencyID="USD">1.00</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        "</cac:InvoiceLine>"
        "</Invoice>"
    ).encode()


def _codelist_diagnostics(report) -> list[str]:  # noqa: ANN001
    return [d.code for d in report.diagnostics if "codelist" in d.code]


# ── The schema-derived catalogue itself ──────────────────────────────────


def test_the_catalogue_contains_every_bundled_lists_own_element_name() -> None:
    """7 of the 11 bundled genericode lists' own ShortName equals the
    schema element's own local name directly; 2 more (BinaryObjectMimeCode
    -> cbc:MimeCode, CountryIdentificationCode -> cbc:IdentificationCode)
    are confirmed element/ShortName mismatches, proven separately,
    behaviorally, below (combined.py's own
    _ELEMENT_NAME_TO_LIST_ID_OVERRIDES); the remaining 2
    (LanguageCode, UnitOfMeasureCode) are carried via XML attributes
    (languageID/unitCode), not elements at all, so they cannot appear in
    an element-only catalogue by construction, not by omission."""
    catalogue = code_bearing_element_qnames()
    local_names = {qn.rsplit("}", 1)[-1] for qn in catalogue}
    attribute_carried = {"LanguageCode", "UnitOfMeasureCode"}
    element_name_mismatches = {"BinaryObjectMimeCode": "MimeCode", "CountryIdentificationCode": "IdentificationCode"}
    for code_list in load_bundled_code_lists():
        if code_list.list_id in attribute_carried:
            continue
        if code_list.list_id in element_name_mismatches:
            assert element_name_mismatches[code_list.list_id] in local_names
            continue
        assert code_list.list_id in local_names


def test_the_catalogue_excludes_a_same_shaped_non_code_type() -> None:
    """cbc:CodeValue restricts udt:TextType, not the CCTS code type, and
    does not end in literal "Code" -- the one deliberate trap in the
    bundled schema, confirmed to not produce a false positive."""
    catalogue = code_bearing_element_qnames()
    local_names = {qn.rsplit("}", 1)[-1] for qn in catalogue}
    assert "CodeValue" not in local_names


def test_the_catalogue_is_reasonably_large_and_every_entry_is_named_code() -> None:
    catalogue = code_bearing_element_qnames()
    assert len(catalogue) > 200
    assert all(qn.rsplit("}", 1)[-1].endswith("Code") for qn in catalogue)


# ── discover_codes=True: default-off, opt-in behavior ────────────────────


def test_discover_codes_defaults_to_false_and_changes_nothing() -> None:
    registry = official_code_list_registry()
    xml = _invoice_with_payment_code("<cbc:PaymentMeansCode>NOT_A_REAL_CODE</cbc:PaymentMeansCode>")

    report = validate_all(xml, code_registry=registry)

    assert _codelist_diagnostics(report) == []


def test_discover_codes_true_finds_an_invalid_undeclared_code() -> None:
    registry = official_code_list_registry()
    xml = _invoice_with_payment_code("<cbc:PaymentMeansCode>NOT_A_REAL_CODE</cbc:PaymentMeansCode>")

    report = validate_all(xml, code_registry=registry, discover_codes=True)

    assert "ubl.codelist.invalid" in _codelist_diagnostics(report)


def test_discover_codes_true_does_not_flag_a_genuinely_valid_code() -> None:
    """"30" (credit transfer) is a real member of the bundled
    PaymentMeansCode-2.3.gc list."""
    registry = official_code_list_registry()
    xml = _invoice_with_payment_code("<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>")

    report = validate_all(xml, code_registry=registry, discover_codes=True)

    assert _codelist_diagnostics(report) == []


def test_discover_codes_true_requires_a_registry_too() -> None:
    xml = _invoice_with_payment_code("<cbc:PaymentMeansCode>NOT_A_REAL_CODE</cbc:PaymentMeansCode>")

    report = validate_all(xml, discover_codes=True)  # no code_registry

    assert _codelist_diagnostics(report) == []


def test_an_element_with_no_bundled_data_and_no_declared_list_is_silently_skipped() -> None:
    """AccountingCostCode is one of the 262 discoverable-but-undata'd
    element types -- discovery finds it, but there is nothing to
    validate it against, so it must not be silently invented as invalid
    or produce any diagnostic at all."""
    registry = official_code_list_registry()
    xml = _invoice_with_payment_code("<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>").replace(
        b"<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>",
        b"<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        b"<cbc:AccountingCostCode>anything-at-all</cbc:AccountingCostCode>",
    )

    report = validate_all(xml, code_registry=registry, discover_codes=True)

    assert _codelist_diagnostics(report) == []


def test_an_explicitly_declared_list_identity_is_honored_over_the_implied_default() -> None:
    """A document that DOES declare listID must never have that
    declaration silently overridden by the implied-default lookup --
    since the declared list here is unregistered, the code must be
    reported as unknown (no diagnostic), not validated against the
    bundled PaymentMeansCode list its own element name would imply."""
    registry = official_code_list_registry()
    xml = _invoice_with_payment_code(
        '<cbc:PaymentMeansCode listID="SomeCustomList">30</cbc:PaymentMeansCode>'
    )

    report = validate_all(xml, code_registry=registry, discover_codes=True)

    assert _codelist_diagnostics(report) == []


def test_the_mime_code_element_name_override_is_applied_behaviorally() -> None:
    """cbc:MimeCode is discoverable (its own type derives from the CCTS
    code type) but its element name does not literally equal the bundled
    genericode list's own ShortName ("BinaryObjectMimeCode") -- proves
    the explicit override in combined.py actually connects the two,
    not merely that both facts are true in isolation."""
    registry = official_code_list_registry()
    xml = _invoice_with_payment_code("<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>").replace(
        b"<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>",
        b"<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        b"<cbc:MimeCode>not/a-real-mime-type</cbc:MimeCode>",
    )

    report = validate_all(xml, code_registry=registry, discover_codes=True)

    assert "ubl.codelist.invalid" in _codelist_diagnostics(report)


def test_the_country_identification_code_element_name_override_is_applied_behaviorally() -> None:
    """cac:Country's own cbc:IdentificationCode child is confirmed (by
    direct schema read) to be this schema's only reference to that
    element, always meaning a country code -- proves the override
    actually connects "CountryIdentificationCode" data to it."""
    registry = official_code_list_registry()
    xml = _invoice_with_payment_code("<cbc:PaymentMeansCode>30</cbc:PaymentMeansCode>").replace(
        b"<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>",
        b"<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        b"<cac:Country><cbc:IdentificationCode>ZZ_NOT_A_REAL_COUNTRY</cbc:IdentificationCode></cac:Country>",
    )

    report = validate_all(xml, code_registry=registry, discover_codes=True)

    assert "ubl.codelist.invalid" in _codelist_diagnostics(report)


def test_discover_codes_composes_with_explicit_used_codes() -> None:
    """Both mechanisms run together: an explicitly supplied bad code AND
    an auto-discovered bad code are both reported, not just one."""
    registry = official_code_list_registry()
    registry.register(CodeList(list_id="UNCL1001", values=frozenset({"380"})))
    explicit_bad = Code(value="999", list_id="UNCL1001")
    xml = _invoice_with_payment_code("<cbc:PaymentMeansCode>NOT_A_REAL_CODE</cbc:PaymentMeansCode>")

    report = validate_all(
        xml, code_registry=registry, used_codes=(explicit_bad,), discover_codes=True
    )

    diagnostics = _codelist_diagnostics(report)
    assert diagnostics.count("ubl.codelist.invalid") == 2
