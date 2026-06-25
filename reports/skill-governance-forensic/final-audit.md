# Format Factory Skill/Command-Only Governance Forensic Audit Report

**Mission:** SKILL-GOV-FORENSIC-20260625
**Sprint:** skill-governance-forensic-audit-20260625
**Date:** 2026-06-25
**Auditor:** Claude Code (Sonnet 4.6)
**Plan Section:** master-plan.md §62

---

## Current State

### Skills Found

| Category | Count |
|----------|-------|
| Total registered skills | 65 |
| Active skills | 62 |
| Deprecated skills | 3 |
| Prompt-backed (`.md` only, no Python) | 58 |
| Python-backed (have `implementation_paths`) | 7 |
| New micro-skills created this sprint | 2 (pre_mutation_guard, ci_skill_attribution_check) |

### Commands Found

- 65 command files in `.claude/commands/`
- 1 broken pointer: `check-mcp-status.md` (deprecated skill — acceptable)
- All 65 skills have discoverable command files
- Command registry: `.claude/commands/command-registry.yaml` — synced (WARN only)

### Registration Status

| Status | Count |
|--------|-------|
| REGISTERED_AND_PROVEN | 7 (Python-backed meta-governance tools) |
| REGISTERED_NOT_USED (prompt-backed) | 58 (design intent — LLM executes) |
| IMPLEMENTED_NOT_REGISTERED | 174 (tools/supervisor/ AD_HOC scripts) |
| BROKEN | 1 (check-mcp-status, deprecated) |
| DUPLICATED | 0 |

---

## Historical Adoption

### Sprints Reviewed

| Sprint ID | Type | Skill Coverage | Verdict |
|-----------|------|----------------|---------|
| SKILL-FIRST-001 (2026-06-24) | Meta-governance | Meta-skills (inventory, scan, etc.) | PARTIALLY_COMPLIANT |
| SKILL-GOVERNANCE-REPAIR-001 (2026-06-25) | Meta-governance | Meta-skills + 2 new skills | PARTIALLY_COMPLIANT |
| PDEP-2026-06-25-001 | Product deepening | add-python-object-model-feature (retroactive) | DECLARED_BUT_UNPROVEN |
| ff-gates-advancement-20260625 | Product + gates | Various | PARTIALLY_COMPLIANT |

### Claude Code Compliance

- **Post-policy mutations:** 2 commits
- **Fully governed:** 1 (787b43e2 — retroactive transcript created)
- **Partially governed:** 1 (5d668226 — additional transcript needed)
- **Compliance rate:** 50%

### Codex Compliance

- Codex not activated (DEC-014 deferred)
- Compliance rate: 0% (no Codex sprints executed)

### Direct Execution Count

- 2 post-policy src/ commits without pre-mutation skill invocation
- Both used Claude Code Edit/Write tools directly
- No technical barrier prevented this

### Receipts Found

- 8 skill receipts in `reports/skill-first/pilots/` (pilot A-H from SKILL-FIRST-001)
- 2 retroactive transcripts in `reports/skills-pdep-20260625/skill-transcripts/`
- Total: 10 receipts (covering 7 meta-governance invocations + 2 product mutations)

### Skill-Created-Not-Used Cases

- 0 violations (no cases where a skill was created then the original task executed directly)

---

## Enforcement Gaps

### Entry-Point Gaps

| Gap ID | Gap | Severity |
|--------|-----|----------|
| EP-001-GAP | Skill registry query is PROMPT_ONLY — no technical barrier to skip | HIGH |
| EP-002-GAP | Mutation guard must be called explicitly by agent — not automatic | HIGH |
| CODEX_MISSING | No Codex-specific entry point until this sprint | HIGH |

### Routing Gaps

- 30/30 capability routes are ACTIVE — no routing gaps
- work-type-skill-map.yaml is complete

### Taskcard Gaps

| Gap ID | Gap | Severity |
|--------|-----|----------|
| EP-008-GAP | Taskcards lack mandatory `execution_contract` field — not validated at READY | MEDIUM |
| EXISTING_TASKCARDS | All prior taskcards lack `skill_ids` and `allowed_paths` fields | MEDIUM |

### Plan Gaps

- Plans can contain "write a script" steps without skill routes
- No plan validator exists (EP-009-GAP)

### Mutation Guard Gaps

| Gap ID | Gap | Severity |
|--------|-----|----------|
| EP-002-GAP | Guard is a call-explicitly tool, not automatic interception | HIGH |
| SKILL-GAP-008 | No pre-commit hook — prevention requires TC-SGF-001 | HIGH |
| SKILL-GAP-012 | Agents that skip declaration bypass EP-003 entirely | HIGH |

### Supervisor Gaps

- 48 governance validators exist and fire on declaration submission
- SKILL-GAP-012: no validator checks `declared_skill_ids` field (TC-SGF-002)

### CI Gaps

- New CI job `skill-attribution-check` added this sprint (EP-006)
- Currently `continue-on-error: true` — WARN only until SKILL-GAP-008 (pre-commit hook) is closed
- After TC-SGF-001 is closed: remove `continue-on-error: true` to make it blocking

### Close-Task Gaps

- No close-task enforcement for skill receipts
- Supervisor grading does not check `declared_skill_ids` field (TC-SGF-002)

---

## Architecture

### Canonical Policy

**Path:** `docs/governance/skill-only-policy.yaml` (CREATED this sprint)
**Status:** IMPLEMENTED — authoritative machine-readable policy for all agents
**Consumed by:** Claude Code entry points (CLAUDE.md → references policy), Codex adapter, CI check

### Shared Registry

**Path:** `.supervisor/skill-registry.yaml`
**Status:** 65 skills, 62 active, 30/30 routes
**Tool:** `skill_inventory.py` (GOVERNED), `validate_skill_contracts.py` (GOVERNED)

### Router

**Path:** `.supervisor/capability-routing-registry.yaml` + `.supervisor/work-type-skill-map.yaml`
**Status:** COMPLETE — 30/30 routes ACTIVE
**Tool:** `build_capability_routes.py` (GOVERNED)

### Micro-Skill Creation Process

Documented in `.supervisor/skill-first-policy.md Rule 6` and `docs/governance/skill-only-policy.yaml §5`.
Missing-capability workflow: taskcard → design → implement → register → test → idempotency → use → receipt.

### Command Runner

**Path:** `.claude/commands/` (65 command files)
**Status:** All commands exist; 1 broken pointer (deprecated)

### Mutation Guard (NEW)

**Path:** `tools/governance/pre_mutation_guard.py`
**Status:** IMPLEMENTED — call-explicitly, not automatic
**Modes:** check (dry-run) and execute (writes authorization record)
**Blocks:** no_active_task, unregistered_skill, deprecated_skill

### Execution Receipts

**Schema:** `.supervisor/schemas/evidence-declaration.schema.json`
**Status:** Schema exists; receipts are voluntary (SKILL-GAP-012)
**Tools:** `validate-skill-transcript`, `collect-skill-execution-receipts`

### Claude Code Adapter

**Status:** CLAUDE.md + AGENTS.md reference skill policies — PROMPT_ONLY
**Gap:** No automatic tool-layer interception

### Codex Adapter (NEW)

**Path:** `docs/governance/codex-adapter.md`
**Status:** CREATED this sprint — references canonical policy
**Pending:** TC-SGF-003 (add AGENTS.md reference)

### Supervisor Enforcement

**Path:** `tools/supervisor/autonomous_cycle.py` Step 2d + 48 governance validators
**Status:** PARTIAL (declaration-based; SKILL-GAP-012 bypass exists)

### CI Enforcement (NEW)

**Path:** `tools/governance/ci_skill_attribution_check.py`
**CI job:** `.github/workflows/ci.yml` → `skill-attribution-check`
**Status:** DETECTION (post-hoc, continue-on-error=true until pre-commit hook ready)

---

## Skills Summary

| Category | Count |
|----------|-------|
| Reused (existing exact match) | 2 (Python-backed) |
| Composed | 0 |
| Repaired | 0 |
| Decomposed | 0 |
| Created (micro-skills, this sprint) | 2 |
| Rejected duplicates | 0 |

**New micro-skills created:**
1. `tools/governance/pre_mutation_guard.py` — runtime mutation authorization (EP-002)
2. `tools/governance/ci_skill_attribution_check.py` — CI ungoverned mutation detection (EP-006)

---

## Pilots

### BT-001: Claude Code direct mutation rejection (no active task)
- Operation: mutation with task_id=NONE
- Guard: `pre_mutation_guard.py`
- Result: **GUARD_ENFORCED** — BLOCKED (no_active_task)

### BT-002: Unregistered skill rejection
- Operation: mutation with skill_id=nonexistent-skill
- Guard: `pre_mutation_guard.py`
- Result: **GUARD_ENFORCED** — BLOCKED (no_registered_skill_bound)

### BT-003: Positive control (authorized mutation)
- Operation: valid task + active skill (add-python-api)
- Guard: `pre_mutation_guard.py`
- Result: **POSITIVE_CONTROL_PASS** — AUTHORIZED

### BT-004: CI detection of known ungoverned commit
- Target: commit 787b43e2 (known UNGOVERNED_MUTATION)
- Guard: `ci_skill_attribution_check.py`
- Result before transcript: **GUARD_ENFORCED** — FAIL, ungoverned=1, exit 1
- Result after retroactive transcript: **REMEDIATION_RECOGNIZED** — PASS, governed=1

### BT-005: Direct bypass proof (primary finding)
- Operation: hypothetical direct Edit/Write tool invocation without calling guard
- Guard: NONE (no automatic interception)
- Result: **BYPASS_PROVEN** — agent could mutate src/ without technical barrier
- First unenforced boundary: Edit/Write/Bash tool invocation

### BT-006: New unregistered script detection
- Operation: create tools/supervisor/my_oneoff_script.py directly
- Guard: `ci_skill_attribution_check.py` (does NOT check tools/ paths)
- Result: **BYPASS_POSSIBLE** — tools/ additions are undetected

**Pilots not yet run** (pending TC-SGF-001 through TC-SGF-005):
- Pilot 1 full (pre-commit hook rejection) — needs TC-SGF-001
- Pilot 2 (Codex direct mutation rejection) — needs TC-SGF-003
- Pilot 8 (machinery-healing sprint through skills) — needs TC-SGF-002
- Pilot 10 (taskcard state mutation rejection) — needs TC-SGF-004
- Pilot 14 (concurrent Claude Code/Codex) — needs DEC-014 activation
- Pilot 15 (idempotent rerun) — partially proven (idempotency-verdict.yaml)

---

## Adoption Metrics

```yaml
governed_mutations_total: 2          # post-policy src/ commits
skill_backed_mutations: 1            # BF-001 resolved
command_backed_mutations: 1          # same
receipt_backed_mutations: 1          # retroactive transcript accepted
direct_mutation_attempts: 2          # both post-policy commits
rejected_direct_mutations: 0         # no pre-mutation guard existed
accepted_direct_mutations: 2         # CURRENT GAP — target is 0
skills_reused: 2                     # per retroactive binding
skills_composed: 0
skills_repaired: 0
micro_skills_created: 2              # this sprint
duplicate_skills_prevented: 0
skill_created_not_used_violations: 0
claude_code_compliance_rate: 0.50    # 1/2 post-policy mutations
codex_compliance_rate: 0.00          # not yet activated
product_sprint_compliance_rate: 0.50
machinery_sprint_compliance_rate: 0.00  # not yet measured
```

**Production target:**
```yaml
accepted_direct_mutations: 0
receipt_backed_mutations: equals_governed_mutations_total
```

---

## Exact Paths

| Component | Path |
|-----------|------|
| Canonical policy | `docs/governance/skill-only-policy.yaml` |
| Skill registry | `.supervisor/skill-registry.yaml` |
| Command registry | `.claude/commands/command-registry.yaml` |
| Capability routing | `.supervisor/capability-routing-registry.yaml` |
| Taskcard schema | `.supervisor/schemas/stage2-taskcard-contract.schema.json` |
| Execution contract schema | `.supervisor/schemas/autonomous-execution-contract.schema.json` |
| Plan validator | NOT_IMPLEMENTED (EP-009-GAP) |
| Mutation guard | `tools/governance/pre_mutation_guard.py` |
| Receipt schema | `.supervisor/schemas/evidence-declaration.schema.json` |
| Claude Code adapter | `CLAUDE.md` + `AGENTS.md` (PROMPT_ONLY) |
| Codex adapter | `docs/governance/codex-adapter.md` |
| Supervisor enforcement | `tools/supervisor/autonomous_cycle.py` + `governance_validators.py` |
| CI check | `tools/governance/ci_skill_attribution_check.py` |
| CI workflow | `.github/workflows/ci.yml` (skill-attribution-check job) |
| Pilots | `reports/skill-governance-forensic/pilots/bypass-test-results.yaml` |
| Historical backfill | `reports/skill-governance-forensic/historical-backfill.yaml` |
| Idempotency verdict | `reports/skill-governance-forensic/idempotency-verdict.yaml` |
| Final audit | `reports/skill-governance-forensic/final-audit.md` (THIS FILE) |
| Micro-taskcards | `.supervisor/taskcards/skill-governance-forensic/TC-SGF-001..005.yaml` |
| Master plan section | `plans/master-plan.md §62` |

---

## Root Cause Analysis

### RC-001: No Pre-Mutation Technical Barrier (PRIMARY)

**First unenforced boundary:** The Claude Code Edit/Write/Bash tools and equivalent
Codex shell/patch tools are invoked directly with no interception from the skill
governance layer.

**Local cause:** The governance system was designed as a documentation+validation layer
(prompt instructions + post-declaration validators). No tool-layer hook exists.

**Systemic cause:** SKILL-GAP-008 (pre-commit hook) has been in "backlog" since 2026-06-24
without a concrete implementation plan. SKILL-GAP-012 (declaration bypass) is acknowledged
as a "known limitation" in `skill-first-policy.md` but not remediated.

**Why existing controls missed it:**
- Governance validators only fire when agents submit declarations
- Declaration submission is a best-effort step that agents can skip
- Prior audit (SKILL-FIRST-001) classified these as backlog rather than blocking

### RC-002: 96.1% of Python Tools Are AD_HOC

**Local cause:** The skill registry uses `implementation_paths` to classify "governed" tools.
Only 7 of 181 tools have registered implementation paths.

**Systemic cause:** Prompt-backed skills (`.md` files) were designed to be the primary
enforcement mechanism. The Python tools are considered internal infrastructure helpers.

**Assessment:** Reasonable design choice for LLM-executed skills. However, the core
autonomy tools (autonomous_cycle.py, governance_validators.py) should be registered as
implementations for the skills they back, for auditability.

### RC-003: Codex Governance Not Activated

**Local cause:** DEC-014 was explicitly deferred with no activation timeline.

**Systemic cause:** No repository-owned Codex entry point pointed to canonical governance
until `docs/governance/codex-adapter.md` was created this sprint.

**Assessment:** Medium severity — Codex is not actively used in this repository's
sprint cycles, so the immediate impact is low. TC-SGF-003 governs activation.

---

## Final Verdict

```
DIRECT_MUTATION_BYPASSES_REMAIN
```

**Justification:** The first unenforced boundary (Edit/Write/Bash tool invocation with
no automatic pre-mutation check) is proven by BT-005. Any agent can mutate `src/`
files without going through the skill system. The enforcement layer is voluntary
and relies on agent compliance with prompt-only instructions.

**Progress made this sprint:**
- Canonical policy document created (first time machine-readable)
- Runtime mutation guard implemented (EP-002)
- CI skill attribution check implemented (EP-006)
- Codex adapter created (pre-conditions for DEC-014 activation)
- 5 micro-taskcards govern remaining gaps (TC-SGF-001 through TC-SGF-005)
- Historical backfill accounted for

**Remaining work to reach `SKILL_COMMAND_ONLY_EXECUTION_ENFORCED_FOR_CLAUDE_CODE_CODEX_AND_ALL_SPRINTS`:**
1. TC-SGF-001: Pre-commit hook (closes SKILL-GAP-008 — primary bypass vector)
2. TC-SGF-002: V-SGF-001 supervisor validator (closes SKILL-GAP-012)
3. TC-SGF-003: Codex activation (closes DEC-014)
4. TC-SGF-004: Taskcard execution_contract gate
5. TC-SGF-005: Top-10 tool registrations
6. Remove `continue-on-error: true` from CI skill-attribution-check job
7. Run full 15-pilot matrix after all controls are in place
8. Achieve 100% compliance rate over ≥3 sprints
