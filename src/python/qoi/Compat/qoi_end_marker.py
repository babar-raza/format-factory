"""QoiEndMarker — production facade for qoi:end-marker."""
from __future__ import annotations
from typing import ClassVar
from ..spec.chunk.end_marker import EndMarker as _SpecEndMarker


class QoiEndMarker(_SpecEndMarker):
    """Production facade for qoi:end-marker."""
    spec_qname: ClassVar[str] = "qoi:end-marker"
    spec_fact_ref: ClassVar[str] = "SAL-QOI-00003"
    namespace_uri: ClassVar[str] = "urn:format:qoi:1.0"
