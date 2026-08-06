"""Preservation-mode serialization and loss disclosure for UBL documents.

UBL-PRESERVE-001 requires (a) an explicit LOSSLESS-vs-CANONICAL caller
choice on ``dumps()``/``dump()``, and (b) a first-class ``LossReport``/
``check_preservation`` API describing what CANONICAL mode would drop.

Scope chosen, documented honestly rather than silently narrowed: this
model's :class:`~format_factory.ubl.model.XmlNode` tree is fully generic
-- every element, whether a core business field or something a typed
accessor does not understand, is stored the same way. Unlike XLIFF (which
has a dedicated ``ExtensionNode`` slot), UBL's model draws no
modeled/unmodeled line anywhere in the tree for a canonical regeneration
to act on. The one place the UBL specification itself draws that line is
the root-level ``ext:UBLExtensions`` container (namespace
``urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2``)
-- the UBL 2.x schema family's own dedicated, optional slot for vendor or
national-customization content (digital signatures, CEN/PEPPOL
extensions, and similar) that sits alongside, not inside, the core
business document. CANONICAL mode drops that one container when present
as a direct child of the document root; every other element -- the
entire business-document tree the typed ``cac:``/``cbc:`` accessors
project over -- is preserved in both modes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..model import UblDocument, XmlNode

_EXTENSIONS_NAMESPACE = (
    "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
)
_EXTENSIONS_QNAME = f"{{{_EXTENSIONS_NAMESPACE}}}UBLExtensions"


class PreservationMode(StrEnum):
    """Caller-selectable output fidelity for ``dumps()``/``dump()``."""

    LOSSLESS = "lossless"
    CANONICAL = "canonical"


@dataclass(frozen=True, slots=True)
class LossReport:
    """Machine-readable disclosure of what CANONICAL mode would drop."""

    is_lossless: bool
    dropped_count: int
    dropped_tags: tuple[str, ...]
    detail: str


def canonicalize(document: UblDocument) -> tuple[UblDocument, tuple[str, ...]]:
    """Return a copy of ``document`` with a root-level ``ext:UBLExtensions``
    container dropped, if one is present as a direct child of the root.

    Returns the regenerated document plus the QName(s) dropped (empty if
    no such container was present -- the tree is returned unchanged, not
    merely equal, in that case).
    """

    root = document.root
    kept: list[XmlNode] = []
    dropped: list[str] = []
    for child in root.children:
        if child.qname == _EXTENSIONS_QNAME:
            dropped.append(child.qname)
        else:
            kept.append(child)
    if not dropped:
        return document, ()
    new_root = root.with_children(tuple(kept))
    return document.with_root(new_root), tuple(dropped)


def check_preservation(document: UblDocument) -> LossReport:
    """Report what CANONICAL mode would drop from ``document``.

    Does not serialize -- this walks the in-memory tree only, so it is
    cheap to call before choosing a preservation mode for ``dumps()``.
    """

    _canonical, dropped = canonicalize(document)
    if not dropped:
        return LossReport(
            is_lossless=True,
            dropped_count=0,
            dropped_tags=(),
            detail=(
                "document has no root-level ext:UBLExtensions container; "
                "LOSSLESS and CANONICAL output are identical"
            ),
        )
    return LossReport(
        is_lossless=False,
        dropped_count=len(dropped),
        dropped_tags=dropped,
        detail=(
            f"CANONICAL mode drops {len(dropped)} root-level "
            "ext:UBLExtensions container(s) -- the UBL specification's own "
            "vendor/customization extension slot"
        ),
    )
