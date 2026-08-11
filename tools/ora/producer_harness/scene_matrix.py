"""Canonical scene matrix for ORA-RENDER-001 / ORA-COMPOSITE-001 /
ORA-ISOLATION-001's shared "agrees with at least two independent
producers/consumers" release gate (POL-LRA-RENDER-01 and siblings,
shared/format-contracts/policy/family-packs/layered_raster_archive.yaml --
an authorized project policy compiled into the real product contract, not
a spec-normative claim; see this session's own Workstream B finding).

Each `Scene` here is a producer-agnostic SPECIFICATION -- deterministic
pixel colors, layer geometry, opacity, composite-op, and group-isolation
declarations -- exercising exactly the semantics those 3 obligations name
in their own rule_text: clipping, order, offsets, visibility, opacity,
compositing, isolation. A scene is realized twice, independently:

1. By a real OpenRaster-producing application (GIMP, scripted -- see
   gimp_scripts/generate_scene.py), running OUTSIDE this repository's own
   code, so its output is genuinely independent of format-factory's own
   renderer.
2. By format-factory's OWN renderer, given the identical scene definition
   turned into an OraStack tree with format_factory.ora's own model
   classes.

`compare.py` then decodes producer #1's own exported PNG (or its .ora's own
embedded mergedimage.png, when full-resolution) and format-factory's own
rendered output, and reports pixel/perceptual agreement -- this is the one
piece of the release gate this repository cannot itself execute (no GIMP
install, no display server; see PROVENANCE.md and this harness's own
README.md for the exact reason and the exact external command that can).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SceneLayer:
    """One layer within a `Scene`, producer-agnostic."""

    name: str
    #: Solid RGBA fill -- deterministic, unambiguous to reproduce in any
    #: producer's own scripting API (no gradients/brushwork to disagree on).
    rgba: tuple[int, int, int, int]
    width: int
    height: int
    x: int = 0
    y: int = 0
    opacity: float = 1.0
    visible: bool = True
    composite_op: str = "svg:src-over"


@dataclass(frozen=True)
class SceneGroup:
    """A nested group of layers, optionally isolated."""

    name: str
    layers: tuple[SceneLayer, ...]
    isolated: bool = False
    opacity: float = 1.0
    composite_op: str = "svg:src-over"


@dataclass(frozen=True)
class Scene:
    scene_id: str
    description: str
    #: Which of the 3 shared-release-gate obligations this scene targets.
    targets: tuple[str, ...]
    canvas_width: int
    canvas_height: int
    #: Top-level children, top (visually uppermost) first -- matches
    #: OpenRaster's own "first child is uppermost" convention.
    children: tuple[SceneLayer | SceneGroup, ...] = field(default_factory=tuple)


# ── The canonical scene set ──────────────────────────────────────────────
#
# Kept intentionally small and orthogonal (one clearly-dominant semantic
# per scene) rather than large and combinatorial -- a disagreement in a
# 2-scene comparison is easy to diagnose; a disagreement in a 20-layer
# combinatorial scene is not. Extending this matrix (more blend modes, more
# nesting depth) is straightforward once the harness is proven end-to-end
# on these.

SCENES: tuple[Scene, ...] = (
    Scene(
        scene_id="single-opaque-layer",
        description="One fully opaque layer covering the canvas -- the trivial base case.",
        targets=("ORA-RENDER-001",),
        canvas_width=64,
        canvas_height=64,
        children=(
            SceneLayer(name="base", rgba=(200, 30, 30, 255), width=64, height=64),
        ),
    ),
    Scene(
        scene_id="layer-order",
        description="Two fully opaque layers overlapping by half the canvas -- proves "
        "visual stacking order (first child = uppermost) agrees across producers.",
        targets=("ORA-RENDER-001",),
        canvas_width=64,
        canvas_height=64,
        children=(
            SceneLayer(name="top", rgba=(0, 200, 0, 255), width=48, height=48, x=16, y=16),
            SceneLayer(name="bottom", rgba=(0, 0, 200, 255), width=48, height=48, x=0, y=0),
        ),
    ),
    Scene(
        scene_id="partial-opacity",
        description="An 80%-opacity semi-transparent layer over an opaque background -- "
        "the exact scenario this package's own hand-verified alpha-compositing tests use, "
        "now against a second, independently-rendered producer instead of arithmetic alone.",
        targets=("ORA-RENDER-001", "ORA-COMPOSITE-001"),
        canvas_width=64,
        canvas_height=64,
        children=(
            SceneLayer(name="fg", rgba=(0, 0, 255, 200), width=64, height=64, opacity=0.8),
            SceneLayer(name="bg", rgba=(255, 255, 255, 255), width=64, height=64),
        ),
    ),
    Scene(
        scene_id="offset-and-clipping",
        description="A layer offset partially off-canvas -- proves clipping at the canvas "
        "boundary agrees, not merely full-canvas layers.",
        targets=("ORA-RENDER-001",),
        canvas_width=32,
        canvas_height=32,
        children=(
            SceneLayer(name="clipped", rgba=(255, 128, 0, 255), width=24, height=24, x=-8, y=-8),
        ),
    ),
    Scene(
        scene_id="hidden-layer",
        description="A hidden layer over a visible one -- proves visibility=hidden is "
        "excluded from compositing identically across producers.",
        targets=("ORA-RENDER-001",),
        canvas_width=32,
        canvas_height=32,
        children=(
            SceneLayer(name="hidden", rgba=(255, 0, 0, 255), width=32, height=32, visible=False),
            SceneLayer(name="visible", rgba=(0, 255, 0, 255), width=32, height=32),
        ),
    ),
    Scene(
        scene_id="multiply-blend",
        description="svg:multiply of two fully opaque layers -- one of the composite-op "
        "family ORA-COMPOSITE-001's own rule_text names explicitly.",
        targets=("ORA-COMPOSITE-001",),
        canvas_width=32,
        canvas_height=32,
        children=(
            SceneLayer(
                name="top", rgba=(200, 50, 10, 255), width=32, height=32,
                composite_op="svg:multiply",
            ),
            SceneLayer(name="bottom", rgba=(100, 250, 90, 255), width=32, height=32),
        ),
    ),
    Scene(
        scene_id="isolated-group-with-opacity",
        description="Two overlapping opaque children inside an isolated group at group "
        "opacity 0.5, over an opaque backdrop -- the exact scenario this package's own "
        "hand-verified isolation test uses (top must fully occlude bottom BEFORE the "
        "group's own opacity is applied, since isolation composites the flattened group "
        "as one unit against the backdrop, not each child independently).",
        targets=("ORA-ISOLATION-001",),
        canvas_width=32,
        canvas_height=32,
        children=(
            SceneGroup(
                name="isolated",
                isolated=True,
                opacity=0.5,
                layers=(
                    SceneLayer(name="top", rgba=(255, 0, 0, 255), width=32, height=32),
                    SceneLayer(name="bottom", rgba=(0, 255, 0, 255), width=32, height=32),
                ),
            ),
            SceneLayer(name="backdrop", rgba=(0, 0, 0, 255), width=32, height=32),
        ),
    ),
    Scene(
        scene_id="non-isolated-group",
        description="The same group opacity (0.5) and backdrop as isolated-group-with-opacity, "
        "but WITHOUT isolation, and with a semi-transparent (not fully opaque) top child --"
        "deliberately NOT the same layer alphas as the isolated scene: two fully-opaque "
        "same-size children mathematically produce an IDENTICAL result whether isolated or "
        "not (nothing shows through either way), so that combination cannot discriminate the "
        "two modes at all. Partial transparency is what makes isolated vs. non-isolated "
        "compositing actually diverge -- matching this package's own "
        "test_non_isolated_auto_group_is_equivalent_to_no_group_at_all, which uses the same "
        "reasoning to choose its own fixture values.",
        targets=("ORA-ISOLATION-001",),
        canvas_width=32,
        canvas_height=32,
        children=(
            SceneGroup(
                name="not-isolated",
                isolated=False,
                opacity=0.5,
                layers=(
                    SceneLayer(name="top", rgba=(255, 0, 0, 160), width=32, height=32),
                    SceneLayer(name="bottom", rgba=(0, 255, 0, 255), width=32, height=32),
                ),
            ),
            SceneLayer(name="backdrop", rgba=(0, 0, 0, 255), width=32, height=32),
        ),
    ),
)


def scene_by_id(scene_id: str) -> Scene:
    for scene in SCENES:
        if scene.scene_id == scene_id:
            return scene
    raise KeyError(f"no scene named {scene_id!r}")


__all__ = ["Scene", "SceneGroup", "SceneLayer", "SCENES", "scene_by_id"]
