"""Empirically test candidate Krita blend modes against the exact
discriminating fixture (backdrop=(30,200,60) opaque, source=(220,40,180)
alpha=166/255) used by composite_oracle.py -- pixel comparison, not
name-based assumption. Krita blendingMode() strings are its own internal
libkis identifiers; probe several plausible candidates per operation since
exact spelling is not documented reliably (matching the same discipline
already used for GIMP's own constant-name probing)."""

app = Krita.instance()
app.setBatchmode(True)


def bgra(rgba):
    r, g, b, a = rgba
    return bytes([b, g, r, a])


def test_mode(name, mode_string):
    doc = app.createDocument(4, 4, "probe", "RGBA", "U8", "", 300.0)
    root = doc.rootNode()
    for n in list(root.childNodes()):
        n.remove()
    bottom = doc.createNode("bottom", "paintlayer")
    root.addChildNode(bottom, None)
    bottom.setPixelData(bytearray(bgra((30, 200, 60, 255)) * 16), 0, 0, 4, 4)
    top = doc.createNode("top", "paintlayer")
    root.addChildNode(top, None)
    top.setPixelData(bytearray(bgra((220, 40, 180, 255)) * 16), 0, 0, 4, 4)
    top.setOpacity(166)  # Node.setOpacity() is 0-255, not 0-100 (empirically confirmed earlier this session)
    try:
        top.setBlendingMode(mode_string)
        actual_mode = top.blendingMode()
    except Exception as exc:  # noqa: BLE001
        log("%s (%s): setBlendingMode FAILED: %r" % (name, mode_string, exc))
        doc.close()
        return
    doc.refreshProjection()
    doc.waitForDone()
    pixel_bytes = bytes(doc.pixelData(1, 1, 1, 1))
    b, g, r, a = pixel_bytes[0], pixel_bytes[1], pixel_bytes[2], pixel_bytes[3]
    log("%s mode_string=%r actual_mode=%r -> %d,%d,%d" % (name, mode_string, actual_mode, r, g, b))
    doc.close()


candidates = {
    "Screen": "screen",
    "Overlay": "overlay",
    "Darken": "darken",
    "Lighten": "lighten",
    "ColorDodge": "dodge",
    "ColorBurn": "burn",
    "HardLight": "hard_light",
    "SoftLight": "soft_light_svg",
    "Difference": "diff",
    "Hue": "hue",
    "Saturation": "saturation",
    "Color": "color",
    "Luminosity": "luminize",
    "Addition_forLighter": "add",
}

for name, mode_string in candidates.items():
    test_mode(name, mode_string)

write_sentinel(status="PASS", detail="krita blend semantics probe finished")
