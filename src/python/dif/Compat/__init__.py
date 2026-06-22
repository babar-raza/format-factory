"""dif.Compat — production facade layer for DIF.

Exports:
    DifHeader — facade for dif:header (FACT-DIF-001)
    DifVector — facade for dif:vector (FACT-DIF-002)
    DifDatum  — facade for dif:datum  (FACT-DIF-003)
"""
from .dif_header import DifHeader
from .dif_vector import DifVector
from .dif_datum import DifDatum

__all__ = ["DifHeader", "DifVector", "DifDatum"]
