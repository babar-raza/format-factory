"""Document-type coverage operations for integrations.

Exposes the typed-root API surface UBL-DOCTYPES-001 names explicitly:
`supported_document_types`, `detect_document_type`, and `create_empty`.
The underlying capability (a distinct typed root per document type,
detection via `loads`, empty-document construction via
`UblDocument.build`) already exists; these are thin, stable wrappers
so integrations can enumerate and act on document-type coverage without
reaching into `model.root_types` directly.
"""

from __future__ import annotations

from ._generated import ROOT_NAMES
from .codec import loads
from .model import ROOT_CLASSES, UblDocument

__all__ = ["create_empty", "detect_document_type", "supported_document_types"]


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
