# Dual-Lane Structural Repair
# Plan: serialized-petting-crab
# mission_id: DUAL-LANE-VERIFICATION-001
# plan_type: machinery_hardening

---

## What the architecture actually is

The gap pipeline has three distinct stages:

```
Stage 1: GENERATION
  poc-targets.yaml + format-registry.yaml + SAL facts
  → tools/capability_layer/capability_map_generator.py (1721 lines)
  → reports/capability-layer/gap-ledger.json
     (committed to git; regenerated on every autonomous cycle;
      preserves closed/deferred/supplemental=True entries across regeneration;
      DROPS open entries not in the new generated set)

Stage 2: COMPILATION
  gap-ledger.json (filtered to open gaps only)
  → tools/supervisor/capability_feature_compiler.py
  → .local/supervisor/next-work-items.json
     (89 items currently; sorted ascending by priority score;
      lower score = higher priority = selected first by agent)

Stage 3: SELECTION
  next-work-items.json + reports/supervisor/next-sprint.md
  → agent reads both, selects by priority order in next-work-items.json
```

---

## Actual root causes (not symptoms)

### Root Cause 1 — DOM gaps do not exist in Stage 1 (P0, structural)

`capability_map_generator.py` derives gaps from specification capabilities defined in
`poc-targets.yaml`, `format-registry.yaml`, and SAL facts. It has no knowledge of
DOM maturity boundaries (D0→D1→D2→D3→D4→D5) or the product-deepening-ledger.yaml.

Result: DOM maturity boundary gaps (MISSING_TYPED_CHILD, MISSING_TRAVERSAL,
MISSING_MUTATION, MISSING_ROUNDTRIP) are never generated. They exist only in
`reports/dual-lane-verification/dom-gap-reconciliation.yaml` — a forensic report that
feeds nothing.

**The previous plan's fix was wrong.** Writing 21 gaps directly to gap-ledger.json
with `status: "open"` would survive exactly one cycle. On the next autonomous cycle,
`capability_map_generator.py` regenerates gap-ledger.json. Open entries not produced
by the generator are silently dropped. The migration would be wiped on first rerun.

The generator preserves entries with `supplemental=True` OR with a closed/deferred
status (lines 1464-1475 of capability_map_generator.py). Any DOM gaps written to the
file must use the `supplemental=True` flag to survive regeneration.

### Root Cause 2 — No tool writes DOM gaps into the pipeline (P0, structural)

There is no `dom_maturity_gap_generator.py`. There is no call site in autonomous_cycle.py
that would generate DOM gaps and add them to gap-ledger.json. The entire Lane B queue
is empty because the tool that would populate it has never been built.

This is not a configuration error or a bug in existing code. It is a missing component.
The dual-lane architecture was designed but the DOM gap generation pipeline was never
implemented. What was implemented:
- ✅ The DOM maturity scale (D0-D5)
- ✅ The product-deepening-ledger.yaml with ceiling and maturity fields
- ✅ The compiler's `_classify_deepening_lane()` and `_lane_balance_penalty()`
- ✅ The lane_selector.py starvation detector
- ❌ The tool that generates DOM maturity gaps and injects them into Stage 1

### Root Cause 3 — Two of three P1 findings are already fixed at HEAD (finding error)

The gleaming-napping-pebble.md plan's ITERATION_REQUIRED lock was written on 2026-06-28.
The fixes for FIND-V01-002 (no ceiling enforcement) and FIND-V01-003 (no replay detection)
were implemented in agile-rolling-marshmallow, which committed AFTER the lock was written.

At current HEAD, `autonomous_cycle_extensions/__init__.py` `update_lane_counters()` has:
- Ceiling guard: `if current >= ceiling: ... continue` (lines 234-238)
- Replay guard: `if sprint_id and entry.get("last_applied_sprint_id") == sprint_id: continue`
  (lines 222-223)

Both are present. lifecycle_audit.py was never re-run after these fixes, so the plan lock
was never promoted from ITERATION_REQUIRED to TERMINAL_CLOSED.

### Root Cause 4 — The starvation warning path is dead, but the scoring path is alive

Two separate starvation paths exist:

**Path A (dead):** `check_continuation.py` Check 10 → `lane_starvation_warnings` in JSON
output → `generate_next_worker_prompt.py` (does not read this field) → agent never sees it.
This path produces log output and a JSON field that nothing downstream consumes.

**Path B (alive but has nothing to boost):** `_lane_balance_penalty()` in the compiler →
reads ledger's `lane_a_consecutive`, `lane_b_consecutive` → applies +15 to items in the
dominant lane → priority scores in next-work-items.json change → agent selects by score.

Path B IS functional. The penalty direction is correct (ascending sort, so +15 increases
score number → later in queue → deprioritized). When `a_consecutive - b_consecutive >= 3`,
feature items get +15, DOM items stay at base score, DOM items appear earlier in the queue.

**Path B has nothing to operate on because Root Cause 1/2 mean zero DOM items exist.**

All 20 formats currently have `lane_b_consecutive = 0`. No DOM sprint has ever been
accepted. No starvation threshold has been crossed. Even if it had been crossed, the
penalty would correctly boost DOM items — but there are none to boost. The scoring
mechanism is correct but its input queue is empty.

### Root Cause 5 — Policy global default is never consumed (P3, minor)

`_load_policies()` in lane_selector.py reads Section 10 but is never called from
`check_starvation()` or `select_lane()`. Per-format `lane_starvation_threshold` from
the ledger is used correctly. The global default in policies.yaml (`default_starvation_threshold: 3`)
matches the hardcoded DEFAULT_STARVATION_THRESHOLD = 3. Observable behavior is identical.
This is a consistency risk, not an active defect.

### Root Cause 6 — classifier can misclassify DOM maturity gaps (P2, conditional)

`_classify_deepening_lane()` checks `gap_type in {"spec_parity_gap", "architecture_only",
"missing_qname_registration"}` and keywords in capability_name. DOM maturity gap types
("dom_maturity_d2", "dom_maturity_d3" etc.) are not in the whitelist. Without an explicit
`deepening_lane` field on the gap record, a DOM maturity gap might classify as "feature"
depending on its capability_name. This is a latent defect that activates the moment DOM
gaps are generated (Root Cause 2 fix).

---

## What breaks consistency across reruns

**The specific failure mode:**
Any DOM gap written to gap-ledger.json without `supplemental=True` is silently deleted
on the next autonomous cycle when `capability_map_generator.py` runs. The system resets
to zero DOM items on every regeneration. This would make even a working implementation
appear to break: the gaps exist after migration, work for one sprint, then vanish.

**The counter initialization problem:**
`lane_b_consecutive` starts at 0 and only increments when a DOM sprint is accepted.
No DOM sprint can be accepted if no DOM item exists. No DOM item exists if Root Cause 1
is not fixed. The counters are frozen at 0 across all reruns because the pipeline is
structurally blocked before counters can accumulate any state.

**The starvation threshold cannot be crossed:**
Starvation is detected when `a_consecutive - b_consecutive >= 3`. With b_consecutive
always 0 and a_consecutive starting from 0, the threshold requires a_consecutive >= 3.
That means after 3 consecutive feature sprints WITHOUT any DOM sprint, the starvation
penalty would apply. But feature sprints don't update a_consecutive either unless there's
a completed work item with `deepening_lane: "feature"` in the declaration. This depends
on whether the sprint declaration carries that field (depends on compile pipeline).
Even if it did, the threshold would eventually trip, but the penalty would boost DOM items
that still don't exist. The system is functionally deadlocked.

---

## What must be preserved

- `capability_map_generator.py` existing generation logic — do not touch existing code paths
- `product-deepening-ledger.yaml` structure and all per-format fields — authoritative state
- `update_lane_counters()` current implementation — already correct at HEAD
- `lane_selector.py` module — select_lane() and check_starvation() logic is correct
- The 84+ existing passing tests — regression baseline
- The `supplemental=True` preservation mechanism in the generator — this is the entry point
- The compiler's scoring path (Path B starvation) — correctly designed, just needs inputs

---

## Production-grade solution

### Design principle

The correct fix is not to migrate 21 gap records. It is to build the missing component
in Stage 1 that produces DOM maturity gaps as durable, supplemental entries in gap-ledger.json.

The generator must:
1. Read authoritative DOM state from product-deepening-ledger.yaml
2. Produce exactly one DOM gap per format: the IMMEDIATE NEXT maturity step
3. Tag each gap with `supplemental=True` so the generator preserves it across regeneration
4. Set `deepening_lane: "dom"` explicitly so the classifier always gets it right
5. Mark previously-emitted gaps as `status: closed` when the format's maturity has advanced
6. Be idempotent: stable gap_id means re-running produces no change

### Why one gap per format (not all future steps)

Emitting all steps from current to ceiling (e.g., D1→D2, D2→D3, D3→D4 for one format)
creates ordering risk: the compiler might select D3→D4 work for a format that is at D1.
Emitting only the IMMEDIATE NEXT step enforces the correct dependency chain without
needing a dependency system. When D1→D2 is completed and maturity advances to D2, the
next run emits D2→D3. The progression is naturally ordered.

### Gap record schema for DOM maturity gaps

```json
{
  "gap_id": "GAP-ABW-DOM-MATURITY-D2-001",
  "format": "ABW",
  "product_type": "foss",
  "capability_name": "dom_typed_child_model for abw",
  "current_state": "not_implemented",
  "gap_type": "dom_maturity_d2",
  "status": "open",
  "deepening_lane": "dom",
  "supplemental": true,
  "dom_maturity_boundary": "D2",
  "dom_maturity_current": "D1",
  "dom_maturity_ceiling": "D4",
  "blocks_poc": false,
  "blocks_readiness": true,
  "commercial_impact": "MEDIUM",
  "foss_impact": "HIGH",
  "priority": "P2",
  "owning_lane": 1,
  "suggested_taskcard": "",
  "suggested_verification": "python -m pytest tests/python/abw/ -v",
  "blockers": [],
  "spec_facts": [],
  "notes": "Auto-generated by dom_maturity_gap_generator. Advance ABW from D1 to D2."
}
```

**Stable ID scheme:** `GAP-{FORMAT_UPPER}-DOM-MATURITY-{BOUNDARY_UPPER}-001`
- Format: uppercase format name
- Boundary: the TARGET level (D2 means "achieve D2 from below")
- -001 suffix: always 001 (one gap per format-boundary combination)
- Collision-free with existing capability gaps (which use `GAP-{FORMAT}-{PRODUCT_TYPE}-{CAP}-{N}`)

**Automatic closure logic:** When `lane_b_maturity >= "D2"` for ABW, the generator marks
`GAP-ABW-DOM-MATURITY-D2-001` as `status: closed` and emits `GAP-ABW-DOM-MATURITY-D3-001`
as the new active gap. The generator reads existing supplemental DOM gaps from gap-ledger.json,
closes the ones whose boundary has been passed, and emits the new ones. All supplemental
gaps (open and closed) survive regeneration by capability_map_generator.py.

### Priority scheme

DOM maturity gaps are universally P2 (medium priority). This puts them in competition with
feature gaps. The lane balance penalty then determines which gets selected when starvation
applies. This avoids hard-coding DOM as always-urgent, which would be wrong — a P0 feature
defect should still outrank a P2 DOM gap.

Exception: if the format is at D0 (no meaningful model at all), consider P1 because D0 is
architecturally blocking. Document this choice explicitly as a constant in the generator.

---

## Taskcards

### TC-VPR-001 | Ground-Truth Audit
**Status:** OPEN
**Goal:** Confirm all root causes at HEAD before touching code. No changes.

**Steps:**

1. Confirm `capability_map_generator.py` does not read product-deepening-ledger.yaml:
   ```
   grep -n "product-deepening\|lane_b_maturity\|dom_maturity" \
     tools/capability_layer/capability_map_generator.py
   ```
   Expected: 0 matches. Confirms Root Cause 1.

2. Confirm `supplemental=True` mechanism exists in capability_map_generator.py:
   Read lines 1440-1477. Verify the preservation logic for `supplemental=True` entries.
   Document exact line numbers. This is the integration point for the new tool.

3. Confirm DOM items are absent from gap-ledger.json and next-work-items.json:
   ```
   python -c "
   import json
   gl = json.load(open('reports/capability-layer/gap-ledger.json'))
   dom = [g for g in gl.get('gaps',[]) if 'dom_maturity' in g.get('gap_type','')
          or g.get('deepening_lane')=='dom' or g.get('supplemental')]
   print('DOM/supplemental gaps in ledger:', len(dom))
   nwi = json.load(open('.local/supervisor/next-work-items.json'))
   items = nwi if isinstance(nwi, list) else nwi.get('items', [])
   dom_items = [i for i in items if i.get('deepening_lane')=='dom']
   print('DOM items in next-work-items:', len(dom_items))
   "
   ```
   Expected: both 0. Confirms Root Cause 2.

4. Confirm ceiling and replay guards are present at HEAD:
   ```
   grep -n "last_applied_sprint_id\|current >= ceiling" \
     tools/supervisor/autonomous_cycle_extensions/__init__.py
   ```
   Expected: both present. Confirms two P1 findings already fixed.

5. Confirm `_load_policies()` is defined but never called:
   ```
   grep -n "_load_policies\|load_policies" tools/supervisor/lane_selector.py
   ```
   Expect: definition found; check_starvation() and select_lane() do NOT call it.

6. Read all `lane_b_consecutive` values from the ledger:
   ```
   python -c "
   import yaml
   d = yaml.safe_load(open('registry/product-deepening-ledger.yaml').read())
   for e in d: print(e.get('format'), 'b_consec:', e.get('lane_b_consecutive',0))
   "
   ```
   Expected: all 0. Confirms no DOM sprint has ever been accepted.

7. Read autonomous_cycle.py around lines 185-195 and 1573-1591 to understand where
   capability_map_generator.py is called and where compile_gaps() is called.
   Document the exact call sequence for wiring the new tool.

8. Write `reports/dual-lane-verification/ground-truth-audit.yaml`:
   ```yaml
   head_revision: <git rev-parse HEAD>
   audit_date: <today>
   root_causes:
     rc1_dom_gaps_not_generated: CONFIRMED  # generator has no DOM logic
     rc2_no_dom_gap_generator_tool: CONFIRMED  # tool doesn't exist
     rc3_p1_findings_already_fixed_at_head: CONFIRMED  # two of three fixed
     rc4_starvation_warning_path_dead: CONFIRMED  # but scoring path alive
     rc5_policy_global_default_unconsumed: CONFIRMED  # minor
     rc6_classifier_missing_dom_types: CONFIRMED  # latent until RC2 fixed
   dom_gaps_in_gap_ledger: 0
   dom_gaps_in_next_work_items: 0
   lane_b_consecutive_all_formats: 0
   supplemental_preservation_mechanism_confirmed: true
   supplemental_preservation_lines: [<line numbers>]
   autonomous_cycle_generator_callsite: <line numbers>
   autonomous_cycle_compiler_callsite: <line numbers>
   ```

**Acceptance:** ground-truth-audit.yaml written. No code changes.

---

### TC-VPR-002 | Build dom_maturity_gap_generator.py
**Status:** OPEN
**Depends on:** TC-VPR-001
**Goal:** Create the missing pipeline component that generates DOM maturity gaps
as durable supplemental entries in gap-ledger.json.

**File:** `tools/supervisor/dom_maturity_gap_generator.py`

**Interface:**
```python
def generate_dom_gaps(
    ledger_path: Path,          # registry/product-deepening-ledger.yaml
    applicability_path: Path,   # reports/dual-lane-deepening/format-dom-applicability.yaml
    gap_ledger_path: Path,      # reports/capability-layer/gap-ledger.json
    dry_run: bool = False,
) -> GenerationResult:
    """Generate or refresh DOM maturity gaps in gap-ledger.json.

    For each format with dom_applicability in (FULL, PARTIAL):
      - Reads current lane_b_maturity and lane_b_ceiling from ledger
      - If current < ceiling: writes/refreshes gap for the IMMEDIATE NEXT boundary
      - If boundary already passed (maturity >= boundary): marks gap as 'closed'
      - Uses supplemental=True so capability_map_generator.py preserves it

    Returns: GenerationResult(added, updated, closed, unchanged, errors)
    Is idempotent: running twice produces identical results.
    """
```

**Core logic:**

```python
DOM_BOUNDARY_TYPES = {
    "D2": "dom_maturity_d2",  # achieve D2: typed children + parser mapping
    "D3": "dom_maturity_d3",  # achieve D3: traversal + navigation + query
    "D4": "dom_maturity_d4",  # achieve D4: mutation + writer integration
    "D5": "dom_maturity_d5",  # achieve D5: roundtrip + package + consumer proof
}

DOM_BOUNDARY_CAPABILITY_NAMES = {
    "D2": "dom_typed_children for {fmt}",
    "D3": "dom_traversal for {fmt}",
    "D4": "dom_mutation for {fmt}",
    "D5": "dom_roundtrip for {fmt}",
}

MATURITY_ORDER = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5}

# Priority by boundary: earlier boundaries are more urgent
BOUNDARY_PRIORITY = {"D2": "P1", "D3": "P2", "D4": "P2", "D5": "P3"}


def _next_boundary(current: str, ceiling: str) -> str | None:
    """Return the immediate next maturity level above current, if below ceiling."""
    levels = ["D0", "D1", "D2", "D3", "D4", "D5"]
    ci = levels.index(current)
    cei = levels.index(ceiling)
    next_i = ci + 1
    return levels[next_i] if next_i <= cei else None


def _make_gap_id(format_name: str, boundary: str) -> str:
    return f"GAP-{format_name.upper()}-DOM-MATURITY-{boundary.upper()}-001"


def _make_gap_record(format_name: str, boundary: str, current: str, ceiling: str,
                     product_type: str = "foss") -> dict:
    gap_id = _make_gap_id(format_name, boundary)
    fmt_lower = format_name.lower()
    cap_name = DOM_BOUNDARY_CAPABILITY_NAMES[boundary].format(fmt=fmt_lower)
    return {
        "gap_id": gap_id,
        "format": format_name.upper(),
        "product_type": product_type,
        "capability_name": cap_name,
        "current_state": "not_implemented",
        "gap_type": DOM_BOUNDARY_TYPES[boundary],
        "status": "open",
        "deepening_lane": "dom",
        "supplemental": True,
        "dom_maturity_boundary": boundary,
        "dom_maturity_current": current,
        "dom_maturity_ceiling": ceiling,
        "blocks_poc": False,
        "blocks_readiness": True,
        "commercial_impact": "MEDIUM",
        "foss_impact": "HIGH",
        "priority": BOUNDARY_PRIORITY[boundary],
        "owning_lane": 1,
        "suggested_taskcard": "",
        "suggested_verification": f"python -m pytest tests/python/{fmt_lower}/ -v",
        "blockers": [],
        "spec_facts": [],
        "notes": (f"Auto-generated by dom_maturity_gap_generator. "
                  f"Advance {format_name.upper()} from {current} to {boundary}."),
    }
```

**Gap-ledger update logic:**
1. Read gap-ledger.json. Load `gaps` list.
2. Build index of existing supplemental DOM gaps: `{gap_id: gap_record}`.
3. For each applicable format:
   a. Compute `next_boundary = _next_boundary(current, ceiling)`
   b. If `next_boundary is None`: format is at ceiling, skip.
   c. Target gap_id = `_make_gap_id(format, next_boundary)`
   d. If gap_id EXISTS in ledger and status="open": unchanged (idempotent).
   e. If gap_id EXISTS and status="closed": re-open ONLY if current < next_boundary.
      (This shouldn't happen normally — closed means maturity advanced past it.)
   f. If gap_id NOT IN ledger: create new record (added).
   g. For ALL other DOM gaps for this format (other boundaries):
      - If their boundary <= current: mark `status: closed`, `closed_at: now`,
        `closed_by_engine: True`, `closure_evidence: "maturity advanced"`
      - If their boundary > next_boundary: leave unchanged (not yet reached)
4. Write updated gap-ledger.json atomically (read-modify-write with file lock if available).

**Tests:** `tests/supervisor/test_dom_maturity_gap_generator.py`
```python
def test_generates_one_gap_per_format_at_immediate_next_boundary():
    # ABW at D1, ceiling D4 → emits GAP-ABW-DOM-MATURITY-D2-001
def test_supplemental_true_on_all_generated_gaps():
    # All generated gaps have supplemental=True
def test_deepening_lane_dom_on_all_generated_gaps():
    # All generated gaps have deepening_lane="dom"
def test_idempotent_rerun_produces_no_changes():
    # Run twice, second run returns (added=0, updated=0, closed=0, unchanged=N)
def test_maturity_advancement_closes_old_gap_and_emits_next():
    # ABW at D1 → emit D2 gap; advance to D2 → D2 gap closed, D3 gap emitted
def test_format_at_ceiling_emits_no_gap():
    # FODS at D5 (ceiling) → no gap emitted
def test_format_non_applicable_emits_no_gap():
    # CSV (FLAT) → no gap emitted
def test_does_not_modify_non_supplemental_existing_gaps():
    # The 1495 existing capability gaps are untouched
def test_gap_id_stable_across_reruns():
    # Same format+boundary always produces same gap_id
```

**Dry-run output format:**
```
DOM Gap Generation (dry-run):
  ABW: D1 → D2 (gap_id=GAP-ABW-DOM-MATURITY-D2-001, status=NEW)
  FODG: D1 → D2 (gap_id=GAP-FODG-DOM-MATURITY-D2-001, status=NEW)
  ...
  FODS: D3 → D4 (gap_id=GAP-FODS-DOM-MATURITY-D4-001, status=NEW)
Total: 8 new, 0 updated, 0 closed, 0 unchanged
```

**Acceptance:** Tool created. 8 tests passing. Dry-run shows 8 gaps to generate.
Real run adds 8 gaps. Immediate rerun shows 0 changes. Idempotency verified.

---

### TC-VPR-003 | Wire Generator into Autonomous Cycle
**Status:** OPEN
**Depends on:** TC-VPR-002
**Goal:** Call dom_maturity_gap_generator.py at the right point in autonomous_cycle.py
so DOM gaps are always current before the compiler runs.

**Correct call site:**
From TC-VPR-001 ground-truth audit: capability_map_generator.py is called around line 185-195.
compile_gaps() is called around lines 1573-1591. The DOM gap generator must run BETWEEN these:
after capability_map_generator.py regenerates gap-ledger.json (which resets open non-supplemental
gaps), but before compile_gaps() reads gap-ledger.json. This ensures:
1. Generator runs → gap-ledger.json regenerated (non-supplemental open gaps refreshed)
2. DOM generator runs → DOM gaps written/refreshed as supplemental entries
3. Compiler runs → reads gap-ledger.json with BOTH capability gaps AND DOM gaps

**Implementation in autonomous_cycle.py** (add ~10 lines near line 1565):
```python
# Generate/refresh DOM maturity gaps before compilation
try:
    from dom_maturity_gap_generator import generate_dom_gaps as _gen_dom
    _dom_result = _gen_dom(
        ledger_path=repo_root / "registry" / "product-deepening-ledger.yaml",
        applicability_path=repo_root / "reports" / "dual-lane-deepening" / "format-dom-applicability.yaml",
        gap_ledger_path=repo_root / "reports" / "capability-layer" / "gap-ledger.json",
    )
    print(f"  DOM gaps: {_dom_result.added} added, {_dom_result.closed} closed, "
          f"{_dom_result.unchanged} unchanged")
except Exception as _dom_err:
    print(f"  WARNING: DOM gap generation failed (non-blocking): {_dom_err}")
    # Non-blocking per Supreme Directive
```

Pattern follows existing extension hooks in autonomous_cycle.py (try/import, non-blocking).

**Acceptance:** DOM gap generator is called in autonomous_cycle.py. When autonomous_cycle
is next run, 8 DOM gaps appear in gap-ledger.json and are preserved across the capability
map regeneration step.

---

### TC-VPR-004 | Classifier Hardening
**Status:** OPEN
**Depends on:** TC-VPR-003
**Goal:** Make `_classify_deepening_lane()` reliably classify DOM maturity gaps.
Currently the explicit `deepening_lane` field on gap records is not checked.
The capability_name "dom_traversal for abw" would match the keyword "dom_" — so the
existing classifier WOULD work for generated DOM gaps. But this is fragile.

**Defense-in-depth update:**

In `tools/supervisor/capability_feature_compiler.py`, `_classify_deepening_lane()`:

```python
def _classify_deepening_lane(gap: dict) -> str:
    # Tier 1: explicit field on record takes precedence
    explicit = gap.get("deepening_lane", "")
    if explicit in ("dom", "feature"):
        return explicit

    # Tier 2: known gap_type taxonomy (existing + DOM maturity types)
    DOM_TYPES = frozenset({
        "spec_parity_gap", "architecture_only", "missing_qname_registration",
        "dom_maturity_d2", "dom_maturity_d3", "dom_maturity_d4", "dom_maturity_d5",
    })
    if gap.get("gap_type", "") in DOM_TYPES:
        return "dom"

    # Tier 3: keyword heuristics (unchanged from existing)
    cap = gap.get("capability_name", "").lower()
    if any(kw in cap for kw in ("object_model", "dom_", "navigation", "mutation", "spec_class")):
        return "dom"

    return "feature"
```

**Tests** (add to existing compiler tests):
```python
def test_explicit_dom_field_bypasses_classifier():
    assert _classify_deepening_lane({"deepening_lane": "dom"}) == "dom"
def test_explicit_feature_field_bypasses_classifier():
    assert _classify_deepening_lane({"deepening_lane": "feature"}) == "feature"
def test_dom_maturity_d2_classifies_as_dom():
    assert _classify_deepening_lane({"gap_type": "dom_maturity_d2"}) == "dom"
def test_dom_maturity_d4_classifies_as_dom():
    assert _classify_deepening_lane({"gap_type": "dom_maturity_d4"}) == "dom"
def test_generated_dom_gap_classifies_correctly():
    # A record from dom_maturity_gap_generator → "dom"
    gap = {"gap_type": "dom_maturity_d2", "deepening_lane": "dom", "capability_name": "dom_typed_children for abw"}
    assert _classify_deepening_lane(gap) == "dom"
```

**Acceptance:** Tests pass. All generated DOM gaps classify as "dom".

---

### TC-VPR-005 | End-to-End Pipeline Verification
**Status:** OPEN
**Depends on:** TC-VPR-004
**Goal:** Prove the full pipeline works: generator → gap-ledger → compiler → next-work-items.

**Steps:**

1. Run DOM gap generator standalone:
   ```
   python tools/supervisor/dom_maturity_gap_generator.py \
     --ledger registry/product-deepening-ledger.yaml \
     --applicability reports/dual-lane-deepening/format-dom-applicability.yaml \
     --gap-ledger reports/capability-layer/gap-ledger.json
   ```

2. Verify DOM gaps in gap-ledger.json:
   ```
   python -c "
   import json
   gl = json.load(open('reports/capability-layer/gap-ledger.json'))
   dom = [g for g in gl.get('gaps',[]) if g.get('supplemental')]
   print('Supplemental DOM gaps:', len(dom))
   for g in dom: print(g['gap_id'], g['status'], g['deepening_lane'])
   "
   ```
   Expected: 8 supplemental DOM gaps, all status=open, all deepening_lane=dom.

3. Run the compiler:
   ```
   python -c "
   import sys; sys.path.insert(0, 'tools/supervisor')
   from capability_feature_compiler import compile_gaps
   import json
   gl = json.load(open('reports/capability-layer/gap-ledger.json'))
   items = compile_gaps(gl.get('gaps', []))
   dom = [i for i in items if i.get('deepening_lane') == 'dom']
   print('DOM items in compiled output:', len(dom))
   for i in dom[:3]: print(i['item_id'], i['priority'], i['deepening_lane'])
   "
   ```
   Expected: 8 DOM items in compiled output.

4. Simulate starvation to verify scoring path:
   Temporarily set `lane_a_consecutive=4, lane_b_consecutive=0` for one format (fods) in a copy
   of the ledger. Re-run compiler with that ledger. Verify:
   - FODS feature items have priority score += 15
   - FODS DOM item has base priority score (no penalty)
   - FODS DOM item appears BEFORE FODS feature items in sorted output

5. Simulate capability_map_generator.py regeneration to verify supplemental persistence:
   ```python
   # Read the generator's preservation logic, simulate it on a subset
   # Verify: DOM gaps tagged supplemental=True survive the regeneration step
   # Key lines: capability_map_generator.py lines 1464-1475
   ```
   Read the logic; write a targeted test if the line confirms `supplemental=True` is preserved.

6. Write integration test `tests/supervisor/test_dom_pipeline_integration.py`:
   ```python
   def test_pipeline_produces_dom_items_end_to_end():
       # Run generator → verify gaps in ledger → compile → verify dom items
   def test_dom_items_survive_simulated_regeneration():
       # Write supplemental DOM gap → simulate generator preservation → still present
   def test_starvation_boosts_dom_priority():
       # Starved state: DOM items rank above feature items
   def test_dom_at_ceiling_produces_no_gap():
       # Format at ceiling: no DOM gap generated, no DOM item compiled
   ```

**Acceptance:** 8 DOM items in compiler output. Starvation boost verified. Supplemental
persistence proven. 4 integration tests passing.

---

### TC-VPR-006 | Policy Consumer Activation (minor)
**Status:** OPEN
**Depends on:** TC-VPR-005
**Goal:** Wire `_load_policies()` into check_starvation() so policies.yaml Section 10
`default_starvation_threshold` becomes the actual global default (instead of a hardcoded
constant that happens to match it).

**Change in lane_selector.py `check_starvation()`:**
```python
def check_starvation(format_name, ledger_path=None, policies_path=None):
    ledger = _load_ledger(ledger_path)
    policies = _load_policies(policies_path)  # ADD: was defined, never called
    entry = _find_entry(ledger, format_name)
    ...
    global_threshold = policies.get("default_starvation_threshold", DEFAULT_STARVATION_THRESHOLD)
    threshold = entry.get("lane_starvation_threshold", global_threshold)
    ...
```

Same pattern in `_lane_balance_penalty()` in compiler — add a module-level policy cache
(read once, reuse) to avoid O(n) file reads inside the hot scoring loop.

**Tests:**
- `test_check_starvation_reads_policy_global_threshold()` — mock policies.yaml, verify used
- `test_per_format_threshold_overrides_global()` — per-format takes precedence
- `test_policy_file_absent_falls_back_gracefully()` — no error, uses DEFAULT_STARVATION_THRESHOLD

**Acceptance:** 3 tests passing. No observable behavior change on current config (values match).
But policies.yaml Section 10 is no longer dead configuration.

---

### TC-VPR-007 | Full Regression Suite
**Status:** OPEN
**Depends on:** TC-VPR-006
**Goal:** Confirm no regressions from all changes in TC-VPR-002 through TC-VPR-006.

**Steps:**

1. Run full supervisor tests:
   ```
   .venv/Scripts/pytest tests/supervisor/ -v --tb=short 2>&1 | tail -60
   ```

2. If any test expects "0 DOM items in next-work-items.json" or snapshots the total item
   count: these are now CORRECT to update. Document each update as an intentional change,
   not a regression fix.

3. Run governance validators:
   ```
   python tools/supervisor/governance_validator_runner.py 2>&1 | tail -20
   ```
   Expected: 165 validators pass. New files (dom_maturity_gap_generator.py) must not
   trigger new architecture violations — it's in tools/supervisor/, not src/python/.

4. Run the full test suite to catch any LOC cap violations (new test files):
   ```
   .venv/Scripts/pytest tests/ -v --tb=short -q 2>&1 | tail -30
   ```

**Acceptance:** All pre-existing tests pass (or are intentionally updated). 165 validators pass.
New tests from TC-VPR-002/004/005/006 all pass.

---

### TC-VPR-008 | Lifecycle Audit and Plan Closure
**Status:** OPEN
**Depends on:** TC-VPR-007
**Goal:** Run the authoritative lifecycle audit and close gleaming-napping-pebble.md.

**Steps:**

1. Run lifecycle audit:
   ```
   python tools/supervisor/lifecycle_audit.py \
     --mission-id DUAL-LANE-DEEPENING-001 \
     --sprint-id TC-VPR-CLOSURE
   ```

2. Read `.local/supervisor/lifecycle-audit-results.json`.

3. If status is TERMINAL_CLOSED:
   ```
   python tools/supervisor/write_plan_lock.py \
     --plan-path plans/.claude/gleaming-napping-pebble.md \
     --terminal --audit-gate
   ```

4. If status is ITERATION_REQUIRED: read the unresolved items, add repair taskcards
   to this plan, execute them, then repeat from step 1. Do not manually update the
   embedded lock.

5. Write verification summary to gleaming-napping-pebble.md embedded audit section:
   - FIND-V01-001 (dead policy config): REPAIRED in TC-VPR-006
   - FIND-V01-002 (no ceiling enforcement): ALREADY_FIXED in agile-rolling-marshmallow
   - FIND-V01-003 (no replay detection): ALREADY_FIXED in agile-rolling-marshmallow
   - ROOT_CAUSE_STRUCTURAL (DOM gaps not in pipeline): REPAIRED in TC-VPR-002/003/004
   - FIND-V03-001 (21 gaps missing from ledger): REPAIRED by generator (auto-generates from state)
   - FIND-V03-002 (3 maturity underclaims): ALREADY_REPAIRED in Phase 2

**Acceptance:** gleaming-napping-pebble.md lock is TERMINAL_CLOSED. This plan may be
closed with write_plan_lock.py --terminal.

---

## Tradeoffs, risks, and honest limits

**Risk 1: generator call order in autonomous_cycle.py**
The DOM gap generator MUST run after capability_map_generator.py (which might reset supplemental
gaps) but before compile_gaps() reads the ledger. Getting this wrong means either DOM gaps are
wiped before compilation (wrong order) or the generator's changes aren't included (too late).
Mitigation: TC-VPR-001 confirms exact line numbers before TC-VPR-003 writes the call.

**Risk 2: supplemental=True preservation is assumed, not verified**
The first agent reported that gaps with `supplemental=True` are preserved across regeneration
(lines 1464-1475 of capability_map_generator.py). This must be confirmed in TC-VPR-001
against the actual source. If the preservation mechanism works differently than described,
the design of TC-VPR-002 must change. Do not implement TC-VPR-003 until TC-VPR-001
confirms the exact preservation semantics.

**Risk 3: lifecycle_audit.py may find additional items**
The ITERATION_REQUIRED lock captured findings at 2026-06-28. Other issues may have emerged
or remain unaddressed. TC-VPR-008 may produce additional iteration tasks. Do not assume
the audit will be clean; follow ITERATION_REQUIRED → repair → re-audit until TERMINAL_CLOSED.

**Risk 4: one gap per format may under-specify the DOM work queue**
Emitting only the immediate next step gives only 8 active DOM items (one per FULL format).
If the compiler's scoring means these 8 items never rank above the 1,487 existing gaps, DOM
work still won't get selected. The priority assignment (P1 for D2, P2 for D3/D4, P3 for D5)
must put DOM items in a competitive range. Verify in TC-VPR-005 step 3 that DOM items
actually appear in the top 20 of compiled output when starvation applies.

**Risk 5: format-dom-applicability.yaml and product-deepening-ledger.yaml may disagree**
The generator reads both. If a format is FULL in applicability but has no lane_b_ceiling
in the ledger (or vice versa), the generator must handle the disagreement gracefully with a
warning, not a crash. Add explicit validation for this case in the generator.

**Dispatch observability — honest ceiling**
The 35-section protocol asks to prove the agent consumed a specific work item. This cannot be
mechanically proven in an LLM-based system. The correct approach is:
- DOM items exist in next-work-items.json with correct priority
- The agent selects by priority order from that file
- This is the strongest proof available without restructuring the entire agent execution model
A `lane_decision_log.jsonl` (recording what was dispatched pre-execution) would improve
observability but is out of scope for this plan. The existing compiler scoring path is sufficient
to establish behavioral intent; actual execution proof requires human review of sprint outputs.

**What this plan does NOT address**
- The dead starvation warning path (Check 10 → nobody reads it). Once DOM gaps exist and
  the compiler scoring path works, this advisory path's output becomes meaningful in logs.
  Fixing it to actually inject starvation context into next-sprint.md is a separate improvement.
- The dual-module structure (package + standalone autonomous_cycle_extensions). Fragile but
  working; do not touch.
- Full 35-section verification protocol output (report files, summary matrices, item-by-item
  CSV). These are artifacts of a working system. Generating them before the system works
  produces misleading documentation. Generate them after TC-VPR-005 confirms end-to-end.
