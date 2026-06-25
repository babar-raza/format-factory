"""Domain model classes for PBM (Portable Bitmap).

Classes:
    PbmDocument — typed wrapper over PbmImage from pbm_parser

spec_qname: pbm:image
spec_fact_ref: see shared/qname-registry/pbm.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class PbmDocument:
    """Typed domain model for a Portable Bitmap (.pbm) image.

    Wraps the PbmImage dataclass returned by parse_pbm_strict().
    Neutral model fields: width (int), height (int), magic (str),
    pixels (list[int]), path (str).
    """

    spec_qname: ClassVar[str] = "pbm:image"
    spec_fact_ref: ClassVar[str] = "FACT-PBM-001"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pbm:1.0"
    local_name: ClassVar[str] = "image"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "PbmDocument":
        """Load a PBM file and return a PbmDocument."""
        from .pbm_parser import parse_pbm_strict
        return cls(parse_pbm_strict(path))

    @property
    def width(self) -> int:
        """Image width in pixels."""
        return int(self._parsed.width)

    @property
    def height(self) -> int:
        """Image height in pixels."""
        return int(self._parsed.height)

    @property
    def pixel_count(self) -> int:
        """Total number of pixels (width * height)."""
        return self.width * self.height

    @property
    def magic(self) -> str:
        """PBM magic number (P1=ASCII, P4=binary)."""
        return str(self._parsed.magic)

    @property
    def is_binary(self) -> bool:
        """True if the image uses binary (P4) encoding."""
        return self.magic == "P4"

    @property
    def path(self) -> str:
        """Path to the source PBM file."""
        return str(self._parsed.path)

    def to_dict(self) -> dict[str, Any]:
        """Return image metrics as a dict."""
        return {
            "width": self.width,
            "height": self.height,
            "pixel_count": self.pixel_count,
            "magic": self.magic,
            "path": self.path,
        }

    def __repr__(self) -> str:
        return f"PbmDocument(width={self.width}, height={self.height}, magic={self.magic!r})"
