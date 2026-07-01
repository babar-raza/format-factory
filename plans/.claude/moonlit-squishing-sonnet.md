# Plan: Capability Layer Healing — Full Rebuild, Reconciliation & Proof
**Plan ID:** moonlit-squishing-sonnet
**Type:** capability_layer_healing
**Created:** 2026-07-01
**Mission:** Rebuild the product capability matrix and all derived artifacts from authoritative obligations, reconcile the gap ledger, wire taskcard linkage, repair consumers, prove through pilots, and enforce idempotency.

---

## Context

The capability layer (L03) is classified as HARDENING_REQUIRED / DEGRADED (maturity 3/5). The
exploration revealed several structural defects that undermine trust in all downstream artifacts:

1. **Inverted authority**: `capability_map_generator.py` uses `poc-targets.yaml` as its PRIMARY
   capability authority. SAL facts are used as enrichment only. The correct chain is:
   SAL facts → obligations → capability requirements → evidence query → gap/verified state.

2. **30/32 open gaps lack taskcards** (93.75%): The bottleneck blocking autonomous execution.
   `capability_to_feature_compiler.py` is a planning stub only; no runtime wiring to autonomous cycle.

3. **Dead and vestigial code**:
   - `gap_ledger_to_work_items.py` — orphaned, logic duplicated in `capability_feature_compiler.py`
   - `capability_queue_consumer.py` — loads FOSS capability map but never uses it
   - `select_poc_gaps.py` — references `poc-targets.yaml` but actual logic uses hardcoded
     `_GAP_WRITER_PROOF` dict; poc-targets path is vestigial

4. **28 MB gap ledger for 32 actionable items**: 1,245 closed gaps pollute active selection.
   No active/historical split exists.

5. **No obligation provenance chain**: capability records have `spec_refs[]` fields populated by
   keyword-matched SAL facts, but no formal `obligation_id` linkage. Every capability needs a
   traceable obligation.

6. **No hash-based queue staleness detection**: consumers cannot verify whether the action queue
   is current against the ledger.

7. **No transactional pipeline**: generator writes artifacts one-by-one with no rollback on failure.

8. **Required output reports do not exist**: `capability-system-inventory.yaml`,
   `capability-consumer-graph.yaml`, `capability-authority-model.yaml`,
   `capability-coverage-universe.yaml`, `capability-proof-audit.yaml` are all missing.

---

## Critical File Paths

| File | Role |
|------|------|
| `product-capability-matrix/poc-targets.yaml` | POC dashboard (19 targets); should be scope/priority input only |
| `tools/capability_layer/capability_map_generator.py` | Generator (1,505 lines); refactor to SAL-driven |
| `tools/capability_layer/validate_capability_map.py` | 10 validators (VAL-001—010); extend |
| `tools/capability_layer/capability_to_feature_compiler.py` | Planning stub only (advisory) |
| `tools/supervisor/capability_feature_compiler.py` | CANONICAL pipeline consumer of gap-ledger |
| `tools/supervisor/capability_queue_consumer.py` | Dead FOSS map load; clean up |
| `tools/supervisor/select_poc_gaps.py` | Vestigial poc-targets ref; uses hardcoded dict |
| `tools/supervisor/gap_ledger_to_work_items.py` | ORPHANED dead code; deprecate |
| `tools/supervisor/autonomous_cycle.py` | Step 4a reads gap-ledger; Step 3e calls queue_consumer |
| `tools/supervisor/check_system_healing_gate.py` | Lane 2 gate; reads action-queue + unified map |
| `reports/capability-layer/gap-ledger.json` | 1,277 gaps (1,245 closed, 32 open); needs split |
| `reports/capability-layer/action-queue.json` | 84 actions; needs hash-based staleness |
| `reports/capability-layer/commercial-capability-map.json` | Generated (2026-06-25) |
| `reports/capability-layer/foss-reduced-capability-map.json` | Generated (2026-06-25) |
| `reports/capability-layer/unified-capability-map.json` | Generated (2026-06-25) |
| `.local/spec-cache/sal-facts-latest.json` | 14,635 SAL facts; the obligation source |
| `registry/format-registry.yaml` | 25 canonical format IDs and families |
| `plans/layers/capability-layer.md` | L03 layer plan (HARDENING_REQUIRED) |
| `.local/evidences/capability-layer-healing-<run-id>/` | Evidence directory for this mission |

---

## Existing Utilities to Reuse

- `tools/spec/merge_sal_facts.py` — merges per-format SAL files; use to confirm latest combined DB
- `tools/supervisor/capability_feature_compiler.py` — CANONICAL gap-to-work-items; extend not replace
- `tools/supervisor/autonomous_cycle.py` (Step 4a) — already calls capability_feature_compiler; wire taskcards there
- `tools/capability_layer/validate_capability_map.py` — extend VAL-008 (taskcard linkage) and add new validators
- `.supervisor/skill-registry.yaml` — register new skills if needed
- `tools/supervisor/write_plan_lock.py` — for plan lock management
- `.venv/Scripts/pytest` — test runner (NOT `python -m pytest`)

---

## Execution Blocks

### BLOCK 1 — Recon Reports (TC-CAP-001 through TC-CAP-003)
*Mission sections 2, 3, 4 — produce the three required YAML reports*

#### TC-CAP-001: Generate capability-system-inventory.yaml
**Status:** OPEN
**Objective:** Produce `reports/capability-layer/capability-system-inventory.yaml` with one entry
per capability artifact. Required counter: `UNINVENTORIED_CAPABILITY_ARTIFACTS = 0`.

**Steps:**
1. Enumerate all files in `reports/capability-layer/`, `tools/capability_layer/`, `product-capability-matrix/`
2. For each artifact, capture: path, type, producer, consumers, source_inputs, generated_at,
   generator_version (if any), current (bool), authoritative (bool), stale (bool), findings
3. Write YAML using the `capability_artifact` schema from mission §2
4. Verify all major artifacts are covered (maps, ledger, queue, validators, tools, plans)

**Validation:** `UNINVENTORIED_CAPABILITY_ARTIFACTS = 0`

#### TC-CAP-002: Generate capability-consumer-graph.yaml
**Status:** OPEN
**Objective:** Produce `reports/capability-layer/capability-consumer-graph.yaml` classifying every
consumer. Required counter: `FALSE_CAPABILITY_CONSUMER_CLAIMS = 0`.

**Steps:**
1. For each consumer file (capability_map_generator, validate_capability_map, select_poc_gaps,
   autonomous_task_generator, gap_ledger_to_work_items, capability_feature_compiler,
   capability_queue_consumer, check_system_healing_gate, update-capability-matrix skill,
   promote-gap-to-taskcard skill, master-plan, capability-layer.md):
   - Classify as: DIRECT_RUNTIME_CONSUMER, INDIRECT_RUNTIME_CONSUMER, GOVERNANCE_CONSUMER,
     SKILL_OR_COMMAND_CONSUMER, REPORT_ONLY_REFERENCE, HISTORICAL_REFERENCE, or FALSE_OR_STALE_CLAIM
   - Record inputs, outputs, filtering rules, stale_artifact_behavior, runtime_proof
2. Mark FALSE findings explicitly:
   - `gap_ledger_to_work_items.py` → FALSE_OR_STALE_CLAIM (ORPHANED dead code)
   - `capability_queue_consumer.py` FOSS map load → FALSE_OR_STALE_CLAIM
   - `select_poc_gaps.py` poc-targets ref → FALSE_OR_STALE_CLAIM
3. Document remediation action for each false claim

**Validation:** `FALSE_CAPABILITY_CONSUMER_CLAIMS = 0` (all false claims documented)

#### TC-CAP-003: Generate capability-authority-model.yaml
**Status:** OPEN
**Objective:** Produce `reports/capability-layer/capability-authority-model.yaml` defining the
canonical authority chain. Required counter: `AMBIGUOUS_CAPABILITY_AUTHORITIES = 0`.

**Steps:**
1. Define the authority chain schema per mission §4:
   - SAL/spec fact → product/format obligation → capability identity →
     implementation evidence → verification evidence → gap or verified state → taskcard when actionable
2. Document the role of each artifact (poc-targets.yaml, SAL facts, format registry,
   capability maps, gap ledger, action queue, taskcards)
3. Record ALL current violations of the authority chain (inverted authority in generator,
   prose-derived capabilities, etc.)
4. Record the target state for each authority violation

**Validation:** `AMBIGUOUS_CAPABILITY_AUTHORITIES = 0` (all authorities explicitly assigned)

---

### BLOCK 2 — Identity and Universe (TC-CAP-004 through TC-CAP-005)
*Mission sections 5, 6 — normalize identities, rebuild eligible universe*

#### TC-CAP-004: Identity Normalization
**Status:** OPEN
**Objective:** Produce `reports/capability-layer/capability-subjects.yaml` with canonical
`capability_subject` entries. Required counters: `UNRESOLVED_PRODUCT_FORMAT_IDENTITIES = 0`,
`DUPLICATE_CAPABILITY_SUBJECTS = 0`.

**Steps:**
1. Read `registry/format-registry.yaml` — enumerate all 25 canonical format IDs
2. For each format, define capability_subject entries per language track (Python/dotnet) and
   commercial vs FOSS:
   - PBM/PGM/PPM: aggregate_parent=netpbm, aggregate_children=[pbm, pgm, ppm]
   - FODS/FODT: separate subjects (not a grouped family, despite being related ODF formats)
   - Netpbm commercial: aggregate (PBM+PGM+PPM combined dotnet product)
   - Each Python FOSS format: individual subject
3. Map all aliases and legacy IDs from poc-targets.yaml to canonical format IDs
4. Record aggregation and expansion rules explicitly
5. Verify no duplicate subject IDs

**Files to create:**
- `reports/capability-layer/capability-subjects.yaml`

**Validation:** `UNRESOLVED_PRODUCT_FORMAT_IDENTITIES = 0`, `DUPLICATE_CAPABILITY_SUBJECTS = 0`

#### TC-CAP-005: Coverage Universe Rebuild
**Status:** OPEN
**Objective:** Produce `reports/capability-layer/capability-coverage-universe.yaml` with one entry
per eligible subject. Required counter: `ELIGIBLE_SUBJECTS_WITHOUT_CAPABILITY_DISPOSITION = 0`.

**Steps:**
1. Derive the complete eligible universe from:
   - Active format registry (25 formats)
   - Source projects in `src/python/` and `src/net/`
   - SAL/spec obligations (`.local/spec-cache/sal-facts-latest.json`)
   - Package projects and tests
   - Explicit exclusions (ora, pam, xpm, zpaq — no products)
2. For each eligible subject:
   - Record inclusion_basis (source exists, SAL facts, gates passed, etc.)
   - Record expected_obligations from SAL (what capabilities should exist)
   - Record discovered_capabilities vs verified_capabilities vs missing_capabilities
   - Record status: COMPLETE, PARTIAL, MISSING, EXCLUDED, DEFERRED
3. Confirm: poc-targets.yaml (19 targets) vs format-registry.yaml (25 formats) discrepancy
   - 6 formats not in POC targets: likely ora, pam, xpm, zpaq (excluded) + 2 others
   - Document each exclusion with basis

**Files to create:**
- `reports/capability-layer/capability-coverage-universe.yaml`

**Validation:** `ELIGIBLE_SUBJECTS_WITHOUT_CAPABILITY_DISPOSITION = 0`

---

### BLOCK 3 — Core Fixes (TC-CAP-006 through TC-CAP-009)
*Mission sections 7-11 — SAL-driven compiler, gap reconciliation, taskcard linkage, queue*

#### TC-CAP-006: SAL/Obligation-Driven Capability Compiler
**Status:** OPEN
**Objective:** Create `tools/capability_layer/capability_compiler.py` — a new canonical compiler
that derives capabilities from SAL facts through obligations. Required counter:
`CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE = 0`.

**Steps:**
1. Read `.local/spec-cache/sal-facts-latest.json` (14,635 facts across 25 formats)
2. Group SAL facts by format_id, then by operation_kind using the existing keyword mapping
   (load, write, roundtrip, probe, etc.) from capability_map_generator.py — REUSE this logic
3. For each (format, operation_kind) group, derive a formal capability requirement:
   - capability_id: canonical (e.g., `fods:python:load:001`)
   - subject_id: from capability-subjects.yaml
   - obligation_ids: formal obligation IDs from `reports/all-format-deepening/all-format-obligation-register.yaml`
   - source_fact_ids: list of FACT-* IDs from SAL
   - expected_evidence: what must exist to mark VERIFIED
4. Query evidence for each capability:
   - implementation_evidence: scan `src/python/{format}/` for function names
   - test_evidence: count test files in `tests/python/{format}/`
   - oracle_evidence: check oracle status from `.local/spec-cache/{format}/oracle-status.json`
   - package_evidence: check `.venv/Lib/site-packages/{format}/`
5. Evaluate state based on evidence (use existing VERIFIED_STATES from validate_capability_map.py)
6. Produce `reports/capability-layer/sal-driven-capability-map.json` with full provenance chain
7. Update `capability_map_generator.py` to use this compiler as the authoritative step and
   relegate poc-targets.yaml to scope/priority metadata only (NOT state authority)

**Files to create:**
- `tools/capability_layer/capability_compiler.py`

**Files to modify:**
- `tools/capability_layer/capability_map_generator.py` — refactor `_build_foss_records()` and
  `_build_commercial_records()` to call capability_compiler.py as source of truth

**Validation:** `CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE = 0`

#### TC-CAP-007: Capability Proof Audit
**Status:** OPEN
**Objective:** Produce `reports/capability-layer/capability-proof-audit.yaml` verifying the
"2,087 verified / zero missing" claim. Required counters:
`FALSE_VERIFIED_CAPABILITIES = 0`, `MISSING_CAPABILITIES_HIDDEN_BY_SCOPE = 0`.

**Steps:**
1. Load the existing unified-capability-map.json; count total records by state
2. Sample 50+ records across formats/states to verify:
   - capability_id provenance traces to SAL fact (not just field name)
   - For `test_verified`: test_refs are non-empty AND test files actually exist on disk
   - For `implementation_verified`: implementation_refs point to real functions in source
   - For `example_verified`: example files exist
   - No grouped-format duplication (Netpbm: PBM+PGM+PPM should not triple-count)
3. Run validate_capability_map.py against current maps; capture exit code and findings
4. Detect:
   - capabilities marked verified based only on source file existence (no test refs)
   - capabilities duplicated across format aliases
   - unsupported capabilities from generic `_scan_python_functions` introspection
5. Produce audit YAML with findings per capability category
6. Record `FALSE_VERIFIED_CAPABILITIES` count honestly (expected: >0, possibly many)

**Files to create:**
- `reports/capability-layer/capability-proof-audit.yaml`

**Validation:** All false verified capabilities identified and reclassified in maps

#### TC-CAP-008: Gap Ledger Reconciliation
**Status:** OPEN
**Objective:** Split gap-ledger.json into active and historical; classify all 1,277 gaps;
fix open gaps without next actions. Required counters:
`ACTIVE_LEDGER_CLOSED_GAPS = 0`, `OPEN_GAPS_WITHOUT_EXACT_NEXT_ACTION = 0`.

**Steps:**
1. Load `reports/capability-layer/gap-ledger.json` (1,277 entries, 28 MB)
2. Classify each gap into one of the statuses from mission §9:
   - OPEN_ACTIONABLE, OPEN_BLOCKED, IN_PROGRESS, CLOSED_VERIFIED, CLOSED_SUPERSEDED,
     DUPLICATE, STALE, INVALID, HISTORICAL_ONLY, REOPEN_REQUIRED
3. Build `reports/capability-layer/gap-ledger-active.json`:
   - Only OPEN_ACTIONABLE, OPEN_BLOCKED, IN_PROGRESS, REOPEN_REQUIRED entries
   - Expected count: ~32 entries (the known open gaps)
   - Include: gap_id, stable_semantic_key, subject_id, capability_id, obligation_ids,
     current_state, expected_state, severity, status, blocker, taskcard_ids, exact_next_action
4. Build `reports/capability-layer/gap-ledger-archive.json`:
   - CLOSED_VERIFIED, CLOSED_SUPERSEDED, DUPLICATE, STALE, INVALID, HISTORICAL_ONLY
   - Preserve all historical fields for auditability
   - Include closure_evidence, closed_revision, supersedes, duplicate_of links
5. For each OPEN_ACTIONABLE gap without exact_next_action, add one based on gap_type:
   - missing_implementation → exact_next_action: "run /add-python-api for {format}"
   - missing_test_coverage → exact_next_action: "run /add-roundtrip-test for {format}"
   - stale_claim → exact_next_action: "re-verify evidence for capability {capability_id}"
6. Update consumers to use gap-ledger-active.json as primary (capability_feature_compiler.py,
   autonomous_cycle.py Step 4a, check_system_healing_gate.py)

**Files to create:**
- `reports/capability-layer/gap-ledger-active.json`
- `reports/capability-layer/gap-ledger-archive.json`

**Files to modify:**
- `tools/supervisor/capability_feature_compiler.py` — read gap-ledger-active.json (with fallback to full ledger)
- `tools/supervisor/autonomous_cycle.py` — update Step 4a path reference
- `tools/supervisor/check_system_healing_gate.py` — update gap ledger path

**Validation:** `ACTIVE_LEDGER_CLOSED_GAPS = 0`, `OPEN_GAPS_WITHOUT_EXACT_NEXT_ACTION = 0`

#### TC-CAP-009: Taskcard Linkage for Open Gaps
**Status:** OPEN
**Objective:** Generate bounded taskcards for all 30 open gaps that currently lack them.
Required counters: `READY_OPEN_GAPS_WITHOUT_TASKCARDS = 0`, `CLOSED_GAPS_WITH_ACTIVE_TASKCARDS = 0`.

**Steps:**
1. Load gap-ledger-active.json (output of TC-CAP-008)
2. For each OPEN_ACTIONABLE gap:
   - Determine eligibility: dependencies resolved? required skill exists? allowed paths known?
   - If eligible: generate a `capability_taskcard` YAML in `reports/capability-layer/taskcards/`
     using the schema from mission §10
   - If OPEN_BLOCKED: record blocker; no taskcard generated
3. Wire each generated taskcard back to its gap entry (update `taskcard_ids` field in
   gap-ledger-active.json)
4. Produce `reports/capability-layer/taskcard-linkage-report.yaml`:
   - Per gap: status, taskcard_id (if generated), blocker (if blocked), reason
5. Verify no CLOSED gap has an active taskcard:
   - Check gap-ledger-archive.json entries for any taskcard_ids that still appear in active queue
   - If found: invalidate those taskcards

**Files to create:**
- `reports/capability-layer/taskcards/<gap_id>.yaml` (one per actionable open gap, ~30 files)
- `reports/capability-layer/taskcard-linkage-report.yaml`

**Validation:** `READY_OPEN_GAPS_WITHOUT_TASKCARDS = 0`, `CLOSED_GAPS_WITH_ACTIVE_TASKCARDS = 0`

#### TC-CAP-010: Action Queue Regeneration with Hash Tracking
**Status:** OPEN
**Objective:** Regenerate action-queue.json from reconciled gap ledger with hash-based staleness
detection. Required counters: `ACTION_QUEUE_STALE_RELATIVE_TO_LEDGER = false`,
`QUEUE_ITEMS_WITHOUT_TASKCARDS = 0`, `CLOSED_GAPS_IN_ACTION_QUEUE = 0`.

**Steps:**
1. Compute SHA-256 of gap-ledger-active.json → `source_ledger_hash`
2. Compute SHA-256 of all taskcard files in `reports/capability-layer/taskcards/` → `source_taskcard_hash`
3. Build new action-queue.json from OPEN_ACTIONABLE gaps only:
   - Every item must include: taskcard_id, gap_id, capability_id, subject, priority,
     dependencies, required_skill, exact_command, validation, evidence_target
   - Set `advisory_only: false` for locally executable items (skill exists + paths known)
   - Set `advisory_only: true` for items requiring TRUE_EXTERNAL_GATE
4. Include staleness check in queue header:
   ```json
   {
     "schema_version": "2.0",
     "generated_at": "<iso>",
     "generator_version": "2.0",
     "source_ledger_hash": "<sha256>",
     "source_taskcard_hash": "<sha256>",
     "stale_detection_enabled": true
   }
   ```
5. Update `check_system_healing_gate.py` to verify hashes match before accepting queue
6. Exclude all CLOSED gaps from action queue; verify no closed gaps appear

**Files to modify:**
- `reports/capability-layer/action-queue.json` (regenerated)
- `tools/capability_layer/capability_map_generator.py` — update `_build_action_queue()` to add hash fields
- `tools/supervisor/check_system_healing_gate.py` — add hash validation

**Validation:** All three required counters at 0/false

---

### BLOCK 4 — Consumer Repairs (TC-CAP-011 through TC-CAP-012)
*Mission sections 12, 13, 14 — fix broken consumers, dashboard governance, historical cleanup*

#### TC-CAP-011: Repair Supervisor and Skill Consumers
**Status:** OPEN
**Objective:** Remove dead code, fix vestigial references, ensure canonical artifact routing.

**Steps:**

**Sub-task A — Deprecate gap_ledger_to_work_items.py (ORPHANED):**
- Add deprecation header comment explaining it is superseded by `capability_feature_compiler.py`
- Do NOT delete (preserve for audit history)
- Remove from any import chains or CLI references if any exist

**Sub-task B — Fix capability_queue_consumer.py (dead FOSS map load):**
- Remove the dead `_load_json(_FOSS_CAPABILITY_MAP)` call that loads but never uses the map
- Verify the gap-ledger reading logic works with gap-ledger-active.json

**Sub-task C — Fix select_poc_gaps.py (vestigial poc-targets reference):**
- The `DEFAULT_MATRIX` path to poc-targets.yaml is vestigial; actual logic uses `_GAP_WRITER_PROOF` dict
- Replace the hardcoded `_GAP_WRITER_PROOF` dict with a query against gap-ledger-active.json
  OR add a comment documenting the hardcoded dict as authoritative for dotnet writer proof,
  distinct from the gap ledger (which is for FOSS gaps)
- If the dotnet proof dict is intentional (not a gap-ledger concern), document it clearly

**Sub-task D — Update autonomous_cycle.py Step 4a:**
- Confirm it reads gap-ledger-active.json after TC-CAP-008 creates it
- Add fallback to full gap-ledger.json if active split does not exist

**Sub-task E — Verify add-python-api, add-dotnet-api, add-dogfood-export skills:**
- Confirm these skills update evidence, capability state, gap entry, and taskcard on completion
- If any skill does NOT close the loop, document the gap

**Files to modify:**
- `tools/supervisor/gap_ledger_to_work_items.py` — deprecation comment
- `tools/supervisor/capability_queue_consumer.py` — remove dead load
- `tools/supervisor/select_poc_gaps.py` — fix or document vestigial ref
- `tools/supervisor/autonomous_cycle.py` — update path reference if needed

#### TC-CAP-012: Dashboard Update Governance and Historical Cleanup
**Status:** OPEN
**Objective:** Clarify `/update-capability-matrix` permissions; implement active/historical separation
per mission §13-14. Required counter: `HISTORICAL_GAPS_POLLUTING_ACTIVE_SELECTION = 0`.

**Steps:**

**Sub-task A — Dashboard governance:**
- Read the `/update-capability-matrix` skill file (`.claude/commands/update-capability-matrix.md`)
- Add explicit governance section clarifying what it MAY and MUST NOT do (per mission §13)
- Ensure generated vs. maintained sections are labeled in poc-targets.yaml itself

**Sub-task B — Historical separation:**
- Confirm gap-ledger-active.json excludes historical entries (done in TC-CAP-008)
- Add a `closure_receipt_index.json` at `reports/capability-layer/closure-receipt-index.json`:
  - One entry per closed gap: gap_id, closed_at, closed_revision, closure_evidence_path
- Update `capability_feature_compiler.py` to only read gap-ledger-active.json (never full ledger)

**Files to modify:**
- `.claude/commands/update-capability-matrix.md` — governance section
- `tools/supervisor/capability_feature_compiler.py` — path update

**Files to create:**
- `reports/capability-layer/closure-receipt-index.json`

**Validation:** `HISTORICAL_GAPS_POLLUTING_ACTIVE_SELECTION = 0`

---

### BLOCK 5 — Validators and Pipeline (TC-CAP-013)
*Mission sections 15, 16 — transactional pipeline, missing validators*

#### TC-CAP-013: Validator Suite Extension + Transactional Pipeline
**Status:** OPEN
**Objective:** Add/repair validators for all requirements in mission §16; implement transactional
generation with atomic install and rollback.

**Steps:**

**Sub-task A — Extend validate_capability_map.py with new validators:**
Existing: VAL-001 through VAL-010 (schema, overclaim, ref existence, test refs, separation, pilots, taskcard linkage, advisory flag, evidence declaration)

Add:
- **VAL-011:** Every capability_id has obligation_ids[] non-empty (no provenance-free capabilities)
- **VAL-012:** No duplicate capability subjects (subject_id unique across maps)
- **VAL-013:** Action queue source_ledger_hash matches current gap-ledger-active.json SHA-256
- **VAL-014:** No closed gaps appear in gap-ledger-active.json
- **VAL-015:** Every OPEN_ACTIONABLE gap in active ledger has at least one taskcard_id
- **VAL-016:** Report generated_at vs. SAL facts mtime drift detection (warn if maps older than SAL)
- **VAL-017:** Grouped format counts: Netpbm aggregate ≠ sum(PBM+PGM+PPM) individual counts (expansion consistency)
- **VAL-018:** Generator non-idempotency detection: if run twice with same inputs, output SHA must match

**Sub-task B — Transactional pipeline:**
- Create `tools/capability_layer/capability_pipeline.py` implementing:
  ```
  LOAD → COMPILE → DISCOVER → EVALUATE → GENERATE → RECONCILE → TASKCARD → QUEUE → VALIDATE → PUBLISH
  ```
  With:
  - Write to temp directory first
  - Validate all cross-links (gap→capability, taskcard→gap, queue→taskcard)
  - If all validations pass → atomic move to reports/capability-layer/
  - If any validation fails → retain previous valid generation, log failure
  - Emit `reports/capability-layer/pipeline-run-manifest.json` with hashes and counts

**Files to modify:**
- `tools/capability_layer/validate_capability_map.py` — add VAL-011 through VAL-018

**Files to create:**
- `tools/capability_layer/capability_pipeline.py`
- `reports/capability-layer/pipeline-run-manifest.json` (generated by pipeline)

---

### BLOCK 6 — Pilots and Tests (TC-CAP-014 through TC-CAP-015)
*Mission sections 17, 18 — all 9 pilots + test suite*

#### TC-CAP-014: Run All 9 Required Pilots
**Status:** OPEN
**Objective:** Execute all pilots from mission §17, produce pilot evidence. Required counter:
`FAILED_REQUIRED_PILOTS = 0`.

**Pilot evidence directory:** `.local/evidences/capability-layer-healing-<run-id>/pilots/`

**Pilot 1 — Existing complete subject** (e.g., FODS Python):
- Load SAL facts → derive obligations → compile capability records → verify evidence → confirm no false gaps
- Run generator twice, confirm identical output

**Pilot 2 — Real missing capability** (select one of the 30 open gaps):
- Show gap creation → taskcard generation → queue inclusion → verify supervisor selection path
- Simulate implementation update (do NOT actually implement; document the trace)

**Pilot 3 — Grouped format expansion** (Netpbm: PBM/PGM/PPM):
- Verify: aggregate dashboard target (Netpbm) + distinct subjects (pbm, pgm, ppm)
- Confirm no duplicate capability counts in unified map
- Verify correct roll-up (sum ≠ triple-count)

**Pilot 4 — Cross-language product** (FODS: Python FOSS + .NET commercial):
- Shared SAL obligations → track-specific capabilities → separate evidence records
- Verify aggregate status rolls up correctly

**Pilot 5 — Historical closed gap** (any CLOSED_VERIFIED gap):
- Confirm it is in gap-ledger-archive.json, absent from gap-ledger-active.json
- Confirm no taskcard or queue item references it

**Pilot 6 — Stale queue detection**:
- Modify gap-ledger-active.json SHA (simulate content change)
- Verify VAL-013 fires: `ACTION_QUEUE_STALE_RELATIVE_TO_LEDGER = true`
- Regenerate queue → verify new hashes installed → VAL-013 passes

**Pilot 7 — False verified evidence** (fixture: source file exists, no test refs):
- Confirm capability_compiler.py produces state=IMPLEMENTED_UNVERIFIED (not VERIFIED)
- Confirm VAL-002 (overclaim detection) does NOT trigger (no overclaim was made)
- Confirm VAL-003 (verified needs refs) does NOT trigger (state is not verified)

**Pilot 8 — SAL obligation change** (modify a disposable obligation fixture):
- Confirm affected capability is invalidated (state → STALE_EVIDENCE)
- Confirm unaffected subjects remain stable
- This uses a test fixture, NOT production SAL data

**Pilot 9 — Idempotency**:
- Run capability_pipeline.py twice with same inputs
- Verify: zero content churn, zero duplicate gaps, zero duplicate taskcards, zero queue churn
- Record before/after SHA-256 for each output file

**Pilot evidence files:**
- `.local/evidences/capability-layer-healing-<run-id>/pilots/pilot-{1-9}-evidence.yaml`

**Validation:** `FAILED_REQUIRED_PILOTS = 0`, `MATERIAL_SECOND_RUN_CHANGES = 0`

#### TC-CAP-015: Test Suite
**Status:** OPEN
**Objective:** Add focused tests covering all areas from mission §18.
Test file location: `tests/capability_layer/`

**Tests to add:**

```
tests/capability_layer/
├── test_capability_compiler.py     (SAL→obligation→capability derivation)
├── test_capability_subjects.py     (identity, grouped targets, aliases, duplicates)
├── test_capability_proof.py        (evidence sufficiency, state evaluation)
├── test_gap_ledger.py              (open/closed/duplicate/superseded/historical)
├── test_taskcard_linkage.py        (ready gap→task, blocked gap, closed gap removes task)
├── test_action_queue.py            (hash staleness, closed-gap exclusion, priority)
├── test_capability_validators.py   (VAL-001 through VAL-018)
└── test_idempotency.py             (repeated generation, reconciliation, compilation, queue)
```

**Key test cases:**
- `test_capability_compiler.py`: SAL fact → obligation → capability record with obligation_ids
- `test_capability_subjects.py`: netpbm aggregate expands to pbm+pgm+ppm subjects
- `test_capability_proof.py`: source-file-only evidence → state IMPLEMENTED_UNVERIFIED (not VERIFIED)
- `test_gap_ledger.py`: closed gap absent from active ledger; historical gap preserved in archive
- `test_taskcard_linkage.py`: ready gap gets taskcard; blocked gap does NOT; closed gap has no taskcard
- `test_action_queue.py`: VAL-013 fires when ledger hash differs; closed gap absent from queue
- `test_idempotency.py`: run generator twice → identical SHA-256 on all output files

**Run with:** `.venv/Scripts/pytest tests/capability_layer/ -v`

---

### BLOCK 7 — Final Reports and Closeout (TC-CAP-016 through TC-CAP-017)

#### TC-CAP-016: Full Validation Run + Finding Registry
**Status:** OPEN
**Objective:** Run all validators, register all material findings in gap ledger, verify all required
counters are 0. Required counter: `MATERIAL_CAPABILITY_FINDINGS_WITHOUT_GAPS = 0`.

**Steps:**
1. Run `capability_pipeline.py` (full pipeline including validation)
2. Run `.venv/Scripts/pytest tests/capability_layer/ -v`
3. Run `validate_capability_map.py` against all generated maps
4. For every finding (AUTHORITY_AMBIGUITY, IDENTITY_MISMATCH, COVERAGE_UNIVERSE_GAP,
   PROSE_DERIVED_CAPABILITY, FALSE_VERIFIED_CAPABILITY, GAP_LEDGER_DEBT, etc.):
   - If P0/P1/P2 and locally actionable: ensure it has a gap entry in gap-ledger-active.json
   - If P3/advisory: document in capability-layer-healing-report.md
5. Verify all required §22 counters:
   - UNINVENTORIED_CAPABILITY_ARTIFACTS = 0
   - FALSE_CAPABILITY_CONSUMER_CLAIMS = 0
   - AMBIGUOUS_CAPABILITY_AUTHORITIES = 0
   - UNRESOLVED_PRODUCT_FORMAT_IDENTITIES = 0
   - ELIGIBLE_SUBJECTS_WITHOUT_CAPABILITY_DISPOSITION = 0
   - CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE = 0
   - FALSE_VERIFIED_CAPABILITIES = 0 (reclassified, not hidden)
   - MISSING_CAPABILITIES_HIDDEN_BY_SCOPE = 0
   - ACTIVE_LEDGER_CLOSED_GAPS = 0
   - READY_OPEN_GAPS_WITHOUT_TASKCARDS = 0
   - CLOSED_GAPS_WITH_ACTIVE_TASKCARDS = 0
   - CLOSED_GAPS_IN_ACTION_QUEUE = 0
   - ACTION_QUEUE_STALE_RELATIVE_TO_LEDGER = false
   - HISTORICAL_GAPS_POLLUTING_ACTIVE_SELECTION = 0
   - MATERIAL_CAPABILITY_FINDINGS_WITHOUT_GAPS = 0
   - FAILED_REQUIRED_PILOTS = 0
   - MATERIAL_SECOND_RUN_CHANGES = 0

#### TC-CAP-017: Terminal Closeout
**Status:** OPEN
**Objective:** Write all required output artifacts and close the plan.

**Required outputs to produce:**
1. `reports/capability-layer/capability-system-inventory.yaml` (TC-CAP-001)
2. `reports/capability-layer/capability-consumer-graph.yaml` (TC-CAP-002)
3. `reports/capability-layer/capability-authority-model.yaml` (TC-CAP-003)
4. `reports/capability-layer/capability-subjects.yaml` (TC-CAP-004)
5. `reports/capability-layer/capability-coverage-universe.yaml` (TC-CAP-005)
6. `reports/capability-layer/capability-proof-audit.yaml` (TC-CAP-007)
7. `reports/capability-layer/gap-ledger-active.json` (TC-CAP-008)
8. `reports/capability-layer/gap-ledger-archive.json` (TC-CAP-008)
9. `reports/capability-layer/taskcards/*.yaml` (TC-CAP-009, ~30 files)
10. `reports/capability-layer/taskcard-linkage-report.yaml` (TC-CAP-009)
11. `reports/capability-layer/action-queue.json` regenerated (TC-CAP-010)
12. `reports/capability-layer/closure-receipt-index.json` (TC-CAP-012)
13. `reports/capability-layer/pipeline-run-manifest.json` (TC-CAP-013)
14. `.local/evidences/capability-layer-healing-<run-id>/pilots/pilot-{1-9}-evidence.yaml` (TC-CAP-014)
15. `tests/capability_layer/test_*.py` (TC-CAP-015)
16. `reports/capability-layer/capability-layer-healing-report.md` (final)
17. `.local/evidences/capability-layer-healing-<run-id>/terminal-closeout.yaml`

**Closeout YAML:**
```yaml
plan_id: moonlit-squishing-sonnet
mission_id: capability-layer-healing
final_verdict: CAPABILITY_LAYER_REBUILT_RECONCILED_PROVEN_AND_IDEMPOTENT
completed_at: <iso>
required_counters_all_zero: true
taskcards_closed:
  - TC-CAP-001 through TC-CAP-017
```

**Write plan lock:**
```
python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/moonlit-squishing-sonnet.md --terminal
```

**Then STOP and report to user.**

---

## Taskcard Status Table

| TC-ID | Title | Status |
|-------|-------|--------|
| TC-CAP-001 | Generate capability-system-inventory.yaml | OPEN |
| TC-CAP-002 | Generate capability-consumer-graph.yaml | OPEN |
| TC-CAP-003 | Generate capability-authority-model.yaml | OPEN |
| TC-CAP-004 | Identity Normalization | OPEN |
| TC-CAP-005 | Coverage Universe Rebuild | OPEN |
| TC-CAP-006 | SAL/Obligation-Driven Capability Compiler | OPEN |
| TC-CAP-007 | Capability Proof Audit | OPEN |
| TC-CAP-008 | Gap Ledger Reconciliation | OPEN |
| TC-CAP-009 | Taskcard Linkage for Open Gaps | OPEN |
| TC-CAP-010 | Action Queue Regeneration with Hash Tracking | OPEN |
| TC-CAP-011 | Repair Supervisor and Skill Consumers | OPEN |
| TC-CAP-012 | Dashboard Update Governance and Historical Cleanup | OPEN |
| TC-CAP-013 | Validator Suite Extension + Transactional Pipeline | OPEN |
| TC-CAP-014 | Run All 9 Required Pilots | OPEN |
| TC-CAP-015 | Test Suite | OPEN |
| TC-CAP-016 | Full Validation Run + Finding Registry | OPEN |
| TC-CAP-017 | Terminal Closeout | OPEN |

---

## Verification

**End-to-end verification:**
1. `.venv/Scripts/pytest tests/capability_layer/ -v` → all green
2. `python tools/capability_layer/validate_capability_map.py reports/capability-layer/ --all` → exit 0
3. `python tools/capability_layer/capability_pipeline.py --validate-only` → all validators pass
4. Run pipeline twice → `python -c "import json,hashlib; ..."` SHA comparison → zero churn
5. All §22 required counters explicitly recorded as 0 in terminal-closeout.yaml

**Final verdict target:**
`CAPABILITY_LAYER_REBUILT_RECONCILED_PROVEN_AND_IDEMPOTENT`

---

## Post-Mission Pilot Rerun Hardening Addendum

**Hardening date:** 2026-07-01
**Trigger:** Pilot rerun and before/after comparison executed post-commit `438286c0`
**Status:** PLAN_FILE_HARDENED_READY_FOR_EXECUTION

---

### 1. Plan File Hardening Change Log

| Change | Type | Finding Source |
|--------|------|----------------|
| Added TC-HARDEN-001: refactor generator to use SAL compiler | New taskcard | GAP-HARDEN-002 |
| Added TC-HARDEN-002: add state field to unified map records | New taskcard | GAP-HARDEN-001 |
| Added TC-HARDEN-003: align active ledger status taxonomy | New taskcard | GAP-HARDEN-003 |
| Added TC-HARDEN-004: fix sal-driven map SHA churn | New taskcard | GAP-HARDEN-004 |
| Added TC-HARDEN-005: extend idempotency-check scope | New taskcard | GAP-HARDEN-004b |
| Added TC-HARDEN-006: normalize format_id casing | New taskcard | GAP-HARDEN-005 |
| Corrected wrong claim in pilot analysis | Contradiction | CONTRADICTED-001 |

---

### 2. Sources Reviewed

| Source | Path | Type |
|--------|------|------|
| Pilot rerun analysis | Conversation (post-commit 438286c0) | Assistant prose / live run |
| Unified capability map | `reports/capability-layer/unified-capability-map.json` | Repository artifact |
| SAL-driven capability map | `reports/capability-layer/sal-driven-capability-map.json` | Repository artifact |
| Active gap ledger | `reports/capability-layer/gap-ledger-active.json` | Repository artifact |
| capability_map_generator.py | `tools/capability_layer/capability_map_generator.py` | Source code |
| Terminal closeout | `.local/evidences/capability-layer-healing-001/terminal-closeout.yaml` | Evidence artifact |
| Test results | `pytest tests/capability_layer/ -q` live rerun | Direct test output |

---

### 3. Assistant Summary Claim Audit

```yaml
prose_claims:
  - claim_id: CLAIM-001
    exact_claim: "Unified capability map (2138 records) still has state: unknown for all records"
    source: "pilot rerun analysis — What Did Not Improve section"
    claim_type: implementation
    claimed_status: PARTIAL
    supporting_evidence: []
    contradictory_evidence:
      - "Direct verification: unified map records have NO state field at all (field absent, not=unknown)"
      - "python -c: State distribution = {'_MISSING_': 2138} using sentinel default"
    proof_level: 0
    required_proof_level: 3
    disposition: CONTRADICTED
    plan_action: >
      Correct: unified map records lack the state field entirely (null/absent), not set to 'unknown'.
      This is a more severe finding. Create TC-HARDEN-002.

  - claim_id: CLAIM-002
    exact_claim: "capability_map_generator.py _build_foss_records() NOT refactored to use SAL compiler"
    source: "pilot rerun — What Did Not Improve section"
    claim_type: implementation
    claimed_status: PARTIAL
    supporting_evidence:
      - "generator does not import capability_compiler: confirmed False"
      - "generator does not call compile_all(): confirmed False"
      - "generator still references poc-targets: confirmed True"
    proof_level: 3
    required_proof_level: 3
    disposition: VERIFIED_AND_PRESERVE
    plan_action: Create TC-HARDEN-001 (high priority)

  - claim_id: CLAIM-003
    exact_claim: "Active ledger statuses are DEFERRED/DEFERRED_BY_DESIGN, not OPEN_ACTIONABLE"
    source: "pilot rerun — direct data inspection"
    claim_type: implementation
    claimed_status: ACTIONABLE_GAP
    supporting_evidence:
      - "Active ledger statuses: {'DEFERRED_BY_DESIGN': 30, 'DEFERRED': 2}"
    proof_level: 3
    required_proof_level: 3
    disposition: VERIFIED_AND_PRESERVE
    plan_action: Create TC-HARDEN-003

  - claim_id: CLAIM-004
    exact_claim: "sal-driven-capability-map.json SHA non-deterministic due to generated_at"
    source: "pilot rerun — SHA comparison table"
    claim_type: idempotency
    claimed_status: ACTIONABLE_GAP
    supporting_evidence:
      - "pilot-9 SHA: 4c94625063daf4ffe098; post-rerun SHA: 1e4729d22d4a4356d207"
    proof_level: 3
    required_proof_level: 3
    disposition: VERIFIED_AND_PRESERVE
    plan_action: Create TC-HARDEN-004 + TC-HARDEN-005

  - claim_id: CLAIM-005
    exact_claim: "Format ID casing inconsistency: SAL lowercase vs unified uppercase"
    source: "pilot rerun — What Did Not Improve section"
    claim_type: integration
    claimed_status: PARTIAL
    supporting_evidence:
      - "SAL map: ['abw', 'csv', 'dif', ...]"
      - "Unified map: ['ABW', 'CSV', 'DIF', ...]"
    proof_level: 2
    required_proof_level: 3
    disposition: ACTIONABLE_GAP
    plan_action: Create TC-HARDEN-006

  - claim_id: CLAIM-006
    exact_claim: "SKILL-GAP-011 governance product_type pre-existing failure"
    source: "pilot rerun + terminal-closeout.yaml notes"
    claim_type: verification
    claimed_status: PREEXISTING_DOCUMENTED
    supporting_evidence:
      - "SKILL-GAP-011 status=closed in full ledger, not in active ledger"
      - "terminal-closeout.yaml: failed_preexisting: 1"
      - "test reads from gap_selector which has different filtering logic than active ledger"
    proof_level: 3
    required_proof_level: 3
    disposition: OUT_OF_SCOPE_VALID
    plan_action: No action needed for moonlit scope; document for gap_selector owner

  - claim_id: CLAIM-007
    exact_claim: "1303/2138 unified map records lack obligation provenance"
    source: "pilot rerun — direct data"
    claim_type: coverage
    claimed_status: ACTIONABLE_GAP
    supporting_evidence:
      - "Direct count: sum(1 for r in recs if not r.get('obligation_ids') and not r.get('spec_refs')) = 1303"
    proof_level: 3
    required_proof_level: 4
    disposition: ACTIONABLE_GAP
    plan_action: Governed by TC-HARDEN-001 (refactoring generator)

  - claim_id: CLAIM-008
    exact_claim: "TC-CAP-006 CLOSED — CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE = 0"
    source: "terminal-closeout.yaml"
    claim_type: closure
    claimed_status: CLAIMED_UNPROVEN
    supporting_evidence:
      - "SAL-driven map: CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE = 0 (169 records)"
    contradictory_evidence:
      - "Unified map: 1303/2138 records lack any obligation/spec provenance"
      - "Generator NOT refactored — TC-CAP-006 objective only partially met"
    proof_level: 2
    required_proof_level: 4
    disposition: IMPLEMENTED_NOT_VERIFIED
    plan_action: >
      TC-CAP-006 closure is PARTIAL. Counter = 0 applies only to the SAL-driven map's 169 records.
      The unified map (primary consumer-facing artifact) is NOT covered.
      TC-HARDEN-001 is the follow-up to complete TC-CAP-006's stated objective.
```

---

### 4. Contradictions Reconciled

| ID | Claim | Reality | Resolution |
|----|-------|---------|------------|
| CONTRADICTED-001 | "Unified map 2138 records all have state=unknown" (pilot prose) | Unified map records have NO state field at all (field entirely absent, not set to 'unknown') | Corrected in this addendum. TC-HARDEN-002 governs. |
| CONTRADICTED-002 | "TC-CAP-006 CLOSED" (terminal-closeout.yaml, all counters=0) | Generator NOT refactored; unified map has no state field; 1303 records lack provenance | TC-CAP-006 partially complete. Counter=0 applies to SAL-driven map only (169 records). TC-HARDEN-001 is the completion path. |

---

### 5. Gap Register

| Gap ID | Severity | Finding | Status |
|--------|----------|---------|--------|
| GAP-HARDEN-001 | HIGH | Unified capability map 2138 records have no `state` field | → TC-HARDEN-002 |
| GAP-HARDEN-002 | HIGH | `capability_map_generator.py` not refactored — still poc-targets primary; no SAL compiler integration | → TC-HARDEN-001 |
| GAP-HARDEN-003 | MEDIUM | Active ledger statuses use non-standard taxonomy (DEFERRED_BY_DESIGN/DEFERRED vs OPEN_ACTIONABLE) | → TC-HARDEN-003 |
| GAP-HARDEN-004 | MEDIUM | `sal-driven-capability-map.json` SHA changes on every re-run due to `generated_at` | → TC-HARDEN-004 |
| GAP-HARDEN-004b | MEDIUM | Pipeline `--idempotency-check` excludes sal-driven map from scope | → TC-HARDEN-005 |
| GAP-HARDEN-005 | LOW | Format ID casing mismatch: SAL lowercase, unified uppercase | → TC-HARDEN-006 |
| GAP-HARDEN-006 | PREEXISTING | SKILL-GAP-011 governance product_type test failure — gap_selector reads closed gaps | Documented only; out of moonlit scope |

---

### 6. Taskcard Register (Hardening Follow-ups)

---

#### TC-HARDEN-001: Refactor `_build_foss_records()` to use SAL compiler as source of truth

```yaml
taskcard:
  task_id: TC-HARDEN-001
  mission_id: capability-layer-healing
  parent_task_id: TC-CAP-006
  title: "Refactor capability_map_generator._build_foss_records() to call compile_all() as source"
  source_finding: GAP-HARDEN-002 / CLAIM-002 / CONTRADICTED-002
  priority: HIGH
  lane: L03-capability
  owner: capability_layer
  status: not_attempted
  objective: >
    Make capability_map_generator.py call capability_compiler.compile_all() as the PRIMARY
    step in _build_foss_records() and _build_commercial_records(). Output of compile_all()
    drives state and provenance fields in the unified map. poc-targets.yaml is relegated to
    scope/priority metadata only (NOT state authority). This completes TC-CAP-006's stated
    objective which was only partially met.
  why_it_matters: >
    Without this refactor, the SAL-driven compiler (169 records) and the unified map
    (2138 records) run as independent parallel artifacts. The unified map — which is the
    artifact consumed by check_system_healing_gate, autonomous_cycle, and dashboards —
    has no state field and 1303 records lacking obligation provenance. The authority
    inversion (poc-targets as primary) remains in place for the consumer-facing artifact.
  allowed_paths:
    - tools/capability_layer/capability_map_generator.py
    - tools/capability_layer/capability_compiler.py
  forbidden_paths:
    - src/
    - reports/ (outputs must be regenerated, not hand-edited)
  dependencies:
    - TC-CAP-006 (compiler must exist and be stable — DONE)
    - TC-HARDEN-003 (status taxonomy must be aligned before map is regenerated)
  expected_outputs:
    - capability_map_generator.py imports and calls capability_compiler.compile_all()
    - _build_foss_records() uses compile_all() output as source of truth for state/provenance
    - unified-capability-map.json regenerated with state field present for all records
    - obligation_ids populated for all 169 SAL-derived records in unified map
    - CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE = 0 for unified map (not just SAL-driven map)
  acceptance_checks:
    - "python -c: unified map records have non-null state field"
    - "python -c: unified map has 0 records without state"
    - "python -c: CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE in unified map = 0"
    - "python tools/capability_layer/capability_pipeline.py --validate-only → 0 errors"
    - ".venv/Scripts/pytest tests/capability_layer/ -q → 188 pass (no regression)"
  verification:
    - source: grep/read capability_map_generator.py for compile_all import and call
    - focused: pytest tests/capability_layer/test_capability_compiler.py
    - integration: pytest tests/capability_layer/ -q
    - e2e: python tools/capability_layer/capability_pipeline.py --idempotency-check
  negative_controls:
    - "poc-targets.yaml must NOT appear as primary source for state decisions in generator"
    - "unified map must not regress existing 2138 records to fewer records"
  regressions:
    - "VAL-001–010 errors must remain 0"
    - "Existing test suite 188 passing must be preserved"
  evidence:
    - unified_map_state_field_present: confirmed
    - CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE_unified: 0
    - idempotency_check: PASS
  rollback_or_recovery: >
    If refactor breaks generator, revert _build_foss_records() changes only.
    compile_all() and SAL-driven map remain unaffected.
  failure_reroute: >
    If generator refactor is too risky, create a wrapper that post-processes unified map
    to inject state and obligation_ids from the SAL-driven map records by format_id match.
  closeout_rules:
    - unified map regenerated and state field non-null for all records
    - CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE = 0 in unified map
    - no test regressions
    - VAL errors = 0
  exact_next_action: >
    Read tools/capability_layer/capability_map_generator.py lines around _build_foss_records().
    Add `from capability_compiler import compile_all` import.
    Call compile_all() at start of _build_foss_records(), merge state/obligation_ids into records.
    Regenerate unified map. Verify state field present. Run tests.
  proof_level_current: 0
  proof_level_target: 4
```

---

#### TC-HARDEN-002: Add `state` field to unified map records

```yaml
taskcard:
  task_id: TC-HARDEN-002
  mission_id: capability-layer-healing
  parent_task_id: TC-HARDEN-001
  title: "Ensure unified capability map records have non-null state field"
  source_finding: GAP-HARDEN-001 / CLAIM-001 (CONTRADICTED)
  priority: HIGH
  lane: L03-capability
  owner: capability_layer
  status: not_attempted
  objective: >
    After TC-HARDEN-001 refactors the generator to use the SAL compiler, verify that
    ALL records in unified-capability-map.json have a non-null, non-absent `state` field.
    Current state: 2138/2138 records have NO state field (field entirely absent).
  why_it_matters: >
    check_system_healing_gate, autonomous_cycle, and dashboards all consume the unified map.
    If the state field is absent, consumers cannot determine capability verification status.
    This makes the primary consumer-facing artifact effectively stateless.
  dependencies:
    - TC-HARDEN-001 (generator refactor must produce state field)
  acceptance_checks:
    - "python -c: sum(1 for r in recs if r.get('state') is None) == 0"
    - "state values must be within: {implementation_verified, test_verified, example_verified, not_verified, unknown}"
  verification:
    - direct: python -c inspection of unified map state distribution
    - focused: pytest tests/capability_layer/test_capability_validators.py
  closeout_rules:
    - state field present and non-null for all 2138 records
    - no test regression
  exact_next_action: "Verify after TC-HARDEN-001 execution: python -c state distribution check"
  proof_level_current: 0
  proof_level_target: 3
```

---

#### TC-HARDEN-003: Align active ledger status taxonomy with TC-CAP-008 specification

```yaml
taskcard:
  task_id: TC-HARDEN-003
  mission_id: capability-layer-healing
  parent_task_id: TC-CAP-008
  title: "Align active ledger gap statuses to OPEN_ACTIONABLE/OPEN_BLOCKED taxonomy"
  source_finding: GAP-HARDEN-003 / CLAIM-003
  priority: MEDIUM
  lane: L03-capability
  owner: capability_layer
  status: not_attempted
  objective: >
    TC-CAP-008 specified status taxonomy: OPEN_ACTIONABLE, OPEN_BLOCKED, IN_PROGRESS,
    REOPEN_REQUIRED. Current active ledger uses DEFERRED_BY_DESIGN (30) and DEFERRED (2).
    Consumers expecting OPEN_ACTIONABLE receive 0 results. Align statuses or update
    all consumers to recognize the actual taxonomy.
  why_it_matters: >
    The action queue contains 32 entries. The active ledger has 32 gaps with statuses
    DEFERRED_BY_DESIGN/DEFERRED. If a consumer queries for OPEN_ACTIONABLE gaps, it gets
    0 results, breaking the autonomous selection pipeline.
  options:
    - A: Reclassify DEFERRED_BY_DESIGN → OPEN_BLOCKED (with blocker field set)
         and DEFERRED → OPEN_BLOCKED (with deferred_reason field set).
    - B: Update consumers (capability_feature_compiler.py, check_system_healing_gate.py,
         autonomous_cycle.py) to recognize DEFERRED_BY_DESIGN as an actionable-blocked status.
    - C: Document DEFERRED_BY_DESIGN as canonical status; update TC-CAP-008 spec to match reality.
  recommended_option: A (reclassify — simpler, preserves spec)
  acceptance_checks:
    - "active ledger has 0 gaps with status DEFERRED_BY_DESIGN or DEFERRED"
    - "active ledger has all gaps with status in {OPEN_ACTIONABLE, OPEN_BLOCKED, IN_PROGRESS, REOPEN_REQUIRED}"
    - "action queue source_ledger_hash still matches active ledger (regenerate if needed)"
  rollback_or_recovery: >
    If reclassification causes consumer failures, use Option B (consumer update) as fallback.
  exact_next_action: >
    Read gap-ledger-active.json gaps, change DEFERRED_BY_DESIGN → OPEN_BLOCKED,
    add blocker: "DEFERRED_BY_DESIGN — see original ledger for rationale".
    Change DEFERRED → OPEN_BLOCKED. Recompute and update action-queue source_ledger_hash.
  proof_level_current: 0
  proof_level_target: 3
```

---

#### TC-HARDEN-004: Fix `sal-driven-capability-map.json` SHA non-determinism

```yaml
taskcard:
  task_id: TC-HARDEN-004
  mission_id: capability-layer-healing
  parent_task_id: TC-CAP-006
  title: "Make sal-driven-capability-map.json byte-stable across re-runs"
  source_finding: GAP-HARDEN-004 / CLAIM-004
  priority: MEDIUM
  lane: L03-capability
  owner: capability_layer
  status: not_attempted
  objective: >
    Every invocation of compile_all() writes a new `generated_at` ISO timestamp into
    sal-driven-capability-map.json, making the SHA change on each run.
    Pilot-9 evidence SHA (4c94625063daf4ffe098) was immediately invalidated on the
    first rerun (1e4729d22d4a4356d207). Either:
    A: Exclude generated_at from hash computation (normalize before SHA), OR
    B: Pin generated_at only when source inputs change (content-hash-gated writes).
  options:
    - A: Strip generated_at before computing SHA (used internally by idempotency check)
    - B: Only write file when content (excluding generated_at) would change — normalized write
  recommended_option: B (normalized write — prevents unnecessary churn in git diff too)
  acceptance_checks:
    - "Two sequential compile_all() calls produce identical SHA (excluding generated_at)"
    - "python -c: sha256(strip_generated_at(content_run1)) == sha256(strip_generated_at(content_run2))"
    - "git diff shows no change to sal-driven-capability-map.json when inputs unchanged"
  exact_next_action: >
    In capability_compiler.py compile_all(): before writing JSON, compute content hash
    of the new content (with generated_at zeroed out). If matches existing file's content
    hash, skip write (preserve existing file with its original generated_at). Otherwise write.
  proof_level_current: 0
  proof_level_target: 3
```

---

#### TC-HARDEN-005: Extend pipeline `--idempotency-check` to include sal-driven map

```yaml
taskcard:
  task_id: TC-HARDEN-005
  mission_id: capability-layer-healing
  parent_task_id: TC-CAP-013
  title: "Include sal-driven-capability-map.json in pipeline idempotency-check scope"
  source_finding: GAP-HARDEN-004b
  priority: MEDIUM
  lane: L03-capability
  owner: capability_layer
  status: not_attempted
  objective: >
    capability_pipeline.py --idempotency-check verifies SHA stability for unified,
    commercial, and FOSS maps only. sal-driven-capability-map.json is excluded, hiding
    the SHA churn introduced by generated_at. Add it to the scope, using content-normalized
    comparison (strip generated_at before comparing).
  dependencies:
    - TC-HARDEN-004 (fix churn first, then extend scope)
  acceptance_checks:
    - "--idempotency-check output includes sal-driven-capability-map.json in comparison"
    - "PASS result after TC-HARDEN-004 fix is applied"
  exact_next_action: >
    In capability_pipeline.py _idempotency_check(): add sal-driven-capability-map.json
    to the list of files to compare, using content-normalized SHA (strip generated_at).
  proof_level_current: 0
  proof_level_target: 3
```

---

#### TC-HARDEN-006: Normalize format_id casing across SAL-driven and unified maps

```yaml
taskcard:
  task_id: TC-HARDEN-006
  mission_id: capability-layer-healing
  parent_task_id: TC-CAP-004
  title: "Normalize format_id casing: SAL-driven (lowercase) vs unified map (uppercase)"
  source_finding: GAP-HARDEN-005 / CLAIM-005
  priority: LOW
  lane: L03-capability
  owner: capability_layer
  status: not_attempted
  objective: >
    SAL-driven map uses lowercase format_ids ('fods', 'abw') while unified map uses
    uppercase ('FODS', 'ABW'). Any consumer that tries to join or cross-reference these
    maps by format_id will get 0 matches. Add a normalization step or pick one canonical
    casing and enforce it everywhere.
  recommended_approach: >
    Use UPPERCASE as canonical (matches format-registry.yaml and unified map).
    In capability_compiler.py, convert format_id to uppercase before writing records:
    `format_id = format_id.upper()`.
  acceptance_checks:
    - "SAL-driven map format_ids are uppercase: ['FODS', 'ABW', ...]"
    - "Cross-reference unified map FODS records match SAL-driven map FODS records"
  exact_next_action: >
    In capability_compiler.py _compile_format(): set format_id = fmt.upper() when
    writing the capability record. Regenerate sal-driven-capability-map.json. Verify.
  proof_level_current: 0
  proof_level_target: 2
```

---

### 7. Verification Matrix (Follow-up Taskcards)

| Taskcard | Proof Required | Primary Test | Integration Check |
|----------|---------------|--------------|-------------------|
| TC-HARDEN-001 | E2E (level 4) | pytest tests/capability_layer/ | pipeline --validate-only |
| TC-HARDEN-002 | Integration (level 3) | python -c state distribution | pytest capability validators |
| TC-HARDEN-003 | Integration (level 3) | python -c status distribution | action-queue hash check |
| TC-HARDEN-004 | Idempotency (level 3) | two-run SHA comparison | git diff shows no churn |
| TC-HARDEN-005 | Integration (level 3) | pipeline --idempotency-check output | — |
| TC-HARDEN-006 | Focused (level 2) | python -c format_id check | cross-ref unified vs SAL |

---

### 8. Gate Contract (Hardening Taskcards)

**Entry condition:** TC-HARDEN-003 completes before TC-HARDEN-001 (status taxonomy must be stable before generator refactor)

**Dependency order:**
```
TC-HARDEN-003 (status taxonomy)
  → TC-HARDEN-001 (generator refactor)
    → TC-HARDEN-002 (verify state field present)
TC-HARDEN-004 (SHA churn fix)
  → TC-HARDEN-005 (extend idempotency scope)
TC-HARDEN-006 (casing — independent)
```

**Gate fail behavior:** If TC-HARDEN-001 breaks existing 188 tests, revert generator changes and use failure_reroute (post-process wrapper).

---

### 9. Anti-Overclaim Rules (Hardening Context)

- CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE = 0 applies to SAL-driven map (169 records) ONLY. The unified map (2138 records) is NOT covered by this counter until TC-HARDEN-001 is complete.
- TC-CAP-006 is PARTIALLY COMPLETE. The SAL compiler exists and runs but does not drive the unified map. Closure of TC-CAP-006 required both: (a) new compiler ✓, and (b) generator refactored ✗.
- "state: unknown" claim in pilot analysis prose was FACTUALLY WRONG. Correct: state field is entirely ABSENT from unified map records (not set to unknown). TC-HARDEN-002 governs.
- Idempotency PASS from `--idempotency-check` covers 3 artifacts (unified, commercial, FOSS maps). It does NOT cover sal-driven map (non-deterministic) or gap-ledger-active (checked only via hash comparison outside the check). MATERIAL_SECOND_RUN_CHANGES = 0 claim must be scoped to these 3 artifacts only.

---

### 10. Plan Hardening Validation

```yaml
plan_hardening_validation:
  plan_path: "plans/.claude/moonlit-squishing-sonnet.md (+ C:/Users/prora/.claude/plans/moonlit-squishing-sonnet.md)"
  claims_reviewed: 8
  explicit_findings: 5
  implied_findings: 2
  contradictions: 2
  taskcards_added: 6
  taskcards_updated: 0
  findings_without_taskcards: 0
  gates_updated: 1
  evidence_rules_updated: 6
  blockers: []
  remaining_true_blockers: []
  verdict: PLAN_FILE_HARDENED_READY_FOR_EXECUTION
```

---

### 11. Exact Next Actions (Priority Order)

1. **TC-HARDEN-003** (MEDIUM, no deps) — reclassify active ledger statuses to OPEN_ACTIONABLE/OPEN_BLOCKED. ~30 min.
2. **TC-HARDEN-004** (MEDIUM, no deps) — fix generate_at SHA churn in compile_all(). ~20 min.
3. **TC-HARDEN-006** (LOW, no deps) — normalize format_id to uppercase in compiler. ~10 min.
4. **TC-HARDEN-001** (HIGH, after 003) — refactor _build_foss_records() to call compile_all(). ~2 hours.
5. **TC-HARDEN-002** (HIGH, after 001) — verify state field present in unified map. ~10 min.
6. **TC-HARDEN-005** (MEDIUM, after 004) — extend idempotency-check scope. ~20 min.
