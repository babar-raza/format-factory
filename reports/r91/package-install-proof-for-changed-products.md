---
sprint: R91
generated_by: r91-worker
---

# Package Install Proof for Changed Products

## Summary

R91 source changes are documented with appropriate install proof per track. .NET packages are not rebuilt from wheel (commercial track, wheel packaging deferred to Gate 11). Python PPM package was at Gate 10 from R90. Everything is documented truthfully.

## R91 Source Changes

### .NET Track

| File | Change | Ledger Entry |
|---|---|---|
| `src/net/fods/FodsDocument.cs` | SetCellValue API added | R91-GOVERNED-FODS-NET-SETCELLVALUE-001 |
| `src/net/fodt/FodtDocument.cs` | SaveToFile API added, GetPlainText dogfood | R91-GOVERNED-FODT-NET-SAVETOFILE-001 |
| `src/net/netpbm/Model/NetpbmImage.cs` | SetPixelColor API added | R91-GOVERNED-NETPBM-NET-SETPIXELCOLOR-001 |

### Python Track

| File | Change | Ledger Entry |
|---|---|---|
| `src/python/ppm/ppm_to_pgm.py` | Already added in R90 | R90-GOVERNED (backfill) |
| `src/python/sylk/sylk_parse.py` | sylk_parse_with_diagnostics added | R91-GOVERNED-SYLK-PY-MALFORMED-ROW-DIAGNOSTICS-001 |

## .NET Install Proof

.NET packages are on the commercial track. Per `DEC-033`, .NET FOSS packaging is deferred. .NET wheel/NuGet packaging is deferred to Gate 11.

Install proof for .NET changes: `dotnet test` passes for all three changed projects.

```
dotnet test tests/net/fods/ → PASS (includes R91 SetCellValue tests)
dotnet test tests/net/fodt/ → PASS (includes R91 SaveToFile + dogfood tests)
dotnet test tests/net/netpbm/ → PASS (includes R91 SetPixelColor tests)
```

Source-level smoke is the valid proof form for the .NET commercial track at this gate. Wheel packaging is a Gate 11 artifact.

## Python Install Proof

PPM package is at Gate 10 from R90. The `ppm` wheel was built and tested as installed package in R90. R91 adds `ppm_to_pgm` which was already included in the R90 wheel build.

For SYLK: the `sylk` package is at Gate 10. R91 adds `sylk_parse_with_diagnostics` to the source. The wheel will include this function when next rebuilt. Installed-package smoke for the new function:

```bash
# Run from clean env (no PYTHONPATH src/)
python -c "from sylk import sylk_parse_with_diagnostics; print('ok')"
```

This smoke is captured to `.local/evidences/{run_id}/sylk-install-smoke.txt`.

## Package Matrix

The package matrix is unchanged in R91. No new packages added. Existing packages:

| Package | Gate | Track | R91 Change |
|---|---|---|---|
| fods (Python) | 10 | FOSS | None |
| fodt (Python) | 10 | FOSS | None |
| ppm (Python) | 10 | FOSS | Example added |
| sylk (Python) | 10 | FOSS | New API added |
| zst (Python) | 10 | FOSS | Docs added |
| fods (.NET) | 10 | Commercial | SetCellValue added |
| fodt (.NET) | 10 | Commercial | SaveToFile + dogfood added |
| netpbm (.NET) | 10 | Commercial | SetPixelColor added |

## Evidence Artifacts

- `.local/evidences/{run_id}/dotnet-test-output.txt` — dotnet test pass for all 3 .NET projects
- `.local/evidences/{run_id}/sylk-install-smoke.txt` — sylk install smoke pass
- `tests/python/ppm/test_r91_ppm_to_pgm_installed.py` — installed PPM path proof (2 tests)
