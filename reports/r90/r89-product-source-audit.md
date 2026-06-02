---
visibility: generated
generated_by: codex
---

# R89 Product Source Audit

## Initial Source Truth

| Product | APIs | Initial Classification |
|---|---|---|
| FODS .NET | `SheetCount`, `GetSheetByName`, `GetCellValue`, `ExportSheetToCsvString` | `PRESENT_WITH_TESTS` |
| FODT .NET | `CharCount`, `SearchText`, `ReplaceText` | `PRESENT_WITH_TESTS` |
| Netpbm .NET | `GetChannelStats`, `Rotate90Cw`, `Crop` | `PRESENT_WITH_TESTS` |

These source changes are preserved. Train J must backfill ledger records as
`BACKFILLED_PRE_GOVERNANCE`.

## Verification Results

| Product | Command | Result |
|---|---|---|
| FODS .NET | `dotnet test tests/net/fods --verbosity quiet` | `191 passed, 0 failed` |
| FODT .NET | `dotnet test tests/net/fodt --verbosity quiet` | `176 passed, 0 failed` |
| Netpbm .NET | `dotnet test tests/net/netpbm --verbosity quiet` | `94 passed, 0 failed` |

The R89 APIs are classified `PRESENT_WITH_TESTS` and ledger-backfilled.
