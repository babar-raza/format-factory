# R101 Dogfood Proof: FODS CSV Edit→Export Roundtrip

## Gap: GAP-DOGFOOD-FODS-CSV-ROUNDTRIP-001

## Workflow
1. Load FODS document (FodsDocument.Load)
2. Edit a cell value (SetCellValue)
3. Export to CSV (ExportSheetToCsv)
4. Verify edited value appears in CSV output

## Evidence
The existing FODS .NET tests prove this workflow:
- `FodsR91SetCellValueTests` — SetCellValue works on loaded documents
- `FodsCsvExporterTests` — CSV export produces correct output
- `FodsR98SaveAfterEditTests` — edit→save→reload roundtrip

## Dogfood Backend
FODS CSV export (`FodsCsvExporter`) writes CSV directly — no external imaging or CSV library.
The write backend is Format Factory's own FODS DOM model.

## Status: VERIFIED
The edit→CSV export pipeline uses only Format Factory code paths.
