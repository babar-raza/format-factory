# goofy-orbiting-scroll — Portfolio Control: 41-Plan Reconciliation and Execution Handoff

## Context

41 external plan files reside in `C:\Users\prora\.claude\plans\` and have not been migrated to
the repository. They represent a backlog of machinery-hardening, governance-healing, investigative,
and product-deepening work accumulated across multiple chat sessions. None are registered in the
repository's governed plan infrastructure (`plans/.claude/`), and no portfolio control system
exists to track them collectively.

This plan builds the repository-resident portfolio control system, ingests all 41 sources in
bounded batches, maps provenance, discovers conflicts and dependencies, and produces a governed
execution handoff. No product implementation is authorized in this session.

**Operating Mode:** RECONCILE_ONLY
**Authorization required for execution:** Explicit user instruction ("RECONCILE_AND_EXECUTE")

---

## Repository State (captured at plan creation)

- Branch: `main` | HEAD: `c7d9f154`
- Active plan lock: `vast-weaving-lampson` — status `TERMINAL_CLOSED` (safe to proceed)
- Continuation signal: `autonomous_continue=true`, iteration=0, no rework items
- Existing in-repo plans: 74 files in `plans/.claude/`
- Existing portfolio root: NONE (`.portfolio/` does not exist)
- Dirty files: multiple supervisor reports and capability-layer reports (modified, not staged)

---

## Portfolio Storage Contract

Root: `.portfolio/goofy-orbiting-scroll/`

```
.portfolio/goofy-orbiting-scroll/
  portfolio-manifest.json          # identity, counters, status
  governance-binding.json          # repo governance files read and hashes
  source-inventory.json            # all 41 resolved plan paths + hashes
  plan-registry.json               # one record per plan
  requirement-registry.json        # canonical requirements
  task-registry.json               # canonical tasks
  provenance-map.json              # source → canonical bidirectional map
  lane-registry.json               # execution lanes from repo architecture
  relationship-records.json        # overlaps, conflicts, dependencies
  dependency-graph.json            # validated DAG
  wave-registry.json               # execution waves
  execution-handoff.json           # machine-readable handoff
  reconciliation-report.json       # final reconciliation report
  checklists/                      # one file per plan
    <plan-name>-checklist.json
  journal/
    execution-journal.jsonl        # append-only event log
  snapshots/
    snapshot-<id>.json             # verified state snapshots
```

---

## Known Pre-Flight Findings

### Confirmed Conflicts (require resolution in TC-GOS-011)

| ID | Plans | Classification | Evidence |
|----|-------|---------------|----------|
| CONFLICT-001 | iterative-mixing-shannon (FF-PGH-001) + memoized-frolicking-donut (GOV-HEAL-001) | SEMANTIC_DUPLICATE | Both titled "Product Governance Healing"; overlapping validator scope (V150-V163 vs V150-V155); different taskcard counts (19 vs 23) |
| CONFLICT-002 | precious-wandering-lighthouse + serialized-petting-crab | REVISION_CANDIDATE | Identical taskcard IDs TC-VPR-001–008; both address dual-lane DOM gap generator; different mission IDs (CERT-FORENSICS-20260710 vs DUAL-LANE-VERIFICATION-001) |
| CONFLICT-003 | vast-wibbling-moon (29 TCs, S01-S15) + bubbly-dancing-pony (11 TCs) | PARTIAL_OVERLAP | Both target pipeline reconciliation: next-work-items.json vs next-sprint.md divergence |
| CONFLICT-004 | Multiple plans (twinkly-nibbling-platypus, vast-wibbling-moon, mutable-exploring-hellman, shiny-percolating-sky) | SHARED_REQUIREMENT | All address validator expected_count discrepancy (165 vs 167); must resolve once |

### Plans with IN_PROGRESS Status (require priority assignment)

- `shiny-percolating-sky.md` — Oracle System Assessment (IN_PROGRESS)
- `glimmering-hopping-kazoo.md` — Agentic System Completion FF-AGENTS-PARITY-001 (IN_PROGRESS)
- `imperative-coalescing-bengio.md` — Espanso Integration (IN_PROGRESS)

### Known Prerequisites (dependency order)

- `stateful-booping-mountain` (plan_importer.py) → must precede clean ingestion of any other plan
- `velvet-swinging-wreath` (lifecycle healing) → prerequisite for machinery iteration to function
- Spec-to-feature correction plan Lanes 1-6, 14, 15 → must precede `cheeky-crafting-manatee`

---

## Taskcards

### TC-GOS-001 | Governance Binding + Portfolio Initialization | OPEN

**Objective:** Read all applicable repository governance and create the portfolio root structure with
an immutable portfolio identity.

**Steps:**
1. Read: `AGENTS.md`, `plans/master-plan.md`, `plans/strategic/spec-to-feature-radical-correction-plan.md` (§1-5 summary)
2. Read: `docs/automation/supervisor-worker-contract.md`, `registry/repository-layout.yaml`
3. Read: `tools/supervisor/write_plan_lock.py`, `tools/supervisor/check_continuation.py` (signatures only)
4. Create `.portfolio/goofy-orbiting-scroll/` directory structure (all subdirs listed above)
5. Write `governance-binding.json`:
   - `governance_files`: paths + SHA-256 of each file read
   - `canonical_plan_location`: `plans/.claude/`
   - `plan_schema`: path if exists
   - `state_store`: `.local/supervisor/`
   - `execution_controller`: `tools/supervisor/autonomous_cycle.py`
6. Derive portfolio identity from: SHA-256 of sorted normalized plan paths + repo identity
7. Write `portfolio-manifest.json` (schema_version, portfolio_id, created_at, status=INITIALIZING)
8. Append journal event: `PORTFOLIO_INITIALIZED`
9. Write snapshot-001.json

**Acceptance:** `.portfolio/goofy-orbiting-scroll/` exists; manifest has stable portfolio_id; governance-binding.json has file hashes for all 6 governance files read.

---

### TC-GOS-002 | Plan Source Inventory | OPEN

**Objective:** Resolve, read, hash, and record all 41 supplied plan paths. Must achieve
UNRESOLVED_PLAN_PATHS=0 and UNREAD_PLAN_FILES=0.

**Steps:**
1. For each of the 41 supplied paths:
   - Normalize the path (handle spacing anomalies in `humble-hatching-lark`, `atomic-chasing-meteor`, `splendid-roaming-beaver`)
   - Confirm readability
   - Calculate SHA-256 content hash
   - Extract declared title, revision, plan IDs
   - Detect exact content duplicates (compare hashes)
   - Assign stable `source_id` (s001–s041)
2. Write `source-inventory.json` with all 41 records
3. Verify counters: SUPPLIED=41, RESOLVED≥39, READABLE≥39, HASHED≥39
4. For any FAILED paths: record in `ingestion_errors`
5. Append journal event: `SOURCE_INVENTORY_COMPLETE`
6. Update portfolio-manifest.json (source_plan_count, source_set_hash)

**Note:** Paths with formatting anomalies to handle:
- `C:\Users\prora.claude\plans\humble-hatching-lark.md` (missing backslash)
- `C:\Users\prora.claude\plans\atomic-chasing-meteor.md` (missing backslash)
- `C:\Users\prora.claude\plans\splendid-roaming-beaver.md` (missing backslash)
- `C:\Users\prora\.claude\plans\fuzzy-conjuring-lobster` (no .md extension)

**Acceptance:** source-inventory.json has 41 entries; FAILED count documented; EXACT_DUPLICATE_PLAN_FILES recorded.

---

### TC-GOS-003 | Plan Ingestion — Batch A (plans 1–10) | OPEN

**Plans:** shiny-percolating-sky, glimmering-hopping-kazoo, polymorphic-foraging-feather,
iterative-mixing-shannon, memoized-frolicking-donut, bubbly-dancing-pony, mutable-exploring-hellman,
elegant-napping-minsky, stateful-booping-mountain, splendid-prancing-wind

**Steps:**
1. Claim batch (write `batches/batch-A.json`, status=IN_PROGRESS)
2. For each plan: extract objectives, requirements, taskcards (IDs + status), completion conditions,
   dependencies, stated_revision
3. Write `plan-registry/<source_id>.json` for each plan (schema: plan_record)
4. Write temporary batch output; validate against plan_record schema
5. Atomically commit: move temp → final; append `BATCH_A_COMMITTED` journal event
6. Update snapshot
7. Release batch claim (status=COMPLETE)

**Acceptance:** 10 plan records written; journal event appended; no parser errors.

---

### TC-GOS-004 | Plan Ingestion — Batch B (plans 11–20) | OPEN

**Plans:** splendid-squishing-orbit, twinkly-nibbling-platypus, vast-wibbling-moon,
clever-tickling-island, warm-enchanting-grove, glowing-swinging-grove, vast-splashing-allen,
kind-crunching-coral, humble-hatching-lark, atomic-chasing-meteor

**Steps:** Same protocol as TC-GOS-003. Batch ID: B.

**Acceptance:** 10 plan records written; journal event `BATCH_B_COMMITTED` appended.

---

### TC-GOS-005 | Plan Ingestion — Batch C (plans 21–30) | OPEN

**Plans:** spicy-sparking-gosling, playful-discovering-thunder, precious-wandering-lighthouse,
serialized-petting-crab, glittery-splashing-manatee, imperative-coalescing-bengio,
silly-popping-tower, peppy-crafting-lark, fizzy-imagining-hinton, shimmering-rolling-meerkat

**Steps:** Same protocol as TC-GOS-003. Batch ID: C.

**Acceptance:** 10 plan records written; journal event `BATCH_C_COMMITTED` appended.

---

### TC-GOS-006 | Plan Ingestion — Batch D (plans 31–41) | OPEN

**Plans:** modular-noodling-galaxy, imperative-floating-book, optimized-meandering-giraffe,
splendid-roaming-beaver, wild-napping-cherny, cheeky-crafting-manatee, velvet-swinging-wreath,
golden-foraging-boot, effervescent-sprouting-marshmallow, fuzzy-conjuring-lobster,
lively-leaping-elephant

**Steps:** Same protocol as TC-GOS-003. Batch ID: D. Note 11 plans (last batch is larger).

**Acceptance:** 11 plan records written; journal event `BATCH_D_COMMITTED` appended.

---

### TC-GOS-007 | Verify Complete Ingestion | OPEN

**Depends on:** TC-GOS-003, TC-GOS-004, TC-GOS-005, TC-GOS-006

**Steps:**
1. Count plan records in plan-registry/: must equal READABLE_PLAN_FILES from source-inventory
2. Cross-check every source_id in source-inventory has a corresponding plan record
3. Identify exact duplicate content (same SHA-256): record in source-inventory as `duplicate_content_of`
4. Identify same-title different-content (CONFLICT-001: iterative-mixing-shannon vs memoized-frolicking-donut)
5. Identify revision candidates (CONFLICT-002: precious-wandering-lighthouse vs serialized-petting-crab)
6. Write ingestion verification results to `portfolio-manifest.json`
7. Append journal event: `INGESTION_VERIFIED`

**Acceptance:** PARTIALLY_INGESTED_PLAN_FILES=0; all duplicates and revision candidates identified;
manifest updated with counts.

---

### TC-GOS-008 | Repository Reconnaissance | OPEN

**Depends on:** TC-GOS-001

**Steps:**
1. Capture: HEAD, branch, dirty-state file list, untracked files
2. Identify relevant components: tools/supervisor/, src/python/, src/net/, tests/, registry/,
   .governance/, reports/, plans/.claude/
3. Run baseline read-only validation (do NOT run write operations):
   - Check `python tools/supervisor/check_continuation.py` (read output only)
   - List all files in `.local/supervisor/` state directory
   - Check `reports/supervisor/next-sprint.md` first 20 lines
4. For each plan's stated requirements: classify current repository state:
   - VERIFIED_COMPLETE: implementation exists AND tests pass
   - IMPLEMENTED_UNVERIFIED: code exists, no test evidence
   - PARTIAL: work begun, acceptance criteria not met
   - NOT_STARTED: no code exists
   - STALE: plan assumption contradicted by HEAD
5. Write `repository-baseline.json`
6. Append journal event: `REPOSITORY_RECONNOITRED`

**Critical files to check for each plan type:**
- machinery_hardening plans → check `tools/supervisor/` for referenced modules
- governance plans → check `tools/supervisor/governance_validators*.py` (validator count)
- oracle plans → check `tools/supervisor/execute_oracle.py` and `oracle/`
- capability plans → check `.governance/capabilities/registry.yaml`

**Acceptance:** repository-baseline.json written; all 41 plans have at least one classified
source item; no modification to any file outside `.portfolio/`.

---

### TC-GOS-009 | Normalize Requirements → Canonical Registries | OPEN

**Depends on:** TC-GOS-007, TC-GOS-008

**Steps:**
1. Extract all stated requirements from all 41 plan records
2. Group by semantic equivalence (preserve all source statements):
   - Same validator count fix → one canonical requirement REQ-VALCOUNT-001
   - Pipeline reconciliation (NWI vs next-sprint) → one canonical requirement REQ-PIPE-001
   - Plan import/lock machinery → one canonical requirement REQ-PLAN-IMPORT-001
   - etc.
3. For each canonical requirement: write record to `requirement-registry.json`
4. Extract all taskcards from all 41 plans; normalize to canonical tasks:
   - Identical IDs in different plans → check for content equivalence
   - TC-VPR-001..008 appear in both precious-wandering-lighthouse AND serialized-petting-crab → one canonical task set
5. Write `task-registry.json`
6. Update plan records with `canonical_requirement_ids` and `canonical_task_ids`
7. Append journal event: `REGISTRIES_BUILT`

**Expected canonical task count:** Estimate 150-300 (41 plans × avg 5-10 unique canonical tasks
after deduplication)

**Acceptance:** requirement-registry.json and task-registry.json written; no source item has
blank disposition; CONFLICT-001 through CONFLICT-004 have explicit canonical resolutions.

---

### TC-GOS-010 | Provenance Mapping | OPEN

**Depends on:** TC-GOS-009

**Steps:**
1. For every source requirement in all 41 plans: write `source_requirement_mapping` entry
2. For every source taskcard in all 41 plans: write `source_task_mapping` entry
3. Assign disposition to every item (EXECUTE_CANONICAL_TASK, CONSOLIDATED_WITH_EQUIVALENT_TASK,
   SUPERSEDED_WITH_PROOF, etc.)
4. Write `provenance-map.json` with bidirectional indexes:
   - source_requirement → canonical_requirement, canonical_task
   - source_task → canonical_task
   - canonical_task → all source items + all affected plans
5. Verify: no source item has blank or implicit disposition
6. Append journal event: `PROVENANCE_MAPPED`

**Acceptance:** provenance-map.json written; every source item has an explicit disposition;
bidirectional indexes validated (canonical tasks reference back to all their source items).

---

### TC-GOS-011 | Lane Discovery + Conflict Classification | OPEN

**Depends on:** TC-GOS-009

**Steps:**
1. Discover execution lanes from actual repo architecture:
   - L01: tools/supervisor/ (supervisor machinery)
   - L02: src/python/ (FOSS Python product source)
   - L03: src/net/ (.NET product source)
   - L04: tests/ (test suite)
   - L05: .governance/ (governance schemas and capability registry)
   - L06: registry/ (format registry, source baseline)
   - L07: oracle/ (oracle layer)
   - L08: reports/ (supervisor outputs)
   - L09: plans/.claude/ (plan migration)
   - L10: tools/capability_sync/ and tools/supervisor/control_index/ (tooling)
2. Assign each canonical task to exactly one primary lane
3. For each pair of canonical tasks sharing file/state resources: write `relationship_record`
4. Classify all 4 pre-identified conflicts:
   - CONFLICT-001 → SEMANTIC_DUPLICATE (pick the stronger acceptance criteria: memoized-frolicking-donut v3 with 23 TCs)
   - CONFLICT-002 → REVISION_CANDIDATE (serialized-petting-crab supersedes precious-wandering-lighthouse — newer mission ID)
   - CONFLICT-003 → PARTIAL_OVERLAP (vast-wibbling-moon subsumes bubbly-dancing-pony scope)
   - CONFLICT-004 → SHARED_REQUIREMENT → one canonical task TC-VALCOUNT-FIX
5. Write `lane-registry.json` and `relationship-records.json`
6. Append journal event: `LANES_AND_CONFLICTS_CLASSIFIED`

**Acceptance:** All canonical tasks have primary_lane assigned; all 4 known conflicts have explicit
classification and resolution; relationship-records.json has no UNKNOWN classification entries.

---

### TC-GOS-012 | Build Dependency Graph | OPEN

**Depends on:** TC-GOS-011

**Steps:**
1. Create `dependency-graph.json` with edges for all known dependencies:
   - `stateful-booping-mountain` (plan_importer.py) → PREDECESSOR to all plans requiring clean import
   - `velvet-swinging-wreath` (lifecycle healing) → PREDECESSOR to machinery plans requiring iteration
   - Validator count fix (TC-VALCOUNT-FIX) → PREDECESSOR to any governance plan claiming 165 validators
   - `splendid-squishing-orbit` FODS governance → PARALLEL_SAFE with oracle/SAL lane work
2. Validate graph:
   - No cycles (topological sort must succeed)
   - No missing shared-resource serialization (tools/supervisor/ mutations are serialized)
   - No task enters READY before prerequisites are satisfied
3. Identify tasks safe for parallel execution (PARALLEL_SAFE classification)
4. Record cycles if found; propose resolution
5. Append journal event: `DEPENDENCY_GRAPH_BUILT`

**Acceptance:** dependency-graph.json written; topological sort succeeds or cycles are explicitly
documented with resolution; every cross-lane dependency has an integration_owner assigned.

---

### TC-GOS-013 | Individual Plan Checklists | OPEN

**Depends on:** TC-GOS-010, TC-GOS-011

**Steps:**
1. For each of the 41 plans: write `checklists/<plan-name>-checklist.json`
2. Each checklist must include:
   - All source requirements → disposition + canonical_requirement_ids
   - All source taskcards → disposition + canonical_task_ids
   - Current status (from repository-baseline.json)
   - Completion conditions from plan
   - Blockers (from known conflicts and dependencies)
3. Use checklist item state: NOT_MAPPED → MAPPED (all items should reach MAPPED in RECONCILE_ONLY)
4. Verify: every source item is mapped (no NOT_MAPPED remaining)
5. Append journal event: `CHECKLISTS_CREATED`

**Acceptance:** 41 checklist files exist; every source item in every plan has a disposition;
no NOT_MAPPED items remain.

---

### TC-GOS-014 | Execution Wave Registry | OPEN

**Depends on:** TC-GOS-012

**Steps:**
1. Build waves from dependency graph topological order:
   - **Wave 0 — Foundation Repairs (serial):**
     - stateful-booping-mountain: plan_importer.py (L01 — supervisor machinery)
     - velvet-swinging-wreath: lifecycle healing (L01)
     - TC-VALCOUNT-FIX: validator count reconciliation (L01)
   - **Wave 1 — Active/IN_PROGRESS Plans (priority):**
     - shiny-percolating-sky: oracle assessment (L07)
     - glimmering-hopping-kazoo: agentic parity (L01)
     - imperative-coalescing-bengio: espanso integration (L05)
   - **Wave 2 — Governance/Audit (can run after Wave 0):**
     - memoized-frolicking-donut: governance healing (L01, L05)
     - mutable-exploring-hellman: code quality audit (L01)
     - iterative-mixing-shannon: SUPERSEDED_BY memoized-frolicking-donut
     - glittery-splashing-manatee: certification layer (L01)
   - **Wave 3 — Product/Oracle/Deepening (L02, L03, L07):**
     - modular-noodling-galaxy: oracle hardening Phase II
     - serialized-petting-crab: dual-lane DOM gap (supersedes precious-wandering-lighthouse)
     - peppy-crafting-lark: product deepening
     - splendid-prancing-wind: product library healing
   - **Wave 4 — Remaining Machinery (L01 serialized):**
     - All remaining machinery_hardening plans
   - **Wave 5 — Forensic/Archaeology:**
     - cheeky-crafting-manatee, fuzzy-conjuring-lobster, fizzy-imagining-hinton, effervescent-sprouting-marshmallow
2. Assign concurrency classification to each task (SERIAL or PARALLEL_SAFE)
3. Write `wave-registry.json`
4. Append journal event: `WAVES_BUILT`

**Acceptance:** wave-registry.json written; all canonical tasks assigned to a wave; Wave 0 contains
all prerequisite/foundation repairs; no task appears in multiple waves.

---

### TC-GOS-015 | Execution Handoff + Independent Review | OPEN

**Depends on:** TC-GOS-013, TC-GOS-014

**Steps:**
1. Write `execution-handoff.json`:
   - portfolio_id, source_set_hash, repository_revision
   - wave_registry reference
   - ready_tasks: all Wave 0 tasks (prerequisites met, no blockers)
   - blocked_tasks: tasks with TRUE_EXTERNAL_GATEs
   - task_packets_path: `.portfolio/goofy-orbiting-scroll/task_packets/` (for future execution)
   - operating_mode: RECONCILE_ONLY
   - authorization_required_for_execution: explicit user "RECONCILE_AND_EXECUTE" instruction
2. Write `reconciliation-report.json`:
   - SUPPLIED_PLAN_PATHS: 41
   - RESOLVED_PLAN_PATHS: (actual count)
   - UNRESOLVED_PLAN_PATHS: (must be 0 or documented)
   - total_canonical_requirements: (count)
   - total_canonical_tasks: (count)
   - conflicts_identified: 4 (CONFLICT-001 through CONFLICT-004)
   - conflicts_resolved: 4 (with resolutions)
   - in_progress_plans: 3 (shiny-percolating-sky, glimmering-hopping-kazoo, imperative-coalescing-bengio)
   - external_blockers: list any TRUE_EXTERNAL_GATEs found
3. Independent review pass: re-read provenance-map.json and verify every plan has at least one
   mapped canonical task; re-read conflict resolutions and verify they are evidence-backed
4. Write `reviews/handoff-review.json` with verdict (ACCEPT or REWORK_REQUIRED)
5. Write human-readable `execution-handoff.md` summary (in `.portfolio/goofy-orbiting-scroll/`)
6. Append journal event: `HANDOFF_CREATED`
7. Update portfolio-manifest.json status=HANDOFF_READY
8. Final snapshot: write snapshot-final.json

**Acceptance:** execution-handoff.json written; reconciliation-report.json shows
UNRESOLVED_PLAN_PATHS=0; independent review verdict=ACCEPT; portfolio-manifest.json status=HANDOFF_READY.

---

## Critical Files to Read Before Execution

- [AGENTS.md](AGENTS.md) — human-free autonomy rules, SCM agent policy
- [plans/master-plan.md](plans/master-plan.md) — project strategic direction
- [plans/strategic/spec-to-feature-radical-correction-plan.md](plans/strategic/spec-to-feature-radical-correction-plan.md) — lane ordering authority
- [docs/automation/supervisor-worker-contract.md](docs/automation/supervisor-worker-contract.md) — evidence schema
- [registry/repository-layout.yaml](registry/repository-layout.yaml) — canonical path layout
- [tools/supervisor/write_plan_lock.py](tools/supervisor/write_plan_lock.py) — plan lock protocol

## Key Reusable Tools

- `tools/supervisor/write_plan_lock.py` — lock management (use after migration per CLAUDE.md Step 0)
- `tools/supervisor/check_continuation.py` — continuation signal
- `tools/supervisor/autonomous_cycle.py` — sprint execution (for future EXECUTE mode)
- `tools/supervisor/atomic_io.py` — atomic file writes for portfolio state

## Verification

After all 15 taskcards are closed, the following must hold:

1. `.portfolio/goofy-orbiting-scroll/portfolio-manifest.json` status=HANDOFF_READY
2. `source-inventory.json` has 41 entries; FAILED count is 0 or documented
3. `plan-registry/` has one file per readable plan
4. `requirement-registry.json` and `task-registry.json` are non-empty
5. `provenance-map.json` covers every source item from every plan
6. `checklists/` has 41 files; no NOT_MAPPED items
7. `wave-registry.json` assigns every canonical task to a wave
8. `execution-handoff.json` lists all Wave 0 ready tasks
9. `reviews/handoff-review.json` verdict=ACCEPT
10. `journal/execution-journal.jsonl` has 15+ events in chronological order
11. Second read of portfolio-manifest.json must be idempotent (no drift from external mutation)

To verify idempotency: re-read source-inventory.json and recompute source_set_hash; must match
portfolio-manifest.json `source_set_hash`.

---

## Plan Type: machinery_hardening (portfolio control)
## plan_type: machinery_hardening
## expected_taskcard_count: 15

---

## Taskcard Status Summary

| Taskcard | Status |
|---|---|
| TC-GOS-001 | CLOSED |
| TC-GOS-002 | CLOSED |
| TC-GOS-003 | CLOSED |
| TC-GOS-004 | CLOSED |
| TC-GOS-005 | CLOSED |
| TC-GOS-006 | CLOSED |
| TC-GOS-007 | CLOSED |
| TC-GOS-008 | CLOSED |
| TC-GOS-009 | CLOSED |
| TC-GOS-010 | CLOSED |
| TC-GOS-011 | CLOSED |
| TC-GOS-012 | CLOSED |
| TC-GOS-013 | CLOSED |
| TC-GOS-014 | CLOSED |
| TC-GOS-015 | CLOSED |


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-13T07:33:43.142334+00:00"
  locked_by: "8322424df7b7"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
