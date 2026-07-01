"""Domain model classes for XCF (GIMP Native Image Format).

Classes:
    XcfDocument — typed wrapper over XcfImage from xcf_parser

spec_qname: xcf:image
spec_fact_ref: see shared/qname-registry/xcf.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class XcfDocument:
    """Typed domain model for a GIMP XCF image file.

    Wraps the XcfImage dataclass returned by parse_xcf_strict().
    Neutral model fields: width (int), height (int), image_type (int),
    version (str), num_layers (int), path (str), layer_names (list).
    """

    spec_qname: ClassVar[str] = "xcf:image"
    spec_fact_ref: ClassVar[str] = "FACT-XCF-001"
    namespace_uri: ClassVar[str] = "urn:format:xcf:2.10"
    local_name: ClassVar[str] = "image"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "XcfDocument":
        """Load an XCF file and return an XcfDocument."""
        from .xcf_parser import parse_xcf_strict
        return cls(parse_xcf_strict(path))

    @property
    def width(self) -> int:
        """Image canvas width in pixels."""
        return int(self._parsed.width)

    @property
    def height(self) -> int:
        """Image canvas height in pixels."""
        return int(self._parsed.height)

    @property
    def layer_count(self) -> int:
        """Number of layers in the XCF image."""
        return int(self._parsed.num_layers)

    @property
    def version(self) -> str:
        """XCF format version string (e.g. 'xcf v011')."""
        return str(self._parsed.version or "")

    @property
    def image_type(self) -> int:
        """Image type flag (0=RGB, 1=RGBA, 2=GRAY, 3=GRAYA, 4=INDEXED, 5=INDEXEDA)."""
        return int(self._parsed.image_type)

    @property
    def layer_names(self) -> list[str]:
        """Names of all layers (may be synthetic if real names unavailable)."""
        names = getattr(self._parsed, "layer_names", None)
        if names is None:
            return [f"Layer {i}" for i in range(self.layer_count)]
        return list(names)

    @property
    def path(self) -> str:
        """Path to the source XCF file."""
        return str(self._parsed.path or "")

    # Dimension geometry properties (FACT-XCF-001)

    @property
    def aspect_ratio(self) -> float:
        """Canvas width-to-height ratio. Returns 0.0 for zero-height images."""
        return self.width / self.height if self.height > 0 else 0.0

    @property
    def is_square(self) -> bool:
        """True if canvas width equals height."""
        return self.width == self.height

    @property
    def is_landscape(self) -> bool:
        """True if canvas width is greater than height."""
        return self.width > self.height

    @property
    def is_portrait(self) -> bool:
        """True if canvas height is greater than width."""
        return self.height > self.width

    @property
    def is_multilayer(self) -> bool:
        """True if the image has more than one layer."""
        return self.layer_count > 1

    # Additional layer and type properties (FACT-XCF-001)

    @property
    def is_flat(self) -> bool:
        """True if the image has at most one layer (not multilayer)."""
        return self.layer_count <= 1

    @property
    def has_layers(self) -> bool:
        """True if the image has at least one layer."""
        return self.layer_count > 0

    @property
    def is_rgb_type(self) -> bool:
        """True if the image type is RGB (image_type == 0)."""
        return self.image_type == 0

    def to_dict(self) -> dict[str, Any]:
        """Return image metrics as a dict."""
        return {
            "width": self.width,
            "height": self.height,
            "layer_count": self.layer_count,
            "version": self.version,
            "image_type": self.image_type,
            "layer_names": self.layer_names,
            "path": self.path,
        }

    def __repr__(self) -> str:
        return (
            f"XcfDocument(width={self.width}, height={self.height}, "
            f"layer_count={self.layer_count})"
        )
