"""ORA-DOCUMENT-001 — the image document and canvas model.

"The root image element requires positive integer w and h attributes and a
version string identifying the OpenRaster specification profile."

"Since profile 0.0.3, xres and yres are optional positive integer
pixels-per-inch values that must be specified together and default to 72."
"""

from __future__ import annotations

from dataclasses import dataclass

from .stack import OraStack

#: The specification's resolution default when xres/yres are absent.
DEFAULT_RESOLUTION_PPI = 72


@dataclass(frozen=True)
class OraDocument:
    """A parsed OpenRaster document: canvas, profile, resolution, root stack."""

    width: int
    height: int
    version: str
    root: OraStack
    xres: int = DEFAULT_RESOLUTION_PPI
    yres: int = DEFAULT_RESOLUTION_PPI

    @property
    def pixel_count(self) -> int:
        """Canvas area. Validated with checked arithmetic at parse time, so this
        is safe to use for allocation sizing."""
        return self.width * self.height


__all__ = ["DEFAULT_RESOLUTION_PPI", "OraDocument"]
