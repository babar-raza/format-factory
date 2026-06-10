# R108 Fresh Mainstream Gaps

## Gap Source
Product-capability-matrix/poc-targets.yaml — latest state after R108 APIs.

## Remaining Depth Gaps (R109+)

### FODS .NET
- Formula cell support (read/write formulas, not just values)
- Sheet-level metadata (custom properties, protection status)
- Multi-sheet CSV export (ExportAllSheetsToCsv already exists — needs hardening)

### FODT .NET
- Table support (read/create tables within document)
- Style-aware paragraph creation (apply named styles)
- Metadata extraction (author, creation date, revision count)

### Netpbm .NET
- Resize with interpolation (bilinear/nearest-neighbor)
- Color space conversion (RGB<->HSV)
- Filter operations (blur, sharpen, median)

### Python/FOSS
- PBM/PGM write functions (currently read-only)
- DIF structured export (write DIF files)
- SYLK formula cell support

## R109 Recommended Focus
Depth: formula cells, table support, resize with interpolation
