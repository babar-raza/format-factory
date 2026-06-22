"""
QOI structural element: qoi:chunk

Spec ref: QOI specification — chunk types (QOI_OP_*)
Fact ref: FACT-QOI-002
QName: qoi:chunk
Canonical class: Chunk
Facade: QoiChunk
"""
from __future__ import annotations
from typing import Any


class Chunk:
    """Canonical spec-shaped class for qoi:chunk (encoded pixel run)."""

    spec_qname = "qoi:chunk"
    spec_fact_ref = "FACT-QOI-002"
    namespace_uri = "urn:format:qoi:1.0"
    local_name = "chunk"
    facade_names = ["QoiChunk"]

    CHUNK_TYPES = ("QOI_OP_RGB", "QOI_OP_RGBA", "QOI_OP_INDEX", "QOI_OP_DIFF", "QOI_OP_LUMA", "QOI_OP_RUN")

    def __init__(self, chunk_type: str, data: dict[str, Any]) -> None:
        self._chunk_type = chunk_type
        self._data = data

    @property
    def chunk_type(self) -> str:
        return self._chunk_type

    @property
    def byte_length(self) -> int:
        return int(self._data.get("byte_length", 1))

    def to_dict(self) -> dict[str, Any]:
        return {"chunk_type": self._chunk_type, **self._data}

    def __repr__(self) -> str:
        return f"Chunk(type={self._chunk_type!r})"
