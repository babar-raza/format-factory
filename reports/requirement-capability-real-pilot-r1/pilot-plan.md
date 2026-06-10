# RCA Real Pilot R1 — Pilot Plan
# Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R1-001

## Pilot Configurations

### Pilot A — Netpbm (.NET)
- **Purpose:** Strong product-proof pilot
- **Spec input:** Spec Authority R2 — `src-r2-netpbm-spec` (ACCEPTED_WITH_CAVEAT, 12 requirements)
- **Claims:** load, save, edit, inspect — all ACCEPTED_FOR_POC
- **Expected outcome:** All claims pass coverage; dogfood present for save+edit
- **Actual outcome:** PASS — all 4 claims ACCEPTED_FOR_POC, coverage PASS

### Pilot B — FODS (.NET)
- **Purpose:** Overclaim prevention — architecture-blocked export
- **Spec input:** Spec Authority R2 — `src-r2-fods-odf13` (ACCEPTED_WITH_CAVEAT, 3 requirements)
- **Claims:** load, save, edit (ACCEPTED_FOR_POC); export_csv, export_html (BLOCKED)
- **Expected outcome:** Load/save/edit PASS; exports BLOCKED (no target writer)
- **Actual outcome:** PASS — 3 accepted, 2 blocked; no false PASS on exports

### Pilot C — FODT (.NET)
- **Purpose:** Second overclaim-prevention pilot
- **Spec input:** FIXTURE_BACKED (no R2 context pack for FODT)
- **Claims:** load, save, edit (ACCEPTED_FOR_POC); export_markdown, export_txt (BLOCKED)
- **Expected outcome:** Load/save/edit PASS; exports BLOCKED
- **Actual outcome:** PASS — 3 accepted, 2 blocked; no false PASS on exports

### Pilot D — ZST (Python)
- **Purpose:** Spec-backed roundtrip proof
- **Spec input:** Spec Authority R2 — `src-r2-zst-rfc8878` (ACCEPTED_SPEC — real RFC 8878)
- **Claims:** roundtrip, compress, decompress — all ACCEPTED_FOR_POC
- **Expected outcome:** All pass; staleness test: old-compress STALE/BLOCKED
- **Actual outcome:** PASS — 3 accepted, 1 stale blocked (synthetic staleness test)

### Pilot E — DIF (Python)
- **Purpose:** Legacy/empirical requirement pilot
- **Spec input:** Spec Authority R2 — `src-r2-dif-empirical` (EMPIRICAL_ONLY)
- **Claims:** parse, inspect — ACCEPTED_WITH_LIMITATIONS
- **Expected outcome:** Claims accepted with visible empirical caveat; UnsupportedFeature linked
- **Actual outcome:** PASS — 2 claims ACCEPTED_WITH_LIMITATIONS; empirical limitation visible

## Minimum Pass Criteria Met
- [x] Netpbm, FODS, FODT, and ZST evaluated
- [x] DIF evaluated as legacy/caveated pilot
- [x] At least one accepted claim (15 total)
- [x] At least one blocked claim (5 total: 4 arch-blocked + 1 stale)
