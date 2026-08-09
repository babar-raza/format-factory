"""Resolve a layer's raster reference against the archive (ORA-ASSET-001).

The metadata reader answers "what does this PNG declare"; this answers "which
member does this layer point at, and is it there". Keeping the join here rather
than leaving it to callers is the point of the obligation: "resolve
archive-root-relative asset references safely" is a property of the library, not
a convention each caller reimplements.
"""

from __future__ import annotations

from dataclasses import dataclass

from format_factory.core import DEFAULT_LIMITS, ResourceLimits

from ..errors import OraValidationError
from ..model.stack import OraLayer, OraStack, OraText
from .container import OraContainer
from .png_metadata import RasterMetadata, read_png_metadata

THUMBNAIL_MEMBER = "Thumbnails/thumbnail.png"
MERGED_IMAGE_MEMBER = "mergedimage.png"


@dataclass(frozen=True)
class ResolvedAsset:
    """A layer's raster, located in the archive and described without decoding."""

    src: str
    metadata: RasterMetadata

    @property
    def declared_byte_size(self) -> int:
        """The raster's byte size as declared by its own PNG metadata,
        without decoding the pixel data."""
        return self.metadata.declared_byte_size


def resolve_asset(
    container: OraContainer,
    layer: OraLayer | OraText,
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> ResolvedAsset:
    """Locate a layer's raster and read its metadata.

    Member lookup is exact: "Member names ... are case-sensitive", so a layer
    referencing `data/Layer.png` does not resolve to `data/layer.png`. Silently
    case-folding here would make a document render differently depending on the
    filesystem it was extracted on.
    """
    src = layer.src
    if not src:
        raise OraValidationError(
            f"layer {layer.name!r} has no src and cannot be resolved to a raster"
        )

    if src not in container.names:
        raise OraValidationError(
            f"layer {layer.name!r} references {src!r}, which is not a member of "
            "the archive"
        )

    return ResolvedAsset(src=src, metadata=read_png_metadata(container.read(src), limits=limits))


def iter_layers(stack: OraStack) -> list[OraLayer]:
    """Every layer in the tree, in visual order, depth-first.

    Order is preserved rather than convenient: it is the order these composite
    in, and a caller resolving assets to render depends on it.
    """
    found: list[OraLayer] = []
    for child in stack.children:
        if isinstance(child, OraStack):
            found.extend(iter_layers(child))
        elif isinstance(child, OraLayer):
            found.append(child)
    return found


def resolve_all_assets(
    container: OraContainer,
    stack: OraStack,
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> list[ResolvedAsset]:
    """Resolve every layer's raster, in visual order.

    Fails on the first unresolvable reference rather than returning a partial
    list: a document missing one of its layers is not a document a caller can
    render correctly, and returning most of it invites exactly that.
    """
    return [resolve_asset(container, layer, limits=limits) for layer in iter_layers(stack)]


__all__ = [
    "MERGED_IMAGE_MEMBER",
    "THUMBNAIL_MEMBER",
    "ResolvedAsset",
    "iter_layers",
    "resolve_all_assets",
    "resolve_asset",
]
