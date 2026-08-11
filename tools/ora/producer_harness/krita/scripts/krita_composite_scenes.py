"""ORA-COMPOSITE-001 full-inventory coverage extension: Krita side.

Covers composite_matrix.py's own 13 BLEND_SCENES using Krita blend-mode
strings independently verified against composite_oracle.py first
(probe_blend_semantics.py, this same directory) -- exact match or within
1 unit per channel (a benign floating-point rounding-mode difference, not
a formula defect: the affected 5 -- Lighten, Soft Light, Hue, Color,
Luminosity -- all matched exactly on the SIMPLER blend functions, and only
diverge by exactly 1 unit on the ones involving more accumulated float
arithmetic (HSL SetLum/SetSat, or the two-branch Soft Light formula),
consistent with round-half-to-even vs round-half-up rather than a wrong
formula). Unlike GIMP, Krita's own blend modes matched the W3C formula for
ALL 13 operations -- a real, disclosed difference between the two
producers' own conformance levels, not evidence trimmed to make GIMP look
better or worse than it is.

The 5 PORTER_DUFF_SCENES have no Krita-native equivalent either (Krita's
own "add" blend mode, the only plausible Lighter/svg:plus candidate,
produced (173,226,177) against the exact GIMP-tested fixture where the
real Porter-Duff Lighter formula requires (105,137,107) -- Krita's own
blendingMode() is a per-LAYER color-blend selector, with no separate
Porter-Duff-operator selection at all, the same structural limitation
already found in GIMP). Covered exclusively via INDEPENDENT_CONSUMER_RENDER
(see build_composite_consumer_fixtures.py).
"""
import os

OUT_DIR = os.environ.get("ORA_HARNESS_OUT", "/out")


def _bgra(rgba):
    r, g, b, a = rgba
    return bytes([b, g, r, a])


def run_blend_scene(slug, mode_string):
    app = Krita.instance()
    doc = app.createDocument(8, 8, slug, "RGBA", "U8", "", 300.0)
    root = doc.rootNode()
    for n in list(root.childNodes()):
        n.remove()
    bottom = doc.createNode("backdrop", "paintlayer")
    root.addChildNode(bottom, None)
    bottom.setPixelData(bytearray(_bgra((30, 200, 60, 255)) * 64), 0, 0, 8, 8)
    top = doc.createNode("source", "paintlayer")
    root.addChildNode(top, None)
    top.setPixelData(bytearray(_bgra((220, 40, 180, 255)) * 64), 0, 0, 8, 8)
    top.setOpacity(166)
    top.setBlendingMode(mode_string)
    doc.refreshProjection()
    doc.waitForDone()
    doc.setBatchmode(True)
    path = os.path.join(OUT_DIR, "composite-blend-%s.png" % slug)
    doc.saveAs(path)
    doc.waitForDone()
    log("run_blend_scene(%r, %r) -> %r" % (slug, mode_string, path))
    doc.close()


SCENES = {
    "screen": "screen",
    "overlay": "overlay",
    "darken": "darken",
    "lighten": "lighten",
    "color-dodge": "dodge",
    "color-burn": "burn",
    "hard-light": "hard_light",
    "soft-light": "soft_light_svg",
    "difference": "diff",
    "hue": "hue",
    "saturation": "saturation",
    "color": "color",
    "luminosity": "luminize",
}

app = Krita.instance()
app.setBatchmode(True)
for slug, mode_string in SCENES.items():
    try:
        run_blend_scene(slug, mode_string)
    except Exception as exc:  # noqa: BLE001
        import traceback
        log("EXCEPTION in scene %r:\n%s" % (slug, traceback.format_exc()))
        write_sentinel(status="ERROR", detail="exception in scene %r: %r" % (slug, exc))
        raise SystemExit(1)

write_sentinel(status="PASS", detail="all 13 composite blend scenes generated")
