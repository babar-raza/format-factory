# Queue-Backed Autonomy Gap Verification
## TC-C1, TC-C2 | Plan Hardening Sprint 2026-06-09

---

## TC-C1: Queue/Executor/Packager Integration State

### Component Inventory

#### 1. Action Queue (tools/supervisor/action_queue.py)
- **Queue file:** `.local/supervisor/action-queue.jsonl` (JSONL format)
- **Current state:** 25 items total, 5 PENDING
- **Key functions:** make_queue_item(), _load_queue(), _save_queue(), validate_item_schema_v2()
- **Forbidden actions enforced:** GIT_PUSH, GIT_COMMIT, GIT_RESET, GATE_8_APPROVAL, GATE_11_APPROVAL, PACKAGE_PUBLISH
- **Schema:** queue-item-v2.schema.json (action_id, action_type, stream, priority, status, allowed_paths, forbidden_paths, evidence_required)
- **Assessment:** IMPLEMENTED and operational

#### 2. ProductSourceExecutor (tools/supervisor/product_source_executor.py)
- **Purpose:** Safe IMPLEMENT_SMALL_PRODUCT_FEATURE execution with path enforcement + rollback
- **Key class:** ProductSourceExecutor(repo_root)
- **Path enforcement:** Hard-forbidden: src/net/, registry/, poc-targets.yaml, .supervisor/, AGENTS.md
- **Diff budget:** Max 200 lines of added code
- **Rollback:** git checkout on test failure
- **Ledger:** Records execution to lane-execution-ledger.json
- **Assessment:** IMPLEMENTED with safety constraints

#### 3. Autonomous Task Generator (tools/supervisor/autonomous_task_generator.py)
- **Purpose:** Generate queue-item-v2 tasks from expansion goals + gap ledger + source introspection
- **Expansion goals:** 100+ predefined functions across ABW, Gnumeric, TSV, NDJSON, FODG
- **Output:** product-task-candidates.json (scored tasks)
- **Assessment:** IMPLEMENTED, generates candidates

#### 4. Product Feature Factory (tools/supervisor/product_feature_factory.py)
- **Purpose:** 6 repeatable code generation patterns
- **Patterns:** Getter, ExportCsv, Roundtrip, Append, Probe, PackageProof
- **Constraint:** Does NOT execute pytest; does NOT modify test files
- **Assessment:** IMPLEMENTED, generates source code templates

#### 5. Bounded Repair Engine (tools/supervisor/bounded_repair_engine.py)
- **Purpose:** Classify test failures and apply deterministic bounded repairs
- **Classifications:** IMPORT_ERROR, SYNTAX_ERROR, ATTRIBUTE_ERROR, ASSERTION_ERROR, NAME_ERROR, TYPE_ERROR, TIMEOUT
- **Safety:** Max 3 repair attempts; SYNTAX_ERROR always rollback; ASSERTION_ERROR never modifies test
- **Assessment:** IMPLEMENTED with safety bounds

#### 6. Evidence Auto-Packager (tools/supervisor/evidence_auto_packager.py)
- **Purpose:** Auto-generate ~80% of evidence-declaration.yaml
- **Auto fields:** run_id, git_head, test_results, changed_files, git_status
- **Manual fields:** worker_self_verdict, declared_scope, work_items, evidence_artifacts
- **Assessment:** IMPLEMENTED, partial automation

### Integration Gaps

| Gap | Severity | Description |
|---|---|---|
| Lane ledger minimal | MEDIUM | Only 1 entry in lane-execution-ledger.json (proof-of-concept only). Most sprints did not write ledger entries. |
| No end-to-end integration test | HIGH | Components work individually but full queue→executor→test→ledger→packager→supervisor cycle never validated as one flow |
| Feature factory + executor not wired | MEDIUM | product_feature_factory generates code but executor does not automatically consume factory output |
| Repair engine + executor loosely coupled | LOW | bounded_repair_engine classifies failures but executor uses it ad-hoc, not systematically |
| Task generator → queue dispatch untested | MEDIUM | autonomous_task_generator outputs candidates but dispatch to action_queue not proven in production |

### Pending Queue Items (5)
```
anl-q-001: ABW function (PRODUCT_SOURCE_PATCH_BOUNDED)
anl-q-002: Gnumeric function (PRODUCT_SOURCE_PATCH_BOUNDED)
anl-q-003: TSV function (PRODUCT_SOURCE_PATCH_BOUNDED)
anl-q-004: NDJSON function (PRODUCT_SOURCE_PATCH_BOUNDED)
anl-q-005: FODG function (PRODUCT_SOURCE_PATCH_BOUNDED)
```
All with forbidden_actions: [GIT_COMMIT, GIT_PUSH, GATE_APPROVAL]

---

## TC-C2: Safe PRODUCT_SOURCE_PATCH_BOUNDED Pilot Design

### Selected Queue Item
**anl-q-001** (ABW format) — selected because:
- ABW has no_public_spec_available (simplest authority basis)
- ABW has extensive test coverage (33 test files, 500+ tests)
- ABW has write capability (write_abw(), create_abw())
- ABW codec is well-understood from 12 acceleration sprints

### Pilot Specification

```yaml
pilot_id: AUTONOMY-PILOT-001
queue_item_id: anl-q-001
action_type: PRODUCT_SOURCE_PATCH_BOUNDED
format: abw
target_function: TBD (select smallest unimplemented function from task generator)

allowed_paths:
  - src/python/abw/abw_codec.py
  - src/python/abw/__init__.py
  - tests/python/abw/

forbidden_paths:
  - registry/*
  - AGENTS.md
  - .supervisor/*
  - src/net/*
  - src/python/*/  (other formats)

diff_budget: 50 lines (source + test combined)

spec_fact_basis: no_public_spec_available (ABW has no accessible spec document)

rollback_plan: git checkout -- src/python/abw/abw_codec.py src/python/abw/__init__.py

test_commands:
  - python -m pytest tests/python/abw/ -x --tb=short

evidence_requirements:
  - Lane ledger entry with: lane_id, files_changed, tests_run, test_count
  - Evidence declaration YAML with auto-generated fields
  - Raw test log captured

loop_segments_to_verify:
  1. Queue item exists and validates against queue-item-v2.schema.json
  2. Executor reads queue item and enforces allowed_paths
  3. Feature factory generates function body (or executor writes directly)
  4. Source file modified within diff budget
  5. __init__.py updated to export new function
  6. Tests run and pass
  7. Lane ledger entry written
  8. Evidence auto-packager derives declaration
  9. Supervisor autonomous-cycle can grade the work
  10. Continuation state classified correctly

stop_conditions:
  - Test failure after patch → rollback immediately
  - Path violation → abort
  - Diff budget exceeded → abort
  - Any modification to forbidden paths → abort

independent_verification:
  - TC-I3 (currently BLOCKED — would verify if pilot executes)
```

### Pilot Execution Status
**BLOCKED** — This sprint is investigation/planning only. Pilot execution requires:
1. TC-C2 design approved (this document)
2. Explicit sprint authorization for source changes
3. Workspace safety check (no conflicting IN_PROGRESS taskcards)
4. Queue item validated against schema

### Exact Unblock Criteria for TC-C3
1. TC-C2 reaches CLOSED state
2. A future sprint explicitly authorizes PRODUCT_SOURCE_PATCH_BOUNDED execution
3. Selected function is confirmed unimplemented (no false positive from existing code)
4. Test file for new function is prepared before source patch
5. Rollback command verified to restore clean state
