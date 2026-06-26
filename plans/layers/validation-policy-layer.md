# Validation Policy Layer

```yaml
layer_metadata:
  layer_id: L12
  canonical_name: Validation Policy Layer
  canonical_slug: validation-policy-layer
  permanent_plan_path: plans/layers/validation-policy-layer.md
  schema_version: "1.0"
  plan_revision: "1"
  repository_revision: "a7744cf6"
  status: GOVERNED_OPERATIONAL
  health: HEALTHY
  maturity_current: 4
  maturity_target: 5
  current_stage: GOVERNED_OPERATION
  current_owner: null
  agent_type: null
  session_id: "923e237958c1"
  active_sprint: "lp-bootstrap"
  active_taskcards: []
  ready_taskcards: [TC-VAL-001]
  blocked_taskcards: []
  completed_taskcards: []
  dependencies: []
  upstream_layers: []
  downstream_layers: [L08, L11]
  skill_ids:
    - validate-mutation-guard
    - validate-product-code-ledger
    - validate-skill-contracts
  command_ids:
    - validate-mutation-guard
    - validate-product-code-ledger
    - validate-skill-contracts
  evidence_paths:
    - tools/supervisor/governance_validators.py
    - tests/supervisor/test_governance_validators.py
  last_started_at: null
  last_progress_at: "2026-06-26"
  last_updated_at: "2026-06-26"
  last_verified_at: "2026-06-26"
  last_verified_revision: "a7744cf6"
  next_task_id: TC-VAL-001
  next_action: "Add layer-plan validators V83-V86 (WARN-level); enforce primary_layer_id in declarations"
  handoff_id: null
```

---

## 1. Layer Metadata

See YAML block above.

## 2. Authority and Purpose

The Validation Policy Layer governs **what constitutes valid work** in Format Factory.
It owns:

- All 85+ governance validators (V1-V82 + SAL validators)
- The Production Library Standard v2 enforcement
- GOV_BLOCK structural failure protocol
- Gate authorization validators (V60-V72)
- SAL spec fact reference enforcement (V13 AND rule)
- Oracle obligation enforcement (V82)
- LOC cap enforcement (V35)
- QName structure validators (V49-V55)

**Standard Reference:** `docs/code-quality/production-library-standard-v2.md`

## 3. Scope

- `tools/supervisor/governance_validators.py` (127 KB, V1-V42)
- `tools/supervisor/governance_validators_ext.py` (57 KB, V43-V55)
- `tools/supervisor/governance_validators_ext2.py` (18 KB, V82)
- `tools/supervisor/governance_validators_dotnet.py` (V73)
- `tools/supervisor/governance_validators_gate_auth.py` (V60-V72)
- `tools/supervisor/governance_validators_ledger.py` (V74)
- `tools/supervisor/governance_validators_sal.py` (V-NEW-001, V-NEW-002)
- `tools/supervisor/governance_validators_signal.py`
- `tools/supervisor/governance_validators_spec.py` (V13, V75-V76)
- `tools/supervisor/governance_validator_runner.py`
- `tests/supervisor/test_governance_validators.py` (138 tests)
- `docs/code-quality/production-library-standard-v2.md`

## 4. Explicit Non-Scope

- Does NOT run validators (that is L11's responsibility via governance_validator_runner.py)
- Does NOT own the sprint cycle (L11)
- Does NOT own product source (L06)
- Does NOT own evidence schema definitions (L08)

## 5. Owned Decisions

- Which violations are FAIL vs. WARN
- When to apply GOV_BLOCK structural exception
- When to upgrade WARN to FAIL (e.g., V75/V76 new violations FAIL, existing WARN)
- LOC cap values (baseline_loc_cap in registry/source-structure-baseline.json)
- spec_fact_refs AND rule (gap_ref + spec_auth both required per TC-GUARD-001)

## 6. Upstream Inputs

- `docs/code-quality/production-library-standard-v2.md` — defines the standard
- `registry/source-structure-baseline.json` — LOC caps
- `shared/qname-registry/` — QName entries for V49-V55 checks
- `.local/sal-output/sal-facts-latest.json` — SAL fact IDs for V13 verification

## 7. Downstream Consumers

| Consumer | What it uses |
|----------|-------------|
| L11 Supervisor | Runs validators on every declaration |
| L08 Evidence | V83-V86 (pending) will validate primary_layer_id in declarations |
| L06 Product | Validators block non-compliant product source |

## 8. Ideal Production Design

The ideal validation policy layer:

1. **Comprehensive validators** covering all 7 dimensions of Production Library Standard v2:
   - Spec parity (V13, V47, V49-V55)
   - Architecture compliance (V66, V69, V70)
   - LOC caps (V35)
   - QName structure (V45, V49)
   - Gate authorization (V60-V72)
   - Oracle obligations (V82)
   - **Layer plan compliance (V83-V86 — PENDING)**
2. **Tiered severity:** FAIL for new violations, WARN for existing (V75/V76 model)
3. **GOV_BLOCK structural exception:** blocks product work, forces analytics separation
4. **Layer-plan validators (V83-V86):** ensure every PRODUCT_SOURCE item has primary_layer_id
5. **Idempotent:** running twice produces same result
6. **Extensible:** new validators added in new modules (ext3, ext4...) following existing pattern

## 9. Verified Current Implementation

```yaml
current_layer_implementation:
  implementation_paths:
    - tools/supervisor/governance_validators.py        # 127KB, V1-V42
    - tools/supervisor/governance_validators_ext.py    # 57KB, V43-V55
    - tools/supervisor/governance_validators_ext2.py   # 18KB, V82
    - tools/supervisor/governance_validators_dotnet.py # V73
    - tools/supervisor/governance_validators_gate_auth.py  # V60-V72
    - tools/supervisor/governance_validators_ledger.py # V74
    - tools/supervisor/governance_validators_sal.py    # V-NEW-001/002
    - tools/supervisor/governance_validators_signal.py
    - tools/supervisor/governance_validators_spec.py   # V13, V75-V76
    - tools/supervisor/governance_validator_runner.py  # runner, lazy imports
  test_paths:
    - tests/supervisor/test_governance_validators.py   # 138 tests (2026-06-26)
    - tests/supervisor/test_lane_guard.py
    - tests/supervisor/test_lane_enforcement.py
  active_components:
    - 85 validators across 9 modules
    - governance_validator_runner.py with lazy imports
    - GOV_BLOCK structural exception (4 validators)
  missing_components:
    - V83: validate_primary_layer_classified (pending TC-VAL-001)
    - V84: validate_permanent_layer_plan_exists (pending TC-VAL-001)
    - V85: validate_prework_log_present (pending TC-VAL-001)
    - V86: validate_layer_task_registered (pending TC-VAL-001)
  contradictions: []
```

## 10. Current Execution Stage

**GOVERNED_OPERATION** — 85 validators operational, 138 tests passing. Gap: 4 layer-plan validators missing.

## 11. Current Maturity Assessment

**LEVEL 4 — GOVERNED** (strong enforcement, one key gap)

Justification:
- 85 validators across 9 modules
- 138 tests covering all major validators
- GOV_BLOCK structural exception correctly implemented
- V13 AND rule (spec_fact_refs + gap_ref) in force
- V74 ledger_continuation_gate blocking non-compliant formats

Gap preventing L5: Layer-plan validators (V83-V86) don't exist yet.

## 12. Target Maturity

**LEVEL 5 — PRODUCTION AUTHORITY**

Achieved when V83-V86 are operational, enforcing primary_layer_id in declarations.

## 13. Current Strengths

- Comprehensive 85-validator coverage
- GOV_BLOCK exception correctly overrides Supreme Directive for structural failures
- V13 AND rule prevents spec_fact_refs workarounds
- V74 ledger_continuation_gate effectively blocks non-compliant format deepening
- Tiered severity model (WARN existing, FAIL new) prevents churn

## 14. Gap Register

| Gap ID | Severity | Current State | Target State | Root Cause | Taskcards |
|--------|----------|---------------|--------------|------------|-----------|
| VAL-GAP-001 | MEDIUM | No layer-plan validators | V83-V86 WARN-level | Layer control plane just created | TC-VAL-001 |
| VAL-GAP-002 | LOW | V46 skill_transcript_present WARN only | Should be FAIL | Skill invocation infrastructure not complete | TC-SKILL-GOV-002 |

## 15. Root-Cause Register

- **VAL-GAP-001:** `plans/layers/` directory did not exist until this bootstrap session. V83-V86 validators have no directory to verify against until now.
- **VAL-GAP-002:** Skill invocation transcript infrastructure (`.supervisor/skill-invocation-transcripts/`) not consistently populated. Making V46 FAIL would block too many legitimate sprints.

## 16. Repair Architecture

**TC-VAL-001:**
1. Add 4 new validator functions to `governance_validators.py` (or new `governance_validators_layers.py`):
   - `validate_primary_layer_classified(item)` → WARN if PRODUCT_SOURCE item lacks `primary_layer_id`
   - `validate_permanent_layer_plan_exists(item)` → WARN if `primary_layer_id` specified but plan file missing
   - `validate_prework_log_present(item)` → WARN if no `work_log_id` in evidence
   - `validate_layer_task_registered(item)` → WARN if `task_id` not in task-register.yaml
2. Register in `governance_validator_runner.py` as V83-V86 (WARN-level, no blocks_sprint)
3. Add 4 tests in `tests/supervisor/test_governance_validators.py`
4. Update `plans/layers/validation-policy-layer.md` §9 active_components

## 17. Schemas and Contracts

- `docs/code-quality/production-library-standard-v2.md` — the governing standard
- `registry/source-structure-baseline.json` — LOC caps (write-once per constraint)

## 18. Producers

- Developer adds new validator functions to governance_validators*.py
- governance_validator_runner.py auto-discovers via lazy imports

## 19. Consumers

- `tools/supervisor/governance_validator_runner.py` runs all validators
- Sprint declaration validation fails/warns based on validator results

## 20. Skills and Commands

| Skill | Purpose |
|-------|---------|
| validate-mutation-guard | Run mutation guard validators |
| validate-product-code-ledger | Validate product code ledger compliance |
| validate-skill-contracts | Validate skill contract files |

## 21. Validators and Enforcement

**GOV_BLOCK validators** (override Supreme Directive — structural failures):
- `monolith_detection_validator` — detects monolithic files
- `validate_source_architecture` — validates architecture compliance
- `validate_multi_responsibility_file` (V66) — blocks multi-responsibility files
- `validate_analytics_naming_enforced` (V69) — blocks analytics naming violations

**Spec parity validators** (V13 AND rule):
- V13: `spec_fact_refs_wired` — BOTH gap_ref AND spec_auth required

**Architecture validators:**
- V35: `loc_cap_not_exceeded` — LOC cap enforcement
- V50: `forbidden_module_names` — blocks *_analytics_extra.py etc.

## 22. Tests and Negative Controls

- `tests/supervisor/test_governance_validators.py` — 138 tests (all passing 2026-06-26)
- `tests/supervisor/test_lane_guard.py` — lane enforcement
- `tests/supervisor/test_lane_enforcement.py` — new lane tests

Negative controls:
- Test that V66 fires for multi-responsibility files
- Test that V74 blocks formats with continuation_allowed=false
- Test that GOV_BLOCK correctly overrides Supreme Directive

## 23. Evidence and Observability

- Governance validator results are in every autonomous-cycle output
- `reports/supervisor/evidence-review.json` contains per-item validator results
- Exit code 3 from autonomous_cycle indicates rework items (including GOV_BLOCK)

## 24. Recovery and Rollback

- GOV_BLOCK: analytics separation refactor required before next product deepening
- Other FAIL: fix declaration, re-run autonomous-cycle
- If validator module import fails: governance_validator_runner.py logs and continues (Supreme Directive)

## 25. Security and Compliance

- Validators enforce OWASP-relevant patterns (forbidden imports, injection vectors not applicable here)
- Legal category validators in V60-V72 gate authorize publication

## 26. Cross-Layer Handoffs

| Handoff | From | To | Artifact |
|---------|------|----|---------|
| HO-006 | L12 | L08 | V83 enforces primary_layer_id in declarations |

## 27. Migration and Backfill

V83-V86 are new validators. Existing declarations without primary_layer_id will
generate WARN (not FAIL) during bootstrap period. After 90 days: consider upgrading
to FAIL for new PRODUCT_SOURCE items.

## 28. Effort and Dependencies

- TC-VAL-001: ~3 hours. No dependencies (validators are independent).
- Can run in parallel with other bootstrap tasks.

## 29. Active Taskcards

| Task ID | Title | Status | Priority |
|---------|-------|--------|---------|
| TC-VAL-001 | Add layer-plan validators V83-V86 | TODO | P2 |

## 30. Ready Taskcards

TC-VAL-001 — READY (no dependencies).

## 31. Completed Taskcards

(None in this session)

## 32. Blocked and Waiting Work

- TC-SKILL-GOV-002 (V46 upgrade to FAIL) — WAITING for skill invocation infrastructure.

## 33. Decision Log

| Decision | Date | Rationale |
|----------|------|-----------|
| V83-V86 are WARN not FAIL | 2026-06-26 | Bootstrap period; new layer control plane |
| V75/V76 WARN existing, FAIL new | Pre-existing | Avoid churn on legacy violations |
| GOV_BLOCK overrides Supreme Directive | Pre-existing | Structural failures require repair, not skip |
| V13 AND rule (both gap_ref + spec_auth) | 2026-06-25 upgrade | Prevent spec_fact_refs workarounds |

## 34. Work Log

```yaml
- log_id: WL-L12-001
  layer_id: L12
  task_id: TC-LP-001
  session_id: "923e237958c1"
  sprint_id: lp-bootstrap
  timestamp: "2026-06-26T00:00:00Z"
  event_type: LAYER_FILE_CREATED
  summary: "Created validation-policy-layer.md permanent plan file"
  repository_revision: a7744cf6
  changed_paths: [plans/layers/validation-policy-layer.md]
  current_stage: GOVERNED_OPERATION
  status: IN_PROGRESS
  next_action: "Execute TC-VAL-001 to add V83-V86 validators"
```

## 35. Verification Log

```yaml
- verification_id: VER-L12-001
  layer_id: L12
  task_id: null
  repository_revision: a7744cf6
  contracts_verified:
    - "85 validators exist across 9 modules"
    - "138 tests pass in test_governance_validators.py"
    - "governance_validator_runner.py lazy-imports all modules"
    - "GOV_BLOCK exception implemented in check_continuation.py"
  focused_result: PASS
  integration_result: PASS
  negative_control_result: PASS
  verdict: VERIFIED
  verified_at: "2026-06-26"
  verifier: forensic-layer-discovery-report.md
```

## 36. Current Session Handoff

```yaml
layer_session_handoff:
  handoff_id: HSH-L12-001
  layer_id: L12
  permanent_layer_plan: plans/layers/validation-policy-layer.md
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  current_status: GOVERNED_OPERATIONAL
  current_stage: GOVERNED_OPERATION
  maturity_current: 4
  exact_next_task: TC-VAL-001
  why_this_is_next: >
    Layer-plan validators (V83-V86) are the only gap preventing maturity 5.
    They enforce primary_layer_id in declarations, connecting L12 to the new
    layer control plane. WARN-level is safe to add without breaking existing sprints.
  ready_tasks: [TC-VAL-001]
  blocked_tasks: []
  required_skills: []
  required_commands: []
  allowed_paths:
    - tools/supervisor/governance_validators.py
    - tools/supervisor/governance_validator_runner.py
    - tests/supervisor/test_governance_validators.py
  forbidden_paths:
    - src/python/
    - src/net/
  required_verification:
    - "tests/supervisor/test_governance_validators.py — all tests pass (138+4)"
    - "V83-V86 appear in governance_validator_runner.py"
  unresolved_findings:
    - "VAL-GAP-001: V83-V86 not yet created"
  known_risks:
    - "Adding V83-V86 must not break existing passing tests"
  resume_instructions: >
    READ this file §29 for TC-VAL-001 details.
    Add 4 WARN-level validators to governance_validators.py.
    Register in governance_validator_runner.py.
    Add 4 tests. Run test_governance_validators.py to verify.
```

## 37. Exact Next Actions

1. Open `tools/supervisor/governance_validators.py`
2. Add 4 new functions: `validate_primary_layer_classified`, `validate_permanent_layer_plan_exists`,
   `validate_prework_log_present`, `validate_layer_task_registered`
3. Add to `governance_validator_runner.py` with IDs V83-V86, severity WARN
4. Add 4 tests to `tests/supervisor/test_governance_validators.py`
5. Run `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py`

## 38. Layer Completion Gate

```yaml
validation_policy_layer_completion_gate:
  permanent_plan_exists: true
  ideal_design_complete: true
  current_state_verified: true
  validators_v83_v86_added: false  # pending TC-VAL-001
  all_validators_tested: false  # pending 4 new tests
  layer_plan_enforcement_active: false  # pending V83-V86
  overall: GOVERNED_OPERATIONAL_MINOR_GAP
```

## 39. Change History

| Date | Session | Change |
|------|---------|--------|
| 2026-06-26 | 923e237958c1 | Created permanent layer plan file (bootstrap TC-LP-001) |
