"""Domain model classes for PPM (Portable Pixmap).

Classes:
    PpmDocument — typed wrapper over PpmImage from ppm_parser

spec_qname: ppm:image
spec_fact_ref: see shared/qname-registry/ppm.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class PpmDocument:
    """Typed domain model for a Portable Pixmap (.ppm) image.

    Wraps the PpmImage dataclass returned by parse_ppm_strict().
    Neutral model fields: width (int), height (int), maxval (int),
    magic (str), pixels (list[tuple[int,int,int]]), path (str).
    """

    spec_qname: ClassVar[str] = "ppm:image"
    spec_fact_ref: ClassVar[str] = "FACT-PPM-001"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:ppm:1.0"
    local_name: ClassVar[str] = "image"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "PpmDocument":
        """Load a PPM file and return a PpmDocument."""
        from .ppm_parser import parse_ppm_strict
        return cls(parse_ppm_strict(path))

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
        """Maximum channel value (typically 255)."""
        return int(self._parsed.maxval)

    @property
    def pixel_count(self) -> int:
        """Total number of pixels (width * height)."""
        return self.width * self.height

    @property
    def magic(self) -> str:
        """PPM magic number (P3=ASCII, P6=binary)."""
        return str(self._parsed.magic)

    @property
    def is_binary(self) -> bool:
        """True if the image uses binary (P6) encoding."""
        return self.magic == "P6"

    @property
    def path(self) -> str:
        """Path to the source PPM file."""
        return str(self._parsed.path)

    # Dimension geometry properties (FACT-PPM-001, FACT-PPM-002)

    @property
    def aspect_ratio(self) -> float:
        """Width-to-height ratio. Returns 0.0 for zero-height images."""
        return self.width / self.height if self.height > 0 else 0.0

    @property
    def is_square(self) -> bool:
        """True if width equals height."""
        return self.width == self.height

    @property
    def is_landscape(self) -> bool:
        """True if width is greater than height."""
        return self.width > self.height

    @property
    def is_portrait(self) -> bool:
        """True if height is greater than width."""
        return self.height > self.width

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
            f"PpmDocument(width={self.width}, height={self.height}, "
            f"maxval={self.maxval}, magic={self.magic!r})"
        )
