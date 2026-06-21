"""fods.Compat — Production facade layer bridging spec stubs to models.

Each facade class has a spec_qname attribute referencing its canonical ODF spec element.
These facades are intended for production API use; the canonical spec stubs in spec/
are for spec-parity verification only.

TC-MACH-ARCH-004 (2026-06-21): Initial facade layer creation.
"""
from .fods_document import FodsDocument
from .fods_sheet import FodsSheet
from .fods_cell import FodsCell

__all__ = ["FodsDocument", "FodsSheet", "FodsCell"]
