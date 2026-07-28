"""gnumeric.Compat — production facade layer for Gnumeric (Gate 11 P-ARCH-001).

Exports:
    GnumericWorkbook — facade for gnm:Workbook (SAL-GNUMERIC-00001)
    GnumericSheet    — facade for gnm:Sheet    (SAL-GNUMERIC-00002)
"""
from .gnumeric_workbook import GnumericWorkbook
from .gnumeric_sheet import GnumericSheet

__all__ = ["GnumericWorkbook", "GnumericSheet"]
