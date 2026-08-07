"""Document-type coverage operations for integrations.

Exposes the typed-root API surface UBL-DOCTYPES-001 names explicitly:
`supported_document_types`, `detect_document_type`, and `create_empty`.
The underlying capability (a distinct typed root per document type,
detection via `loads`, empty-document construction via
`UblDocument.build`) already exists; these are thin, stable wrappers
so integrations can enumerate and act on document-type coverage without
reaching into `model.root_types` directly.

`DocumentTypeCoverage`/`document_type_coverage` formalize the three-tier
vocabulary UBL-DOCTYPES-001 names explicitly (supported / preservation-only
/ unsupported), declared per type rather than as a single blanket claim.
Every one of the 91 UBL 2.3 root types this package recognizes is fully
typed today -- there is currently no PRESERVATION_ONLY case (a root type
this package would round-trip losslessly but expose no typed accessors
for); this is a factual statement about the current package, not an
assumption the enum itself makes, so a future root added as
preservation-only would use this same vocabulary without changing it.
"""

from __future__ import annotations

from enum import Enum

from ._generated import ROOT_NAMES
from .codec import loads
from .model import ROOT_CLASSES, UblDocument

__all__ = [
    "DocumentTypeCoverage",
    "create_empty",
    "detect_document_type",
    "document_type_coverage",
    "document_type_coverage_manifest",
    "supported_document_types",
]


class DocumentTypeCoverage(Enum):
    """"Document-type coverage is declared per type (supported/
    preservation-only/unsupported) - never claimed globally."\""""

    SUPPORTED = "supported"
    PRESERVATION_ONLY = "preservation_only"
    UNSUPPORTED = "unsupported"


def document_type_coverage(root_name: str) -> DocumentTypeCoverage:
    """This one document root's coverage tier, never a package-wide claim.

    SUPPORTED: `root_name` has a typed dataclass in `model.root_types`
    (every field modeled). UNSUPPORTED: `loads()` refuses any document
    declaring this root -- confirmed by `UblParseError` at parse time,
    not merely an absent registry entry.
    """
    if root_name in ROOT_CLASSES:
        return DocumentTypeCoverage.SUPPORTED
    return DocumentTypeCoverage.UNSUPPORTED


def document_type_coverage_manifest() -> dict[str, DocumentTypeCoverage]:
    """Every currently-recognized root name's coverage tier, keyed by name."""

    return {name: DocumentTypeCoverage.SUPPORTED for name in ROOT_NAMES}


def supported_document_types() -> tuple[str, ...]:
    """Return every supported UBL 2.3 document root name, sorted."""

    return ROOT_NAMES


def detect_document_type(source: bytes | bytearray | memoryview | str) -> str:
    """Parse `source` and return its detected document root name.

    Raises the same errors `loads` would for malformed or unsupported input.
    """

    return loads(source, mode="preservation").root_name


def create_empty(document_type: str) -> UblDocument:
    """Construct a minimal, valid document of `document_type`.

    Raises ValueError if `document_type` is not one of
    `supported_document_types()`.
    """

    root_class = ROOT_CLASSES.get(document_type)
    if root_class is None:
        raise ValueError(f"unsupported UBL document type: {document_type!r}")
    return root_class.build()
