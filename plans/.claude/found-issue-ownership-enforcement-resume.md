# Resume: Complete FI-027 / FI-028 / FI-030 (successor to found-issue-ownership-enforcement)

**mission_id:** FOUND-ISSUE-OWNERSHIP-ENFORCEMENT-RESUME-2026-07-17
**parent_mission:** FOUND-ISSUE-OWNERSHIP-ENFORCEMENT-2026-07-17 (TERMINAL_CLOSED, `plans/.claude/found-issue-ownership-enforcement.md`)

## Context

The parent mission is done: 4 of 6 taskcards genuinely `CLOSED` and verified (the
allowlist-disposition fix, the ambient closure-time guard, `FI-025`'s dead-code
cleanup, and verifiable-evidence-for-conflict-resolution). The remaining 2
(`TC-FIX-001`, `TC-STRUCT-004`) are marked `EXCLUDED` — not abandoned, not
incomplete work papered over, but a **verified** external block: 4 specific
files needed for 3 registered found-issues (`FI-027`, `FI-028`, `FI-030`) are
under an exclusive lease held by a different, genuinely and continuously
active concurrent agent (`agent-claude-code-20260717T060141-e225cd`, running
its own large `PORTFOLIO-AUDIT-2026-07-16` mission). This was re-verified
multiple times this session with materially different methods each time
(direct governed-takeover attempts, an independent git-history check for
whether their work had already landed, and an analysis of whether a
non-overlapping line-level edit could safely bypass the file-level lock) —
every check confirms the same thing: still genuinely blocked, not assumed.

The parent plan file carries its own `mutation_policy: "no further
plan/hardening/execution writes"` now that it is `TERMINAL_CLOSED` — correctly
so; it should not be reopened for this. This is a **successor plan**, scoped
*only* to finishing the 3 already-fully-designed, already-registered fixes the
moment the external block clears. No new scope, no new design work — the
"what to do" is already fully specified in `registry/found-issue-register.yaml`
(`FI-027`, `FI-028`, `FI-030`) and the parent plan's own Execution Log; this
plan exists so a future session (or a later point in this one) can execute
efficiently without re-deriving context, and so the resume work itself is
taskcard-tracked rather than ad hoc.

## What's blocked, and exactly what finishing it means

All 4 required files are under `agent-claude-code-20260717T060141-e225cd`'s
lease: `.claude/commands/reconcile-contract-capabilities.md`,
`tools/supervisor/autonomous_cycle.py`,
`registry/governance/validator-id-authority.yaml`,
`tools/supervisor/governance_validator_runner.py`.

- **FI-027** (`reconcile-contract-capabilities.md` stale command-hash): commit
  the already-verified-legitimate uncommitted edit (2 documentation bullets
  referencing real validators V247/V248) → refresh
  `reports/skills-first-control/command-skill-hash-baseline.json`'s entry for
  this file → re-run `validate_skills_first_control.py`, confirm the HIGH
  finding clears → set `FI-027`'s disposition to `HEALED_AND_VERIFIED` with
  evidence.
- **FI-028** (`autonomous_cycle.py`'s 4 `write_journal` enum-bug call sites):
  apply the identical `op="edit", source="cli"` fix already shipped this
  session to the 6 sibling sites (`write_plan_lock.py` ×3,
  `lifecycle_audit.py` ×1, `sprint_executor.py` ×2) → run the file's existing
  tests + a full `tests/governance/`/`tests/supervisor/` regression → set
  `FI-028`'s disposition to `HEALED_AND_VERIFIED`.
- **FI-030** (`V252` wiring): add a `V252` entry to
  `registry/governance/validator-id-authority.yaml` → wire its dispatch into
  `governance_validator_runner.py`'s `run_all_governance_validators()`
  (explicit import + call, matching the existing V194-V196 pattern — the
  `@validator` decorator does not auto-register) → surface `V252`'s
  aged-findings output into `reports/supervisor/session-resume.md`'s
  generation step in `autonomous_cycle.py` → set `FI-030`'s disposition to
  `HEALED_AND_VERIFIED`.

**Important caution for whoever executes this:** by the time this unblocks,
the other agent's own work will very likely have landed via their own commits
— `governance_validator_runner.py` alone carried a +407/-55 uncommitted diff
at last check (substantial, real, unrelated validator additions).
**Re-read every file fresh before editing** — do not assume its content still
matches what this plan or the parent mission's notes describe from memory.

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-RESUME-001 | PENDING |

## Taskcards

### TC-RESUME-001 — Complete FI-027 / FI-028 / FI-030 once unblocked

**Trigger condition:** a fresh check (`python -m tools.supervisor.coordination status`,
or a direct `coordination takeover --lease <id>` dry-run) shows
`agent-claude-code-20260717T060141-e225cd` no longer holds
`lease-9be32fa9df`, `lease-46db2d424c`, `lease-711c2454d3`, or
`lease-d745d84477` as genuinely `ACTIVE` (released, reassigned, or the agent
is confirmed gone).

**Steps:** for each of the 3 sub-fixes above — re-read the target file(s)
fresh (do not trust memory of prior content), apply the fix, run its
targeted tests, run the full `tests/governance/` suite, update the
corresponding `found-issue-register.yaml` entry's `disposition` to
`HEALED_AND_VERIFIED` with real evidence (test output, hash comparison, or
validator PASS), and commit. If any file's content has materially changed
from what's described above (the other agent's own work landed
differently than expected), re-derive the fix from current reality rather
than blindly applying the old diff.

**Do not** reopen or edit `plans/.claude/found-issue-ownership-enforcement.md`
— it stays `TERMINAL_CLOSED`. Completion is tracked entirely via this
successor plan and the `found-issue-register.yaml` disposition updates.

**Closure:** once all 3 dispositions are `HEALED_AND_VERIFIED`, run
`validate_skills_first_control.py` to confirm 0 CRITICAL/HIGH, then close
this successor plan via the normal `write_plan_lock.py --terminal --audit-gate`
flow.

## Non-goals

- No new design work. The 4 "remaining, narrower limits" documented in the
  parent plan's own Residual Risks section (e.g., the sub-48h attribution
  gap, the prose-disclosure self-attestation limit) are explicitly **not**
  in scope here — confirmed with the user as out of scope for this plan.
- No changes to any file not already named above.

## Verification

- `validate_skills_first_control.py` — 0 CRITICAL/HIGH after all 3 fixes.
- Full `tests/governance/` suite — no regressions (baseline before this
  plan: 152/153, the 1 failure being `FI-027` itself, so 153/153 expected
  once fixed).
- Each `found-issue-register.yaml` entry's `verification_verdict` filled in
  with real evidence, not left null.

