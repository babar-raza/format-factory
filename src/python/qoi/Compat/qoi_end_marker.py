"""QoiEndMarker — production facade for qoi:end-marker."""
from __future__ import annotations
from ..spec.chunk.end_marker import EndMarker as _SpecEndMarker


class QoiEndMarker(_SpecEndMarker):
    """Production facade for qoi:end-marker."""
    spec_qname = "qoi:end-marker"
    spec_fact_ref = "FACT-QOI-003"
    namespace_uri = "urn:format:qoi:1.0"
