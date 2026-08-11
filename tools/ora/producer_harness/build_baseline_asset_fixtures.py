"""Generate real thumbnail.png / mergedimage.png baseline assets via
format-factory's own writer, for ORA-BASELINEASSET-001's amended
visual-assurance procedure (see
reports/format-contract-layer/ora-baseline-asset-visual-assurance-amendment.md).

Uses scenes already independently verified by this session's own
Workstream A oracle/GIMP/Krita pipeline (scene_matrix.SCENES), so the
question "is this the right image" is already answered -- this script
isolates the encoding path specifically: generate_baseline_assets()
(render.py:1055), which neither this harness's own scene-matrix
comparison (format_factory_side.render_scene) nor any composite-op proof
this session built has ever exercised (both stop at the in-memory
DecodedRaster returned by render(), never calling encode_png() or
generate_thumbnail()).
"""
from __future__ import annotations

import json
import struct
import sys
import zlib
from pathlib import Path

_ORA_SRC = Path(__file__).resolve().parents[3] / "src" / "python" / "ora" / "src"
if str(_ORA_SRC) not in sys.path:
    sys.path.insert(0, str(_ORA_SRC))

from format_factory.ora.model.document import OraDocument  # noqa: E402
from format_factory.ora.model.stack import OraLayer, OraStack  # noqa: E402
from format_factory.ora.render import decode_png, generate_baseline_assets  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from tools.ora.producer_harness.scene_matrix import (  # noqa: E402
    SCENES,
    Scene,
    SceneGroup,
    SceneLayer,
)

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


def _build_node(item, members: dict, counter: list) -> OraLayer | OraStack:
    if isinstance(item, SceneLayer):
        name = f"layer-{counter[0]}.png"
        counter[0] += 1
        members[name] = _solid_rgba_png(item.width, item.height, item.rgba)
        return OraLayer(
            src=name, x=item.x, y=item.y, opacity=item.opacity,
            visibility="visible" if item.visible else "hidden",
            composite_op=item.composite_op,
        )
    assert isinstance(item, SceneGroup)
    children = tuple(_build_node(layer, members, counter) for layer in item.layers)
    return OraStack(
        children=children, isolation="isolate" if item.isolated else "auto",
        opacity=item.opacity, composite_op=item.composite_op,
    )


def build(scene: Scene) -> dict:
    members: dict[str, bytes] = {}
    counter = [0]
    children = tuple(_build_node(item, members, counter) for item in scene.children)
    root = OraStack(children=children)
    document = OraDocument(
        width=scene.canvas_width, height=scene.canvas_height, version="0.0.4", root=root
    )
    thumbnail_bytes, merged_bytes = generate_baseline_assets(document, members)
    thumb_raster = decode_png(thumbnail_bytes)
    merged_raster = decode_png(merged_bytes)
    assert thumb_raster.pixels == merged_raster.pixels, (
        f"{scene.scene_id}: thumbnail/mergedimage diverge unexpectedly for a "
        "scene within THUMBNAIL_MAX_EDGE -- scope assumption violated"
    )
    return {
        "scene_id": scene.scene_id,
        "width": scene.canvas_width,
        "height": scene.canvas_height,
        "thumbnail_bytes": thumbnail_bytes,
        "merged_bytes": merged_bytes,
        "expected_pixels_hex": merged_raster.pixels.hex(),
    }


def main() -> None:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    scene_ids = sys.argv[2:] if len(sys.argv) > 2 else ["multiply-blend", "layer-order"]
    out_dir.mkdir(parents=True, exist_ok=True)
    by_id = {s.scene_id: s for s in SCENES}
    manifest = []
    for scene_id in scene_ids:
        scene = by_id[scene_id]
        result = build(scene)
        (out_dir / f"thumbnail-{scene_id}.png").write_bytes(result["thumbnail_bytes"])
        (out_dir / f"mergedimage-{scene_id}.png").write_bytes(result["merged_bytes"])
        manifest.append({
            "scene_id": scene_id,
            "width": result["width"],
            "height": result["height"],
            "expected_pixels_hex": result["expected_pixels_hex"],
        })
        print(f"wrote {scene_id}: thumbnail={len(result['thumbnail_bytes'])}B "
              f"merged={len(result['merged_bytes'])}B")
    (out_dir / "expected-manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
