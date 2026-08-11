"""Probe: what is a fresh group layer's default blendingMode()? Does setting
it to a pass-through-shaped string succeed, and does the resulting .ora own
stack.xml show isolation="auto" vs "isolate" accordingly? This is the most
direct possible test -- round-trip through Krita's own real .ora exporter
and read the actual XML attribute it writes."""
import os

OUT_DIR = os.environ.get("ORA_HARNESS_OUT", "/out")
app = Krita.instance()
app.setBatchmode(True)
doc = app.createDocument(16, 16, "probe2", "RGBA", "U8", "", 300.0)
root = doc.rootNode()
for n in list(root.childNodes()):
    n.remove()

group = doc.createNode("mygroup", "grouplayer")
log("default blendingMode(): %r" % (group.blendingMode(),))
root.addChildNode(group, None)
child = doc.createNode("child", "paintlayer")
group.addChildNode(child, None)

doc.refreshProjection()
doc.waitForDone()
path_default = os.path.join(OUT_DIR, "probe-default.ora")
doc.setBatchmode(True)
doc.saveAs(path_default)
doc.waitForDone()
log("saved default-mode ora: %r" % (path_default,))

candidates = ["pass through", "pass_through", "passthrough", "Pass Through", "normal"]
for candidate in candidates:
    try:
        group.setBlendingMode(candidate)
        actual = group.blendingMode()
        log("setBlendingMode(%r) -> blendingMode() now %r" % (candidate, actual))
    except Exception as exc:
        log("setBlendingMode(%r) FAILED: %r" % (candidate, exc))

# leave it on the last successful-looking candidate for the export test
group.setBlendingMode("pass through")
doc.refreshProjection()
doc.waitForDone()
path_pt = os.path.join(OUT_DIR, "probe-passthrough.ora")
doc.saveAs(path_pt)
doc.waitForDone()
log("saved 'pass through'-mode ora: %r" % (path_pt,))

write_sentinel(status="PASS", detail="blendmode probe finished")
doc.close()
