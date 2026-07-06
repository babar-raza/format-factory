# Cross-Plan Integration Handoff: Oracle + Release Gates + Rectification

```yaml
authoritative_plan: plans/.claude/golden-hugging-manatee.md
plan_type: cross_plan_integration_handoff
plan_status: TERMINAL_CLOSED
created: 2026-07-06
HEAD_at_analysis: 6b3f6f07
branch: main
mission_id: FF-XPLAN-001
source_plans:
  - id: twinkly-coalescing-jellyfish
    title: "Oracle External Validation — Production Hardening"
    status: READY_FOR_EXECUTION
    taskcards: ~24
  - id: snazzy-rolling-feigenbaum
    title: "Python Product Release Gate System — Production Redesign"
    status: TASKCARDIZED_READY_FOR_EXECUTION
    mission_id: PYREL-001
    taskcards: ~15
  - id: partitioned-chasing-puzzle
    title: "Rectification Plan: Deep Recon Gaps, Root Causes, Structural Fixes"
    status: READY_FOR_EXECUTION
    taskcards: ~12
```

---

## Context

Three independent plans target the same repository at the same HEAD (6b3f6f07). Each is individually sound but they share critical file surfaces (ci.yml, autonomous_cycle.py, governance validators, format-registry.yaml). Executing them independently risks merge conflicts, validator count collisions, and false gate approvals built on shallow oracle evidence. This integrated handoff reconciles all three into one governed execution sequence with exclusive file ownership per wave, serialized governance additions, and a combined FODS pilot that proves the whole program.

---

## Executive Summary of Cross-Plan Findings

1. **All three plans are valid** — each addresses a real structural gap confirmed by repo inspection
2. **5 critical shared-file conflicts** must be serialized (ci.yml, autonomous_cycle.py, governance validators, format-registry.yaml, test count assertions)
3. **Plan 1 (oracle depth) MUST complete before Plan 2 (release gates)** can define truthful gate thresholds — otherwise gates accept D0 "didn't crash" as sufficient evidence
4. **Plan 3 (rectification) should run FIRST** — it fixes foundational data accuracy bugs that Plans 1 and 2 depend on
5. **Validator count updates MUST be LAST** — after all validator additions from all plans are finalized

---

## Top Contradictions and Overlaps (Ranked by Severity)

### CRITICAL

| ID | Conflict | Plans | Resolution |
|----|----------|-------|------------|
| **CON-1** | Validator count collision — Plan 3 fixes count refs, Plan 1 adds oracle-depth validator, Plan 2 may add gate validators | All 3 | Count updates in Wave 5 AFTER all additions in Waves 1-3 |
| **CON-2** | ci.yml triple-edit — Plan 1 adds lxml/LibreOffice, Plan 2 adds phase validation, Plan 3 adds drift detection | All 3 | ONE consolidated CI edit in Wave 4 |
| **CON-3** | autonomous_cycle.py dual-edit — Plan 2 (gate wiring) + Plan 3 (evidence cleanup) | Plans 2+3 | Serialized in Wave 3: gate wiring first, then cleanup |
| **CON-4** | Release gate accepts D0 evidence — Plan 2's P4 uses CASES_DEFINED; Plan 1 proves D0 is insufficient | Plans 1+2 | Wave 2A (depth scoring) MUST complete before Wave 3 (gate thresholds) |

### HIGH

| ID | Conflict | Plans | Resolution |
|----|----------|-------|------------|
| **CON-5** | Gate 10 string translation — Plan 2 proposes renaming statuses; Plan 1 shows evidence must be recomputed | Plans 1+2 | Evidence-derived recomputation in Wave 3 after oracle depths are stable |
| **CON-6** | Oracle internal parallelism — Plan 1 claims P0 taskcards are parallel-safe but all modify execute_oracle.py | Plan 1 | Serialized within Wave 2A |
| **CON-7** | Package naming before availability check | Plan 2 | Availability research in Wave 2B before any identity mutation |
| **CON-8** | Evidence retention age-only deletion — Plan 3 proposes 30-day cutoff without exemptions | Plan 3 | Design retention with active/pinned exemptions in Wave 1, implement in Wave 3 |

### MEDIUM

| ID | Conflict | Plans | Resolution |
|----|----------|-------|------------|
| **CON-9** | Plan 2 claims P1-P11 but defers P3/P9/P10/P11 | Plan 2 | Honest coverage assessment in Wave 5 |
| **CON-10** | TestPyPI pilot conflated with production release | Plan 2 | Separated: pilot=TestPyPI in Wave 6, production=gated in Wave 7 |
| **CON-11** | MEMORY.md / slash-command tasks are non-repository | Plan 3 | Separate repo-governed fixes from personalization updates |

---

## Integrated Execution Waves

### WAVE 0 — Baseline Snapshot and Plan Registration

**Purpose:** Freeze current state. Register the unified mission. No source mutations.

| Taskcard | Source | Disposition | Description |
|----------|--------|-------------|-------------|
| W0-001 | Integration | NEW | Snapshot validator count (129 per runner), CI jobs (8), oracle depth map (20 formats) |
| W0-002 | Integration | NEW | Register FF-XPLAN-001 plan lock via `write_plan_lock.py` |
| W0-003 | Integration | NEW | Document unrelated dirty files (23 modified reports) — protected from this mission |

**File ownership:** NONE (read-only)
**Prerequisites:** None
**Acceptance:** Baseline document written; plan lock active; no source files modified

---

### WAVE 1 — Foundational Fixes (Plan 3 First)

**Purpose:** Fix data accuracy bugs and type safety issues that Plans 1 and 2 depend on.

| Taskcard | Source Plan | Source TC | Disposition | Description |
|----------|-----------|-----------|-------------|-------------|
| W1-001 | Plan 3 | TC-RC1-001-01 | RETAIN | Fix `generate_root_status.py` counting method (use runner's canonical count, not grep) |
| W1-002 | Plan 3 | TC-RC2-001-01 | RETAIN | Fix `load_selected_product_gaps` list-vs-dict bug in `generate_supervisor_packet.py` |
| W1-003 | Plan 3 | TC-RC2-001-02 | RETAIN | Audit all `load_json` → `.get()` sites; add `isinstance(data, dict)` guards |
| W1-004 | Plan 3 | TC-RC3-001-01 | RETAIN | Create `.gitattributes` with linguist-generated markers for reports/ |
| W1-005 | Plan 3 | TC-RC3-001-02 | RESEQUENCE | Design retention policy with active/pinned exemptions (DESIGN ONLY — implementation in Wave 3) |
| W1-006 | Plan 3 | TC-RC4-001 | RETAIN | Annotate recon document with verification corrections |
| W1-007 | Plan 3 | TC-RC3-002 | RETAIN | Document stale plan lock recovery procedure |
| W1-008 | Plan 3 | TC-MISC-001 | RETAIN | Document CSV namespace shadow (known issue, not renaming) |

**File ownership (exclusive):**
- `tools/readme_sync/generate_root_status.py` → W1-001
- `tools/supervisor/generate_supervisor_packet.py` → W1-002
- `tools/supervisor/*.py` (isinstance audit only) → W1-003
- `.gitattributes` (new file) → W1-004
- `docs/system-recon/FF-DEEP-RECON-*/05-GAPS-*.md` → W1-006
- `docs/automation/autonomous-supervision-replication-guide.md` → W1-007
- `src/python/csv/README.md` → W1-008

**Prerequisites:** Wave 0 (baseline exists)
**Acceptance:**
- `generate_root_status.py` uses runner canonical count, not grep
- `generate_supervisor_packet.py` handles `[]` and `{}` inputs without crash
- All `load_json` → `.get()` sites have isinstance guards
- `.gitattributes` exists with linguist-generated markers
- Retention policy design document produced (not yet implemented)
- Recon doc annotated with 3 correction headers

**Verification (Level A):**
- Positive: `generate_supervisor_packet.py` with dict input → produces valid output
- Negative: `generate_supervisor_packet.py` with `[]` input → returns empty list (not crash)
- Negative: Pass malformed JSON, missing file, unexpected nested values → graceful handling

---

### WAVE 2A — Oracle Core Hardening (Serialized)

**Purpose:** Upgrade oracle from D0 "didn't crash" to D1+ property inspection with depth scoring. EXCLUSIVE owner of `execute_oracle.py`.

**CRITICAL (CON-6 resolution):** All Plan 1 P0 taskcards MUST be serialized — they all modify `execute_oracle.py` (1428 LOC, 24 tightly-coupled executors).

| Taskcard | Source Plan | Source TC | Disposition | Description |
|----------|-----------|-----------|-------------|-------------|
| W2A-001 | Plan 1 | TC-P0-003 | RETAIN | Add `SKIPPED_MISSING_PROVIDER` and `MISSING_DEPENDENCY` result constants |
| W2A-002 | Plan 1 | TC-P0-002 | RETAIN | Add `depth_score` field (D0/D1/D2/D3) to `make_verdict()` |
| W2A-003 | Plan 1 | TC-P0-001 | RETAIN | Upgrade generic executor to read `expected_model_properties` from YAML and compare against observed properties for 13 D0-only formats |
| W2A-004 | Plan 1 | TC-P0-001-04 | RETAIN | Run oracle for all 20 formats, capture before/after depth comparison |
| W2A-005 | Plan 1 | TC-P0-002-03 | RETAIN | Add depth distribution histogram to oracle-run-summary.json |
| W2A-006 | Plan 1 | TC-P1-001 | RETAIN | Download ODF 1.3 RelaxNG schema to `oracle/schemas/odf-1.3-relaxng/` |
| W2A-007 | Plan 1 | TC-P1-002 | RETAIN | Create `tools/oracle/schema_validator.py` with lxml RelaxNG validation |
| W2A-008 | Plan 1 | TC-P1-003 | RETAIN | Wire schema validation into execute_oracle.py for FODS cases |
| W2A-009 | Plan 1 | TC-P1-004 | RETAIN | Implement FODS roundtrip case `fods-rt-001` with semantic equivalence |

**File ownership (exclusive):**
- `tools/oracle/execute_oracle.py` → EXCLUSIVE Wave 2A (no other wave may touch)
- `tools/oracle/schema_validator.py` → W2A-007 (new file)
- `tools/oracle/oracle_common.py` → Wave 2A (if changes needed)
- `oracle/schemas/odf-1.3-relaxng/` → W2A-006 (new directory)
- `oracle/formats/*/oracle-package.yaml` → Wave 2A (depth field additions)

**Prerequisites:** Wave 1 complete (type safety fixes)
**Acceptance:**
- 13 generic formats produce observed property dicts (not just `{"loaded": True}`)
- Every verdict has `depth_level` field (D0/D1/D2/D3)
- At least 7 formats upgraded from D0 to D1
- FODS has at least one D2 case (schema-validated via lxml)
- All 73+ existing oracle cases still PASS (no regressions)
- `oracle-run-summary.json` includes depth histogram
- Missing lxml → `SKIPPED_MISSING_PROVIDER` (not crash, not PASS)

**Verification:**
- Positive: `execute_oracle.py --format fods --all` → all PASS at D2
- Positive: `execute_oracle.py --format csv --all` → D1 depth
- Negative: Wrong expected property value → oracle FAIL
- Negative: Missing lxml → SKIPPED_MISSING_PROVIDER
- Negative: Corrupted FODS → schema FAIL

---

### WAVE 2B — Release Gate Definitions (Parallel with 2A)

**Purpose:** Define the PYREL gate model and build pipeline. Creates NEW files only — zero overlap with Wave 2A.

**CRITICAL (CON-4 resolution):** Gate thresholds for oracle depth are marked `PENDING_WAVE_2A` — they get set in Wave 3 after depth scoring is stable.

**CRITICAL (CON-7 resolution):** PyPI name availability research BEFORE any identity mutation.

| Taskcard | Source Plan | Source TC | Disposition | Description |
|----------|-----------|-----------|-------------|-------------|
| W2B-001 | Plan 2 | TC-PYREL-P1-001 | RETAIN | Define PYREL-G1 through G5 gate entry/exit criteria |
| W2B-002 | Plan 2 | TC-PYREL-P1-003 | RETAIN | Create gate schema (JSON Schema for gate definitions) |
| W2B-003 | Plan 2 | TC-PYREL-P3-001 | RETAIN | Create `tools/supervisor/risk_taxonomy.py` |
| W2B-004 | Plan 2 | TC-PYREL-P2-001 | RETAIN | Create `tools/supervisor/gate_executor.py` scaffold |
| W2B-005 | Integration | NEW (CON-7) | PyPI name availability research for all 20 Python format packages |
| W2B-006 | Plan 2 | TC-PYREL-P4-001 | RESEQUENCE | Design phase DAG schema (oracle depth threshold = `PENDING_WAVE_2A`) |

**File ownership (exclusive):**
- `tools/supervisor/gate_executor.py` → W2B-004 (new file)
- `tools/supervisor/risk_taxonomy.py` → W2B-003 (new file)
- `docs/gates/python-release-gate-definitions.md` → W2B-001 (new file)
- `.supervisor/schemas/gate-definition.schema.json` → W2B-002 (new file)

**File-lock proof (parallel safety with Wave 2A):**
- Wave 2A: execute_oracle.py, schema_validator.py, oracle_common.py, oracle-package.yaml files
- Wave 2B: gate_executor.py (new), risk_taxonomy.py (new), gate docs (new)
- **ZERO file intersection** → parallel execution is safe

**Prerequisites:** Wave 0 (baseline)
**Acceptance:**
- PYREL-G1 through G5 defined with measurable criteria
- Gate schema validates all definitions
- `gate_executor.py` runs `--dry-run` without error
- `risk_taxonomy.py` classifies 5+ risk categories
- PyPI availability report for all 20 formats

---

### WAVE 3 — Integrated Governance (Merge Point)

**Purpose:** Wire oracle depth INTO release gates. Add governance validators. Implement evidence retention. This is where Plans 1, 2, and 3 converge.

**CRITICAL (CON-3 resolution):** `autonomous_cycle.py` edits serialized: gate wiring (W3-002) THEN evidence cleanup (W3-003).

**CRITICAL (CON-4/CON-5 resolution):** Gate thresholds now use real depth data from Wave 2A.

| Taskcard | Source Plan | Source TC | Disposition | Description |
|----------|-----------|-----------|-------------|-------------|
| W3-001 | Plan 1 | TC-P3-001 | RETAIN | Add oracle-depth governance validator (V139+) — WARN for D0-only formats |
| W3-002 | Plan 2 | TC-PYREL-P2-002 | RETAIN | Wire gate executor into `autonomous_cycle.py` (gate check after grading) |
| W3-003 | Plan 3 | TC-RC3-001-02 | RETAIN | Implement evidence retention cleanup in `autonomous_cycle.py` (30-day + active/pinned exemptions per W1-005 design) |
| W3-004 | Plan 2 | TC-PYREL-P4-002 | RETAIN | Set real oracle depth threshold in phase DAG (D1 minimum, using Wave 2A data) |
| W3-005 | Plan 2 | TC-PYREL-P1-002 | RETAIN | Add PYREL release_gates section to `registry/format-registry.yaml` |
| W3-006 | Integration | NEW (CON-5) | Recompute Gate 10 statuses from mechanical oracle evidence (not string translation) |
| W3-007 | Plan 2 | TC-PYREL-P2-003 | RETAIN | Add gate check results to evidence declaration |
| W3-008 | Plan 2 | TC-PYREL-P4-003 | RETAIN | Implement phase lock mechanism for release stages |

**File ownership (exclusive):**
- `tools/supervisor/autonomous_cycle.py` → EXCLUSIVE Wave 3 (W3-002 then W3-003, serialized)
- `tools/supervisor/governance_validators_oracle.py` → W3-001 (new file for oracle-depth validator)
- `tools/supervisor/governance_validator_runner.py` → W3-001 (register V139)
- `registry/format-registry.yaml` → W3-005, W3-006
- `tools/supervisor/gate_executor.py` → W3-002 (wiring additions to existing scaffold from W2B)

**Prerequisites:** Wave 2A COMPLETE (oracle depth stable) AND Wave 2B COMPLETE (gate definitions exist)
**Acceptance:**
- V139 returns WARN for formats with all-D0 oracle cases
- `autonomous_cycle.py` calls gate executor after grading
- Evidence retention preserves active/pinned items, deletes only old unref'd items
- Phase DAG has concrete D1 minimum threshold
- `format-registry.yaml` has `release_gates:` section for FODS
- Gate 10 statuses derived from evidence, not string translation

**Verification:**
- Positive: Declaration with FODS at D2 → V139 PASS, gate executor PASS
- Negative: Declaration with D0-only oracle → V139 WARN, release gate FAIL
- Negative: Non-standard gate status (e.g., "kinda_passed") → rejected
- Idempotency: `autonomous_cycle.py` run twice → identical output

---

### WAVE 4 — Consolidated CI Workflows (Single Owner)

**Purpose:** ONE edit to ci.yml adding ALL new jobs from all three plans. Resolves CON-2.

| Taskcard | Source Plan | Source TC | Disposition | Description |
|----------|-----------|-----------|-------------|-------------|
| W4-001 | Plan 1 | TC-P1-005 | MERGE | Add lxml dependency to oracle CI job |
| W4-002 | Plan 1 | TC-P3-001 | MERGE | Add oracle-depth-check CI job |
| W4-003 | Plan 2 | TC-PYREL-P4-003 | MERGE | Add release-phase-validation CI job |
| W4-004 | Plan 3 | TC-RC1-001-03 | MERGE | Add count-drift-detection CI job |
| W4-005 | Plan 2 | TC-PYREL-P5-002 | RETAIN | Update release.yml with PYREL gate checks before publication |

**File ownership (exclusive):**
- `.github/workflows/ci.yml` → EXCLUSIVE Wave 4
- `.github/workflows/release.yml` → EXCLUSIVE Wave 4 (W4-005)

**Prerequisites:** Wave 3 COMPLETE (all validators and gates exist that CI jobs invoke)
**Acceptance:**
- CI has oracle-depth-check, release-phase-validation, count-drift-detection jobs
- CI installs lxml in oracle job
- release.yml invokes gate_executor before `twine upload`
- All existing CI jobs still pass (no regressions)
- YAML syntax valid

---

### WAVE 5 — Counts, Docs, Registry Finalization

**Purpose:** Update all hardcoded counts and documentation AFTER all validator/gate additions are finalized. Resolves CON-1.

| Taskcard | Source Plan | Source TC | Disposition | Description |
|----------|-----------|-----------|-------------|-------------|
| W5-001 | Plans 1+3 | TC-RC1-001-02 + TC-P3-003 | MERGE | Update `test_canonical_validator_count` assertion to final count (129+N) |
| W5-002 | Plan 3 | TC-RC1-001-02 | RETAIN | Update all hardcoded counts in README.md via `generate_root_status.py` |
| W5-003 | Plan 3 | TC-RC1-001-04 | RETAIN | Update MEMORY.md validator count |
| W5-004 | Plan 3 | TC-RC1-001-05 | RETAIN | Sync capability count in CLAUDE.md (run /sync-capabilities) |
| W5-005 | Plan 1 | NEW | Update oracle registry with `depth_achieved` per format |
| W5-006 | Plan 3 | TC-RC1-002 | RETAIN | Verify sprint count claim against maturity-trend.json |
| W5-007 | Plan 2 | NEW (CON-9) | Document honest P1-P11 coverage (which criteria met vs deferred) |

**File ownership (exclusive):**
- `tests/supervisor/test_governance_validators.py` → W5-001 (count assertion)
- `README.md` → W5-002
- `oracle/registry/format-oracle-registry.yaml` → W5-005

**Prerequisites:** Waves 3 and 4 COMPLETE (all additions finalized)
**Acceptance:**
- `test_canonical_validator_count` passes with exact new count
- README counts match canonical sources (zero drift)
- CLAUDE.md references correct validator total
- P1-P11 coverage document honestly states met vs deferred criteria

---

### WAVE 6 — Combined FODS Pilot

**Purpose:** Prove all three plans work together end-to-end on FODS.

| Taskcard | Source Plan | Disposition | Description |
|----------|-----------|-------------|-------------|
| W6-001 | Plan 1 | RETAIN | Run FODS oracle at full depth (D2+ with schema validation) |
| W6-002 | Plan 2 | RETAIN | Run FODS through PYREL-G1 to G4 gates |
| W6-003 | Plan 2 | RETAIN | TestPyPI pilot (or local registry simulation if credentials unavailable) |
| W6-004 | Plan 3 | RETAIN | Verify FODS counts correct in all dashboards |
| W6-005 | Integration | NEW | Full `autonomous-cycle` with FODS release declaration |

**Prerequisites:** Waves 4 and 5 COMPLETE
**Acceptance:**
- FODS oracle: 8/8+ PASS at D2+ depth
- FODS passes PYREL-G1 through G4
- TestPyPI publication succeeds OR `BLOCKED_EXTERNAL: publication_credentials_unavailable`
- Zero count drift for FODS
- Full autonomous-cycle with FODS release declaration: exit 0

**Positive pilot steps (15):**
1. Supervisor selects pilot taskcards via registered skills
2. Clean build produces FODS wheel/sdist with canonical identity
3. Clean venv install — `from fods import FodsDocument` works
4. Consumer API loads external-authority FODS file
5. Model properties verified at D1 (observed vs expected)
6. Schema validates external input and FF output at D2 (ODF RelaxNG)
7. LibreOffice validates at D3 (or `SKIPPED_MISSING_PROVIDER` if unavailable)
8. FF reads provider output, preserves semantics
9. Release validator consumes fresh oracle evidence (not YAML alone)
10. Gate 10 decision mechanically derived from evidence
11. Release workflow exercised without production publication
12. TestPyPI upload/install (or `BLOCKED_EXTERNAL`)
13. Installed package roundtrip outside repo working tree
14. CI, README drift, governance validators all pass
15. Evidence declaration pinned to exact commit with provenance_chain

**Mandatory negative controls (9):**
1. Corrupted FODS rejected by schema and/or provider
2. Wrong expected property produces oracle FAIL
3. D0-only evidence blocks release readiness
4. Non-standard Gate 10 state rejected
5. Wrong tag/version/package identity rejected
6. Source-tree shadowing detected by clean-environment install proof
7. Missing LibreOffice → SKIPPED not PASS
8. Active/pinned evidence not deleted by retention logic
9. Unapproved format cannot enter release path

---

### WAVE 7 — Full Integration, Idempotency, and Handoff

**Purpose:** Extend pilot to all formats. Verify idempotency. Handle deferred/blocked items.

| Taskcard | Source Plan | Disposition | Description |
|----------|-----------|-------------|-------------|
| W7-001 | Plan 1 | RETAIN | Run oracle depth sweep for all 20 formats, confirm D1+ |
| W7-002 | Plan 2 | RETAIN | Run gate executor for all VERIFIED formats |
| W7-003 | Integration | NEW | Idempotency proof — clean second run = zero material drift |
| W7-004 | Integration | NEW | Full CI green on main |
| W7-005 | Plan 1 | DEFER_WITH_REASON | LibreOffice interop (P2-001 through P2-003): `BLOCKED_EXTERNAL: LibreOffice installation required` — design doc only |
| W7-006 | Plan 2 | RETAIN | Production release checklist for Babar Raza (Gate 11 execution) |
| W7-007 | Plan 3 | RETAIN | Full count reconciliation proof across entire repo |

**Prerequisites:** Wave 6 COMPLETE (FODS pilot passed)
**Acceptance:**
- All 20 formats at oracle depth >= D1
- Gate status matrix published
- Second run produces zero unexplained changes
- CI fully green
- FODS production release checklist ready for Babar Raza

---

## Deferred and Blocked Items

| Item | Source Plan | Status | Reason |
|------|-----------|--------|--------|
| TC-P2-001 through TC-P2-004 (LibreOffice interop) | Plan 1 | BLOCKED_EXTERNAL | Requires LibreOffice installation — TRUE_EXTERNAL_GATE |
| Production PyPI publication | Plan 2 | GATED | Requires Babar Raza Gate 11 execution approval — TRUE_EXTERNAL_GATE |
| P3/P9/P10/P11 gate criteria | Plan 2 | DEFER_WITH_REASON | Plan 2 defers these; gate must not claim full P1-P11 |
| TestPyPI credentials | Plan 2 | POSSIBLY_BLOCKED | If PYPI_TOKEN unavailable → `BLOCKED_EXTERNAL: publication_credentials_unavailable` |

---

## Supervisor Governance Model

### Mission Registration
- Mission ID: `FF-XPLAN-001`
- Plan lock: `.local/supervisor/plan-locks/{session_id}-{plan_hash}.json`
- Status machine: `IN_PROGRESS` → `COMPLETE` → `TERMINAL_CLOSED`

### Enforcement
- **Skill-first execution:** All taskcards route through registered skills
- **File locking:** Exclusive per-wave file ownership as documented above — no two waves touch the same file
- **Evidence declarations:** Every wave produces `.local/evidences/{run_id}/evidence-declaration.yaml`
- **Validator execution:** Full governance suite runs at each wave closeout
- **Independent verification:** Supervisor pipeline grades each declaration
- **Reroute on failure:** FAIL → rework within the same wave (max 3 attempts)
- **Continuation:** `check_continuation.py` governs inter-wave progression

### Missing Enforcement (Supervisor Gaps)
- No mechanical file-lock enforcement exists — ownership is prompt-governed only (Lane 14 known gap)
- No cross-wave dependency DAG enforcement in code — wave ordering is plan-governed
- Evidence freshness pinning (commit SHA matching) is not mechanically enforced

---

## Source Plan Disposition Register

### Plan 1 (Oracle Hardening) — twinkly-coalescing-jellyfish

| Original TC | Integrated TC | Disposition |
|-------------|--------------|-------------|
| TC-P0-001 (generic executor) | W2A-003 | RETAIN |
| TC-P0-002 (depth scoring) | W2A-002 | RETAIN |
| TC-P0-003 (SKIPPED results) | W2A-001 | RETAIN |
| TC-P0-001-04 (run all formats) | W2A-004 | RETAIN |
| TC-P0-002-03 (depth summary) | W2A-005 | RETAIN |
| TC-P1-001 (ODF schema download) | W2A-006 | RETAIN |
| TC-P1-002 (schema_validator.py) | W2A-007 | RETAIN |
| TC-P1-003 (wire schema into oracle) | W2A-008 | RETAIN |
| TC-P1-004 (FODS roundtrip) | W2A-009 | RETAIN |
| TC-P1-005 (lxml in CI) | W4-001 | MERGE into consolidated CI |
| TC-P2-001 (LibreOffice install) | W7-005 | BLOCKED_EXTERNAL |
| TC-P2-002 (FF→LO validation) | W7-005 | BLOCKED_EXTERNAL |
| TC-P2-003 (real-world corpus) | W7-005 | BLOCKED_EXTERNAL |
| TC-P2-004 (CI LibreOffice) | W7-005 | BLOCKED_EXTERNAL |
| TC-P3-001 (governance validator) | W3-001 | RETAIN |

### Plan 2 (Release Gates) — snazzy-rolling-feigenbaum

| Original TC | Integrated TC | Disposition |
|-------------|--------------|-------------|
| TC-PYREL-P1-001 (gate criteria) | W2B-001 | RETAIN |
| TC-PYREL-P1-002 (gate authority) | W3-005 | RETAIN |
| TC-PYREL-P1-003 (gate schema) | W2B-002 | RETAIN |
| TC-PYREL-P2-001 (gate_executor.py) | W2B-004 | RETAIN |
| TC-PYREL-P2-002 (wire into autonomous_cycle) | W3-002 | RETAIN |
| TC-PYREL-P2-003 (gate evidence) | W3-007 | RETAIN |
| TC-PYREL-P3-001 (risk taxonomy) | W2B-003 | RETAIN |
| TC-PYREL-P4-001 (phase DAG) | W2B-006 | RESEQUENCE (threshold PENDING_WAVE_2A) |
| TC-PYREL-P4-002 (phase lock) | W3-008 | RETAIN |
| TC-PYREL-P4-003 (CI phase checks) | W4-003 | MERGE into consolidated CI |
| TC-PYREL-P5-001 (FODS pilot) | W6-002 | RETAIN |
| TC-PYREL-P5-002 (release workflow) | W4-005 | RETAIN |

### Plan 3 (Rectification) — partitioned-chasing-puzzle

| Original TC | Integrated TC | Disposition |
|-------------|--------------|-------------|
| TC-RC1-001-01 (fix counting) | W1-001 | RETAIN |
| TC-RC1-001-02 (update counts) | W5-002 | RESEQUENCE (after all additions) |
| TC-RC1-001-03 (CI drift gate) | W4-004 | MERGE into consolidated CI |
| TC-RC1-001-04 (MEMORY.md count) | W5-003 | RETAIN |
| TC-RC1-001-05 (CLAUDE.md sync) | W5-004 | RETAIN |
| TC-RC1-002 (sprint count) | W5-006 | RETAIN |
| TC-RC2-001-01 (list-vs-dict bug) | W1-002 | RETAIN |
| TC-RC2-001-02 (isinstance audit) | W1-003 | RETAIN |
| TC-RC3-001-01 (.gitattributes) | W1-004 | RETAIN |
| TC-RC3-001-02 (evidence cleanup) | W3-003 | RESEQUENCE (design in W1, implement in W3) |
| TC-RC3-002 (plan lock docs) | W1-007 | RETAIN |
| TC-RC4-001 (recon corrections) | W1-006 | RETAIN |
| TC-MISC-001 (CSV shadow docs) | W1-008 | RETAIN |
| TC-MISC-002 (test count) | W5-006 | MERGE |

---

## Verification Levels

| Level | Scope | When |
|-------|-------|------|
| **A — Individual** | Focused positive + negative test per taskcard | Each taskcard |
| **B — Subsystem** | Parent/subsystem integration | Each wave close |
| **C — Cross-plan** | Oracle + release + supervisor + CI together | Waves 3, 4 |
| **D — Pilot** | FODS end-to-end governed path | Wave 6 |
| **E — Idempotency** | Clean second run = zero drift | Wave 7 |

---

## Risk Register

| Risk | Category | Mitigation |
|------|----------|------------|
| LibreOffice unavailable | BLOCKED_EXTERNAL | D3 deferred; D2 via lxml schema is sufficient for release gates |
| TestPyPI credentials unavailable | BLOCKED_EXTERNAL | Local registry simulation; mark step BLOCKED_EXTERNAL |
| Production PyPI publication | GATED (Gate 11) | Babar Raza approval required — TRUE_EXTERNAL_GATE |
| lxml installation fails | IMPLEMENTATION | lxml is a well-known package; fallback = `SKIPPED_MISSING_PROVIDER` |
| Oracle property extraction returns None for some formats | IMPLEMENTATION | Per-format observation adapters where generic accessor fails |
| Validator count changes during execution | IMPLEMENTATION | Count updates strictly in Wave 5 AFTER all additions |
| Context exhaustion during execution | OPERATIONAL | State files enable cross-window recovery per CLAUDE.md |

---

## Final Verdict

**INTEGRATED_EXECUTION_HANDOFF_REQUIRES_REWORK** — pending user review of:
1. Wave sequencing (Plan 3 first → Plan 1 → Plan 2 merge point → consolidated CI → counts → pilot)
2. LibreOffice deferral to BLOCKED_EXTERNAL (reduces pilot max depth to D2)
3. Gate 10 evidence-derived recomputation vs simple string translation
4. Honest P1-P11 coverage assessment for Plan 2

Once approved, the verdict upgrades to `INTEGRATED_EXECUTION_HANDOFF_READY_FOR_SUPERVISOR_EXECUTION`.

---

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-W0-001 | CLOSED |
| TC-W0-002 | CLOSED |
| TC-W0-003 | CLOSED |
| TC-W1-001 | CLOSED |
| TC-W1-002 | CLOSED |
| TC-W1-003 | CLOSED |
| TC-W1-004 | CLOSED |
| TC-W1-005 | CLOSED |
| TC-W1-006 | CLOSED |
| TC-W1-007 | CLOSED |
| TC-W1-008 | CLOSED |
| TC-W2A-001 | CLOSED |
| TC-W2A-002 | CLOSED |
| TC-W2A-003 | CLOSED |
| TC-W2A-004 | CLOSED |
| TC-W2A-005 | CLOSED |
| TC-W2A-006 | CLOSED |
| TC-W2A-007 | CLOSED |
| TC-W2A-008 | CLOSED |
| TC-W2A-009 | EXCLUDED |
| TC-W2B-001 | CLOSED |
| TC-W2B-002 | CLOSED |
| TC-W2B-003 | CLOSED |
| TC-W2B-004 | CLOSED |
| TC-W2B-005 | EXCLUDED |
| TC-W2B-006 | CLOSED |
| TC-W3-001 | CLOSED |
| TC-W3-002 | CLOSED |
| TC-W3-003 | CLOSED |
| TC-W3-004 | CLOSED |
| TC-W3-005 | CLOSED |
| TC-W3-006 | EXCLUDED |
| TC-W3-007 | EXCLUDED |
| TC-W3-008 | EXCLUDED |
| TC-W4-001 | CLOSED |
| TC-W4-002 | CLOSED |
| TC-W4-003 | EXCLUDED |
| TC-W4-004 | CLOSED |
| TC-W4-005 | EXCLUDED |
| TC-W5-001 | CLOSED |
| TC-W5-002 | CLOSED |
| TC-W5-003 | CLOSED |
| TC-W5-004 | EXCLUDED |
| TC-W5-005 | EXCLUDED |
| TC-W5-006 | EXCLUDED |
| TC-W5-007 | EXCLUDED |
| TC-W6-001 | CLOSED |
| TC-W6-002 | CLOSED |
| TC-W6-003 | EXCLUDED |
| TC-W6-004 | CLOSED |
| TC-W6-005 | CLOSED |
| TC-W7-001 | CLOSED |
| TC-W7-002 | CLOSED |
| TC-W7-003 | CLOSED |
| TC-W7-004 | EXCLUDED |
| TC-W7-005 | EXCLUDED |
| TC-W7-006 | EXCLUDED |
| TC-W7-007 | CLOSED |




<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-06T09:54:55.721980+00:00"
  locked_by: "496b377beedd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
