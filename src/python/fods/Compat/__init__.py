"""fods.Compat — Production facade layer for FODS (Gate 11 P-ARCH-001).

Each facade class has a spec_qname attribute referencing its canonical ODF spec element.
These facades are the production public API; the canonical spec authority classes in spec/
establish spec-parity traceability.

TC-MACH-ARCH-004 (2026-06-21): Initial facade layer creation.
"""
from .fods_document import FodsDocument
from .fods_sheet import FodsSheet
from .fods_cell import FodsCell


def get_spec_qname(obj) -> str | None:
    """Return the ODF QName for a FODS model object, or None if not annotated."""
    return getattr(obj, "spec_qname", None)


__all__ = ["FodsDocument", "FodsSheet", "FodsCell", "get_spec_qname"]
