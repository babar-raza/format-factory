"""cac:ExternalReference — a pointer to content outside the document.

"cac:ExternalReference is an aggregate with optional URI, DocumentHash,
MimeCode, FileName, and Description elements." (SAL-UBL-00119, verified
against the OASIS UBL Specification.) Every element is optional per the
spec; this model does not invent a required field the spec does not name.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import UblValidationError
from .document import XmlNode
from .typed import find


@dataclass(frozen=True)
class ExternalReference:
    """A pointer to content outside the document (cac:ExternalReference)."""

    uri: str | None = None
    document_hash: str | None = None
    mime_code: str | None = None
    filename: str | None = None
    description: str | None = None


def _text_or_none(node: XmlNode | None) -> str | None:
    return node.text if node is not None else None


def external_reference_of(node: XmlNode | None) -> ExternalReference:
    if node is None:
        raise UblValidationError(
            "cannot project a missing element into a cac:ExternalReference"
        )
    return ExternalReference(
        uri=_text_or_none(find(node, "URI")),
        document_hash=_text_or_none(find(node, "DocumentHash")),
        mime_code=_text_or_none(find(node, "MimeCode")),
        filename=_text_or_none(find(node, "FileName")),
        description=_text_or_none(find(node, "Description")),
    )


__all__ = ["ExternalReference", "external_reference_of"]
