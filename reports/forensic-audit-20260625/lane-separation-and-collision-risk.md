# Lane Separation and Collision Risk Report

**Sprint/Run ID:** ff-archaeology-20260625

---

## Summary

Lane separation is **ENFORCED** at the code level via GOV_BLOCK signals and the
Wave 3 gate. Machinery lanes (1-6, 14, 15) are logically separate from product
lanes (7-13). Three active collision risks exist but all are mitigated by existing
validators. No active collisions detected at audit time.

---

## Lane Map

### Machinery Lanes (Lanes 1-6, 14, 15)

| Lane | Purpose | Enforced By |
|------|---------|------------|
| Lane 0 | Coordinator + Supervision | autonomous_cycle.py |
| Lane 1 | SAL Pipeline Wiring | sal-pipeline-heal skill |
| Lane 2 | Capability Reintegration | capability_map_generator.py |
| Lane 3 | Capability-to-Feature Compiler | capability_feature_compiler.py |
| Lane 4 | Skills + Prompt Wiring | skill-registry.yaml, V43/V44 |
| Lane 5 | Validators + Gate Hardening | governance_validators.py |
| Lane 6 | QName-to-Code Ontology | shared/qname-registry/, V53 |
| Lane 14 | Autonomous Supervision Audit | autonomous-supervisor-audit reports |
| Lane 15 | Autonomous Healing/Learning | failure_memory.py (partial) |

### Product Lanes (Lanes 7-13)

| Lane | Purpose | Gate |
|------|---------|------|
| Lane 7 | .NET Architecture Blueprint | Wave 3 gate (BLOCKER) |
| Lane 8 | Python Architecture Blueprint | Wave 3 gate (BLOCKER) |
| Lane 9 | FODS Product Rebuild | Wave 3 gate |
| Lane 10 | FODT Product Rebuild | Wave 3 gate |
| Lane 11 | ZST/XCF/FODG Product Hardening | Wave 3 gate |
| Lane 12 | CI, Package, Evidence Hardening | Wave 3 gate |
| Lane 13 | Post-Regeneration Recompute | Wave 3 gate |

**Wave 3 Gate:** A BLOCKER gate that requires all machinery healing (Lanes 1-6, 14, 15)
to be COMPLETE before any product rebuild (Lanes 7-13) begins. This is the primary
lane-separation enforcement mechanism.

---

## GOV_BLOCK Signals

Two GOV_BLOCK signals are BINDING and NON-OVERRIDABLE (CLAUDE.md Supreme Directive exception):

### GOV_BLOCK:monolith_detection_validator
- **Trigger:** A product source file exceeds 800 LOC AND is a NEW violation (not in known_violations)
- **Effect:** check_continuation.py returns STOP with `reason: structural_govblock_must_be_resolved_first`
- **Required action:** Analytics separation sprint BEFORE next product deepening
- **Applicable to:** Any format where a codec/parser/model file is created oversized
- **Current status:** NOT triggered (all oversized files are in known_violations with frozen caps)

### GOV_BLOCK:validate_source_architecture
- **Trigger:** Source architecture validator detects WORSENED violation (LOC or functions increased above baseline cap)
- **Effect:** Same hard stop as above
- **Current status:** NOT triggered (no worsened violations detected)

---

## Collision Risk Analysis

### Risk 1: Product Deepening Creates Oversized Files

**Scenario:** A developer uses `add-python-api` or `add-analytics-function` skill to
add functions to an existing file, pushing it above its baseline_loc_cap.

**Mitigation:**
- baseline_loc_cap is write-once (NEVER increase)
- source_structure_validator.py checks both LOC AND function count at submission
- If LOC increases above cap → `blocks_sprint=True` in validator output
- GOV_BLOCK:validate_source_architecture fires
- autonomous_cycle.py circuit breaker (SUP-RECT-005) detects repeated zero-task cycles

**Risk level:** LOW (mitigated, but monitoring required)

### Risk 2: Analytics Functions Bypass Suspension

**Scenario:** A developer uses `add-analytics-function` skill on ZST/XCF/FODG where
the rotation was suspended.

**Mitigation:**
- V42 (`validate_deepening_suspension`) blocks PRODUCT_SOURCE items with `_mod_\d+_times_\d+`
  pattern in evidence_paths
- `add-analytics-function` skill is registered but suspended for these formats in skill-registry.yaml

**Limitation:** V42 only blocks arithmetic masquerade functions (`_mod_N_times_N` pattern).
Other non-arithmetic analytics additions are NOT blocked by V42 for ZST/XCF/FODG.

**Risk level:** MEDIUM (partially mitigated)

### Risk 3: Per-Chat Plan Bypassed by Session Mismatch

**Scenario:** A new conversation starts with `continue` and incorrectly picks up
the sprint loop instead of checking for active per-chat plan.

**Mitigation:**
- CCI-MVP: continuation-signal.json contains session_id
- SESSION_MISMATCH → NON-OVERRIDABLE hard stop
- CHAT_ID_MISMATCH → NON-OVERRIDABLE hard stop
- Context compaction disambiguation rule in CLAUDE.md
- Active plan lock files in `.local/supervisor/plan-locks/`

**Risk level:** LOW (well-mitigated by CCI-MVP)

### Risk 4: Product Source Items Without gap_ledger_ref

**Scenario:** A sprint declares PRODUCT_SOURCE or PRODUCT_TEST items without gap_ledger_ref,
capability_ref, or spec_fact_refs — "purposeless" work.

**Mitigation:**
- TC-GUARD-001 (UPGRADED to BLOCK mode 2026-06-18): Unconditional block in autonomous_cycle.py Step 2d3
- Items without any of {gap_ledger_ref, capability_ref, spec_fact_refs} → added to rework_items
- TC-GUARD-002: Purpose check in grade_declared_work.py labels items PURPOSEFUL/UNPURPOSEFUL
- V53 ensures spec_qname exists on any generated class

**Risk level:** LOW (TC-GUARD-001 is a hard block, not advisory)

---

## Active Collision Status

**At time of audit (2026-06-25):**
- No GOV_BLOCK signals active
- No worsened violations in source_structure_validator
- No rework_items in continuation signal
- No SESSION_MISMATCH or CHAT_ID_MISMATCH detected
- All 50 validators registered and operational

**Conclusion: No active collisions. All risks are mitigated.**

---

## Lane Separation Maturity Assessment

| Mechanism | Implementation | Maturity |
|-----------|---------------|---------|
| Wave 3 gate (BLOCKER) | Defined in master plan, Wave dependency graph | PARTIAL (plan-enforced, not code-enforced) |
| GOV_BLOCK signals | Code-enforced in autonomous_cycle.py | FULL |
| Lane ownership validation | lane_enforcement_validator.py (validates declared_lane) | PARTIAL (validates but doesn't prevent assignment) |
| DAG ordering | Defined in master plan wave structure | NONE (prompt-only) |
| Analytics suspension | V42 validator (arithmetic pattern only) | PARTIAL |
| TC-GUARD-001 | Code-enforced in autonomous_cycle.py | FULL |
| Session identity (CCI-MVP) | Code-enforced in check_continuation.py | FULL |

**Overall lane separation maturity: GOOD (with prompt-enforcement gaps for DAG ordering)**
