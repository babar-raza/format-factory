# Playbook Layer — Policy and Architecture

**Document status:** Active (S-F2F-01 complete — schema and policy established)
**Created:** S-F2F-01 (2026-05-08)
**Replaces:** Proposed-only note in AGENTS.md Section AA and GOVERNANCE.md Section 20
**Authority:** This document is governance reference only. It is NOT evidence authority.
**Schemas:** schemas/playbook/acquisition-playbook.schema.json, schemas/playbook/review-queue.schema.json

---

## 1. Purpose

This document defines what the playbook layer is, what it is not, and how it operates within
format-factory's acquisition pipeline. Playbooks in format-factory are YAML documents that
record, for each acquisition gate, what operations were performed, what files were expected,
what validation commands confirm correctness, what evidence artifacts are required, and what
happened when replay produced a conflict.

Playbooks are execution aids. They do not replace any existing authority.

---

## 2. Relationship to MAIN SPRINT

The playbook layer is a SECONDARY capability. The MAIN SPRINT (format acquisition gate
execution) remains the active delivery path. Playbooks may only be created and used in
a manner that does not conflict with MAIN SPRINT gate progress, gate statuses, evidence
contracts, or human approval decisions.

A playbook may reference MAIN SPRINT gate outputs as evidence. It cannot modify them.
It cannot claim they are satisfied when they are not.

---

## 3. Relationship to Evidence Contracts

Evidence contracts (tools/evidence/contracts/*.yaml) are authoritative for what artifacts
must exist in an evidence bundle. Playbooks are NOT evidence contracts. Playbooks may
reference evidence contracts but cannot substitute for them. A gate cannot pass based
on a playbook replay alone — the required evidence contract must be satisfied independently.

Review queue items are inputs to evidence review, not replacements for evidence contracts.

---

## 4. Relationship to Master Plan and Current-State Authority

The authoritative record of gate state is: registry/format-registry.yaml (approved by human).
The authoritative record of run state is: bundle-metadata/git-log.txt and git-status-final.txt
in the evidence bundle (see docs/current-state-and-evidence-authority.md).

Playbooks and replay reports are DERIVED ARTIFACTS. They are informational. They are NOT
authority for any gate state, run state, or compliance claim. plans/master-plan.md remains
the single operational authority for sprint planning.

---

## 5. Relationship to DEC-034 Independent Verification

DEC-034 (AGENTS.md Section V, GOVERNANCE.md Section 15) requires that every agent-initiated
gate advance must be independently verified by a separate agent session before human review.

Playbook replay does NOT satisfy DEC-034. A replay report is one additional data point
available to the independent verifier. The independent verifier still runs their own checks,
reads the evidence bundle, and produces a separate verification report.

---

## 6. What Playbooks Are

Playbooks are:

1. **Structured YAML documents** following schemas/playbook/acquisition-playbook.schema.json.
2. **Replay reference memory** — they record what operations were executed in a prior sprint
   so that future sprints can check consistency.
3. **Conflict detectors** — when a replay does not match expected state, the discrepancy
   is exported to a review queue (schemas/playbook/review-queue.schema.json).
4. **Format-family reuse guides** — family playbooks (e.g., odf-flat) allow related formats
   to share operation templates, reducing documentation duplication.
5. **Non-authoritative documentation** — a playbook can explain what was done; it cannot
   declare what the result means.

---

## 7. What Playbooks Are Not

Playbooks are NOT:

1. **Gate approval mechanisms** — a gate cannot pass because a playbook replay passed.
2. **Evidence contracts** — they do not determine what must exist in a bundle.
3. **DEC-034 substitutes** — they do not perform independent verification.
4. **Human approval substitutes** — human review of a replay report is NOT human gate approval.
5. **Spec or legal authority** — they contain no normative legal or specification claims.
6. **Product release authority** — they do not authorize source code creation or product release.
7. **Active tools (yet)** — as of S-F2F-01, no replay tools exist. This policy document
   precedes tooling. Tooling requires separate authorization (S-F2F-02 through S-F2F-04).
8. **Apply mode mechanisms** — apply mode is not authorized; it is a future risk-review
   subject (S-F2F-06).
9. **LLM authority** — any LLM fallback in a replay context is informational only and cannot
   produce authoritative conclusions.

---

## 8. Why Full2Foss-Inspired Patterns Are Being Borrowed

The Full2Foss open-source model uses structured playbooks to make complex multi-step
acquisition pipelines reproducible and reviewable. format-factory adopts this inspiration
with the following adaptations:

- **Deterministic first**: replay engines (when they exist) check deterministic outputs
  (checksums, validation results) before any LLM involvement.
- **No inherited gate approval**: format-factory's strict 11-gate model does not allow
  any gate to be implicitly approved by virtue of a family relationship.
- **Human gating preserved**: every gate still requires a human approval prompt, regardless
  of playbook state.
- **DEC-034 preserved**: independent verification is required before every human review.

---

## 9. What Is Not Being Borrowed

The following Full2Foss patterns are NOT being adopted:

1. **Automated gate approval** — gates require explicit human approval in format-factory.
2. **LLM-as-authority** — LLM outputs in playbook context are informational only.
3. **Continuous deployment pipelines** — format-factory is not CI/CD.
4. **Implicit family inheritance** — each format must be independently evaluated.
5. **Any pattern that bypasses evidence contracts or DEC-034** — these are non-negotiable.

---

## 10. Playbook Lifecycle

A playbook for a format goes through these phases:

1. **Schema established** (S-F2F-01 — this sprint): schema.json files created; policy doc written.
2. **Validation tool created** (S-F2F-02 — future): tools/playbook/validate_playbook.py validates
   YAML against schema. Read-only. No writes.
3. **Dry-run replay** (S-F2F-03 — future): tools/playbook/replay_acquisition_playbook.py
   simulates operations and exports review queue. No file writes.
4. **Golden tests** (S-F2F-04 — future): tests/playbook/ golden fixtures for replay consistency.
5. **Family playbook** (S-F2F-05 — future): acquisition-packs/_families/odf-flat/playbook.yaml
   defines shared operation templates.
6. **Apply mode risk review** (S-F2F-06 — future): risk review document only; apply mode
   implementation is NOT authorized until a separate prompt authorizes it after reading the risk review.
7. **Actual playbook.yaml files** — created in future sprints under acquisition-packs/ after
   schema validation and dry-run tooling are available and approved.

---

## 11. Schema Overview

### acquisition-playbook.schema.json (top-level structure)

Key fields:
- `schema_version`: "1.0"
- `playbook_id`: stable identifier (e.g., "fods-acquisition")
- `format_id`: format identifier (e.g., "fods")
- `format_family`: family identifier (e.g., "odf-flat")
- `playbook_kind`: one of format_playbook | family_playbook | documentation_example
- `status`: draft | proposed | active | deprecated | superseded | documentation_example_only
- `authority_statement`: what this playbook IS authoritative for
- `non_authority_statement`: what this playbook is NOT authoritative for
- `operations`: list of acquisition operation records
- `forbidden_uses`: must include automatic_gate_approval, spec_or_legal_authority,
  replacing_dec034, replacing_human_approval

### Operation record (nested in operations[])

Key fields:
- `mode_allowed`: validate_only | dry_run | apply_proposed | apply_authorized
- `approval_boundary`: no_gate_approval | requires_dec034 | requires_human_approval | requires_dec034_and_human
- `reuse_level`: none | full | adapt | guide | new
- `conflict_policy`: fail_and_queue | warn_and_continue | fail_hard | defer_to_human

### review-queue.schema.json

Key fields:
- `items[].severity`: low | medium | high | blocker
- `items[].status`: open | in_review | resolved | deferred | rejected | superseded
- `items[].owner_role`: agent | independent_verifier | human | main_sprint_owner | secondary_sprint_owner
- `items[].blocks_apply_mode`: MUST be true if severity=high or blocker
- `items[].blocks_gate_progress`: if true, requires DEC-034 or human review
- `governance.cannot_approve_gates`: always true
- `governance.high_severity_blocks_apply`: always true

---

## 12. Review Queue Lifecycle

1. Replay tool (S-F2F-03, not yet created) runs an operation in dry-run mode.
2. If output does not match expected, a review item is created.
3. Items are exported to plans/review-queues/ (directory created when S-F2F-03 executes).
4. Items with severity=high or blocker block apply mode unconditionally.
5. Items with blocks_gate_progress=true require resolution (DEC-034 or human) before gate advance.
6. Resolution is recorded in the item's resolution_notes; status changes to resolved.
7. Resolved queue is included in the evidence bundle for the sprint.

---

## 13. Deterministic-First Rule

When a replay engine (S-F2F-03) runs an operation, it must:

1. First check all deterministic outputs: file existence, checksums, validation command results.
2. Only if deterministic checks pass may it report a PASS for that operation.
3. If any deterministic check fails, a review queue item is created immediately.
4. LLM fallback is NOT permitted at the deterministic layer.
5. LLM assistance is only permitted for generating descriptive fields (notes, descriptions),
   and these fields are explicitly marked as informational-only.

---

## 14. LLM Fallback Policy

LLM assistance may be used to:
- Generate descriptions, summaries, and explanatory text in playbooks.
- Suggest fixes in review queue items (informational only).
- Create draft playbook.yaml files for human review.

LLM assistance MUST NOT be used to:
- Determine gate pass/fail.
- Approve a gate in any way.
- Replace checksum verification.
- Replace schema validation.
- Replace DEC-034 independent verification.
- Replace human approval.
- Declare compliance with any spec or legal standard.

All LLM-generated content in playbooks must be clearly marked as informational.
No LLM fallback mechanism is implemented as of S-F2F-01.

---

## 15. Family Reuse Policy

Family playbooks (e.g., odf-flat family covering FODS and FODT) allow:
- Shared operation templates at the family level.
- Format-specific overrides for each format.
- reuse_level classification: full | adapt | guide | new.

Family playbooks MUST NOT:
- Claim inherited gate approval for member formats.
- Claim that if one format passed a gate, a related format does too.
- Override the DEC-034 requirement for any format.
- Override human approval requirements.

Each format must go through its own independent gate evaluation regardless of family membership.

---

## 16. Gate Approval Policy

**A playbook replay result, review queue resolution, or family reuse claim
CANNOT approve any gate. Period.**

Gates in format-factory are approved by:
1. An independent agent verification sprint (DEC-034).
2. Explicit human approval via a human-authorized prompt.

These two steps are required for every gate. No playbook layer artifact changes this.

---

## 17. Evidence Bundle Integration

Playbook-related artifacts that may appear in evidence bundles:
- `bundle-metadata/playbook-replay-report.md` — informational replay summary.
- `bundle-metadata/review-queue-export.yaml` — open review items.
- `repo/schemas/playbook/*.json` — the schemas (committed to repo).
- `repo/docs/playbook-layer.md` — this policy document.
- `repo/docs/examples/*.yaml` — documentation-only examples.

These are informational inputs. They do not replace any required_metadata_files
or required_repo_files in an evidence contract.

---

## 18. Prohibited Uses

The following uses of playbooks, review queues, and replay reports are explicitly prohibited:

1. **Automatic gate approval** — any gate approval based solely on playbook output.
2. **Spec or legal authority** — any normative claim about format specifications or legal status.
3. **Product release authority** — any claim that a format is ready for product release.
4. **DEC-034 replacement** — any substitution for the independent verification requirement.
5. **Human approval replacement** — any substitution for the human gate approval prompt.
6. **Applying without authorization** — running apply mode before it is explicitly authorized
   in a human prompt naming the specific taskcard and sprint.
7. **Evidence substitution** — treating a replay report as if it were an evidence bundle.
8. **LLM fallback authority** — treating any LLM-generated content as authoritative for
   compliance, legal, or gate-state purposes.

---

## 19. Future Rollout Phases

| Phase | Taskcard | Status | Creates |
|-------|----------|--------|---------|
| S-F2F-01 | Playbook Schema and Policy | **COMPLETE** | schemas/playbook/, docs/playbook-layer.md, docs/examples/ |
| S-F2F-02 | Playbook Validation Tool | proposed | tools/playbook/validate_playbook.py |
| S-F2F-03 | Dry-Run Replay + Review Queue | proposed | tools/playbook/replay_acquisition_playbook.py, review queue export |
| S-F2F-04 | Golden Dry-Run Tests | proposed | tests/playbook/ golden fixtures |
| S-F2F-05 | ODF-Flat Family Playbook | proposed | acquisition-packs/_families/odf-flat/ |
| S-F2F-06 | Apply-Mode Risk Review | proposed | Risk review doc only; apply mode NOT authorized |
| S-F2F-07 | Product Dependency Closure | proposed | docs/product-dependency-closure.md (design only) |
| S-F2F-08 | Product Skeleton/Stub Design | proposed | docs/product-skeleton-generator.md (design only) |

All phases after S-F2F-01 require separate human authorization prompts naming the taskcard.

---

## 20. S-F2F-01 Acceptance Criteria

S-F2F-01 is DONE when:

1. schemas/playbook/acquisition-playbook.schema.json — valid JSON, all required fields present.
2. schemas/playbook/review-queue.schema.json — valid JSON, all required fields present.
3. docs/playbook-layer.md — this document, 20 sections, all mandatory policy text present.
4. docs/examples/acquisition-playbook-fods-documentation-example.yaml — documentation only,
   status=documentation_example_only, not_for_execution=true.
5. ZERO tool files in tools/playbook/ — it must NOT exist.
6. ZERO playbook.yaml in acquisition-packs/fods/ or acquisition-packs/fodt/.
7. ZERO files in acquisition-packs/_families/.
8. BUNDLE_VALIDATION: PASS with --check-no-pending.
9. Git status clean after commit.
10. S-F2F-01 taskcard updated to completed_pending_independent_verification.
11. S-F2F-02 through S-F2F-08 remain proposed_pending_human_approval.
12. No MAIN SPRINT gate statuses changed.
13. No push performed.
