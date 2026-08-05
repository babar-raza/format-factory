"""format-factory-ora — OpenRaster layered raster archives.

OpenRaster is a ZIP archive holding an ordered layer tree (`stack.xml`), the
layer rasters it references, and flattened viewing assets. This package reads,
validates, edits and writes those documents.

Archive members and XML are untrusted passive data: parsing never executes
embedded content and never resolves network resources.

Specification: freedesktop.org (community) OpenRaster 0.0.5,
commit f050b99fa8af44cb4cc3c9d842d25097458765f6.
"""

from __future__ import annotations

from .codec import (
    OPENRASTER_MEDIA_TYPE,
    OraContainer,
    RasterMetadata,
    ResolvedAsset,
    parse_stack,
    read_png_metadata,
    resolve_all_assets,
    resolve_asset,
)
from .model import OraDocument, OraLayer, OraNode, OraStack, OraText
from .lifecycle import (
    OraImage,
    PreservationMode,
    ReadMode,
    dump,
    dumps,
    load,
    loads,
    validate,
)
from .errors import OraArchiveError, OraError, OraLimitError, OraValidationError

__version__ = "0.1.0.dev0"

__all__ = [
    "OPENRASTER_MEDIA_TYPE",
    "OraArchiveError",
    "OraContainer",
    "OraDocument",
    "OraError",
    "OraImage",
    "OraLayer",
    "OraNode",
    "OraStack",
    "OraText",
    "PreservationMode",
    "RasterMetadata",
    "ReadMode",
    "ResolvedAsset",
    "OraLimitError",
    "OraValidationError",
    "__version__",
    "dump",
    "dumps",
    "load",
    "loads",
    "parse_stack",
    "read_png_metadata",
    "resolve_all_assets",
    "resolve_asset",
    "validate",
]
