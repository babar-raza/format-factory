# Upstream issue packages — local only, NOT submitted

Directive Section 10. Each file in this directory is a reproducible,
self-contained issue package for a confirmed upstream defect found during
ORA-COMPOSITE-001's own producer-evidence work this cycle. **None of these
have been submitted to any upstream tracker, and no maintainer has been
contacted.** Drafting and locally validating them is authorized by the
governing directive; external submission is an explicitly separate gate
requiring its own authorization, not granted here.

| file | project | defect |
|---|---|---|
| `01-jsora-webgl-read-write-hazard.md` | jsora 0.3.0 | multi-layer render corruption (WebGL read/write-same-resource hazard) |
| `02-jsora-absolute-zip-paths.md` | jsora 0.3.0 | writer emits absolute (`/data/layerN.png`) ZIP member paths |
| `03-gimp3-svg-plus-semantic-mismatch.md` | GIMP 3.0.4 | Addition layer-mode does not conform to Porter-Duff Lighter |
| `04-gimp3-missing-version-attribute.md` | GIMP 3.0.4 | exported `<image>` element omits the required `version` attribute |
| `05-gegl-piecewise-blend-formula-defect.md` | GEGL 0.4.48 | `svg:overlay`/`svg:hard-light`/`gegl:soft-light` premultiplied reformulation does not match the W3C spec |

Each package includes: a minimal fixture reference (pointing to the
already-committed evidence, not duplicating binary content), the exact
pinned version/digest used, a one-command reproduction, the expected
result from the governing standard, the actual observed result, the exact
delta, and concise proposed issue text a maintainer could act on.
