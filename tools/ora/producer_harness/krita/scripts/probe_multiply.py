"""Probe: what composite-op string does a plain layer with blendingMode
'multiply' actually export as in stack.xml? Needs to match format-factory's
own registry value 'svg:multiply' to be usable, not a krita:-prefixed one."""
import os

OUT_DIR = os.environ.get("ORA_HARNESS_OUT", "/out")
app = Krita.instance()
app.setBatchmode(True)
doc = app.createDocument(8, 8, "probe3", "RGBA", "U8", "", 300.0)
root = doc.rootNode()
for n in list(root.childNodes()):
    n.remove()

layer = doc.createNode("multi", "paintlayer")
log("default layer blendingMode(): %r" % (layer.blendingMode(),))
layer.setBlendingMode("multiply")
log("after setBlendingMode('multiply'): %r" % (layer.blendingMode(),))
root.addChildNode(layer, None)

doc.refreshProjection()
doc.waitForDone()
path = os.path.join(OUT_DIR, "probe-multiply.ora")
doc.saveAs(path)
doc.waitForDone()
log("saved: %r" % (path,))

write_sentinel(status="PASS", detail="multiply probe finished")
doc.close()
