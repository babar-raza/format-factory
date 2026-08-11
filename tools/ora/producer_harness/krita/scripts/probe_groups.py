"""One-off probe: empirically verify Krita's own group-layer/isolation API
before writing the real scene matrix (same discipline as smoke_test.py)."""
import os

OUT_DIR = os.environ.get("ORA_HARNESS_OUT", "/out")
app = Krita.instance()
app.setBatchmode(True)
doc = app.createDocument(32, 32, "probe", "RGBA", "U8", "", 300.0)
root = doc.rootNode()

for n in list(root.childNodes()):
    log("removing default node: %r name=%r" % (n, n.name()))
    n.remove()

group = doc.createNode("mygroup", "grouplayer")
log("group node: %r, attrs with 'pass' or 'isolat': %r" % (
    group, sorted(a for a in dir(group) if "pass" in a.lower() or "isolat" in a.lower())
))
log("full group node attrs: %r" % (sorted(a for a in dir(group) if not a.startswith("_")),))

root.addChildNode(group, None)
child = doc.createNode("child", "paintlayer")
group.addChildNode(child, None)
log("group childNodes after add: %r" % ([c.name() for c in group.childNodes()],))

try:
    group.setPassThroughMode(True)
    log("setPassThroughMode(True) succeeded, value now: %r" % (group.passThroughMode() if hasattr(group, "passThroughMode") else "NO GETTER"))
except Exception as exc:
    log("setPassThroughMode FAILED: %r" % (exc,))

try:
    group.setPassThroughMode(False)
    log("setPassThroughMode(False) succeeded, value now: %r" % (group.passThroughMode() if hasattr(group, "passThroughMode") else "NO GETTER"))
except Exception as exc:
    log("setPassThroughMode(False) FAILED: %r" % (exc,))

log("node type of group: %r" % (group.type() if hasattr(group, "type") else "NO type()",))
log("blendingMode-related attrs: %r" % (sorted(a for a in dir(group) if "blend" in a.lower()),))

write_sentinel(status="PASS", detail="group probe finished")
doc.close()
