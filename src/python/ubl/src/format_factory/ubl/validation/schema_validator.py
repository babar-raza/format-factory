"""XSD conformance validation against the bundled, official UBL 2.3 schemas.

The obligations this module addresses repeatedly named "full schema and
cardinality validation across every UBL complexType" and "full element-
order validation across every UBL complexType" as a "genuinely large,
separate undertaking, out of the full UBL 2.3 schema's ~91 root document
types" -- correctly so, since building an independent, hand-written
structural validator matching all 91 root types' own real schemas from
scratch would be exactly that. Composing the REAL schemas the OASIS
distribution itself ships is a fundamentally different, much smaller task.

The bundled schemas (validation/schemas/{common,maindoc}/*.xsd) are the
actual OASIS-published UBL 2.3 schema files, extracted byte-for-byte from
the pinned raw acquisition cache: .local/format-contracts/acquired/ubl/
src-ubl-002.bin is not spec prose -- it is the official UBL 2.3
distribution ZIP (already used once this session to bundle the official
genericode code lists), containing xsd/common/ (15 shared component
schemas: CommonAggregateComponents, CommonBasicComponents, etc.) and
xsd/maindoc/ (91 root-document-type schemas, one per document this
package's own ROOT_CLASSES models -- Invoice, CreditNote, DespatchAdvice,
and so on), each importing the common schemas via a plain relative path
that resolves automatically because every file is bundled together,
unmodified, in the same directory structure exactly as OASIS ships them.

XSD sequence validation inherently checks cardinality AND element order
together in one pass (an out-of-order or over-repeated child is
structurally the same kind of violation to an XSD validator) -- this is
not two separate features bolted together, it is what "valid against the
schema" has always meant.

Deliberately narrow about what this does NOT do: it validates raw XML
structure only, independent of this package's own typed object model (so
cac:Attachment, which this package's typed model does not represent, is
still fully checked here, since validation operates on the XML directly).
It does not make the WRITER auto-reorder elements into schema-valid order
regardless of construction order -- that remains a separate, genuinely
unbuilt capability (UBL-WRITE-001's own "independent of mutation order"
clause).

`xmlschema` is an optional dependency (the `schema` extra in
pyproject.toml) -- imported lazily here so the rest of this package works
with no `xmlschema` installation at all.
"""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, cast

from format_factory.core import Diagnostic, SourceLocation, ValidationReport

from .._generated.root_catalog import ROOT_NAME_SET
from ..errors import SchemaValidationUnavailable, UblParseError

if TYPE_CHECKING:
    import xmlschema as _xmlschema_typing

_SCHEMAS_DIR = Path(__file__).parent / "schemas"
_MAINDOC_DIR = _SCHEMAS_DIR / "maindoc"


def _require_xmlschema() -> ModuleType:
    try:
        import xmlschema
    except ImportError as exc:
        raise SchemaValidationUnavailable(
            "XSD schema validation requires the optional 'xmlschema' "
            "dependency. Install it with: pip install format-factory-ubl[schema]"
        ) from exc
    return xmlschema


def _detect_root_name(source: bytes | str) -> str:
    """The local name of `source`'s own root element, without fully
    parsing or loading it -- just enough to select the matching schema."""
    stream = io.BytesIO(source if isinstance(source, bytes) else source.encode())
    try:
        for _, element in ET.iterparse(stream, events=("start",)):
            tag = element.tag
            return tag.rsplit("}", 1)[-1] if "}" in tag else tag
    except ET.ParseError as exc:
        raise UblParseError(f"cannot detect root element: {exc}") from exc
    raise UblParseError("source has no root element")


@lru_cache(maxsize=None)
def _load_schema(root_name: str) -> "_xmlschema_typing.XMLSchema":
    xmlschema = _require_xmlschema()
    path = _MAINDOC_DIR / f"UBL-{root_name}-2.3.xsd"
    return cast("_xmlschema_typing.XMLSchema", xmlschema.XMLSchema(str(path)))


def schema_validate(source: bytes | str, *, root_name: str | None = None) -> ValidationReport:
    """Validate raw UBL XML `source` against the bundled official schema
    matching its own root document type.

    `root_name`, if not given, is auto-detected from `source`'s own root
    element (e.g. "Invoice", "CreditNote") -- one of this package's own
    91 supported ROOT_NAME_SET types. Reports every violation found (both
    cardinality and element-order, checked together as XSD sequence
    validation always does), not just the first.

    Raises `SchemaValidationUnavailable` if the optional `xmlschema`
    dependency is not installed, or `UblParseError` if `root_name` is not
    one of this package's own 91 supported document types.
    """

    name = root_name if root_name is not None else _detect_root_name(source)
    if name not in ROOT_NAME_SET:
        raise UblParseError(
            f"{name!r} is not a supported UBL 2.3 root document type "
            f"(no bundled schema for it)"
        )
    schema = _load_schema(name)
    diagnostics: list[Diagnostic] = []
    xmlschema = _require_xmlschema()
    try:
        errors: list["_xmlschema_typing.XMLSchemaValidationError"] = list(
            schema.iter_errors(source)
        )
    except xmlschema.exceptions.XMLResourceParseError as exc:
        raise UblParseError(f"malformed XML: {exc}") from exc
    for error in errors:
        path = tuple(segment for segment in (error.path or "").split("/") if segment)
        diagnostics.append(
            Diagnostic(
                "ubl.schema.invalid",
                error.reason or str(error),
                location=SourceLocation(path=path) if path else None,
            )
        )
    return ValidationReport(diagnostics)


__all__ = ["schema_validate"]
