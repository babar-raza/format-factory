"""cac:ExternalReference — a pointer to content outside the document.

"cac:ExternalReference is an aggregate with optional URI, DocumentHash,
MimeCode, FileName, and Description elements." (SAL-UBL-00119, verified
against the OASIS UBL Specification.) Every element is optional per the
spec; this model does not invent a required field the spec does not name.

UBL-PARSE-001 (FF6-EVENT-000482): all 5 fields are namespace-precise via
`find_qname`, not `find`'s own local-name-only matching -- the first of
the ~84 disclosed `find()`/`find_all()` call sites migrated to the
namespace-precise primitive (FF6-EVENT-000481), chosen as the smallest,
fully self-contained wave (one file, 5 call sites, every field's own
namespace already confirmed unambiguous and CBC-only by this module's
own pre-existing test fixtures before this migration).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import UblValidationError
from .document import XmlNode
from .typed import find_qname

#: Every cac:ExternalReference child field is a CommonBasicComponents
#: simple type -- confirmed directly against this module's own
#: pre-existing test fixtures (test_obligation_external_reference.py),
#: which build every field exclusively under this namespace.
_CBC_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"


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


def _find(node: XmlNode, name: str) -> XmlNode | None:
    return find_qname(node, _CBC_NAMESPACE, name)


def external_reference_of(node: XmlNode | None) -> ExternalReference:
    if node is None:
        raise UblValidationError(
            "cannot project a missing element into a cac:ExternalReference"
        )
    return ExternalReference(
        uri=_text_or_none(_find(node, "URI")),
        document_hash=_text_or_none(_find(node, "DocumentHash")),
        mime_code=_text_or_none(_find(node, "MimeCode")),
        filename=_text_or_none(_find(node, "FileName")),
        description=_text_or_none(_find(node, "Description")),
    )


__all__ = ["ExternalReference", "external_reference_of"]
