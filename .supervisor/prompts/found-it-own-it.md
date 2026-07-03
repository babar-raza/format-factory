---
espanso_provenance:
  source_trigger: ":found-it-own-it"
  source_block: 48
  source_line_range: [64178, 65188]
  gap_id: GAP-ESP-003
  extraction_date: "2026-07-03"
  capability_id: null
  note: "Policy protocol — not a standalone capability. Referenced by audit-root-tools and post-sprint-audit."
prompt_id: ESP-PROMPT-4
title: "Found-It-Own-It Issue Ownership Protocol"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Found-It-Own-It (FIOI) Issue Ownership Protocol

## Core Doctrine

```
IF AN AGENT DISCOVERS A REAL PROBLEM,
THE AGENT OWNS ITS INVESTIGATION, CAPTURE, HEALING, AND VERIFICATION.
```

This applies regardless of:
- whether the issue existed before the current task
- whether another agent caused it
- whether it is in unrelated files
- whether it is "pre-existing technical debt"

**"Pre-existing" is provenance, not disposition. It does not excuse inaction.**

## Short-Context View

When you discover any issue (failed test, broken import, stale fixture, contradictory evidence,
schema violation, bypassed skill, missing qname): you own it from discovery to closure.
Capture → Reproduce → Root-cause → Taskcard → Heal → Verify → Regression-protect.
Do not defer. Do not leave it for a later agent. Do not mark a sprint complete while known issues remain open.

---

## Issue Classification

Trigger this protocol when any of the following is discovered:

**Test failures:**
- Failed test, flaky test, unexpected warning

**Artifact failures:**
- Malformed output, broken fixture, stale fixture, missing fixture
- Incorrect generated file, schema violation, invalid state transition

**Source failures:**
- Broken import, package failure, consumer failure, regression
- Suspicious stub, dead code, duplicated code

**Governance failures:**
- Bypassed skill or command, missing skill registration
- Invalid qname or hierarchy, missing provenance, unsupported claim
- Contradictory evidence, stale plan or taskcard

**Evidence failures:**
- Synthetic proof presented as real proof
- Missing evidence for a DONE claim

## Required Lifecycle

Every discovered issue must follow this lifecycle:

```
1. PRESERVE
   → Record the exact failure (error message, stack trace, file, line)
   → Do not modify the failing item before recording its state

2. REPRODUCE
   → Confirm the issue is repeatable
   → Identify the minimal reproduction case

3. CLASSIFY
   → Assign: test_failure | artifact_failure | source_failure | governance_failure | evidence_failure
   → Assess severity: BLOCKING | HIGH | MEDIUM | LOW

4. ROOT-CAUSE
   → Trace to the first failing boundary (not just the symptom)
   → Ask: "Why does this fail?" not "What file is broken?"

5. TASKCARD
   → Write a taskcard to `.local/evidences/<run_id>/` or into the active plan
   → Include: reproduction steps, root cause, acceptance criteria

6. HEAL
   → Implement the fix at the root cause, not the symptom
   → Do not suppress errors, weaken tests, or add bypass comments

7. VERIFY
   → Run the exact reproduction case again
   → Confirm the fix resolves the original failure

8. REGRESSION-PROTECT
   → Add a test or assertion that would catch this if it recurs
   → Update the validator, schema, or governance rule if applicable

9. CLOSE OR VALIDLY BLOCK
   → Mark the taskcard DONE with evidence
   → If externally blocked: classify exactly (EXTERNAL_BLOCKER: <reason>)
   → If deferred: explain why and create a tracked gap entry
```

## What FIOI Does NOT Mean

- You do not abandon your primary taskcard to chase every minor issue
- Priority issues (MEDIUM/LOW) may be captured as taskcards for a later sprint
- BLOCKING issues must be resolved before marking the primary sprint complete
- You are not required to fix issues in completely unrelated systems — but you must capture them

## Closure Anti-Patterns (forbidden)

- "I didn't cause it" — not a valid reason to ignore it
- "Unrelated to my change" — not permission to leave it open
- "Pre-existing debt" — captures the history, not the disposition
- Marking sprint DONE while known BLOCKING issues remain open
- Creating a finding note without a taskcard

## Integration with Post-Sprint Audit

The post-sprint-audit (PSL-PROMPT-1) will classify issues discovered during execution.
Any issue discovered during execution that was NOT captured as a FIOI taskcard will appear
as `claimed_unproven` or `risk_not_reduced` in the audit. Capture issues as you find them
to avoid audit rework.
