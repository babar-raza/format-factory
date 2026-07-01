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

| TC-ID | CLOSED |
|-------|--------|
| TC-CAP-001 | CLOSED |
| TC-CAP-002 | CLOSED |
| TC-CAP-003 | CLOSED |
| TC-CAP-004 | CLOSED |
| TC-CAP-005 | CLOSED |
| TC-CAP-006 | CLOSED |
| TC-CAP-007 | CLOSED |
| TC-CAP-008 | CLOSED |
| TC-CAP-009 | CLOSED |
| TC-CAP-010 | CLOSED |
| TC-CAP-011 | CLOSED |
| TC-CAP-012 | CLOSED |
| TC-CAP-013 | CLOSED |
| TC-CAP-014 | CLOSED |
| TC-CAP-015 | CLOSED |
| TC-CAP-016 | CLOSED |
| TC-CAP-017 | CLOSED |

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


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-01T12:20:22.028728+00:00"
  locked_by: "34c4217ef0bd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
