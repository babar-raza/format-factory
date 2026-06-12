# Autonomy Default Routing Policy

## Core Principle

Autonomy is acceleration, not authority. Evidence, tests, route decisions, taskcards, and supervisor verdicts are authority.

## Routes

| Route | Description |
|-------|-------------|
| AUTONOMOUS_ACCELERATED_DEFAULT | Safe product work qualified by category, tests, evidence, allowed paths |
| AGENT_GOVERNED_ROUTE_DECISION_REQUIRED | Machinery or unqualified work awaiting governed decision |
| GOVERNED_DIRECT_EXECUTION | Machinery with valid governed route decision on allowed paths |
| HUMAN_APPROVAL_REQUIRED | High-risk or gate-requiring work needing human authorization |
| BLOCKED_UNSAFE_OR_UNCLASSIFIED | Unknown, ambiguous, or unsafe work — fail closed |

## Task Categories

### Product Categories (may default to autonomous when qualified)
- PRODUCT_IMPLEMENTATION
- PRODUCT_TESTING
- PRODUCT_CAPABILITY_EXPANSION
- PRODUCT_EXPORT_OR_DOGFOOD

### Machinery Categories (require governed route decision)
- SPEC_AUTHORITY_MACHINERY
- REQUIREMENT_CAPABILITY_MACHINERY
- ACTION_QUEUE_MACHINERY
- AUTONOMY_ORCHESTRATOR_MACHINERY
- SUPERVISOR_VERDICT_MACHINERY
- VALIDATOR_OR_EVIDENCE_MACHINERY
- PROMPT_GENERATION_MACHINERY
- GOVERNED_SKILL_OR_GENERATOR_MACHINERY

### Blocked Category
- UNKNOWN_OR_AMBIGUOUS — always fails closed

## Fail-Closed Rules

1. Unknown or missing task category on current-run items blocks.
2. Legacy/backfill items without category may warn only when non-source-mutating.
3. Machinery without valid route_decision_id blocks.
4. Route decision must match task_id/category and not be blocked.
5. Product work routes to autonomous only with non-empty tests, evidence, and allowed_paths.
6. Generated prompts with unauthorized commit/push/publish instructions are quarantined.
7. Every route decision is written to the route ledger.

## Qualification for Autonomous Default

Product work qualifies for AUTONOMOUS_ACCELERATED_DEFAULT when:
- task_category is a product category
- required_tests is non-empty
- required_evidence is non-empty
- allowed_paths is non-empty
- no forbidden machinery mutation
- risk_level is LOW or MEDIUM
- no human_approval_required flag

## Enforcement Boundary

Route enforcement operates at two distinct layers:

**Layer 1 — Governance validator (autonomous_cycle.py Step 2e):**
- Validator 11 (`route_decision_required_validator`) checks that every current-run PRODUCT_SOURCE
  item in the declaration has a `route_decision_id`.
- Current-run items without one: `result=FAIL`, `blocks_sprint=True`.
- Legacy/backfill items (grace exemption): `result=WARN`, `blocks_sprint=False`.
- This layer validates PRESENCE only — it does not read the decision file contents.

**Layer 2 — Dispatch-time gate (next_action_runner.py → check_action_route_allowed()):**
- Called at action dispatch time, before any backend executes the action.
- Validates decision CONTENT: `allowed_paths`, `forbidden_paths`, `required_tests`, task_id/category match.
- Machinery items: requires a valid governed route decision on disk.
- Product source-mutating items: requires route_decision_id + valid decision file.
- Returns `(allowed=False, reason)` to block dispatch when enforcement fails.

**Gap — Manual/skill execution bypass:**
- Manual execution and skill-governed execution (MANUAL_GOVERNED_BY_SKILL) bypass Layer 2.
- These paths are governed by the skill transcript and evidence declaration instead.
- The governance validator (Layer 1) still applies to these items via Validator 11.

**Implementation references:**
- `tools/supervisor/governance_validators.py` → `validate_route_decision_required` (V11)
- `tools/supervisor/autonomy_route_decider.py` → `check_action_route_allowed()`
- `tools/supervisor/next_action_runner.py` → route enforcement block (Step 2)

## Product Mutation Evidence Auto-Generation

*Design specification — implementation deferred to a future sprint.*

### When to generate

After `check_action_route_allowed()` returns `True` in `next_action_runner.run_action()`,
immediately before the backend executes, generate a product mutation route evidence record.

### Where to write

`<evidence_root>/product-mutation-route-evidence.json`

### Field mapping

| Evidence field | Source |
|---------------|--------|
| `mutation_id` | `action["action_id"]` |
| `task_id` | `action["task_id"]` |
| `route_decision_id` | `action["route_decision_id"]` |
| `authorized_route` | `route_decision["final_route"]` |
| `allowed_paths_used` | Paths actually modified during execution (post-hoc) |
| `forbidden_paths_checked` | `route_decision["forbidden_paths"]` |
| `tests_proving_mutation` | `route_decision["required_tests"]` |

### Reference schema

`schemas/evidence/product-mutation-route-evidence.schema.json`

### Implementation note

One manually-created instance exists at
`.local/evidences/route-aware-product-reentry-20260610-001030-e382e5f/product-mutation-route-evidence.json`
as a reference. Auto-generation is deferred — the design here is authoritative.
