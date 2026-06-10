# R108 Netpbm Product Depth

## New API: ApplyGamma
- `ApplyGamma(double gamma)` — gamma correction for PGM/PPM, PBM returns clone
- gamma < 1 brightens, gamma > 1 darkens
- 10 tests in NetpbmR108ApplyGammaTests.cs
- Ledger entry: R108-GOVERNED-DOTNET-NETPBM-APPLYGAMMA-001
- SHA: af782955c46aaa92bce95b194b863b5a2ad6a5a7be30f272452502bc8b28a6ff
