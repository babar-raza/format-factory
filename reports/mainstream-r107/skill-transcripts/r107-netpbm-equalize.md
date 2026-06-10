# Skill Transcript: Netpbm Equalize

- **Skill:** /add-dotnet-api
- **Format:** Netpbm
- **API:** Equalize() -> NetpbmImage
- **Sprint:** FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001
- **Wave:** 2 (Commercial .NET APIs)

## Source File Changed
- `src/net/netpbm/Model/NetpbmImage.cs` — Added Equalize method + IsPbm/IsPgm/IsPpm helpers

## Behavior
Histogram equalization for PGM images (builds histogram, CDF, LUT, remaps pixels). PPM converts to grayscale first, PBM returns clone. Returns a NEW image.

## Tests Created
- `tests/net/netpbm/NetpbmR107EqualizeTests.cs` — 8 tests
- `tests/net/netpbm/NetpbmR107DogfoodEqualizeOverlayTests.cs` — shared dogfood coverage

## Validation
- `dotnet test tests/net/netpbm/ --filter R107` — 24 passed, 0 failed
- Ledger record written to `reports/r90/product-code-change-ledger.json`
