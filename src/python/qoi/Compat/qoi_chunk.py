"""QoiChunk — production facade for qoi:chunk."""
from __future__ import annotations
from ..spec.chunk.chunk import Chunk as _SpecChunk


class QoiChunk(_SpecChunk):
    """Production facade for qoi:chunk."""
    spec_qname = "qoi:chunk"
    spec_fact_ref = "FACT-QOI-002"
    namespace_uri = "urn:format:qoi:1.0"
