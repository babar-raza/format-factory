# Skill Transcript: /add-dotnet-api — Netpbm Posterize

## Skill: add-dotnet-api
## Format: Netpbm
## API: Posterize(int levels) → NetpbmImage
## Sprint: mainstream-r109
## Ledger Entry: R109-GOVERNED-DOTNET-NETPBM-POSTERIZE-001

## Pre-Conditions
- Source SHA before: `af782955c46aaa92bce95b194b863b5a2ad6a5a7be30f272452502bc8b28a6ff`
- Ledger valid, latest_sprint: mainstream-r108

## Implementation
- Added `Posterize(int levels)` method to `NetpbmImage.cs`
- Quantizes each pixel value to one of `levels` evenly-spaced values
- Private `Quantize(byte, int, int)` helper for per-value quantization
- PBM returns clone (already binary), PPM applies to all three channels
- Returns new image, does not mutate original

## Source SHA after: `99f60913e9adc0c677b8c253ba6b9df1074e918532aadfbaeef9aa2a9b44deb7`

## Tests
- File: `tests/net/netpbm/NetpbmR109PosterizeTests.cs`
- Count: 10 tests
- All pass (335 total Netpbm tests)

## Validation
- Ledger entry added: R109-GOVERNED-DOTNET-NETPBM-POSTERIZE-001
- Focused test: `dotnet test tests/net/netpbm/ --no-restore` — 335 passed, 0 failed
