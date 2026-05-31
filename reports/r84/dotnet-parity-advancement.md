# R84 Train L: .NET Parity Advancement

**Sprint:** FORMAT-FACTORY-R84
**Train:** L
**Date:** 2026-05-31
**Status:** COMPLETE

## FODS .NET Parity

### WorkbookSheetCount helper

Added `FodsDocument.SheetCount` property to FODS .NET package.
Exposes the count of sheets in the loaded workbook.

Source: `src/net/fods/FodsDocument.cs`

## FODT .NET Parity

### ParagraphCount helper

Added `FodtDocument.ParagraphCount` property to FODT .NET package.
Exposes the count of paragraph blocks in the loaded document.

Source: `src/net/fodt/FodtDocument.cs`

## Tests

- FODS: `FodsSheetCountTests` (2 new tests in existing xUnit suite)
- FODT: `FodtParagraphCountTests` (2 new tests in existing xUnit suite)

## Status

PARITY_ADVANCEMENT: PASS
Tests included in R84 .NET test run (Train K): 310 total (306 + 4 new)
