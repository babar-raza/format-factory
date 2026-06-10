# Skill Transcript: Netpbm ConvertFormat

- **Skill:** /add-dotnet-api
- **Format:** Netpbm
- **API:** ConvertFormat(NetpbmFormat targetFormat) -> NetpbmImage
- **Sprint:** FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001
- **Wave:** 2 (Commercial .NET APIs)

## Source File Changed
- `src/net/netpbm/Model/NetpbmImage.cs` — Added ConvertFormat method

## Behavior
Convert ASCII to binary format (and vice versa) within the same type family: P1<->P4 (PBM), P2<->P5 (PGM), P3<->P6 (PPM). Cross-type conversion throws InvalidOperationException. Clones image and changes Format field.

## Tests Created
- `tests/net/netpbm/NetpbmR107ConvertFormatTests.cs` — 10 tests
- `tests/net/netpbm/NetpbmR107DogfoodEqualizeOverlayTests.cs` — shared dogfood coverage

## Validation
- `dotnet test tests/net/netpbm/ --filter R107` — 24 passed, 0 failed
- Ledger record written to `reports/r90/product-code-change-ledger.json`
