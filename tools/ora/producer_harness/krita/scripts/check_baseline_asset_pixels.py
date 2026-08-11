"""Workstream B3 (ORA-BASELINEASSET-001 visual-assurance amendment): open
each real format-factory-generated mergedimage.png through Krita's own
PNG decoder (openDocument) and read back every pixel via doc.pixelData(),
so the comparison is against what Krita itself decoded, not
format-factory's own decode_png() a second time."""
import os

app = Krita.instance()
app.setBatchmode(True)

SCENES = [
    ("multiply-blend", 32, 32),
    ("layer-order", 64, 64),
]

for scene_id, width, height in SCENES:
    path = "/out/mergedimage-%s.png" % scene_id
    doc = app.openDocument(path)
    if doc is None:
        log("%s: openDocument returned None" % scene_id)
        write_sentinel(status="ERROR", detail="openDocument failed for %s" % scene_id)
        raise SystemExit(1)
    w, h = doc.width(), doc.height()
    if (w, h) != (width, height):
        log("%s: dimension mismatch, expected %dx%d got %dx%d" % (scene_id, width, height, w, h))
        write_sentinel(status="ERROR", detail="dimension mismatch for %s" % scene_id)
        raise SystemExit(1)
    raw = bytes(doc.pixelData(0, 0, w, h))
    for y in range(h):
        for x in range(w):
            o = (y * w + x) * 4
            b, g, r, a = raw[o], raw[o + 1], raw[o + 2], raw[o + 3]
            log("%s,%d,%d,%d,%d,%d,%d" % (scene_id, x, y, r, g, b, a))
    doc.close()

write_sentinel(status="PASS", detail="baseline-asset pixel dump done")
