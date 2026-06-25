"""Domain model classes for PGM (Portable Graymap).

Classes:
    PgmDocument — typed wrapper over PgmImage from pgm_parser

spec_qname: pgm:image
spec_fact_ref: see shared/qname-registry/pgm.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class PgmDocument:
    """Typed domain model for a Portable Graymap (.pgm) image.

    Wraps the PgmImage dataclass returned by parse_pgm_strict().
    Neutral model fields: width (int), height (int), maxval (int),
    magic (str), pixels (list[int]), path (str).
    """

    spec_qname: ClassVar[str] = "pgm:image"
    spec_fact_ref: ClassVar[str] = "FACT-PGM-001"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pgm:1.0"
    local_name: ClassVar[str] = "image"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "PgmDocument":
        """Load a PGM file and return a PgmDocument."""
        from .pgm_parser import parse_pgm_strict
        return cls(parse_pgm_strict(path))

    @property
    def width(self) -> int:
        """Image width in pixels."""
        return int(self._parsed.width)

    @property
    def height(self) -> int:
        """Image height in pixels."""
        return int(self._parsed.height)

    @property
    def maxval(self) -> int:
        """Maximum grayscale value (typically 255)."""
        return int(self._parsed.maxval)

    @property
    def pixel_count(self) -> int:
        """Total number of pixels (width * height)."""
        return self.width * self.height

    @property
    def magic(self) -> str:
        """PGM magic number (P2=ASCII, P5=binary)."""
        return str(self._parsed.magic)

    @property
    def is_binary(self) -> bool:
        """True if the image uses binary (P5) encoding."""
        return self.magic == "P5"

    @property
    def path(self) -> str:
        """Path to the source PGM file."""
        return str(self._parsed.path)

    def to_dict(self) -> dict[str, Any]:
        """Return image metrics as a dict."""
        return {
            "width": self.width,
            "height": self.height,
            "maxval": self.maxval,
            "pixel_count": self.pixel_count,
            "magic": self.magic,
            "path": self.path,
        }

    def __repr__(self) -> str:
        return (
            f"PgmDocument(width={self.width}, height={self.height}, "
            f"maxval={self.maxval}, magic={self.magic!r})"
        )
