"""ods.Compat — production facade layer for ODS (Gate 11 P-ARCH-001).

Exports:
    OdsDocument  — facade for office:document (FACT-ODS-EX-0029)
    OdsSheet     — facade for table:table     (FACT-ODS-EX-0129)
    OdsCell      — facade for table:table-cell (FACT-ODS-EX-0479)
"""
from .ods_document import OdsDocument
from .ods_sheet import OdsSheet
from .ods_cell import OdsCell

__all__ = ["OdsDocument", "OdsSheet", "OdsCell"]
