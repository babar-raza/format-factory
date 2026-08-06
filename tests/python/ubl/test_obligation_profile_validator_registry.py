"""UBL-PROFILE-001 -- pluggable profile-specific validator registry.

MUST (SAL-UBL-OBL-7D0855CD163E1EFD): "Allow profile-specific validators to
be registered; never claim profile conformance without the installed
ruleset passing."

required_tests: "Profile ruleset plug-in fixture: verdicts scoped to the
profile and absent when not installed."

Before this slice, no mechanism existed anywhere in this codebase for a
caller to register a validator for a specific UBL customization profile
(EN 16931, PEPPOL BIS, or any other) -- validate() checks only the fixed
structural chassis, on purpose (see validation/profiles.py's module
docstring). This file proves the new plug-in registry: a validator
registered for one customization ID never runs against a document
declaring a different one, and validate_profile() returns None -- not an
empty/passing report -- when nothing is installed for the document's own
customization ID, so a caller cannot mistake "nothing checked" for
"checked and clean."
"""

from __future__ import annotations

import pytest

from format_factory.core import Diagnostic, Severity, ValidationReport
from format_factory.ubl import (
    ROOT_CLASSES,
    ProfileValidatorRegistry,
    XmlNode,
    loads,
    validate_profile,
)

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
Invoice = ROOT_CLASSES["Invoice"]

EN16931 = "urn:cen.eu:en16931:2017"
PEPPOL = "urn:fdc:peppol.eu:2017:poacc:billing:3.0"


def _invoice(*, customization: str | None = None) -> bytes:
    parts = [f'<Invoice xmlns="{NAMESPACE}" xmlns:cbc="{CBC}">']
    if customization is not None:
        parts.append(f"<cbc:CustomizationID>{customization}</cbc:CustomizationID>")
    parts.append("<cbc:ID>INV-001</cbc:ID></Invoice>")
    return "".join(parts).encode()


def _always_passes(document) -> ValidationReport:
    return ValidationReport(())


def _always_fails(document) -> ValidationReport:
    return ValidationReport(
        [Diagnostic("test.profile.rejected", "rejected by fixture validator", Severity.ERROR)]
    )


# ── registration is immutable and returns a new registry ───────────────────


def test_a_fresh_registry_is_empty() -> None:
    registry = ProfileValidatorRegistry()

    assert len(registry) == 0
    assert registry.installed_for(EN16931) is None


def test_register_returns_a_new_registry_leaving_the_original_untouched() -> None:
    original = ProfileValidatorRegistry()
    updated = original.register(EN16931, _always_passes)

    assert len(original) == 0
    assert len(updated) == 1
    assert original.installed_for(EN16931) is None
    assert updated.installed_for(EN16931) is _always_passes


def test_re_registering_the_same_id_replaces_it() -> None:
    registry = (
        ProfileValidatorRegistry()
        .register(EN16931, _always_passes)
        .register(EN16931, _always_fails)
    )

    assert len(registry) == 1
    assert registry.installed_for(EN16931) is _always_fails


def test_multiple_distinct_ids_coexist() -> None:
    registry = (
        ProfileValidatorRegistry()
        .register(EN16931, _always_passes)
        .register(PEPPOL, _always_fails)
    )

    assert len(registry) == 2
    assert registry.installed_for(EN16931) is _always_passes
    assert registry.installed_for(PEPPOL) is _always_fails


def test_registering_an_empty_id_is_refused() -> None:
    with pytest.raises(ValueError, match="customization_id"):
        ProfileValidatorRegistry().register("", _always_passes)


# ── validate_profile: scoped to the document's own customization ID ────────


def test_verdict_is_scoped_to_the_documents_own_customization_id() -> None:
    document = loads(_invoice(customization=EN16931))
    registry = (
        ProfileValidatorRegistry()
        .register(EN16931, _always_passes)
        .register(PEPPOL, _always_fails)
    )

    report = validate_profile(document, registry)

    assert report is not None
    assert report.is_valid


def test_a_registered_validator_for_a_different_id_never_runs() -> None:
    """The clearest proof of scoping: register only a failing validator for
    a DIFFERENT customization ID than the document declares, and confirm
    the document is untouched by it (no report at all, not a coincidental
    pass)."""
    document = loads(_invoice(customization=EN16931))
    registry = ProfileValidatorRegistry().register(PEPPOL, _always_fails)

    report = validate_profile(document, registry)

    assert report is None


def test_a_failing_installed_ruleset_is_reported_not_silently_passed() -> None:
    """"Never claim profile conformance without the installed ruleset
    passing" -- the registry must not soften or discard a real failure."""
    document = loads(_invoice(customization=EN16931))
    registry = ProfileValidatorRegistry().register(EN16931, _always_fails)

    report = validate_profile(document, registry)

    assert report is not None
    assert not report.is_valid
    assert any(item.code == "test.profile.rejected" for item in report.diagnostics)


# ── Absent when not installed: None, never an empty "passing" report ───────


def test_no_verdict_when_nothing_is_registered_at_all() -> None:
    document = loads(_invoice(customization=EN16931))
    registry = ProfileValidatorRegistry()

    assert validate_profile(document, registry) is None


def test_no_verdict_when_the_document_declares_no_customization_id() -> None:
    document = loads(_invoice())
    registry = ProfileValidatorRegistry().register(EN16931, _always_passes)

    assert validate_profile(document, registry) is None


def test_no_verdict_for_a_freshly_built_document_with_no_customization_id() -> None:
    document = Invoice.build(children=(XmlNode.create(f"{{{CBC}}}ID", text="INV-1"),))
    registry = ProfileValidatorRegistry().register(EN16931, _always_passes)

    assert validate_profile(document, registry) is None
