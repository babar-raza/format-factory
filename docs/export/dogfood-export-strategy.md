# Dogfood Export Strategy

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31
Version: 1.1

## Definition

**Dogfooding** in Format Factory means: when a Format Factory library exports to another format,
it MUST use another Format Factory library as the write backend — not stdlib, not external packages.

This is a product-quality signal: if our libraries are not good enough for us to use internally,
they are not good enough for customers.

## Rule

Every export function in Format Factory must satisfy:

```
EXPORT_RULE: source_library(FF) → export_function → target_library(FF)
```

Where `target_library(FF)` means a Format Factory-produced library (`write_X`, `write_pgm`, etc.).

External libraries (PIL, cv2, openpyxl, etc.) are FORBIDDEN in export paths.
stdlib-only writes (raw file.write) without FF write primitives are FORBIDDEN.

## Dogfood Status Values

| Status | Meaning |
|--------|---------|
| `IMPLEMENTED` | Export uses FF library for write backend |
| `GAP_DOGFOOD_EXTERNAL` | Export writes directly or uses non-FF library; gap documented |
| `NOT_IMPLEMENTED` | Export not yet built |
| `NOT_APPLICABLE` | Format has no multi-format export (e.g., CSV is terminal) |

## Current Dogfood Map (R85)

See: reports/r85/dogfood-export-map.md for the authoritative per-format matrix.

## Enforcement

1. **Python:** Test class `TestDogfoodLibraryUsage` in each test file verifies:
   - `inspect.getsource(mod)` does NOT contain PIL/cv2/imageio/skimage/matplotlib
   - `write_X` from FF library IS present in source

2. **.NET:** `dogfood_status` field in `NetpbmExporter` XML comments and test assertions
   verify FF `NetpbmImage` model (not third-party model) is used throughout

3. **CI gate:** Any `GAP_DOGFOOD_EXTERNAL` must be documented in poc-targets.yaml with a
   remediation sprint noted. Undocumented gaps are RC-blocking.

## Remediation Priority

| Gap | Owner | Sprint |
|-----|-------|--------|
| FODT→TXT .NET (FodtTxtExporter writes directly) | .NET team | R86+ (needs .NET text FF lib) |

## Format Family Coverage

### XML Office-Like (FODS/FODT)

- Python FODT→TXT: `IMPLEMENTED` — uses FF neutral_model document_to_text
- .NET FODT→TXT: `GAP_DOGFOOD_EXTERNAL` — FodtTxtExporter writes text directly
- .NET FODT→HTML: `GAP_DOGFOOD_EXTERNAL` — no FF HTML write library yet
- .NET FODT→Markdown: `GAP_DOGFOOD_EXTERNAL` — no FF Markdown write library yet

### Netpbm (PBM/PGM/PPM)

- Python PBM→PGM: `IMPLEMENTED` — pbm_to_pgm.py uses FF write_pgm from pgm library
- Python PBM→PPM: `IMPLEMENTED` — pbm_to_ppm.py uses FF write_ppm from ppm library
- Python PGM→PPM: `IMPLEMENTED` — pgm_to_ppm.py uses FF write_ppm from ppm library
- Python PPM→PGM: `IMPLEMENTED` — ppm_to_pgm.py uses FF write_pgm from pgm library
- .NET PBM→PGM: `IMPLEMENTED` — NetpbmExporter.PbmToPgm uses NetpbmWriter (FF)
- .NET PBM→PPM: `IMPLEMENTED` — NetpbmExporter.PbmToPpm uses NetpbmWriter (FF)

### ZST (Zstandard)

- Python ZST decompress→raw bytes: `NOT_APPLICABLE` — ZST is a compression layer; output is the embedded format

### SYLK

- Python SYLK→CSV: `IMPLEMENTED` — sylk_to_csv uses FF SYLK parser (no external lib)
  Note: CSV is a terminal format; FF CSV writer not applicable (stdlib csv module would shadow)

## Strategy Going Forward

1. Every new export function MUST be tagged `dogfood_status` in its source
2. A test MUST verify no external libraries in the export module
3. `GAP_DOGFOOD_EXTERNAL` gaps require a taskccard in poc-targets.yaml
4. When the target write library is built in FF, close the gap and update status

## Reference

- Product track doc: docs/product-factory/product-object-model-edit-save-export-strategy.md
- POC targets: product-capability-matrix/poc-targets.yaml
- Export map: reports/r85/dogfood-export-map.md
