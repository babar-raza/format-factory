# Next Execution Prompt
## Taskcard-Driven Product Deepening + Autonomy Pilot Sprint

---

## Sprint Goal
Execute a controlled multi-lane sprint that advances product maturity, proves queue-backed autonomy, and prepares Gate 11-G approval — all under taskcard governance.

## Input Documents
- reports/system-maturity/plan-hardening-20260609/taskcards.yaml (governance)
- reports/system-maturity/plan-hardening-20260609/state-machine-governance.yaml (state machine)
- reports/system-maturity/plan-hardening-20260609/product-portfolio-maturity-matrix.md (format priorities)
- reports/system-maturity/plan-hardening-20260609/queue-autonomy-gap-verification.md (pilot design)

## Lanes (Parallel Execution)

### Lane A: Product Deepening (60% of sprint effort)
**Priority:** 1
**Focus:** Deepen FODS Python to publication candidate quality
**Tasks:**
1. Verify FODS Python roundtrip integrity (write_fods → parse → compare)
2. Add roundtrip test if missing
3. Create pyproject.toml with full metadata for format_factory_fods
4. Run install-test in clean venv
5. Document public API in README stub

**Allowed paths:** src/python/fods/, tests/python/fods/, package configs
**Forbidden paths:** registry/, AGENTS.md, src/net/

### Lane B: Autonomy Pilot (25% of sprint effort)
**Priority:** 2
**Focus:** Execute TC-C3 (PRODUCT_SOURCE_PATCH_BOUNDED pilot on ABW)
**Prerequisite:** Unblock TC-C3 by confirming:
  - Queue item anl-q-001 validates against schema
  - Selected function is confirmed unimplemented
  - Test file prepared before source patch
  - Rollback verified
**Tasks:**
1. Validate queue item
2. Execute pilot (50-line diff budget)
3. Write lane ledger entry
4. Auto-generate evidence declaration
5. Grade with supervisor

**Allowed paths:** src/python/abw/, tests/python/abw/, .local/supervisor/
**Forbidden paths:** registry/, AGENTS.md, src/net/, src/python/*/ (other formats)

### Lane C: Gate 11-G Packet Preparation (15% of sprint effort)
**Priority:** 3
**Focus:** Unblock TC-B4 and prepare agent-preparable portions of Gate 11-G packet
**Tasks:**
1. Create capability checklist from docs/gates.md criteria
2. Map current FODS .NET evidence to each criterion
3. Document test evidence summary (547 tests)
4. Document security posture (DTD prohibition, size guards)
5. List remaining human-required items
6. Package as Gate 11-G approval packet template

**Allowed paths:** reports/
**Forbidden paths:** registry/ (no gate status changes)

## Governance Rules
- All work must have taskcards (create new or unblock existing)
- State machine transitions must be logged
- No commits without explicit user authorization
- No Gate 11 approval (only packet preparation)
- No publication
- Product-first: ≥60% of items must be PRODUCT_SOURCE or TEST type
- Lane ledger entry required for every executed taskcard

## Success Criteria
1. FODS Python has pyproject.toml + roundtrip test + install-test result
2. One complete queue→patch→test→ledger→evidence cycle documented
3. Gate 11-G approval packet template exists
4. Zero test regressions
5. All taskcards in terminal states
6. Evidence bundle with SHA-256 provided

## Evidence Caveats
- Context-pack.yaml still contains stale Gate 11 overclaim (not corrected in planning sprint)
- Continuation-signal at iteration 10/12 (2 remaining before max_iterations)
- Mode 5 gate not yet approved by user
