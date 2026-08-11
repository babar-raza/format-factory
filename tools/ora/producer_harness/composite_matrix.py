"""Composite-operation coverage extension for ORA-COMPOSITE-001's own
"complete compositing-operation inventory" release gate.

`scene_matrix.py`'s own 8-scene matrix already covers `svg:src-over`
(every scene) and `svg:multiply` (the `multiply-blend` scene) with real
two-producer pixel-exact evidence. This module covers the remaining 18
composite-op values COMPOSITE_OP_REGISTRY declares (model/composite_ops.py)
-- 13 more blend functions and all 5 non-default Porter-Duff operators --
using discriminating fixtures independently verified against
`composite_oracle.py` (a from-scratch W3C/Porter-Duff re-derivation, not
copied from render.py) before being relied on here.

Two scene families, not one, because the two producer-evidence paths
genuinely differ (see PRODUCER-MAPPING.md in this directory for the full,
empirically-verified account of which producer can create which operation
natively):

- `BLEND_SCENES`: a single opaque backdrop + single semi-transparent
  foreground, differing only in `composite_op`. The exact colors
  (backdrop=(30,200,60), source=(220,40,180) alpha=166) were chosen and
  computationally verified to produce 15 pairwise-DISTINCT results across
  every blend function in the registry -- not assumed, checked (an earlier
  candidate pair produced identical Hue and Color results, silently
  failing to discriminate them; this pair does not).
- `PORTER_DUFF_SCENES`: two partially-overlapping, differently-alpha'd
  layers (destination offset (0,0) 20x20, source offset (12,12) 20x20),
  exercising all 5 regions POL-LRA-RENDER-01's own discriminating-fixture
  requirement names (destination-only, source-only, overlap, transparent,
  partially-transparent-overlap) in one scene, independently verified via
  composite_oracle.py to produce 6 pairwise-distinct results (including
  Source Over, already covered elsewhere, as a continuity check) at the
  overlap sample point.
"""
from __future__ import annotations

from tools.ora.producer_harness.scene_matrix import Scene, SceneLayer

# ── Blend-function scenes (13 remaining of 15; Normal/Multiply already
# covered by scene_matrix.py's own scenes) ──────────────────────────────

_BLEND_BACKDROP_RGBA = (30, 200, 60, 255)
_BLEND_SOURCE_RGBA = (220, 40, 180, 166)

_REMAINING_BLEND_OPS: tuple[tuple[str, str], ...] = (
    ("screen", "svg:screen"),
    ("overlay", "svg:overlay"),
    ("darken", "svg:darken"),
    ("lighten", "svg:lighten"),
    ("color-dodge", "svg:color-dodge"),
    ("color-burn", "svg:color-burn"),
    ("hard-light", "svg:hard-light"),
    ("soft-light", "svg:soft-light"),
    ("difference", "svg:difference"),
    ("hue", "svg:hue"),
    ("saturation", "svg:saturation"),
    ("color", "svg:color"),
    ("luminosity", "svg:luminosity"),
)

BLEND_SCENES: tuple[Scene, ...] = tuple(
    Scene(
        scene_id=f"composite-blend-{slug}",
        description=(
            f"{composite_op} of two layers using the discriminating fixture "
            "(backdrop=(30,200,60) opaque, source=(220,40,180) alpha=166) "
            "independently verified via composite_oracle.py to produce 15 "
            "pairwise-distinct results across every registered blend "
            "function -- not a trivial color pair that could pass by "
            "accident."
        ),
        targets=("ORA-COMPOSITE-001",),
        canvas_width=8,
        canvas_height=8,
        children=(
            SceneLayer(name="source", rgba=_BLEND_SOURCE_RGBA, width=8, height=8, composite_op=composite_op),
            SceneLayer(name="backdrop", rgba=_BLEND_BACKDROP_RGBA, width=8, height=8),
        ),
    )
    for slug, composite_op in _REMAINING_BLEND_OPS
)

# ── Porter-Duff operator scenes (5 of 6; Source Over already covered by
# every scene in scene_matrix.py) ───────────────────────────────────────

_PD_DEST_RGBA = (230, 60, 40, 153)
_PD_SOURCE_RGBA = (40, 120, 230, 128)

_REMAINING_PORTER_DUFF_OPS: tuple[tuple[str, str], ...] = (
    ("lighter", "svg:plus"),
    ("destination-in", "svg:dst-in"),
    ("destination-out", "svg:dst-out"),
    ("source-atop", "svg:src-atop"),
    ("destination-atop", "svg:dst-atop"),
)

PORTER_DUFF_SCENES: tuple[Scene, ...] = tuple(
    Scene(
        scene_id=f"composite-porterduff-{slug}",
        description=(
            f"{composite_op} (Normal blend, no color mixing) over a "
            "destination layer (0,0)-(20,20) alpha=153 and a source layer "
            "(12,12)-(32,32) alpha=128 -- exercises destination-only "
            "(5,5), source-only (25,25), partially-transparent overlap "
            "(16,16), and fully-transparent (2,28) regions in one scene, "
            "independently verified via composite_oracle.py to produce a "
            "result at the overlap point distinct from all 5 sibling "
            "operators and from svg:src-over."
        ),
        targets=("ORA-COMPOSITE-001",),
        canvas_width=32,
        canvas_height=32,
        children=(
            SceneLayer(
                name="source", rgba=_PD_SOURCE_RGBA, width=20, height=20,
                x=12, y=12, composite_op=composite_op,
            ),
            SceneLayer(name="destination", rgba=_PD_DEST_RGBA, width=20, height=20, x=0, y=0),
        ),
    )
    for slug, composite_op in _REMAINING_PORTER_DUFF_OPS
)

ALL_COMPOSITE_SCENES: tuple[Scene, ...] = BLEND_SCENES + PORTER_DUFF_SCENES


def scene_by_id(scene_id: str) -> Scene:
    for scene in ALL_COMPOSITE_SCENES:
        if scene.scene_id == scene_id:
            return scene
    raise KeyError(f"no composite scene named {scene_id!r}")


__all__ = [
    "ALL_COMPOSITE_SCENES",
    "BLEND_SCENES",
    "PORTER_DUFF_SCENES",
    "scene_by_id",
]
