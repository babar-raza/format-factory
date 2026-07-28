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
    spec_fact_ref: ClassVar[str] = "SAL-QOI-00001"
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

    # Dimension geometry properties (SAL-QOI-00001)

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

    # Image size classification properties (SAL-QOI-00001)

    @property
    def is_tiny(self) -> bool:
        """True if pixel_count is less than 1024 (smaller than 32x32)."""
        return self.pixel_count < 1024

    @property
    def is_large_image(self) -> bool:
        """True if pixel_count exceeds 4,000,000 (4 megapixels or more)."""
        return self.pixel_count > 4_000_000

    @property
    def megapixels(self) -> float:
        """Total pixel count expressed in megapixels (pixel_count / 1_000_000)."""
        return self.pixel_count / 1_000_000

    # Additional channel and colorspace properties (SAL-QOI-00001)

    @property
    def is_rgb(self) -> bool:
        """True if the image has 3 channels (RGB, no alpha)."""
        return self.channels == 3

    @property
    def is_srgb(self) -> bool:
        """True if the colorspace is sRGB (colorspace == 0)."""
        return self.colorspace == 0

    @property
    def is_linear(self) -> bool:
        """True if the colorspace is linear light (colorspace == 1)."""
        return self.colorspace == 1

    # Edge length and channel classification properties (SAL-QOI-00001 R1243)

    @property
    def long_edge(self) -> int:
        """Maximum of width and height."""
        return max(self.width, self.height)

    @property
    def short_edge(self) -> int:
        """Minimum of width and height."""
        return min(self.width, self.height)

    @property
    def is_rgba(self) -> bool:
        """True if channels == 4 (RGBA)."""
        return self.channels == 4

    # Canvas geometry and density properties (SAL-QOI-00001 R1263)

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
    def bytes_per_pixel_estimate(self) -> int:
        """Estimated bytes per pixel (= channels: 3 for RGB, 4 for RGBA)."""
        return self.channels

    # Scale and density classification properties (SAL-QOI-00001 R1283)

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

    def set_pixel(self, index: int, value: tuple[int, ...]) -> None:
        """Set a pixel value in place by flat index.

        Args:
            index: Zero-based flat (row-major) pixel index.
            value: New pixel value as (R, G, B) or (R, G, B, A) tuple.

        Raises:
            QoiError: If index is out of range or value has wrong channel count.
        """
        from .qoi_parser import QoiError
        pixels = self._parsed.pixels
        if index < 0 or index >= len(pixels):
            raise QoiError(f"pixel index {index} out of range (0..{len(pixels) - 1})")
        if not (isinstance(value, (tuple, list)) and len(value) in (3, 4)):
            raise QoiError("value must be an (R, G, B) or (R, G, B, A) tuple")
        pixels[index] = tuple(int(c) for c in value)

    def save_to_file(self, path: "str | Path") -> None:
        """Save this image to a .qoi file.

        Raises:
            QoiError: If path is empty or encoding fails.
        """
        from .qoi_parser import QoiError
        from .qoi_encoder import encode_qoi_to_file
        if not path:
            raise QoiError("path must not be empty")
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        encode_qoi_to_file(self._parsed, dest)

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
