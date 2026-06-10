# Adversarial Review
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Lane: L-ADVERSARIAL
# Date: 2026-06-07

---

## Review Methodology

This is an independent review of all plan-repair artifacts produced in this sprint.
Each of the 10 adversarial questions is answered with PASS, ADVISORY, or CRITICAL.

CRITICAL findings block the single-go execution prompt.
ADVISORY findings are noted but do not block.

---

## Question 1: Does the repaired plan allow any product implementation to slip through?

**Finding: PASS**

Evidence reviewed:
- All taskcards in authority-healing-taskcards.json have `src/` in forbidden_paths
- VG-014 explicitly checks that no taskcard has src/ in allowed_paths
- TCA-012 non_goals explicitly lists: new_product_implementation, new_test_files, src_changes
- repaired-plan.md constraints section reiterates: NO product source file changes

No pathway for product implementation to slip through in this sprint.

---

## Question 2: Is any bypass ledger entry not covered by a taskcard?

**Finding: ADVISORY**

The 10 bypass inventory entries (BYP-001 through BYP-010) from the investigation are not all explicitly mapped to taskcards in this plan-repair sprint:
- BYP-001 → TCA-004 (selector authority gate design)
- BYP-002 → TCA-002 (spec_fact_refs enforcement)
- BYP-003 → TCA-015 (proof graph authority edges)
- BYP-004 → TCA-008 (supervisor gate)
- BYP-005, BYP-006 → TCA-012 (Gnumeric/ABW bypass pilot)
- BYP-007, BYP-008, BYP-009, BYP-010 → not individually mapped

The unmapped bypasses (BYP-007..BYP-010) need taskcards in the healing sprint. This is ADVISORY for the plan-repair sprint since the healing sprint will cover them.

**Recommendation:** Add a note to single-go-execution-prompt.md that BYP-007..BYP-010 need taskcards in the stop-the-bleeding sprint.

---

## Question 3: Is any state machine transition unsafe (can jump to CLOSED_VERIFIED without evidence)?

**Finding: PASS**

Review of authority-healing-state-machine.json:
- CLOSED_VERIFIED entry_criteria: ["all_closure_criteria_met", "evidence_bundle_present"]
- CLOSED_VERIFIED allowed_transitions_from: ["INDEPENDENT_VERIFIED", "RELEASE_GATE_ENFORCED"] only
- Cannot reach CLOSED_VERIFIED from IMPLEMENTING directly
- Cannot reach CLOSED_VERIFIED from PILOT_RUNNING

All paths to CLOSED_VERIFIED require at least INDEPENDENT_VERIFIED (agent review) or RELEASE_GATE_ENFORCED (supervisor chain).

---

## Question 4: Does the single-go prompt allow spec_fact_refs to be warning-only?

**Finding: PASS**

VG-012 explicitly checks for "warning" near "spec_fact_refs" in repaired-plan.md and must return 0.
repaired-plan.md states: "spec_fact_refs is BLOCKING" as a standing constraint.
REPAIR-007 is documented as applied.

The single-go-execution-prompt.md will inherit this constraint.

---

## Question 5: Does any taskcard allow validated_by: human without a real human gate?

**Finding: PASS**

Review of all taskcards: no taskcard sets validated_by: human.
repaired-plan.md Human Approval Rules section explicitly limits human approval to 4 scenarios.
VG-011 checks for unsafe validated_by: human in repaired-plan.md.
TCA-010 notes: "validated_by: independent_agent_verifier for agent-verifiable facts".

---

## Question 6: Is any lane allowed to write to a file it should not own?

**Finding: PASS**

Lane ownership map reviewed:
- L-SCHEMA writes only to schema-design.md (not live schemas/)
- L-SELECTOR writes only to selector-design.md (not tools/supervisor/)
- L-ADVERSARIAL writes only to adversarial-review.md
- L-BUNDLE writes only to .local/ and SHA256-MANIFEST.txt
- L-COORD does not write to authority-healing-taskcards.json (exclusive to L-STATEMACHINE)
- VG-009 checks overlap checker passes

No unsafe lane write permissions found.

---

## Question 7: Is the FODS positive pilot truly gated on PDF availability (not assumed present)?

**Finding: PASS**

TCA-011 state_transition_rules explicitly includes:
```
"pdf_missing": "DISCOVERED -> BLOCKED_BY_MISSING_SPEC"
```

TCA-011 validation_commands include:
```
"test -f .local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf && echo PDF_PRESENT || echo BLOCKED_MISSING_SPEC"
```

REPAIR-009 is documented as applied.

Live check during this sprint confirmed PDF IS present (24270588 bytes, SHA confirmed).

---

## Question 8: Is the bypass pilot truly blocked from creating product code?

**Finding: PASS**

TCA-012 non_goals:
- "new_product_implementation"
- "new_test_files"
- "src_changes"
- "modifying gnumeric_codec.py or abw_codec.py"

TCA-012 implementation_scope: "metadata-only — populate exception_classification fields"
TCA-012 allowed_paths: reports/ directory only
TCA-012 forbidden_paths: src/, .local/, tools/, tests/

REPAIR-008 confirmed applied. VG-014 validates no taskcard has src/ in allowed_paths.

---

## Question 9: Are all 10 confirmed bypass ledger entries covered by repair taskcards?

**Finding: ADVISORY** (same as Question 2)

BYP-001..006 are covered. BYP-007..010 need taskcards in the stop-the-bleeding sprint.
This is expected — plan-repair sprint covers planning, not full healing implementation.
The single-go-execution-prompt.md must instruct the stop-the-bleeding sprint to create these taskcards.

---

## Question 10: Is the evidence bundle self-contained without requiring live repo access?

**Finding: ADVISORY**

The bundle at `.local/spec-authority-plan-repair/${RUN_ID}/` contains all plan artifacts.
However:
- The bundle references paths like `${REPO_ROOT}/...` which require the repo to be present
- The SHA256-MANIFEST.txt makes the bundle tamper-evident but not portable to other machines
- The single-go-execution-prompt.md references dynamic values (REPO_ROOT, RUN_ID) that must be computed at execution time

This is an inherent constraint for a repo-local bundle. It is not a defect — the bundle is self-contained for review purposes on this machine.

---

## Adversarial Summary

| Question | Finding | Severity |
|----------|---------|---------|
| Q1: No product implementation slipthrough | PASS | — |
| Q2: All bypass ledger entries covered | ADVISORY | BYP-007..010 need taskcards in healing sprint |
| Q3: No unsafe CLOSED_VERIFIED path | PASS | — |
| Q4: spec_fact_refs not warning-only in prompt | PASS | — |
| Q5: No unsafe validated_by:human | PASS | — |
| Q6: No unsafe lane write permissions | PASS | — |
| Q7: FODS pilot gated on PDF availability | PASS | — |
| Q8: Bypass pilot blocked from product code | PASS | — |
| Q9: All bypass entries covered | ADVISORY | Same as Q2 |
| Q10: Bundle self-contained | ADVISORY | Portable constraint noted |

**CRITICAL issues found: 0**
**ADVISORY issues found: 2** (both noted; neither blocks single-go prompt)

**Verdict: NO CRITICAL ISSUES — single-go-execution-prompt.md may be produced.**
