"""
XCF structural element: xcf:header

Spec ref: GIMP XCF file format — file header
Fact ref: SAL-XCF-00001
QName: xcf:header
Canonical class: Header
Facade: XcfHeader
"""
from __future__ import annotations
from typing import Any, ClassVar


class Header:
    """Canonical spec-shaped class for xcf:header (XCF file header)."""

    spec_qname: ClassVar[str] = "xcf:header"
    spec_fact_ref: ClassVar[str] = "SAL-XCF-00001"
    namespace_uri: ClassVar[str] = "urn:format:gimp:xcf:1.0"
    local_name: ClassVar[str] = "header"
    facade_names: ClassVar[list] = ["XcfHeader"]

    MAGIC = b"gimp xcf "

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def version(self) -> str:
        """Return the XCF version string (e.g. 'v011')."""
        return str(self._data.get("version", ""))

    @property
    def width(self) -> int:
        """Return the canvas width in pixels."""
        return int(self._data.get("width", 0))

    @property
    def height(self) -> int:
        """Return the canvas height in pixels."""
        return int(self._data.get("height", 0))

    @property
    def color_mode(self) -> int:
        """Return the color mode integer (0=RGB, 1=GRAYSCALE, 2=INDEXED)."""
        return int(self._data.get("color_mode", 0))

    @property
    def layer_count(self) -> int:
        """Return the number of layers in the file."""
        return int(self._data.get("layer_count", 0))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(version={self.version!r}, width={self.width}, height={self.height}, layers={self.layer_count})"
