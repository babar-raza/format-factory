# R89 Trains N-O: Dogfood Export Verification

## Sprint
FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## Dogfood Exports Verified
1. FODS→CSV (Python): `workbook_to_csv` uses stdlib csv.writer — NOW PROVEN in full suite (csv shadow fixed)
2. SYLK→CSV (Python): `sylk_to_csv` uses stdlib csv.writer — NOW PROVEN in full suite
3. DIF→CSV (Python): `dif_to_csv` uses stdlib csv.writer — NOW PROVEN in full suite
4. FODT→TXT (Python): `document_to_text` uses FF FODT library
5. PBM→PGM (Python): uses FF write_pgm

## Key R89 Impact
The csv shadow fix means all CSV-based dogfood exports now pass in full-suite runs.
Previously, these would fail when collected with `tests/python/csv/` tests.

## .NET Dogfood Status
- FODS→CSV (.NET): FodsCsvExporter writes directly (no FF CSV library dependency)
- FODT→TXT (.NET): FodtDocument.GetPlainText writes directly
- Netpbm cross-format (.NET): NetpbmExporter uses FF NetpbmImage model only

## Status: COMPLETE
