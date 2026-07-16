"""QoiChunk — production facade for qoi:chunk."""
from __future__ import annotations
from typing import ClassVar
from ..spec.chunk.chunk import Chunk as _SpecChunk


class QoiChunk(_SpecChunk):
    """Production facade for qoi:chunk."""
    spec_qname: ClassVar[str] = "qoi:chunk"
    spec_fact_ref: ClassVar[str] = "SAL-QOI-00002"
    namespace_uri: ClassVar[str] = "urn:format:qoi:1.0"
