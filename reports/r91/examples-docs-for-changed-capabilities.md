---
sprint: R91
generated_by: r91-worker
---

# Examples and Docs for Changed Capabilities

## Summary

Examples added for all R91 new capabilities. All examples reference only real implemented APIs — no stubs, no forward references.

## FODS .NET: SetCellValue

File: `examples/net/fods/EditCellExample.cs`

Demonstrates:
- Loading a FODS workbook from file
- Calling `SetCellValue(sheetName, row, col, value)` to update a cell
- Saving the modified workbook back to FODS format

Only uses APIs that exist in `src/net/fods/FodsDocument.cs` after the R91 `SetCellValue` addition.

## FODT .NET: SaveToFile

File: `examples/net/fodt/SaveAfterEditExample.cs`

Demonstrates:
- Loading a FODT document from file
- Appending a paragraph using `AppendParagraph(text)`
- Saving to a new file path using `SaveToFile(path)`

Only uses APIs that exist in `src/net/fodt/FodtDocument.cs` after the R91 `SaveToFile` addition.

## Netpbm .NET: SetPixelColor

File: `examples/net/netpbm/PixelEditExample.cs`

Demonstrates:
- Loading a Netpbm image from file (PPM/PGM/PBM)
- Calling `SetPixelColor(x, y, color)` to update a pixel
- Writing the modified image back to file

Only uses APIs that exist in `src/net/netpbm/Model/NetpbmImage.cs` after the R91 `SetPixelColor` addition.

## Python PPM: Installed Workflow

File: `examples/python/ppm/installed_workflow.py`

Demonstrates:
- Importing from installed `ppm` package (no PYTHONPATH required)
- Parsing a PPM file using `parse_ppm_strict`
- Converting to PGM using `ppm_to_pgm`
- Writing the output PGM to disk

See also `reports/r91/python-netpbm-reduced-foss-product-hardening.md` for test coverage of this example.

## Correctness Constraints

All examples satisfy the following:
1. Import only from package public APIs (no `from ppm._internal import ...`)
2. Use only functions that exist in src/ after R91 changes are applied
3. Include a brief comment at the top: `# Requires: <package> at Gate 10 or later`
4. Do not claim Gate 11 / commercial availability

## Example Directory Structure After R91

```
examples/
  net/
    fods/
      EditCellExample.cs          (R91 NEW)
    fodt/
      SaveAfterEditExample.cs     (R91 NEW)
    netpbm/
      PixelEditExample.cs         (R91 NEW)
  python/
    ppm/
      installed_workflow.py       (R91 NEW)
```

## Evidence Artifacts

- `examples/net/fods/EditCellExample.cs`
- `examples/net/fodt/SaveAfterEditExample.cs`
- `examples/net/netpbm/PixelEditExample.cs`
- `examples/python/ppm/installed_workflow.py`
