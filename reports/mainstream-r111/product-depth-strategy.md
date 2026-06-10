# R111 Product Depth Strategy

## Quota Requirements
- Commercial .NET: 5+ deliverables, 3+ save/export/dogfood/package/object-model depth, max 2 helper
- FOSS: 4+ deliverables, 2+ workflows, 2+ roundtrip/export
- Dogfood: 3+ deliverables, 2+ implemented

## Commercial .NET Plan (6 APIs, 0 helper)

### FODS (2 depth APIs)
1. **MergeCells** — merge rectangular range using table:number-columns-spanned + table:number-rows-spanned. Object-model depth.
2. **SetCellFormula** — set table:formula attribute on cell. Object-model depth.

### FODT (2 depth APIs)
1. **RemoveHeading** — remove heading element by index. Object-model depth (complements InsertHeading).
2. **GetDocumentOutline** — return list of (Level, Text) tuples from all heading elements. Object-model depth.

### Netpbm (2 depth APIs)
1. **Sharpen** — 3x3 unsharp-mask-style kernel for PGM/PPM. Image processing depth.
2. **BlurBox** — NxN box blur for PGM/PPM. Image processing depth.

## FOSS Plan (4 deliverables)
1. **ZST dictionary workflow** — test compress with dictionary, verify round-trip
2. **PPM pixel-transform roundtrip** — write→read→verify pixel invariants
3. **SYLK write roundtrip** — write_sylk→parse_sylk cycle
4. **DIF CSV export hardening** — edge-case tests for dif_to_csv

## Dogfood Plan (3 pipelines)
1. **FODS save roundtrip** — load→edit formula→save→reload→verify
2. **FODT outline export** — load→outline→markdown export
3. **Netpbm sharpen-save** — load→sharpen→save→reload→verify
