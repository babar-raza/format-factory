# Format Factory — Kilo Agent Instructions

> **Status:** UNVERIFIABLE_PLATFORM_UNKNOWN — Kilo platform capabilities have not been confirmed
> via a live agent run. These instructions define the intended lifecycle but cannot be validated.
> Per TC-ACP-001-01 (FF-AGENTS-PARITY-001, 2026-07-13): Kilo has no documented integration with
> Format Factory governance infrastructure. All sections below marked with [UNKNOWN] require
> live Kilo testing before they can be confirmed.
> See `docs/agents/bundles/kilo-bundle.yaml` for current capability surface.

---

## 1. Session Start [PARTIALLY_ACHIEVABLE]

Read the following files at session start (requires file-read capability):
1. `docs/agents/bundles/kilo-bundle.yaml` — discover all blocked capabilities and state paths
2. `AGENTS.md` — human-free autonomy doctrine
3. `plans/master-plan.md` — strategic direction
4. `docs/governance/kilo-adapter.md` — this adapter's full lifecycle contract
5. `docs/agents/canonical-agent-contract.yaml` — 22 RC lifecycle semantics

**BLOCKED_ON_KILO:** `CLAUDE.md` references Claude Code-specific mechanisms (Skill tool,
EnterPlanMode, plan-mode) that have no Kilo equivalent. Do NOT attempt to follow CLAUDE.md
directly — use `kilo-adapter.md` as the Kilo-specific authority.

## 2. Plan Binding [UNKNOWN]

If a plan is active (check `docs/agents/bundles/kilo-bundle.yaml` session_state paths):
1. Read `.local/supervisor/active-plan-lock.json` — identifies active plan and status
2. Execute ONLY the plan's pending taskcards
3. Update `last_taskcard` field after each taskcard completes [UNKNOWN if writeable]
4. When all taskcards done: set `status: COMPLETE` in the lock file [UNKNOWN]

**BLOCKED_ON_KILO (RC-004):** No KILO.md awareness mechanism confirmed in Kilo platform.
No plan-mode equivalent known. Route all plan binding decisions to Claude Code.

## 3. Skill-First Execution [BLOCKED_ON_KILO]

All source mutations must be preceded by a registered skill invocation.
See `docs/governance/kilo-adapter.md` for the execution contract.

**BLOCKED_ON_KILO (RC-016/RC-017):** Kilo has no skill dispatch mechanism.
All Kilo source mutations are UNGOVERNED until RC-016/RC-017 are resolved on the platform.
Before any mutation: file a `BLOCKED_SKILL_GAP` record at `.local/taskcards/SKILL-GAP-<timestamp>.yaml`.

## 4. Pre-Mutation Guard [UNKNOWN]

If Kilo can execute Python scripts:
```
python tools/governance/pre_mutation_guard.py \
    --agent-type KILO \
    --task-id <task-id> \
    --skill-id <skill-id> \
    --target-paths <file-paths>
```

If Kilo CANNOT execute scripts: **BLOCKED_ON_KILO** — do not proceed with mutation.
Route to Claude Code for all mutations requiring governance guard.

## 5. Evidence Declaration [UNKNOWN]

If Kilo can write files and execute Python:
1. Write `.local/evidences/<run_id>/evidence-declaration.yaml` with all required fields
2. Run: `python tools/supervisor/sprint_executor_validate.py <path> --repair`
3. Fix all FAIL errors
4. Run: `python tools/supervisor/autonomous_cycle.py --declaration <path>`

If Kilo CANNOT execute scripts: **BLOCKED_ON_KILO** — evidence generation requires Claude Code.

## 6. Blocked Capabilities

These RC capabilities are BLOCKED on Kilo with routing to alternative agent:

| RC | Capability | Reason | Route To |
|----|-----------|--------|---------|
| RC-004 | load_instruction_files | KILO.md awareness unconfirmed | Claude Code |
| RC-016 | invoke_skills_by_name | No skill dispatch mechanism | Claude Code |
| RC-017 | enforce_skill_first_policy | No enforcement hook | Claude Code |
| RC-022 | multi_sprint_autonomous_loop | Unknown if autonomous loop supported | Claude Code |

All other capabilities: UNVERIFIABLE_PLATFORM_UNKNOWN — see `docs/agents/agent-inventory.yaml`
kilo entries for current status. Route to Claude Code for any capability not confirmed on Kilo.

## Coordination Preflight (MANDATORY — Mission AGENT-COORD-2026-07-15)

Kilo shares the working tree with concurrent agents. Before any mutation,
follow `docs/governance/kilo-adapter.md` section 2a: `register` at entry,
`claim` before writing, `preflight` before / `record-write` after each write,
`heartbeat` periodically, `release` + `complete` on exit — all via
`python -m tools.supervisor.coordination <verb>`. Never `git add -A`, never
clean/revert unexplained changes, never touch files under another agent's
lease. Rules: AGENTS.md Section CO.

## Full Reference

- `docs/governance/kilo-adapter.md` — full lifecycle contract (8 sections)
- `docs/agents/bundles/kilo-bundle.yaml` — capability bundle (0 available until kilo_supported: true set)
- `docs/agents/canonical-agent-contract.yaml` — canonical RC lifecycle semantics
- `docs/agents/kilo-platform-capabilities.md` — platform capability research (TC-ACP-001-01)
