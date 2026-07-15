"""
NRRD structural element: nrrd:data

Spec ref: Teem NRRD Format Specification — Section 3. Data
Fact ref: FACT-NRRD-003
QName: nrrd:data
Canonical class: Data
Facade: NrrdData
"""
from __future__ import annotations
from typing import Any


class Data:
    """Canonical spec-shaped class for nrrd:data (data payload metadata).

    Wraps the encoding/size metadata produced by ``nrrd.nrrd_codec.load_nrrd``.
    architecture_only marker class: no I/O, no decoding logic — a read-only
    view over already-computed payload metadata.
    """

    spec_qname = "nrrd:data"
    spec_fact_ref = "FACT-NRRD-003"
    namespace_uri = "urn:format:nrrd:5.0"
    local_name = "data"
    facade_names = ["NrrdData"]

    # Encodings named in FACT-NRRD-003. raw/ascii/hex are uncompressed;
    # gzip/bzip2/zlib (and the "gz" alias accepted by the codec) are compressed.
    UNCOMPRESSED_ENCODINGS = ("raw", "ascii", "hex")
    KNOWN_ENCODINGS = ("raw", "ascii", "hex", "gzip", "gz", "bzip2", "zlib")

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def encoding(self) -> str:
        """Return the data encoding field (defaults to 'raw' per spec)."""
        return str(self._data.get("encoding", "raw"))

    @property
    def data_size(self) -> int:
        """Return the data payload size in bytes."""
        try:
            return int(self._data.get("data_size", 0))
        except (TypeError, ValueError):
            return 0

    @property
    def element_count(self) -> int:
        """Return the total number of data elements (product of axis sizes)."""
        try:
            return int(self._data.get("element_count", 0))
        except (TypeError, ValueError):
            return 0

    @property
    def is_compressed(self) -> bool:
        """Return True if the encoding is anything other than raw/ascii/hex."""
        return self.encoding not in self.UNCOMPRESSED_ENCODINGS

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data-metadata dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Data(encoding={self.encoding!r}, data_size={self.data_size}, element_count={self.element_count})"
