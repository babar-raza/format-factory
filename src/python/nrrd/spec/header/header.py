"""
NRRD structural element: nrrd:header

Spec ref: Teem NRRD Format Specification — Section 2. Header
Fact ref: FACT-NRRD-002
QName: nrrd:header
Canonical class: Header
Facade: NrrdHeader
"""
from __future__ import annotations
from typing import Any

# NRRD `kinds` values that denote a domain (spatial/temporal) axis, per the
# Teem spec's kind enumeration. Any other declared kind (scalar, vector,
# RGB-color, ..., or an unrecognized value) is a range axis.
_DOMAIN_KINDS = frozenset({"domain", "space", "time"})


def _parse_vector(token: str) -> tuple[float, ...] | None:
    """Parse a single NRRD space vector token, e.g. ``(1,0,0)`` or ``none``."""
    token = token.strip()
    if token.lower() == "none":
        return None
    if token.startswith("(") and token.endswith(")"):
        inner = token[1:-1].strip()
        if not inner:
            return ()
        return tuple(float(x) for x in inner.split(","))
    return None


def _parse_vector_list(value: str) -> list[tuple[float, ...] | None]:
    """Parse a whitespace-separated list of NRRD space vectors/``none`` tokens."""
    import re

    tokens = re.findall(r"\([^)]*\)|none", value, flags=re.IGNORECASE)
    return [_parse_vector(t) for t in tokens]


class Header:
    """Canonical spec-shaped class for nrrd:header (key:value header fields).

    Wraps the parsed header dict (type, dimension, sizes, encoding, endian)
    produced by ``nrrd.nrrd_codec.load_nrrd``. architecture_only marker class:
    no I/O — a read-only view over an already-parsed dict. The ``sizes``
    property does minimal in-memory string-to-list coercion (splitting the
    already-parsed header value), not file/byte parsing.
    """

    spec_qname = "nrrd:header"
    spec_fact_ref = "FACT-NRRD-002"
    namespace_uri = "urn:format:nrrd:5.0"
    local_name = "header"
    facade_names = ["NrrdHeader"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def type(self) -> str:
        """Return the NRRD data type field (e.g. 'uint8', 'float', 'double')."""
        return str(self._data.get("type", ""))

    @property
    def dimension(self) -> int:
        """Return the number of array dimensions."""
        raw = self._data.get("dimension", "0")
        try:
            return int(raw)
        except (TypeError, ValueError):
            return 0

    @property
    def sizes(self) -> list[int]:
        """Return the per-axis sizes as a list of ints (empty if absent)."""
        sizes_str = self._data.get("sizes", "")
        if not sizes_str:
            return []
        return [int(s) for s in sizes_str.split()]

    @property
    def encoding(self) -> str:
        """Return the data encoding field (defaults to 'raw' per spec)."""
        return str(self._data.get("encoding", "raw"))

    @property
    def endian(self) -> str:
        """Return the endianness field ('little' or 'big'), empty if absent."""
        return str(self._data.get("endian", ""))

    @property
    def kinds(self) -> list[str]:
        """Return the per-axis ``kinds`` field values (empty if absent).

        Distinguishes domain (spatial/temporal) axes from range axes
        (vector/tensor/color-channel components) — see :attr:`domain_axes`
        and :attr:`range_axes`.
        """
        kinds_str = self._data.get("kinds", "")
        if not kinds_str:
            return []
        return kinds_str.split()

    @property
    def domain_axes(self) -> list[int]:
        """Return the indices of axes whose ``kinds`` value is domain/space/time."""
        return [i for i, k in enumerate(self.kinds) if k.lower() in _DOMAIN_KINDS]

    @property
    def range_axes(self) -> list[int]:
        """Return the indices of axes whose ``kinds`` value is NOT domain/space/time."""
        return [i for i, k in enumerate(self.kinds) if k.lower() not in _DOMAIN_KINDS]

    @property
    def space(self) -> str:
        """Return the ``space`` field (e.g. 'left-posterior-superior'), empty if absent."""
        return str(self._data.get("space", ""))

    @property
    def space_directions(self) -> list[tuple[float, ...] | None]:
        """Return the per-axis ``space directions`` vectors.

        Each entry is a tuple of floats for a spatial axis, or None for an
        axis marked ``none`` (a non-spatial axis, e.g. a color channel).
        Empty list if the field is absent.
        """
        raw = self._data.get("space directions", "")
        if not raw:
            return []
        return _parse_vector_list(raw)

    @property
    def space_origin(self) -> tuple[float, ...] | None:
        """Return the ``space origin`` point vector, or None if absent."""
        raw = self._data.get("space origin", "")
        if not raw:
            return None
        return _parse_vector(raw)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying header dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(type={self.type!r}, dimension={self.dimension}, encoding={self.encoding!r})"
