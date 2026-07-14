# Format Factory — Kilo Agent Governance Adapter

> **Status:** UNVERIFIABLE_PLATFORM_UNKNOWN (TC-ACP-009, FF-AGENTS-PARITY-001, 2026-07-13)
> Kilo platform capabilities have not been confirmed via live agent run.
> This adapter documents the intended contract but all sections marked [UNKNOWN] await validation.

**This file is the Kilo entry point for skill-only governance.**
**It is subordinate to `docs/governance/skill-only-policy.yaml` — the canonical authority.**

---

## 1. Entry Point

At session start, read `docs/agents/bundles/kilo-bundle.yaml` to discover:
- Blocked capabilities (bundle.blocked_capabilities)
- Session state paths (bundle.session_state)
- Governance files to read (bundle.governance)

Current bundle status: **0 capabilities available** (all require `kilo_supported: true` in
skill-registry.yaml; per-skill classification deferred pending Kilo instantiation).

## 2. Execution Contract [PARTIAL — Codex-parallel, Kilo-native]

When executing tasks:

1. **Read** — Read all governance files from `kilo-bundle.yaml` bundle.governance list
2. **Check** — Read `active-plan-lock.json`; if a plan is active, follow ONLY that plan [UNKNOWN if writeable]
3. **Guard** — Before any mutation, run `pre_mutation_guard.py --agent-type KILO` [UNKNOWN if script exec available]
4. **Skill** — BLOCKED: Kilo has no skill dispatch mechanism. All mutations are ungoverned until resolved [RC-016]
5. **Declare** — Write `evidence-declaration.yaml`; run `sprint_executor_validate.py --repair` [UNKNOWN]
6. **Review** — Run `autonomous_cycle.py` for sprint review [UNKNOWN]
7. **Continue** — Read `continuation-signal.json`; verify session_id before consuming [UNKNOWN]

## 3. State File Paths

| File | Purpose |
|------|---------|
| `.local/supervisor/continuation-signal.json` | Sprint continuation verdict |
| `.local/supervisor/active-plan-lock.json` | Active per-chat plan lock |
| `reports/supervisor/session-resume.md` | Session state after context compaction |
| `reports/supervisor/next-sprint.md` | Next sprint tasks (when no plan active) |

## 4. Evidence Generation Flow [UNKNOWN]

If Kilo supports Python script execution:
1. Write `.local/evidences/<run_id>/evidence-declaration.yaml`
2. Validate: `python tools/supervisor/sprint_executor_validate.py <path> --repair`
3. Submit: `python tools/supervisor/autonomous_cycle.py --declaration <path>`

If not: route evidence generation to Claude Code.

## 5. Pre-Mutation Guard Invocation [UNKNOWN]

```bash
python tools/governance/pre_mutation_guard.py \
    --agent-type KILO \
    --task-id <task-id> \
    --skill-id <skill-id> \
    --target-paths <space-separated-paths>
```

Exit codes: 0=AUTHORIZED, 1=BLOCKED, 2=CONFIG_ERROR.
If BLOCKED: do not proceed; file SKILL-GAP record.

## 6. Missing Skill Workflow [UNKNOWN]

When a required skill is not in `.supervisor/skill-registry.yaml`:
1. Write `.local/taskcards/SKILL-GAP-<timestamp>.yaml` with work_type and reason
2. Stop work on that task type
3. Route to Claude Code for skill registration via `/check-skill-coverage`

## 7. Known Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| No KILO.md awareness pre-2026-07-13 | Platform doesn't load governance at session start | Added .kilo/KILO.md now; effectiveness unconfirmed |
| No skill dispatch (RC-016) | All mutations are ungoverned | Route all mutations to Claude Code |
| Script execution unknown | Cannot run governance validators | Route validation to Claude Code |
| Multi-sprint loop unknown (RC-022) | Cannot self-continue | Use Claude Code for autonomous loops |
| kilo_supported defaults false | 0 capabilities available | Defer until Kilo instantiation and live testing |

## 8. Blocked Capabilities with Routing

| RC | Capability | Blocking Reason | Route To |
|----|-----------|----------------|---------|
| RC-004 | load_instruction_files | KILO.md awareness unconfirmed | Claude Code (RC confirmed VERIFIED) |
| RC-016 | invoke_skills_by_name | No skill dispatch mechanism | Claude Code |
| RC-017 | enforce_skill_first_policy | No enforcement hook | Claude Code |
| RC-022 | multi_sprint_autonomous_loop | Autonomous loop capability unknown | Claude Code |

For all other RC capabilities: `UNVERIFIABLE_PLATFORM_UNKNOWN` — route to Claude Code until
live Kilo testing confirms achievability. See `docs/agents/agent-inventory.yaml` kilo entries.

---

**Related files:**
- `.kilo/KILO.md` — Kilo session start instructions
- `docs/agents/bundles/kilo-bundle.yaml` — machine-readable capability bundle
- `docs/agents/kilo-platform-capabilities.md` — platform research (TC-ACP-001-01)
- `docs/agents/canonical-agent-contract.yaml` — canonical RC lifecycle semantics
