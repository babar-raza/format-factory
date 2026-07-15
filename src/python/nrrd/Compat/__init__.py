"""nrrd.Compat — production facade layer for NRRD.

Exports:
    NrrdHeader — facade for nrrd:header (FACT-NRRD-002)
    NrrdData   — facade for nrrd:data   (FACT-NRRD-003)
"""
from .nrrd_header import NrrdHeader
from .nrrd_data import NrrdData

__all__ = ["NrrdHeader", "NrrdData"]
