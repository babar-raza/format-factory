"""Unified, all-layers validation entry point.

SAL-UBL-OBL-788B2748204338B8 (UBL-VALIDATE-001): "Run syntax, schema,
referential, code-list, and pluggable business-rule validation as
separately reportable layers, returning all diagnostics with paths rather
than stopping at the first error."

Before this module, a caller had to invoke each layer separately:
``validate()`` for the structural chassis, ``schema_validate()`` for XSD
conformance, ``DocumentIndex`` methods for referential checks,
``validate_code()`` per code value, and ``validate_profile()`` for
pluggable business rules. ``validate_all()`` runs all five from one call,
against one source, collecting every layer's diagnostics into a single
report -- never stopping at the first error, per the obligation's own
wording.

**Honest scope note on the code-list layer.** ``used_codes`` (always
available) validates exactly the ``Code`` values a caller supplies --
explicit about what it does and does not cover.

FF6-UBL-VALIDATE-DISCOVERED-CODES-001 adds ``discover_codes=True`` (opt
-in; default behavior is byte-for-byte unchanged): walks the document for
every element whose own type derives from the CCTS root code type
(``schema_validator.code_bearing_element_qnames`` -- 273 such elements
across the whole bundled schema graph, root-independent, confirmed
directly against the real schemas), and validates each one this package
has real data for. A document rarely declares ``listID``/
``listAgencyID``/``listVersionID`` explicitly (confirmed against this
package's own bundled official Invoice.xml sample: 5 of 6 code elements
declare none) -- for 9 of the 11 element types this package bundles
genuine OASIS genericode data for (``model.genericode.
load_bundled_code_lists``; 7 by the element's own local name matching
the list's ShortName directly, 2 more via ``_ELEMENT_NAME_TO_LIST_ID_
OVERRIDES`` for a confirmed element/ShortName mismatch), an undeclared
code is validated against that list as an implied default; a document
that DOES declare list identity explicitly is always honored over any
implied default. The remaining 2 bundled lists (LanguageCode,
UnitOfMeasureCode) are carried via XML attributes
(``languageID``/``unitCode``), not separate elements at all -- a
genuinely different discovery mechanism this element-only catalogue
does not attempt; see ``_ELEMENT_NAME_TO_LIST_ID_OVERRIDES``'s own
comment for the full citation trail.

This closes real, disclosed depth, not the whole obligation: 262 of the
273 discoverable element types have no bundled value data at all --
sourcing more official code lists (UNTDID, additional ISO/UN registries)
is a separate data-acquisition undertaking this does not attempt, and
attribute-carried codes need a separate walker this does not build.
Discovering that an element IS code-bearing (a schema-introspection
fact) and knowing what values it may legally hold (a data-availability
fact) are kept honestly distinct throughout.
"""

from __future__ import annotations

from format_factory.core import BinarySource, Diagnostic, ResourceLimits, Severity, ValidationReport

from ..codec import loads
from ..codec.reader.reader import _read_source
from ..errors import SchemaValidationUnavailable, UblError
from ..model import (
    Code,
    CodeListRegistry,
    UblDocument,
    code_of,
    load_bundled_code_lists,
    local_name,
    validate_code,
)
from ..model.query import DocumentIndex
from ..security import effective_limits
from .profiles import ProfileValidatorRegistry, validate_profile
from .schema_validator import code_bearing_element_qnames, schema_validate
from .validator import validate


def _referential_diagnostics(document: UblDocument) -> list[Diagnostic]:
    index = DocumentIndex(document.root)
    diagnostics: list[Diagnostic] = []
    for duplicate in index.duplicate_line_ids():
        paths = ", ".join(".".join(str(part) for part in match.path) for match in duplicate.matches)
        diagnostics.append(
            Diagnostic(
                "ubl.referential.duplicate_line_id",
                f"line identifier {duplicate.identifier!r} is not unique, found at: {paths}",
                severity=Severity.ERROR,
            )
        )
    return diagnostics


def _code_list_diagnostics(
    registry: CodeListRegistry | None, used_codes: tuple[Code, ...]
) -> list[Diagnostic]:
    if registry is None:
        return []
    diagnostics: list[Diagnostic] = []
    for code in used_codes:
        result = validate_code(registry, code)
        if result.is_valid is False:
            diagnostics.append(
                Diagnostic(
                    "ubl.codelist.invalid",
                    f"code {code.value!r} (list {code.list_id!r}): {result.detail}",
                    severity=Severity.ERROR,
                )
            )
    return diagnostics


#: For 7 of the 11 bundled lists, the genericode file's own
#: Identification/ShortName equals the schema element's own local name
#: (e.g. list "PaymentMeansCode" describes element cbc:PaymentMeansCode)
#: -- confirmed directly for all 11, not assumed. Two more are
#: discoverable but under a different element name, confirmed by direct
#: schema read: "BinaryObjectMimeCode" describes element cbc:MimeCode
#: (UBL-CommonBasicComponents-2.3.xsd:624), and "CountryIdentificationCode"
#: describes element cbc:IdentificationCode (line 468 of the same file),
#: used exclusively inside cac:CountryType (confirmed to be its only
#: reference anywhere in the common schemas, so the mapping is safe
#: without further per-context disambiguation). The remaining 2 bundled
#: lists -- LanguageCode and UnitOfMeasureCode -- are NOT element-based
#: at all: their own values are carried via the `languageID`/`unitCode`
#: XML ATTRIBUTES on TextType/MeasureType-typed elements (CCTS
#: convention), not a separate global `<cbc:LanguageCode>`/
#: `<cbc:UnitOfMeasureCode>` element -- confirmed directly
#: (BDNDR-CCTS_CCT_SchemaModule-1.1.xsd's own `languageID`/`unitCode`
#: attribute declarations). Attribute-carried codes are a genuinely
#: different discovery mechanism `code_bearing_element_qnames` (element
#: -only) does not attempt; disclosed, not force-mapped here.
_ELEMENT_NAME_TO_LIST_ID_OVERRIDES: dict[str, str] = {
    "MimeCode": "BinaryObjectMimeCode",
    "IdentificationCode": "CountryIdentificationCode",
}


def _implied_bundled_defaults() -> dict[str, tuple[str, str | None, str | None]]:
    """Local element name -> (list_id, agency_id, version) for exactly the
    bundled official lists this package has data for. Rebuilt each call
    -- `load_bundled_code_lists()` itself parses small local files with
    no I/O cost worth caching across a single `validate_all()` call."""
    by_list_id = {
        code_list.list_id: (code_list.list_id, code_list.agency_id, code_list.version)
        for code_list in load_bundled_code_lists()
    }
    result = dict(by_list_id)
    for element_name, list_id in _ELEMENT_NAME_TO_LIST_ID_OVERRIDES.items():
        if list_id in by_list_id:
            result[element_name] = by_list_id[list_id]
    return result


def _discovered_code_diagnostics(
    document: UblDocument, registry: CodeListRegistry
) -> list[Diagnostic]:
    """Walk every element in `document` whose own type is schema-derived
    from the CCTS code type, and validate the ones this package has real
    data for -- see this module's own docstring for exactly what this
    does and does not cover."""
    code_qnames = code_bearing_element_qnames()
    implied_defaults = _implied_bundled_defaults()
    diagnostics: list[Diagnostic] = []
    for node in document.root.iter():
        if node.qname not in code_qnames:
            continue
        code = code_of(node)
        if code.list_id is None:
            implied = implied_defaults.get(local_name(node.qname))
            if implied is None:
                continue  # discoverable, but no bundled data and no declared list -- nothing to check
            list_id, agency_id, version = implied
            code = Code(code.value, list_id=list_id, list_agency_id=agency_id, list_version_id=version)
        result = validate_code(registry, code)
        if result.is_valid is False:
            diagnostics.append(
                Diagnostic(
                    "ubl.codelist.invalid",
                    f"{local_name(node.qname)} {code.value!r} (list {code.list_id!r}): "
                    f"{result.detail}",
                    severity=Severity.ERROR,
                )
            )
    return diagnostics


def validate_all(
    source: BinarySource,
    *,
    code_registry: CodeListRegistry | None = None,
    used_codes: tuple[Code, ...] = (),
    discover_codes: bool = False,
    profile_registry: ProfileValidatorRegistry | None = None,
    limits: ResourceLimits | None = None,
) -> ValidationReport:
    """Run every validation layer against `source`, returning one combined report.

    Layers, in the order this function runs them (matching the obligation's
    own enumeration): syntax (can the source be parsed at all), schema (XSD
    conformance against the bundled maindoc schema), referential (duplicate
    line identifiers), code-list (caller-supplied codes, plus -- when
    `discover_codes=True` and `code_registry` is given -- every
    schema-discoverable code-bearing element this package has bundled data
    for; see this module's own docstring), pluggable business-rule (a
    caller-registered profile validator, if one matches the document's own
    customization ID).

    `discover_codes` defaults to `False`: passing neither it nor
    `used_codes` reproduces this function's original code-list behavior
    exactly (empty code-list diagnostics), unchanged.

    A source that fails to parse at all returns immediately with a single
    FATAL diagnostic -- the remaining layers have nothing to run against.
    Every other layer's failures are collected together; this function
    never raises for malformed input.
    """

    selected_limits = effective_limits(limits)
    try:
        raw = _read_source(source, selected_limits)
    except UblError as exc:
        return ValidationReport(
            [Diagnostic("ubl.source.unreadable", str(exc), severity=Severity.FATAL)]
        )

    diagnostics: list[Diagnostic] = []
    try:
        document: UblDocument | None = loads(raw, limits=selected_limits)
    except UblError as exc:
        diagnostics.append(
            Diagnostic("ubl.syntax.invalid", str(exc), severity=Severity.FATAL)
        )
        document = None

    if document is not None:
        diagnostics.extend(validate(document, limits=limits).diagnostics)
        diagnostics.extend(_referential_diagnostics(document))

    try:
        diagnostics.extend(schema_validate(raw).diagnostics)
    except SchemaValidationUnavailable:
        pass
    except UblError as exc:
        # schema_validate() detects the root element itself from `raw`
        # (independent of the syntax layer's own `loads()` call above) and
        # can fail that detection on the same malformed input the syntax
        # layer already reported -- report it under the schema layer's own
        # diagnostic code rather than letting a second parse attempt raise.
        diagnostics.append(
            Diagnostic("ubl.schema.unreadable", str(exc), severity=Severity.ERROR)
        )

    diagnostics.extend(_code_list_diagnostics(code_registry, used_codes))
    if discover_codes and document is not None and code_registry is not None:
        try:
            diagnostics.extend(_discovered_code_diagnostics(document, code_registry))
        except SchemaValidationUnavailable:
            pass

    if document is not None and profile_registry is not None:
        profile_report = validate_profile(document, profile_registry)
        if profile_report is not None:
            diagnostics.extend(profile_report.diagnostics)

    return ValidationReport(diagnostics)


__all__ = ["validate_all"]
