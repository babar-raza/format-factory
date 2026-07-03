# Espanso Capability Integration Plan

## Context

The Format Factory project has accumulated 92 match blocks (~330 triggers, 98K lines) in an external Espanso file (`C:\Users\prora\AppData\Roaming\espanso\match\format-factory.yml`) containing reusable operational prompts. These prompts encode governance rules, execution protocols, audit workflows, and product deepening strategies developed over time.

The repository already has a mature governance system: **103 capabilities** (verified 2026-07-03), 98+ skills, 94 commands, 30 routes, 24 schemas, 85 validators. Most Espanso blocks are verbose instantiations of patterns the repo already governs. The goal is to extract genuine gaps, resolve conflicts, create traceable provenance, and wire new capabilities into existing registries -- NOT to create 92 prompt files or parallel governance systems.

**Reassessment date:** 2026-07-03. All plan items verified against current system state — zero items completed, zero items superseded. Capability registry grew from 94 to 103 entries between planning sessions (9 capabilities added by an intervening sprint), but none of the 5 proposed new capability IDs conflict with those additions. All target files confirmed absent.

**Problem:** Valuable operational knowledge is trapped in an external Espanso file, invisible to repository agents. Some capabilities have no repo equivalent. Duplicates and conflicts exist between Espanso prompts and repo governance.

**Outcome:** A provenance-mapped, gap-analyzed integration where genuine new capabilities are wired into existing registries, conflicts are resolved, and agents can discover everything through the standard skill/capability/routing systems.

---

## Phase 1: Provenance Inventory (TC-ESP-001)

**Create** `.supervisor/prompts/espanso-provenance-map.yaml`

Parse the complete Espanso file and create a machine-readable entry for every block:

```yaml
provenance_entries:
  - block_id: 1
    primary_trigger: ":ffreadme"
    all_triggers: [":ff-investigate-and-enhance-root-readme", ...]
    line_range: [3, 1507]
    family: readme_governance
    disposition: GAP_NEW_ASSET | COVERED_BY_EXISTING | PARTIAL_COVERAGE | DUPLICATE_OF | POLICY_ONLY | EMPTY_BLOCK
    mapped_capability: null | existing-capability-id
    gap_id: GAP-ESP-001 | null
    notes: ""
```

Dispositions (from gap analysis -- 79 populated blocks):
- **COVERED_BY_EXISTING** (~50 blocks): Dual-lane deepening, skill governance, plan hardening, spec authority, analytics, oracle, evidence/proof, autonomous loop
- **GAP_NEW_ASSET** (8 blocks): See Phase 2
- **POLICY_ONLY** (~5 blocks): Found-it-own-it, production standards, micro-triggers
- **DUPLICATE_OF** (~8 blocks): Multiple product-deepening trains, duplicate expert-review, duplicate layer-plans
- **EMPTY_BLOCK** (18 blocks): No triggers defined

**Files:** `.supervisor/prompts/espanso-provenance-map.yaml` (new)

---

## Phase 2: Extract 8 New Prompt Assets (TC-ESP-002)

Create distilled prompt assets (80-200 lines each, NOT verbatim copies) for genuine gaps:

| ID | File | Source Block | Purpose |
|---|---|---|---|
| ESP-PROMPT-1 | `.supervisor/prompts/bounded-executor.md` | `:ff-execute-short-context-plan` (line 45456) | One-taskcard-at-a-time executor for context-limited agents |
| ESP-PROMPT-2 | `.supervisor/prompts/readme-governance.md` | `:ffreadme` (line 27946) | Root README forensic maintenance with preservation-first rules |
| ESP-PROMPT-3 | `.supervisor/prompts/expert-review-plan.md` | `:ff-expert-review-plan` (line 122470) | Read-only expert manual system review protocol |
| ESP-PROMPT-4 | `.supervisor/prompts/found-it-own-it.md` | `:found-it-own-it` (line 64179) | Issue ownership enforcement protocol |
| ESP-PROMPT-5 | `.supervisor/prompts/machinery-iteration-forensics.md` | `:ff-machinery-iteration-forensics` (line 75372) | Lifecycle iteration failure diagnosis |
| ESP-PROMPT-6 | `.supervisor/prompts/human-free-rectification.md` | `:ff-humanfree` (line 125601) | Scan/fix governance text incorrectly requiring human intervention |
| ESP-PROMPT-7 | `.supervisor/prompts/layer-hardening-template.md` | `:ffl0:`-`:ffl7:` family | Parameterized per-layer hardening (ONE template, not 10 files) |
| ESP-PROMPT-8 | `.supervisor/prompts/production-standards-enforcement.md` | `:ffmgh:` (line 92465) | Code quality checklist enforcement sprint |

Each prompt asset includes:
- Structured protocol (not verbose prose)
- `espanso_provenance:` metadata header
- `short_context_view:` section (first 30 lines, self-contained for weaker agents)

**Files:** 8 new `.md` files in `.supervisor/prompts/`

---

## Phase 3: Extend Prompt Registry (TC-ESP-003)

Extend `.supervisor/prompts/prompt-registry.yaml` with an `operational_prompts:` section (same schema as existing `prompts:` entries). Do NOT create a separate registry file.

Add entries for ESP-PROMPT-1 through ESP-PROMPT-8 with:
- `id`, `name`, `file`, `description`, `stage`, `mode`
- `inputs[]`, `outputs[]`, `output_schema`
- `successor_rules[]`, `validation_rules[]`

**Files modified:** `.supervisor/prompts/prompt-registry.yaml`

---

## Phase 4: Wire New Capabilities (TC-ESP-004)

Add 5 new capabilities to `.governance/capabilities/registry.yaml`:

| capability_id | product_track | parity_status |
|---|---|---|
| `bounded-execution` | infrastructure | PARTIAL |
| `readme-root-governance` | layer_governance | PARTIAL |
| `expert-review-plan` | governance | PARTIAL |
| `machinery-iteration-forensics` | governance | PARTIAL |
| `human-free-rectification` | governance | PARTIAL |

Remaining 3 prompts (found-it-own-it, layer-hardening-template, production-standards-enforcement) are policy protocols referenced by existing capabilities, not standalone capabilities.

**Files modified:** `.governance/capabilities/registry.yaml`

---

## Phase 5: Wire New Routes (TC-ESP-005)

Add 3 new routes to `.supervisor/capability-routing-registry.yaml`:

| route_id | preferred_skill_ids | status |
|---|---|---|
| `bounded_execution` | `[autonomous-loop]` | ROUTE_ACTIVE |
| `root_readme_governance` | `[sync-readmes]` | ROUTE_ACTIVE |
| `governance_rectification` | `[human-free-rectification]` | MISSING_SKILL_CAPABILITY |

**Files modified:** `.supervisor/capability-routing-registry.yaml`

---

## Phase 6: Conflict Resolution Document (TC-ESP-006)

Create `.supervisor/prompts/espanso-conflict-resolution.md` documenting:

1. **Duplicate blocks** -- which Espanso blocks are near-identical (e.g., Blocks 24/25 product-deepening trains, Blocks 12/13/14 layer plans, Blocks 76/77 expert review)
2. **Trigger collisions** -- where Espanso triggers shadow existing commands (e.g., `:fflayers` used by 4 blocks, `:ffs:` used by 2 unrelated blocks)
3. **Policy conflicts** -- where Espanso instructions conflict with current AGENTS.md/CLAUDE.md (resolution: repo truth wins)
4. **Supersession map** -- which Espanso blocks are superseded by existing repo capabilities

**Files:** `.supervisor/prompts/espanso-conflict-resolution.md` (new)

---

## Phase 7: Discovery Index (TC-ESP-007)

Create `.supervisor/prompts/agent-prompt-index.yaml` -- a compact machine-readable index:

```yaml
agent_prompt_index:
  - prompt_id: ESP-PROMPT-1
    intents: [short_context, bounded_execution, weaker_agent]
    purpose: "Execute one taskcard at a time for context-limited agents"
    when_to_use: "Agent has limited context window or is resuming after compaction"
    mutating: true
    context_profile: short
    command: null
    skill: autonomous-loop
```

Also update the generated capability index in CLAUDE.md via `/sync-capabilities` after Phase 4.

**Files:** `.supervisor/prompts/agent-prompt-index.yaml` (new), CLAUDE.md capability table (updated by tool)

---

## Verification

1. **Provenance completeness**: Every Espanso block (79 populated + 18 empty) has an entry in the provenance map
2. **No duplicate IDs**: All ESP-PROMPT-* IDs are unique across prompt-registry.yaml
3. **Registry consistency**: Run `/sync-capabilities` -- new capabilities appear in CLAUDE.md table
4. **Route resolution**: All new routes in routing registry have valid `preferred_skill_ids` references
5. **Idempotency**: Re-running the integration produces zero material changes (same provenance map, same prompt count)
6. **No parallel registries**: Only existing registry files are extended, no new registries created

---

## Taskcard Status

| TC-ID | Status | Title |
|---|---|---|
| TC-ESP-001 | CLOSED | Create espanso-provenance-map.yaml |
| TC-ESP-002 | CLOSED | Extract 8 new prompt assets |
| TC-ESP-003 | CLOSED | Extend prompt-registry.yaml |
| TC-ESP-004 | CLOSED | Wire 5 new capabilities to registry |
| TC-ESP-005 | CLOSED | Wire 3 new routes to routing registry |
| TC-ESP-006 | CLOSED | Create conflict resolution document |
| TC-ESP-007 | CLOSED | Create agent-prompt-index.yaml discovery index |

---

## Summary

- **New files:** 12 (1 provenance map + 8 prompts + 1 conflict doc + 1 discovery index + 1 YAML)
- **Modified files:** 3 (prompt-registry.yaml, capabilities/registry.yaml, capability-routing-registry.yaml)
- **New capabilities:** 5
- **New routes:** 3
- **Espanso blocks accounted for:** 92/92
- **Espanso file modified:** NO (read-only source)


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-02T20:48:54.417630+00:00"
  locked_by: "0ce45942c388"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
