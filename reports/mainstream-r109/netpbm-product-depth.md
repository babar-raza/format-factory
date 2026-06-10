# R109 Netpbm Product Depth Report

## New API: Posterize(int levels) → NetpbmImage
- Quantizes pixel values to N evenly-spaced levels
- Levels must be >= 2 (throws ArgumentOutOfRangeException)
- PBM images return a clone (already binary)
- PPM applies to all three channels independently
- Returns new image; original not mutated

## Source
- File: `src/net/netpbm/Model/NetpbmImage.cs`
- SHA before: `af782955c46aaa92bce95b194b863b5a2ad6a5a7be30f272452502bc8b28a6ff`
- SHA after: `99f60913e9adc0c677b8c253ba6b9df1074e918532aadfbaeef9aa2a9b44deb7`

## Tests
- File: `tests/net/netpbm/NetpbmR109PosterizeTests.cs` (10 tests)
- Total Netpbm .NET tests: 335

## Ledger
- Entry: R109-GOVERNED-DOTNET-NETPBM-POSTERIZE-001
- Skill transcript: `reports/mainstream-r109/skill-transcripts/r109-netpbm-posterize.md`
