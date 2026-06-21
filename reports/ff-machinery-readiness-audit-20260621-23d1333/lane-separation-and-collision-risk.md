# Lane Separation and Collision Risk
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Current Lane Structure

### Designed (per spec-to-feature-radical-correction-plan.md)

16 lanes defined:
- Lane 0: Coordinator
- Lanes 1-6: System healing (SAL, capability, skills, validators, qname, backfill)
- Lane 7-13: Product deepening (regeneration, migration, testing, exporters, gate prep)
- Lane 14: Autonomous supervision hardening
- Lane 15: Autonomous healing/learning

### Actual Implemented Structure

**ONE track exists: "product"**

The lane-execution-ledger.json contains basic per-lane metadata but does NOT enforce:
- Which source files each lane owns
- Which files are shared between lanes
- Which lane must complete before another begins
- Cross-lane collision detection

## Lane Boundary Map

| Lane | Purpose | Files | Separate track? |
|------|---------|-------|----------------|
| Machinery (SAL) | SAL pipeline repair | tools/specification-authority-layer/ | NO |
| Machinery (QName) | Canonical class creation | src/net/FormatFactory/, src/python/shared/ | NO |
| Machinery (Validators) | Add governance validators | tools/supervisor/governance_validators.py | NO |
| Machinery (Backfill) | Migrate existing src/ | src/**/*.py, src/**/*.cs | NO |
| Product (Feature) | Add features to existing products | src/python/{format}/, src/net/{format}/ | YES (sole current track) |
| Product (Tests) | Add/fix tests | tests/python/, tests/net/ | NO |
| Product (Gate prep) | Gate 11 readiness packets | reports/gate11/ | NO |

## Shared-File Risk Map

| File | Lane A reads/writes? | Lane B reads/writes? | Collision risk |
|------|---------------------|---------------------|----------------|
| src/python/fods/fods/__init__.py | Backfill (write) | Product deepening (write) | HIGH |
| src/net/fods/FodsDocument.cs | Backfill (write) | Product deepening (write) | HIGH |
| tools/supervisor/governance_validators.py | Validator lane (write) | Supervisor (read) | MEDIUM |
| reports/capability-layer/gap-ledger.json | Capability lane (write) | Product lane (read) | MEDIUM |
| .local/supervisor/continuation-signal.json | Machinery (read/write) | Product (read/write) | HIGH |
| registry/source-structure-baseline.json | Validator lane (read) | Any sprint with src/ changes | HIGH |

## Contamination/Collision Risk Matrix

| Scenario | Risk | Mitigation in place? |
|----------|------|---------------------|
| Machinery sprint adds validator → fails product sprint's governance | HIGH | NO |
| Product sprint adds analytics to xcf_analytics.py → triggers GOV_BLOCK | HIGH | YES (V42 validator) |
| Backfill migration changes class names → breaks 1000+ existing tests | CRITICAL | NO |
| SAL pipeline repair changes fact IDs → breaks declaration validation | HIGH | NO |
| QName canonical class creation at src/net/FormatFactory/ → conflicts with existing namespace | MEDIUM | NO |
| Plan lock from machinery sprint → blocks product sprint continuation | HIGH | YES (in design; currently stale lock is exactly this problem) |

## Required Guardrails

1. **Separate continuation signals**: Create `continuation-signal-machinery.json` parallel to `continuation-signal.json`
2. **File ownership locks**: YAML file declaring which lane owns which files (write ownership)
3. **Lane prerequisite gates**: `check_continuation_machinery.py` must pass before product lane opens
4. **Backfill isolation**: Backfill migration must run in a branch or staged per-file with test validation at each step
5. **Capability-product gate**: Product sprint that claims a capability must verify it's in the gap ledger AND has a GAP entry

## Required Supervisor Changes

1. Add `--track machinery` to `check_continuation.py`
2. Add `machinery_readiness_confirmed` field to approval-gates.md
3. Add `lane_ownership_conflicts` check to `autonomous_cycle.py`
4. Emit `GOV_BLOCK:lane_ownership_conflict` when a sprint touches files outside its declared lane
