# Mainstream Next-Sprint Handoff — R2 Upgrade

## From Supervisor Traffic Controller R2 to Mainstream

**Source**: Supervisor stream (R2 sprint)
**Target**: Mainstream stream (next sprint)
**Current Classification**: PARTIAL_FEW_FAMILIES (breadth=2, need 3+)
**Current Decision**: CONTINUE_WITH_LIMITATIONS

## CLEAN_PASS Requirements

To achieve `CLEAN_PASS` classification, Mainstream must satisfy ALL of:

| Requirement | Minimum | Current | Gap |
|---|---|---|---|
| `families_touched` | 3 | 2 | +1 |
| `source_diffs` | 3 | ~2 | Need 3 format families with source changes |
| `governed_transcripts` | 3 | 0 | Need Skills to produce these |
| `raw_logs` | 3 | Need format-specific test logs | Capture per-family logs |
| `capability_matrix_deltas` | 3 | ~2 | Update capability matrix for each family |
| `repair_items / product_items` | repair < 50% | Unknown | Keep repair work < half of total |
| `skills_consumption` | consumed | not_consumed | See Skills gap below |
| `acceleration_consumption` | consumed | not_consumed | See Acceleration gap below |

## Target Format Families

Target **FODS + FODT + Netpbm** (3 distinct families):

### 1. FODS (Priority 1)
- 215 .NET tests already passing
- Add 2+ new APIs (e.g., `GetColumnHeaders`, `SortRows`)
- Capture per-family raw test log
- Update capability matrix

### 2. FODT (Priority 2)
- 201 .NET tests passing
- Add 2+ new APIs (e.g., `GetDocumentOutline`, `InsertHeading`)
- Capture per-family raw test log
- Update capability matrix

### 3. Netpbm (Priority 3)
- 120 .NET tests passing (PBM/PGM/PPM)
- Add 2+ new APIs (e.g., `Tile`, `Sharpen`)
- Capture per-family raw test log
- Update capability matrix

## Cross-Stream Requirements

### Skills Consumption
Skills stream must first produce governed execution transcripts.
Then Mainstream declares: `governed_execution_consumed: true` in replay results.

### Acceleration Consumption
Acceleration stream must first produce `ai_draft` outputs.
Then Mainstream declares: `reusable_accelerator_consumed: true` in replay results.

## Stop Conditions (Must Not Violate)

- Do NOT target fewer than 3 format families
- Do NOT declare CLEAN_PASS without `source_diffs ≥ 3`
- Do NOT declare `governed_execution_consumed: true` unless Skills produced transcripts
- Do NOT claim `reusable_accelerator_consumed: true` unless Acceleration produced ai_draft
- No git push / commit without explicit user authorization
- No Gate 8 or Gate 11 approval

## Evidence Required

Each format family needs:
1. At least 1 source diff (`src/net/{format}/*.cs` or `src/python/{format}/*.py`)
2. Raw test log showing tests pass for that family
3. Capability matrix update entry
4. (Optional) Governed execution transcript if Skills has produced one

## Routing Packet Reference

See [reports/supervisor-streams/mainstream/routing-packet.json](../../reports/supervisor-streams/mainstream/routing-packet.json) for the 8 actionable product gaps.
