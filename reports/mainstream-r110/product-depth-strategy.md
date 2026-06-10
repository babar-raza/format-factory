# R110 Product Depth Strategy

## Quotas
- **Commercial .NET:** 5+ deliverables (3+ save/export/dogfood/object-model depth, max 2 shallow helpers)
- **FOSS:** 4+ deliverables (2+ workflows, 2+ roundtrip/export)
- **Dogfood/Export:** 3+ deliverables (2+ implemented)

## Planned Commercial .NET Deliverables (7 planned, need 5+)

### Depth APIs (3+ required)
1. **FODS RemoveSheet** — object model depth, removes table element by name
2. **FODT FindText** — search depth, returns paragraph indices containing search string
3. **Netpbm Solarize** — image processing depth, inverts pixels above threshold
4. **Netpbm Sepia** — image processing depth, applies sepia tone to PPM

### Helper APIs (max 2)
5. **FODS GetCellDataType** — reads office:value-type attribute
6. **FODT GetParagraphStyles** — reads style names for paragraphs

### Stretch
7. **FODS InsertColumnWithValues** — column-oriented insert (if time permits)

## Planned FOSS Deliverables (4+)
1. **ZST Multi-frame Workflow** — compress→decompress→verify chain (workflow)
2. **SYLK Parse Edge-Cases** — empty cells, special chars, large grids (roundtrip)
3. **PBM Write→Read Roundtrip** — cross-format verification (roundtrip)
4. **PPM Grayscale Workflow** — write→read→verify pixel values (workflow)

## Planned Dogfood Deliverables (3+)
1. **FODS CSV Export Pipeline** — load→edit→ExportSheetToCsv dogfood
2. **FODT Markdown Export Pipeline** — load→edit→ExportToMarkdown dogfood
3. **Netpbm Posterize→Save Pipeline** — load→posterize→SaveToFile dogfood

## Evidence Per Deliverable
Each governed .NET API requires: source diff, tests (8+), raw log, skill transcript, ledger entry.
Each FOSS test suite requires: test file (8+), raw log.
Each dogfood pipeline requires: test file (4+), raw log.
