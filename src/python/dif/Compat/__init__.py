"""dif.Compat — production facade layer for DIF.

Exports:
    DifHeader — facade for dif:header (SAL-DIF-00001)
    DifVector — facade for dif:vector (SAL-DIF-00002)
    DifDatum  — facade for dif:datum  (SAL-DIF-00003)
"""
from .dif_header import DifHeader
from .dif_vector import DifVector
from .dif_datum import DifDatum

__all__ = ["DifHeader", "DifVector", "DifDatum"]
