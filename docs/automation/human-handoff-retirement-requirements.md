# Human-Handoff Retirement Requirements

## Problem Statement

The Format Factory development loop currently requires three manual human handoffs per sprint
that are not true approval gates:

1. Human carries evidence bundle from disk to ChatGPT web
2. ChatGPT reasons about evidence and writes next sprint prompt
3. Human carries next sprint prompt back to Claude Code

These three steps add 30–90 minutes of non-gate delay per sprint and require ChatGPT web
access (no paid OpenAI/ChatGPT API available).

## Constraints

- No paid OpenAI API
- No ChatGPT web automation (no Selenium, Puppeteer, Playwright)
- ChatGPT web is optional external auditor — NOT required every sprint
- Format Factory authority remains final (cannot be delegated to any tool)
- All human approval gates are preserved (just shifted to true gate events)

## Retirement Map

| Old (human does this) | New (automated) | Component |
|-----------------------|-----------------|-----------|
| Upload evidence bundle to ChatGPT | `discover_latest_evidence.py` finds bundle | Layer 2 |
| ChatGPT reviews evidence | `validate_evidence_for_supervisor.py` + evidence-review.md prompt | Layer 2+5 |
| ChatGPT detects contradictions | `compare_goal_to_evidence.py` | Layer 2 |
| ChatGPT writes next sprint prompt | `generate_supervisor_packet.py` writes next-sprint.md | Layer 2+5 |
| Human pastes prompt into Claude Code | TM imports next-sprint-taskmaster.json | Layer 3 |
| Human selects parallel work | Ruflo consumes next-ruflo-lanes.json | Layer 4 |
| Human remembers project state | `.supervisor/project-memory.md` synced | Layer 2 |
| Human decides continue/stop | Approval gate classifier (8 outcomes) | Layer 2 |

## True Approval Gates (Preserved — Human Required)

These are NOT retired. They require human approval:

1. **G11-G Gate Approval** — commercial product readiness (Babar Raza, always)
2. **MCP Activation (MODE 4)** — registers MCP servers system-wide (explicit written approval)
3. **Push/Merge** — any git push to remote (explicit per-session approval)
4. **Credentials** — API keys, secrets, paid service configuration
5. **Destructive Operations** — rm -rf, force-push, schema deletion
6. **Governance Conflicts** — unresolvable contradictions in AGENTS.md or GOVERNANCE.md

## KPI Targets

| KPI | Baseline (manual) | Target (MODE 5) |
|-----|------------------|-----------------|
| Manual upload actions per sprint | 1 | 0 |
| Manual copy-paste events per sprint | 2 | 0 (non-gate sprints) |
| ChatGPT review sessions required | 1/sprint | 0 (optional only) |
| Time bundle → next sprint artifact (minutes) | 30–90 | < 10 |
| Human interventions not at true gates | 2–4/sprint | 0 |
| Successful autonomous loop iterations | 0 (baseline) | Measured per sprint |

## Phase Model

| Mode | Name | Human Gate? |
|------|------|-------------|
| MODE 0 | PLAN_HEALING | Not needed — plan normalization only |
| MODE 1 | LOCAL_SUPERVISOR_FOUNDATION | Not needed — local implementation |
| MODE 2 | LOCAL_SUPERVISOR_REPLAY | Not needed — local replay/hardening |
| MODE 3 | TASKMASTER_RUFLO_LOCAL_DRY_RUN | Not needed — local dry run |
| MODE 4 | ACTIVE_MCP_ACTIVATION | **REQUIRED** — system-level MCP change |
| MODE 5 | AUTONOMOUS_SPRINT_LOOP_RC | **REQUIRED** — first full autonomous run |

Internal promotion from MODE 0→1→2→3 is automatic if local evidence gates pass.
No human needed until MCP activation (MODE 4).

## Measurement

`supervisor_loop.py` writes timing metadata to `.supervisor/state/current-run.json`:
- `discover_timestamp`, `review_timestamp`, `next_timestamp`, `memory_sync_timestamp`
- `run_start`, `run_end`
- `final_exit_code`, `critical_contradictions`, `autonomous_continue`

This enables KPI measurement per sprint without external tooling.

## Non-Requirements (Explicitly Out of Scope)

- ChatGPT web automation — FORBIDDEN
- OpenAI API calls — no paid access, not required
- Replacing human authority at true gates — Format Factory gates are human-only
- Daemon processes in MODE 0-3 — only allowed in MODE 3 temp directory rehearsal
- Pushing code automatically — always requires explicit human approval
