---
visibility: generated
generated_by: codex
---

# R90 Product-Code Change Ledger

## R90 Governed Product Change

| Entry | Classification | Skill | Product | Capability | Validation |
|---|---|---|---|---|---|
| `R90-GOVERNED-PYTHON-NETPBM-PPM-TO-PGM-001` | `GOVERNED_PRODUCT_CHANGE` | `/add-dogfood-export` | Netpbm Python FOSS | PPM-to-PGM using `pgm.pgm_parser.write_pgm` | `5 passed` |

The machine-readable authority is `reports/r90/product-code-change-ledger.json`.

R89 product APIs are backfilled as `BACKFILLED_PRE_GOVERNANCE` because they were
already present at the start of R90:

| Product | APIs | Ledger Entry |
|---|---|---|
| FODS .NET | `ExportSheetToCsvString` | `R90-BACKFILL-R89-FODS-CSV-001` |
| FODS .NET | `SheetCount`, `GetSheetByName`, `GetCellValue` overloads | `R90-BACKFILL-R89-FODS-DOCUMENT-001` |
| FODT .NET | `CharCount`, `SearchText`, `ReplaceText`, `ParagraphCount` | `R90-BACKFILL-R89-FODT-DOCUMENT-001` |
| Netpbm .NET | `GetChannelStats`, `Rotate90Cw`, `Crop` | `R90-BACKFILL-R89-NETPBM-IMAGE-001` |

New or modified `src/` files after the R89 tracking ref require a ledger entry
with the file's current SHA-256, or an explicit deletion reference.
