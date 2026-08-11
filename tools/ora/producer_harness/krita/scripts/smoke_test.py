"""ORA harness Krita driver script -- SMOKE TEST (feasibility spike).

Executed inside the ora_harness_driver PyKrita plugin's own exec() sandbox
(see ../pykrita_ext/ora_harness_driver/__init__.py) -- `Krita`, `window`,
`log`, and `write_sentinel` are already bound in this script's own globals.

Deliberately treats this FIRST real run as an empirical API probe, not a
blind implementation -- several details of Krita's own Python scripting API
(addChildNode's insertion-order semantic, setPixelData's exact byte
ordering, opacity's numeric scale) are documented inconsistently across
Krita versions, and this session's own established discipline (see the
GIMP lane's own generate_scenes.scm header comments) is to verify
empirically against the real running application rather than assume. Every
step logs before and after state so a failure is diagnosable from the log
file alone.
"""
import os

import krita as krita_module

OUT_DIR = os.environ.get("ORA_HARNESS_OUT", "/out")

log("krita module file: %r" % (getattr(krita_module, "__file__", None),))
log("krita module attrs: %r" % (sorted(a for a in dir(krita_module) if not a.startswith("_")),))

app = Krita.instance()
log("Krita.instance() = %r" % (app,))
log("Krita.instance() attrs (paint-relevant subset): %r" % (
    sorted(a for a in dir(app) if any(k in a.lower() for k in ("document", "batch", "version")))
))

doc = app.createDocument(32, 32, "smoke-test", "RGBA", "U8", "", 300.0)
log("createDocument -> %r" % (doc,))
app.setBatchmode(True)

root = doc.rootNode()
log("rootNode() -> %r, initial childNodes=%r" % (root, root.childNodes()))

def make_solid_layer(name, r, g, b, a, x, y, w, h):
    node = doc.createNode(name, "paintlayer")
    log("createNode(%r) -> %r" % (name, node))
    # Krita's own 8-bit RGBA pixel data is documented (and empirically
    # reconfirmed here, not assumed) to be byte-order BGRA per pixel.
    pixel = bytes([b, g, r, a])
    data = pixel * (w * h)
    node.setPixelData(bytearray(data), x, y, w, h)
    log("setPixelData(%r, x=%d, y=%d, w=%d, h=%d) done, len(data)=%d" % (name, x, y, w, h, len(data)))
    return node

bottom = make_solid_layer("bottom", 0, 0, 200, 255, 0, 0, 32, 32)
top = make_solid_layer("top", 200, 30, 30, 255, 8, 8, 16, 16)

root.addChildNode(bottom, None)
log("after addChildNode(bottom, None): childNodes=%r" % (root.childNodes(),))
root.addChildNode(top, None)
log("after addChildNode(top, None): childNodes=%r" % (root.childNodes(),))
log("childNode names in order: %r" % ([n.name() for n in root.childNodes()],))

doc.refreshProjection()
doc.waitForDone()
log("refreshProjection()/waitForDone() done")

kra_path = os.path.join(OUT_DIR, "smoke-test.kra")
ora_path = os.path.join(OUT_DIR, "smoke-test.ora")

doc.setBatchmode(True)
saved_kra = doc.saveAs(kra_path)
log("saveAs(%r) -> %r" % (kra_path, saved_kra))
doc.waitForDone()

saved_ora = doc.saveAs(ora_path)
log("saveAs(%r) -> %r" % (ora_path, saved_ora))
doc.waitForDone()

log("kra exists=%r size=%r" % (os.path.exists(kra_path), os.path.getsize(kra_path) if os.path.exists(kra_path) else None))
log("ora exists=%r size=%r" % (os.path.exists(ora_path), os.path.getsize(ora_path) if os.path.exists(ora_path) else None))

if os.path.exists(ora_path) and os.path.getsize(ora_path) > 0:
    write_sentinel(status="PASS", detail="smoke test scene created and saved as .kra and .ora")
else:
    write_sentinel(status="ERROR", detail="ora file missing or empty after saveAs")

doc.close()
log("document closed")
