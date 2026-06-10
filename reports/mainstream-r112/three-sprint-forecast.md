# Three-Sprint Forecast (R113-R115)

## R113 — Deepen Object Model + Cross-Format Export
- FODS: AddSheet/RemoveSheet roundtrip, conditional formatting read
- FODT: Style extraction (bold/italic/font), list item support
- Netpbm: Crop, Rotate90/180/270, FlipH/FlipV
- FOSS: PBM write roundtrip, PGM write roundtrip, DIF sample file creation
- Dogfood: PGM→PPM colorize workflow, FODS→JSON→FODS roundtrip

## R114 — Save/Export Maturity + Package Readiness
- FODS: Multi-sheet CSV export, cell formatting read
- FODT: Table extraction, image reference extraction
- Netpbm: Brightness/Contrast adjust, Threshold
- FOSS: SYLK→CSV export, ZST dictionary mode
- Package: Rebuild all wheels, installed-import validation

## R115 — Gate 11 Preparation + Commercial Polish
- Full API documentation generation
- Edge-case hardening pass across all formats
- Performance benchmarks for large files
- Gate 11 G11-G approval packet preparation
