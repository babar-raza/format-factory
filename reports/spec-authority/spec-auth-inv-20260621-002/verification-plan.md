# Specs Authority Layer — Verification Plan
**Run ID:** spec-auth-inv-20260621-002
**Date:** 2026-06-21

All verification gates ordered P0 → P3.
Blocking gates must pass before the next sprint proceeds.

---

## Gate V0-001: SAL Output File Integrity (P0 — BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove GAP-SA-NEW-001 is resolved: single-format run does not overwrite all-format latest |
| **Command** | `python tools/specification-authority-layer/sal_master_runner.py --all --output-dir .local/sal-output/` |
| **Then:** | `python tools/specification-authority-layer/sal_master_runner.py --format zst --output-dir .local/sal-output/` |
| **Expected result** | `sal-facts-latest.json` has ≥20 format entries after both runs |
| **Failure interpretation** | GAP-SA-NEW-001 not fixed; single-format still overwrites all-format |
| **Evidence file** | `reports/spec-authority/<run_id>/evidence/v0-001-sal-integrity.json` |
| **Blocking** | YES |

```bash
# Verification command:
python tools/specification-authority-layer/sal_master_runner.py --all
python tools/specification-authority-layer/sal_master_runner.py --format zst
python -c "import json; d=json.loads(open('.local/sal-output/sal-facts-latest.json').read()); \
           assert len(d['results']) >= 20, f'Only {len(d[\"results\"])} formats found'; \
           print('PASS: all-format file intact')"
```

---

## Gate V0-002: Validator Path Consistency (P0 — BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove V37 and V47 read from the same SAL output |
| **Command** | Static check: inspect source code paths |
| **Expected result** | Both validators use same `sal_path` value |
| **Failure interpretation** | GAP-SA-NEW-002 not fixed |
| **Evidence file** | `reports/spec-authority/<run_id>/evidence/v0-002-validator-paths.txt` |
| **Blocking** | YES |

```bash
grep -n "sal_path\|sal-facts-latest" tools/supervisor/governance_validators.py | \
  grep -E "validate_spec_fact_authority_chain|validate_spec_fact_refs_in_sal_output" -A2
# Expected: both functions show same path
```

---

## Gate V1-001: spec_verifier Anti-Bypass (P1 — BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove spec_verifier.py is called from SAL runner and rejects no-source_id facts |
| **Command** | `python -m pytest tests/specification-authority-layer/test_sal_verifier_adversarial.py -v` |
| **Expected result** | 14/14 PASS (already passing) |
| **Additional test** | New test: inject workbench entry with source_id=null → SAL runner excludes it |
| **Failure interpretation** | Anti-bypass not enforced in production path |
| **Evidence file** | Test output |
| **Blocking** | YES |

---

## Gate V1-002: GAP-INT-002 Traceability Test (P1 — BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove all product source FACT-* refs resolve in SAL |
| **Command** | `python -m pytest tests/specification-authority-layer/test_gap_int_002_product_source_fact_refs.py -v` |
| **Expected result** | 13/13 PASS (currently 12/13 — PBM failure must be fixed) |
| **Failure interpretation** | Source code cites fact IDs not in SAL; traceability broken |
| **Evidence file** | Test output |
| **Blocking** | YES |

---

## Gate V1-003: Spec Source Acquired Validator (P1 — BLOCKING for new formats)

| Field | Value |
|-------|-------|
| **Purpose** | Prove V48 warns when PRODUCT_SOURCE item for format with sha256_snapshot=null is declared |
| **Command** | `python -m pytest tests/supervisor/test_governance_validators.py::TestV48SpecSourceAcquired -v` |
| **Expected result** | WARN result returned; blocks_sprint=False initially |
| **Failure interpretation** | V48 not wired or not detecting null sha256 |
| **Evidence file** | Test output |
| **Blocking** | YES (for new formats acquiring spec) |

---

## Gate V1-004: Full SAL Test Suite (P1 — BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove 191 collected SAL tests pass |
| **Command** | `python -m pytest tests/specification-authority-layer/ -v --timeout=300` |
| **Expected result** | 191/191 PASS (currently 190/191 pass + timeout issues) |
| **Failure interpretation** | Core SAL functionality broken |
| **Evidence file** | `reports/spec-authority/<run_id>/evidence/v1-004-sal-tests.txt` |
| **Blocking** | YES (must achieve ≥190/191) |

---

## Gate V2-001: Proof Graph Population (P2 — NON-BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove bidirectional fact-product linkage for FODS |
| **Command** | `python tools/traceability/populate_proof_graph.py --format fods` |
| **Expected result** | `.local/capability-proof-graph/fods-traceability.json` created; FACT-FODS-001 has ≥1 product_file and ≥1 test_file |
| **Failure interpretation** | Traceability not populated |
| **Evidence file** | `.local/capability-proof-graph/fods-traceability.json` |
| **Blocking** | NO (P2 — warning only) |

---

## Gate V2-002: Behavioral Fact Count (P2 — NON-BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove behavioral fact count is tracked separately from structural enumeration |
| **Command** | `python tools/specification-authority-layer/fact_coverage_report.py --format fods --show-categories` |
| **Expected result** | Report shows behavioral_count ≥ 50 for FODS |
| **Failure interpretation** | fact_category field not added to schema |
| **Evidence file** | Coverage report output |
| **Blocking** | NO |

---

## Gate V2-003: Staleness Detection Integration (P2 — NON-BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove refresh_check.py is called in autonomous cycle and warns on stale spec |
| **Command** | Set FODS spec-index.yaml `stale: true`; run autonomous_cycle.py Step 0a; assert warning |
| **Expected result** | Cycle log contains "WARNING: stale spec detected" |
| **Failure interpretation** | GAP-SA-NEW-008 not fixed |
| **Evidence file** | Cycle log excerpt |
| **Blocking** | NO (must restore spec-index.yaml stale: false after test) |

---

## Gate V3-001: Pilot Acquisition Rerun (P1 — BLOCKING for pilot)

| Field | Value |
|-------|-------|
| **Purpose** | Prove full acquisition authority chain works end-to-end for ZST |
| **Command** | See pilot-rerun-plan.md |
| **Expected result** | ZST facts from spec text → verified → used in task packet → task closes with matching spec refs |
| **Failure interpretation** | Authority chain broken for ZST |
| **Evidence file** | pilot-rerun-plan.md section 7 |
| **Blocking** | YES for pilot completion |

---

## Gate V3-002: Governance Validator Suite (P1 — BLOCKING)

| Field | Value |
|-------|-------|
| **Purpose** | Prove all existing governance validators related to SAL still pass |
| **Command** | `python -m pytest tests/supervisor/test_governance_validators.py -v --timeout=60` |
| **Expected result** | All SAL-related validators pass (V13, V19, V37, V47 at minimum) |
| **Evidence file** | Test output |
| **Blocking** | YES |

---

## Negative Tests Required

| Test | Expected Behavior | Status |
|------|------------------|--------|
| FACT-XYZ-999 (nonexistent) cited in declaration | V47 FAILS sprint | Not currently tested |
| Cross-format fact: FACT-FODS-001 cited in ZST item | V37 WARN; V47 may pass (fact exists) | Not tested |
| Workbench fact with source_id=null | SAL runner excludes it after MVR-3 | Not currently tested |
| Single-format SAL run after all-format run | all-format latest unchanged | Needed for MVR-1 |
| spec-index.yaml stale=true | refresh_check.py warns in cycle | Needed for MVR-FPR-3 |
| ABW format PRODUCT_SOURCE in declaration | V48 WARN (sha256=null; status=unavailable) | Needed for MVR-4 |

---

## Pilot Rerun Gates (see pilot-rerun-plan.md for full detail)

| Step | Gate | Command |
|------|------|---------|
| 1 | Spec loaded with SHA-256 | `python tools/spec-cache/refresh_check.py --format zst` |
| 2 | Facts verifiable against spec text | `python tools/specification-authority-layer/run_fact_verification.py --format zst` |
| 3 | Facts emitted with source_id | `jq '.results[0].spec_facts[0].source_id' .local/sal-output/sal-facts-zst.json` |
| 4 | V47 passes for ZST task declaration | Inject test declaration with FACT-ZST-001; assert PASS |
| 5 | Deterministic rerun | Run twice; compare outputs byte-for-byte |

---

## Final Verdict Format

Sprint producing healing repairs must report:

```
SPEC_AUTHORITY_HEALING_SPRINT_VERDICT:
  GAP_SA_NEW_001: RESOLVED | PARTIAL | UNRESOLVED
  GAP_SA_NEW_002: RESOLVED | PARTIAL | UNRESOLVED
  GAP_SA_NEW_003: RESOLVED | PARTIAL | UNRESOLVED
  GAP_SA_NEW_004: RESOLVED | PARTIAL | UNRESOLVED
  PILOT_RERUN_ZST: PASS | FAIL | SKIPPED
  GOVERNANCE_TESTS: N/M PASS
  SAL_TESTS: N/M PASS
  OVERALL: HEALING_COMPLETE | PARTIAL_HEALING | HEALING_BLOCKED
```
