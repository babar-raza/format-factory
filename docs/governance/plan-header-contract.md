# Plan Header Contract

Canonical reference for recognized plan header fields in Format Factory governed plans.

**Authority:** TC-LHEAL-005 (glittery-splashing-manatee, 2026-07-13)

---

## `plan_type` Vocabulary

| Value | Description | Layer Obligation |
|-------|-------------|-----------------|
| `product_certification` | Plan produces a certified product layer | Infers `required_permanent_layers: [L28]` |
| `machinery_hardening` | Plan repairs or hardens supervisor machinery | Triggers lifecycle_audit before TERMINAL_CLOSED |
| `layer_formalization_healing` | Plan heals a permanent layer governance gap | None (declare explicitly if needed) |
| `product_deepening` | Plan adds FOSS Python or .NET product features | None |

If `plan_type` is absent, no inferred obligations apply.

---

## `required_permanent_layers` Field

```yaml
required_permanent_layers: [L28]
```

**When to declare:** When your plan's completion produces or depends on a permanent layer entry in `plans/layers/index.yaml`.

**What V88 does with it:** Before writing `TERMINAL_CLOSED`, `write_plan_lock.py` calls `validate_required_layers_at_terminal` (V88 in `governance_validators_layers.py`). If any declared layer ID is absent from `plans/layers/index.yaml`, the terminal write is blocked with exit code 2.

**Inference rules:**
- `plan_type: product_certification` → `required_permanent_layers: [L28]` (inferred automatically if not declared)
- All other plan_types: no inference. Declare explicitly if needed.

**Emergency bypass:** `--skip-v88` flag on `write_plan_lock.py`. Always audited in `.local/supervisor/v88-skipped.jsonl`.

---

## Example Plan Headers

### Product certification plan

```yaml
# Mission: CERT-LAYER-HEAL-20260710
# Plan Type: product_certification
# required_permanent_layers: [L28]
```

### Machinery hardening plan

```yaml
# Mission: MCP-W1-002
# plan_type: machinery_hardening
```

### Layer formalization plan

```yaml
# Mission: CERT-LAYER-HEAL-20260710
# Plan Type: layer_formalization_healing
# required_permanent_layers: [L28]  # declare explicitly
```

---

## Backfill Note

`plans/.claude/crispy-jingling-snail.md` was closed 2026-06-28 without `required_permanent_layers` declared.
L28 was created retroactively 2026-06-29. V88 (added 2026-07-13) would have blocked this premature closure.
