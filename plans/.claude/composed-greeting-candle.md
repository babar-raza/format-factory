# Plan: SAL & Capability Pipeline Reconnection — Production-Grade Redesign
**Plan ID:** composed-greeting-candle
**Mission:** SAL-CAP-RECONNECT-001
**Type:** multi_sprint_infrastructure
**Revised:** deeper pass — based on actual source code reading

---

## Actual System State (verified by reading source)

This plan replaces the prior surface-level version. All findings below are from
reading the actual code, not exploration-agent summaries.

### Two Parallel Pipelines (one live, one dead)

**Pipeline A — Live execution path (21 consumers):**
```
sal_master_runner.py + patch_sal_facts.py
    → .local/sal-output/sal-facts-latest.json   [RESULTS-ARRAY schema]
    → capability_map_generator.py               [enriches from poc-targets.yaml + adds spec_refs]
    → reports/capability-layer/gap-ledger.json  [1,479 gaps]
    → capability_feature_compiler.py
    → next-work-items.json
    → autonomous_cycle.py                       [ACTUAL SPRINT EXECUTION]
```

**Pipeline B — Dead research path (6 consumers, not in execution loop):**
```
ingest-spec-sal + per-format extractors
    → .local/spec-cache/sal-facts-{format}.json  [DIFFERENT schema, no sync to sal-output]
    → tools/capability_layer/capability_compiler.py  [reads spec-cache ONLY]
    → sal-driven-capability-map.json             [169 caps]
    → NOWHERE — not consumed by capability_feature_compiler.py
```

The goal of "SAL-backed capability derivation" already exists in Pipeline B.
The problem is Pipeline B never reaches the execution loop.

---

## Root Causes (distinct from symptoms)

### RC-1: Dual SAL stores with different schemas and no sync

- **`.local/sal-output/sal-facts-latest.json`** — structure: `{results: [{format_id, spec_facts: [...]}]}`
  - Written by `sal_master_runner.py`, patched by `patch_sal_facts.py`
  - 21 tools depend on this path
  - Used as spec_refs enrichment source by `capability_map_generator.py`

- **`.local/spec-cache/sal-facts-{format}.json`** — per-format flat files with at least 2 different schemas:
  - ABW: `{id, qname (=actual XML QName like "abw:abiword"), local_name, namespace_uri, element_type}` — no `fact_status`, no `claim`
  - CSV/FODS: `{qname ("FACT-CSV-001"), claim, section, description, authority, fact_status}`
  - Read ONLY by `tools/capability_layer/capability_compiler.py`
  - patch_sal_facts.py writes to sal-output NOT spec-cache — patches are invisible to capability_compiler

- **The two stores are never synchronized.** A fact added by patch_sal_facts.py to sal-output
  never reaches spec-cache. A fact extracted by ingest-spec-sal to spec-cache never reaches sal-output
  unless an explicit merge step runs.

### RC-2: SAL-driven compiler is a dead code path

`tools/capability_layer/capability_compiler.py` produces `sal-driven-capability-map.json` (169 caps).
`capability_feature_compiler.py` (the execution loop) reads `gap-ledger.json` — it never reads
`sal-driven-capability-map.json`. There is no code path connecting the SAL-driven output to sprint work selection.

The 169-cap SAL-driven map is consumed only by its own tests and `capability_pipeline.py` (which is
also not in the execution loop). It is research infrastructure with no operational effect.

### RC-3: State determination produces universally optimistic results

In `tools/capability_layer/capability_compiler.py`, `_evaluate_state()`:

**Bug 1 — False evidence fallback (line 243-245):**
```python
if not op_fns and fns:
    op_fns = fns[:3]  # ANY 3 functions credited as implementation evidence
```
This means every format with any Python source gets `implementation_verified` for every operation,
regardless of whether those functions implement the operation.

**Bug 2 — Format-name test detection (lines 260-268):**
A test file is credited for an operation if it contains `op_kind.split("_")[0]` **OR** `fmt` (the format
name). Since every test file for format `abw` contains the string "abw", every operation for ABW that
has any matching SAL facts shows `test_verified`.

**Confirmed impact:** ABW "style" capability shows `test_verified` because `test_abw_append_truncate_pipeline.py`
contains "abw". ABW has no style implementation. FODS shows all 15 ops as `test_verified`.
168/169 capabilities in `sal-driven-capability-map.json` are `test_verified` — this is not the real
production state of 20 formats.

### RC-4: poc-targets enrichment is confused with SAL authority

`capability_map_generator.py` reads `sal-output/sal-facts-latest.json` and populates `spec_refs[]` on
each generated capability. This looks like SAL backing but is post-hoc enrichment:
1. Capability is derived from poc-targets.yaml prose
2. Spec refs are added by keyword lookup in sal-output
3. The spec refs justify a capability that already existed independent of them

The resulting gap records show `spec_facts: [FACT-FODS-001, ...]` which looks like authority but is
linkage from the output side. The capability was not DERIVED from those facts.

### RC-5: spec-change invalidation does not exist

`capability_compiler.py` has content-normalized write (strips `generated_at` before comparing hashes).
But there is no mechanism to detect when upstream SAL facts changed and re-derive capabilities.
If a fact is corrected in sal-output, nothing forces a recompile of dependent capabilities.

### RC-6: Two `capability_compiler.py` files with different authorities

- `tools/capability_layer/capability_compiler.py` — reads spec-cache, SAL-primary, dead path
- `tools/supervisor/capability_compiler.py` — reads sal-output, generates taskcards from gap records

These have different purposes, different inputs, and different outputs. They are not in conflict but
the naming is a source of confusion and the wrong one is alive in the execution loop.

---

## What Is Working Correctly (do not touch)

These are verified correct and must not be broken:

- **sal-output as canonical data store** — 21 consumers depend on it; it is the correct hub
- **gap-ledger.json gap scoring and deduplication** — `capability_feature_compiler.py` scoring logic is sound
- **Oracle layer** — 73/73 PASS across 20 formats; this is real evidence, not synthetic
- **Governance validators** — 85 validators, 138 tests; the validation framework works
- **Per-format spec-cache files for FOSS formats** — CSV (55 facts, RFC-derived), FODS (4,988 facts) are real
- **`autonomous_cycle.py` execution loop** — do not change the execution interface
- **Content-normalized write in capability_compiler.py** — prevents SHA churn; keep this

---

## Production-Grade Solution

Four independent repairs, ordered by dependency and risk. Each has a test and a regression control.

### Repair 1: Fix State Determination in SAL-Driven Compiler
**File:** `tools/capability_layer/capability_compiler.py`
**Risk:** Low — outputs only `sal-driven-capability-map.json`, which is not in the execution loop

**Change 1a — Remove the false-evidence fallback:**
```python
# REMOVE lines 243-245:
#   if not op_fns and fns:
#       op_fns = fns[:3]
# REPLACE with: if no op-specific functions found, op_fns stays empty → state=missing
```

**Change 1b — Replace format-name test detection with function-name analysis:**
```python
# REPLACE lines 260-268 with:
op_test_files = []
for tf in test_files:
    try:
        tree = ast.parse(tf.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("test_"):
                    fn_lower = node.name.lower()
                    op_root = op_kind.split("_")[0]
                    kws = _OP_KEYWORDS.get(op_root, [])[:3]
                    if op_root in fn_lower or any(kw in fn_lower for kw in kws):
                        op_test_files.append(f"tests/python/{fmt}/{tf.name}")
                        break
    except SyntaxError:
        pass
test_refs = op_test_files[:3]
```

**Validation:**
- Run `python tools/capability_layer/capability_compiler.py --verbose`
- Expect: state_breakdown has `missing` count > 0, `test_verified` count < 100
- Regression: `tests/capability_layer/test_capability_compiler.py` and `test_idempotency.py` must pass
- Expected result: ABW "style" drops from `test_verified` to `implementation_verified` or `missing`

---

### Repair 2: Add SAL Backing Requirement Gate to Gap Ledger
**Files:** `tools/capability_layer/capability_map_generator.py`,
`tools/supervisor/governance_validators_sal.py`
**Risk:** Medium — changes which gaps enter the execution loop

**The core reconnection:** Instead of connecting the dead Pipeline B to the execution loop (risky,
requires replacing 2,529 caps with 169), add a gate at the gap-ledger boundary that requires real
SAL fact backing.

**Change 2a — Gate in `capability_map_generator.py`:**
Add a constant at the top:
```python
_SAL_BACKING_REQUIRED = True  # When True, gaps without spec_facts are excluded from gap-ledger
```

In the gap generation logic, after enriching with spec_refs, check:
```python
if _SAL_BACKING_REQUIRED and not gap.get("spec_facts"):
    gap["status"] = "SAL_UNGROUNDED"
    gap["notes"] = (gap.get("notes", "") +
                    " EXCLUDED: no SAL fact backing; derive capability from spec first.")
```

This preserves ALL existing gaps in the ledger (no deletions) but marks SAL_UNGROUNDED ones
so `capability_feature_compiler.py` filters them out.

**Change 2b — Update `capability_feature_compiler.py` `_SKIP_STATUSES`:**
```python
_SKIP_STATUSES = {
    "closed", "CLOSED",
    "DEFERRED_BY_DESIGN", "DEFERRED",
    "test_verified", "implementation_verified",
    "SAL_UNGROUNDED",  # NEW: no SAL fact authority; exclude until facts exist
}
```

**Change 2c — Add governance validator `V-CAP-SAL-GATE-001`:**
In `tools/supervisor/governance_validators_sal.py`:
- Validator reads `next-work-items.json`
- Verifies every item has `spec_facts` count > 0
- Emits WARN (not FAIL) for items with empty spec_facts
- This provides ongoing monitoring without blocking

**Validation:**
- Run `python tools/capability_layer/capability_map_generator.py`
- Run `python tools/supervisor/capability_feature_compiler.py --dry-run`
- Count items with non-empty spec_facts in output
- Target: 0 work items with `spec_facts: []` in `next-work-items.json`
- Regression: total open work items may decrease; verify not below 10 (i.e., enough valid work remains)
- Regression: `tests/python/` suite must remain green

---

### Repair 3: Migrate patch_sal_facts.py to Write to spec-cache
**Files:** `tools/scripts/patch_sal_facts.py`, and target spec-cache files
**Risk:** Low — additive change; does not break sal-output consumers

**The disconnect:** `patch_sal_facts.py` writes FACT-* style facts to sal-output but never to spec-cache.
The capability_compiler reads from spec-cache. XPM has 0 facts in spec-cache despite having FACT-XPM-001/002
in patch_sal_facts.py. Same for ZPAQ (0 facts in spec-cache).

**Change 3a — Migrate patches to spec-cache per-format files:**
For each format in `patch_sal_facts.py` that has 0 facts in spec-cache (xpm, zpaq, and any others):
1. Read the fact records from patch_sal_facts.py
2. Write them to `.local/spec-cache/sal-facts-{format}.json` in the standard FACT-*-ID schema
   (matching the CSV/FODS schema: `{qname, claim, section, description, authority, fact_status: "verified", source}`)
3. Verify `_load_sal_facts_for_format("xpm")` returns > 0

For formats that ALREADY have facts in spec-cache (csv, abw, etc.): dedup and merge.
The FACT-* IDs in patch_sal_facts.py must not overwrite existing FACT-* IDs in spec-cache.

**Change 3b — ABW schema normalization:**
ABW's spec-cache file uses `{id, qname (=abw:abiword), local_name, namespace_uri}` — not standard.
Add a migration: read the 5 ABW facts, map them to standard schema, write back.
Example: `{qname: "abw:abiword", element_type: "root"}` → `{qname: "FACT-ABW-001", claim: "ABW root element is abw:abiword", section: "1.1", description: "...", authority: "awml-spec-1.0", fact_status: "verified"}`
The old `abw:abiword`-style qname can remain as an alias field if needed.

**Do NOT change sal-output** — leave all 21 sal-output consumers untouched.

**Validation:**
- `python -c "from tools.capability_layer.capability_compiler import _load_sal_facts_for_format; print(len(_load_sal_facts_for_format('xpm')))"`
- Expected: ≥ 2 (was 0)
- `python -c "from tools.capability_layer.capability_compiler import _load_sal_facts_for_format; f=_load_sal_facts_for_format('abw'); print(f[0].get('qname'), f[0].get('claim'))"`
- Expected: FACT-ABW-001 (not abw:abiword)
- Run `tools/capability_layer/capability_compiler.py --format xpm --format zpaq --verbose`
- Expect: capabilities generated for xpm and zpaq (currently 0)

---

### Repair 4: Spec-Change Invalidation Signal
**Files:** `tools/capability_layer/capability_compiler.py`,
`tools/capability_layer/capability_pipeline.py`
**Risk:** Low — additive metadata; no breaking changes

**Design:** Track per-format SAL fact hash in the output file. On re-run, detect changes.

**Change 4a — In `compile_all()`**, after loading per-format facts, compute:
```python
import hashlib
facts_hash = hashlib.sha256(
    json.dumps([f.get("qname") for f in facts], sort_keys=True).encode()
).hexdigest()[:16]
```
Store this in each capability record: `"sal_facts_hash": facts_hash`

**Change 4b — On subsequent runs**, in `compile_format_capabilities()`:
Load the existing output file if present, find capabilities for this format, compare their
`sal_facts_hash` to the current hash. If different: force recompile even if source hasn't changed.
Log: `[capability_compiler] {fmt}: SAL facts changed (hash {old} → {new}), recompiling`

**Change 4c — In `capability_pipeline.py` LOAD stage** (line ~50, `CapabilityPipeline._stage_load()`):
Add a pre-check: for each format, compare current spec-cache file mtime/hash against
the hash stored in the existing sal-driven-capability-map.json. Log stale formats.

**Validation:**
- Run compiler, capture sal_facts_hash for CSV
- Append one fact to `.local/spec-cache/sal-facts-csv.json`
- Re-run compiler, verify: "SAL facts changed" log appears for CSV, CSV recompiles
- Remove the added fact, re-run, verify: CSV recompiles again to restore prior state
- Third run: verify no recompile ("Content unchanged")

---

## Taskcards

| TC-ID | Repair | Description | Lane | Risk |
|-------|--------|-------------|------|------|
| TC-SCP-001 | 1 | Fix `_evaluate_state()` — remove false-evidence fallback and format-name test detection | 14 | Low |
| TC-SCP-002 | 1 | Validate: verify state_breakdown contains realistic missing/partial counts | 14 | Low |
| TC-SCP-003 | 2 | Add SAL_UNGROUNDED status + gate in capability_map_generator.py | 14 | Medium |
| TC-SCP-004 | 2 | Update `_SKIP_STATUSES` in capability_feature_compiler.py | 14 | Medium |
| TC-SCP-005 | 2 | Add V-CAP-SAL-GATE-001 governance validator | 14 | Low |
| TC-SCP-006 | 3 | Migrate XPM, ZPAQ (and any other 0-fact formats) from patch_sal_facts.py to spec-cache | 14 | Low |
| TC-SCP-007 | 3 | ABW schema normalization in spec-cache (QName-style → FACT-*-ID style) | 14 | Low |
| TC-SCP-008 | 4 | Add per-format sal_facts_hash to capability compiler output | 14 | Low |
| TC-SCP-009 | 4 | Add hash-comparison invalidation trigger in compile_format_capabilities() | 14 | Low |
| TC-SCP-010 | All | Run all 8 required pilots + completion gate | 15 | Low |

### Taskcard Status Table

| TC-ID | Title | Status |
|-------|-------|--------|
| TC-SCP-001 | Fix _evaluate_state() false positives | CLOSED |
| TC-SCP-002 | Validate realistic state breakdown | CLOSED |
| TC-SCP-003 | SAL_UNGROUNDED gate in gap-ledger | CLOSED |
| TC-SCP-004 | Skip SAL_UNGROUNDED in execution loop | CLOSED |
| TC-SCP-005 | V-CAP-SAL-GATE-001 governance validator | CLOSED |
| TC-SCP-006 | Migrate XPM/ZPAQ patches to spec-cache | CLOSED |
| TC-SCP-007 | ABW schema normalization | CLOSED |
| TC-SCP-008 | Per-format sal_facts_hash in output | CLOSED |
| TC-SCP-009 | Hash-comparison invalidation trigger | CLOSED |
| TC-SCP-010 | Pilots + completion gate | CLOSED |

### Taskcard Closure Summary (machine-readable)

| TC-ID | CLOSED |
|-------|--------|
| TC-SCP-001 | CLOSED |
| TC-SCP-002 | CLOSED |
| TC-SCP-003 | CLOSED |
| TC-SCP-004 | CLOSED |
| TC-SCP-005 | CLOSED |
| TC-SCP-006 | CLOSED |
| TC-SCP-007 | CLOSED |
| TC-SCP-008 | CLOSED |
| TC-SCP-009 | CLOSED |
| TC-SCP-010 | CLOSED |

---

## Key Files (all verified to exist)

### Primary targets (must change)
- [tools/capability_layer/capability_compiler.py](tools/capability_layer/capability_compiler.py) (616 LOC) — Repairs 1, 4
- [tools/capability_layer/capability_map_generator.py](tools/capability_layer/capability_map_generator.py) — Repair 2
- [tools/supervisor/capability_feature_compiler.py](tools/supervisor/capability_feature_compiler.py) (331 LOC) — Repair 2
- [tools/supervisor/governance_validators_sal.py](tools/supervisor/governance_validators_sal.py) (227 LOC) — Repair 2
- [tools/scripts/patch_sal_facts.py](tools/scripts/patch_sal_facts.py) (94 LOC) — Repair 3
- [.local/spec-cache/sal-facts-abw.json](.local/spec-cache/sal-facts-abw.json) — Repair 3 (schema migration)

### Secondary (read-only during repairs)
- [tools/capability_layer/capability_pipeline.py](tools/capability_layer/capability_pipeline.py) (15KB) — Repair 4 monitoring hook
- [.local/spec-cache/sal-facts-latest.json](.local/spec-cache/sal-facts-latest.json) — existence check path
- [.local/sal-output/sal-facts-latest.json](.local/sal-output/sal-facts-latest.json) — DO NOT CHANGE (21 consumers)
- [reports/capability-layer/gap-ledger.json](reports/capability-layer/gap-ledger.json) — DO NOT CHANGE SCHEMA
- [reports/capability-layer/sal-driven-capability-map.json](reports/capability-layer/sal-driven-capability-map.json) — output of Repair 1

### Test files (must stay green)
- [tests/capability_layer/test_capability_compiler.py](tests/capability_layer/test_capability_compiler.py)
- [tests/capability_layer/test_idempotency.py](tests/capability_layer/test_idempotency.py)
- All `.venv/Scripts/pytest tests/` tests (must stay at current pass count)

---

## What Is NOT in Scope (and why)

**Connecting Pipeline B directly to the execution loop** — would require replacing 2,529 poc-targets-derived
capabilities with 169 SAL-derived capabilities. 93% reduction in work queue is not a reconnection; it's
a replacement. The correct approach (Repair 2) gates on SAL backing, preserving scope while enforcing provenance.

**Replacing sal-output with spec-cache as canonical** — 21 consumers depend on sal-output schema. Changing
the canonical store is high-blast-radius work with no current justification. Repair 3 adds spec-cache
coverage for formats that are missing it, without touching sal-output.

**Rewriting capability_map_generator.py from scratch** — it works correctly for poc-targets-derived
capabilities. The only needed change is the SAL_UNGROUNDED gate (Repair 2).

**Eliminating patch_sal_facts.py** — it serves a real function (adding facts for formats without real
spec extractors). Repair 3 only migrates its output to spec-cache; it does not eliminate it.

---

## Tradeoffs and Risks

**Risk 1: Repair 2 may reduce the open work item queue significantly**
Some open gaps may have `spec_facts: []` if their capability was not enriched with sal-output references.
Run `capability_map_generator.py` in a dry-run mode first and count SAL_UNGROUNDED items before applying.
If > 50% of open gaps become SAL_UNGROUNDED, pause and audit why — it may indicate a broken enrichment step.

**Risk 2: Repair 1 (AST test detection) is slower than content search**
For formats with 50+ test files: ~250-500ms additional compile time per format.
For 20 formats: adds ~5-10 seconds to a full compile. Acceptable for a batch operation.
Not acceptable if called in tight loops — add a `--fast` flag that skips AST analysis.

**Risk 3: ABW schema migration (Repair 3) may break ABW-specific downstream consumers**
Any tool that reads spec-cache/sal-facts-abw.json and expects `{local_name, namespace_uri}` fields
would break. Before migrating: grep for `local_name` or `namespace_uri` in tools/. If found, add
alias fields to the migrated schema rather than removing old fields.

**Risk 4: Repair 3's xpm/zpaq migration may create facts the capability compiler then uses to generate capabilities**
This is intentional — xpm and zpaq should get capabilities if they have facts. But verify that the
oracle (which says OBLIGATION_CREATED for xpm, zpaq) aligns with having capabilities before proceeding.
A capability without an oracle case is not a pipeline problem — it's expected for unimplemented formats.

**Confidence levels:**
- RC-1 (dual stores): HIGH — verified by reading both paths and listing actual file content
- RC-2 (dead code path): HIGH — verified by tracing imports; no tool calls sal-driven-capability-map
- RC-3 (state detection): HIGH — confirmed by running _evaluate_state() live; ABW "style" = test_verified
- RC-4 (enrichment vs authority): HIGH — verified in capability_map_generator.py source
- RC-5 (no invalidation): HIGH — confirmed; no hash tracking exists
- RC-6 (two compilers): HIGH — both files confirmed at different paths reading different stores

---

## Completion Gate (from objective, mapped to repairs)

| Counter | Repair | Verification |
|---------|--------|--------------|
| UNINVENTORIED_PIPELINE_DISCONNECTIONS = 0 | Plan (this document) | 6 disconnections documented above |
| PIPELINE_GAPS_WITHOUT_PROVEN_ROOT_CAUSE = 0 | Plan (this document) | 6 root causes with code citations |
| MANUALLY_SEEDED_FACTS_USED_AS_CANONICAL_INPUT = 0 | Repair 3 | xpm/zpaq in spec-cache; patch_sal_facts.py still exists but facts duplicated to spec-cache |
| CAPABILITIES_WITHOUT_SAL_FACT_AUTHORITY = 0 | Repair 2 | All next-work-items have spec_facts > 0 |
| CAPABILITIES_WITHOUT_QNAME_OR_DOMAIN_OWNER = 0 | Already 99.4% — keep |
| CAPABILITIES_WITHOUT_IMPLEMENTATION_COMPILATION = 0 | Repair 2 | SAL_UNGROUNDED caps have taskcards to get SAL facts first |
| FORMATS_NOT_BACKFILLED_OR_TASKED = 0 | Repair 3 + TC-SCP-010 | All 25 formats either have spec-cache facts or DEFERRED_BY_DESIGN |
| FAILED_REQUIRED_PILOTS = 0 | TC-SCP-010 | Run all 8 pilots from objective |
| MATERIAL_SECOND_RUN_CHANGES = 0 | Repair 4 | Hash-stable rerun of compiler; same spec_facts = same output |

---

## Regression Controls (non-negotiable)

After every taskcard:
1. `.venv/Scripts/pytest tests/capability_layer/ -v` — must stay green
2. `.venv/Scripts/pytest tests/ -x -q` — full suite, no new failures
3. `python tools/supervisor/capability_feature_compiler.py --dry-run --gap-ledger reports/capability-layer/gap-ledger.json` — must produce ≥ 10 items
4. `python tools/supervisor/governance_validators_sal.py` — no new FAILs

The open work item count in next-work-items.json is allowed to decrease (SAL_UNGROUNDED items removed).
It is not allowed to reach 0 — that would mean the execution loop has no work, which is a blocker.


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-04T12:30:33.566367+00:00"
  locked_by: "6ccb0fc24c11"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
