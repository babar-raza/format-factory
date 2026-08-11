#!/usr/bin/env python2
"""GIMP Python-Fu script: realize one scene from ../scene_matrix.py as a
real GIMP image and export it as OpenRaster (.ora), independently of
format-factory's own code.

This file runs INSIDE GIMP's own bundled Python-Fu interpreter (GIMP <= 2.10
ships Python 2.7; GIMP 3.x's GObject-Introspection API differs -- see
../README.md for the exact version this script targets and the GIMP 3.x
migration note). It is not importable by format-factory's own test suite or
CI (no `gimpfu` module exists outside a real GIMP install) -- that is by
design: this script's own correctness can only be fully proven by actually
running it inside GIMP, which this repository's own sandboxed environment
cannot do (no GIMP install, no display server; see ../README.md).

Usage (headless, batch mode, one scene per invocation):

    gimp -i -b '(python-fu-generate-scene RUN-NONINTERACTIVE
                  "single-opaque-layer" "/out/single-opaque-layer.ora")'
        -b '(gimp-quit 0)'

`scene_id` must match one of scene_matrix.SCENES's own `scene_id` values --
this script re-derives the SAME scene data GIMP-side via a small, deliberately
duplicated (not imported) copy of the matrix below, so the two sides stay
independently reviewable rather than one silently trusting the other's
Python 2/3 import at GIMP-script-authoring time. If the matrix changes,
both copies must be updated together -- `../compare.py`'s own
`assert_scene_matrices_agree()` test (mocked, run from this repo's own CI)
catches drift between them without needing GIMP installed.
"""

from __future__ import print_function

from gimpfu import (  # noqa: F401  (only resolvable inside a real GIMP install)
    RGBA_IMAGE,
    LAYER_MODE_NORMAL,
    LAYER_MODE_MULTIPLY,
    main,
    pdb,
    register,
    PF_STRING,
)

# Deliberately duplicated from scene_matrix.py, not imported -- GIMP's own
# Python-Fu interpreter cannot import this repository's format_factory
# package (no such dependency inside GIMP's bundled interpreter), and a
# script this consequential should not depend on format-factory's own code
# being importable to construct the INDEPENDENT side of the comparison.
SCENES = {
    "single-opaque-layer": {
        "width": 64, "height": 64,
        "layers": [
            {"rgba": (200, 30, 30, 255), "w": 64, "h": 64, "x": 0, "y": 0, "opacity": 100, "visible": True, "mode": LAYER_MODE_NORMAL},
        ],
    },
    "layer-order": {
        "width": 64, "height": 64,
        "layers": [
            {"rgba": (0, 200, 0, 255), "w": 48, "h": 48, "x": 16, "y": 16, "opacity": 100, "visible": True, "mode": LAYER_MODE_NORMAL},
            {"rgba": (0, 0, 200, 255), "w": 48, "h": 48, "x": 0, "y": 0, "opacity": 100, "visible": True, "mode": LAYER_MODE_NORMAL},
        ],
    },
    "partial-opacity": {
        "width": 64, "height": 64,
        "layers": [
            {"rgba": (0, 0, 255, 200), "w": 64, "h": 64, "x": 0, "y": 0, "opacity": 80, "visible": True, "mode": LAYER_MODE_NORMAL},
            {"rgba": (255, 255, 255, 255), "w": 64, "h": 64, "x": 0, "y": 0, "opacity": 100, "visible": True, "mode": LAYER_MODE_NORMAL},
        ],
    },
    "offset-and-clipping": {
        "width": 32, "height": 32,
        "layers": [
            {"rgba": (255, 128, 0, 255), "w": 24, "h": 24, "x": -8, "y": -8, "opacity": 100, "visible": True, "mode": LAYER_MODE_NORMAL},
        ],
    },
    "hidden-layer": {
        "width": 32, "height": 32,
        "layers": [
            {"rgba": (255, 0, 0, 255), "w": 32, "h": 32, "x": 0, "y": 0, "opacity": 100, "visible": False, "mode": LAYER_MODE_NORMAL},
            {"rgba": (0, 255, 0, 255), "w": 32, "h": 32, "x": 0, "y": 0, "opacity": 100, "visible": True, "mode": LAYER_MODE_NORMAL},
        ],
    },
    "multiply-blend": {
        "width": 32, "height": 32,
        "layers": [
            {"rgba": (200, 50, 10, 255), "w": 32, "h": 32, "x": 0, "y": 0, "opacity": 100, "visible": True, "mode": LAYER_MODE_MULTIPLY},
            {"rgba": (100, 250, 90, 255), "w": 32, "h": 32, "x": 0, "y": 0, "opacity": 100, "visible": True, "mode": LAYER_MODE_NORMAL},
        ],
    },
    # isolated-group-with-opacity / non-isolated-group need GIMP layer
    # GROUPS (gimp-image-insert-layer with a group parent,
    # gimp-item-set-visible / gimp-layer-set-opacity on the GROUP item
    # itself) rather than flat layers -- left as a documented extension
    # point (see ../README.md "Known gaps") since GIMP's own group-opacity
    # -vs-OpenRaster-isolation-attribute mapping needs to be verified
    # against a real GIMP install's actual .ora export before this script
    # can claim it reproduces scene_matrix.py's own isolation semantics
    # correctly -- exactly the kind of claim this harness's own discipline
    # (never assume, verify against real output) refuses to make blind.
}


def generate_scene(run_mode, scene_id, output_path):
    if scene_id not in SCENES:
        raise ValueError("unknown scene_id: %r (isolation scenes not yet scripted -- see module docstring)" % scene_id)
    spec = SCENES[scene_id]
    image = pdb.gimp_image_new(spec["width"], spec["height"], RGBA_IMAGE)

    # Reverse order: GIMP's own layer stack is also top-first, matching
    # OpenRaster's "first child is uppermost" -- inserting in the SAME
    # order scene_matrix.py declares children keeps both sides' own visual
    # stacking order identical without needing to reverse anything.
    for layer_spec in spec["layers"]:
        layer = pdb.gimp_layer_new(
            image, layer_spec["w"], layer_spec["h"], RGBA_IMAGE,
            "layer", layer_spec["opacity"], layer_spec["mode"],
        )
        pdb.gimp_image_insert_layer(image, layer, None, 0)
        pdb.gimp_layer_set_offsets(layer, layer_spec["x"], layer_spec["y"])
        pdb.gimp_image_set_active_layer(image, layer)
        r, g, b, a = layer_spec["rgba"]
        pdb.gimp_context_set_foreground((r, g, b))
        pdb.gimp_layer_add_alpha(layer)
        pdb.gimp_image_select_rectangle(image, 2, 0, 0, layer_spec["w"], layer_spec["h"])
        pdb.gimp_edit_fill(layer, 0)  # FILL-FOREGROUND
        if a < 255:
            pdb.gimp_layer_set_opacity(layer, layer_spec["opacity"] * (a / 255.0))
        pdb.gimp_selection_none(image)
        pdb.gimp_item_set_visible(layer, layer_spec["visible"])

    pdb.gimp_image_flatten_layer_group_check = None  # no-op placeholder; groups not yet scripted
    pdb.file_openraster_save(image, image.active_drawable, output_path, scene_id)
    pdb.gimp_image_delete(image)
    return output_path


register(
    "python-fu-generate-scene",
    "Generate one canonical ORA scene as OpenRaster, independent of format-factory's own code",
    "Generate one canonical ORA scene as OpenRaster, independent of format-factory's own code",
    "format-factory project",
    "Apache-2.0",
    "2026-08-11",
    "<Toolbox>/Filters/Format Factory ORA Harness/Generate Scene...",
    "",
    [
        (PF_STRING, "scene-id", "Scene ID (see scene_matrix.py)", "single-opaque-layer"),
        (PF_STRING, "output-path", "Output .ora path", "/tmp/scene.ora"),
    ],
    [],
    generate_scene,
)

main()
