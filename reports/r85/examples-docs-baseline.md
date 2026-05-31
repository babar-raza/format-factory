# R85 Train R — Examples and Docs Baseline for POC Products

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## New Examples (R85)

### Python: PBM → PGM (Dogfood Export)

**File:** examples/python/pbm/pbm_to_pgm_example.py

Demonstrates the R85 dogfood export workflow:
1. Parse PBM using format-factory-pbm (parse_pbm_strict)
2. Convert using convert_pbm_to_pgm (dogfood — no external libs)
3. Verify output is valid PGM with correct pixel mapping

### .NET: Netpbm First Slice

Tests demonstrate the complete first-slice workflow.
Example in tests/net/netpbm/ shows load/edit/save/export.
Standalone example file: not created (tests serve as living examples for .NET track).

## Existing Examples (Pre-R85)

| Format | Track | Examples | Sprint |
|--------|-------|---------|--------|
| FODS | Python | edit_save_fods.py, edit_save_export_fods.py, edit_save_export_fods_installed.py | R76-R82 |
| FODT | Python | (via tests) | R79 |
| ZST | Python | (via tests) | R34 |

## New Format-Family Playbooks (R85)

| File | Coverage |
|------|---------|
| docs/format-family-playbooks/00-index.md | Index |
| docs/format-family-playbooks/xml-office-like.md | FODS/FODT/ODS/ODT pattern |
| docs/format-family-playbooks/simple-binary-image.md | PBM/PGM/PPM/QOI pattern |

## Dogfood Export Docs (R85)

| File | Purpose |
|------|---------|
| docs/export/dogfood-export-strategy.md | Strategy + enforcement rules |
| reports/r85/dogfood-export-map.md | Per-format dogfood coverage matrix |

## Gap: .NET Netpbm Standalone Example

No standalone .NET example file created yet. The tests/net/netpbm/ test suite
serves as living documentation. A standalone `examples/net/netpbm/` directory
with a program.cs is scheduled for R86.

## TRAIN_R_STATUS: COMPLETE (Python example + playbooks + dogfood docs)
