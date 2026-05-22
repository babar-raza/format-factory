# Export Dogfooding Status

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22

## FODS Export Status

| Exporter | Implemented | Tests | Installed-Wheel Proof |
|----------|-------------|-------|----------------------|
| CSV export (`csv_exporter.py`) | PASS | tests/python/fods/ | R51 (local wheel) |
| XML write (`workbook_to_xml`) | PASS | tests/python/fods/ | R51 (local wheel) |
| Formula preservation round-trip | **PASS (R53)** | test_r53_formula_preservation.py | R53 (local) |

## FODT Export Status

| Exporter | Implemented | Tests | Installed-Wheel Proof |
|----------|-------------|-------|----------------------|
| TXT export | PASS | tests/python/fodt/ | R51 (local wheel) |
| XML write (`document_to_xml`) | PASS | tests/python/fodt/ | R51 (local wheel) |
| Markdown export | NOT IMPLEMENTED | — | — |

## Export Dogfooding Gaps

### Gap: No Extracted-Bundle Replay

The installed-wheel smokes in R51 used locally built wheels from `.local/package-builds/`.
No round-trip proof from an extracted evidence bundle exists.

For clean dogfooding: extract the bundle ZIP, `pip install` the wheel from the extracted
`package-artifacts/` directory, then run FODS/FODT smoke.

**Blocked by:** R52/R53 do not contain artifact files in bundle (REQ-PKG-002, GAP-003).

### Gap: FODT Markdown Export

Planned but not implemented. Blocked by FODT writer structural preservation (TC-0057/0058/0059).
Markdown export requires headings and lists to be properly round-tripped first.

## R53 Dogfooding Result

Direct local dogfooding (not from extracted bundle):
```python
from src.python.fods.parser import parse_fods
from src.python.fods.writer import write_fods
# parse -> edit -> save -> reload -> CSV export — verified in tests
# formula preservation verified in test_r53_formula_preservation.py
```

**Result:** PASS (local source; not extracted-bundle)
