"""xliff.Compat — production facade layer for XLIFF.

Exports:
    XliffFile    — facade for xliff:file     (FACT-XLIFF-001)
    XliffUnit    — facade for xliff:unit     (FACT-XLIFF-002)
    XliffSegment — facade for xliff:segment  (FACT-XLIFF-002)
"""
from .xliff_file import XliffFile
from .xliff_unit import XliffUnit
from .xliff_segment import XliffSegment

__all__ = ["XliffFile", "XliffUnit", "XliffSegment"]
