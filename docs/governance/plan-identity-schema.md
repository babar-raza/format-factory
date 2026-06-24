# Plan Identity Schema — Format Factory

## Purpose

Every per-chat or repository plan file should include a machine-readable `plan_identity:` block
(or an HTML comment wrapping it for Markdown compatibility). This allows plan identity to be
reconstructed from the plan file itself when lock files expire or sessions change.

## When to Add It

- At plan creation time (in plan mode, or when creating a repository supplement plan)
- When a plan is adopted for execution from a prior session
- When running TC-PG-002 or any plan governance healing taskcard

## Format

Use an HTML comment at the top of the file so the identity block does not interfere with
Markdown rendering:

```markdown
<!--plan_identity:
  schema_version: "1.0"
  plan_id: "<filename-stem>"
  mission_id: "<FF-MISSION-ID>"
  native_plan_path: "<absolute or repo-relative path>"
  native_plan_filename: "<filename.md>"
  created_by_agent: "autonomous-agent | claude-sonnet-4-6 | human"
  created_during_plan_mode: true | false
  created_at: "<ISO 8601 date or approximate>"
  repository: "format-factory"
  branch: "main"
  parent_plan_id: null | "<parent-plan-id>"
  successor_plan_id: null | "<successor-plan-id>"
  ownership_status: "ACTIVE | TRANSFERRED | TERMINALLY_LOCKED | SUPERSEDED | DEFERRED"
  plan_type: "<type string — see below>"
  ledger_entry: "LEDGER-<N> | null"
  current_revision: "<semver or version string>"
  terminal_lock: false | true
  terminal_lock_reason: null | "<reason>"
  terminal_locked_at: null | "<ISO 8601>"
-->
```

## Required Fields

| Field | Required | Description |
|---|---|---|
| `schema_version` | Yes | Always `"1.0"` for this version |
| `plan_id` | Yes | Matches the filename stem (e.g., `"snoopy-juggling-seal"`) |
| `mission_id` | Yes | Stable mission identifier (e.g., `"FF-SAL-FORENSICS-001"`) |
| `native_plan_path` | Yes | Absolute or repo-relative path to THIS file |
| `native_plan_filename` | Yes | Just the filename (e.g., `"snoopy-juggling-seal.md"`) |
| `created_by_agent` | Yes | Who created the plan |
| `created_during_plan_mode` | Yes | `true` if created via Claude Code plan mode |
| `created_at` | Yes | Creation date |
| `repository` | Yes | Always `"format-factory"` |
| `branch` | Yes | Git branch (usually `"main"`) |
| `ownership_status` | Yes | Current ownership state |
| `terminal_lock` | Yes | `false` until the plan is terminally closed |

## Optional Fields

| Field | Description |
|---|---|
| `parent_plan_id` | If this plan supersedes or continues another plan |
| `successor_plan_id` | If a successor plan was created after this one closed |
| `plan_type` | Category of plan (see below) |
| `ledger_entry` | The LEDGER-N entry in `plans/master-plan-memory.md` |
| `current_revision` | Plan version string |
| `run_id` | The evidence run ID if known |

## Plan Types

| Type | Description |
|---|---|
| `machinery_hardening` | Governance, tooling, or infrastructure fix |
| `sal_forensics` | SAL source-to-consumption pipeline analysis |
| `capability_layer_supplement` | Capability layer supplement to the master plan |
| `product_deepening` | Product feature implementation |
| `sprint_loop` | Autonomous sprint loop plan |
| `lifecycle_hardening` | Lifecycle enforcement machinery |
| `general` | Default / unclassified |

## Ownership States

| State | Description |
|---|---|
| `ACTIVE` | Plan is in active development or execution |
| `TRANSFERRED` | Ownership transferred to another agent or session |
| `TERMINALLY_LOCKED` | Plan is closed; no further writes permitted |
| `SUPERSEDED` | Replaced by a successor plan |
| `DEFERRED` | Work was deferred; requires explicit reauthorization |

## Plan Discovery Algorithm

When resolving the native plan path for an active mission, use this priority order:

1. **Execution-state-bound native plan path** — from `.local/supervisor/plan-locks/`
2. **Plan ID recorded in mission state** — from active-plan-lock.json
3. **Native plan path from plan identity front-matter** — parsed from this schema
4. **Exact path supplied by caller** — explicit override
5. **Matching ledger entry** — from `plans/master-plan-memory.md`
6. **Repository plan registry** — from `plans/` directory
7. **Current plan-mode creation event** — from Claude Code session context

If more than one candidate remains after all steps, return `PLAN_IDENTITY_AMBIGUOUS`
and do NOT write to any plan file until exactly one is authoritative.

## Forbidden Resolution Sources

Do NOT derive plan identity from:
- Most recently modified `.md` file
- Most popular or most referenced plan filename
- Global default plan configured in any settings file
- `plans/snoopy-juggling-seal.md` (unless its `plan_id` matches the current mission)
- Another chat's active plan
- Another mission's plan

## Machine Parsing

The `tools/supervisor/plan_identity.py` module implements `extract_plan_identity(plan_path)`
to parse this block. It strips the HTML comment delimiters and parses the YAML body.
Returns `None` if no block is found (backward-compatible).

## Example — Repository Plan

```markdown
<!--plan_identity:
  schema_version: "1.0"
  plan_id: "snoopy-juggling-seal"
  mission_id: "FF-SAL-FORENSICS-001"
  native_plan_path: "plans/snoopy-juggling-seal.md"
  native_plan_filename: "snoopy-juggling-seal.md"
  created_by_agent: "autonomous-agent"
  created_during_plan_mode: true
  created_at: "2026-06-16 (approximate)"
  repository: "format-factory"
  branch: "main"
  ownership_status: "ACTIVE"
  plan_type: "sal_forensics"
  ledger_entry: "LEDGER-001"
  current_revision: "3.16"
  terminal_lock: false
-->
```

## Example — Claude Plans Directory Plan

```markdown
<!--plan_identity:
  schema_version: "1.0"
  plan_id: "keen-snacking-quiche"
  mission_id: "FF-PLAN-GOV-001"
  native_plan_path: "C:/Users/prora/.claude/plans/keen-snacking-quiche.md"
  native_plan_filename: "keen-snacking-quiche.md"
  created_by_agent: "claude-sonnet-4-6"
  created_during_plan_mode: true
  created_at: "2026-06-23"
  repository: "format-factory"
  branch: "main"
  ownership_status: "ACTIVE"
  plan_type: "machinery_hardening"
  ledger_entry: "LEDGER-009"
  current_revision: "1.0"
  terminal_lock: false
-->
```
