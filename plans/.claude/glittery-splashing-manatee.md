# glittery-splashing-manatee
# Mission: CERT-LAYER-HEAL-20260710
# Plan Type: layer_formalization_healing

---

## What We Actually Found (Code-Level)

This plan is based on direct reads of:
- `tools/supervisor/write_plan_lock.py` — full
- `tools/supervisor/check_continuation.py` — full
- `tools/supervisor/governance_validators_layers.py` — full (266 lines, 4 functions)
- `tools/supervisor/sprint_executor_validate.py` — all 13 phases
- `tools/supervisor/generate_next_worker_prompt.py` — full (1,553 lines)
- `.supervisor/skill-registry.yaml` — create-permanent-layer-plan entry
- `.claude/commands/create-permanent-layer-plan.md` — full
- `plans/layers/index.yaml` — full, including L28/L01/L14 entries
- `plans/layers/dependency-register.yaml` — full

---

## Symptoms, Root Causes, and Structural Weaknesses

### Symptoms
1. `crispy-jingling-snail` (19 taskcards, `plan_type: product_certification`) closed on 2026-06-28. No `plans/layers/` entry for L28 existed at that moment.
2. L28 was created retroactively on 2026-06-29 by a separate sprint.
3. TC-CERT-L-003 ("register certification tools as skills") is still TODO. `certification-audit-layer.md` §1 has `skill_ids: []`, `command_ids: []`.
4. `index.yaml` L28 entry has `skill_ids: [certification-dashboard]` — one skill, not nine.

### Root Causes (Confirmed by Code)

**RC-1 — `write_plan_lock.py` calls zero validators before writing `TERMINAL_CLOSED`**

Confirmed at lines 264–390. The terminal path is:
```python
write_lock(plan_path, ..., terminal=True)
# → sets status: "TERMINAL_CLOSED"
# → NO validator calls
# → NO plans/layers/ reference anywhere in the file
```
The only pre-terminal check is `lifecycle_audit` (lines 292–320), which fires only when `--audit-gate` is passed and is scoped to `plan_type: machinery_hardening`. For `product_certification` plans, no audit fires.

**RC-2 — The plan schema has no `required_permanent_layers` field**

`crispy-jingling-snail.md` has `plan_type: product_certification` but no `required_permanent_layers:` field. There is no schema that infers one from the other. Nothing told the closeout machinery "this plan type must produce a layer."

**RC-3 — `/create-permanent-layer-plan` is a prompt template, not Python code**

Confirmed: `.claude/commands/create-permanent-layer-plan.md` is a specification document. It tells Claude what to do but has no Python implementation. It covers only 3 of 7 registries:
- ✅ `plans/layers/<slug>.md`
- ✅ `plans/layers/index.yaml`
- ✅ `plans/layers/change-ledger.jsonl`
- ❌ `plans/layers/task-register.yaml`
- ❌ `plans/layers/dependency-register.yaml`
- ❌ `plans/layers/handoff-register.yaml`
- ❌ `plans/layers/decision-register.yaml`

The `mandatory_validations: [no_duplicate_layer_id, file_written, index_updated]` in skill-registry.yaml are instructions to Claude, not enforced in code. This means layer creation is only as reliable as the agent following the prompt.

**RC-4 — V83–V86 are WARN-only with no blocking power**

All four functions in `governance_validators_layers.py` return `"result": "WARN"`. None are called from `write_plan_lock.py`. Even if V84 fires and says "L28 doesn't exist," no sprint is blocked and terminal closeout proceeds.

**RC-5 — Layer tasks are invisible to the autonomous supervisor**

`generate_next_worker_prompt.py` reads: POC targets, gap-extraction fixtures, supervisor review grades, product code ledger. It synthesizes 8 train groups (G1–G8, hardcoded in `GROUP_DEFS` at lines 104–113). It does not read `plans/layers/task-register.yaml`. TC-CERT-L-003 has never appeared in a `next-sprint.md` prompt and will not until TC-SUP-002 is implemented.

### Structural Weaknesses

**SW-1 — The governance system enforces via prompts, not code, for the most critical operations**

Layer creation (`/create-permanent-layer-plan`) is a prompt. Its "mandatory validations" are prose. This is the root of why 4 of 7 registries were left unupdated during L28's creation — the prompt says to update 3, and the fourth through seventh require separate skill calls that can be forgotten.

**SW-2 — The layer system's governance contract (master.md §3) is aspirational, confirmed**

"NO PRIMARY LAYER → NO WORK / NO WORK LOG → NO CONTINUATION" — none of these are enforced in `check_continuation.py`, `sprint_executor_validate.py`, or `autonomous_cycle.py`. Section §22 explicitly documents this: "NOT YET IMPLEMENTED. This is TC-SUP-002."

**SW-3 — TC-SUP-002 integration is more complex than it appears**

Adding layer tasks to work selection requires adding a G9 group to `synthesize_trains()` in `generate_next_worker_prompt.py` (lines 181–440, ~260 lines of complex train-synthesis logic). This is not a small addition. The existing G1–G8 groups read specific data structures (review grades, gap fixtures, POC targets). Layer tasks have a different data shape. This requires its own sprint with its own evidence declaration, not a side addition to this plan.

**SW-4 — `skill_ids: []` in certification-audit-layer.md is cosmetic, not functional**

The 9 certification tools (Python executables in `tools/certification/`) work regardless of what this metadata field says. The gap matters for discoverability, not execution.

---

## What Is Actually Breaking Consistency Across Reruns

1. **Future `plan_type: product_certification` plans will close without L28** — nothing in the terminal path checks for it. RC-1 and RC-2 will repeat.

2. **Layer creation will remain incomplete** — `/create-permanent-layer-plan` covers 3/7 registries. Every new layer will have 4 registries missing unless someone manually runs additional skills. RC-3 will repeat.

3. **Layer tasks will stay invisible to the supervisor** — TC-CERT-L-003 and all other layer tasks will never surface in `next-sprint.md`. RC-5 will repeat until TC-SUP-002 is implemented.

4. **V83–V86 will generate warnings that are ignored** — There is no escalation path from WARN to enforcement. SW-1 will repeat.

---

## What to Preserve

1. **plans/layers/ directory, 7 registries, 28 layer files** — architecturally correct, well-designed
2. **39-section template** — appropriate depth; the 4-registry gap in `/create-permanent-layer-plan` is a prompt-coverage problem, not a template problem
3. **V83–V86 as WARN-only during bootstrap** — correct decision; don't make them FAIL until TC-SUP-002 makes them actionable
4. **skill-registry.yaml structure with `implementation_paths`** — good
5. **Control index SQLite** — good queryability
6. **TC-SUP-002 as the future integration point** — don't preempt it with a parallel system
7. **The lifecycle_audit pattern in write_plan_lock.py** — this is the right integration model; V88 should follow the same pattern

---

## What Must Be Redesigned

### R1 — `layer_promotion.py`: Python code that covers all 7 registries

The prompt-based `/create-permanent-layer-plan` is insufficient for production. The fix is a Python implementation that updates all 7 registries in a single invocation. This makes layer creation testable, idempotent, and not dependent on Claude following prompt instructions correctly.

This replaces the 6-step manual process (create-permanent-layer-plan + register-layer-task + update-layer-master-index + 3 manual edits) with one command.

### R2 — V88 terminal gate in `write_plan_lock.py`

Add one validation call to the `--terminal` path, following the existing `lifecycle_audit` pattern. Narrow scope: fires only when plan declares `required_permanent_layers:` OR has `plan_type: product_certification`. Does not touch the non-terminal path.

### R3 — `required_permanent_layers` as a plan header field

A plan with `plan_type: product_certification` that doesn't declare `required_permanent_layers: [L28]` should fail a linter check — not at runtime, but as a pre-commit or pre-terminal advisory. Document the field in the plan schema.

### R4 — Complete TC-CERT-L-003 concretely

Use the repaired tool to update L28's skill_ids/command_ids across all 7 registries and close the task. This is overdue immediate work.

### R5 — Update `/create-permanent-layer-plan` skill to reference `layer_promotion.py`

The skill's `implementation_paths` in skill-registry.yaml should point to `tools/supervisor/layer_promotion.py`. The command file should note that for production use, `layer_promotion.py` covers all 7 registries. This closes the gap between what the prompt says and what the code does.

---

## What Is Explicitly Out of Scope

**TC-SUP-002** (wire layer index to supervisor work selection) — requires adding a G9 group to `synthesize_trains()` in `generate_next_worker_prompt.py`, touching ~260 lines of complex train-synthesis logic. This is its own sprint with its own evidence and risks. This plan documents the gap but does not implement it.

**Upgrading V83–V86 to FAIL level** — premature until TC-SUP-002 makes layer classification mandatory for all work.

**Auto-syncing 39-section layer files** — no consumption path exists until TC-SUP-002; auto-sync creates churn without benefit.

**`sprint_executor_validate.py` Phase 14** — The 13 existing phases run at declaration time (sprint submission), not at terminal time. Adding a Phase 14 there would check every sprint declaration for missing layers, which is wrong — layers should only be required at terminal closeout. The right integration point is `write_plan_lock.py`.

---

## Taskcards

### TC-LHEAL-001 — Forensics & Baseline Capture
**Type:** LAYER_FORENSICS
**Status:** TODO

**Objective:** Generate a precise, hash-backed baseline snapshot before any changes. Establish the ground truth for the idempotency proof.

**Steps:**
1. Parse `plans/layers/index.yaml` L28 entry; record `skill_ids`, `command_ids`, `maturity_current`, `next_task_id`
2. Parse `plans/layers/task-register.yaml` TC-CERT-L-003 entry; record `status`, `current_stage`
3. Read `plans/layers/certification-audit-layer.md` lines 35-40 (§1 metadata); confirm `skill_ids: []`
4. Grep `tools/supervisor/governance_validators_layers.py` for V87, V88 — confirm absent
5. Grep `tools/supervisor/write_plan_lock.py` for "plans/layers", "required_permanent", "governance_validators" — confirm absent
6. Grep `tools/supervisor/generate_next_worker_prompt.py` for "task-register" — confirm absent
7. SHA-256 hash: `plans/layers/certification-audit-layer.md`, `plans/layers/index.yaml`, `plans/layers/task-register.yaml`
8. Write to `.local/evidences/layer-heal-001/original-state/baseline.yaml`

**Evidence:** `baseline.yaml` with SHA-256 hashes and specific field values confirming pre-change state
**Completion check:** 7 findings documented; hashes recorded for idempotency comparison

---

### TC-LHEAL-002 — V88: Terminal Closeout Gate
**Type:** CLOSEOUT_GATE_REPAIR
**Status:** TODO
**Depends on:** TC-LHEAL-001

**Objective:** Add a FAIL-level validator that blocks `write_plan_lock.py --terminal` when a plan declares `required_permanent_layers` that don't exist in `plans/layers/index.yaml`. This is the exact point where crispy-jingling-snail should have been blocked.

**Implementation — `tools/supervisor/governance_validators_layers.py`:**

Add function `validate_required_layers_at_terminal(plan_path: str, repo_root: Path) -> dict`:

```python
def validate_required_layers_at_terminal(plan_path: str, repo_root: Path) -> dict:
    """V88: FAIL if plan's required_permanent_layers are absent from plans/layers/index.yaml.
    Called ONLY from write_plan_lock.py --terminal. Not called during sprint validation.

    Triggers on either:
      1. Plan header has `required_permanent_layers: [L-XX, ...]`
      2. Plan header has `plan_type: product_certification` (infers [L28])

    Returns:
      {"result": "PASS"} — no declared obligations, or all layers present
      {"result": "SKIP"} — plan file unreadable or no metadata block
      {"result": "FAIL",
       "missing_layers": [layer_id, ...],
       "fix_command": "python tools/supervisor/layer_promotion.py --...",
       "hint": "Run fix_command, then retry write_plan_lock.py --terminal"}
    """
    plan_text = Path(plan_path).read_text(errors="replace")

    # Extract YAML metadata block (```yaml ... ``` in first 80 lines)
    header = _extract_plan_header(plan_text[:3000])
    if not header:
        return {"result": "SKIP", "reason": "no_parseable_header"}

    required = header.get("required_permanent_layers") or []
    plan_type = header.get("plan_type", "")

    # Infer from plan_type
    if not required and plan_type == "product_certification":
        required = ["L28"]

    if not required:
        return {"result": "PASS", "reason": "no_obligations_declared"}

    # Read index.yaml
    index_path = repo_root / "plans" / "layers" / "index.yaml"
    if not index_path.exists():
        return {"result": "FAIL", "missing_layers": required,
                "hint": "plans/layers/index.yaml not found"}

    index = yaml.safe_load(index_path.read_text())
    registered = {e["layer_id"] for e in index.get("layers", [])}

    missing = [lid for lid in required if lid not in registered]
    if missing:
        return {
            "result": "FAIL",
            "missing_layers": missing,
            "fix_command": f"python tools/supervisor/layer_promotion.py --layer-id {missing[0]} --help",
            "hint": "Create the required layer(s), then retry: python tools/supervisor/write_plan_lock.py --plan-path ... --terminal"
        }

    return {"result": "PASS", "layers_verified": required}
```

Helper: `_extract_plan_header(text: str) -> dict | None` — extracts and parses the first `\`\`\`yaml ... \`\`\`` block.

**Integration — `tools/supervisor/write_plan_lock.py`:**

In the `--terminal` branch (before the `write_lock()` call at lines ~327-340), add:

```python
if args.terminal:
    # V88: check required permanent layers before writing TERMINAL_CLOSED
    v88 = validate_required_layers_at_terminal(args.plan_path, repo_root)
    if v88["result"] == "FAIL":
        print(f"\nBLOCKED: Cannot write TERMINAL_CLOSED — missing required layers:")
        for lid in v88["missing_layers"]:
            print(f"  - {lid}")
        print(f"\nFix: {v88['fix_command']}")
        print(f"Hint: {v88['hint']}")
        sys.exit(2)  # exit 2 = blocked by governance, not internal error
    # ... existing write_lock() call follows
```

**Exit code 2** is new and distinct from exit 1 (internal error). This lets callers distinguish "missing layer" from "tool failure."

**Scope constraint:** `validate_required_layers_at_terminal` is called ONLY from this one insertion point. It is NOT added to sprint validation phases, V83–V86 call sites, or check_continuation.

**Backward compatibility:** Plans without `required_permanent_layers` or `plan_type: product_certification` return `PASS` unconditionally. Zero existing plans are affected unless they explicitly declare obligations.

**Tests (`tests/supervisor/test_v88_terminal_gate.py`):**
- `test_v88_skip_when_no_header` — unstructured plan → SKIP
- `test_v88_pass_when_no_obligations` — ordinary plan, no field → PASS
- `test_v88_pass_when_layer_exists` — L28 declared, L28 in index → PASS
- `test_v88_fail_when_layer_missing` — L28 declared, L28 absent from index → FAIL, missing_layers=[L28]
- `test_v88_infer_from_product_certification_plan_type_layer_present` → PASS
- `test_v88_infer_from_product_certification_plan_type_layer_absent` → FAIL
- `test_v88_write_plan_lock_exits_2_when_v88_fails` — integration: `write_plan_lock.py --terminal` on a fixture plan with missing layer → exit code 2
- `test_v88_write_plan_lock_succeeds_when_v88_passes` — integration: with layer present → exit code 0

**Risk:** If V88 returns FAIL on a real terminal event incorrectly (false positive), the agent is blocked from closing its plan. Mitigation: `--skip-v88` emergency flag on `write_plan_lock.py` that logs a WARNING but proceeds. This must be auditable, so it writes to `.local/supervisor/v88-skipped.jsonl` with timestamp and reason. Do not add `--skip-v88` silently.

---

### TC-LHEAL-003 — `layer_promotion.py`: Python Implementation Covering All 7 Registries
**Type:** LAYER_PROMOTION
**Status:** TODO
**Depends on:** TC-LHEAL-001

**Objective:** Create a Python tool that replaces the 6-step manual process (prompt-based skill + 5 separate registry edits) with one testable, idempotent command. This is what `/create-permanent-layer-plan` should eventually delegate to.

**File:** `tools/supervisor/layer_promotion.py` (~350 LOC)

**CLI:**
```bash
# Create a new layer (all 7 registries)
python tools/supervisor/layer_promotion.py create --request path/to/request.yaml [--dry-run]

# Update an existing layer (e.g., add skill_ids)
python tools/supervisor/layer_promotion.py update --layer-id L28 \
  --set skill_ids=certification-dashboard,certification-stub-detector,... [--dry-run]

# Show what would change without writing
python tools/supervisor/layer_promotion.py dry-run --request path/to/request.yaml

# Rollback from manifest (remove entries added in last run)
python tools/supervisor/layer_promotion.py rollback --manifest .local/supervisor/layer-promotion-manifest.json
```

**Eligibility gate (for `create` mode — 9 checks, all must pass):**

| Check | Condition | REJECT reason |
|-------|-----------|--------------|
| ID unique | `candidate_id` not in `index.yaml` with conflicting data | `DUPLICATE_LAYER_ID` |
| Name not conflicting | No layer with same `canonical_name` | `DUPLICATE_LAYER_NAME` |
| Methodology proven | `evidence_paths` non-empty AND ≥1 path exists on disk | `METHODOLOGY_NOT_PROVEN` |
| Responsibility declared | `permanent_responsibility` non-empty | `RESPONSIBILITY_NOT_DECLARED` |
| Authority boundary | Both `upstream_layers` and `downstream_consumers` provided | `AUTHORITY_BOUNDARY_MISSING` |
| Upstreams resolve | Each `upstream_layer` ID in `index.yaml` | `UNKNOWN_UPSTREAM_LAYER` |
| Skills resolve | Each `skill_id` in `.supervisor/skill-registry.yaml` | `UNKNOWN_SKILL_ID` |
| No competing authority | No existing layer with `permanent_responsibility` textually overlapping >60% | `COMPETING_AUTHORITY` (WARNING, not FAIL — manual review advised) |
| Status valid | `requested_status` in {PROPOSED, GOVERNED_OPERATIONAL} | `INVALID_STATUS` |

Note on competing authority: Use simple token overlap, not semantic matching. Output a WARNING with the overlapping layer ID and let the human decide. Do not FAIL on this check — false positives would block legitimate new layers.

**Transaction — 7 registries in order:**

All changes are recorded in a manifest before writing. If any write fails, the manifest identifies what was partially written (for rollback).

1. **`plans/layers/<slug>.md`** — Generate from 39-section template populated with request fields. If file exists: merge `skill_ids`/`command_ids` only (don't overwrite §34/§35 work logs). Read-validate-write: parse generated YAML block before writing.

2. **`plans/layers/index.yaml`** — Append or update L-XX entry (28-field schema confirmed from code read). Use `ruamel.yaml` or `PyYAML` with explicit block-style to preserve existing structure. Never sort or reformat existing entries.

3. **`plans/layers/task-register.yaml`** — Add bootstrap taskcard with `status: TODO`, `priority: P1`, `dependencies: []`. Use the same schema as existing TC-LP-001 entry.

4. **`plans/layers/dependency-register.yaml`** — Add DEP-XXX entries for each `upstream_layer`. Schema: `dependency_id`, `producer_layer`, `consumer_layer`, `dependency_type: UPSTREAM_DATA`, `strength: REQUIRED`, `current_unmet: true/false`. Auto-increment DEP-NNN from max existing.

5. **`plans/layers/handoff-register.yaml`** — Add HO-XXX entry for each downstream consumer relationship. Schema matches existing HO-008 structure.

6. **`plans/layers/decision-register.yaml`** — Add DEC-XXX entry with `decision_type: ACCEPT`, `rationale: "Layer promotion via layer_promotion.py"`.

7. **`plans/layers/change-ledger.jsonl`** — Append `{"event_id": "CL-NNN", "event_type": "LAYER_ADDED", "layer_id": "L-XX", ...}`. JSONL is append-only — no read-modify-write needed; safest registry to update.

**Idempotency contract:**

Before writing any registry entry, compute a "match key" (layer_id for index, dependency pair for dep-register, etc.) and check if it already exists with equivalent data. If yes: skip write for that registry, record in manifest as `action: ALREADY_CURRENT`. On a second run with identical input, every registry should show `ALREADY_CURRENT` and `total_changes: 0`.

**Manifest (``.local/supervisor/layer-promotion-manifest.json``):**
```json
{
  "run_id": "2026-07-10T...",
  "layer_id": "L28",
  "mode": "update",
  "changes": [
    {"registry": "index.yaml", "action": "UPDATED", "field": "skill_ids", "before": "[certification-dashboard]", "after": "[...]"},
    {"registry": "certification-audit-layer.md", "action": "UPDATED", "section": "§20"},
    {"registry": "change-ledger.jsonl", "action": "APPENDED", "event_id": "CL-005"}
  ],
  "total_changes": 3,
  "idempotency": "CHANGES_MADE"
}
```

**Tests (`tests/supervisor/test_layer_promotion.py`):**
- `test_create_new_layer_writes_all_7_registries` — fixture request → verify all 7 files updated
- `test_create_is_idempotent_second_run` — same request twice → second run `total_changes: 0`
- `test_update_skill_ids_on_existing_layer` — `--update --layer-id L28` → index.yaml and plan file updated
- `test_update_is_idempotent` — same `--update` twice → second `total_changes: 0`
- `test_duplicate_layer_id_rejected` — `candidate_id: L28` for existing layer (create mode) → REJECTED
- `test_missing_evidence_rejected` — `evidence_paths: []` → REJECTED: METHODOLOGY_NOT_PROVEN
- `test_unknown_skill_id_rejected` — `skill_ids: [nonexistent-skill]` → REJECTED: UNKNOWN_SKILL_ID
- `test_unknown_upstream_layer_rejected` — `upstream_layers: [L99]` → REJECTED: UNKNOWN_UPSTREAM_LAYER
- `test_dry_run_writes_nothing` — `--dry-run` → no files written, changeset printed
- `test_rollback_removes_created_entries` — create + rollback → all 7 registries back to pre-creation state
- `test_competing_authority_warns_not_fails` — overlapping responsibility → WARNING in output, not REJECTED

**Risk: YAML write correctness.** The hardest part. Reading a YAML file with `yaml.safe_load()`, modifying in Python, and re-writing with `yaml.dump()` strips comments and can alter ordering. Mitigation: use `ruamel.yaml` (preserves comments and ordering). If `ruamel.yaml` is not available in the venv, fall back to `yaml.safe_load()` + `yaml.dump()` with `default_flow_style=False` and `allow_unicode=True`, and document the comment-stripping behavior. Test this explicitly.

**Risk: Partial write failure.** If Python crashes mid-transaction (OOM, disk full), some registries are updated and others aren't. Mitigation: write manifest at START (recording intent), then write registries in order. On failure, manifest shows which entries were written. `rollback` command reads manifest and reverts.

---

### TC-LHEAL-004 — Complete TC-CERT-L-003 Using `layer_promotion.py`
**Type:** LAYER_SKILL_WIRING
**Status:** TODO
**Depends on:** TC-LHEAL-003

**Objective:** Close TC-CERT-L-003 by linking 9 certification skills to L28 across all relevant registries.

**The 9 skills to link** (confirmed from skill-registry.yaml, `product_track: governance`):
- `certification-assertion-scorer`
- `certification-dashboard`
- `certification-dotnet-assertion-scorer`
- `certification-exception-checker`
- `certification-fix-weak-assertions`
- `certification-generate-exception-tests`
- `certification-generate-security-tests`
- `certification-inventory-extractor`
- `certification-stub-detector`

**Command:**
```bash
python tools/supervisor/layer_promotion.py update \
  --layer-id L28 \
  --set skill_ids=certification-assertion-scorer,certification-dashboard,certification-dotnet-assertion-scorer,certification-exception-checker,certification-fix-weak-assertions,certification-generate-exception-tests,certification-generate-security-tests,certification-inventory-extractor,certification-stub-detector \
  --set command_ids=certification-assertion-scorer,certification-dashboard,certification-dotnet-assertion-scorer,certification-exception-checker,certification-fix-weak-assertions,certification-generate-exception-tests,certification-generate-security-tests,certification-inventory-extractor,certification-stub-detector \
  --set maturity_current=4
```

**Additional manual updates** (cannot be automated by `--update` flag):
- `plans/layers/certification-audit-layer.md` §20: replace "Current skill IDs: `[]`" with listed skills
- `plans/layers/certification-audit-layer.md` §29→§31: move TC-CERT-L-003 from ready to completed
- `plans/layers/certification-audit-layer.md` §34: append work log entry
- `plans/layers/certification-audit-layer.md` §35: append verification log entry
- `plans/layers/certification-audit-layer.md` §36 handoff: update next_task_id to null
- `plans/layers/task-register.yaml` TC-CERT-L-003: `status: CLOSED`, `closed_at`, `skill_ids`, `closure_summary`

**Verification:**
```bash
python -c "
import yaml
# Check index.yaml
idx = yaml.safe_load(open('plans/layers/index.yaml').read())
l28 = next(x for x in idx['layers'] if x['layer_id'] == 'L28')
skills = l28.get('skill_ids', [])
assert len(skills) == 9, f'Expected 9 skills, got {len(skills)}: {skills}'
assert l28['maturity_current'] == 4, f'Expected maturity 4, got {l28[\"maturity_current\"]}'

# Check task register
reg = yaml.safe_load(open('plans/layers/task-register.yaml').read())
tc = next(t for t in reg['tasks'] if t['task_id'] == 'TC-CERT-L-003')
assert tc['status'] == 'CLOSED', f'Expected CLOSED, got {tc[\"status\"]}'

print('TC-CERT-L-003 verification PASS')
"
```

---

### TC-LHEAL-005 — Plan Schema: `required_permanent_layers` Field
**Type:** DOCUMENTATION + LAYER_VALIDATOR
**Status:** TODO
**Depends on:** TC-LHEAL-001

**Objective:** Establish `required_permanent_layers` as a recognized plan header field, document its inference rules, and backfill crispy-jingling-snail.

**File: `docs/governance/plan-header-contract.md`** (create new):
- Canonical list of recognized plan header fields
- `plan_type` vocabulary: `product_certification`, `machinery_hardening`, `layer_formalization_healing`, `product_deepening`
- `required_permanent_layers: [L-XX, ...]` — when to declare, what V88 does with it
- Inference rules: `product_certification` → `[L28]` unless overridden
- Example plan headers

**Update `plans/.claude/crispy-jingling-snail.md` header** (backfill only — not re-execution):
Add to the YAML metadata block:
```yaml
required_permanent_layers: [L28]
# Added retroactively 2026-07-10: this field was absent at plan closure (2026-06-28),
# which allowed TERMINAL_CLOSED without L28 existing. V88 now enforces this.
```
This is a historical record, not re-opening the plan.

**Do NOT create a `.supervisor/schemas/plan-header.schema.json`** yet — this would be a JSON Schema that validation tooling needs to read. We don't have that tooling. Document the field in prose for now. The schema can be formalized when `sprint_executor_validate.py` adds a Phase 0 that validates plan headers.

---

### TC-LHEAL-006 — Update `/create-permanent-layer-plan` Skill Reference
**Type:** LAYER_SKILL_WIRING
**Status:** TODO
**Depends on:** TC-LHEAL-003

**Objective:** Close the gap between what the skill promises and what it delivers. Update skill-registry.yaml to reference `layer_promotion.py` as the implementation.

**Update `.supervisor/skill-registry.yaml` entry for `create-permanent-layer-plan`:**
```yaml
implementation_paths:
  - tools/supervisor/layer_promotion.py   # ← add this (Python, covers all 7 registries)
  - plans/layers/                          # ← keep existing (prompt template reference)
notes: >
  For production use, invoke `tools/supervisor/layer_promotion.py create --request <file>`
  which covers all 7 registries. The .claude/commands/ file documents the manual fallback
  that covers only 3 registries (plan file, index.yaml, change-ledger.jsonl).
  skill_ids field must be populated in the same invocation (not a separate task).
```

**Update `.claude/commands/create-permanent-layer-plan.md`** — add at top:
```markdown
> **Production path:** `python tools/supervisor/layer_promotion.py create --request <file>`
> This covers all 7 registries including task-register, dependency-register, handoff-register,
> and decision-register. Skill wiring (skill_ids) is included in the same transaction.
> The prompt instructions below are the fallback for environments without Python access.
```

---

### TC-LHEAL-007 — Document the TC-SUP-002 Gap and Layer Task Visibility
**Type:** DOCUMENTATION
**Status:** TODO
**Depends on:** TC-LHEAL-001

**Objective:** Make the supervisor-layer decoupling explicit in all relevant files so future agents don't mistake aspirational governance for enforced governance.

**Updates:**

`plans/layers/master.md §22` — replace "NOT YET IMPLEMENTED" note with:
```
GAP-SUP-002 (CONFIRMED, DEFERRED):
- generate_next_worker_prompt.py reads: POC targets, gap fixtures, review grades.
- It does NOT read plans/layers/task-register.yaml.
- G1-G8 train groups are hardcoded in GROUP_DEFS (lines 104-113 of generate_next_worker_prompt.py).
- A G9 layer-task group would require modifying synthesize_trains() (lines 181-440).
- This is a separate sprint. Until TC-SUP-002 is implemented, layer tasks are INVISIBLE
  to the autonomous supervisor. They must be manually scheduled in next-sprint.md.
- Affected tasks: TC-CERT-L-003, TC-SAL-001, TC-QN-001, TC-SUP-001, TC-FEAT-001,
  and all other TODO tasks in task-register.yaml.
```

`plans/layers/certification-audit-layer.md §14` (Gap Register) — add:
```
CERT-LAYER-GAP-001: Layer tasks invisible to supervisor (TC-SUP-002 TODO).
TC-CERT-L-003 has been in TODO state since 2026-06-29 and was never surfaced by
the autonomous loop. It required manual identification and scheduling.
```

`docs/governance/layer-promotion-guide.md` (create) — full guide:
- What makes a subsystem eligible for layer promotion (9 criteria)
- How to use `layer_promotion.py` (create, update, dry-run, rollback)
- What V88 checks and when it fires
- The 3/7 vs 7/7 registry gap in the prompt skill vs Python tool
- What TC-SUP-002 will enable (and what the current state is without it)
- How to manually schedule a layer task (next-sprint.md injection) until TC-SUP-002 is done
- Honest limits: V83-V86 are warnings; layer tasks are invisible to automation

---

### TC-LHEAL-008 — Future-Layer Pilot + Negative Controls
**Type:** FUTURE_LAYER_PILOT
**Status:** TODO
**Depends on:** TC-LHEAL-003

**Objective:** Prove `layer_promotion.py create` works on a new candidate in fixture mode. Prove negative controls reject invalid candidates.

**Fixture layer candidate:**
```yaml
# tests/fixtures/layers/pilot-request.yaml
candidate_id: L-PILOT-TEST
candidate_name: "Sample Corpus Assessment Layer (Fixture Only)"
permanent_responsibility: "Track sample corpus completeness per format (test fixture, not production)"
cross_cutting: true
upstream_layers: [L01, L06]
downstream_consumers: [L05, L07]
skill_ids: [inventory-format-dom]
command_ids: [inventory-format-dom]
evidence_paths: ["samples/by-format/"]
requested_status: PROPOSED
fixture_mode: true  # writes to tests/fixtures/layers/, not plans/layers/
```

**Fixture mode:** When `fixture_mode: true`, `layer_promotion.py` writes to `tests/fixtures/layers/l-pilot-test-layer.md` and to in-memory fixtures of the 7 registries rather than the real registry files. The manifest still records what would have changed. This prevents the test from polluting production registries.

**Pilot runs:**
```bash
# Run 1: dry-run verification
python tools/supervisor/layer_promotion.py create \
  --request tests/fixtures/layers/pilot-request.yaml --dry-run

# Run 2: actual creation (fixture mode)
python tools/supervisor/layer_promotion.py create \
  --request tests/fixtures/layers/pilot-request.yaml
# Verify: tests/fixtures/layers/l-pilot-test-layer.md created

# Run 3: idempotency proof
python tools/supervisor/layer_promotion.py create \
  --request tests/fixtures/layers/pilot-request.yaml
# Must output: total_changes: 0, idempotency: ALREADY_CURRENT
```

**Negative controls:**
```bash
# 1. Duplicate production layer ID
python tools/supervisor/layer_promotion.py create \
  --request tests/fixtures/layers/pilot-request-duplicate-l28.yaml
# Expected: REJECTED: DUPLICATE_LAYER_ID

# 2. Empty evidence paths
python tools/supervisor/layer_promotion.py create \
  --request tests/fixtures/layers/pilot-request-no-evidence.yaml
# Expected: REJECTED: METHODOLOGY_NOT_PROVEN

# 3. Unknown skill reference
python tools/supervisor/layer_promotion.py create \
  --request tests/fixtures/layers/pilot-request-bad-skill.yaml
# Expected: REJECTED: UNKNOWN_SKILL_ID

# 4. Unknown upstream layer
python tools/supervisor/layer_promotion.py create \
  --request tests/fixtures/layers/pilot-request-bad-upstream.yaml
# Expected: REJECTED: UNKNOWN_UPSTREAM_LAYER
```

**Cleanup:** Delete `tests/fixtures/layers/l-pilot-test-layer.md` after verification. The fixture request YAML files remain (they are test assets).

---

### TC-LHEAL-009 — Tests
**Type:** LAYER_VALIDATOR
**Status:** TODO
**Depends on:** TC-LHEAL-002, TC-LHEAL-003

**Files to create:**
- `tests/supervisor/test_v88_terminal_gate.py` — 8 tests (listed in TC-LHEAL-002)
- `tests/supervisor/test_layer_promotion.py` — 11 tests (listed in TC-LHEAL-003)

**Regression tests to run (must not regress):**
```bash
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v
# All 13 V83-V86 tests must still pass
```

---

### TC-LHEAL-010 — Idempotency Proof & Final Report
**Type:** IDEMPOTENCY + DOCUMENTATION
**Status:** TODO
**Depends on:** All previous taskcards

**Idempotency proof:**

```bash
# Step 1: Capture hashes after all changes
sha256sum plans/layers/certification-audit-layer.md \
          plans/layers/index.yaml \
          plans/layers/task-register.yaml \
          plans/layers/dependency-register.yaml \
          plans/layers/handoff-register.yaml \
          plans/layers/decision-register.yaml \
          plans/layers/change-ledger.jsonl > .local/evidences/layer-heal-001/verification/hashes-run1.txt

# Step 2: Re-run the update command
python tools/supervisor/layer_promotion.py update \
  --layer-id L28 \
  --set skill_ids=certification-assertion-scorer,certification-dashboard,...

# Step 3: Capture hashes again
sha256sum plans/layers/certification-audit-layer.md \
          plans/layers/index.yaml ... > .local/evidences/layer-heal-001/verification/hashes-run2.txt

# Step 4: Compare (timestamps in change-ledger.jsonl excluded from comparison)
diff .local/evidences/layer-heal-001/verification/hashes-run1.txt \
     .local/evidences/layer-heal-001/verification/hashes-run2.txt
# Must be empty diff (zero material changes)
```

**Final report:** `reports/layer-governance/certification-layer-healing-report.md`

Required sections:
1. Incident — what was missing, when, why
2. Structural analysis — RC-1 through RC-5, SW-1 through SW-4 (from this plan)
3. Code evidence — exact function names, line numbers, confirming each root cause
4. Failure boundary — `CERTIFICATION PROOF → [NO TERMINAL GATE] → TERMINAL_CLOSED`
5. Changes made — V88, layer_promotion.py, TC-CERT-L-003 closure, skill registration
6. What was NOT fixed — TC-SUP-002 explicitly deferred with justification
7. Verification results — test counts, idempotency comparison
8. Next actions — TC-SUP-002 as the remaining systemic gap

**Final verdict** (select one after verification):
- `CERTIFICATION_LAYER_BACKFILLED_AND_AUTONOMOUS_LAYER_FORMALIZATION_PROVEN` — if all checks pass
- `CERTIFICATION_LAYER_BACKFILLED_FUTURE_LAYER_AUTOMATION_REWORK_REQUIRED` — if pilot fails

---

## Execution Order

```
TC-LHEAL-001 (forensics — 1 hr)
  ├── TC-LHEAL-002 (V88 terminal gate — 2 hr)      ← implement first; highest structural value
  ├── TC-LHEAL-003 (layer_promotion.py — 4 hr)     ← parallel with TC-LHEAL-002
  │     ├── TC-LHEAL-004 (complete TC-CERT-L-003)  ← depends on layer_promotion.py
  │     ├── TC-LHEAL-006 (update skill reference)   ← depends on layer_promotion.py
  │     └── TC-LHEAL-008 (pilot + negative controls)
  ├── TC-LHEAL-005 (plan schema documentation)      ← parallel with TC-LHEAL-002/003
  └── TC-LHEAL-007 (document TC-SUP-002 gap)        ← parallel with TC-LHEAL-002/003
        └── TC-LHEAL-009 (tests — after 002 and 003 are done)
              └── TC-LHEAL-010 (idempotency + report)
```

TC-LHEAL-002 and TC-LHEAL-003 can proceed in parallel after forensics. TC-LHEAL-005 and TC-LHEAL-007 have no code dependencies and can run at any point.

---

## Key Files

| File | Action | LOC Change | Risk |
|------|--------|-----------|------|
| `tools/supervisor/governance_validators_layers.py` | Add V88 function | +60 | Low |
| `tools/supervisor/write_plan_lock.py` | Call V88 before TERMINAL_CLOSED (~line 327) | +12 | Medium — changes terminal path |
| `tools/supervisor/layer_promotion.py` | Create new | +350 | Medium — new tool, YAML write |
| `plans/layers/certification-audit-layer.md` | §1, §20, §29→31, §34, §35, §36 | +30 | Low |
| `plans/layers/index.yaml` | L28: skill_ids, maturity | +8 | Low |
| `plans/layers/task-register.yaml` | TC-CERT-L-003: CLOSED | +5 | Low |
| `plans/layers/change-ledger.jsonl` | Append CL-005 | +1 line | Low (append) |
| `plans/.claude/crispy-jingling-snail.md` | Add `required_permanent_layers` to header | +3 | Low |
| `.supervisor/skill-registry.yaml` | Add implementation_paths for create-permanent-layer-plan | +3 | Low |
| `.claude/commands/create-permanent-layer-plan.md` | Add production path note | +6 | Low |
| `docs/governance/layer-promotion-guide.md` | Create new | +200 | Low |
| `docs/governance/plan-header-contract.md` | Create new | +80 | Low |
| `tests/supervisor/test_v88_terminal_gate.py` | Create new | +120 | Low |
| `tests/supervisor/test_layer_promotion.py` | Create new | +200 | Low |
| `reports/layer-governance/certification-layer-healing-report.md` | Create new | +300 | Low |

---

## Tradeoffs and Risks

**YAML write correctness:** Reading a YAML file, modifying in Python, and re-writing can strip comments and reorder keys. `ruamel.yaml` preserves both; check if it's available in `.venv`. If not, `PyYAML` strips comments — document this and accept it. Test by writing a registry file and comparing parsed structure (not raw text) on read-back.

**V88 false positives:** If V88 fires incorrectly on a non-certification plan, the agent can't close the plan. The `--skip-v88` escape hatch (with mandatory audit log) is the safety valve. Keep the inference logic narrow: only `product_certification` plan type and explicit `required_permanent_layers` declarations trigger V88. Don't add new inferred types without code evidence.

**exit code 2 is new:** Any script that calls `write_plan_lock.py` and checks only for exit 0/1 will treat exit 2 as an error. Check `tools/supervisor/autonomous_cycle.py` and `tools/supervisor/sprint_executor.py` for hardcoded exit code checks before deploying. They should treat exit 2 as "BLOCKED_GOVERNANCE" not "TOOL_FAILURE."

**TC-SUP-002 is the remaining systemic gap:** This plan does not make layer tasks visible to the autonomous supervisor. After this plan completes, an agent can still close a `product_certification` plan without creating L28 IF the plan header omits `required_permanent_layers` — because V88 only fires on declared obligations or the one inferred type. Plans with other types that prove cross-cutting capabilities are not protected. This is an accepted limitation; the right fix requires TC-SUP-002.

**layer_promotion.py covers all 7 registries only in CREATE mode:** The `update` mode (used for TC-CERT-L-003) updates `index.yaml`, the layer plan file, and `change-ledger.jsonl`. It does NOT update task-register.yaml, dependency-register.yaml, handoff-register.yaml, or decision-register.yaml on update — those were already created during the original layer creation. This is correct behavior.

**Competing authority detection is advisory:** The 60% token overlap check for competing authority will have false positives (two layers that mention "certification" in their responsibility descriptions). Outputs WARNING, not REJECT. Humans must review.

---

## Completion Gate

This plan closes when:

| Check | Verified by |
|-------|------------|
| `plans/layers/certification-audit-layer.md` §1 `skill_ids` has 9 entries | Assertion script |
| `plans/layers/index.yaml` L28 `skill_ids` has 9 entries | Assertion script |
| `plans/layers/task-register.yaml` TC-CERT-L-003 `status: CLOSED` | Assertion script |
| `tools/supervisor/governance_validators_layers.py` contains V88 function | Grep |
| `tools/supervisor/write_plan_lock.py` calls V88 before TERMINAL_CLOSED | Grep |
| `tools/supervisor/layer_promotion.py` exists and `--help` works | Bash |
| `tests/supervisor/test_v88_terminal_gate.py` 8/8 PASS | pytest |
| `tests/supervisor/test_layer_promotion.py` 11/11 PASS | pytest |
| Existing `test_governance_validators.py` still 13/13 PASS | pytest (regression) |
| Pilot: `layer_promotion.py create --request pilot-request.yaml` → PROMOTED | Bash |
| Pilot: second run → `total_changes: 0` | Bash |
| 4 negative controls all REJECTED as expected | Bash |
| SHA-256 comparison: run1 vs run2 hashes are identical | diff |
| `reports/layer-governance/certification-layer-healing-report.md` exists | File check |

Does NOT close because:
- V83–V86 are promoted to FAIL level (not in scope)
- TC-SUP-002 is implemented (separate sprint)
- Layer tasks automatically surface in next-sprint.md (requires TC-SUP-002)
