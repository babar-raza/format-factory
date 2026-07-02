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

    # Additional image analysis properties (FACT-PPM-001)

    @property
    def is_high_depth(self) -> bool:
        """True if the image uses more than 8-bit depth per channel (maxval > 255)."""
        return self.maxval > 255

    @property
    def is_tiny(self) -> bool:
        """True if both width and height are at most 64 pixels."""
        return self.width <= 64 and self.height <= 64

    @property
    def megapixels(self) -> float:
        """Image size in megapixels (pixel_count / 1,000,000)."""
        return self.pixel_count / 1_000_000.0

    # Encoding and size classification properties (FACT-PPM-001 R1239)

    @property
    def is_ascii(self) -> bool:
        """True if the image uses ASCII (P3) encoding."""
        return self.magic == "P3"

    @property
    def is_large_image(self) -> bool:
        """True if pixel_count > 1,000,000."""
        return self.pixel_count > 1_000_000

    @property
    def long_edge(self) -> int:
        """Maximum of width and height."""
        return max(self.width, self.height)

    @property
    def short_edge(self) -> int:
        """Minimum of width and height."""
        return min(self.width, self.height)

    # Geometry ratio properties (FACT-PPM-001 R1259)

    @property
    def edge_ratio(self) -> float:
        """long_edge / short_edge; 1.0 if short_edge is 0."""
        if self.short_edge == 0:
            return 1.0
        return self.long_edge / self.short_edge

    @property
    def is_narrow(self) -> bool:
        """True if edge_ratio > 3.0."""
        return self.edge_ratio > 3.0

    @property
    def is_micro(self) -> bool:
        """True if width <= 64 and height <= 64."""
        return self.width <= 64 and self.height <= 64

    # Scale and density classification properties (FACT-PPM-001 R1279)

    @property
    def is_banner(self) -> bool:
        """True if is_narrow and is_landscape (wide strip)."""
        return self.is_narrow and self.is_landscape

    @property
    def is_tall_strip(self) -> bool:
        """True if is_narrow and is_portrait (tall strip)."""
        return self.is_narrow and self.is_portrait

    @property
    def pixel_density_class(self) -> str:
        """'micro' if long_edge<=64; 'small' if <=256; 'medium' if <=1024; 'large' otherwise."""
        le = self.long_edge
        if le <= 64:
            return "micro"
        if le <= 256:
            return "small"
        if le <= 1024:
            return "medium"
        return "large"

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
