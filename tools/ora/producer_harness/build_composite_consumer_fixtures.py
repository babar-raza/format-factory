"""Author real, strict-mode-passing .ora files for the 5 Porter-Duff
operators no real OpenRaster-producing application this session found
(GIMP, Krita) can create natively -- confirmed empirically, not assumed
(see gimp_scripts/probe_blend_semantics.scm and
krita/scripts/probe_blend_semantics.py: neither GIMP's own layer-mode
system nor Krita's own blendingMode() exposes Porter-Duff-operator
selection at all; both always composite with implicit Source Over
regardless of blend mode).

Per this session's own directive (Workstream A2): "If a producer cannot
natively create an operation but can import and render it... generate a
strict ORA through the format-factory writer, then have GIMP and Krita
independently open and render it. Label this evidence
INDEPENDENT_CONSUMER_RENDER, not PRODUCER_NATIVE_EXPORT." This script is
that writer -- format_factory.ora.lifecycle.dumps(preservation=CANONICAL)
regenerates a real stack.xml from an in-memory OraDocument model (not a
byte-preserving round-trip of an existing file), which is exactly the
"format-factory writer" capability that directive assumes exists.
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

_ORA_SRC = Path(__file__).resolve().parents[3] / "src" / "python" / "ora" / "src"
if str(_ORA_SRC) not in sys.path:
    sys.path.insert(0, str(_ORA_SRC))

from format_factory.ora import OraLayer, OraStack  # noqa: E402
from format_factory.ora.lifecycle import (  # noqa: E402
    OraImage,
    PreservationMode,
    dumps,
)
from format_factory.ora.model.document import OraDocument  # noqa: E402
from format_factory.ora.render import generate_baseline_assets  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from tools.ora.producer_harness.composite_matrix import PORTER_DUFF_SCENES  # noqa: E402

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data)) + kind + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def _solid_rgba_png(width: int, height: int, rgba: tuple[int, int, int, int]) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    row = bytes([0]) + bytes(rgba) * width
    raw = row * height
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(raw)) + _chunk(b"IEND", b"")


def build_fixture(scene) -> bytes:
    """Build a real, strict-mode-passing .ora archive for one
    composite_matrix.Scene, using format-factory's own writer end to end
    (dumps(CANONICAL) for stack.xml, generate_baseline_assets for the
    required thumbnail/mergedimage) -- not a hand-assembled ZIP."""
    members: dict[str, bytes] = {}
    children = []
    for item in scene.children:
        name = f"{item.name}.png"
        members[name] = _solid_rgba_png(item.width, item.height, item.rgba)
        children.append(
            OraLayer(
                src=name, x=item.x, y=item.y, opacity=item.opacity,
                visibility="visible" if item.visible else "hidden",
                composite_op=item.composite_op,
            )
        )
    root = OraStack(children=tuple(children))
    document = OraDocument(width=scene.canvas_width, height=scene.canvas_height, version="0.0.4", root=root)

    thumbnail, merged = generate_baseline_assets(document, members)
    members["Thumbnails/thumbnail.png"] = thumbnail
    members["mergedimage.png"] = merged
    image = OraImage(document=document, members=members)

    return dumps(image, preservation=PreservationMode.CANONICAL)


def main() -> None:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    for scene in PORTER_DUFF_SCENES:
        data = build_fixture(scene)
        path = out_dir / f"{scene.scene_id}.ora"
        path.write_bytes(data)
        print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
