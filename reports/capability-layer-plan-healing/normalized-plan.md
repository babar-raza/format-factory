# Normalized Plan — Capability & Feature Understanding Layer Sprint
# Sprint ID: FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001
# Run ID: capability-feature-understanding-layer-healing-20260608-e382e5f
# Normalized: 2026-06-08

## Corrections from Plan Healing

1. Run ID: `capability-feature-understanding-layer-healing-20260608-e382e5f` (auto-detected)
2. Gnumeric `set_cell_value`: ALREADY IMPLEMENTED — only verify tests pass
3. `test_r126_gnumeric_set_cell.py`: ALREADY EXISTS — only run it
4. FUL layer: EXISTS at `schemas/format-understanding/` — EXTEND, don't replace
5. Known supervisor failures: RE-DETECT fresh (do not assume 21)
6. poc-targets.yaml staleness: UPDATE as part of Phase C/D healing

---

## Phase Execution Order

Phase A → Phase B → Phase C (parallel with D-schemas) → Phase D → Phase E → Phase F → Phase G → Phase H → Phase I

---

## Phase A — COMPLETE (plan healing artifacts created)

Files created:
- `reports/capability-layer-plan-healing/plan-review.md`
- `reports/capability-layer-plan-healing/plan-healing-decision-log.json`
- `reports/capability-layer-plan-healing/capability-vocabulary.yaml`
- `schemas/capability/capability_status_taxonomy.schema.json`
- `reports/capability-layer-plan-healing/status-taxonomy.md`
- `reports/capability-layer-plan-healing/normalized-plan.md` (this file)

---

## Phase B — Taskcard Creation

Create taskcards at: `taskcards/capability-layer/capability-feature-understanding-layer-healing-20260608-e382e5f/`
Create registry at: `reports/capability-layer-plan-healing/taskcard-registry.json`
Create execution state at: `reports/capability-layer-plan-healing/execution-state.json`

Taskcard groups: CAP-PLAN-001..005, CAP-DISC-001..008, CAP-SCHEMA-001..006, CAP-GEN-001..011, CAP-VAL-001..010, CAP-SEL-001..006, CAP-PROD-001..007, CAP-PILOT-*, CAP-MANUAL-001..008, CAP-EVID-001..007

---

## Phase C — Investigation (27 areas)

Files to create:
- `reports/capability-layer/investigation-report.md`
- `reports/capability-layer/investigation-matrix.md`
- `reports/capability-layer/repo-truth-inventory.json`

Key investigation areas (see Phase C in main plan for full list):
- FUL schema state (schemas/format-understanding/ contents)
- poc-targets.yaml staleness (confirmed — update needed)
- product_task_selector.py hardcoded catalog (confirmed — needs gap integration)
- Requirements authority tool state (tools/requirements_authority/)
- Current known test failures (re-detect)

---

## Phase D — Capability Layer Build

New files to create (schemas):
- `schemas/capability/capability_record.schema.json`
- `schemas/capability/capability_map.schema.json`
- `schemas/capability/capability_gap.schema.json`
- `schemas/capability/pilot_report.schema.json`

New tool files:
- `tools/capability_layer/__init__.py`
- `tools/capability_layer/capability_map_generator.py`
- `tools/capability_layer/validate_capability_map.py`

Generated outputs:
- `reports/capability-layer/unified-capability-map.json`
- `reports/capability-layer/commercial-capability-map.json`
- `reports/capability-layer/foss-reduced-capability-map.json`
- `reports/capability-layer/gap-ledger.json`
- `reports/capability-layer/action-queue.json`

Design doc:
- `docs/capability-layer-design.md`

---

## Phase E — Product Progress

### E1. FODG write/export (CAP-PROD-001..003)
Target: `src/python/fodg/fodg_codec.py`
- Add `write_fodg(doc, dest)` — serialize FODG XML back to file
- Add `export_to_txt(doc)` — extract text content as string
- Tests: `tests/python/fodg/test_cap_r126_fodg_write.py`
- Sample output
- Ledger entries for both changes

Pattern reuse:
- `write_gnumeric()` in gnumeric_codec.py for XML+ODF structure
- `abw_codec.py:export_to_txt()` for text export pattern

### E2. Gnumeric set_cell_value (CAP-PROD-004..005)
- ALREADY IMPLEMENTED — just run `test_r126_gnumeric_set_cell.py`
- Update poc-targets.yaml with set_cell_value: PASS
- Add ledger entry for the R125/R126 implementation (if not already there)

---

## Phase F — Pilots (8 total)

All pilots at: `reports/capability-layer/pilots/<pilot_id>.{md,json}`

| Pilot ID | Format | Type | Expected Verdict |
|----------|--------|------|-----------------|
| C-001 | FODS | Commercial | PASS_WITH_LIMITATIONS (no live spec cache) |
| C-002 | FODT | Commercial | PASS_WITH_LIMITATIONS |
| C-003 | Netpbm | Commercial | PASS_WITH_LIMITATIONS |
| F-001 | ABW | FOSS/reduced | PASS_VERIFIED (all functions confirmed) |
| F-002 | Gnumeric | FOSS/reduced | PASS_VERIFIED |
| F-003 | NDJSON | FOSS/reduced | PASS_VERIFIED |
| E-001 | FODG | Expansion | PASS_WITH_LIMITATIONS (write added this sprint) |
| A-001 | TOML | Acquisition | NOT_ENOUGH_AUTHORITY_DATA (no spec downloaded) |

---

## Phase G — Validation

Test commands (in order):
1. `python -m pytest tests/capability_layer/ -v` (new tests)
2. `python -m pytest tests/python/fodg/ -v` (FODG new tests)
3. `python -m pytest tests/python/gnumeric/ -v` (verify set_cell_value)
4. `python -m pytest tests/python/abw/ -v` (regression)
5. `python -m pytest tests/supervisor/ -v --tb=short` (re-detect failures)
6. `python -m pytest tests/python/ -v --tb=short` (broad regression)

Note: NEVER use PYTHONPATH=src/python prefix (causes csv module shadowing).

---

## Phase H — Manual Verification

Create:
- `reports/capability-layer/manual-artifact-verification.md`
- `reports/capability-layer/manual-artifact-verification.json`

---

## Phase I — Closeout

1. Write `.local/evidences/capability-feature-understanding-layer-healing-20260608-e382e5f/evidence-declaration.yaml`
2. Run: `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/capability-feature-understanding-layer-healing-20260608-e382e5f/evidence-declaration.yaml`
3. Check exit code
4. Run: `python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/capability-feature-understanding-layer-healing-20260608-e382e5f/evidence-declaration.yaml`
5. Report absolute path + SHA-256
