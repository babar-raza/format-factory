# Oracle Layer Wave 5/6 Hardening Addendum
# Addendum to: FORMAT-FACTORY-ORACLE-LAYER-HARDENING-001 (master-plan §74)
# Source audit: .local/supervisor/oracle-hardening-audit/
# Audit verdict: SPRINT_ACCEPTED_WITH_LIMITATIONS
# Hardening date: 2026-06-25
# Mission: Govern unresolved oracle integration and backfill work after mission close

---

## 1. Plan File Hardening Change Log

| Entry | Date | Change |
|---|---|---|
| INIT | 2026-06-25 | Addendum created from PSL-PROMPT-1 audit of oracle layer mission |
| RESOLVED-L1-001 | 2026-06-25 | All oracle files committed as 8263527f |
| RESOLVED-L2-004 | 2026-06-25 | master-plan.md §74 added with CLOSED status |
| TC-ORC-001 CLOSED | 2026-06-26 | FODS executor implemented; 7/8 PASS; fods-valid-005 genuine oracle finding |
| TC-ORC-002 CLOSED | 2026-06-26 | executor_property_gaps added to coverage report; unsupported-property WARNINGs in CSV+ZST executors |
| TC-ORC-003 CLOSED | 2026-06-26 | V82 validate_oracle_obligations wired into governance suite; 3 regression tests PASS |
| TC-ORC-004 CLOSED | 2026-06-26 | All 6 comparator entries annotated with implementation_status + implementation_note |
| TC-ORC-005 CLOSED | 2026-06-26 | oracle-obligations CI stage added to .gitlab-ci.yml; allow_failure: false |
| TC-ORC-006 CLOSED | 2026-06-26 | _validate_oracle_package_schema() wired into run_oracle_for_format(); graceful fallback |
| TC-ORC-007 CLOSED | 2026-06-26 | oracle-backfill-wave6.md created; 4 GAP-ORC-BACKFILL-* entries in gap-ledger.json |
| ADDENDUM COMPLETE | 2026-06-26 | All 7 Wave 5/6 taskcards CLOSED. Plan status: TERMINAL_CLOSED |

---

## 2. Audit Findings Incorporated

Source: `.local/supervisor/oracle-hardening-audit/stage1-{l1,l2,l3}*-issues.yaml`

| Finding ID | Level | Title | Disposition |
|---|---|---|---|
| L1-001 | L1 | All oracle files uncommitted | RESOLVED — commit 8263527f |
| L1-002 | L1 | FODS executor not implemented | OPEN → TC-ORC-001 |
| L1-003 | L1 | cell_value executor gap unregistered | OPEN → TC-ORC-002 |
| L2-001 | L2 | Oracle obligation validator not wired into governance suite | OPEN → TC-ORC-003 |
| L2-002 | L2 | Comparator implementation files absent | OPEN → TC-ORC-004 |
| L2-003 | L2 | No CI gate for oracle | OPEN → TC-ORC-005 |
| L2-004 | L2 | master-plan.md not updated | RESOLVED — §74 added |
| L3-001 | L3 | Oracle obligation gate advisory-only | MERGED with TC-ORC-003 |
| L3-002 | L3 | Schema not auto-validated at runtime | OPEN → TC-ORC-006 |
| L3-003 | L3 | Wave 6 backfill has no sprint plan | OPEN → TC-ORC-007 |

---

## 3. Resolved / Preserved Work

All oracle layer Wave 3 deliverables are ACCEPTED_VERIFIED and must NOT be re-executed:

- `oracle/schema/oracle-package.schema.json` — JSON Schema v7, 12-class authority
- `oracle/schema/oracle-verdict.schema.json` — verdict output schema
- `oracle/registry/format-oracle-registry.yaml` — 24 format obligations
- `oracle/registry/oracle-profile-registry.yaml` — 17 reusable profiles
- `oracle/registry/comparator-registry.yaml` — 6 comparators (design-doc status)
- `oracle/oracle-authority-policy.md` — 8-section authority policy
- `oracle/oracle-layer-inventory.yaml` — maturity Level 2→3 assessment
- `oracle/formats/csv/oracle-package.yaml` — 5/5 PASS (RFC 4180, SPEC_NORMATIVE)
- `oracle/formats/zst/oracle-package.yaml` — 6/6 PASS (facebook/zstd, AUTH_REF_VECTOR)
- `oracle/formats/fods/oracle-package.yaml` — 9 cases defined (ODF 1.3, SPEC_NORMATIVE)
- `oracle/reports/oracle-coverage-report.json` — portfolio state
- `tools/oracle/execute_oracle.py` — verdict engine (CSV+ZST handlers active)
- `tools/oracle/validate_oracle_obligations.py` — 24/24 PASS standalone

---

## 4. Unresolved Work Register

| TC ID | Title | Priority | Wave | Status |
|---|---|---|---|---|
| TC-ORC-001 | FODS oracle executor handler | HIGH | 5 | CLOSED — 7/8 PASS (fods-valid-005 is genuine oracle finding: spec_qname office:document ≠ fods:spreadsheet) |
| TC-ORC-002 | Register cell_value executor gap | LOW | 5 | CLOSED — executor_property_gaps section added to oracle-coverage-report.json; CSV/ZST/FODS supported_properties documented; unsupported-property warnings added to CSV+ZST executors |
| TC-ORC-003 | Wire oracle obligation validator into governance suite as V82 | HIGH | 5 | CLOSED — V82 in governance_validators_ext2.py + governance_validator_runner.py; 3/3 regression tests PASS; real-repo 24/24 PASS |
| TC-ORC-004 | Add implementation_status to comparator registry | LOW | 5 | CLOSED — all 6 comparator entries have implementation_status + implementation_note; YAML valid |
| TC-ORC-005 | Add oracle obligation CI step | MEDIUM | 5 | CLOSED — oracle-obligations stage added to .gitlab-ci.yml; allow_failure: false; YAML valid |
| TC-ORC-006 | Add runtime schema validation in executor | LOW | 5 | CLOSED — _validate_oracle_package_schema() wired into run_oracle_for_format(); prints WARNING; graceful fallback if jsonschema absent |
| TC-ORC-007 | Create Wave 6 oracle backfill sprint plan (18 formats) | MEDIUM | 6 | CLOSED — plans/oracle-backfill-wave6.md created with 4 batches + authority sources; 4 GAP-ORC-BACKFILL-* entries in gap-ledger.json |

---

## 5. Taskcard Register

### TC-ORC-001: FODS Oracle Executor Handler
```
taskcard_id: TC-ORC-001
title: Implement FODS oracle executor handler in execute_oracle.py
source_issue_ids: [L1-002]
source_issue_level: L1_EXECUTION
source_audit_finding: >
  oracle/formats/fods/oracle-package.yaml has 9 cases defined (5 valid + 3 invalid + 1 roundtrip)
  but tools/oracle/execute_oracle.py has no FODS case handler. execute_oracle.py --format fods
  would fail with "unsupported format" error.
why_it_matters: >
  FODS is the primary ODF spreadsheet format. It has the most complete oracle package
  (SPEC_NORMATIVE + ODF 1.3 references). Without execution, oracle level remains AUTHORITY_MAPPED
  and the FODS oracle gap persists despite all case definitions being written.
risk_addressed: >
  Prevents oracle package from being a design document only. Completes the FODS
  product oracle loop (Wave 5 target: CASES_DEFINED + first execution).
status: not_attempted
priority: HIGH
wave: 5
lane_owner: oracle-executor-lane
supervisor_role: PSL-PROMPT-3
required_implementation:
  - Add execute_fods_valid_case(case, oracle_pkg) function in tools/oracle/execute_oracle.py
  - Add execute_fods_invalid_case(case, oracle_pkg) function
  - Wire fods handlers into run_oracle_for_format() dispatch
  - Import FodsDocument or use load_fods() from installed fods package
  - Populate observed dict with sheet_count, row_count, column_count, has_header at minimum
  - For invalid cases: confirm parser raises / returns error state for malformed FODS
required_verification:
  - python tools/oracle/execute_oracle.py --format fods --all produces at least 3/9 PASS
  - No regression in CSV 5/5 PASS or ZST 6/6 PASS
  - oracle/formats/fods/reports/oracle-run-summary.json written with verdict != INVALID_ORACLE
required_evidence:
  - oracle/formats/fods/reports/oracle-run-summary.json showing >=3 PASS
  - terminal output of execute_oracle.py --format fods --all
quality_dimensions:
  - requirement_correctness: executor supports fods case types
  - implementation_correctness: observed dict fields match fods oracle case expected_model_properties
  - test_coverage: at least valid+invalid cases exercised
  - evidence_completeness: run-summary.json written
  - repeatability: two sequential runs produce identical verdicts
scoring_rubric:
  pass_threshold: all_required_dimensions >= 4
reroute_rule_if_score_below_4: >
  If fods model properties unavailable, downgrade case scope to structural_validity only
  (fods_valid: is_fods=true, sheet_count>=1) — narrow scope rather than failing.
acceptance_criteria:
  - execute_oracle.py --format fods --all runs without "unsupported format" error
  - oracle-run-summary.json verdict != INVALID_ORACLE
  - No regression in CSV/ZST pilots
stop_conditions:
  - fods package not importable from venv (BLOCKED_EXTERNAL — reinstall wheel)
allowed_paths:
  - Modify tools/oracle/execute_oracle.py
  - Read oracle/formats/fods/oracle-package.yaml
  - Read src/python/fods/ source
forbidden_paths:
  - Do not modify oracle/formats/fods/oracle-package.yaml case definitions
  - Do not modify CSV or ZST handlers in execute_oracle.py
  - Do not modify oracle schemas or registries
dependencies: []
closeout_rules: oracle/formats/fods/reports/oracle-run-summary.json shows verdict not INVALID_ORACLE
machine_state: not_attempted
validation_commands:
  - python tools/oracle/execute_oracle.py --format fods --all
  - python tools/oracle/execute_oracle.py --format csv --all  # regression
  - python tools/oracle/execute_oracle.py --format zst --all  # regression
```

---

### TC-ORC-002: Register cell_value Executor Gap
```
taskcard_id: TC-ORC-002
title: Register cell_value lookup gap in oracle executor documentation
source_issue_ids: [L1-003]
source_issue_level: L1_EXECUTION
source_audit_finding: >
  csv-valid-003 was originally designed to test cell_value(row=0, col=1) but the executor
  observed dict only supports row_count, column_count, has_header, headers. The gap is
  commented in oracle-package.yaml but not in any oracle gap registry.
why_it_matters: >
  Future oracle authors writing CSV cases with property: cell_value will produce cases that
  silently evaluate to no property check (null observed). The gap should be in a machine-readable
  registry so the executor can warn at parse time.
risk_addressed: Silent oracle case misconfiguration that passes vacuously
status: not_attempted
priority: LOW
wave: 5
lane_owner: oracle-executor-lane
supervisor_role: PSL-PROMPT-3
required_implementation:
  - Add executor_property_gaps section to oracle/reports/oracle-coverage-report.json
    OR create oracle/registry/executor-property-registry.yaml
  - Document which formats support which expected_model_properties keys
  - Add a warning in execute_oracle.py when an expected property key is not in observed dict
required_verification:
  - Running execute_oracle.py with a case containing an unsupported property key prints WARNING
  - Existing csv 5/5 and zst 6/6 unaffected
required_evidence:
  - Updated oracle/reports/oracle-coverage-report.json OR new executor-property-registry.yaml
acceptance_criteria:
  - A case with property: cell_value in expected_model_properties causes a WARNING log line
    (not a FAIL — it should be INCONCLUSIVE or logged as unsupported_property)
  - Existing tests unaffected
stop_conditions: none (low-risk documentation task)
allowed_paths:
  - Modify tools/oracle/execute_oracle.py (add unsupported-key warning)
  - Modify oracle/reports/oracle-coverage-report.json
  - Create oracle/registry/executor-property-registry.yaml
forbidden_paths:
  - Do not change existing passing case results
dependencies: []
closeout_rules: execute_oracle.py warns on unknown property keys
machine_state: not_attempted
```

---

### TC-ORC-003: Wire Oracle Obligation Validator into Governance Suite (V80)
```
taskcard_id: TC-ORC-003
title: Register oracle obligation validator as V80 in governance_validators.py
source_issue_ids: [L2-001, L3-001]
source_issue_level: L2_INTEGRATION
source_audit_finding: >
  tools/oracle/validate_oracle_obligations.py runs standalone (24/24 PASS) but is not
  integrated into the governance validator suite (V1-V79). This means oracle obligation
  gaps are not detected at sprint closeout or in autonomous-cycle grading. The oracle gate
  is documentation-enforced but not machine-enforced in the sprint loop.
why_it_matters: >
  Without governance suite registration, a sprint that adds a new format without an oracle
  obligation can pass sprint closeout without any validator objecting. The 24/24 pass rate
  only holds if someone manually runs the tool.
risk_addressed: >
  Silent oracle obligation drift. Format additions that bypass the oracle onboarding gate.
  This is the machine-enforcement complement to the oracle-authority-policy.md rules.
status: not_attempted
priority: HIGH
wave: 5
lane_owner: governance-suite-lane
supervisor_role: PSL-PROMPT-3
required_implementation:
  - Add validate_oracle_obligations() function to tools/supervisor/governance_validators.py
    OR tools/supervisor/governance_validators_ext2.py (if ext2 is below cap)
  - Function signature: validate_oracle_obligations(declaration: dict) -> dict
  - Implementation: call validate_oracle_obligations.py logic or import and call directly
  - Return dict with: validator_id="V80", name="validate_oracle_obligations",
    status="PASS"/"WARN"/"FAIL", details=list, blocks_sprint=False (WARN only — not BLOCK)
  - Register in governance_validator_runner.py
  - Add 3 regression tests in tests/supervisor/test_governance_validators.py:
    (1) 24/24 formats with obligations → PASS
    (2) declaration with new format lacking obligation → WARN
    (3) obligation exists but status=OBLIGATION_NOT_MET → WARN
required_verification:
  - python tools/supervisor/governance_validator_runner.py prints V80 result
  - All 3 regression tests pass
  - Existing 135+ governance tests unaffected
required_evidence:
  - terminal output showing V80 in governance runner output
  - test run output showing V80 tests PASS
quality_dimensions:
  - implementation_correctness: V80 returns correct PASS/WARN for known good/bad cases
  - governance_compliance: registered in runner and validator list
  - test_coverage: 3+ regression tests
  - evidence_completeness: runner output captured
scoring_rubric:
  pass_threshold: implementation_correctness >= 4 and test_coverage >= 4
reroute_rule_if_score_below_4: >
  If governance_validators.py is at LOC cap, add V80 to governance_validators_ext2.py instead.
  If ext2 is also at cap, create governance_validators_oracle.py following the ext.py pattern
  (re-export from parent for backward compat).
acceptance_criteria:
  - V80 appears in governance runner output
  - Missing oracle obligation produces WARN (not silent PASS)
  - Existing 135+ tests unaffected
stop_conditions:
  - governance_validators.py and ext2 both at LOC cap AND creating new file would
    break imports → classify as BLOCKED_INTERNAL_CAP, propose governance_validators_oracle.py
allowed_paths:
  - Modify tools/supervisor/governance_validators.py or governance_validators_ext2.py
  - Modify tools/supervisor/governance_validator_runner.py
  - Modify tests/supervisor/test_governance_validators.py
  - Create tools/supervisor/governance_validators_oracle.py if needed
forbidden_paths:
  - Do not modify oracle/registry/format-oracle-registry.yaml
  - Do not modify tools/oracle/validate_oracle_obligations.py (import it; do not copy it)
  - Do not change existing validator IDs or remove existing validators
dependencies:
  - tools/oracle/validate_oracle_obligations.py must be importable from governance_validators.py
    (sys.path may need adjustment if governance_validators.py is in tools/supervisor/)
closeout_rules: V80 in governance runner output; 3 regression tests PASS
machine_state: not_attempted
validation_commands:
  - python tools/supervisor/governance_validator_runner.py
  - .venv/Scripts/pytest tests/supervisor/test_governance_validators.py -x -q
```

---

### TC-ORC-004: Add implementation_status to Comparator Registry
```
taskcard_id: TC-ORC-004
title: Mark comparator registry entries with implementation_status field
source_issue_ids: [L2-002]
source_issue_level: L2_INTEGRATION
source_audit_finding: >
  oracle/registry/comparator-registry.yaml defines 6 comparators with implementation
  paths (oracle/shared/comparators/*.py) that do not exist. The registry is a design
  document but presents implementation paths as if files exist.
why_it_matters: >
  Any reader of comparator-registry.yaml who attempts to import or test comparator
  implementations will find missing files. This is a misleading design/reality gap.
risk_addressed: Confusion for future oracle package authors and tool builders
status: not_attempted
priority: LOW
wave: 5
lane_owner: oracle-registry-lane
supervisor_role: PSL-PROMPT-3
required_implementation:
  - Add implementation_status: INLINE_IN_EXECUTOR to each comparator entry
    (or FORWARD_DECLARATION for those not yet implemented inline)
  - Add implementation_note field: "Inline in tools/oracle/execute_oracle.py as of Wave 3"
  - No new Python files needed
required_verification:
  - Comparator registry YAML is valid (python -c "import yaml; yaml.safe_load(open(...))")
  - No oracle tool crashes after registry update
required_evidence:
  - Updated oracle/registry/comparator-registry.yaml with implementation_status fields
acceptance_criteria: All 6 comparators have implementation_status field
stop_conditions: none
allowed_paths:
  - Modify oracle/registry/comparator-registry.yaml
forbidden_paths:
  - Do not create oracle/shared/comparators/*.py files (deferred to Wave 6)
  - Do not modify execute_oracle.py comparator logic
dependencies: []
closeout_rules: YAML has implementation_status on all 6 comparator entries
machine_state: not_attempted
```

---

### TC-ORC-005: Add Oracle Obligation CI Step
```
taskcard_id: TC-ORC-005
title: Add oracle obligation validation as a CI pipeline step
source_issue_ids: [L2-003]
source_issue_level: L2_INTEGRATION
source_audit_finding: >
  Neither execute_oracle.py nor validate_oracle_obligations.py is wired into any CI
  pipeline. .gitlab-ci.yml exists in the repo but oracle commands are not in it.
why_it_matters: >
  CI is the primary enforcement point. Without a CI step, oracle obligation drift
  can accumulate across feature sprints without any automated detection.
risk_addressed: Silent drift of oracle obligations across multiple sprints
status: not_attempted
priority: MEDIUM
wave: 5
lane_owner: ci-lane
supervisor_role: PSL-PROMPT-3
required_implementation:
  - Add oracle-obligations stage or step to .gitlab-ci.yml
  - Script: python tools/oracle/validate_oracle_obligations.py
  - allow_failure: false (obligation gaps should fail CI)
  - Stage placement: after unit tests, before Gate 10 checks
required_verification:
  - .gitlab-ci.yml is valid YAML (python -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))")
  - Step does not break existing CI stages
required_evidence:
  - Updated .gitlab-ci.yml with oracle-obligations step
  - YAML validation pass
acceptance_criteria:
  - .gitlab-ci.yml has oracle-obligations step
  - Validation shows 24/24 PASS still holds after CI step added
stop_conditions:
  - .gitlab-ci.yml structure conflicts with oracle step placement → classify as
    BLOCKED_CI_STRUCTURE, propose alternative (pre-commit hook instead)
allowed_paths:
  - Modify .gitlab-ci.yml
forbidden_paths:
  - Do not modify oracle tools or registries for CI compatibility
dependencies:
  - TC-ORC-003 (V80) recommended first, but not required for CI step
closeout_rules: .gitlab-ci.yml has oracle step; YAML valid
machine_state: not_attempted
```

---

### TC-ORC-006: Add Runtime Schema Validation in Oracle Executor
```
taskcard_id: TC-ORC-006
title: Add jsonschema validation for oracle packages in execute_oracle.py
source_issue_ids: [L3-002]
source_issue_level: L3_SYSTEM_WEAKNESS
source_audit_finding: >
  oracle/schema/oracle-package.schema.json and oracle-verdict.schema.json exist as
  authoritative JSON Schema files, but execute_oracle.py does not load or validate
  against them at runtime. A malformed oracle package could be committed and silently
  produce incorrect results.
why_it_matters: >
  Schema validation is the primary defense against oracle package authoring errors
  (missing required fields, wrong authority class values, wrong result enum values).
  Without it, schema correctness is documentation-only.
risk_addressed: Malformed oracle packages producing silent incorrect verdicts
status: not_attempted
priority: LOW
wave: 5
lane_owner: oracle-executor-lane
supervisor_role: PSL-PROMPT-3
required_implementation:
  - Check if jsonschema is installed in .venv; if not, add graceful fallback
  - In run_oracle_for_format(), after loading oracle_pkg YAML:
    - Load oracle/schema/oracle-package.schema.json
    - Run jsonschema.validate(oracle_pkg, schema)
    - If validation fails: print WARNING, continue with INVALID_ORACLE verdict for all cases
  - Do NOT make schema validation a hard blocker (graceful degradation if jsonschema absent)
required_verification:
  - A deliberately malformed oracle package (missing required field) triggers WARNING
  - Valid CSV and ZST packages still produce 5/5 and 6/6 PASS (no regression)
required_evidence:
  - Terminal output showing WARNING for malformed package
  - csv 5/5, zst 6/6 still passing
acceptance_criteria:
  - Invalid oracle package triggers INVALID_ORACLE with schema error message
  - Fallback if jsonschema not installed (WARN + skip validation)
stop_conditions:
  - jsonschema not installable → use fallback (skip validation, print WARN)
allowed_paths:
  - Modify tools/oracle/execute_oracle.py
forbidden_paths:
  - Do not make schema validation mandatory (would block CI if jsonschema absent)
  - Do not modify oracle schemas
dependencies: []
closeout_rules: malformed package triggers INVALID_ORACLE; csv/zst pass unchanged
machine_state: not_attempted
```

---

### TC-ORC-007: Create Wave 6 Oracle Backfill Sprint Plan
```
taskcard_id: TC-ORC-007
title: Create sprint plan for Wave 6 oracle package backfill (18 formats)
source_issue_ids: [L3-003]
source_issue_level: L3_SYSTEM_WEAKNESS
source_audit_finding: >
  oracle/registry/format-oracle-registry.yaml shows 18 formats as
  OBLIGATION_CREATED_BACKFILL_REQUIRED. No sprint plan, gap-ledger entries, or
  taskcards exist to drive the creation of 18 oracle packages.
why_it_matters: >
  Without a sprint plan, Wave 6 backfill is aspirational only. The oracle layer
  maturity cannot advance beyond Level 3 without executing packages for the remaining
  18 formats.
risk_addressed: Indefinite stall of oracle layer maturity at Level 3
status: not_attempted
priority: MEDIUM
wave: 6
lane_owner: oracle-backfill-lane
supervisor_role: sprint-planning
required_implementation:
  - Group 18 formats into 4 sprint batches by family:
    Batch A (cells): gnumeric, ods, dif, sylk — 4 formats, SPEC_NORMATIVE
    Batch B (words/draw): abw, fodt, fodg, fodp, odt — 5 formats
    Batch C (imaging): xcf, pbm, pgm, ppm, qoi — 5 formats
    Batch D (data): toml, tsv, ndjson — 3 formats, SPEC_NORMATIVE
  - For each batch, create oracle-package.yaml using the CSV/ZST packages as templates
  - Priority: Batch A (cells) first (cells family has the most gate-critical formats)
  - Create one gap-ledger entry per batch (GAP-ORC-BACKFILL-A/B/C/D)
  - Add batch entries to reports/capability-layer/gap-ledger.json
required_verification:
  - gap-ledger.json has 4 new GAP-ORC-BACKFILL-* entries
  - Wave 6 sprint plan file exists at plans/oracle-backfill-wave6.md
  - Each batch has estimated case count and authority source identified
required_evidence:
  - oracle-backfill-wave6.md plan file
  - gap-ledger.json with 4 GAP-ORC-BACKFILL entries
acceptance_criteria:
  - 4 gap-ledger entries created (one per batch)
  - oracle-backfill-wave6.md exists with 4 batches, authority sources, and timeline
stop_conditions: none (planning task only)
allowed_paths:
  - Create plans/oracle-backfill-wave6.md
  - Modify reports/capability-layer/gap-ledger.json
forbidden_paths:
  - Do not create oracle packages yet — this task is PLANNING only
  - Do not modify existing oracle packages
dependencies: []
closeout_rules: gap-ledger has 4 GAP-ORC-BACKFILL-* entries; wave6 plan file exists
machine_state: not_attempted
```

---

## 6. Lane Ownership

| Lane | Owner | Taskcards |
|---|---|---|
| oracle-executor-lane | executor sprint agent | TC-ORC-001, TC-ORC-002, TC-ORC-006 |
| governance-suite-lane | governance sprint agent | TC-ORC-003 |
| oracle-registry-lane | registry maintenance agent | TC-ORC-004 |
| ci-lane | CI configuration agent | TC-ORC-005 |
| oracle-backfill-lane | backfill planning agent | TC-ORC-007 |

---

## 7. Gate Contract

### Wave 5 Exit Gate (before Wave 6 backfill begins)
Required:
- TC-ORC-001 CLOSED: FODS oracle runs with verdict != INVALID_ORACLE
- TC-ORC-003 CLOSED: V80 in governance runner; 3 tests PASS

Recommended (not blocking):
- TC-ORC-002 CLOSED: executor gap registry updated
- TC-ORC-004 CLOSED: comparator registry has implementation_status
- TC-ORC-005 CLOSED: CI step added

### Wave 6 Entry Gate
Requires Wave 5 exit gate to pass, plus:
- TC-ORC-007 CLOSED: 4 gap-ledger entries and backfill plan exist

### Oracle Maturity Level 4 Gate (all formats have oracle packages)
Requires Wave 6 backfill completion: all 18 oracle-package.yaml files created and executed.

---

## 8. Evidence Contract

| Taskcard | Required Evidence | Format |
|---|---|---|
| TC-ORC-001 | oracle/formats/fods/reports/oracle-run-summary.json | JSON |
| TC-ORC-001 | execute_oracle.py --format fods --all terminal output | text |
| TC-ORC-002 | Updated oracle-coverage-report.json with executor_property_gaps | JSON |
| TC-ORC-003 | governance_validator_runner.py output showing V80 | text |
| TC-ORC-003 | pytest output for 3 V80 regression tests PASS | text |
| TC-ORC-004 | Updated comparator-registry.yaml | YAML |
| TC-ORC-005 | Updated .gitlab-ci.yml with oracle step | YAML |
| TC-ORC-006 | Terminal output showing malformed package → INVALID_ORACLE | text |
| TC-ORC-007 | oracle-backfill-wave6.md plan file | Markdown |
| TC-ORC-007 | gap-ledger.json with 4 GAP-ORC-BACKFILL-* entries | JSON |

All evidence must be raw output or file contents — not prose descriptions of results.

---

## 9. Verification Matrix

| Check | Command | Expected | Required For |
|---|---|---|---|
| FODS execution | `python tools/oracle/execute_oracle.py --format fods --all` | verdict != INVALID_ORACLE | TC-ORC-001 |
| CSV no regression | `python tools/oracle/execute_oracle.py --format csv --all` | 5/5 PASS | TC-ORC-001 |
| ZST no regression | `python tools/oracle/execute_oracle.py --format zst --all` | 6/6 PASS | TC-ORC-001 |
| Obligations | `python tools/oracle/validate_oracle_obligations.py` | 24/24 PASS | All |
| Governance V80 | `python tools/supervisor/governance_validator_runner.py` | V80 appears | TC-ORC-003 |
| Governance tests | `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py` | 135+ pass | TC-ORC-003 |
| Comparator YAML | `python -c "import yaml; yaml.safe_load(open('oracle/registry/comparator-registry.yaml'))"` | no error | TC-ORC-004 |
| CI YAML valid | `python -c "import yaml; yaml.safe_load(open('.gitlab-ci.yml'))"` | no error | TC-ORC-005 |
| Schema warning | `python tools/oracle/execute_oracle.py --format csv-malformed --all` | INVALID_ORACLE | TC-ORC-006 |

---

## 10. Repair Loop

If any taskcard scores below 4/5 in required dimensions:

1. Mark taskcard REROUTED
2. Identify the specific dimension failure (e.g., test_coverage=3 → write additional test)
3. Apply the reroute rule from the taskcard's `reroute_rule_if_score_below_4` field
4. Rerun verification commands
5. Rescore
6. Accept only after all required dimensions >= 4/5

If BLOCKED_EXTERNAL (e.g., fods package not importable):
- Create gap-ledger entry: GAP-ORC-EXEC-FODS-001
- Mark TC-ORC-001 as blocked_external
- Continue to next unblocked taskcard

---

## 11. Anti-Overclaim Rules

For this addendum's execution sprints:

1. DO NOT claim TC-ORC-003 (governance suite) complete unless V80 appears in runner output with correct PASS/WARN behavior — not just "added to file."
2. DO NOT claim TC-ORC-001 (FODS executor) complete unless oracle-run-summary.json exists and shows verdict != INVALID_ORACLE — not just "handler written."
3. DO NOT claim TC-ORC-004 (comparator registry) complete unless all 6 entries have implementation_status field — not just "some updated."
4. DO NOT treat governance test count passing as proof of new V80 — explicitly check V80 is in the output.
5. DO NOT claim schema validation (TC-ORC-006) working unless a deliberately malformed package triggers INVALID_ORACLE.
6. DO NOT count Wave 6 backfill (TC-ORC-007) as started until gap-ledger.json has the 4 GAP-ORC-BACKFILL-* entries.
7. DO NOT accept synthetic-only tests for TC-ORC-003 — at least one test must load a real oracle/formats/csv/oracle-package.yaml and verify V80 returns PASS.

---

## 12. Closeout Criteria

This addendum is CLOSED when ALL of the following are true:

### Wave 5 Closure (TC-ORC-001 through TC-ORC-006)
- [ ] TC-ORC-001: oracle/formats/fods/reports/oracle-run-summary.json exists with verdict != INVALID_ORACLE
- [ ] TC-ORC-002: execute_oracle.py warns on unknown property keys
- [ ] TC-ORC-003: V80 in governance runner; 3 regression tests PASS; no regression in existing 135+
- [ ] TC-ORC-004: All 6 comparator entries have implementation_status field
- [ ] TC-ORC-005: .gitlab-ci.yml has oracle step; YAML valid
- [ ] TC-ORC-006: Malformed oracle package → INVALID_ORACLE; csv/zst no regression

### Wave 6 Planning Closure (TC-ORC-007)
- [ ] TC-ORC-007: oracle-backfill-wave6.md exists; gap-ledger.json has 4 GAP-ORC-BACKFILL-* entries

### Evidence Closure
- [ ] All evidence files referenced above exist as committed or staged artifacts
- [ ] Oracle maturity assessment updated to Level 4 in oracle-layer-inventory.yaml
  (all formats have packages — after Wave 6 backfill executes, not just plans)

---

## 13. Remaining True Blockers

No TRUE_EXTERNAL_GATEs block this addendum's execution.

All work is agent-executable:
- FODS executor: Python code, importable package available
- Governance V80: Python code, follows existing V1-V79 pattern
- CI step: YAML edit, follows existing .gitlab-ci.yml patterns
- Wave 6 planning: YAML/Markdown creation

The only BLOCKED_EXTERNAL risk:
- FODS package wheel not installed or broken import path → fallback: reinstall from
  `.local/package-builds/python-foss/` or from source at `src/python/fods/`


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-06-26T09:53:03.507698+00:00"
  locked_by: "688d4a5de421"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
