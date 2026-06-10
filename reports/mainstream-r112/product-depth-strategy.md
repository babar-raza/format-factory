# R112 Product Depth Strategy

## Sprint: mainstream-r112

## Quotas
- Commercial .NET: 5+ total, 3+ save/export/dogfood/object-model depth, max 2 helper
- FOSS: 4+ total, 2+ products, 2+ roundtrip/export/package
- Dogfood: 3+ total, 2+ implemented

## Commercial .NET Plan (Wave 6)

### Lane A — FODS (2 deliverables)
1. **RemoveSheet** (object_model_depth) — via /add-dotnet-api
2. **FODS CSV export dogfood** (save_export_depth) — edit→export→verify roundtrip test

### Lane B — FODT (2 deliverables)
1. **InsertHeading save roundtrip** (save_export_depth) — heading persistence proof
2. **ReplaceText save roundtrip** (save_export_depth) — text replacement persistence proof

### Lane C — Netpbm (2 deliverables)
1. **Equalize depth tests** (image_processing_depth) — comprehensive histogram equalization
2. **Sepia save roundtrip** (save_export_depth) — Sepia→Save→Load proof

**Total: 6 commercial (4 save/export depth + 2 object_model/image depth)**
**Quota: 6/5+ total, 4/3+ depth — PASS**

## FOSS Plan (Wave 7)

1. **ZST multi-frame hardening** — large payload compress/decompress
2. **PPM binary P6 roundtrip** — write P6→read→verify pixel data
3. **SYLK edge-case hardening** — special chars, empty cells, large grids
4. **DIF roundtrip** — parse→export→verify with varied data types

**Total: 4 FOSS, 3 products (ZST/PPM/SYLK+DIF), 3 roundtrip**
**Quota: 4/4+, 3/2+ products, 3/2+ roundtrip — PASS**

## Dogfood Plan (Wave 8)

1. **FODS CSV export dogfood** — MergeCells→ExportToCsv→verify
2. **FODT Markdown export dogfood** — InsertHeading→ExportToMarkdown→verify
3. **Netpbm format convert dogfood** — ConvertFormat PGM→PPM→Save→Reload

**Total: 3 dogfood, all implemented**
**Quota: 3/3+, 3/2+ implemented — PASS**
