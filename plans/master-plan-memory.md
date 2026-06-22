# Master Plan Memory — Plan Lineage Ledger
# Format Factory Project
# Schema version: 1.0
# Created: 2026-06-22
# Maintained by: plan governance system

## PURPOSE

This file is the **durable plan lineage ledger** for the format-factory project.

It records all per-chat plan files that have been created, executed, and closed across sessions.
Session-keyed lock files in `.local/supervisor/plan-locks/` expire after 7 days.
This ledger provides the permanent historical record.

---

## FORBIDDEN: This File Must NOT Be Used As

- Active execution plan
- Hardening target for any per-chat or sprint plan
- Sprint audit amendment target
- Source of taskcard mutations during execution
- Redirect target for agent writes
- Override of explicit `active_plan_path` binding from a loaded per-chat plan

Violation of these rules constitutes a **plan governance failure**.
If any agent writes taskcard content, sprint prompts, execution instructions,
or `next-sprint` content to this file, that is a production bug.

---

## PERMITTED: This File May Only

- Record plan lineage history (LEDGER-N entries)
- Record terminal lock metadata for closed plans
- Record plan hashes at close time (or "unknown" if not captured)
- Serve as audit trail for plan lifecycle events
- Receive new LEDGER-N entries when new plans complete

Ledger annotation is the ONLY permitted post-close action for terminal plans.

---

## Entry Schema

```yaml
plan_ledger_entry:
  ledger_entry_id: LEDGER-<N>
  mission_id: <plan-name-without-extension>
  repository: format-factory
  branch: main
  plan_path: <absolute or relative path>
  plan_hash: <sha256 or "unknown">
  plan_status: ACTIVE | TERMINAL_CLOSED | COMPLETE | DEFERRED | SUPERSEDED
  created_at: <ISO 8601 or approximate>
  created_by: <agent or human>
  hardened_at: <ISO 8601 or null>
  executed_runs: []
  sprint_audits: []
  evidence_roots: []
  terminal_lock:
    locked_at: <ISO 8601>
    locked_by: <session_id>
    lock_state: TERMINAL_CLOSED | COMPLETE | DEFERRED
    mutation_policy: "no further plan/hardening/execution writes"
    allowed_post_close_actions:
      - ledger annotation only
  final_verdict: <verdict string or null>
  supersedes: []
  superseded_by: null
  notes: ""
```

---

## Plan Ledger Entries

---

### LEDGER-001 — snoopy-juggling-seal

```yaml
ledger_entry_id: LEDGER-001
mission_id: snoopy-juggling-seal
repository: format-factory
branch: main
plan_path: plans/snoopy-juggling-seal.md
plan_hash: unknown
plan_status: ACTIVE
created_at: "2026-06-16 (approximate — version 3.0)"
created_by: autonomous-agent
plan_description: >
  SAL (Specification Authority Layer) source-to-consumption pipeline
  forensics and redesign plan. Currently at v3.12. Contains 30 sections,
  30+ taskcards (TC-SAL-*, TC-HARD-*, TC-ZS-*, TC-FODT-*, TC-SA-HEAL-*).
  Zero-stub audit hardening incorporated at v3.11. Continuously evolving.
plan_version_at_entry: "3.12"
terminal_lock: null
final_verdict: null
notes: >
  IMPORTANT: This file is NOT a global fallback for plan amendments.
  It is the SAL forensics plan. Agents must NOT write hardening
  changes from other per-chat plans into this file.
  See CLAUDE.md Plan Hardening section for the plan file identity rule.
```

---

### LEDGER-002 — sunny-crunching-cherny

```yaml
ledger_entry_id: LEDGER-002
mission_id: sunny-crunching-cherny
repository: format-factory
branch: main
plan_path: C:/Users/prora/.claude/plans/sunny-crunching-cherny.md
plan_hash: unknown
plan_status: TERMINAL_CLOSED
created_at: "2026-06-21 (approximate)"
created_by: autonomous-agent
plan_description: >
  Per-chat plan to harden snoopy-juggling-seal.md with Zero-Stub Audit
  (ZERO-STUB-AUDIT-20260621) findings. 5 edits to snoopy: version bump
  3.10→3.11, TC-HARD-007 status update, §29 register row, §30 section
  (TC-ZS-001..006), anti-overclaim rule #12.
hardened_at: "2026-06-21 (within plan)"
executed_runs: [pgov-20260622-085859]
evidence_roots:
  - .local/evidences/pgov-20260622-085859/
terminal_lock:
  locked_at: "2026-06-22T09:01:17.145423+00:00"
  locked_by: "59511d3f9256"
  lock_state: TERMINAL_CLOSED
  mutation_policy: "no further plan/hardening/execution writes"
  allowed_post_close_actions:
    - ledger annotation only
final_verdict: PLAN_GOVERNANCE_ACCEPTED_VERIFIED
notes: >
  All 5 edits confirmed VERIFIED_PRESENT in snoopy v3.12.
  Terminal lock written by TC-PLAND-003 (enumerated-wibbling-torvalds execution).
  Evidence at .local/evidences/pgov-20260622-085859/sunny-terminal-lock.json
```

---

### LEDGER-003 — floating-stargazing-globe

```yaml
ledger_entry_id: LEDGER-003
mission_id: floating-stargazing-globe
repository: format-factory
branch: main
plan_path: C:/Users/prora/.claude/plans/floating-stargazing-globe.md
plan_hash: unknown
plan_status: TERMINAL_CLOSED
created_at: "2026-06-22 (approximate)"
created_by: autonomous-agent
plan_description: >
  Per-chat plan executed in session 59511d3f9256. Plan file no longer
  exists on disk. Marked TERMINAL_CLOSED and COMPLETE by TC-STREAM-HEAL-001.
terminal_lock:
  locked_at: "2026-06-22T08:15:08+00:00"
  locked_by: "59511d3f9256"
  lock_state: TERMINAL_CLOSED
  mutation_policy: "no further plan/hardening/execution writes"
completion_reason: "Plan file does not exist on disk. TC-STREAM-HEAL-001 cleanup."
final_verdict: null
notes: >
  File no longer exists. Lock was written by TC-STREAM-HEAL-001.
```

---

### LEDGER-004 — polished-hopping-glacier

```yaml
ledger_entry_id: LEDGER-004
mission_id: polished-hopping-glacier
repository: format-factory
branch: main
plan_path: C:/Users/prora/.claude/plans/polished-hopping-glacier.md
plan_hash: unknown
plan_status: TERMINAL_CLOSED
created_at: "2026-06-21 (approximate)"
created_by: autonomous-agent
plan_description: Per-chat plan. Two locks exist for this plan from different sessions.
terminal_lock:
  - locked_at: "2026-06-21T18:34:45.426910+00:00"
    locked_by: "24bf75a51998"
    lock_state: TERMINAL_CLOSED
  - locked_at: "2026-06-21T07:05:09.696662+00:00"
    locked_by: "45da76b0e59c"
    lock_state: COMPLETE
final_verdict: null
notes: >
  Two sessions locked this plan (COMPLETE then TERMINAL_CLOSED from different sessions).
  Older lock (45da76b0e59c) shows COMPLETE; newer lock (24bf75a51998) shows TERMINAL_CLOSED.
```

---

### LEDGER-005 — indexed-crafting-peacock

```yaml
ledger_entry_id: LEDGER-005
mission_id: indexed-crafting-peacock
repository: format-factory
branch: main
plan_path: C:/Users/prora/.claude/plans/indexed-crafting-peacock.md
plan_hash: unknown
plan_status: DEFERRED
created_at: "2026-06-21 (approximate)"
created_by: autonomous-agent
plan_description: >
  Per-chat plan with not_attempted and partially_done tasks.
  Originating session 7c0655b93790 became stale.
deferred_at: "2026-06-22T08:11:14.723233+00:00"
deferred_by: "7c0655b93790"
deferred_reason: >
  Originating session 7c0655b93790 is no longer active (lock stale since
  2026-06-21T17:40). Plan has not_attempted and partially_done tasks.
  Marked DEFERRED by TC-STREAM-HEAL-001 to unblock continuation pipeline
  stream_field_match. Work must resume in a new authorized session.
final_verdict: null
notes: >
  Plan work was not completed. Deferred pending explicit reauthorization.
  A new per-chat session must explicitly adopt this plan before resuming.
```

---

### LEDGER-006 — enumerated-wibbling-torvalds

```yaml
ledger_entry_id: LEDGER-006
mission_id: enumerated-wibbling-torvalds
repository: format-factory
branch: main
plan_path: C:/Users/prora/.claude/plans/enumerated-wibbling-torvalds.md
plan_hash: unknown
plan_status: TERMINAL_CLOSED
created_at: "2026-06-22"
created_by: autonomous-agent
plan_description: >
  Plan file governance + locking + ledger + autonomous execution healing.
  9 parent taskcards (TC-PLAND-000 through TC-PLAND-008).
  Verifies 5 snoopy edits, creates this ledger file, writes terminal lock for
  sunny-crunching-cherny.md, extends write_plan_lock.py with binding contract,
  fixes CLAUDE.md plan hardening section, creates governance test suite.
executed_runs: [pgov-20260622-085859]
evidence_roots:
  - .local/evidences/pgov-20260622-085859/
terminal_lock:
  locked_at: "2026-06-22T09:45:00+00:00"
  locked_by: "59511d3f9256"
  lock_state: TERMINAL_CLOSED
  mutation_policy: "no further plan/hardening/execution writes"
  allowed_post_close_actions:
    - ledger annotation only
final_verdict: PLAN_GOVERNANCE_ACCEPTED_VERIFIED
notes: >
  Terminal lock written at TC-PLAND-008-03. This file (master-plan-memory.md)
  created as TC-PLAND-004 deliverable. Evidence root: .local/evidences/pgov-20260622-085859/
```
