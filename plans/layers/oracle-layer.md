# Oracle Layer

```yaml
layer_metadata:
  layer_id: L05
  canonical_name: Oracle Layer
  canonical_slug: oracle-layer
  permanent_plan_path: plans/layers/oracle-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 4
  maturity_target: 4
  current_stage: GOVERNED_OPERATION
  current_owner: null
  agent_type: null
  session_id: "923e237958c1"
  active_sprint: "lp-bootstrap"
  active_taskcards: []
  ready_taskcards: [TC-ORC-004]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: [L04, L06]
  upstream_layers: [L04, L06]
  downstream_layers: [L07, L08]
  skill_ids: [run-oracle]
  command_ids: [run-oracle]
  evidence_paths:
    - oracle/registry/format-oracle-registry.yaml
    - oracle/formats/fods/reports/oracle-run-summary.json
  last_started_at: null
  last_progress_at: "2026-06-26"
  last_updated_at: "2026-06-26"
  last_verified_at: "2026-06-26"
  last_verified_revision: "a7744cf6"
  next_task_id: TC-ORC-004
  next_action: "Add oracle cases for ora/pam/xpm/zpaq once products exist; refactor execute_oracle.py (at LOC cap)"
  handoff_id: null
```

---

## 1. Layer Metadata

See YAML block above.

## 2. Authority and Purpose

The Oracle Layer provides **conformance verification** for all Format Factory format
packages. It owns:

- The oracle package definition per format (`oracle/formats/{format}/oracle-package.yaml`)
- The oracle registry (`oracle/registry/format-oracle-registry.yaml`)
- The oracle executor (`tools/oracle/execute_oracle.py`, 1428 LOC, at cap)
- The oracle test runner (`/run-oracle` skill)
- Oracle lifecycle management: OBLIGATION_CREATED → SCAFFOLDED → AUTHORITY_MAPPED → CASES_DEFINED → VERIFIED → PRODUCTION_ACTIVE

**Current status:** ALL 20 Python FOSS formats at VERIFIED (73/73 PASS) as of 2026-06-26.

## 3. Scope

- `oracle/formats/{format}/` — per-format oracle packages (20 active)
- `oracle/registry/format-oracle-registry.yaml` — oracle registry
- `tools/oracle/execute_oracle.py` — oracle executor
- `oracle/formats/{format}/reports/oracle-run-summary.json` — per-format run reports

## 4. Explicit Non-Scope

- Does NOT own format product source (L06)
- Does NOT own test infrastructure (L07) — oracle is distinct from unit/integration tests
- Does NOT own sample corpus (L04) — though oracle uses samples

## 5. Owned Decisions

- Oracle lifecycle state machine
- Which formats are OBLIGATION_CREATED vs. VERIFIED
- Oracle case definitions (valid, invalid, edge cases)
- execute_oracle.py architecture (at LOC cap — refactor pending)

## 6. Upstream Inputs

- L04 (Corpus): sample files for oracle test cases
- L06 (Product): format packages to verify (import and call)
- `oracle/formats/{format}/oracle-package.yaml` — case definitions

## 7. Downstream Consumers

- L07 (Test Infrastructure): oracle VERIFIED status proves format API correctness
- L08 (Evidence): V82 oracle obligations validator checks oracle status
- L12 (Validation): V82 blocks release for formats not at OBLIGATION_CREATED+

## 8. Ideal Production Design

The ideal oracle:

1. **oracle-package.yaml** per format defines: format_id, oracle_version, authority_spec,
   samples, valid_cases, invalid_cases, edge_cases
2. **execute_oracle.py** runs all cases for a format, returns PASS/FAIL per case
3. **Lifecycle:** OBLIGATION_CREATED → SCAFFOLDED → AUTHORITY_MAPPED → CASES_DEFINED → VERIFIED
4. **V82 validator:** blocks RELEASE_GATE for formats not at OBLIGATION_CREATED or higher
5. **LOC cap:** execute_oracle.py at 1428/1428 cap — needs refactor (split into per-format executors)
6. **/run-oracle skill:** runs oracle for one or all formats, writes oracle-run-summary.json

## 9. Verified Current Implementation

```yaml
current_layer_implementation:
  implementation_paths:
    - tools/oracle/execute_oracle.py  # 1428 LOC, at LOC cap
    - oracle/formats/fods/oracle-package.yaml
    - oracle/formats/fodt/oracle-package.yaml
    - oracle/formats/ods/oracle-package.yaml
    - oracle/formats/odt/oracle-package.yaml
    - oracle/formats/fodg/oracle-package.yaml
    - oracle/formats/fodp/oracle-package.yaml
    - oracle/formats/xcf/oracle-package.yaml
    - oracle/formats/zst/oracle-package.yaml
    - oracle/formats/ndjson/oracle-package.yaml
    - oracle/formats/toml/oracle-package.yaml
    - oracle/formats/csv/oracle-package.yaml
    - oracle/formats/tsv/oracle-package.yaml
    - oracle/formats/abw/oracle-package.yaml
    - oracle/formats/dif/oracle-package.yaml
    - oracle/formats/gnumeric/oracle-package.yaml
    - oracle/formats/sylk/oracle-package.yaml
    - oracle/formats/qoi/oracle-package.yaml
    - oracle/formats/pbm/oracle-package.yaml
    - oracle/formats/pgm/oracle-package.yaml
    - oracle/formats/ppm/oracle-package.yaml
  registry_paths:
    - oracle/registry/format-oracle-registry.yaml
  active_components:
    - execute_oracle.py with 20 format executors
    - /run-oracle skill (TC-LA-010)
    - V82 oracle obligations validator (TC-ORC-003)
  missing_components:
    - oracle cases for ora/pam/xpm/zpaq (no products yet)
  stale_components:
    - execute_oracle.py at LOC cap (1428/1428) — next executor MUST be separate
  verified_formats:
    fods: {cases: 8, pass: 8, status: VERIFIED}
    fodt: {cases: 3, pass: 3, status: VERIFIED}
    ods: {cases: 3, pass: 3, status: VERIFIED}
    odt: {cases: 3, pass: 3, status: VERIFIED}
    fodg: {cases: 3, pass: 3, status: VERIFIED}
    fodp: {cases: 3, pass: 3, status: VERIFIED}
    xcf: {cases: 3, pass: 3, status: VERIFIED}
    zst: {cases: 6, pass: 6, status: VERIFIED}  # requires .venv/Scripts/python
    ndjson: {cases: 4, pass: 4, status: VERIFIED}
    toml: {cases: 4, pass: 4, status: VERIFIED}
    csv: {cases: 5, pass: 5, status: VERIFIED}
    tsv: {cases: 4, pass: 4, status: VERIFIED}
    abw: {cases: 3, pass: 3, status: VERIFIED}
    dif: {cases: 3, pass: 3, status: VERIFIED}
    gnumeric: {cases: 3, pass: 3, status: VERIFIED}
    sylk: {cases: 3, pass: 3, status: VERIFIED}
    qoi: {cases: 3, pass: 3, status: VERIFIED}
    pbm: {cases: 3, pass: 3, status: VERIFIED}
    pgm: {cases: 3, pass: 3, status: VERIFIED}
    ppm: {cases: 3, pass: 3, status: VERIFIED}
```

## 10. Current Execution Stage

**GOVERNED_OPERATION** — All 20 active Python FOSS formats at VERIFIED. 73/73 PASS.

## 11. Current Maturity Assessment

**LEVEL 4 — GOVERNED**

Justification:
- 20 formats VERIFIED
- 73/73 test cases PASS
- /run-oracle skill registered
- V82 validator active
- oracle-run-summary.json per format

Ceiling: execute_oracle.py at LOC cap (cannot add format executors without refactor).

## 12. Target Maturity

**LEVEL 4 — GOVERNED** (maintained at this level until ora/pam/xpm/zpaq products exist)

Future upgrade to L5 requires: PRODUCTION_ACTIVE status for all commercial formats.

## 13. Current Strengths

- 100% VERIFIED for active Python FOSS formats
- Clear lifecycle state machine
- V82 validator enforces oracle obligations
- Known ZST quirk documented: requires `.venv/Scripts/python` (not system Python)

## 14. Gap Register

| Gap ID | Severity | Current State | Target State | Root Cause | Taskcards |
|--------|----------|---------------|--------------|------------|-----------|
| ORC-GAP-001 | LOW | execute_oracle.py at LOC cap | Refactored into per-format modules | Progressive growth | TC-ORC-004 |
| ORC-GAP-002 | LOW | 4 formats OBLIGATION_CREATED (no products) | VERIFIED | No product source for ora/pam/xpm/zpaq | Waiting |

## 15. Root-Cause Register

- **ORC-GAP-001:** execute_oracle.py grew incrementally as formats were added. At 1428 LOC/cap, the next format executor must go into a new file.

## 16. Repair Architecture

**TC-ORC-004:**
1. Refactor execute_oracle.py: extract per-format executor functions into `tools/oracle/executors/{format}_executor.py`
2. Main execute_oracle.py becomes a dispatcher (≤200 LOC)
3. When ora/pam/xpm/zpaq products exist: add oracle cases using pattern from existing formats

## 17. Schemas and Contracts

```yaml
oracle_package_schema:
  format_id: string
  oracle_version: string
  authority_spec: string
  status: OBLIGATION_CREATED | SCAFFOLDED | AUTHORITY_MAPPED | CASES_DEFINED | VERIFIED | PRODUCTION_ACTIVE
  samples:
    - path: string
      description: string
  valid_cases:
    - case_id: string
      description: string
      input: string
      expected_output_type: string
  invalid_cases: []
  edge_cases: []
```

## 18. Producers

- Format package developers create oracle-package.yaml and add cases
- `/run-oracle` skill executes cases

## 19. Consumers

- L07 (Tests) relies on VERIFIED status as proof of API correctness
- L08 (Evidence) V82 checks oracle obligations in declarations
- L18 (Package Release) requires VERIFIED before release

## 20. Skills and Commands

| Skill | Purpose |
|-------|---------|
| /run-oracle | Run oracle for one or all formats; writes oracle-run-summary.json |

## 21. Validators and Enforcement

- V82: `validate_oracle_obligations` — formats must be at ≥OBLIGATION_CREATED status
  - FAIL for RELEASE_GATE items if format not tracked in oracle registry
  - WARN for PRODUCT_SOURCE items if format at OBLIGATION_CREATED but not VERIFIED

## 22. Tests and Negative Controls

- Positive: run `/run-oracle --format fods` → 8/8 PASS
- ZST quirk: run with `.venv/Scripts/python tools/oracle/execute_oracle.py fods` (not `python`)
- Negative: introduce format API change that breaks oracle case → FAIL detected

## 23. Evidence and Observability

- `oracle/formats/{format}/reports/oracle-run-summary.json` — per-format results
- `oracle/registry/format-oracle-registry.yaml` — lifecycle status for all formats

## 24. Recovery and Rollback

- If oracle case FAILS: fix product API (L06) to pass, OR update oracle case if expectation was wrong
- FODS fix example: fods-valid-005 expected `fods:spreadsheet` → corrected to `office:document`

## 25. Security and Compliance

- Oracle tests use local samples only (no network calls)
- ZST requires `.venv/Scripts/python` for `zstandard` package

## 26. Cross-Layer Handoffs

| Handoff | From | To | Artifact |
|---------|------|----|---------|
| HO-004 | L05 | L07 | oracle-package.yaml VERIFIED status |

## 27. Migration and Backfill

For ora/pam/xpm/zpaq: create oracle-package.yaml with OBLIGATION_CREATED status when products exist.
No backfill needed for existing 20 formats (all at VERIFIED).

## 28. Effort and Dependencies

- TC-ORC-004 (execute_oracle.py refactor): ~3 hours. No dependencies.
- Oracle cases for ora/pam/xpm/zpaq: WAITING for product source.

## 29. Active Taskcards

| Task ID | Title | Status | Priority |
|---------|-------|--------|---------|
| TC-ORC-004 | Refactor execute_oracle.py at LOC cap; add cases for 4 new formats | TODO | P3 |

## 30. Ready Taskcards

TC-ORC-004 — READY (execute_oracle.py refactor can proceed independently of product).

## 31. Completed Taskcards

- TC-ORC-001: Oracle cases for fods/fodt — CLOSED (2026-06-26)
- TC-ORC-002: Wave 6 batch oracle backfill — CLOSED (2026-06-26)
- TC-ORC-003: V82 oracle obligations validator — CLOSED (2026-06-26)

## 32. Blocked and Waiting Work

- Oracle cases for ora/pam/xpm/zpaq: WAITING on product source existence.

## 33. Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| execute_oracle.py LOC cap = 1428 | 2026-06-26 | At baseline; next executor must be separate file |
| ZST requires .venv/Scripts/python | 2026-06-26 | zstandard package not in system Python |
| fods-valid-005: expected office:document | 2026-06-26 | FODS root element is office:document not fods:spreadsheet |

## 34. Work Log

```yaml
- log_id: WL-L05-001
  layer_id: L05
  task_id: TC-LP-001
  session_id: "923e237958c1"
  sprint_id: lp-bootstrap
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created oracle-layer.md permanent plan file"
  repository_revision: a7744cf6
  current_stage: GOVERNED_OPERATION
  status: IN_PROGRESS
  next_action: "TC-ORC-004: refactor execute_oracle.py"
```

## 35. Verification Log

```yaml
- verification_id: VER-L05-001
  layer_id: L05
  task_id: null
  repository_revision: a7744cf6
  contracts_verified:
    - "20 oracle-package.yaml files exist"
    - "73/73 PASS across all active formats"
    - "/run-oracle skill registered (TC-LA-010)"
    - "V82 oracle obligations validator active"
    - "oracle-run-summary.json generated per format"
  focused_result: PASS
  integration_result: PASS
  verdict: VERIFIED
  verified_at: "2026-06-26"
  verifier: forensic-layer-discovery-report.md
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L05-001
  layer_id: L05
  permanent_layer_plan: plans/layers/oracle-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: GOVERNED_OPERATIONAL
  current_stage: GOVERNED_OPERATION
  maturity_current: 4
  exact_next_task: TC-ORC-004
  why_this_is_next: >
    execute_oracle.py is at LOC cap (1428/1428). The next format executor cannot be
    added without refactoring the file. This blocks adding oracle cases for new formats.
  ready_tasks: [TC-ORC-004]
  blocked_tasks: []
  required_skills: [run-oracle]
  required_commands: [run-oracle]
  allowed_paths:
    - tools/oracle/
    - oracle/formats/
    - oracle/registry/
  forbidden_paths:
    - src/python/
    - src/net/
  required_verification:
    - "After refactor: .venv/Scripts/python tools/oracle/execute_oracle.py → all 20 formats PASS"
    - "ZST uses .venv/Scripts/python (not python)"
  important_decisions:
    - "fods-valid-005 expects office:document (not fods:spreadsheet)"
    - "ZST: must use .venv/Scripts/python"
    - "4 formats (ora/pam/xpm/zpaq) at OBLIGATION_CREATED — waiting for products"
  resume_instructions: >
    Oracle is healthy. 73/73 PASS. Next work is TC-ORC-004 (execute_oracle.py refactor).
    Run /run-oracle skill to verify current state before any changes.
```

## 37. Exact Next Actions

1. Run `.venv/Scripts/python tools/oracle/execute_oracle.py` to verify all 73 PASS
2. Plan refactor: extract per-format functions from execute_oracle.py to `tools/oracle/executors/{format}_executor.py`
3. execute_oracle.py becomes dispatcher (≤200 LOC)
4. Update oracle/registry/format-oracle-registry.yaml with new executor paths

## 38. Layer Completion Gate

```yaml
oracle_layer_completion_gate:
  all_active_formats_verified: true  # 20/20 VERIFIED
  execute_oracle_below_loc_cap: false  # at cap 1428/1428
  run_oracle_skill_registered: true
  v82_validator_active: true
  per_format_reports_exist: true
  overall: GOVERNED_OPERATIONAL_MINOR_GAP
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (bootstrap TC-LP-001) |
