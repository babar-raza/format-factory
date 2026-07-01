# Capability Compiler File Relationship

## Two Compiler Files

The format-factory supervisor has two compiler files that serve different purposes:

### capability_compiler.py (521 LOC, tracked)

**Purpose:** Full-stack gap-to-feature compilation pipeline.

Takes a single gap entry from `gap-ledger.json` and compiles it through a multi-stage pipeline:
1. SAL fact validation (`validate_sal_input`)
2. Feature IR generation (`compile_gap_to_feature_ir`)
3. Feature graph construction (`compile_gap_to_feature_graph`)
4. QName ontology attachment (`attach_qname_ontology`)
5. Test obligation matrix (`compile_test_obligation_matrix`)
6. Evidence obligation matrix (`compile_evidence_obligation_matrix`)
7. Gate readiness projection (`compile_gate_readiness_projection`)
8. Taskcard generation (`compile_feature_ir_to_taskcard`)

**Primary API:** `compile_gap(gap: dict) -> dict` — compiles a single gap into a full feature IR + taskcard.

**Output:** Individual compilation artifacts written to `reports/capability-layer/compilations/`.

### capability_feature_compiler.py (280 LOC, untracked)

**Purpose:** Batch gap-to-work-item prioritizer for the autonomous cycle.

Takes a list of gaps and produces a prioritized list of work items for `next-work-items.json`:
1. Priority scoring (P0=0 through P8=80, with impact/blocker adjustments)
2. Lane classification (product, governance, documentation)
3. External gate detection
4. Work item formatting for the sprint executor

**Primary API:** `compile_gaps(gaps: list[dict], max_items: int = 20) -> tuple[list[dict], list[dict]]` — returns `(selected_items, deferred_items)`.

**Called from:** `autonomous_cycle.py` Step 4a (line ~1456).

## Why Both Exist

- `capability_compiler.py` is the **deep compiler** — it produces rich feature IRs with SAL facts, QName ontology, test/evidence obligations, and gate projections. Used for detailed per-gap analysis.
- `capability_feature_compiler.py` is the **batch prioritizer** — it takes many gaps and produces a ranked work item list for the next sprint. Used by the autonomous cycle to select work.

They are complementary, not duplicates. The feature compiler (`capability_feature_compiler.py`) handles the "what to work on next" question, while the capability compiler (`capability_compiler.py`) handles the "how to implement this gap" question.

## Authoritative for Autonomous Cycle

`capability_feature_compiler.py` is the authoritative compiler for the autonomous cycle's work selection (Step 4a). It is imported as:

```python
from capability_feature_compiler import compile_gaps as _compile_gaps
```

The capability compiler (`capability_compiler.py`) is used independently for detailed gap analysis but is not directly called during the autonomous cycle's work selection step.
