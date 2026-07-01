# Plan: Gate 4 Prototype Coverage — Forensic Recon, Canonical Evidence, Gap Backfill, Pipeline Healing

plan_type: gate4_backfill
mission_id: FF-G4-BACKFILL-001

## Context

Gate 4 (parsing feasibility prototype) has inconsistent representation across the 24 tracked formats.
Seven formats have canonical prototypes in `prototypes/by-format/`. Thirteen formats have mature
source tracks in `src/python/` with gate_4 marked COMPLETE/PASS in the registry, but no evidence
wrapper or canonical Gate 4 artifact. Four formats (CSV, TSV, NDJSON, TOML) have full source
implementations but incomplete Gate 4 registry traceability. Two formats (XPM, PAM) completed
Gates 1–3 but have no parser or prototype. Two formats (ZPAQ, ORA) are blocked before Gate 4.
The acquisition pipeline has no schema or validator enforcing one explicit Gate 4 disposition per
format, allowing this drift to accumulate silently.

This plan normalizes all 24 formats to one canonical Gate 4 evidence contract, backfills gaps,
creates minimal prototypes only where prerequisites are complete, heals the pipeline, and proves
idempotency.

---

## Discovered State (Phase 1 Research)

**Canonical prototypes** (prototypes/by-format/):
- fods, fodt, zst (have README + test files)
- fodp, fodg, gnumeric, abw (parsers exist; README/manifest absent or partial)
- Gate 4 skill tests: tests/skills/test_{abw,fodg,fodp,gnumeric,zst}_gate4_prototype.py

**Source-track equivalents** (src/python/ exists, gate_4 complete in registry, no wrapper):
- dif, sylk, pbm, pgm, ppm, qoi, ods, odt, xcf — COMPLETE/PASS in registry

**Source tracks with missing Gate 4 traceability:**
- csv, tsv — Gate 3 complete, gate_4 field absent from registry
- ndjson, toml — Gate 1 in registry only; full src/python/ exists

**Gate 1–3 complete, no parser/prototype:**
- xpm — XPM3 format, samples exist in samples/by-format/xpm/
- pam — P7 netpbm, samples exist in samples/by-format/pam/

**Blocked before Gate 4:**
- zpaq — Gate 3 blocked (requires ZPAQL VM bytecode generation, zpaq CLI unavailable)
- ora — Gate 1 deferred (score 6.8/10 < 7.0 threshold)

**Key files:**
- registry/format-registry.yaml
- registry/format-completion-matrix.yaml
- acquisition-packs/{format}/pack.yaml (all 26 formats)
- prototypes/by-format/{format}/ (7 existing)
- src/python/{format}/ (20 formats)
- samples/by-format/{format}/ (23 formats)
- docs/python-foss/acquisition-workflow.md
- docs/governance/prototype-quarantine-policy.md
- tests/skills/test_*_gate4_prototype.py (6 files)
- tests/python/test_gate4_prototype_common.py

---

## Taskcards

| TC-ID | Status |
|-------|--------|
| TC-G4-001 | CLOSED |
| TC-G4-002 | CLOSED |
| TC-G4-003 | CLOSED |
| TC-G4-004 | CLOSED |
| TC-G4-005 | CLOSED |
| TC-G4-006 | CLOSED |
| TC-G4-007 | CLOSED |
| TC-G4-008 | CLOSED |

---

## TC-G4-001: Inventory, Drift Root Cause, Gap Ledger

**Deliverables:**

1. `reports/prototypes/gate4-format-inventory.yaml`
   - 24 format entries with all required fields:
     format_id, gate_1/2/3/4_status, gate_4_representation (CANONICAL_PROTOTYPE /
     SOURCE_TRACK_EQUIVALENT / EVIDENCE_WRAPPER / REGISTRY_CLAIM_ONLY / MISSING /
     BLOCKED_BEFORE_GATE4 / NOT_APPLICABLE), prototype_path, source_path, acquisition_pack,
     sample_paths, gate4_tests, current_truth, gap_type, required_action
   - UNCLASSIFIED_SUPPORTED_FORMATS = 0

2. `reports/prototypes/gate4-drift-root-cause.yaml`
   - Root causes classified per the 9 categories (GOVERNANCE_EVOLUTION, REGISTRY_SCHEMA_GAP,
     WORKFLOW_BYPASS, SOURCE_TRACK_SHORTCUT, MISSING_PREREQUISITES, FORMAT_SCOPE_EXCEPTION,
     HISTORICAL_MIGRATION, TEST_COVERAGE_GAP, DOCUMENTATION_DRIFT)
   - GATE4_REPRESENTATION_ROOT_CAUSES_IDENTIFIED = true

3. `reports/prototypes/gate4-gap-ledger.yaml`
   - Each gap classified as: A=REGISTRY_ONLY_GAP, B=EVIDENCE_WRAPPER_GAP,
     C=RETROSPECTIVE_ACQUISITION_GAP, D=NEW_GATE4_PROTOTYPE_REQUIRED,
     E=BLOCKED_BEFORE_GATE4, F=VALID_SCOPE_EXCEPTION
   - MATERIAL_GATE4_GAPS_WITHOUT_CANONICAL_ENTRIES = 0
   - READY_GATE4_GAPS_WITHOUT_TASKCARDS = 0

**Expected classification:**
- 7 CANONICAL_PROTOTYPE (fods, fodt, zst, fodp, fodg, gnumeric, abw) — some need contract normalization
- 9 SOURCE_TRACK_EQUIVALENT needing EVIDENCE_WRAPPER (dif, sylk, pbm, pgm, ppm, qoi, ods, odt, xcf)
- 4 MISSING Gate 4 traceability (csv=B+C, tsv=B+C, ndjson=C, toml=C)
- 2 NEW_GATE4_PROTOTYPE_REQUIRED (xpm, pam)
- 2 BLOCKED_BEFORE_GATE4 (zpaq, ora)

---

## TC-G4-002: Verify + Complete Existing Canonical Prototypes

**Goal:** Confirm the 7 existing canonical prototypes satisfy the new Gate 4 contract.
Ensure README.md + manifest present for all; fill gaps without duplicating logic.

**Formats:** fods, fodt, zst, fodp, fodg, gnumeric, abw

**Per-prototype checklist:**
- README.md exists and declares: format_id, evidence_type=STANDALONE_PROTOTYPE,
  Gate 3 corpus reference, limitations, delegated_source (if any), no-release-readiness disclaimer
- gate4_wrapper manifest (gate4_wrapper: block) in README or separate manifest.yaml
- At least one valid sample parse test passes
- At least one invalid/missing input handled
- No parser logic duplicated from src/python/

**Currently missing:**
- fodp, fodg, gnumeric: no README.md — must be added
- abw: README.md present but verify manifest block
- fods, fodt, zst: README.md present; verify contract fields

**Do NOT modify:** Parser logic, tests that already pass

---

## TC-G4-003: Evidence Wrappers — CSV, TSV, NDJSON, TOML

**Goal:** Create thin evidence wrappers delegating to existing src/python/ parsers.
Update registry to add gate_4 field. Label retrospective acquisition explicitly.

**Per-format deliverables (under prototypes/by-format/{format}/):**
- README.md with gate4_wrapper manifest block
- {format}_gate4_probe.py — thin adapter delegating to src/python/{format}/
  - validate(): imports from src.python.{format}, loads valid sample, returns parsed result
  - probe_invalid(): confirms graceful rejection of invalid input
  - contains NO parsing logic
- gate4-evidence.yaml — records gate3_corpus, valid_probe_result, invalid_probe_result,
  evidence_type, delegated_source, source_revision

**Retrospective label:** NDJSON and TOML have Gate 1 only in registry but have full source.
The evidence wrappers must be explicitly labeled `retrospective: true` and reconstruct
the Gate 2–4 acquisition trace from existing artifacts.

**Registry updates (format-registry.yaml):**
- csv: add gate_4 block with status: passed, evidence_type: EVIDENCE_WRAPPER,
  prototype_path, corpus, tests, verified_revision
- tsv: same as csv
- ndjson: add gate_2, gate_3, gate_4 blocks retrospectively
- toml: same as ndjson

**Rule:** Do not duplicate parser logic. Every method in the probe must call into existing src/python/.

---

## TC-G4-004: Minimal Prototypes — XPM and PAM

**Prerequisites confirmed:** Gates 1–3 complete; samples exist; no src/python/ parser.

**XPM prototype** (`prototypes/by-format/xpm/`):
- xpm_parser.py
  - parse_xpm3(path): read XPM3 file, parse `/* XPM */` signature, dimensions line
    (`"W H N C"` — width, height, ncolors, chars_per_pixel), color table entries,
    pixel data rows; return dict with format_id, width, height, ncolors, colors, pixels
  - is_xpm3(path): check magic `/* XPM */` header
  - Rejects: invalid magic, malformed dimension line, truncated color table
  - Security: bounded input (max 4096x4096, max 256 colors, max 16 chars/pixel)
  - No production namespace — Gate 4 scope only
- README.md with gate4_wrapper manifest (evidence_type: STANDALONE_PROTOTYPE)
- tests/skills/test_xpm_gate4_prototype.py
  - test_valid_xpm3_loads, test_dimensions_correct, test_color_table_parsed,
    test_pixel_rows_present, test_invalid_magic_rejected, test_malformed_dimensions_rejected

**PAM prototype** (`prototypes/by-format/pam/`):
- pam_parser.py
  - parse_pam(path): read P7 header lines until ENDHDR, extract WIDTH, HEIGHT, DEPTH,
    MAXVAL, TUPLTYPE; compute raster size = WIDTH * HEIGHT * DEPTH * bytes_per_sample;
    verify raster data length; return dict with format_id + header fields
  - is_pam(path): check magic `P7\n` header
  - Rejects: non-P7 magic, missing required header fields, raster size mismatch
  - Security: bounded (max 4096x4096, max depth 4)
- README.md with gate4_wrapper manifest (evidence_type: STANDALONE_PROTOTYPE)
- tests/skills/test_pam_gate4_prototype.py
  - test_valid_pam_loads, test_header_fields_parsed, test_raster_length_validated,
    test_invalid_magic_rejected, test_malformed_header_rejected

---

## TC-G4-005: Blocked Format Documentation — ZPAQ, ORA

**ZPAQ:** Gate 3 blocked — cannot verify corpus samples without ZPAQL VM or zpaq CLI.
- Add explicit entry in gate4-gap-ledger.yaml: type=BLOCKED_BEFORE_GATE4
- Add registry gate_4 block: status=blocked, reason=gate3_prerequisite_incomplete,
  blocker=zpaql_vm_unavailable, next_gate=gate_3_recovery_required,
  recovery_path=acquire_zpaq_cli_or_implement_vm
- Do NOT create prototype, do NOT mark passed

**ORA:** Gate 1 deferred — acquisition score 6.8/10 below 7.0 threshold.
- Add explicit entry in gate4-gap-ledger.yaml: type=BLOCKED_BEFORE_GATE4
- Add registry gate_4 block: status=blocked, reason=gate1_not_passed,
  blocker=score_below_threshold, next_gate=gate_1_rescore_or_defer
- Do NOT create prototype

---

## TC-G4-006: Registry + Acquisition Pack Reconciliation

**format-registry.yaml updates:**
- Every format must have a gate_4 block with: status, evidence_type, prototype_path OR
  delegated_source_path, tests[], corpus[], acquisition_pack, limitations[], verified_revision
- Normalize existing passing formats (ods, odt, qoi, xcf, dif, sylk, pbm, pgm, ppm) to include
  evidence_type: SOURCE_TRACK_EQUIVALENT or EVIDENCE_WRAPPER where appropriate
- Do NOT change release authorization, commercial readiness, or Gate 10/11 status

**format-completion-matrix.yaml updates:**
- Every format row must have gate_4_status column: passed / blocked / not_applicable / in_progress
- Sync with registry gate_4.status

**Acquisition pack updates** (`acquisition-packs/{format}/pack.yaml`):
- CSV, TSV, NDJSON, TOML: add gate_4 section referencing wrapper path + tests
- XPM, PAM: add gate_4 section referencing new prototype path + tests
- ZPAQ, ORA: add gate_4 section with status=blocked + blocker explanation

**Consistency check:**
- GATE4_REGISTRY_ACQUISITION_MISMATCHES = 0 after update

---

## TC-G4-007: Pipeline Healing + Skill + Tests

**Gate 4 evidence schema** (`docs/gate4-evidence-contract.yaml`):
- Define required fields: format_id, evidence_type, gate3_corpus[], valid_probe_result,
  invalid_probe_result, limitations[], tests[], acquisition_pack, registry_links[],
  evidence_hash, verdict
- Prohibited: gate_4 pass with path_only, source parser without evidence artifact, supported
  format with no gate_4 disposition, prototype code promoted without production hardening

**Gate transition validator** (`tools/gates/validate_gate4_evidence.py`):
- validate_gate4(format_id): checks registry gate_4 block completeness, verifies prototype_path
  or delegated_source_path exists, verifies at least one test references the format,
  verifies corpus sample exists, verifies acquisition_pack linked
- Returns PASS / FAIL with specific field failures

**Skill registration** (`.supervisor/skill-registry.yaml`):
```yaml
- id: backfill-gate4-prototype-evidence
  command: /backfill-gate4-prototype-evidence
  description: Inventory Gate 4 status, classify evidence strategy, create wrappers,
    create minimal prototypes only when allowed, update registries/acquisition packs,
    run focused validation, emit resumable evidence.
  task_types: [GATE4_INVENTORY, GATE4_REGISTRY_REPAIR, GATE4_EVIDENCE_WRAPPER,
    GATE4_RETROSPECTIVE_ACQUISITION, GATE4_MINIMAL_PROTOTYPE, GATE4_PREREQUISITE_BLOCKER,
    GATE4_TEST_BACKFILL, GATE4_PIPELINE_HEALING, GATE4_IDEMPOTENCY]
```

**Contract tests** (`tests/python/test_gate4_contract.py`):
- test_path_only_evidence_rejected: validator rejects entry with no tests/corpus
- test_missing_gate3_corpus_rejected: validator rejects when gate_3_status != passed
- test_valid_wrapper_accepted: validator accepts properly formed EVIDENCE_WRAPPER
- test_standalone_prototype_accepted: validator accepts STANDALONE_PROTOTYPE
- test_blocked_prerequisite_retained: validator accepts BLOCKED_BEFORE_GATE4 with blocker field

**Governance tests** (`tests/python/test_gate4_governance.py`):
- test_every_format_has_gate4_disposition: read format-registry.yaml, assert every format has gate_4 block
- test_registry_matrix_consistent: gate_4.status in registry matches completion-matrix gate_4_status
- test_blocked_formats_not_passed: zpaq and ora do not have gate_4.status = passed
- test_no_path_only_claims: no gate_4 block has only prototype_path with no tests

---

## TC-G4-008: Pilots + Idempotency + Final Report

**Pilot 1 — Existing canonical prototype:**
- Run tests/skills/test_fods_gate4_prototype.py (or test_zst_gate4_prototype.py)
- Assert existing prototype satisfies new contract (README has manifest block, valid+invalid coverage)

**Pilot 2 — Evidence wrapper:**
- Run wrapper probe for CSV: python prototypes/by-format/csv/csv_gate4_probe.py
- Assert delegation works, corpus executes, registry traceable, no code duplication

**Pilot 3 — Retrospective acquisition:**
- Verify NDJSON gate4-evidence.yaml is labeled retrospective=true
- Verify Gates 2–4 blocks added to registry (reconstructed from existing source/samples)

**Pilot 4 — New minimal prototype:**
- Run tests/skills/test_xpm_gate4_prototype.py
- Assert valid XPM3 parses, invalid magic rejected, dimensions returned

**Pilot 5 — Blocked prerequisite:**
- Run validate_gate4("zpaq") → assert returns FAIL with reason=gate3_prerequisite_incomplete
- Run validate_gate4("ora") → assert returns FAIL with reason=gate1_not_passed
- Assert neither appears in registry with gate_4.status=passed

**Pilot 6 — Source API drift:**
- Temporarily alias a delegated symbol in CSV wrapper to nonexistent name
- Assert wrapper raises ImportError or AttributeError (compatibility check fails)
- Revert change

**Pilot 7 — Idempotency:**
- Re-run: inventory build, wrapper generation, registry sync, acquisition sync, validator
- Assert zero material changes (file checksums unchanged, test counts unchanged)

**Final counters (must all be 0):**
- UNCLASSIFIED_SUPPORTED_FORMATS
- GATE4_PASS_WITHOUT_EXECUTABLE_EVIDENCE
- GATE4_REGISTRY_ACQUISITION_MISMATCHES
- DUPLICATED_PARSER_IMPLEMENTATIONS_CREATED
- READY_GATE4_GAPS_WITHOUT_TASKCARDS
- FALSE_GATE4_PASSES_FOR_BLOCKED_FORMATS
- FAILED_REQUIRED_PILOTS
- MATERIAL_SECOND_RUN_CHANGES

**Final report:** `reports/prototypes/gate4-prototype-backfill-report.md`

**Final verdict:** GATE4_COVERAGE_NORMALIZED_BACKFILLED_PROVEN_AND_IDEMPOTENT

---

## Verification

```bash
# Pre-mutation guard
python tools/supervisor/validate_source_architecture.py

# Gate 4 contract tests
.venv/Scripts/pytest tests/python/test_gate4_contract.py tests/python/test_gate4_governance.py -q

# Format-specific Gate 4 skill tests
.venv/Scripts/pytest tests/skills/test_*gate4* -q

# XPM and PAM new prototype tests
.venv/Scripts/pytest tests/skills/test_xpm_gate4_prototype.py tests/skills/test_pam_gate4_prototype.py -q

# Source track format tests (ensure wrappers don't break existing)
.venv/Scripts/pytest tests/python/csv/ tests/python/tsv/ tests/python/ndjson/ tests/python/toml/ -q

# Gate 4 validator
python tools/gates/validate_gate4_evidence.py

# Idempotency: re-run inventory and assert no changes
python tools/gates/validate_gate4_evidence.py --all-formats
```

---

## Files to Create / Modify

**New files:**
- reports/prototypes/gate4-format-inventory.yaml
- reports/prototypes/gate4-drift-root-cause.yaml
- reports/prototypes/gate4-gap-ledger.yaml
- reports/prototypes/gate4-prototype-backfill-report.md
- docs/gate4-evidence-contract.yaml
- tools/gates/validate_gate4_evidence.py
- prototypes/by-format/csv/csv_gate4_probe.py + README.md + gate4-evidence.yaml
- prototypes/by-format/tsv/tsv_gate4_probe.py + README.md + gate4-evidence.yaml
- prototypes/by-format/ndjson/ndjson_gate4_probe.py + README.md + gate4-evidence.yaml
- prototypes/by-format/toml/toml_gate4_probe.py + README.md + gate4-evidence.yaml
- prototypes/by-format/xpm/xpm_parser.py + README.md
- prototypes/by-format/pam/pam_parser.py + README.md
- tests/skills/test_xpm_gate4_prototype.py
- tests/skills/test_pam_gate4_prototype.py
- tests/python/test_gate4_contract.py
- tests/python/test_gate4_governance.py

**Modified files:**
- registry/format-registry.yaml (gate_4 blocks for csv, tsv, ndjson, toml, zpaq, ora; normalize others)
- registry/format-completion-matrix.yaml (gate_4_status column for all formats)
- acquisition-packs/{csv,tsv,ndjson,toml,xpm,pam,zpaq,ora}/pack.yaml (gate_4 sections)
- prototypes/by-format/{fodp,fodg,gnumeric}/README.md (add — currently missing)
- .supervisor/skill-registry.yaml (add backfill-gate4-prototype-evidence skill)

**Existing files — verify only (do not modify logic):**
- prototypes/by-format/{fods,fodt,zst,abw}/ (verify contract compliance)
- tests/skills/test_{abw,fodg,fodp,gnumeric,zst}_gate4_prototype.py


## Convergence Audit Findings (2026-07-01 Post-Sprint Audit)

**FINDING A001:** Registry state regressed after readme_sync run_sync.py. Root cause: YAML round-trip
by pipeline tool between script writes and audit. Mitigation: re-run update + patch scripts idempotently.
Status: RESOLVED — scripts re-run, validator 25/25 PASS.

**FINDING A002 (pre-existing):** test_no_src_net_zst fails — `src/net/zst/` exists. Not caused by
this plan. Classifed VERIFIED_NEGATIVE pre-existing.

**FINDING A003:** Registry durability requires scripts be re-run after any yaml pipeline operation.
Mitigation added: `tools/gates/update_gate4_registry.py` + `tools/gates/patch_gate4_registry_fields.py`
must be run atomically after any registry round-trip. Future hardening via registry schema enforcement.

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-G4-001 | CLOSED |
| TC-G4-002 | CLOSED |
| TC-G4-003 | CLOSED |
| TC-G4-004 | CLOSED |
| TC-G4-005 | CLOSED |
| TC-G4-006 | CLOSED |
| TC-G4-007 | CLOSED |
| TC-G4-008 | CLOSED |

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-01T11:59:02.729802+00:00"
  locked_by: "34c4217ef0bd"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
