---
version: "1.0"
created: "2026-06-24"
mission: SKILL-FIRST-001
authority:
  - AGENTS.md §E (Reuse-Before-Regenerate)
  - AGENTS.md §B2 (Phase Verification)
  - .supervisor/skill-registry.yaml global_controls
  - .supervisor/autonomy-boundary-contract.yaml
  - CLAUDE.md "Supreme Directive" and "Governance" sections
---

# Skill-First Execution Policy

**Canonical sources:** This document extracts and consolidates rules from
`AGENTS.md`, `CLAUDE.md`, `.supervisor/skill-registry.yaml`, and
`.supervisor/autonomy-boundary-contract.yaml`. Those files are the authority.
This document is a derived operational summary. On conflict, the source wins.

---

## Rule 1: DISCOVER BEFORE CREATING

> Source: `AGENTS.md §E1-E5`

Before any mutating task, query the skill and command registries:

1. Load `.supervisor/skill-registry.yaml` and `.supervisor/capability-routing-registry.yaml`
2. Classify the required operation type using the `route_id` taxonomy
3. Look up the matching route
4. If `current_status: ROUTE_ACTIVE` → use only the listed `preferred_skill_ids`
5. If `current_status: MISSING_SKILL_CAPABILITY` → follow Rule 6 (Missing Skill Workflow)

Log `SKILL_REUSED: <skill_id>` when reusing. Log `ARTIFACT_REUSED: <artifact_id>` for artifacts (per `AGENTS.md §E2`).

---

## Rule 2: REUSE BEFORE EXTENDING, EXTEND BEFORE DUPLICATING

> Source: `.supervisor/skill-registry.yaml global_controls.source_edits_require_explicit_handoff: true`

Resolution order:
1. **REUSE** — existing skill contract fully covers the task
2. **COMPOSE** — combine existing atomic skills for multi-capability tasks
3. **EXTEND** — add a bounded capability to an existing skill when it belongs to the same responsibility
4. **REPAIR** — fix a broken/stale skill before creating a replacement
5. **CREATE** — only when no existing skill owns the responsibility AND the capability is expected to recur

Never create a new skill because an existing one needs repair.
Never create a sprint-specific skill variant.
Never duplicate existing skill logic in an orchestration prompt.

---

## Rule 3: MANDATORY ROUTING ALGORITHM

> Source: `.supervisor/work-type-skill-map.yaml` (machine-readable authority), `.supervisor/capability-routing-registry.yaml` (schema-rich version)

```
CLASSIFY TASK OPERATION TYPE
  → QUERY capability-routing-registry.yaml by route_id
  → IF route found AND current_status: ROUTE_ACTIVE
      → SELECT preferred_skill_ids[0] (primary skill)
      → VERIFY skill is in skill-registry.yaml with status: active
      → BUILD handoff document with required_handoff_fields
      → EXECUTE skill
      → RUN validate-skill-transcript against handoff
  → IF route returns MISSING_SKILL_CAPABILITY
      → FOLLOW Rule 6 (Missing Skill Workflow)
  → IF operation type has no route
      → CLASSIFY as MISSING_SKILL_CAPABILITY
      → FOLLOW Rule 6
```

An agent that skips this routing step and edits files directly violates
`global_controls.source_edits_require_explicit_handoff: true`
from `.supervisor/skill-registry.yaml`.

---

## Rule 4: MUTATION GUARD

> Source: `autonomous_cycle.py Step 2d`, `governance_validators.py` (48 validators)

The declaration-based enforcement layer operates as follows:

- Every `src/` file mutation must be declared in an evidence declaration YAML
- `autonomous_cycle.py` Step 2d runs all 48 governance validators against declarations
- Validators that fire produce `rework_items` entries; persistent `rework_items` → exit code 3
- Key validators for skill compliance:
  - V35: LOC enforcement (file must stay within `baseline_loc_cap`)
  - V42: Analytics deepening suspension (no `_mod_N_times_N` functions)
  - V48: Architecture-only stub gate (RELEASE_GATE items may not cite stubs)
  - V50: Forbidden module names (no `*_analytics_extra.py` etc.)

**Known limitation (SKILL-GAP-012):** This enforcement fires only when an agent
submits an evidence declaration. Agents that edit files without declaring bypass
this layer entirely. `scan-residual-bypasses` monitors for this pattern post-hoc.

---

## Rule 5: IDEMPOTENCY REQUIREMENT

Applies to Python-backed tools in `tools/supervisor/` that produce deterministic file outputs.
Does NOT apply to prompt-backed skills (`.md` command files) — those are evaluated structurally.

A Python-backed skill must prove:
- Run 1 on valid input → expected output
- Run 2 on same input → identical output (no material change)
- Run after partial failure → safe resume or rollback
- Run after valid manual improvement → preserve or merge (never downgrade)

Use `run-skill-idempotency` to generate a machine-readable `skill_idempotency_proof.yaml`.

---

## Rule 6: MISSING SKILL WORKFLOW

> Source: `.supervisor/skill-registry.yaml missing_skill_workflow`

When `check-skill-coverage` returns `BLOCKED_SKILL_GAP`:

1. Verify no existing skill can be extended (reuse/extend check)
2. Create a skill development taskcard at `.local/taskcards/SKILL-GAP-<timestamp>.yaml`
3. Define inputs, outputs, ownership, idempotency rules, and LOC budget (<100 lines)
4. Implement the smallest correct atomic skill
5. Write tests (`tests/supervisor/test_<skill_name>.py`)
6. Register in `.supervisor/skill-registry.yaml`
7. Add to `.claude/commands/command-registry.yaml` via `sync-skill-command-registry`
8. Add route to `.supervisor/work-type-skill-map.yaml`
9. Prove focused behavior (run + verify output)
10. Prove idempotency (run twice, diff)
11. Use the skill to complete the original task
12. Write execution receipt

Skill creation without original-task completion is incomplete.

---

## Rule 7: EXCEPTION PROTOCOL

> Source: `CLAUDE.md "Governance"` and `.supervisor/autonomy-boundary-contract.yaml`

Direct execution without a registered skill is allowed only for:
- Read-only investigation (no mutation)
- Disposable fixture experiments (no production state mutation)
- Governed emergency recovery (must be documented)

Every exception must be recorded:
```yaml
skill_policy_exception:
  exception_id:
  mission_id:
  task_id:
  reason:
  scope:
  paths: []
  risk:
  authorization:
  expiry:
  final_disposition:
```

Exceptions must be bounded. They do not create precedent.

---

## Rule 8: COMMAND/SKILL SYNC

> Source: `.supervisor/skill-registry.yaml`, `.claude/commands/command-registry.yaml`

After any sprint that adds, modifies, or deprecates skills:
1. Run `sync-skill-command-registry` to detect drift between the three registries
2. Auto-repair: missing command-registry entries are added; status fields are synced
3. Flag (do not auto-repair): orphan `.md` files, broken `command_file` pointers, orphan command-registry entries
4. Run a second pass; second pass must report zero items repaired (idempotency proof)

Drift between skill-registry.yaml and command-registry.yaml is a governance defect.
Run sync as part of every registration batch.

---

## Rule 9: AGENT COMPLIANCE VERIFICATION

> Source: `.supervisor/skill-registry.yaml global_controls.skill_invocation_transcript_required: true`

Every skill invocation must produce a handoff transcript containing:
- `skill_id` (registered, active skill)
- `format_id` (if applicable)
- `exact_source_paths` (paths within explicit handoff scope)
- `exact_test_paths`
- `ledger_entry_path` (for `src/` mutations)

After execution, run `validate-skill-transcript` against the handoff to confirm compliance.
Transcripts are stored in `.local/transcripts/`.
`collect-skill-execution-receipts` aggregates them into a unified index.

---

## Routing Quick-Reference

For the full 30-route table, see `.supervisor/capability-routing-registry.yaml`.

| Operation Type | Primary Skill |
|---------------|--------------|
| status_and_recon | reproduce-master-plan |
| plan_creation | create-taskcard |
| source_generation | spec-parity-source-regeneration-and-migration |
| product_backfill | add-python-api / add-dotnet-api |
| analytics_migration | extract-analytics-from-monolith |
| sprint_audit | post-sprint-audit |
| evidence_capture | build-evidence-bundle |
| skill_inventory | inventory-skills |
| sync_skill_command | sync-skill-command-registry |
| rollback_and_recovery | MISSING_SKILL_CAPABILITY (SKILL-GAP-011) |
