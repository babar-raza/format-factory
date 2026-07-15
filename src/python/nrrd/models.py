"""Domain model for NRRD documents."""

from __future__ import annotations

from typing import Any, ClassVar


class NrrdDocument:
    """Typed domain model wrapping a parsed NRRD file."""

    spec_qname: ClassVar[str] = "nrrd:header"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> NrrdDocument:
        """Load an NRRD document from the file at path."""
        from nrrd.nrrd_codec import load_nrrd

        return cls(load_nrrd(path))

    @property
    def raw(self) -> dict[str, Any]:
        """Return the underlying parsed data dictionary."""
        return self._data

    @property
    def version(self) -> int:
        """Return the NRRD format version number."""
        return self._data.get("version", 0)

    @property
    def header(self) -> dict[str, str]:
        """Return the parsed NRRD header fields."""
        return self._data.get("header", {})

    @property
    def data_size(self) -> int:
        """Return the total data payload size in bytes."""
        return self._data.get("data_size", 0)

    @property
    def dimension(self) -> int:
        """Return the number of array dimensions."""
        return int(self.header.get("dimension", "0"))

    @property
    def encoding(self) -> str:
        """Return the data encoding type (e.g. 'raw', 'gzip')."""
        return self.header.get("encoding", "raw")

    @property
    def nrrd_type(self) -> str:
        """Return the NRRD data type string."""
        return self.header.get("type", "")

    @property
    def sizes(self) -> list[int]:
        """Return the sizes for each dimension as a list of ints."""
        sizes_str = self.header.get("sizes", "")
        if not sizes_str:
            return []
        return [int(s) for s in sizes_str.split()]

    @property
    def is_empty(self) -> bool:
        """Return True if the document contains no data."""
        return self.data_size == 0

    @property
    def key_value_pairs(self) -> dict[str, str]:
        """Return the NRRD0002+ arbitrary key:=value pairs (distinct from fixed header fields)."""
        return self._data.get("key_value_pairs", {})

    @property
    def kinds(self) -> list[str]:
        """Return the per-axis ``kinds`` values (e.g. ``['domain', 'domain', 'RGB-color']``)."""
        return list(self._data.get("kinds", []))

    @property
    def domain_axes(self) -> list[int]:
        """Return the indices of axes whose ``kinds`` value is a domain kind (domain/space/time)."""
        from nrrd.nrrd_codec import DOMAIN_KINDS

        return [i for i, k in enumerate(self.kinds) if k.lower() in DOMAIN_KINDS]

    @property
    def range_axes(self) -> list[int]:
        """Return the indices of axes whose ``kinds`` value is a range kind (vector/color/tensor/...)."""
        from nrrd.nrrd_codec import DOMAIN_KINDS

        return [i for i, k in enumerate(self.kinds) if k.lower() not in DOMAIN_KINDS]

    @property
    def space(self) -> str:
        """Return the ``space`` field (e.g. ``'left-posterior-superior'``), empty if absent."""
        return str(self._data.get("space", ""))

    @property
    def space_directions(self) -> list[tuple[float, ...] | None]:
        """Return the per-axis ``space directions`` vectors (None entries mark non-spatial axes)."""
        return list(self._data.get("space_directions", []))

    @property
    def space_origin(self) -> tuple[float, ...] | None:
        """Return the ``space origin`` point vector, or None if absent."""
        return self._data.get("space_origin")

    @property
    def array(self) -> list[Any] | None:
        """Return the flat decoded data values, or None if decode was not possible."""
        return self._data.get("array")

    @property
    def array_shape(self) -> list[int] | None:
        """Return the per-axis shape of the decoded array, or None if unavailable."""
        return self._data.get("array_shape")

    def to_array(self) -> Any:
        """Return the decoded data reshaped into nested lists per axis sizes.

        Returns None if the declared type/encoding was not decodable.
        """
        from nrrd.nrrd_codec import get_array

        return get_array(self._data)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"NrrdDocument(version={self.version}, encoding={self.encoding!r})"
