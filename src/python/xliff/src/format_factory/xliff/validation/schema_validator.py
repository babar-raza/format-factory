"""XSD conformance validation against the bundled, official XLIFF 2.1
core and module schemas.

MUST (SAL-XLIFF-OBL-078DE5F17834C232 / SAL-XLIFF-OBL-C1BB9934B09B3B70):
"XLIFF documents must be well-formed XML and valid against the core
schema with module content valid against its module schema."
Well-formedness is already enforced at parse time (reader.py). This
module supplies both remaining halves.

The bundled schemas (validation/schemas/*.xsd) are the actual OASIS-
published XLIFF 2.1 schema files, extracted byte-for-byte from the
pinned raw acquisition cache: .local/format-contracts/acquired/xliff/
src-xlf-002.bin is not spec prose -- it is a ZIP archive (confirmed by
its own "PK" magic bytes), the official XLIFF 2.1 OS schema
distribution package, containing xliff_core_2.0.xsd plus one .xsd per
standard module (Format Style, Glossary, ITS, ITS Mapping, Matches,
Metadata, Resource Data, Size and Length Restriction, Validation). Each
module schema's own <xs:import schemaLocation="xliff_core_2.0.xsd"/>
resolves automatically because all ten files are bundled together in
the same directory, unmodified relative to how OASIS ships them.

Deliberately narrow about one remaining thing: this validates XSD
structural conformance only. Schematron is not required by this
obligation's own rule_text ("valid against ... schema", not "... and its
Schematron rules"), so executing it is correctly left unattempted here --
see bundled_schematron_paths() below for why, concretely, not just in
principle.

`xmlschema` is an optional dependency (the `schema` extra in
pyproject.toml) -- imported lazily here so the rest of this package
works with no `xmlschema` installation at all.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Iterator, cast

from format_factory.core import Diagnostic, SourceLocation, ValidationReport

from ..errors import SchemaValidationUnavailable

if TYPE_CHECKING:
    import xmlschema as _xmlschema_typing

_SCHEMAS_DIR = Path(__file__).parent / "schemas"
_CORE_SCHEMA_PATH = _SCHEMAS_DIR / "xliff_core_2.0.xsd"
#: Every standard module's own schema file, bundled alongside the core.
_MODULE_SCHEMA_FILENAMES = (
    "fs.xsd",
    "glossary.xsd",
    "its.xsd",
    "itsm.xsd",
    "matches.xsd",
    "metadata.xsd",
    "resource_data.xsd",
    "size_restriction.xsd",
    "validation.xsd",
)
#: SAL-XLIFF-OBL-07A1F5F6A9B3A95F / 1405C2E94EEF25E6 / 21B94445F4216B94:
#: "the official XLIFF 2.1 schema bundle contains exactly nine Schematron
#: rule sets covering core processing constraints and the modules that
#: define Schematron constraints" -- one core plus eight of the nine
#: modules (ITS Mapping defines none of its own). Extracted byte-for-byte
#: from the same src-xlf-002.bin ZIP the module XSDs above came from --
#: this session's earlier extraction only pulled the *.xsd entries out of
#: that archive and never re-examined it for its *.sch/*.nvdl entries.
_SCHEMATRON_FILENAMES = (
    "xliff_core_2.1.sch",
    "fs.sch",
    "glossary.sch",
    "its.sch",
    "matches.sch",
    "metadata.sch",
    "resource_data.sch",
    "size_restriction.sch",
    "validation.sch",
)
#: SAL-XLIFF-OBL-191B67AD2A05CA4E / 56B240550D37E1BA: "the release package
#: supplies ... an NVDL advanced-validation dispatch artifact."
_NVDL_FILENAME = "xliff_2_advanced_validation.nvdl"


def _require_xmlschema() -> ModuleType:
    try:
        import xmlschema
    except ImportError as exc:
        raise SchemaValidationUnavailable(
            "XSD schema validation requires the optional 'xmlschema' "
            "dependency. Install it with: pip install format-factory-xliff[schema]"
        ) from exc
    return xmlschema


@lru_cache(maxsize=1)
def _load_core_schema() -> "_xmlschema_typing.XMLSchema":
    xmlschema = _require_xmlschema()
    return cast("_xmlschema_typing.XMLSchema", xmlschema.XMLSchema(str(_CORE_SCHEMA_PATH)))


@lru_cache(maxsize=1)
def _load_full_schema() -> "_xmlschema_typing.XMLSchema":
    """Core schema composed with every standard module's own schema.

    A single xmlschema.XMLSchema built from the full file list -- each
    module schema's own xs:import of the core resolves via the shared
    directory, so this is the real OASIS-defined combined grammar, not
    a hand-assembled approximation.
    """

    xmlschema = _require_xmlschema()
    paths = [str(_CORE_SCHEMA_PATH)]
    paths.extend(str(_SCHEMAS_DIR / name) for name in _MODULE_SCHEMA_FILENAMES)
    return cast("_xmlschema_typing.XMLSchema", xmlschema.XMLSchema(paths))


def _diagnostics_from_errors(errors: "Iterator[_xmlschema_typing.XMLSchemaValidationError]", code: str) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for error in errors:
        path = tuple(segment for segment in (error.path or "").split("/") if segment)
        diagnostics.append(
            Diagnostic(
                code,
                error.reason or str(error),
                location=SourceLocation(path=path) if path else None,
            )
        )
    return diagnostics


def schema_validate(source: bytes | str) -> ValidationReport:
    """Validate raw XLIFF XML `source` against the bundled core schema
    only (module extension content, if present, is not checked).

    Operates on raw XML text/bytes, independent of whether this
    package's own strict reader could load it -- a document a third
    party produced (or a hand-crafted fixture) can be checked for core
    schema conformance without first surviving this package's own
    stricter parse-time checks. Reports every violation found, not just
    the first, per this obligation's own rule_text.

    Raises `SchemaValidationUnavailable` if the optional `xmlschema`
    dependency is not installed.
    """

    schema = _load_core_schema()
    return ValidationReport(
        _diagnostics_from_errors(schema.iter_errors(source), "xliff.schema.core.invalid")
    )


def full_schema_validate(source: bytes | str) -> ValidationReport:
    """Validate raw XLIFF XML `source` against the core schema composed
    with every standard module's own schema.

    Unlike :func:`schema_validate`, this also structurally validates any
    module extension content (Glossary, Metadata, Validation, Size and
    Length Restriction, Matches, Resource Data, Format Style, ITS, ITS
    Mapping) present in the document -- the "module content valid
    against its module schema" half of this obligation's own compound
    rule_text. Reports every violation, from either the core or any
    module, in one combined report.

    Raises `SchemaValidationUnavailable` if the optional `xmlschema`
    dependency is not installed.
    """

    schema = _load_full_schema()
    return ValidationReport(
        _diagnostics_from_errors(schema.iter_errors(source), "xliff.schema.module.invalid")
    )


def bundled_module_schema_paths() -> tuple[Path, ...]:
    """The nine official module XSDs bundled with this package (Format
    Style, Glossary, ITS, ITS Mapping, Matches, Metadata, Resource Data,
    Size and Length Restriction, Validation) -- the same files
    _load_full_schema() composes with the core schema, exposed here as a
    public, path-returning accessor for a caller that wants the files
    directly rather than a loaded xmlschema.XMLSchema object.
    """
    return tuple(_SCHEMAS_DIR / name for name in _MODULE_SCHEMA_FILENAMES)


def bundled_schematron_paths() -> tuple[Path, ...]:
    """The official ISO Schematron rule sets bundled with this package: one
    core (xliff_core_2.1.sch) plus one per module that defines Schematron
    constraints of its own (eight of the nine standard modules -- ITS
    Mapping has none).

    This package does not execute them: lxml.isoschematron, the only
    Schematron engine available without a new heavyweight dependency,
    refuses every one of these nine files outright with "This
    implementation of ISO Schematron does not work with schemas using the
    'xslt2' query language" -- confirmed empirically against all nine
    files, not assumed from the core's own declared queryBinding="xslt2"
    attribute alone. Running them requires an XSLT 2.0-capable Schematron
    processor (e.g. a Java toolchain) this package does not bundle.
    Returned as paths so a caller with such a processor can use the real,
    official rule sets directly.
    """
    return tuple(_SCHEMAS_DIR / name for name in _SCHEMATRON_FILENAMES)


def bundled_nvdl_path() -> Path:
    """The official NVDL (Namespace-based Validation Dispatching Language)
    advanced-validation dispatch artifact bundled with this package --
    the document that routes a document's namespaced content to the
    correct schema/Schematron pair. Not executed by this package for the
    same reason as bundled_schematron_paths(): dispatching to Schematron
    rule sets this package cannot itself run would not add real
    validation capability.
    """
    return _SCHEMAS_DIR / _NVDL_FILENAME


__all__ = [
    "bundled_module_schema_paths",
    "bundled_nvdl_path",
    "bundled_schematron_paths",
    "full_schema_validate",
    "schema_validate",
]
