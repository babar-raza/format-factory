# Truth Snapshot — Mainstream Mega-Train
# Generated: 2026-06-10
# Git HEAD: 3a3ba1a (main)
# Git status: 2 modified files (non-product, non-blocking)

## Gate 11 State (AUTHORITATIVE — from registry/format-registry.yaml)
- FODS gate_11: commercial_readiness_in_progress, approved_by: null, approved_date: null
- FODT gate_11: commercial_readiness_in_progress, approved_by: null, approved_date: null
- All other formats: gate_11 not_started, approved_by: null
- **CONCLUSION: Gate 11 is NOT approved for ANY format.**

## SDK Availability
- Python: 3.13.2
- .NET: 10.0.204
- pytest: available via .local/venv
- xUnit: available in .NET test projects

## .NET Build State (all 7 projects build with 0 errors)
| Project | Tests | Status |
|---------|-------|--------|
| FormatFactory.Fods | 547 | PASS |
| FormatFactory.Fodt | 520 | PASS |
| FormatFactory.Netpbm | 465 | PASS |
| FormatFactory.Csv | 15 | PASS |
| FormatFactory.Html | 12 | PASS |
| FormatFactory.Markdown | 11 | PASS |
| FormatFactory.Txt | 8 | PASS |
| **Total .NET** | **1578** | **ALL PASS** |

## Python Test State (candidate formats)
| Format | Tests | Maturity |
|--------|-------|----------|
| FODS | 211 | production_track_real |
| FODT | 248 | production_track_real |
| NDJSON | 233 | roundtrip_capable_library |
| ODS | 107 | export_capable_library |
| QOI | 108 | roundtrip_capable_library |
| ZST | 62 | production_track_real |
| PPM | 49 | read_only_prototype |
| PBM | 48 | read_only_prototype |
| PGM | 47 | read_only_prototype |
| XCF | 42 | probe_only |
| SYLK | 40 | read_only_prototype |
| DIF | 39 | read_only_prototype |
| ODT | 66 | read_only_prototype |
| TOML | 30 | read_write_library_foundation |
| CSV | 19 | read_only_prototype |
| TSV | 19 | read_only_prototype |
| ABW | 17 | probe_only (per matrix) |
| Gnumeric | 16 | probe_only (per matrix) |
| FODG | 19 | probe_only |
| FODP | 16 | probe_only |
| **Total Python (candidates)** | **4026 passed, 20 skipped** | |

## Dirty Git State Classification
- `reports/supervisor/materialized-evidence-review.md` — supervisor output, non-blocking
- `tests/supervisor/test_governance_validators_integration.py` — test file, non-blocking
- **No product source files dirty. No registry files dirty.**

## Advisory/Generated Contradictions
- Gnumeric, ABW, FODG, FODP: completion-matrix says probe_only but claimed G10 in registry
- These are KNOWN overclaims flagged in r33 review — gate corrections applied in pack.yaml
- Registry format-registry.yaml still shows claimed_gate G10 for these — evidence_backed_gate is G4

## Supervisor State
- Mode: MODE 4 (ACTIVE_MCP_ACTIVATION)
- Last sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-10-001
- Autonomous continue: True
- Last test count: 391 passed (supervisor scope)
