# Layer Promotion Guide

**Authority:** TC-LHEAL-007 (glittery-splashing-manatee, 2026-07-13)

---

## What Makes a Subsystem Eligible for Layer Promotion

A subsystem earns a permanent layer when ALL 9 eligibility criteria are met:

1. **Unique ID** — `candidate_id` not already in `plans/layers/index.yaml`
2. **Unique name** — `canonical_name` not already registered
3. **Methodology proven** — `evidence_paths` non-empty AND ≥1 path exists on disk
4. **Responsibility declared** — `permanent_responsibility` non-empty
5. **Authority boundary** — both `upstream_layers` and `downstream_consumers` provided
6. **Upstreams resolve** — each `upstream_layer` ID in `plans/layers/index.yaml`
7. **Skills resolve** — each `skill_id` in `.supervisor/skill-registry.yaml`
8. **Competing authority** — WARNING if >60% token overlap with existing layer (not a blocker)
9. **Status valid** — `requested_status` in `{PROPOSED, GOVERNED_OPERATIONAL}`

---

## Using `layer_promotion.py`

### Create a new layer

```bash
python tools/supervisor/layer_promotion.py create \
  --request path/to/request.yaml
```

**Request YAML format:**
```yaml
candidate_id: L29
candidate_name: "Sample Corpus Assessment Layer"
permanent_responsibility: "Track sample corpus completeness per format"
upstream_layers: [L01, L06]
downstream_consumers: [L05, L07]
skill_ids: [inventory-format-dom]
command_ids: [inventory-format-dom]
evidence_paths: ["samples/by-format/"]
requested_status: PROPOSED
```

### Dry-run (show changes without writing)

```bash
python tools/supervisor/layer_promotion.py create \
  --request path/to/request.yaml --dry-run
```

### Update an existing layer

```bash
python tools/supervisor/layer_promotion.py update \
  --layer-id L28 \
  --set skill_ids=skill-a,skill-b,skill-c \
  --set maturity_current=4
```

Update is idempotent: second run with same args returns `total_changes=0`.

### Rollback

```bash
python tools/supervisor/layer_promotion.py rollback \
  --manifest .local/supervisor/layer-promotion-manifest.json
```

---

## V88: What It Checks and When It Fires

V88 (`validate_required_layers_at_terminal` in `governance_validators_layers.py`) fires when:
- `python tools/supervisor/write_plan_lock.py --plan-path ... --terminal` is called
- AND the plan declares `required_permanent_layers: [L-XX, ...]`
- OR the plan has `plan_type: product_certification` (infers `[L28]`)

**On FAIL** (missing layers): exits with code 2, prints which layers are missing and how to fix.

**Emergency bypass:** `--skip-v88` flag on `write_plan_lock.py`. Always audited in `.local/supervisor/v88-skipped.jsonl`.

---

## 3/7 vs 7/7 Registry Gap

`/create-permanent-layer-plan` (the .claude/commands/ prompt skill) covers **3 of 7** registries:
- ✅ `plans/layers/<slug>.md`
- ✅ `plans/layers/index.yaml`
- ✅ `plans/layers/change-ledger.jsonl`
- ❌ `plans/layers/task-register.yaml`
- ❌ `plans/layers/dependency-register.yaml`
- ❌ `plans/layers/handoff-register.yaml`
- ❌ `plans/layers/decision-register.yaml`

`layer_promotion.py create` covers **all 7** (dependency-register, handoff-register,
decision-register covered in `create` mode; `update` mode covers index.yaml + layer plan file).

For production use, prefer `layer_promotion.py` over the prompt skill.

---

## What TC-SUP-002 Will Enable (Current State Without It)

**Current state (without TC-SUP-002):**
- `generate_next_worker_prompt.py` does NOT read `plans/layers/task-register.yaml`
- Layer tasks like TC-CERT-L-003 never surface in `reports/supervisor/next-sprint.md`
- Layer tasks are INVISIBLE to the autonomous supervisor
- `check_continuation.py`, `sprint_executor_validate.py`, and `autonomous_cycle.py` do not enforce layer classification

**TC-SUP-002 (deferred separate sprint):**
- Adds G9 train group to `synthesize_trains()` in `generate_next_worker_prompt.py`
- Makes layer tasks appear automatically in next-sprint.md
- Enforces "NO PRIMARY LAYER → NO WORK" rule from `plans/layers/master.md §3`

**Workaround until TC-SUP-002:** Manually inject layer task IDs into `reports/supervisor/next-sprint.md` or schedule them in next-work-items.json.

---

## Honest Limits

- V83-V86 are WARN-only; they do not block sprints during bootstrap phase
- V88 fires only for `required_permanent_layers` or `product_certification` plans — plans with other types that produce layers are not yet protected
- Layer tasks are invisible to automation (TC-SUP-002 deferred)
- `layer_promotion.py update` only updates index.yaml and the layer plan file — it does not modify task-register, dependency-register, handoff-register, or decision-register
