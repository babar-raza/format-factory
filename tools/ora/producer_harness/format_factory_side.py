"""Realize a `Scene` (scene_matrix.py) as format-factory's own OraStack tree
and render it -- the side of the comparison this repository CAN fully build
and test on its own, with no external producer application involved.
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

_ORA_SRC = Path(__file__).resolve().parents[3] / "src" / "python" / "ora" / "src"
if str(_ORA_SRC) not in sys.path:
    sys.path.insert(0, str(_ORA_SRC))

from format_factory.ora import OraLayer, OraStack, render  # noqa: E402
from format_factory.ora.render import DecodedRaster  # noqa: E402

from .scene_matrix import Scene, SceneGroup, SceneLayer  # noqa: E402

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def _solid_rgba_png(width: int, height: int, rgba: tuple[int, int, int, int]) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    row = bytes([0]) + bytes(rgba) * width
    raw = row * height
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(raw)) + _chunk(b"IEND", b"")


def _build_node(item: SceneLayer | SceneGroup, members: dict[str, bytes], counter: list[int]) -> OraLayer | OraStack:
    if isinstance(item, SceneLayer):
        name = f"layer-{counter[0]}.png"
        counter[0] += 1
        members[name] = _solid_rgba_png(item.width, item.height, item.rgba)
        return OraLayer(
            src=name,
            x=item.x,
            y=item.y,
            opacity=item.opacity,
            visibility="visible" if item.visible else "hidden",
            composite_op=item.composite_op,
        )
    children = tuple(_build_node(layer, members, counter) for layer in item.layers)
    return OraStack(
        children=children,
        isolation="isolate" if item.isolated else "auto",
        opacity=item.opacity,
        composite_op=item.composite_op,
    )


def render_scene(scene: Scene) -> DecodedRaster:
    """Build `scene` with format-factory's own model classes and render it
    with format-factory's own renderer -- entirely self-contained, no file
    I/O, no producer dependency."""
    members: dict[str, bytes] = {}
    counter = [0]
    children = tuple(_build_node(item, members, counter) for item in scene.children)
    root = OraStack(children=children)
    return render(root, members, width=scene.canvas_width, height=scene.canvas_height)


__all__ = ["render_scene"]
