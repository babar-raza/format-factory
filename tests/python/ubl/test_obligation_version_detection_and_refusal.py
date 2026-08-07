"""UBL-UPGRADE-001 against the shipped namespace.

MUST (SAL-UBL-OBL-7B16479ACBBC8EFC): "Detect older specification versions
where practical; migrate via explicit transforms producing a migration
report; never label a document as the target version without structural
migration and validation."

Before this slice: NO test file was mapped to this capability at all,
even though the underlying detection and refusal mechanisms were already
real and correct -- confirmed directly: UblDocument.declared_version
(model/document.py) already reads whatever cbc:UBLVersionID a source file
actually declares (proven for older versions like "2.0"/"2.1" by
test_obligation_detected_declared_version.py under UBL-LIFECYCLE-001,
cited here as a cross-capability duplicate of the same underlying fact),
and validator.py's own version check (line ~77) already refuses a
document declaring anything other than "2.3" with a clear
ubl.version.unsupported diagnostic -- proven here directly through
validate(), which UBL-LIFECYCLE-001's own test file only exercises
through dumps()'s separate write-time refusal, not through validate()
itself.

"Migrate via explicit transforms producing a migration report" remains
genuinely unbuilt: no transform infrastructure exists for any UBL version
pair, and building one would require deep knowledge of what changed
between UBL 2.0/2.1/2.2/2.3 schemas -- a substantial, separate investigation
not attempted here. This file therefore proves the "detect... and never
label a document as the target version without structural migration"
half only, and the obligation stays honestly partial.
"""

from __future__ import annotations

from format_factory.ubl import loads, validate

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"


def _invoice(version: str) -> bytes:
    return (
        f'<Invoice xmlns="{NAMESPACE}" xmlns:cbc="{CBC}">'
        f"<cbc:UBLVersionID>{version}</cbc:UBLVersionID>"
        "<cbc:ID>INV-001</cbc:ID>"
        "</Invoice>"
    ).encode()


def test_an_older_declared_version_is_detected_not_silently_accepted_as_current() -> None:
    """"Detect older specification versions" -- the document's own declared
    version is read as what it actually says, "2.0", never coerced or
    silently reported as this package's target, "2.3"."""
    document = loads(_invoice("2.0"))

    assert document.declared_version == "2.0"
    assert document.declared_version != "2.3"


def test_validate_refuses_an_older_version_with_a_clear_diagnostic() -> None:
    """"never label a document as the target version without structural
    migration and validation" -- validate() itself (not only dumps())
    reports an older-version document as invalid, with a diagnostic
    naming the version mismatch, rather than silently treating it as a
    valid 2.3 document."""
    document = loads(_invoice("2.0"))

    report = validate(document)

    assert report.is_valid is False
    assert any(item.code == "ubl.version.unsupported" for item in report.diagnostics)


def test_validate_accepts_the_current_target_version() -> None:
    """Control: the refusal is version-specific, not unconditional."""
    document = loads(_invoice("2.3"))

    report = validate(document)

    assert report.is_valid is True


def test_a_different_older_version_is_also_detected_and_refused() -> None:
    document = loads(_invoice("2.1"))

    assert document.declared_version == "2.1"
    report = validate(document)
    assert report.is_valid is False
    assert any(item.code == "ubl.version.unsupported" for item in report.diagnostics)
