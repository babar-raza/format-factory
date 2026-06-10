---
sprint: mainstream-R99
train: H
ledger: R99-GOVERNED-DOGFOOD-PGM-TO-PPM-PYTHON-001
---

# Dogfood Export Proof — R99

## New Dogfood: PGM -> PPM (Python, grayscale-to-color)

**Source library:** format-factory-pgm (`parse_pgm_strict`)
**Write backend:** format-factory-ppm (`write_ppm`)
**Example:** `examples/python/ppm/pgm_to_ppm_example.py`

### Workflow
1. Write sample PGM grayscale (3x3, maxval=255)
2. Parse PGM via `parse_pgm_strict`
3. Convert grayscale to RGB: gray -> (R=G=B)
4. Write PPM via `write_ppm`
5. Re-parse PPM via `parse_ppm_strict` and verify pixel mapping

### Execution Result
```
dogfood_status: IMPLEMENTED
dogfood_library: format-factory-ppm (write_ppm)
source_library: format-factory-pgm (parse_pgm_strict)
Pixel mapping verification: PASS (gray -> R=G=B)
```

### .NET Parallel: ToColor()
The R99 .NET `NetpbmImage.ToColor()` method performs the same PGM->PPM conversion at the product level.

## Cumulative Dogfood Map
| Path | Source | Target | Sprint |
|------|--------|--------|--------|
| PBM -> PGM | format-factory-pbm | format-factory-pgm | R85 |
| PBM -> PPM | format-factory-pbm | format-factory-ppm | R86 |
| PPM -> PGM | format-factory-ppm | format-factory-pgm | R90 |
| PGM -> PPM | format-factory-pgm | format-factory-ppm | R99 |

## Status: DOGFOOD PASS — NEW PGM->PPM EXPORT VERIFIED
