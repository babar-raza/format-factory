"""xcf.Compat — production facade layer for XCF.

Exports:
    XcfHeader — facade for xcf:header (FACT-XCF-001)
    XcfLayer  — facade for xcf:layer  (FACT-XCF-002)
"""
from .xcf_header import XcfHeader
from .xcf_layer import XcfLayer

__all__ = ["XcfHeader", "XcfLayer"]
