"""ods.Compat — production facade layer for ODS (Gate 11 P-ARCH-001).

Exports:
    OdsDocument  — facade for office:document (SAL-ODS-00029)
    OdsSheet     — facade for table:table     (SAL-ODS-00127)
    OdsCell      — facade for table:table-cell (SAL-ODS-00474)
"""
from .ods_document import OdsDocument
from .ods_sheet import OdsSheet
from .ods_cell import OdsCell

__all__ = ["OdsDocument", "OdsSheet", "OdsCell"]
