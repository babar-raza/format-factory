"""fods.Compat — Production facade layer for FODS spec elements (Gate 11 P-ARCH-001)."""
from .fods_document import FodsDocument
from .fods_sheet import FodsSheet
from .fods_cell import FodsCell


def get_spec_qname(obj) -> str | None:
    """Return the ODF QName for a FODS model object, or None if not annotated."""
    return getattr(obj, "spec_qname", None)


__all__ = ["FodsDocument", "FodsSheet", "FodsCell", "get_spec_qname"]
