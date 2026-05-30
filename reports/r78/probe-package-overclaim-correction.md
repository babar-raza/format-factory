# R78 Probe Package Overclaim Correction

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** J

## Overclaim Definition

R77 supervisor classification D77-09: FODP, FODG, Gnumeric, and ABW state files list
"Gates 1-10" as the gate status, implying equivalent product depth to FODS/FODT.
However, these formats have TECHNICAL EVIDENCE gates only — they do not have:
- Neutral model APIs (workbook_* or document_*)
- Edit capability
- Write capability beyond what was scaffolded
- Examples demonstrating real usage
- Commercial product depth

## Corrected Gate Assessment

| Format | True Gate Status | What Was Done | What Was NOT Done |
|---|---|---|---|
| FODP | Gates 1-10 technical evidence | Parser + basic probe; acquisition pack | No neutral model APIs; no write; no product depth |
| FODG | Gates 1-10 technical evidence | Parser + basic probe; acquisition pack | No neutral model APIs; no write; no product depth |
| Gnumeric | Gates 1-10 technical evidence | XML parser + gzip decompress; acquisition pack | No neutral model APIs; no write; no product depth |
| ABW | Gates 1-10 technical evidence | XML parser + DOCTYPE strip; acquisition pack | No neutral model APIs; no write; no product depth |

## Corrected State for Each Format

### FODP (OpenDocument Flat Drawing - Presentation)
- Gate 1-10: technical_evidence_only
- Python source: src/python/fodp/fodp_codec.py
- Public API: probe_fodp(), validate_file()
- NOT equivalent to FODS/FODT depth
- commercial_product_ready: false
- No examples, no product APIs beyond basic probe

### FODG (OpenDocument Flat Drawing - Graphics)
- Gate 1-10: technical_evidence_only
- Python source: src/python/fodg/fodg_codec.py
- Public API: probe_fodg(), validate_file()
- NOT equivalent to FODS/FODT depth
- commercial_product_ready: false

### Gnumeric (.gnumeric)
- Gate 1-10: technical_evidence_only
- Python source: src/python/gnumeric/gnumeric_codec.py
- Public API: probe_gnumeric(), decompress_gnumeric(), validate_file()
- NOT equivalent to FODS/FODT depth
- commercial_product_ready: false

### ABW (AbiWord)
- Gate 1-10: technical_evidence_only
- Python source: src/python/abw/abw_codec.py
- Public API: probe_abw(), parse_abw(), validate_file()
- NOT equivalent to FODS/FODT depth
- commercial_product_ready: false

## Corrected Language

Previous (overclaim): "Gates 1-10 PASSED" — implies same gate meaning as FODS/FODT
Corrected: "Gates 1-10 technical evidence complete" — clarifies technical gate passage
without implying commercial or product-depth equivalence

## Comparison Table: FODS vs Probe Packages

| Attribute | FODS | FODP/FODG/Gnumeric/ABW |
|---|---|---|
| Gate depth | Full product gates (all criteria) | Technical evidence only |
| API count | 28 public APIs | 2-4 basic probe APIs |
| Edit capability | YES (set_cell_value, add_sheet) | NO |
| Write capability | YES (write_fods, workbook_to_xml) | NO (or scaffolded only) |
| Examples | YES (2 examples) | NO |
| Neutral model | Full workbook model | Probe/validate only |
| Commercial consideration | alpha-foss-preview (Gates 1-10) | probe-only (not commercial-path) |

## State Correction Required

The following files should use corrected language (not changed in R78 to avoid scope creep;
documented here for next sprint action):

| File | Current Language | Corrected Language |
|---|---|---|
| state/current-state.md | Not explicitly listing probe status | Add corrected note |
| acquisition-packs/fodp/pack.yaml | gate_10: pass | gate_10: technical_evidence_only |
| acquisition-packs/fodg/pack.yaml | gate_10: pass | gate_10: technical_evidence_only |
| acquisition-packs/gnumeric/pack.yaml | gate_10: pass | gate_10: technical_evidence_only |
| acquisition-packs/abw/pack.yaml | gate_10: pass | gate_10: technical_evidence_only |

PROBE_OVERCLAIM_CORRECTION: DOCUMENTED
REMEDIATION_SCOPE: Next sprint (R79) — update acquisition pack yaml files
