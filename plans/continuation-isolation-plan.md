# Per-Chat Continuation Isolation — Production Plan

**Authority:** This is the authoritative plan for continuation state isolation.
**Plan ID:** CCI-PLAN-001
**Created:** 2026-06-16
**Status:** READY_FOR_IMPLEMENTATION

---

## 1. Authority Declaration

This plan governs all continuation state isolation work. It enhances (does not replace) the existing autonomous supervision architecture defined in `plans/spec-to-feature-radical-correction-plan.md`. No competing continuation isolation plan may be created.

## 2. Incident Summary

**Reported symptom:** A user working on task X in Chat A found that continuation resumed with task Y from Chat B. The autonomous loop picked up another chat's work context.

**Severity:** SEV2 — Cross-chat continuation selects wrong task; source mutations possible if the wrong sprint executes.

**Root cause (confirmed):** All continuation state is stored in global singleton files with zero chat/session/mission identity. Any chat that reads these files inherits whatever the last chat wrote.

## 3. Continuation Isolation Requirement

Every continuation must be scoped by explicit identity. A continuation created in Chat A must never be consumed by Chat B unless an explicit governed handoff occurs. The system must fail closed on ambiguity rather than defaulting to "latest file wins."

## 4. Current-State Evidence

### 4.1 Global Singleton State Files (Zero Identity Scoping)

| File | Path | Scoping | Identity Fields |
|------|------|---------|-----------------|
| continuation-signal.json | `.local/supervisor/continuation-signal.json` | **GLOBAL** | source_sprint_id only |
| active-continuation.json | `.local/supervisor/active-continuation.json` | **GLOBAL** | sprint_id, prior_run_id |
| next-action.json | `.local/supervisor/next-action.json` | **GLOBAL** | prior_sprint_id |
| next-work-items.json | `.local/supervisor/next-work-items.json` | **GLOBAL** | run_id, sprint_id |
| orchestrator-state.json | `.local/supervisor/orchestrator-state.json` | **GLOBAL** | orchestrator_run_id |
| current-run.json | `.supervisor/state/current-run.json` | **GLOBAL** | sprint_id |
| session-resume.md | `reports/supervisor/session-resume.md` | **GLOBAL** | None |
| next-sprint.md | `reports/supervisor/next-sprint.md` | **GLOBAL** | sprint_id |
| approval-gates.md | `reports/supervisor/approval-gates.md` | **GLOBAL** | sprint_id |
| action-queue.jsonl | `.local/supervisor/action-queue.jsonl` | **GLOBAL** | per-item action_id |

**Finding: Zero files carry chat_id, conversation_id, session_id, or mission_id. The grep across all supervisor tools and all `.local/supervisor/` state files returned zero matches for these identity fields.**

### 4.2 Continuation Decision Flow

```
Chat starts
  → CLAUDE.md says: read session-resume.md
  → session-resume.md says: run check_continuation.py
  → check_continuation.py reads:
      1. .local/supervisor/continuation-signal.json (GLOBAL)
      2. reports/supervisor/approval-gates.md (GLOBAL)
      3. .local/supervisor/next-work-items.json (GLOBAL)
  → If CONTINUE: read next-work-items.json + next-sprint.md
  → Execute sprint
  → Sprint closeout writes:
      1. evidence-declaration.yaml (scoped by run_id in path)
      2. supervisor_loop.py autonomous-cycle generates:
         - evidence-review.json (GLOBAL)
         - contradictions.json (GLOBAL)
         - session-resume.md (GLOBAL)
         - approval-gates.md (GLOBAL)
         - next-sprint.md (GLOBAL)
         - continuation-signal.json (GLOBAL)
      3. evidence_continuation.py writes:
         - next-action.json (GLOBAL)
         - active-continuation.json (GLOBAL)
  → Next chat reads these GLOBAL files and inherits this chat's context
```

### 4.3 Claude Auto-Memory (Cross-Chat Contamination Vector)

`C:\Users\prora\.claude\projects\...\memory\MEMORY.md` persists across ALL conversations for this project. It contains:
- Sprint numbers, run IDs, SHA hashes from prior sessions
- "Latest" state descriptions that may be stale
- Task context from different missions

This is a secondary contamination vector: even without shared files, memory text can redirect a new chat toward an old mission.

## 5. Symptoms

| ID | Symptom | Why Insufficient as Root Cause |
|----|---------|-------------------------------|
| SYM-001 | Wrong task resumed in new chat | Symptom of state selection, not the cause |
| SYM-002 | next-sprint.md contains another chat's work | Result of global overwrite, not the mechanism |
| SYM-003 | continuation-signal.json reflects stale sprint | Produced by last-writer-wins, not by missing validation |
| SYM-004 | Auto-memory references outdated sprint context | Memory is a secondary vector; primary is file state |
| SYM-005 | TODO list replaced with unrelated tasks | Chat reads global next-work-items.json without identity check |

## 6. Root Causes

### RC-001: Zero Chat/Session Identity in Continuation State

**First failing boundary:** continuation-signal.json has no `chat_id` field.
**Immediate cause:** `check_continuation.py` reads this file without any identity filter.
**Underlying cause:** The entire continuation state model was designed for single-chat operation. Identity was never part of the schema.
**Affected components:** check_continuation.py, continuation_state.py, continuation_router.py, evidence_continuation.py, supervisor_loop.py
**Why prior analysis missed it:** The system was built incrementally for single-chat autonomous loops.

### RC-002: Global Singleton File Layout

**First failing boundary:** All state files live in a single flat directory `.local/supervisor/`.
**Immediate cause:** Any chat writing to this directory overwrites the previous chat's state.
**Underlying cause:** No per-chat or per-mission namespace in the file layout.

### RC-003: Last-Writer-Wins Overwrite Semantics

**First failing boundary:** `_save_json()` in continuation_state.py unconditionally overwrites.
**Immediate cause:** No compare-and-swap, no consumed marker, no conflict detection.
**Underlying cause:** Single-writer assumption baked into all producers.

### RC-004: No Consumed-Event Tracking

**First failing boundary:** No mechanism marks a continuation artifact as "consumed by Chat X."
**Immediate cause:** A second chat can re-consume the same continuation.
**Underlying cause:** Append-only event log was never implemented.

### RC-005: session-resume.md Used as Authoritative Continuation Source

**First failing boundary:** CLAUDE.md mandates reading session-resume.md at start.
**Immediate cause:** session-resume.md is global and reflects the last chat's closeout.
**Underlying cause:** Session resume was designed as a human-readable summary, not a scoped continuation token.

### RC-006: Auto-Memory Cross-Session Contamination

**First failing boundary:** MEMORY.md is shared across all conversations for this project.
**Immediate cause:** Memory contains sprint IDs, task context, and "latest state" that may redirect.
**Underlying cause:** Claude auto-memory has no per-conversation isolation by design.

## 7. Structural Weaknesses

| ID | Weakness | Impact |
|----|----------|--------|
| SW-001 | No identity envelope schema | Cannot filter by chat/mission |
| SW-002 | No continuation ledger | Cannot track consumed/superseded state |
| SW-003 | No per-chat state root | All chats share one directory |
| SW-004 | No conflict detection | Concurrent chats silently overwrite |
| SW-005 | No stale-state garbage collection | Old continuations persist indefinitely |
| SW-006 | No fail-closed on ambiguity | System picks "latest" when multiple exist |
| SW-007 | No cross-chat regression tests | Issue was never tested for |
| SW-008 | No consumed markers | Continuations can be re-consumed |
| SW-009 | Markdown files used as state | session-resume.md parsed as continuation input |
| SW-010 | Memory used as authority | Auto-memory can override durable state |

## 8. Preserve vs. Redesign Decisions

### Preserve (Working)
- **Taskcard-based continuation:** Taskcards carry their own identity and state.
- **Evidence declarations:** Scoped by run_id in their directory path.
- **Autonomous rework:** Rework items are part of grading output, work correctly within a session.
- **Supervisor pipeline:** validate → inspect → grade → plan-next → generate packet works.
- **check_continuation.py logic:** The 7-condition check is sound; it just lacks identity filtering.
- **continuation_router.py safety checks:** Advisory rejection, action safety validation.

### Redesign (Broken for Multi-Chat)
- **continuation-signal.json:** Add identity envelope, move to scoped path.
- **active-continuation.json:** Add identity, move to scoped path.
- **next-action.json:** Scope per mission/chat.
- **session-resume.md:** Add identity header, or replace with scoped pointer.
- **next-sprint.md:** Add identity header.
- **next-work-items.json:** Scope per run.
- **check_continuation.py:** Add identity filtering before condition checks.
- **evidence_continuation.py:** Write to scoped paths.
- **Auto-memory guidance:** Add rules to prevent cross-mission contamination.

## 9. Selected Design: Option D — Hybrid Ledger + Per-Chat Artifact Roots

### Design Scorecard

| Criterion | A:MinFields | B:PerChat | C:Ledger | **D:Hybrid** | E:Namespace | F:Service | G:Prompts | H:Disable |
|-----------|:-----------:|:---------:|:--------:|:------------:|:-----------:|:---------:|:---------:|:---------:|
| Cross-chat isolation | 2 | 4 | 4 | **5** | 4 | 5 | 1 | 5 |
| Rerun consistency | 2 | 4 | 5 | **5** | 3 | 5 | 1 | 3 |
| Backward compat | 5 | 3 | 3 | **4** | 3 | 1 | 5 | 2 |
| Migration complexity | 5 | 3 | 3 | **3** | 3 | 1 | 5 | 2 |
| Implementation cost | 5 | 3 | 3 | **3** | 3 | 1 | 5 | 2 |
| Testability | 2 | 4 | 5 | **5** | 3 | 5 | 1 | 3 |
| Observability | 1 | 3 | 5 | **5** | 3 | 5 | 1 | 2 |
| Failure safety | 2 | 4 | 5 | **5** | 3 | 5 | 1 | 5 |
| Stale-state handling | 1 | 4 | 5 | **5** | 3 | 5 | 1 | 3 |
| Concurrency handling | 1 | 5 | 4 | **5** | 4 | 5 | 1 | 5 |
| Autonomous compat | 4 | 4 | 4 | **5** | 3 | 3 | 4 | 1 |
| Existing workflow | 5 | 3 | 3 | **4** | 3 | 1 | 5 | 1 |
| Override resistance | 1 | 4 | 5 | **5** | 4 | 5 | 1 | 5 |
| Maintainability | 4 | 3 | 3 | **4** | 3 | 2 | 5 | 3 |
| Usability | 4 | 3 | 3 | **4** | 3 | 2 | 4 | 2 |
| Durability | 1 | 4 | 5 | **5** | 3 | 5 | 1 | 3 |
| **Total** | **45** | **58** | **67** | **72** | **51** | **56** | **42** | **47** |

**Selected: Option D — Hybrid Ledger + Per-Chat Artifact Roots**

Rationale: Combines per-chat directory isolation (prevents overwrites) with a central ledger (enables conflict detection, consumed tracking, and observability). Preserves existing pipeline with adapters.

## 10. Identity Envelope

```yaml
continuation_identity:
  schema_version: 2
  chat_id: "<uuid or session identifier>"
  project_id: "format-factory"
  repository_id: "format-factory"
  repository_path: "C:/Users/prora/OneDrive/Documents/GitHub/format-factory"
  branch: "main"
  worktree_id: null
  mission_id: "<mission identifier, e.g., product-deepening-sprint-155>"
  plan_id: "spec-to-feature-radical-correction-plan"
  run_id: "<evidence run_id>"
  parent_run_id: "<prior run_id if continuation>"
  taskcard_root: "taskcards/"
  queue_root: ".local/supervisor/chats/<chat_id>/queue/"
  evidence_root: ".local/evidences/<run_id>/"
  controller_type: "interactive|headless"
  controller_instance_id: "<unique per controller>"
  created_at: "<ISO timestamp>"
  updated_at: "<ISO timestamp>"
  last_consumed_at: null
  status: "active"  # active|paused|consumed|superseded|blocked|completed|quarantined
  resume_token: "<sha256 of state at creation>"
  content_digest: "<sha256 of continuation content>"
  state_digest: "<sha256 of full state snapshot>"
```

### Chat ID Resolution

Claude Code does not expose a native `chat_id`. Resolution strategy:
1. **Primary:** Generate a UUID at session start, store in `.local/supervisor/chats/<uuid>/identity.json`.
2. **Secondary:** If resuming, match by `mission_id` + `branch` + `repository_path` to find the correct chat root.
3. **Fallback:** If no match found and multiple active chats exist, fail closed and prompt user to select.

## 11. Continuation Ledger

### Schema: `.local/supervisor/continuation-ledger.jsonl`

Append-only JSONL file.

```yaml
continuation_event:
  event_id: "<uuid>"
  event_type: "created|consumed|superseded|paused|resumed|completed|blocked|quarantined|conflict_detected|migrated|rejected_identity_mismatch"
  timestamp: "<ISO>"
  chat_id: "<chat_id>"
  mission_id: "<mission_id>"
  run_id: "<run_id>"
  plan_id: "<plan_id>"
  artifact_path: "<path to continuation artifact>"
  artifact_digest: "<sha256>"
  controller_type: "<interactive|headless>"
  controller_instance_id: "<id>"
  consumed_by_chat_id: null
  superseded_by_event_id: null
  detail: "<human-readable detail>"
```

### Active State Pointer

`.local/supervisor/chats/<chat_id>/active-state.json`:
```json
{
  "chat_id": "<chat_id>",
  "mission_id": "<current mission>",
  "active_continuation_event_id": "<last created/resumed event>",
  "status": "active",
  "updated_at": "<ISO>"
}
```

## 12. Scoped Artifact Layout

```
.local/supervisor/
  continuation-ledger.jsonl          # Append-only event log
  chats/
    <chat_id>/
      identity.json                   # Chat identity envelope
      active-state.json               # Current active continuation pointer
      missions/
        <mission_id>/
          runs/
            <run_id>/
              continuation-signal.json
              active-continuation.json
              next-action.json
              next-work-items.json
              queue/
                action-queue.jsonl
              evidence-link.yaml
              controller-state.json
              resume.md
  # Legacy compatibility pointers (read-only, validated):
  continuation-signal.json            # Symlink/pointer to active chat's signal
  active-continuation.json            # Symlink/pointer to active chat's continuation
  next-work-items.json                # Symlink/pointer to active chat's work items
```

### Global Pointer Files

For backward compatibility, global files remain but become validated pointers:
- On write: update both scoped path and global pointer.
- On read: validate that global pointer matches active chat identity before use.
- On mismatch: reject and fail closed.

## 13. Selection Algorithm

```
1. Load chat identity from .local/supervisor/chats/<chat_id>/identity.json
   - If chat_id unknown: scan all chat dirs for matching mission_id + branch
   - If multiple matches: FAIL_CLOSED, prompt user
   - If no matches: create new chat identity

2. Load continuation ledger (.local/supervisor/continuation-ledger.jsonl)

3. Filter by exact chat_id → only this chat's events

4. Find latest "created" or "resumed" event not followed by
   "consumed", "superseded", "completed", or "quarantined"

5. If zero active continuations: check for global legacy artifacts
   - If legacy artifact exists and no other chat claims it: offer to migrate
   - Otherwise: start fresh

6. If exactly one active continuation: validate identity envelope
   - Match: project_id, repository_path, branch, mission_id
   - Any mismatch: REJECT, log rejection event
   - All match: RESUME

7. If multiple active continuations for same chat:
   - Apply deterministic tiebreaker: latest updated_at wins
   - Supersede all others
   - Log conflict_detected event

8. Record selection decision as ledger event

9. Mark consumed continuations when consumed

10. NEVER fall back to global latest file without identity validation
```

## 14. Controller Contract

### Supervisor Controller
- Receives chat identity at initialization
- Writes all outputs to scoped chat/mission/run directory
- Updates global pointer files with identity header
- Records all state transitions in continuation ledger
- Refuses to consume artifacts from other chats
- One controller per chat at a time

### Autonomous Cycle Controller
- Same identity contract as supervisor
- Preserves mission_id across cycles
- Increments run_id within mission
- Updates evidence root per run
- Records cycle events in ledger

### Ownership Rules
- Only the controller that created a continuation may consume it
- If controller crashes: continuation remains "active" until timeout or explicit resume
- Stale controller detection: heartbeat older than 30 minutes = stale
- Stale continuations may be claimed by same chat's new controller

## 15. Migration Plan

### Phase 1: Inventory (non-destructive)
1. Scan `.local/supervisor/` for all current state files
2. Read `continuation-signal.json`, `active-continuation.json`, etc.
3. Record current sprint_id, run_id, state
4. Create migration manifest

### Phase 2: Create Identity Infrastructure
1. Generate chat_id for current active session
2. Create `.local/supervisor/chats/<chat_id>/` directory
3. Initialize continuation ledger
4. Copy (not move) current state files to scoped location

### Phase 3: Add Identity to Global Files
1. Add `chat_id` field to continuation-signal.json
2. Add `chat_id` field to active-continuation.json
3. Both scoped and global copies updated

### Phase 4: Quarantine Ambiguous Artifacts
1. Any artifact without provable identity → `.local/supervisor/quarantine/`
2. Preserve for audit
3. Do not auto-promote to active state

### Phase 5: Activate Enforcement
1. Update `check_continuation.py` to require identity match
2. Update `evidence_continuation.py` to write scoped paths
3. Update `continuation_router.py` to filter by chat_id
4. Enable fail-closed behavior

## 16. Quarantine Policy

- Artifacts missing `chat_id`: quarantine unless only one chat has ever existed
- Artifacts with mismatched `mission_id`: quarantine
- Artifacts older than 7 days with no matching chat: quarantine
- Quarantined artifacts stored in `.local/supervisor/quarantine/<timestamp>/`
- Quarantine is permanent until explicit user review

## 17. Validators

| Validator | What It Checks | Fail Behavior |
|-----------|---------------|---------------|
| identity-presence | chat_id, mission_id, run_id present | REJECT |
| identity-match | chat_id matches active session | REJECT |
| repository-match | repository_path matches current | REJECT |
| branch-match | branch matches current (if required) | REJECT or WARN |
| consumed-reuse | artifact not already consumed | REJECT |
| superseded-reuse | artifact not superseded | REJECT |
| quarantined-select | artifact not quarantined | REJECT |
| stale-detection | artifact not older than threshold | WARN |
| global-latest-fallback | global file used without identity | REJECT |
| conflict-detection | multiple active for same chat | RESOLVE + LOG |
| evidence-root-match | evidence root matches chat | REJECT |
| controller-ownership | controller instance matches | REJECT or MIGRATE |

## 18. Observability

### Selection Log: `.local/supervisor/continuation-selection-log.jsonl`

Every continuation selection records:
```yaml
selection_event:
  timestamp: "<ISO>"
  active_chat_id: "<chat_id>"
  active_mission_id: "<mission_id>"
  candidate_count: <int>
  accepted_candidate:
    artifact_path: "<path>"
    event_id: "<ledger event>"
  rejected_candidates:
    - artifact: "<path>"
      reason: "<identity_mismatch|consumed|superseded|quarantined|stale>"
  ambiguity: <bool>
  fail_closed: <bool>
  selected_by: "<algorithm|user_selection|migration>"
```

### Reports (on-demand)
- Active continuations by chat
- Quarantined artifacts
- Cross-chat rejection events
- Stale continuations
- Controller ownership conflicts

## 19. Regression Tests

See `continuation-regression-test-plan.md` for the full 25-scenario suite.

Key scenarios:
1. Chat A and Chat B: correct isolation
2. Newer artifact from wrong chat: rejected
3. Missing chat_id: migration or quarantine
4. Consumed artifact: not reused
5. Summary vs. durable state: durable wins
6. Legacy unscoped artifact: quarantine
7. Interrupted run: resumes correctly
8. Multiple reruns: stable path

## 20. Rollout Plan

| Step | Action | Reversible | Risk |
|------|--------|------------|------|
| 1 | Add identity envelope schema | Yes | None |
| 2 | Add continuation ledger (append-only) | Yes | None |
| 3 | Create per-chat directory structure | Yes | Low |
| 4 | Update producers (dual-write: scoped + global) | Yes | Low |
| 5 | Update consumers (read scoped, fallback global) | Yes | Low |
| 6 | Add validators (warn mode) | Yes | None |
| 7 | Migrate legacy artifacts | Yes | Low |
| 8 | Enable fail-closed (enforce mode) | Yes | Medium |
| 9 | Run regression suite | N/A | None |
| 10 | Remove global fallback | Careful | Medium |

## 21. Rollback Plan

At any step:
1. Revert consumer changes to read global files (pre-step-5 behavior)
2. Global files are always written (dual-write), so rollback is safe
3. Continuation ledger is append-only, no data loss
4. Quarantined artifacts can be restored from quarantine directory
5. Per-chat directories can be removed without affecting global state

## 22. Tradeoffs and Limits

| Tradeoff | Impact | Mitigation |
|----------|--------|------------|
| Chat_id not natively available | Must generate UUID | Stable within session; resume by mission_id |
| Per-chat dirs increase file count | More files in .local/ | Cleanup policy for completed chats |
| Fail-closed reduces convenience | User must select on ambiguity | Clear error messages with options |
| Legacy artifacts quarantined | May lose continuation | One-time migration resolves |
| Stricter identity may block | Some continuations rejected | Warn mode before enforce mode |
| Memory contamination hard to prevent | Secondary vector | Add memory hygiene rules |

**Known limits:**
- If durable state was never written, recovery requires explicit user selection
- If two missions merged in working tree, reconstruction may be imperfect
- Chat_id is synthetic — must be managed carefully on resume

## 23. Gates

| Gate | Status | Evidence Required |
|------|--------|-------------------|
| CCI-0: Incident Reconstructed | **PASS** | Section 4-6 of this plan |
| CCI-1: Artifacts Inventoried | **PASS** | Section 4.1 |
| CCI-2: Root Causes Proven | **PASS** | Section 6 (RC-001 through RC-006) |
| CCI-3: Design Selected | **PASS** | Section 9 (Option D, score 72/80) |
| CCI-4: Identity Model Defined | **PASS** | Section 10 |
| CCI-5: Selection Algorithm Defined | **PASS** | Section 13 |
| CCI-6: Controller Contract Defined | **PASS** | Section 14 |
| CCI-7: Migration Defined | **PASS** | Section 15 |
| CCI-8: Regression Suite Defined | **PASS** | Section 19 |
| CCI-9: Production Readiness | **PASS_WITH_LIMITATIONS** | Implementation not yet executed |

## 24. Taskcards

| ID | Title | Status | Gate |
|----|-------|--------|------|
| TC-CCI-001 | Incident reconstruction | COMPLETE | CCI-0 |
| TC-CCI-002 | Continuation artifact inventory | COMPLETE | CCI-1 |
| TC-CCI-003 | Producer-consumer map | COMPLETE | CCI-1 |
| TC-CCI-004 | Unsafe selection-pattern audit | COMPLETE | CCI-2 |
| TC-CCI-005 | Root-cause register | COMPLETE | CCI-2 |
| TC-CCI-006 | Structural-weakness register | COMPLETE | CCI-2 |
| TC-CCI-007 | Preserve-vs-redesign decision record | COMPLETE | CCI-3 |
| TC-CCI-008 | Solution-option scorecard | COMPLETE | CCI-3 |
| TC-CCI-009 | Identity-envelope schema | READY | CCI-4 |
| TC-CCI-010 | Continuation-ledger schema | READY | CCI-4 |
| TC-CCI-011 | Scoped artifact layout | READY | CCI-5 |
| TC-CCI-012 | Selection algorithm implementation | READY | CCI-5 |
| TC-CCI-013 | Supervisor controller contract | READY | CCI-6 |
| TC-CCI-014 | Autonomous-cycle controller contract | READY | CCI-6 |
| TC-CCI-015 | Legacy migration and quarantine | READY | CCI-7 |
| TC-CCI-016 | Validators | READY | CCI-8 |
| TC-CCI-017 | Observability and selection logs | READY | CCI-8 |
| TC-CCI-018 | Multi-chat regression tests | READY | CCI-8 |
| TC-CCI-019 | Rerun consistency tests | READY | CCI-8 |
| TC-CCI-020 | Conflict and fail-closed tests | READY | CCI-8 |
| TC-CCI-021 | Rollout and rollback plan | READY | CCI-9 |
| TC-CCI-022 | Enhance authoritative plan (this doc) | COMPLETE | CCI-9 |
| TC-CCI-023 | Production-readiness verdict | PENDING | CCI-9 |

## 25. Production-Readiness Criteria

1. Identity envelope schema implemented and validated
2. Continuation ledger writing and reading works
3. Per-chat directory creation and isolation works
4. All producers write scoped + global (dual-write)
5. All consumers validate identity before reading
6. Fail-closed behavior activates on mismatch
7. Legacy migration completes for current state
8. All 25 regression scenarios pass
9. Two concurrent chat simulation passes
10. Rollback tested from each step

---

END OF PLAN
