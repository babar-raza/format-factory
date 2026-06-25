# Evidence and Supervisor Gate Audit
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## 1. Evidence Declaration — Required Fields Assessment

### What the Contract Requires (supervisor-worker-contract.md)

| Field | Required? | Spec Authority Relevance |
|-------|----------|--------------------------|
| `gap_ledger_ref` | YES | Identifies the gap being closed — NOT a spec authority citation |
| `capability_ref` | YES (or gap_ledger_ref) | Identifies the capability — NOT a spec authority citation |
| `tests_run` | YES | Test count — NOT spec-backed test requirement |
| `test_results` | YES | Pass/fail count — NOT verified against spec facts |
| `worker_self_verdict` | YES | Worker assessment — advisory |
| `evidence_paths` | YES | Artifact paths — NOT required to include spec-cache artifacts |
| `changed_files` | YES | Modified files list — NOT checked for FACT-* citations |
| **`spec_fact_refs`** | **NO — NOT IN REQUIRED FIELDS** | **CRITICAL GAP** |
| `exception_classification` | NO (optional) | Allows bypass of spec authority gates |

**Verdict**: Evidence declaration schema does NOT mandate spec_fact_refs. Any sprint can achieve ACCEPTED verdict without citing a single spec fact.

---

## 2. TC-GUARD-001 Assessment

**Location**: `tools/supervisor/autonomous_cycle.py` Step 2d3

**Current Logic**:
```python
has_authority = (
    item.get("gap_ledger_ref") or
    item.get("capability_ref") or
    item.get("spec_fact_refs")
)
if not has_authority:
    guard001_violations.append(item)
```

**Finding**: OR logic means gap_ledger_ref ALONE satisfies the guard. spec_fact_refs is never required.

**Live Evidence** — zst-frame-count-coverage-20260622 sprint declaration:
```yaml
gap_ledger_ref: GAP-ZST-FOSS-FRAME-COUNT-001
spec_fact_refs: null
verdict: ACCEPTED
```

TC-GUARD-001 passed with zero spec authority citations.

**Required Logic**:
```python
has_authority = (
    item.get("gap_ledger_ref") and
    (item.get("spec_fact_refs") or item.get("exception_classification"))
)
```

---

## 3. V13 (validate_spec_fact_refs_wired) Assessment

**Location**: `tools/supervisor/governance_validators.py`, line 912

**Current Behavior**:
- FIRES when: spec_fact_refs is PROVIDED AND does not match sal-facts-{format}.json entries → FAIL (blocks_sprint=True)
- DOES NOT FIRE when: spec_fact_refs is ABSENT/null → no enforcement
- PASSES when: exception_classification is any valid value → bypasses check entirely

**Exception Classifications That Bypass V13**:
| Classification | Formats | Appropriate? |
|----------------|---------|-------------|
| `no_public_spec_available` | ABW, SYLK, DIF, TSV | YES — correct by design |
| `schema_authority_available` | Gnumeric | YES — correct by design |
| `legacy_backfill` | CSV, NDJSON, TOML, XCF, QOI | TEMPORARY — should sunset |

**Required Enhancement**:
- V13 should ALSO fire when: spec_fact_refs is ABSENT AND no exception_classification AND item_type is PRODUCT_SOURCE
- This closes the "omit and ignore" bypass path while preserving legitimate exceptions

---

## 4. Anti-Skip Detectors — Spec Authority Coverage

**Detector 17: Stream-Local Authority Check** (MEDIUM severity)
- Checks for `spec_fact_refs` presence in stream items
- Severity: MEDIUM — informational, does NOT block
- Finding: Advisory only. Does not prevent ACCEPTED verdict.

**Detector 19: ODF Spec Linkage Check** (HIGH severity)
- Checks ODF PRODUCT_SOURCE items for `spec_qname_refs` and `spec_fact_refs`
- Severity: HIGH — DOWNGRADES verdict from ACCEPTED to ACCEPTED_WITH_WARNINGS
- Finding: Downgrades but does NOT block. Sprint still ACCEPTED.
- Scope: ODF formats only. Non-ODF formats not checked.

**Gap**: Neither detector prevents a sprint from being ACCEPTED. Detector 19 is the strongest check but only warns.

---

## 5. Supervisor Review — Authority State Assessment

**Does supervisor_loop.py autonomous-cycle check spec authority state?**

Steps that touch spec authority:
- Step 0a-refresh: refresh_check.py (non-blocking, advisory)
- Step 2d3: TC-GUARD-001 (bypassed by gap_ledger_ref)
- Step 2d4: validate_spec_cache_ai_guard (advisory only)
- Governance validators: V13 (partially enforced — absent = no-op)
- Anti-skip: Detectors 17, 19 (advisory)

**Steps that do NOT touch spec authority**:
- Step 0b: plan lock (no authority check)
- Step 1: task selection (poc-targets only, not P-level)
- Step 2a-2c: declaration generation (no spec injection)
- Step 3: grading (gap_ledger_ref sufficient for purpose check)
- Step 4: continuation check (no authority state required)
- Step 5: next sprint generation (no authority data injected)

**Finding**: Spec authority is checked in 4 places but bypassed in all 4. No stage in the autonomous cycle is a hard spec authority gate.

---

## 6. Proof Graph — Authority Chain Assessment

**What proof graph should document**:
```
spec PDF → section → FACT-FODS-001 → requirement pack → code citation → test citation → evidence
```

**What actually exists**:
- `fods-p6-proof-graph.yaml` at `.local/spec-cache/fods/1.3/workbench/reports/authority-conveyor-20260608/`
- Covers FACT-FODS-001 only (1/4988 facts)
- Explicitly scoped: "P6 is claimed ONLY for FACT-FODS-001"
- `project_product_ledger_to_proof_graph.py` exists but traces code→test only (NOT spec→fact→code)
- Three iterations of builders (iter001-003) — ongoing evolution
- Product ledger does NOT record authority level per format

**Gap**: Proof graph is not updated per sprint. authority_integration_fabric.py (which would update the graph) is never called.

---

## 7. Summary — Gate Coverage Table

| Gate | Location | Type | Effective? | Bypass? |
|------|----------|------|-----------|---------|
| TC-GUARD-001 | autonomous_cycle.py Step 2d3 | Pre-grade block | PARTIAL | YES — gap_ledger_ref bypass |
| V13 | governance_validators.py | Post-grade block | PARTIAL | YES — absent=no-op; exception_classification |
| Detector 17 | anti_skip_checker.py | Advisory | NO | N/A |
| Detector 19 (ODF) | anti_skip_checker.py | Verdict downgrade | PARTIAL | YES — ODF only, not blocking |
| refresh_check | autonomous_cycle.py Step 0a | Advisory | NO | N/A |
| validate_spec_cache_ai_guard | autonomous_cycle.py Step 2d4 | Advisory | NO | N/A |
| authority_integration_fabric | (unwired) | NOT ACTIVE | NO | N/A |

**Effective blocking gates**: 0 out of 7

**Verdict**: No spec authority gate currently blocks a product sprint from being ACCEPTED with zero spec authority citations. The system is enforcement-weak.
