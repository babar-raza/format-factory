"""Public UBL model types."""

from .document import UblDocument, XmlNode
from .root_types import ROOT_CLASSES
from .values import (
    Amount,
    BinaryObject,
    Code,
    Identifier,
    Quantity,
    Rounding,
)


def document_from_root(
    root: XmlNode,
    *,
    source_sha256: str | None = None,
    signed_content_sha256: str | None = None,
) -> UblDocument:
    root_name = root.qname.rsplit("}", 1)[-1]
    document_type = ROOT_CLASSES.get(root_name)
    if document_type is None:
        raise ValueError(f"unsupported UBL document root: {root_name}")
    return document_type(
        root,
        source_sha256=source_sha256,
        signed_content_sha256=signed_content_sha256,
    )

__all__ = [
    "Rounding",
    "Quantity",
    "Identifier",
    "Code",
    "BinaryObject",
    "Amount","ROOT_CLASSES", "UblDocument", "XmlNode", "document_from_root"]
