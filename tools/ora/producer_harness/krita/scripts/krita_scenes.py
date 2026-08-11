"""ORA harness Krita driver -- REAL 8-scene matrix, mirroring
../../gimp_scripts/generate_scenes.scm and ../../scene_matrix.py's own
canonical values exactly. Deliberately duplicates scene data (this file
cannot import scene_matrix.py -- it runs inside Krita's own bundled Python
interpreter, with no access to this repository's own package layout) --
kept in sync manually, matching the same discipline already established for
the GIMP lane's own generate_scenes.scm.

Every API call below was empirically verified against this exact real
Krita 5.0.2 install before being relied on here (see probe_groups.py,
probe_blendmode.py, probe_multiply.py, probe_opacity.py in this same
directory, and PROVENANCE-krita-execution-2026-08-12.md for the full
account):

- createDocument() auto-creates a default "Background" layer (opacity=0,
  fully transparent but still an extra node) -- removed explicitly here so
  every scene has exactly the layers it declares, nothing extra.
- Node.addChildNode(node, None) inserts the new node as the new TOPMOST
  layer each time (confirmed: after addChildNode(bottom, None) then
  addChildNode(top, None), the exported stack.xml lists top first, matching
  OpenRaster's own "first child is uppermost" convention) -- so children
  are added here in BOTTOM-TO-TOP order (reversed from this file's own
  top-first declaration order, matching scene_matrix.py's own convention).
- Node.setPixelData(bytes, x, y, w, h) expects BGRA byte order per pixel
  (confirmed: RGBA colors set this way round-tripped correctly through a
  real Krita export and a fresh-process re-export via format-factory's own
  decoder).
- Node.setOpacity() takes an INTEGER 0-255 (confirmed: setOpacity(128) ->
  exported stack.xml opacity="0.501961", i.e. 128/255 -- NOT a 0-100
  percentage, NOT a 0.0-1.0 float).
- Node.setBlendingMode("multiply") exports as the real, standard
  composite-op="svg:multiply" -- confirmed directly by reading the real
  exported stack.xml, not assumed from the string's own plausibility.
- Krita's own real .ora GROUP export ALWAYS writes isolation="isolate"
  literally, regardless of the group's own blendingMode (confirmed: a
  fresh default-mode group and a "pass through"-mode group both exported
  isolation="isolate"; "pass through" mode instead changes composite-op to
  the NON-STANDARD "krita:pass through", which independently ALSO forces
  is_isolated_group=True in format-factory's own reader via its own
  composite-op-differs-from-default rule). This means Krita's own group
  mechanism cannot produce a genuinely non-isolated group at all -- the
  IDENTICAL conclusion already reached and fixed for the GIMP lane (see
  scene_matrix.py's own "non-isolated-group" docstring), for a different
  underlying reason. The fix is the same: non-isolated-group is scripted
  here with NO Krita group node at all, matching the already-verified
  "equivalent to no group at all" principle.
"""
import os

OUT_DIR = os.environ.get("ORA_HARNESS_OUT", "/out")


def _clear_default_layers(doc):
    root = doc.rootNode()
    for node in list(root.childNodes()):
        node.remove()
    return root


def _bgra(rgba):
    r, g, b, a = rgba
    return bytes([b, g, r, a])


def _make_layer(doc, parent, name, rgba, x, y, w, h, opacity=1.0, visible=True, composite_op="svg:src-over"):
    layer = doc.createNode(name, "paintlayer")
    parent.addChildNode(layer, None)
    layer.setPixelData(bytearray(_bgra(rgba) * (w * h)), x, y, w, h)
    layer.setOpacity(round(opacity * 255))
    layer.setVisible(visible)
    if composite_op == "svg:multiply":
        layer.setBlendingMode("multiply")
    elif composite_op != "svg:src-over":
        raise ValueError("unhandled composite_op for this scene matrix: %r" % (composite_op,))
    return layer


def _export(doc, scene_id):
    doc.refreshProjection()
    doc.waitForDone()
    doc.setBatchmode(True)
    kra_path = os.path.join(OUT_DIR, "%s.kra" % scene_id)
    ora_path = os.path.join(OUT_DIR, "%s.ora" % scene_id)
    ok_kra = doc.saveAs(kra_path)
    doc.waitForDone()
    ok_ora = doc.saveAs(ora_path)
    doc.waitForDone()
    log("%s: saveAs .kra -> %r, .ora -> %r" % (scene_id, ok_kra, ok_ora))
    doc.close()


def run_single_opaque_layer():
    doc = Krita.instance().createDocument(64, 64, "single-opaque-layer", "RGBA", "U8", "", 300.0)
    root = _clear_default_layers(doc)
    _make_layer(doc, root, "base", (200, 30, 30, 255), 0, 0, 64, 64)
    _export(doc, "single-opaque-layer")


def run_layer_order():
    doc = Krita.instance().createDocument(64, 64, "layer-order", "RGBA", "U8", "", 300.0)
    root = _clear_default_layers(doc)
    _make_layer(doc, root, "bottom", (0, 0, 200, 255), 0, 0, 48, 48)
    _make_layer(doc, root, "top", (0, 200, 0, 255), 16, 16, 48, 48)
    _export(doc, "layer-order")


def run_partial_opacity():
    doc = Krita.instance().createDocument(64, 64, "partial-opacity", "RGBA", "U8", "", 300.0)
    root = _clear_default_layers(doc)
    _make_layer(doc, root, "bg", (255, 255, 255, 255), 0, 0, 64, 64)
    _make_layer(doc, root, "fg", (0, 0, 255, 200), 0, 0, 64, 64, opacity=0.8)
    _export(doc, "partial-opacity")


def run_offset_and_clipping():
    doc = Krita.instance().createDocument(32, 32, "offset-and-clipping", "RGBA", "U8", "", 300.0)
    root = _clear_default_layers(doc)
    _make_layer(doc, root, "clipped", (255, 128, 0, 255), -8, -8, 24, 24)
    _export(doc, "offset-and-clipping")


def run_hidden_layer():
    doc = Krita.instance().createDocument(32, 32, "hidden-layer", "RGBA", "U8", "", 300.0)
    root = _clear_default_layers(doc)
    _make_layer(doc, root, "visible", (0, 255, 0, 255), 0, 0, 32, 32)
    _make_layer(doc, root, "hidden", (255, 0, 0, 255), 0, 0, 32, 32, visible=False)
    _export(doc, "hidden-layer")


def run_multiply_blend():
    doc = Krita.instance().createDocument(32, 32, "multiply-blend", "RGBA", "U8", "", 300.0)
    root = _clear_default_layers(doc)
    _make_layer(doc, root, "bottom", (100, 250, 90, 255), 0, 0, 32, 32)
    _make_layer(doc, root, "top", (200, 50, 10, 255), 0, 0, 32, 32, composite_op="svg:multiply")
    _export(doc, "multiply-blend")


def run_isolated_group_with_opacity():
    doc = Krita.instance().createDocument(32, 32, "isolated-group-with-opacity", "RGBA", "U8", "", 300.0)
    root = _clear_default_layers(doc)
    _make_layer(doc, root, "backdrop", (0, 0, 0, 255), 0, 0, 32, 32)
    group = doc.createNode("isolated", "grouplayer")
    root.addChildNode(group, None)
    _make_layer(doc, group, "bottom", (0, 255, 0, 255), 0, 0, 32, 32)
    _make_layer(doc, group, "top", (255, 0, 0, 255), 0, 0, 32, 32)
    group.setOpacity(round(0.5 * 255))
    _export(doc, "isolated-group-with-opacity")


def run_non_isolated_group():
    # No Krita group node at all -- see this file's own module docstring
    # for why (Krita's real .ora group export always writes
    # isolation="isolate", so it cannot represent a genuinely non-isolated
    # group; "no group wrapper" is mathematically equivalent for this exact
    # scene, matching scene_matrix.py's own already-verified redesign).
    doc = Krita.instance().createDocument(32, 32, "non-isolated-group", "RGBA", "U8", "", 300.0)
    root = _clear_default_layers(doc)
    _make_layer(doc, root, "backdrop", (0, 0, 0, 255), 0, 0, 32, 32)
    _make_layer(doc, root, "bottom", (100, 250, 90, 160), 0, 0, 32, 32)
    _make_layer(doc, root, "top", (200, 50, 10, 255), 0, 0, 32, 32, composite_op="svg:multiply")
    _export(doc, "non-isolated-group")


SCENES = [
    run_single_opaque_layer,
    run_layer_order,
    run_partial_opacity,
    run_offset_and_clipping,
    run_hidden_layer,
    run_multiply_blend,
    run_isolated_group_with_opacity,
    run_non_isolated_group,
]


def run_all_scenes():
    app = Krita.instance()
    app.setBatchmode(True)
    for fn in SCENES:
        try:
            log("running scene: %s" % fn.__name__)
            fn()
        except Exception as exc:  # noqa: BLE001
            import traceback
            log("EXCEPTION in %s:\n%s" % (fn.__name__, traceback.format_exc()))
            write_sentinel(status="ERROR", detail="exception in %s: %r" % (fn.__name__, exc))
            return
    write_sentinel(status="PASS", detail="all 8 scenes created and saved as .kra and .ora")


run_all_scenes()
