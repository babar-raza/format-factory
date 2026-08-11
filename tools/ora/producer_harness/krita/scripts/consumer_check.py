"""Independent-consumer-acceptance check for ORA-BASELINEASSET-001: open a
real format-factory-GENERATED PNG asset in real Krita and report success."""
import os

path = os.environ.get("ORA_HARNESS_CONSUMER_INPUT", "/out/format-factory-generated-mergedimage.png")
app = Krita.instance()
app.setBatchmode(True)

doc = app.openDocument(path)
log("openDocument(%r) -> %r" % (path, doc))
if doc is None:
    write_sentinel(status="ERROR", detail="openDocument returned None")
else:
    w, h = doc.width(), doc.height()
    log("LOADED width=%d height=%d" % (w, h))
    write_sentinel(status="PASS", detail="LOADED width=%d height=%d" % (w, h))
    doc.close()
