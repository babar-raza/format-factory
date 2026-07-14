---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: PIPELINE_TOOL
created-by: TC-EXT-009-01
invocation_mode: automatic_pipeline
product_track: infrastructure
loc_budget: "<600 lines (frozen baseline; registration only)"
---

# /capability-compiler

Compile capability gap records (from the capability gap ledger) into feature IRs,
executable taskcards, and their supporting obligation/graph artifacts (Phases 0, 1,
2, 3, 3.5, 6, 7, 8 of the capability-to-feature compiler design).

## Invocation Mode (IMPORTANT)

This is a **pipeline tool, not a user-invoked slash command**. It has no interactive
workflow of its own. It is invoked automatically, every sprint, by
`tools/supervisor/capability_queue_consumer.py`, which in turn is called from
`tools/supervisor/autonomous_cycle.py` Step 2h ("CAPABILITY QUEUE CONSUMER").

This command file exists so `capability_compiler.py` has a formal, governed skill
identity (skill_id, routing entry, registry presence) — it does **not** define a new
manual workflow. Do not invoke `/capability-compiler` interactively as a first step;
if you need to run the underlying compiler directly for diagnostics, use the CLI form
below.

## Purpose

Given a gap record (`{format_id, function_name, ...}`), produce:
- a **feature IR** (spec-enriched intermediate representation, using SAL facts when available)
- an **executable taskcard** (`status: READY_TO_EXECUTE`, module/test targets, governance requirements)
- a **feature graph node** (dependency/spec-connection metadata)
- a **QName ontology attachment** (links to `qname-to-code-map-{fmt}.json` when present)
- a **test obligation matrix** and **evidence obligation matrix**
- a **gate readiness projection** (impact on Gate 4/8/11 readiness)

## Underlying Implementation

`tools/supervisor/capability_compiler.py` (521 lines). Functions:
`load_sal_facts`, `validate_sal_input` (Phase 0), `compile_gap_to_feature_ir` (Phase 1),
`compile_feature_ir_to_taskcard` (Phase 2), `compile_gap_to_feature_graph` (Phase 3),
`attach_qname_ontology` (Phase 3.5), `compile_test_obligation_matrix` (Phase 6),
`compile_evidence_obligation_matrix` (Phase 7), `compile_gate_readiness_projection`
(Phase 8), and the orchestrating `compile_gap`.

## CLI Usage (diagnostic / direct invocation only)

```bash
python tools/supervisor/capability_compiler.py \
    --gap-record '{"format_id": "FODP", "function_name": "fodp_slide_notes", ...}' \
    --output-dir .local/evidences/<run_id>/taskcards/generated/
```

## Automatic Pipeline Usage (the normal path)

```bash
python tools/supervisor/capability_queue_consumer.py --max-gaps 5 \
    --output-dir .local/capability-consumer/taskcards
```

This selects FOSS-eligible gaps from the gap ledger, calls the compiler for each,
and writes one `{taskcard_id}.json` per gap plus `consumer-summary.json` to the
output directory. `tools/supervisor/autonomous_task_generator.py` reads this output
directory (see `_load_compiled_taskcards()`, added TC-EXT-009-05) and folds compiled
candidates into its candidate list.

## Known Naming Collision (do not confuse)

`tools/capability_layer/capability_compiler.py` is a **different, unrelated tool**
(Layer L03 — SAL/obligation-driven capability derivation for `sal-driven-capability-map.json`,
invoked separately from `autonomous_cycle.py`'s TC-CL-003-05 step). It shares a filename
with this Layer L14 compiler by historical accident, not by design. See
`plans/layers/decision-register.yaml` (TC-EXT-009-04) for the full disposition of all
overlapping/duplicate compiler-family files.

## Allowed Paths

- `tools/supervisor/capability_compiler.py` (read; registration only, no logic change)
- `.local/evidences/<run_id>/taskcards/generated/` (write, diagnostic runs)
- `.local/capability-consumer/taskcards/` (write, via `capability_queue_consumer.py`)

## Forbidden Paths

- `tools/capability_layer/capability_compiler.py` — distinct L03 tool, not in scope
- Deep Lane-3 batch-compilation / Phase-4 concept-graph logic — out of scope, follow-on only

## Idempotency Contract

`verify_idempotency()` in `capability_compiler.py` runs compilation twice for the same
gap record and asserts the feature IR and taskcard outputs are byte-identical
(deterministic IDs via `_deterministic_id()`, no timestamps in compiled content).

## Stop Conditions

- Stop if `--gap-record` is not valid JSON
- Stop if the output directory cannot be created/written

## Output Format

- `feature-ir.json`, `taskcard.json`, `sal-validation.json`, `feature-graph.json`,
  `test-obligation-matrix.json`, `evidence-obligation-matrix.json`,
  `gate-readiness-projection.json` per compiled gap
- Exit 0 on success; exit 1 if `--verify-idempotency` detects non-determinism
