# Task Master AI — Supervisor Integration

## Overview

Task Master AI (Layer 3) is the task graph and state memory engine.
It does NOT have authority over Format Factory gates or evidence.
The Local Supervisor Control Plane (Layer 2) generates TM inputs from evidence.

## Integration Points

```
Supervisor (Layer 2)                    Task Master AI (Layer 3)
─────────────────────────────────────   ──────────────────────────────
generate_supervisor_packet.py
  │
  ├── writes next-sprint-taskmaster.json
  │       │
  │       └── TM import (MODE 3+)  ──►  .taskmaster/tasks/tasks.json
  │
  └── writes next-ruflo-lanes.json
          │
          └── Ruflo import (MODE 3+) ─► lane coordination
```

## Data Flow

1. `supervisor_loop.py run-on-latest` runs after evidence bundle created
2. `generate_supervisor_packet.py` reads `evidence-review.json` + `contradictions.json`
3. Generates `next-sprint-taskmaster.json` (schema-validated against next-sprint-taskmaster.schema.json)
4. In MODE 3+: TM imports the generated JSON
5. In MODE 4+: TM MCP server provides task selection to Claude Code

## next-sprint-taskmaster.json Format

```json
{
  "sprint_id": "format-factory-RNNNN-...",
  "timestamp": "2026-05-30T00:00:00",
  "verdict": "SUPERVISOR_...",
  "tasks": [
    {
      "task_id": "TASK-001",
      "title": "Human-readable task title",
      "status": "pending",
      "ff_taskcard_ref": "TC-0001",       // or ff_gate_ref or ff_doc_ref
      "acceptance_evidence": "pytest tests/python/fods/ -v",
      "validation_command": "pytest tests/python/fods/ -v",
      "non_authoritative": true
    }
  ]
}
```

At least one of `ff_taskcard_ref`, `ff_gate_ref`, or `ff_doc_ref` is required per task.
`non_authoritative: true` is required — TM task state never overrides FF authority.

## Bridge Validation

`tools/taskmaster/validate_taskmaster_bridge.py` validates every TM export:

- Each task must reference a FF taskcard, gate, or doc
- `acceptance_evidence` required (non-empty string)
- `validation_command` required (non-empty string)
- Blocked tasks must include `blocker_type`
- Done tasks must have `non_authoritative: true`

Run: `python tools/taskmaster/validate_taskmaster_bridge.py reports/supervisor/next-sprint-taskmaster.json`

## TM CLI Note

`task-master-ai --version` and `task-master-ai --help` both start an MCP server.
They do NOT print version or help text. Use `npm show task-master-ai version` for version.

Default tool mode: core (7 tools). Full surface available via MCP.

## Mode Activation

- MODE 0-2: No TM activation. Schema validation only.
- MODE 3: Dry run — `npm show task-master-ai version` + schema import test. No daemon.
- MODE 4+: Active TM with MCP registration (requires human approval).

## State Recovery

If TM state contradicts FF evidence:
1. `validate_dual_orchestration_bridge.py` detects the drift
2. Supervisor generates repair-focused next-sprint.md
3. TM state for affected tasks reverts to `evidence_blocked`
4. Human notified if drift is CRITICAL

TM state is non-authoritative — it can always be rebuilt from FF evidence.
