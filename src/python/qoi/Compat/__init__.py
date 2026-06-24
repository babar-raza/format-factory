"""qoi.Compat — production facade layer for QOI.

Exports:
    QoiHeader    — facade for qoi:header     (FACT-QOI-001)
    QoiChunk     — facade for qoi:chunk      (FACT-QOI-002)
    QoiEndMarker — facade for qoi:end-marker (FACT-QOI-003)
"""
from .qoi_header import QoiHeader
from .qoi_chunk import QoiChunk
from .qoi_end_marker import QoiEndMarker

__all__ = ["QoiHeader", "QoiChunk", "QoiEndMarker"]
