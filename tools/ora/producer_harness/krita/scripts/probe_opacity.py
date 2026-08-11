"""Probe: what numeric scale does Node.setOpacity() actually use? Compare
input value to (a) opacity() getter and (b) the real exported stack.xml
opacity="..." attribute, which must be a 0.0-1.0 float per the OpenRaster
spec (already confirmed elsewhere in this session's own real exports)."""
import os

OUT_DIR = os.environ.get("ORA_HARNESS_OUT", "/out")
app = Krita.instance()
app.setBatchmode(True)
doc = app.createDocument(8, 8, "probe4", "RGBA", "U8", "", 300.0)
root = doc.rootNode()
for n in list(root.childNodes()):
    n.remove()

layer = doc.createNode("half", "paintlayer")
log("default opacity(): %r" % (layer.opacity(),))
layer.setOpacity(128)
log("after setOpacity(128): opacity()=%r" % (layer.opacity(),))
root.addChildNode(layer, None)

doc.refreshProjection()
doc.waitForDone()
path = os.path.join(OUT_DIR, "probe-opacity.ora")
doc.saveAs(path)
doc.waitForDone()
log("saved: %r" % (path,))

write_sentinel(status="PASS", detail="opacity probe finished")
doc.close()
