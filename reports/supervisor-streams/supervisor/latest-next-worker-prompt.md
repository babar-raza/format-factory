# FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001
# Generated: 2026-06-22T14:21:55.958465
# Source: Supervisor autonomous-cycle review of forensics-healing-sprint-20260622
# Stream: supervisor
# ADVISORY ONLY -- not a Format Factory authority document

---

## Preflight (read before any code change)

Read these files before writing any code:

1. `AGENTS.md`
2. `GOVERNANCE.md`
3. `plans/master-plan.md`
4. `registry/format-registry.yaml`
5. `reports/supervisor/session-resume.md`
6. `reports/supervisor/latest-review.md`
7. `.supervisor/policies.yaml`
8. `.supervisor/skill-registry.yaml`
9. `.local/supervisor/selected-product-gaps.json`
10. `product-capability-matrix/poc-targets.yaml`
11. `CLAUDE.md`

---

## Sprint Identity

- Sprint ID: FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001
- Prior sprint: forensics-healing-sprint-20260622
- Prior verdict: ACCEPTED_WITH_REWORK
- Prior tests: 0 passed, 0 failed, 0 skipped
- Autonomous continue: True

---

## Sprint Goal

**Goal:** Advance Supervisor tooling: Improve supervisor pipeline components; Strengthen evidence model or declaration schema. Build evidence declaration and run supervisor autonomous-cycle.

---

## Mandatory Evidence Rules

1. Worker MUST write `.local/evidences/<run_id>/evidence-declaration.yaml` at sprint end.
2. Last instruction MUST be:
   ```
   python tools/supervisor/supervisor_loop.py autonomous-cycle \
     --declaration .local/evidences/<run_id>/evidence-declaration.yaml
   ```
3. The declaration must list ALL work items with status, evidence paths, and test references.
4. Do NOT use the legacy `run-on-latest --bundle` command. It is deprecated.
5. Evidence is support infrastructure -- the goal is product POC progress.

---

## Governed Product Acceleration Rules

1. Load `.local/supervisor/selected-product-gaps.json` before choosing product work.
2. Resolve each selected product gap through `.supervisor/skill-registry.yaml`.
3. No direct ad-hoc `src/` edits are permitted. Use a governed skill or generated execution handoff.
4. Every `src/` edit MUST be recorded in `reports/r90/product-code-change-ledger.json`.
5. Run `python tools/supervisor/validate_product_code_ledger.py --ledger reports/r90/product-code-change-ledger.json` after product-code changes.
6. Include at least one dogfood export lane and one package/install proof lane.

---

## Train Manifest

| Train | Group | Title |
|-------|-------|-------|
| A | G1 | Governance Preflight |
| B | G2 | Improve supervisor pipeline components |
| C | G2 | Strengthen evidence model or declaration schema |
| D | G7 | State + Memory + POC Matrix Sync |
| E | G8 | Evidence Declaration + Supervisor Autonomous-Cycle |

---

## Group G1: Governance + Preflight

### Train A: Governance Preflight

Read all governance files. Verify no policy violations from prior sprint. Confirm MCP status, supervisor mode, and gate states. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before selecting product work.

**Acceptance Criteria:**
- All preflight files read
- No policy violations detected
- Gate states documented

**Files:**
- `reports/<run_id>/00-preflight.md`

## Group G2: Rework / Repair

### Train B: Improve supervisor pipeline components

Enhance inspection, grading, prompt generation, or context-pack building.

**Acceptance Criteria:**
- Tests pass for affected tools
- Evidence declared

**Files:**
- `tools/supervisor/`
- `tests/supervisor/`

### Train C: Strengthen evidence model or declaration schema

Improve declaration validation, manifest generation, or materialization.

**Acceptance Criteria:**
- Tests pass for affected tools
- Evidence declared

**Files:**
- `tools/supervisor/`
- `tests/supervisor/`

## Group G7: State / Memory / POC Matrix

### Train D: State + Memory + POC Matrix Sync

Update state/current-state.md, .supervisor/project-memory.md, and product-capability-matrix/poc-targets.yaml with sprint results.

**Acceptance Criteria:**
- poc-targets.yaml reflects actual status (no overclaiming)
- state/current-state.md updated
- project-memory.md entry appended

**Files:**
- `state/current-state.md`
- `.supervisor/project-memory.md`
- `product-capability-matrix/poc-targets.yaml`

## Group G8: Evidence + Supervisor Loop

### Train E: Evidence Declaration + Supervisor Autonomous-Cycle

Write evidence-declaration.yaml listing ALL work items. Run autonomous-cycle. Verify session-resume.md is regenerated. Validate `reports/r90/product-code-change-ledger.json` for any governed product source edit.

**Acceptance Criteria:**
- evidence-declaration.yaml written with all work items
- autonomous-cycle exits 0 or 3
- session-resume.md regenerated with current data
- approval-gates.md shows correct AUTONOMOUS_CONTINUE

**Files:**
- `.local/evidences/<run_id>/evidence-declaration.yaml`
- `reports/supervisor/session-resume.md`

**Verification:**
```bash
python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```


---

## Hard Prohibitions

- No `git push` without explicit user authorization.
- No `git commit` without explicit user authorization.
- No Gate 8 or Gate 11 approval (requires Babar Raza).
- No `commercial_product_ready: true` in any file.
- No PyPI / NuGet / GitHub release publication.
- No paid external AI API or web automation.
- No MCP activation unless MODE 4 already authorized.
- No destructive git operations (`git reset --hard`, `git clean -fd`, force-push).
- No deletion of existing test files.
- No PENDING markers in final state files.
- No overclaiming: if evidence is missing, declare status honestly.
- No direct ad-hoc `src/` edits outside the governed skill registry or generated handoff.
- No product-code change without a product-code ledger entry.

---

## Final Validation Sequence

After all trains complete, run this exact sequence:

```bash
# 1. Python tests
.local/venv/Scripts/python -m pytest tests/ -x -q --tb=short

# 2. Compile check on supervisor tools
.local/venv/Scripts/python -m py_compile tools/supervisor/autonomous_cycle.py
.local/venv/Scripts/python -m py_compile tools/supervisor/supervisor_loop.py
.local/venv/Scripts/python -m py_compile tools/supervisor/generate_supervisor_packet.py

# 3. .NET tests (if .NET work was done)
# (no .NET work this sprint)

# 4. Write evidence declaration
# (create .local/evidences/<run_id>/evidence-declaration.yaml)

# 5. Run supervisor autonomous-cycle
.local/venv/Scripts/python tools/supervisor/supervisor_loop.py autonomous-cycle \
  --declaration .local/evidences/<run_id>/evidence-declaration.yaml
```

---

## Allowed Verdicts

The sprint MUST end with one of these verdicts in the evidence declaration:

| Verdict | Meaning |
|---------|---------|
| ALL_TRAINS_COMPLETE | All trains passed acceptance criteria |
| PARTIAL_TRAINS_COMPLETE_PUBLICATION_BLOCKED | Some trains done, publication gate blocks remaining |
| REWORK_REQUIRED | Supervisor review found issues requiring repair |
| BLOCKED_EXTERNAL_GATE | Cannot proceed without external gate approval |

---

## Final Artifact Specification

At sprint end, these files MUST exist:

- `.local/evidences/<run_id>/evidence-declaration.yaml` -- declaration of all work items
- `reports/supervisor/session-resume.md` -- regenerated by autonomous-cycle
- `reports/supervisor/approval-gates.md` -- regenerated by autonomous-cycle
- `product-capability-matrix/poc-targets.yaml` -- updated if any product status changed
- `state/current-state.md` -- updated with sprint outcome

---

END OF SUPERVISOR-GENERATED MEGA-TRAIN EXECUTION PROMPT


## Durable Failure Memory Warnings

The following failures have been recorded in durable failure memory.
Address escalated failures with priority.

- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_execution_method_required_validator_failed (seen 138x, last: fuzzy-conjuring-papert)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_source_diff_required_validator_failed (seen 107x, last: fuzzy-conjuring-papert)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_idempotency_key_required_validator_failed (seen 72x, last: fuzzy-conjuring-papert)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_claim_classification_validator_failed (seen 7x, last: IDEMPOTENT-SWARM-EXECUTION-20260615-E31FA98)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_route_decision_required_validator_failed (seen 106x, last: fuzzy-conjuring-papert)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_spec_fact_refs_validator_failed (seen 189x, last: fuzzy-conjuring-papert)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_monolith_detection_validator_failed (seen 271x, last: CAPABILITY-LAYER-HEALING-20260621-ed51041)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): exit_code_3_rework_required (seen 172x, last: forensics-healing-sprint-20260622)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_source_architecture_failed (seen 15x, last: governance-healing-final-2026-06-22)
- ESCALATED FAILURE (SUPERVISOR_CONTROL_FAILURE): governance_validator_validate_skill_transcript_present_failed (seen 4x, last: fuzzy-conjuring-papert)
- WARNING: 10 unresolved failures in failure memory



## Learning-Based Governance Advisories

- **SPRINT_CLOSEOUT_PATTERN** (seen 16x): Sprint declaration validated PASS with sprint_executor_validate.py — *Action:* Continue using sprint_executor_validate.py --repair before closeout

## Spec-Parity Requirements (from skill registry)

The following skills require `spec_qname` mapping when invoked for product model work.
Any product model task using these skills MUST declare which spec QNames are addressed
and MUST NOT invent arbitrary flat class names without spec authority.

- **add-dotnet-api**: spec_qname_required=true
- **add-python-api**: spec_qname_required=true
- **add-dotnet-object-model-feature**: spec_qname_required=true
- **add-python-object-model-feature**: spec_qname_required=true
- **add-same-format-writer-feature**: spec_qname_required=true
- **spec-literal-qname-to-code-mapping**: spec_qname_required=true
- **spec-shaped-product-architecture-blueprint**: spec_qname_required=true
- **spec-parity-source-regeneration-and-migration**: spec_qname_required=true
- **python-reduced-spec-parity-model**: spec_qname_required=true

**Enforcement:** If a product model change is made without citing spec_fact_refs,
governance validator V8 (spec_fact_references) will FAIL the item.
Use SAL output at `.local/sal-output/sal-facts-latest.json` for valid FACT-* refs.
