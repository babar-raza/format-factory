# Dual-Orchestration Architecture

## Overview

Format Factory uses a 5-layer architecture where Task Master AI (Layer 3) and Ruflo (Layer 4)
are orchestration tools subordinate to Format Factory repo authority (Layer 1).

The "dual orchestration" refers to TM + Ruflo working together as coordination layers,
not as authority layers.

## 5-Layer Architecture

```
Layer 1: Format Factory Repo (AUTHORITY — final)
  ├── registry/format-registry.yaml        ← gate status (L1, highest)
  ├── plans/master-plan.md                 ← operational authority (L2)
  ├── taskcards/                           ← task authority (L3)
  ├── evidence bundles (.local/)           ← sprint output (L4)
  ├── AGENTS.md / GOVERNANCE.md            ← non-negotiable rules
  └── validators / tests / gates           ← acceptance criteria

Layer 2: Local Supervisor Control Plane (replaces ChatGPT handoff)
  ├── .supervisor/                         ← config, memory, prompts, schemas, state
  ├── tools/supervisor/                    ← 6 deterministic scripts
  ├── reports/supervisor/                  ← supervisor runtime outputs
  └── discover → validate → generate → export → sync memory

Layer 3: Task Master AI (TASK GRAPH / STATE ENGINE — non-authority)
  ├── .taskmaster/tasks/tasks.json         ← task graph (non-authoritative)
  ├── Consumes supervisor-generated task exports
  └── Bridge fields must reference FF taskcards/gates/docs

Layer 4: Ruflo (ORCHESTRATION LAYER — non-authority)
  ├── CLI: claude-flow (NOT `ruflo`)
  ├── MCP management: claude-flow mcp start/stop/status/tools/toggle
  ├── v3.10.13 — orphan-process watchdog since v3.10.11
  └── Cannot approve gates, push, override validators

Layer 5: Claude Code (EXECUTOR, VS Code)
  ├── Runs supervisor scripts and prompts
  ├── Uses Task Master for task selection
  ├── Uses Ruflo for lane coordination
  └── Runs FF validators/evidence for acceptance
```

## Authority Model

Only one thing has authority over gate status: Format Factory repo evidence.

- `registry/format-registry.yaml`: gate status (read-only for all tools)
- `plans/master-plan.md`: operational decisions (human-maintained)
- Evidence bundles: sprint output validated by `validate_evidence_bundle.py`

The supervisor, TM, and Ruflo are advisory tools. They assist Claude Code.
They do not replace human judgment at true approval gates.

## Data Flow (Full Sprint Cycle)

```
Evidence bundle (Layer 1)
       │
       ▼
supervisor_loop.py discover (Layer 2)
       │
       ▼
validate_evidence_for_supervisor.py
       │
       ▼
compare_goal_to_evidence.py
       │
       ▼
generate_supervisor_packet.py
  │                    │
  ▼                    ▼
next-sprint-taskmaster.json    next-ruflo-lanes.json
  │                                    │
  ▼                                    ▼
Task Master AI (Layer 3)       Ruflo (Layer 4)
  │                                    │
  └──────────────┬─────────────────────┘
                 │
                 ▼
           Claude Code (Layer 5)
                 │
                 ▼
         New evidence bundle (Layer 1)
```

## No-Drift Contract Summary

The no-drift contract is enforced by `validate_dual_orchestration_bridge.py`:

1. TM task "done" ≠ FF gate closed
2. Ruflo lane "complete" ≠ evidence accepted
3. Supervisor verdict ≠ gate approval
4. TM done + evidence fails → TM state reverts
5. Ruflo state contradicting FF registry → marked stale
6. Supervisor next-sprint.md is INPUT to next sprint — not authority

## Phase Model Summary

| Mode | Layer 2 | Layer 3 | Layer 4 | Human Gate? |
|------|---------|---------|---------|-------------|
| MODE 0 | Plan healing only | None | None | No |
| MODE 1 | Foundation impl | None | None | No |
| MODE 2 | Replay/hardening | Schema only | Schema only | No |
| MODE 3 | Dry run | Dry run | Dry run | No |
| MODE 4 | Active | Active MCP | Active MCP | **YES** |
| MODE 5 | Autonomous | Active | Active | **YES** |

## Key Files Quick Reference

| Purpose | File |
|---------|------|
| Supervisor config | `.supervisor/config.yaml` |
| No-drift policies | `.supervisor/policies.yaml` |
| Sprint memory | `.supervisor/project-memory.md` |
| Supervisor loop procedure | `.supervisor/sprint-loop.md` |
| Bridge validator | `tools/taskmaster/validate_taskmaster_bridge.py` |
| No-drift validator | `tools/taskmaster/validate_dual_orchestration_bridge.py` |
| Supervisor orchestrator | `tools/supervisor/supervisor_loop.py` |
| Supervisor architecture doc | `docs/automation/local-supervisor-control-plane.md` |
| TM operating profile | `docs/taskmaster/taskmaster-format-factory-operating-profile.md` |
| Ruflo operating profile | `docs/ai/ruflo-format-factory-operating-profile.md` |
| KPI model | `docs/taskmaster/dual-orchestration-kpi-model.md` |
| No-drift state contract | `docs/taskmaster/taskmaster-no-drift-state-contract.md` |
