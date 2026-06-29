# Certification Audit Layer

```yaml
layer_metadata:
  layer_id: L28
  canonical_name: Certification Audit Layer
  canonical_slug: certification-audit-layer
  permanent_plan_path: plans/layers/certification-audit-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "16b454ca"
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 3
  maturity_target: 4
  current_stage: GOVERNED_OPERATION
  current_owner: null
  agent_type: null
  session_id: null
  active_sprint: null
  active_taskcards: []
  ready_taskcards: [TC-CERT-L-003]
  blocked_taskcards: []
  completed_taskcards: [TC-CERT-L-001, TC-CERT-L-002]
  dependencies: [L05, L06, L07]
  upstream_layers: [L05, L06, L07]
  downstream_layers: [L18]
  skill_ids: []
  command_ids: []
  evidence_paths:
    - reports/certification/portfolio-certification-matrix.json
    - reports/certification-integration/report-integrity-audit.yaml
    - reports/certification-integration/product-verdict-review.yaml
    - reports/certification-integration/gap-reconciliation-map.yaml
  last_started_at: "2026-06-28"
  last_progress_at: "2026-06-28"
  last_updated_at: "2026-06-28"
  last_verified_at: "2026-06-28"
  last_verified_revision: "16b454ca"
  next_task_id: TC-CERT-L-003
  next_action: "Register certification tools as skills; add governance validators V87+"
  handoff_id: HO-008
```

---

## 1. Layer Metadata

See YAML block above.

## 2. Authority and Purpose

The Certification Audit Layer provides **portfolio-wide quality certification** for all
Format Factory format packages. It owns:

- The certification tool suite (`tools/certification/` — 9 tools)
- Per-format certification reports (`reports/certification/{format}/` — 9 report types)
- The portfolio certification matrix (`reports/certification/portfolio-certification-matrix.json`)
- The certification dashboard generator (`tools/certification/certification_dashboard.py`)
- Certification verdict taxonomy: CERTIFIED, CERTIFIED_WITH_KNOWN_GAPS, NOT_CERTIFIED, IN_PROGRESS, NOT_STARTED

**Current status:** ALL 20 Python FOSS formats at CERTIFIED as of 2026-06-28.

## 3. Scope

- `tools/certification/` — 9 certification tools (inventory_extractor, stub_detector, exception_coverage_checker, assertion_quality_scorer, dotnet_assertion_scorer, certification_dashboard, generate_exception_tests, fix_weak_assertions, generate_security_tests)
- `reports/certification/{format}/` — per-format audit reports (20 format directories)
- `reports/certification/portfolio-certification-matrix.json` — portfolio verdicts
- `reports/certification/certification-report.md` — human-readable portfolio report
- `tests/certification/` — integration and integrity tests (456 tests)

## 4. Explicit Non-Scope

- Does NOT own format product source (L06)
- Does NOT own test infrastructure (L07) — certification audits test quality, does not own tests
- Does NOT own oracle verification (L05) — oracle is an input dimension to certification
- Does NOT own the canonical gap ledger (L03) — certification findings reconcile with gaps but do not own the ledger

## 5. Owned Decisions

- Certification dimension taxonomy (9 dimensions: api_contract, traceability, stubs, exceptions, oracle, test_quality, roundtrip, package, consumer)
- Verdict derivation logic (CERTIFIED requires all dimensions PASS or NOT_APPLICABLE)
- Per-format report schema and structure
- Tool contracts (CLI interfaces, exit codes, output schemas)

## 6. Dependencies

| Dependency | Direction | Description |
|------------|-----------|-------------|
| L05 (Oracle) | Upstream | Oracle alignment is one of 9 certification dimensions |
| L06 (Product Source) | Upstream | API contract extraction requires product source |
| L07 (Tests) | Upstream | Assertion quality scoring requires test files |
| L18 (Release Pipeline) | Downstream | Certification verdicts inform release readiness |

## 7. Tasks

| Task ID | Status | Description |
|---------|--------|-------------|
| TC-CERT-L-001 | CLOSED | Validate all 9 certification tools individually |
| TC-CERT-L-002 | CLOSED | Create integration tests (456 tests, all pass) |
| TC-CERT-L-003 | TODO | Register certification tools as skills in skill-registry.yaml |

## 8. Evidence

- **Tool verification:** `reports/certification-integration/tool-verification.yaml`
- **Report integrity:** `reports/certification-integration/report-integrity-audit.yaml`
- **Verdict review:** `reports/certification-integration/product-verdict-review.yaml`
- **Gap reconciliation:** `reports/certification-integration/gap-reconciliation-map.yaml`
- **Baseline:** `reports/certification-integration/baseline.yaml`
- **Integration tests:** `tests/certification/test_tool_pipeline.py` (9 tests, all pass)
- **Integrity tests:** `tests/certification/test_report_integrity.py` (447 tests, all pass)

## 9. Findings

| Finding ID | Severity | Status | Description |
|------------|----------|--------|-------------|
| CERT-DASHBOARD-001 | P2 | FIXED | NOT_APPLICABLE treated as non-PASS in verdict logic (8 false downgrades) |
| CERT-TOOL-001 | P3 | DOCUMENTED | `_rel()` crashes on output paths outside repo root |
| CERT-TOOL-002 | P3 | DOCUMENTED | Exception coverage uses naive text search (not AST) |
| CERT-TOOL-003 | P3 | DOCUMENTED | .NET assertion scorer uses regex (not Roslyn AST) |
| CERT-TOOL-004 | P3 | DOCUMENTED | generate_exception_tests.py is not idempotent |
| CERT-TOOL-005 | P3 | DOCUMENTED | fix_weak_assertions.py is not idempotent |
| CERT-TOOL-006 | P3 | DOCUMENTED | generate_security_tests.py is not idempotent |

## 10. Gaps

- **GAP-CERT-SKILL-001:** Certification tools not registered in skill-registry.yaml (TC-CERT-L-003)
- **GAP-CERT-VALIDATOR-001:** No governance validators enforce certification report consistency

## 11. Maturity Assessment

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Tools exist and parse | 4/4 | 9 tools, all valid Python |
| Tools produce correct output | 4/4 | Verified for all 20 formats |
| Integration tests exist | 3/4 | 456 tests pass; no negative/mutation tests yet |
| Gap reconciliation clean | 4/4 | 0 material findings without canonical gaps |
| Portfolio verdicts justified | 4/4 | 20/20 CERTIFIED (after CERT-DASHBOARD-001 fix) |
| Supervisor integration | 2/4 | No skill registration, no governance validators |

**Overall maturity: 3/4** (operational but missing skill registration and validators)

## 12. Lifecycle

```
NOT_STARTED → DISCOVERY → PLAN_HARDENING → EXECUTION_IN_PROGRESS → GOVERNED_OPERATIONAL
                                                                      ↑ (current)
```

## 13. Certification Pipeline

```
Source code (src/python/, src/net/)
    ↓
inventory_extractor.py → api-contract.json
stub_detector.py → stub-audit.json
exception_coverage_checker.py → exception-audit.json
assertion_quality_scorer.py → assertion-quality.json
dotnet_assertion_scorer.py → dotnet-assertion-quality.json
    ↓
    + oracle-alignment.json (from L05)
    + traceability-audit.json (from plan execution)
    + roundtrip-audit.json (from plan execution)
    + package-proof.json (from plan execution)
    + consumer-proof.json (from plan execution)
    ↓
certification_dashboard.py → portfolio-certification-matrix.json + certification-report.md
```
