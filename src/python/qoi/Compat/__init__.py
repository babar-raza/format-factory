"""qoi.Compat — production facade layer for QOI.

Exports:
    QoiHeader    — facade for qoi:header     (SAL-QOI-00001)
    QoiChunk     — facade for qoi:chunk      (SAL-QOI-00002)
    QoiEndMarker — facade for qoi:end-marker (SAL-QOI-00003)
"""
from .qoi_header import QoiHeader
from .qoi_chunk import QoiChunk
from .qoi_end_marker import QoiEndMarker

__all__ = ["QoiHeader", "QoiChunk", "QoiEndMarker"]
