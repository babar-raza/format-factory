"""UBL-VALIDATE-001 -- one call running all five validation layers.

MUST (SAL-UBL-OBL-788B2748204338B8): "Run syntax, schema, referential,
code-list, and pluggable business-rule validation as separately reportable
layers, returning all diagnostics with paths rather than stopping at the
first error."

Before ``validate_all()``, a caller invoked ``validate()``,
``schema_validate()``, ``DocumentIndex`` methods, ``validate_code()``, and
``validate_profile()`` separately -- this obligation's own missing_behavior
named exactly that as the gap. The code-list layer here validates only
caller-supplied ``Code`` values (see ``combined.py``'s own module docstring
for why an automatic whole-document code walker is a separate, larger
undertaking, not attempted here) -- everything else runs automatically from
one source.
"""

from __future__ import annotations

from pathlib import Path

from format_factory.core import Diagnostic, Severity, ValidationReport
from format_factory.ubl import Code, CodeList, CodeListRegistry, validate_all
from format_factory.ubl.validation.profiles import ProfileValidatorRegistry

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl"


def _invoice(*, extra_header: str = "", lines: str | None = None) -> bytes:
    if lines is None:
        lines = _line("1")
    return (
        f'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" '
        f'xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}">'
        "<cbc:ID>INV-001</cbc:ID>"
        "<cbc:IssueDate>2026-01-01</cbc:IssueDate>"
        "<cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>"
        "<cbc:DocumentCurrencyCode>USD</cbc:DocumentCurrencyCode>"
        f"{extra_header}"
        '<cac:AccountingSupplierParty><cac:Party><cbc:WebsiteURI>http://x.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingSupplierParty>"
        '<cac:AccountingCustomerParty><cac:Party><cbc:WebsiteURI>http://y.com</cbc:WebsiteURI>'
        "</cac:Party></cac:AccountingCustomerParty>"
        '<cac:LegalMonetaryTotal><cbc:PayableAmount currencyID="USD">1.00</cbc:PayableAmount>'
        "</cac:LegalMonetaryTotal>"
        f"{lines}"
        "</Invoice>"
    ).encode()


def _line(line_id: str) -> str:
    return (
        "<cac:InvoiceLine>"
        f"<cbc:ID>{line_id}</cbc:ID>"
        '<cbc:InvoicedQuantity unitCode="KGM">1</cbc:InvoicedQuantity>'
        '<cbc:LineExtensionAmount currencyID="USD">1.00</cbc:LineExtensionAmount>'
        "<cac:Item><cbc:Name>Widget</cbc:Name></cac:Item>"
        '<cac:Price><cbc:PriceAmount currencyID="USD">1.00</cbc:PriceAmount></cac:Price>'
        "</cac:InvoiceLine>"
    )


def test_a_fully_valid_document_passes_every_layer_with_zero_diagnostics() -> None:
    report = validate_all(_invoice())

    assert report.is_valid is True
    assert report.diagnostics == ()


def test_malformed_xml_is_reported_by_the_syntax_layer_not_a_raise() -> None:
    report = validate_all(b"not xml at all")

    assert report.is_valid is False
    codes = [d.code for d in report.diagnostics]
    assert "ubl.syntax.invalid" in codes


def test_a_nonexistent_source_is_reported_not_a_raise() -> None:
    report = validate_all(str(SAMPLES / "does-not-exist.xml"))

    assert report.is_valid is False
    assert report.diagnostics[0].code == "ubl.source.unreadable"


def test_a_schema_violation_is_reported_by_the_schema_layer() -> None:
    # CustomizationID is a real field, but placed out of its schema-declared
    # position -- this is a genuine XSD ordering violation, not garbage input.
    report = validate_all(_invoice(extra_header="<cbc:CustomizationID>urn:x</cbc:CustomizationID>"))

    assert report.is_valid is False
    codes = [d.code for d in report.diagnostics]
    assert "ubl.schema.invalid" in codes


def test_a_duplicate_line_id_is_reported_by_the_referential_layer() -> None:
    report = validate_all(_invoice(lines=_line("1") + _line("1")))

    assert report.is_valid is False
    codes = [d.code for d in report.diagnostics]
    assert "ubl.referential.duplicate_line_id" in codes
    finding = next(d for d in report.diagnostics if d.code == "ubl.referential.duplicate_line_id")
    assert "InvoiceLine[0]" in finding.message
    assert "InvoiceLine[1]" in finding.message


def test_an_out_of_list_code_is_reported_by_the_code_list_layer_when_supplied() -> None:
    registry = CodeListRegistry()
    registry.register(CodeList(list_id="UNCL1001", values=frozenset({"380"})))
    bad_code = Code(value="999", list_id="UNCL1001")

    report = validate_all(_invoice(), code_registry=registry, used_codes=(bad_code,))

    assert report.is_valid is False
    codes = [d.code for d in report.diagnostics]
    assert "ubl.codelist.invalid" in codes


def test_an_in_list_code_produces_no_code_list_diagnostic() -> None:
    registry = CodeListRegistry()
    registry.register(CodeList(list_id="UNCL1001", values=frozenset({"380"})))
    good_code = Code(value="380", list_id="UNCL1001")

    report = validate_all(_invoice(), code_registry=registry, used_codes=(good_code,))

    assert report.is_valid is True


def test_the_code_list_layer_is_silently_skipped_when_no_registry_is_supplied() -> None:
    # Honest scope: no automatic document-wide code walker exists, so
    # omitting a registry must not fabricate a pass/fail verdict for codes
    # this call never looked at.
    report = validate_all(_invoice())

    codes = [d.code for d in report.diagnostics]
    assert "ubl.codelist.invalid" not in codes


def test_a_registered_profile_validator_runs_when_the_customization_id_matches() -> None:
    def rejects_everything(document: object) -> ValidationReport:
        return ValidationReport(
            [Diagnostic("custom.rule.failed", "business rule X violated", severity=Severity.ERROR)]
        )

    registry = ProfileValidatorRegistry().register("urn:my:profile", rejects_everything)
    report = validate_all(
        _invoice(extra_header="<cbc:CustomizationID>urn:my:profile</cbc:CustomizationID>"),
        profile_registry=registry,
    )

    codes = [d.code for d in report.diagnostics]
    assert "custom.rule.failed" in codes


def test_no_profile_validator_runs_when_the_document_declares_no_customization_id() -> None:
    def rejects_everything(document: object) -> ValidationReport:
        return ValidationReport(
            [Diagnostic("custom.rule.failed", "business rule X violated", severity=Severity.ERROR)]
        )

    registry = ProfileValidatorRegistry().register("urn:my:profile", rejects_everything)
    report = validate_all(_invoice(), profile_registry=registry)

    codes = [d.code for d in report.diagnostics]
    assert "custom.rule.failed" not in codes


def test_multiple_layer_violations_are_all_reported_together_not_just_the_first() -> None:
    # syntax passes, but schema + referential both fail on the same input --
    # the obligation's own "returning all diagnostics... rather than
    # stopping at the first error" requirement, proven across layers.
    report = validate_all(
        _invoice(
            extra_header="<cbc:CustomizationID>urn:x</cbc:CustomizationID>",
            lines=_line("1") + _line("1"),
        )
    )

    codes = {d.code for d in report.diagnostics}
    assert "ubl.schema.invalid" in codes
    assert "ubl.referential.duplicate_line_id" in codes
