# Full2Foss-Inspired Secondary Plan — Defect Review
# Sprint: S-F2F-00 (plan repair)
# Reviewed: 2026-05-08
# Source: iridescent-coalescing-stearns.md (plan mode, never executed — ExitPlanMode rejected)
# Status: COMPLETED (this document captures defects corrected in plan-v2)

---

## Overview

The original Full2Foss-inspired secondary roadmap plan (iridescent-coalescing-stearns.md)
was produced in plan mode during the secondary sprint planning session. The ExitPlanMode
tool call was rejected by the user before execution. This document catalogues the 15
defects identified in that plan before it was repaired in plan-v2.

---

## Defect Catalogue

### D-01: Planning vs. Implementation Confusion (CRITICAL)

**Location:** Section "Files to Create (All in Implementation Sprint — Not Now)" line ~306,
immediately followed by "New Files (planning + governance — approved in this planning sprint)"
at line ~321.

**Defect:** The heading says all files are in an "implementation sprint, not now" but the very
next sub-section declares plans/secondary/, taskcards, and governance docs as "approved in
this planning sprint." The plan cannot simultaneously say files are "not now" and "approved now."

**Impact:** An executor following the plan would be confused about what to create when.

**Correction in v2:** Two-column file table separating "created this sprint" from "created in
future implementation sprints." plans/secondary/ and taskcards are explicitly created by the
plan-repair sprint (S-F2F-00). Implementation artifacts (schemas, tools, tests) are clearly
deferred with phase labels.

---

### D-02: Pre-Authorized Governance Updates (CRITICAL)

**Location:** Section "Governance Updates (approved in this planning sprint)"

**Defect:** AGENTS.md Section AA, GOVERNANCE.md Section 20, docs/acquisition-workflow.md,
and docs/current-state-and-evidence-authority.md are listed as "approved in this planning
sprint." The plan as a whole is PROPOSED_PENDING_HUMAN_APPROVAL. Nothing in a proposed plan
is self-authorized. The plan cannot approve its own execution.

**Impact:** Could lead an executor to make governance changes under the belief they were
pre-approved when they were not.

**Correction in v2:** All governance appends are listed as actions of the plan-repair sprint
execution (S-F2F-00), authorized by the execution prompt, not the planning doc. The governance
sections are explicitly marked "Proposed — Requires S-F2F-01 Human Approval" so their rules
do not become active until the playbook system is actually built.

---

### D-03: Circular S-F2F-01 Status Claim (HIGH)

**Location:** Section "Proposed Taskcards — S-F2F-01"

**Defect:** Under S-F2F-01 (gap analysis), the plan says "Status after this sprint: completed
(this IS the sprint)." The sprint was never executed — ExitPlanMode was rejected. The sprint
that existed was a plan mode session, not an execution sprint. Calling it "completed" before
execution is a false status claim.

**Impact:** Future sprints would find S-F2F-01 listed as completed when no execution run
had occurred, creating a stale state contradiction.

**Correction in v2:** S-F2F-00 is defined as the plan-repair sprint (this execution sprint).
S-F2F-01 is now "Playbook Schema and Policy" — the first future implementation slice. All
S-F2F-01 through S-F2F-08 are proposed_pending_human_approval.

---

### D-04: Typo in YAML Example (MEDIUM)

**Location:** Layer 4 example YAML, operation_id field

**Defect:** `operation_id: oracle-libr eoffice-setup` — embedded space in the identifier
breaks YAML semantics and would cause parse errors if copied to actual use.

**Impact:** If a future implementer copied the example, the YAML would be invalid.

**Correction in v2:** Corrected to `oracle-libreoffice-setup` (no space).

---

### D-05: Premature Product Schema Items (HIGH)

**Location:** Layer 6 "New planning docs (implementation sprint — docs only)"

**Defect:** `schemas/product/api-surface.schema.json` and `schemas/product/feature-boundary.
schema.json` are listed as "docs only" items in an "implementation sprint" but are actually
JSON schema definition files — not documentation. Schema files are implementation-layer artifacts
that require product gate authorization, not planning-only docs.

**Impact:** Blurs the docs-vs-implementation boundary. Could lead to schema files being created
before product gates authorize source work.

**Correction in v2:** schema files moved entirely to Phase P1 (product dependency closure
design), which is deferred until FODS Gate 8+ AND explicit human authorization. Phase P1 itself
is further decomposed: design docs first, schema files require separate explicit authorization.

---

### D-06: Unauthorized settings.json Change Proposal (MEDIUM)

**Location:** Section "Settings Update Needed"

**Defect:** The plan proposes adding multiple paths to `.claude/settings.json` allow list
(plans/secondary/**, tools/playbook/**, etc.) as a planning-doc recommendation. Settings.json
changes are system configuration changes — they require authorization in the specific execution
sprint that needs them, not blanket pre-authorization in a planning document.

**Impact:** Could lead an executor to change settings.json without understanding which sprint
actually needed which path.

**Correction in v2:** Settings.json allow-list additions are NOT in this sprint. Each future
implementation sprint (S-F2F-01, S-F2F-02, etc.) must include settings.json updates as part
of its own authorized scope. No blanket pre-authorization.

---

### D-07: Sequencing Error — Review Queue Before Apply Mode (HIGH)

**Location:** Phase S-F2F-04 (review queue integration)

**Defect:** The plan lists S-F2F-04's prerequisite as "S-F2F-03 apply mode working." This is
backwards. The review queue is the safety mechanism that makes apply mode safe. Implementing
apply mode BEFORE the review queue exists means unresolved conflicts have no structured handling.

**Impact:** Apply mode could be implemented without a conflict management system, creating
uncontrolled file mutation risk.

**Correction in v2:** Phases resequenced:
- S-F2F-03: Dry-run mode + review queue export (together)
- S-F2F-04: Golden dry-run tests
- S-F2F-06: Apply-mode risk review (creates risk assessment doc; no implementation)
Apply mode implementation is NOT authorized by this plan at all — it requires a separate
human authorization after reading the risk review.

---

### D-08: No Minimal Viable Playbook Layer Defined (MEDIUM)

**Location:** Rollout phases section

**Defect:** The plan proposes schemas + replay engine + review queue + golden tests + family
playbook + apply mode all without defining which is the smallest safe first step. A human
reviewer cannot incrementally approve/reject the roadmap without knowing the minimal viable
unit.

**Impact:** Human cannot give partial approval for a small low-risk first step.

**Correction in v2:** S-F2F-01 (playbook schema + policy doc only) is defined as the minimal
viable first step. No replay engine until S-F2F-01 is complete and approved. The first step
is deliberately schema + documentation only — no tools, no execution capability.

---

### D-09: Missing Rollback Strategy (MEDIUM)

**Location:** Not present in original plan.

**Defect:** No section explains how to reverse any proposed change if something goes wrong.

**Impact:** Executor has no guidance on reversing implementations that fail validation or are
rejected by human review.

**Correction in v2:** Section 21 (Reversibility) added to plan-v2, covering each phase
individually. All phases are append-only to repo structure and fully reversible.

---

### D-10: Missing Acceptance Criteria Per Taskcard (MEDIUM)

**Location:** Proposed Taskcards section

**Defect:** Taskcard summaries list "approval needed" but no explicit "done" definition.
A human reviewer cannot tell when a taskcard's execution is complete.

**Impact:** Executor can claim completion without meeting objective criteria.

**Correction in v2:** Each S-F2F taskcard now includes a "Done Definition" section with
specific, verifiable acceptance criteria (e.g., "schema validates against jsonschema draft-7;
4 test cases PASS; BUNDLE_VALIDATION: PASS").

---

### D-11: S-F2F-06 Parallel Track Ambiguity (LOW)

**Location:** Phase S-F2F-06 (ODF flat family playbook), prerequisite statement

**Defect:** S-F2F-06 is listed as not requiring S-F2F-03/04/05, implying it can run after
S-F2F-01 (schema). But S-F2F-03/04/05 are in the same numbered sequence, making the parallel
track non-obvious to a human reader.

**Impact:** Potential confusion about dependency ordering.

**Correction in v2:** S-F2F-05 (ODF flat family playbook) explicitly states it can run after
S-F2F-01 schema is approved; it does NOT require S-F2F-02/03/04. Diagram-style dependency
table included in plan-v2.

---

### D-12: Product Dependency Closure Gate Prerequisite Too Vague (MEDIUM)

**Location:** S-F2F-07 prerequisite

**Defect:** "FODS Gate 7+ progress" is vague. It doesn't specify which gate exactly, or
what human authorization is required beyond Gate 7 progress.

**Impact:** Executor might start product dependency closure design too early.

**Correction in v2:** S-F2F-07 prerequisite is explicit: requires FODS Gate 8 (security review)
to be PASSED AND a separate human authorization prompt explicitly naming S-F2F-07. "Gate 7+
progress" is not sufficient.

---

### D-13: Old Taskcard Numbering (HIGH)

**Location:** All taskcard numbering throughout original plan.

**Defect:** Original plan numbered S-F2F-01 as the gap analysis sprint. This sprint (the
execution sprint) IS the plan repair sprint — it is S-F2F-00. The gap analysis was part of
the plan-mode session, which was never executed. Numbering S-F2F-01 as "gap analysis" when
there is no S-F2F-00 creates a gap in the sequence and misidentifies what sprint 01 is.

**Impact:** Future sprints would have an unexplained gap between sprint "00" (implicit) and
sprint "01" (gap analysis), and sprint 01's content (gap analysis, which is planning only)
would conflict with implementation work expected in numbered execution sprints.

**Correction in v2:** S-F2F-00 = plan repair (THIS sprint). S-F2F-01 = playbook schema and
policy (first future implementation sprint). S-F2F-02 = playbook validation tool. Etc.
Renumbering is clean and sequential.

---

### D-14: plans/secondary/ Listed Under Both "Not Now" and "Now" (HIGH)

**Location:** "New Directories" list and "New Files (approved in this planning sprint)"

**Defect:** plans/secondary/ appears in the "New Directories (all in implementation sprint,
not now)" list AND in the "New Files (approved in this planning sprint)" list. The same
directory cannot be simultaneously "not now" and "approved now."

**Impact:** An executor would not know whether to create plans/secondary/.

**Correction in v2:** plans/secondary/ is unambiguously created by S-F2F-00 (this sprint).
It is not an "implementation" artifact — it is a planning artifact. The distinction between
"planning documents" (plans/secondary/) and "implementation artifacts" (tools/playbook/,
schemas/playbook/) is now explicit.

---

### D-15: Evidence Contract Referenced But Never Created or Validated (HIGH)

**Location:** Evidence Contract section of original plan.

**Defect:** The plan describes a contract file `secondary-full2foss-system-strengthening-plan.yaml`
but it was never created during the plan-mode session (which was never executed). No validation
against base-run v1.2 was performed. The plan-mode session cannot create files.

**Impact:** Any execution of the original plan would immediately fail evidence validation
because the contract file did not exist.

**Correction in v2:** A new contract `secondary-full2foss-plan-repair.yaml` is created as
part of THIS execution sprint (S-F2F-00). This is the first real contract for secondary sprints.
The obsolete contract reference (`secondary-full2foss-system-strengthening-plan.yaml`) is
not created — it described a sprint that never ran.

---

## Summary Table

| ID | Severity | Category | Corrected |
|----|----------|----------|-----------|
| D-01 | CRITICAL | Planning/implementation confusion | YES — file table split |
| D-02 | CRITICAL | Pre-authorized governance | YES — marked proposed-only |
| D-03 | HIGH | Circular status claim | YES — S-F2F-00 = plan repair |
| D-04 | MEDIUM | YAML typo | YES — space removed |
| D-05 | HIGH | Premature schema files | YES — deferred to P1+ |
| D-06 | MEDIUM | Unauthorized settings change | YES — removed from plan |
| D-07 | HIGH | Wrong sequencing | YES — review queue before apply |
| D-08 | MEDIUM | No minimal viable slice | YES — S-F2F-01 = schema only |
| D-09 | MEDIUM | Missing rollback | YES — Section 21 added |
| D-10 | MEDIUM | Missing acceptance criteria | YES — Done Definition per card |
| D-11 | LOW | Parallel track ambiguity | YES — explicit table |
| D-12 | MEDIUM | Vague product gate prereq | YES — Gate 8 PASSED required |
| D-13 | HIGH | Wrong taskcard numbering | YES — S-F2F-00 through S-F2F-08 |
| D-14 | HIGH | Directory in both "now" and "not now" | YES — unambiguous split |
| D-15 | HIGH | Contract never created | YES — new contract created |

15 defects identified. 15 defects corrected. No unresolved defects.
