"""XLIFF-PARSE-001 -- XSD conformance against the bundled core schema.

MUST (SAL-XLIFF-OBL-078DE5F17834C232 / SAL-XLIFF-OBL-C1BB9934B09B3B70):
"XLIFF documents must be well-formed XML and valid against the core
schema with module content valid against its module schema."

The bundled schemas are the actual OASIS-published XLIFF 2.1 schema
files, extracted from the real official distribution ZIP found inside
the pinned raw acquisition cache (.local/format-contracts/acquired/
xliff/src-xlf-002.bin -- confirmed a ZIP by its own "PK" magic bytes,
not spec prose).

This file tests schema_validate() (core schema only). The composed
core+module validation (full_schema_validate(), the "module content
valid against its module schema" half) is tested separately in
test_obligation_full_module_schema_validation.py.
"""

from __future__ import annotations

import sys

import pytest

xmlschema = pytest.importorskip("xmlschema", reason="optional xmlschema dependency not installed")

from format_factory.xliff import SchemaValidationUnavailable, schema_validate  # noqa: E402
from format_factory.xliff.validation.schema_validator import _load_core_schema  # noqa: E402

_XLIFF_NS = "urn:oasis:names:tc:xliff:document:2.0"


def _document(body: str) -> bytes:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{_XLIFF_NS}" version="2.0" srcLang="en">\n'
        f'<file id="f1">{body}</file>\n'
        f"</xliff>\n"
    ).encode()


def test_a_schema_valid_document_reports_no_diagnostics() -> None:
    document = _document('<unit id="u1"><segment><source>Hello</source></segment></unit>')

    report = schema_validate(document)

    assert report.is_valid
    assert report.diagnostics == ()


def test_a_missing_required_attribute_is_flagged() -> None:
    document = _document('<unit><segment><source>Hello</source></segment></unit>')

    report = schema_validate(document)

    assert not report.is_valid
    codes = {item.code for item in report.diagnostics}
    assert codes == {"xliff.schema.core.invalid"}


def test_every_violation_is_reported_not_just_the_first() -> None:
    """"returning all diagnostics with paths rather than stopping at the
    first error" -- both the file's own missing id and the nested unit's
    own missing id must each be independently reported."""
    document = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{_XLIFF_NS}" version="2.0" srcLang="en">\n'
        f"<file>"
        f"<unit><segment><source>Hello</source></segment></unit>"
        f"</file>\n"
        f"</xliff>\n"
    ).encode()

    report = schema_validate(document)

    assert len(report.diagnostics) >= 2


def test_diagnostics_carry_a_structural_path() -> None:
    document = _document('<unit><segment><source>Hello</source></segment></unit>')

    (diagnostic,) = schema_validate(document).diagnostics

    assert diagnostic.location is not None
    assert diagnostic.location.path == ("xliff", "file", "unit")


def test_a_valid_document_with_a_target_and_multiple_units_validates_cleanly() -> None:
    document = _document(
        '<unit id="u1"><segment><source>Hello</source><target>Bonjour</target></segment></unit>'
        '<unit id="u2"><segment><source>Bye</source></segment></unit>'
    )

    assert schema_validate(document).is_valid


def test_schema_validation_unavailable_when_xmlschema_cannot_be_imported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The optional dependency degrades gracefully: importing this
    package never requires `xmlschema` at all, only calling
    schema_validate() does, and it fails with a clear, actionable
    error rather than an opaque ImportError or a crash at package
    import time."""
    _load_core_schema.cache_clear()
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
            schema_validate(b"<x/>")
    finally:
        _load_core_schema.cache_clear()


def test_the_bundled_core_schema_targets_the_core_document_namespace() -> None:
    """SAL-XLIFF-OBL-194616F7A49381E8: "The XLIFF 2.1 core XSD defines
    namespace-qualified XML element syntax for the core document
    vocabulary in urn:oasis:names:tc:xliff:document:2.0." A structural
    inventory claim about the bundled schema itself, distinct from (and
    narrower than) the runtime validation the rest of this file proves --
    but the runtime tests above already exercise real core-vocabulary
    elements (unit/segment/source/target) qualified in exactly this
    namespace, so this test names the claim explicitly rather than
    leaving it implicit."""
    schema = _load_core_schema()

    assert schema.target_namespace == _XLIFF_NS
    assert _XLIFF_NS in schema.maps.namespaces
