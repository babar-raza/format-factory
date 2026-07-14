---
version: "1.0"
last-updated: "2026-07-11"
phase-available: "all"
gate-required: null
created-by: TC-SGOV-W4-001
spec_qname_required: "false"
product_track: "governance"
---

# /validate-missing-skill-workflow

Execute the missing-skill discovery and resolution workflow defined in
`docs/governance/skill-only-policy.yaml` §4 (Skill Discovery Requirements) and
the `missing_skill_workflow` block in `.supervisor/skill-registry.yaml`.

When a governed operation has no registered skill, this command produces the
canonical REUSE | COMPOSE | REPAIR | CREATE decision with documented rejection
reasons for all evaluated candidates.

## Handoff Fields (required)

| Field | Description |
|---|---|
| `capability_description` | Human-readable description of the capability needed |
| `operation_type` | The governed operation type (from skill-only-policy.yaml §1) |
| `search_results` | List of candidate skill IDs examined from skill-registry.yaml |
| `rejection_reasons` | Dict mapping each candidate skill_id → rejection reason |

## Handoff Fields (optional)

| Field | Description |
|---|---|
| `route_id` | The capability-routing-registry route_id this maps to (if known) |
| `gap_id` | Existing gap-ledger entry ID if this gap was previously identified |
| `preferred_resolution` | REUSE / COMPOSE / REPAIR / EXTEND / CREATE |

## Pre-conditions

1. `.supervisor/skill-registry.yaml` is readable
2. `.supervisor/capability-routing-registry.yaml` is readable
3. `capability_description` is supplied
4. `search_results` lists at least 1 candidate (or explicitly states "no candidates found")

## Execution

1. **Load the skill registry** — read `.supervisor/skill-registry.yaml`, collect all
   active skill IDs and their `purpose` fields
2. **Classify the operation** — map `capability_description` + `operation_type` to the
   discovery algorithm (skill-only-policy.yaml §3 steps 1-6):
   - Step 1: classify task operation type using route_id taxonomy
   - Step 2: query capability-routing-registry by route_id
   - Step 3: if ROUTE_ACTIVE → select preferred_skill_ids (primary)
   - Step 4: verify skill in skill-registry with status=active
   - Step 5: if MISSING_SKILL_CAPABILITY → execute this workflow
   - Step 6: if no route → classify as MISSING_SKILL_CAPABILITY
3. **Evaluate each candidate** in skill_resolution_order:
   - REUSE_EXACT_MATCH: existing skill fully covers the capability
   - REUSE_PARAMETERIZED_MATCH: existing skill covers with different params
   - COMPOSE_EXISTING_SKILLS: combine atomic skills for multi-capability task
   - REPAIR_EXISTING_SKILL: fix broken/stale skill before replacement
   - EXTEND_EXISTING_SKILL: add bounded capability to existing skill
   - CREATE_MISSING_MICRO_SKILL: only when no existing skill owns responsibility
4. **Document rejection reasons** — for every evaluated candidate not selected,
   write a rejection_reason entry (why REUSE_EXACT_MATCH didn't apply, etc.)
5. **Produce decision** — one of:
   - `REUSE: <skill_id>` — with invocation handoff populated
   - `COMPOSE: [<skill_id_1>, <skill_id_2>]` — with composition order
   - `REPAIR: <skill_id>` — with repair description
   - `EXTEND: <skill_id>` — with extension scope
   - `CREATE: <proposed_skill_id>` — with micro_skill_spec (see §5 new_skill_creation_rule)
6. **Write gap record** (if CREATE decision):
   - Path: `.local/taskcards/SKILL-GAP-<timestamp>.yaml`
   - Fields: capability_description, operation_type, evaluated_candidates,
     rejection_reasons, proposed_skill_id, micro_skill_spec, created_at

## Output Schema

```yaml
decision: REUSE | COMPOSE | REPAIR | EXTEND | CREATE
skill_id: <skill_id>           # for REUSE/REPAIR/EXTEND
skill_ids: [...]               # for COMPOSE
proposed_skill_id: <id>        # for CREATE
rejection_reasons:
  <candidate_skill_id>: <reason string>
rationale: <one-sentence reason for the chosen resolution>
gap_record_path: <path>        # if CREATE, where the gap record was written
```

## Mandatory Validations

- `capability_described`: `capability_description` must be non-empty
- `candidates_evaluated`: at least 1 candidate evaluated OR "no candidates found" stated
- `rejection_reasons_documented`: every non-selected candidate has a rejection_reason
- `decision_is_valid`: decision must be one of REUSE / COMPOSE / REPAIR / EXTEND / CREATE
- `create_only_when_justified`: CREATE decision requires documented rejection of all reuse paths

## Allowed Paths

- `.supervisor/skill-registry.yaml` — read-only (discovery)
- `.supervisor/capability-routing-registry.yaml` — read-only (route lookup)
- `.local/taskcards/` — write (gap record creation for CREATE decisions)

## Forbidden Paths

- `src/net/**` — no product source mutation
- `src/python/**` — no product source mutation
- `.supervisor/skill-registry.yaml` — write forbidden (use preflight-skill-entry for registration)
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if `capability_description` is empty
- Stop if skill-registry.yaml is unreadable
- Stop if the decision is CREATE but no proposed_skill_id is specified
- Do NOT stop if no candidates match — that is the expected CREATE path

## Reference

- Canonical policy: `docs/governance/skill-only-policy.yaml` §3-§5
- Resolution order: `skill_only-policy.yaml` §4 `skill_resolution_order`
- New skill creation rules: `skill-only-policy.yaml` §5 `new_skill_creation_rule`
- Skill registry: `.supervisor/skill-registry.yaml`
- Gap ledger: reports in `.local/taskcards/SKILL-GAP-*.yaml`
