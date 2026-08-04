"""OpenRaster codec: archive container reading and writing."""

from __future__ import annotations

from .container import (
    ALLOWED_COMPRESSION,
    MIMETYPE_MEMBER,
    OPENRASTER_MEDIA_TYPE,
    STACK_MEMBER,
    OraContainer,
)
from .assets import (
    MERGED_IMAGE_MEMBER,
    THUMBNAIL_MEMBER,
    ResolvedAsset,
    iter_layers,
    resolve_all_assets,
    resolve_asset,
)
from .png_metadata import PNG_SIGNATURE, RasterMetadata, read_png_metadata
from .stack_xml import ROOT_ELEMENT, parse_stack

__all__ = [
    "ALLOWED_COMPRESSION",
    "MIMETYPE_MEMBER",
    "OPENRASTER_MEDIA_TYPE",
    "STACK_MEMBER",
    "OraContainer",
    "MERGED_IMAGE_MEMBER",
    "PNG_SIGNATURE",
    "ResolvedAsset",
    "THUMBNAIL_MEMBER",
    "iter_layers",
    "resolve_all_assets",
    "resolve_asset",
    "RasterMetadata",
    "ROOT_ELEMENT",
    "read_png_metadata",
    "parse_stack",
]
