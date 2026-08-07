"""XSD conformance validation against the bundled XLIFF 2.0/2.1 core schema.

MUST (SAL-XLIFF-OBL-078DE5F17834C232 / SAL-XLIFF-OBL-C1BB9934B09B3B70):
"XLIFF documents must be well-formed XML and valid against the core
schema with module content valid against its module schema."
Well-formedness is already enforced at parse time (reader.py). This
module supplies the "valid against the core schema" half.

xliff_core_2.0.xsd, bundled alongside this module, is transcribed
byte-for-byte from the pinned XLIFF 2.1 specification's own Appendix
A.3 "Core XML Schema" (.local/format-contracts/acquired/xliff/
src-xliff-003.bin, lines 3230-3657) -- the spec's own words: "The schema
listed below for reading convenience is accessible at
http://docs.oasis-open.org/xliff/xliff-core/v2.1/os/schemas/xliff_core_2.1.xsd."
This is the authoritative, normative core-only schema, not fabricated
or reconstructed from memory. It imports the standard, unversioned W3C
`xml:` namespace schema (xml:lang/xml:space/xml:id), which `xmlschema`
resolves from its own bundled copy without any network access.

Deliberately narrow: this validates ONLY the core schema. Module content
(Glossary, Metadata, Validation, Size and Length Restriction, Matches,
Resource Data, Format Style, ITS) each has its own separate module
schema this function does not load or check -- composing all of them
into one combined schema (via xs:import/xs:redefine) remains a
genuinely larger, separate undertaking, not attempted here.

`xmlschema` is an optional dependency (the `schema` extra in
pyproject.toml) -- imported lazily here so the rest of this package
works with no `xmlschema` installation at all.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from format_factory.core import Diagnostic, SourceLocation, ValidationReport

from ..errors import SchemaValidationUnavailable

if TYPE_CHECKING:
    import xmlschema as _xmlschema_typing

_SCHEMA_PATH = Path(__file__).parent / "xliff_core_2.0.xsd"


@lru_cache(maxsize=1)
def _load_schema() -> "_xmlschema_typing.XMLSchema":
    try:
        import xmlschema
    except ImportError as exc:
        raise SchemaValidationUnavailable(
            "XSD schema validation requires the optional 'xmlschema' "
            "dependency. Install it with: pip install format-factory-xliff[schema]"
        ) from exc
    return xmlschema.XMLSchema(str(_SCHEMA_PATH))


def schema_validate(source: bytes | str) -> ValidationReport:
    """Validate raw XLIFF XML `source` against the bundled core schema.

    Operates on raw XML text/bytes, independent of whether this
    package's own strict reader could load it -- a document a third
    party produced (or a hand-crafted fixture) can be checked for core
    schema conformance without first surviving this package's own
    stricter parse-time checks. Reports every violation found, not just
    the first, per this obligation's own rule_text.

    Raises `SchemaValidationUnavailable` if the optional `xmlschema`
    dependency is not installed.
    """

    schema = _load_schema()
    diagnostics: list[Diagnostic] = []
    for error in schema.iter_errors(source):
        path = tuple(segment for segment in (error.path or "").split("/") if segment)
        diagnostics.append(
            Diagnostic(
                "xliff.schema.core.invalid",
                error.reason or str(error),
                location=SourceLocation(path=path) if path else None,
            )
        )
    return ValidationReport(diagnostics)


__all__ = ["schema_validate"]
