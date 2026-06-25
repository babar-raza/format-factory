"""Domain model classes for QOI (Quite OK Image Format).

Classes:
    QoiDocument — typed wrapper over QoiImage from qoi_parser

spec_qname: qoi:image
spec_fact_ref: see shared/qname-registry/qoi.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class QoiDocument:
    """Typed domain model for a QOI image file.

    Wraps the QoiImage dataclass returned by parse_qoi_strict().
    Neutral model fields: width (int), height (int), channels (int),
    colorspace (int), pixels (list[tuple]), path (str).
    """

    spec_qname: ClassVar[str] = "qoi:image"
    spec_fact_ref: ClassVar[str] = "FACT-QOI-001"
    namespace_uri: ClassVar[str] = "urn:format:qoi:1.0"
    local_name: ClassVar[str] = "image"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "QoiDocument":
        """Load a QOI file and return a QoiDocument."""
        from .qoi_parser import parse_qoi_strict
        return cls(parse_qoi_strict(path))

    @property
    def width(self) -> int:
        """Image width in pixels."""
        return int(self._parsed.width)

    @property
    def height(self) -> int:
        """Image height in pixels."""
        return int(self._parsed.height)

    @property
    def channels(self) -> int:
        """Number of color channels (3=RGB, 4=RGBA)."""
        return int(self._parsed.channels)

    @property
    def colorspace(self) -> int:
        """Colorspace flag (0=sRGB, 1=linear)."""
        return int(self._parsed.colorspace)

    @property
    def pixel_count(self) -> int:
        """Total number of pixels (width * height)."""
        return self.width * self.height

    @property
    def has_alpha(self) -> bool:
        """True if the image has an alpha channel (channels == 4)."""
        return self.channels == 4

    @property
    def path(self) -> str:
        """Path to the source QOI file."""
        return str(self._parsed.path)

    def to_dict(self) -> dict[str, Any]:
        """Return image metrics as a dict."""
        return {
            "width": self.width,
            "height": self.height,
            "channels": self.channels,
            "colorspace": self.colorspace,
            "pixel_count": self.pixel_count,
            "has_alpha": self.has_alpha,
            "path": self.path,
        }

    def __repr__(self) -> str:
        return (
            f"QoiDocument(width={self.width}, height={self.height}, "
            f"channels={self.channels})"
        )
