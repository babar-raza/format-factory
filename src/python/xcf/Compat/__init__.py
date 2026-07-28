"""xcf.Compat — production facade layer for XCF.

Exports:
    XcfHeader — facade for xcf:header (SAL-XCF-00001)
    XcfLayer  — facade for xcf:layer  (SAL-XCF-00002)
"""
from .xcf_header import XcfHeader
from .xcf_layer import XcfLayer

__all__ = ["XcfHeader", "XcfLayer"]
