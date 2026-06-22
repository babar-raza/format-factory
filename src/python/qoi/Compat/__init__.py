"""qoi.Compat — production facade layer for QOI.

Exports:
    QoiHeader — facade for qoi:header (FACT-QOI-001)
    QoiChunk  — facade for qoi:chunk  (FACT-QOI-002)
"""
from .qoi_header import QoiHeader
from .qoi_chunk import QoiChunk

__all__ = ["QoiHeader", "QoiChunk"]
