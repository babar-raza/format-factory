# Plan: Format Factory — External Plan Ingestion and Standardization
plan_id: stateful-booping-mountain
mission_id: FF-PLIS-001
status: READY_FOR_EXECUTION
plan_type: machinery_hardening
authority: per-chat-plan

---

## Part 1: Production Failure Analysis

Three distinct failure modes break consistency across reruns. Each has a different cause and a different fix.

---

### Failure Mode 1 — Session B's Step 0 overwrites execution state (CRITICAL)

**What happens:**

Session A imports `~/.claude/plans/X.md` → `plans/.claude/X.md`, writes a lock, executes 5 of 9 taskcards (changing their status in the plan file to CLOSED), then exhausts context.

Session B opens. CLAUDE.md Step 0 runs unconditionally (no "already imported" check exists — confirmed by codebase search returning zero matches). Step 0 runs `cp ~/.claude/plans/X.md plans/.claude/X.md`. This **overwrites the modified plan file** with the original content. All 5 CLOSED taskcards revert to OPEN.

`autonomous_cycle.py` Step 0b then reads the plan lock (which is still IN_PROGRESS from Session A — the cycle does NOT filter locks by session_id at startup, confirmed at lines 323-349). It treats the plan as active. But the plan file has been reset. Session B re-executes all 9 taskcards from scratch, duplicating work or producing conflicting results.

**This is not a hypothetical edge case. It is the exact sequence that runs when context is compacted and a new session starts with the same plan loaded.**

**Root cause:** `cp` is destructive on an already-modified target. Step 0 has no target-exists check.

---

### Failure Mode 2 — Partial taskcard parse allows silent premature closure

**What happens:**

A plan has 9 taskcards. 7 are in the 2-column `| TC-ID | STATUS |` table format. 2 were added post-import in block heading format (`### TC-X-008` + `Status: OPEN`).

`lifecycle_audit.parse_plan_taskcards()` uses all 3 regex patterns but the block pattern requires the Status: line to appear within 4 lines after the heading (`(?:[^\n]*\n){0,4}?`). If there's a description paragraph between the heading and Status:, this misses. The audit sees 7 tasks. 7 are CLOSED. `all_taskcards_closed = (0 == 0) and (7 > 0)` = True. Plan closes. 2 tasks never ran.

**Root cause:** No `expected_taskcard_count` baseline exists. The audit only knows what it finds at runtime, with no count to validate against.

---

### Failure Mode 3 — Mission ID conflicts are silent and undetected

**What happens:**

Two separate plan-mode sessions produce plans with the same `mission_id` (either deliberately similar scope or accidental collision). Both are imported. Both are locked as IN_PROGRESS. Both execute. Both attempt to close the same mission. The closure records conflict, the task queue double-counts, and the governance reports show mission FF-001 as both complete and in-progress.

**Root cause:** No registry indexed by `mission_id`. There is nowhere to check "is this mission already active?"

---

### What these three failures share

All three are caused by a single underlying property: **the import operation has no persistent state**. It writes a file and a lock but records nothing about what was imported, what content it had, or what mission it belongs to. Every session starts with zero knowledge of prior sessions' import decisions.

A registry that records `(source_hash → plan_path, mission_id, status)` fixes all three:

1. Source hash → detect existing import → SKIP `cp` if already registered → execution state preserved
2. Taskcard count at import time → `expected_taskcard_count` in plan_identity → audit comparison
3. Mission ID index → detect conflict before activating second plan

---

## Part 2: Structural Weaknesses in the Spec Requirements

The 20 required counters partition cleanly into three groups:

**Group A — Address real production risks (fix these):**
`DUPLICATE_PLAN_ITEM_IDS`, `COMPETING_AUTHORITATIVE_PLANS`, `PARTIALLY_REGISTERED_PLANS`, `DIRECT_UNSTANDARDIZED_PLAN_COPY_PATHS`, `MATERIAL_SECOND_RUN_CHANGES`, `LEGACY_IMPORTED_PLANS_NOT_RECONCILED`

**Group B — Satisfied structurally, not semantically (define scope precisely, then trivially satisfied):**
`SOURCE_PLAN_BLOCKS_NOT_CLASSIFIED = 0` — true if UNSTRUCTURED_PROSE is a valid classification
`SOURCE_PLAN_BLOCKS_SILENTLY_DROPPED = 0` — true if content is preserved verbatim and nothing is removed
`CANONICAL_PLAN_ITEMS_WITHOUT_SOURCE_TRACE = 0` — true if "canonical items" means plan_identity fields + TC-* entries (structural), not prose sentences
`SOURCE_REQUIREMENTS_NOT_PRESERVED = 0` — true if prose is not transformed (can't drop what you don't parse)

**Group C — Require upstream changes to plan-mode generation (not fixable at import time):**
`ACTIONABLE_PLAN_ITEMS_WITHOUT_TASKCARDS` — detecting "actionable prose without a TC-*" requires semantic understanding. The best this system can do is flag when `tc_count == 0`. Partial: yes. Complete: no.
`TASKCARDS_WITHOUT_LANE_OWNERSHIP` — plans don't have per-TC lane fields today. Addressable by adding `default_lane: UNRESOLVED` to plan_identity (all taskcards inherit it). This satisfies the counter technically while being honest that lane assignment is deferred.

The spec's semantic requirements (per-sentence traceability, requirement extraction from prose, 19-category classification) cannot be achieved with deterministic code and must be addressed at generation time through plan-mode prompt constraints. This plan does not attempt them.

---

## Part 3: What to Preserve vs Redesign

**Preserve without modification:**

| Component | Reason |
|---|---|
| `write_plan_lock.py` | Correct, tested, all status transitions work |
| `check_continuation.py` | Session-ID filtering logic (M6/M7/M8) is correct |
| `lifecycle_audit.py` | Add only 15 lines for expected_taskcard_count check |
| `plan_identity.py` | All functions reused directly, no modification |
| `validate_plan_readiness.py` | Reuse existing 8 checks at import time |
| Session-keyed lock files | Multi-plan isolation is correct |
| `autonomous_cycle.py` Step 0b | Reading any IN_PROGRESS lock (not session-filtered) is correct for resume |

**Redesign:**

| What | Change |
|---|---|
| CLAUDE.md Step 0 `cp` command | Replace with `python tools/supervisor/plan_importer.py --source <path>` |
| Validation gate timing | Pre-lock: validate plan_identity, TC table, mission conflict |
| Import idempotency | Registry check before any file write; skip `cp` if already registered |
| `plan_identity:` enforcement | BLOCKING at import (add block if missing; fail if can't be added) |
| Taskcard baseline | Embed `expected_taskcard_count` in plan_identity at import time |

**Do not build:**

| What | Why |
|---|---|
| Separate extractors / validators / registry as independent modules | All fit in one well-structured file; 5 modules for 300 LOC is over-engineered |
| Separate import-records/ directory | plan_identity block IS the import record; no duplication needed |
| 19-category semantic classifier | Not achievable reliably; breaks idempotency |
| Staging directory | Atomic write with .tmp + os.replace() directly to target is sufficient |
| Parallel JSON schema for the plan | Markdown IS the canonical form |

---

## Part 4: Architecture

### Core insight: plan_identity block doubles as the import record

Every piece of import provenance that needs to survive across sessions should live in the plan file's `plan_identity` block. That block is:
- Already the system's metadata carrier
- Already read by `plan_identity.py`, `validate_plan_readiness.py`, `lifecycle_audit.py`
- Session-independent (lives in the file, not the lock)
- Survives `cp` (if we stop using `cp` and use the importer instead)

The registry is a separate index for fast lookups (deduplication, conflict detection). It is NOT the source of truth — the plan file is. If the registry is lost, it can be rebuilt by scanning plan_identity blocks.

### Registry design

`.local/supervisor/plan-registry.json`:
```json
{
  "version": "1.0",
  "plans": {
    "sha256:abc123...": {
      "plan_id": "my-plan",
      "mission_id": "FF-001",
      "plan_path": "plans/.claude/my-plan.md",
      "status": "ACTIVE",
      "imported_at": "2026-07-10T..."
    }
  },
  "active_missions": {
    "FF-001": "sha256:abc123..."
  }
}
```

Source hash as primary key (not UUID import_id). This is the deduplication primitive. `active_missions` maps mission_id → source_hash of the currently ACTIVE plan for that mission. Used for fast conflict detection.

Atomic write: `.tmp` + `os.replace()`. No advisory lock needed for a single-agent tool — the check-then-write window is <1ms and no concurrent Python processes are expected.

### Extended plan_identity block

Fields added at import time:
```
<!--plan_identity:
  schema_version: "2.0"
  plan_id: "my-plan"
  mission_id: "FF-001"
  plan_type: "per_chat"
  default_lane: "UNRESOLVED"
  expected_taskcard_count: 9
  source:
    original_path: "~/.claude/plans/my-plan.md"
    original_hash: "sha256:abc123..."
    imported_at: "2026-07-10T..."
    importer_version: "1.0"
-->
```

These 4 new fields are sufficient:
- `expected_taskcard_count` — fixes Failure Mode 2
- `source.original_hash` — enables idempotency (registry deduplication)
- `source.original_path` — provenance
- `default_lane` — satisfies TASKCARDS_WITHOUT_LANE_OWNERSHIP counter

### Import logic (non-destructive)

The critical behavioral change from `cp`:

```
IF plans/.claude/{plan_id}.md exists AND source_hash is in registry:
    → DUPLICATE_NO_CHANGE (skip copy, just write new session lock)
ELIF plans/.claude/{plan_id}.md exists AND source_hash is NOT in registry:
    → The in-repo plan was modified post-import (agent edits or manual change)
    → Do NOT overwrite (would destroy execution state)
    → UPDATE_EXISTING_PLAN: re-read current file, update plan_identity source fields only
ELSE:
    → NEW_PLAN: write augmented plan to target, register, lock
```

This eliminates Failure Mode 1 entirely.

---

## Part 5: Taskcards

| Taskcard | Title | Status |
|---|---|---|
| TC-PIS-001 | plan-identity-v2 schema | OPEN |
| TC-PIS-002 | plan_importer.py (single module, all logic) | OPEN |
| TC-PIS-003 | lifecycle_audit.py patch (expected_taskcard_count check) | OPEN |
| TC-PIS-004 | Pilot tests and legacy migrator | OPEN |
| TC-PIS-005 | V144 governance validator and CLAUDE.md update | OPEN |

---

## TC-PIS-001 — plan-identity-v2 Schema

**Objective:** One JSON schema encoding the extended plan_identity block contract. Schema-only, no Python.

**File:** `.supervisor/schemas/plan-identity-v2.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PlanIdentityV2",
  "type": "object",
  "required": ["schema_version", "plan_id", "mission_id"],
  "additionalProperties": true,
  "properties": {
    "schema_version": {"type": "string", "enum": ["1.0", "2.0"]},
    "plan_id": {"type": "string", "minLength": 1},
    "mission_id": {"type": "string", "minLength": 1},
    "plan_type": {"type": "string"},
    "default_lane": {"type": "string", "default": "UNRESOLVED"},
    "expected_taskcard_count": {"type": "integer", "minimum": 0},
    "source": {
      "type": "object",
      "required": ["original_path", "original_hash"],
      "properties": {
        "original_path": {"type": "string"},
        "original_hash": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
        "imported_at": {"type": "string"},
        "importer_version": {"type": "string"}
      }
    }
  }
}
```

`additionalProperties: true` ensures backward compatibility with existing v1 plans that have extra fields.

**Validation:** `python -c "import json, jsonschema; jsonschema.validate({}, json.load(open('.supervisor/schemas/plan-identity-v2.schema.json')))"` should raise a validation error (missing required fields), not a schema load error.

**Allowed paths:** `.supervisor/schemas/` only.

---

## TC-PIS-002 — plan_importer.py

**Objective:** Single Python module (~320 LOC) that replaces the `cp` command. All logic in one file: extraction, augmentation, validation, registry, lock write.

**File:** `tools/supervisor/plan_importer.py`

**Functions and responsibilities:**

```python
# Public API
def import_plan(source: Path, supersede: bool = False, force: bool = False) -> ImportResult
def rebuild_registry(repo_root: Path = Path(".")) -> dict

# Internal — structural extraction (reuse existing parsers)
def _extract_tc_entries(text: str) -> list[dict]  # calls lifecycle_audit patterns directly
def _extract_plan_identity(plan_path: Path) -> dict | None  # calls plan_identity.extract_plan_identity()

# Internal — augmentation
def _augment_plan_identity(text: str, source: Path, source_hash: str, tc_count: int) -> str
def _normalize_tc_table(text: str, tc_entries: list[dict]) -> str

# Internal — validation
def _validate_structure(plan_path: Path, tc_count: int, registry: dict) -> list[str]  # blocking errors

# Internal — registry
def _load_registry(registry_path: Path) -> dict
def _save_registry(registry: dict, registry_path: Path) -> None  # atomic: .tmp + os.replace()
def _determine_disposition(source_hash: str, mission_id: str, registry: dict, supersede: bool) -> str

# Internal — import record (embedded in plan_identity, no separate file)
```

**`import_plan()` step sequence:**

1. **Compute source_hash.** `sha256 = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()`

2. **Check registry for DUPLICATE.** Load registry. If `source_hash in registry["plans"]` → return `ImportResult(disposition="DUPLICATE_NO_CHANGE")`. Zero further writes.

3. **Extract structure from source.** Call `_extract_tc_entries(source.read_text())` using the three compiled regexes imported directly from `lifecycle_audit`. Call `_extract_plan_identity(source)`. Record `tc_count = len(set(e["tc_id"] for e in tc_entries))`.

4. **Determine target path.** `target = Path("plans/.claude") / f"{plan_id}.md"` where `plan_id` is from plan_identity block or filename stem.

5. **Handle existing target (non-destructive).** If `target.exists()`:
   - Source hash NOT in registry → `UPDATE_EXISTING_PLAN`: read current target, update only the `source:` sub-object in plan_identity, do NOT touch taskcard statuses or other content.
   - Source hash IS in registry → already handled in step 2 (DUPLICATE). This path is unreachable.

6. **Augment plan_identity.** If target does not exist (NEW_PLAN): call `_augment_plan_identity()` which prepends the `<!--plan_identity: ...-->` block if missing, or adds the `source:` sub-object if block exists. Sets `expected_taskcard_count`, `default_lane`.

7. **Normalize TC table.** If TC entries found in BLOCK or INLINE format but no TABLE rows exist: call `_normalize_tc_table()` which inserts a 2-column table after the plan_identity block. Does NOT remove original format. If tc_count == 0: record GAP(MISSING_TASKCARDS). Without `--force`, return `ImportResult(disposition="REJECT_INVALID", errors=["No TC-* entries found"])`.

8. **Validate structure.** Call `_validate_structure(target_path_or_staging, tc_count, registry)` which checks: (a) plan_identity block present with plan_id and mission_id, (b) no duplicate TC-IDs, (c) no mission_id conflict in registry unless `--supersede`, (d) TC statuses are recognized values. Returns list of blocking error strings.

9. **Atomic write to target.** Write augmented text to `target.with_suffix(".md.tmp")`, then `os.replace(tmp, target)`. If target existed: write only the plan_identity section changes.

10. **Update registry atomically.** Determine disposition from `_determine_disposition()`. For CONFLICT: write entry to `.local/supervisor/plan-conflicts.jsonl`, return without registering. For all others: update `registry["plans"]` and `registry["active_missions"]`, call `_save_registry()`.

11. **Write plan lock.** ONLY after step 10 succeeds: call `subprocess.run(["python", "tools/supervisor/write_plan_lock.py", "--plan-path", str(target)])` or import and call the function directly.

12. **Return result with all 20 counters computed.**

**`ImportResult` dataclass:**
```python
@dataclass
class ImportResult:
    success: bool
    disposition: str         # DUPLICATE_NO_CHANGE | NEW_PLAN | UPDATE_EXISTING_PLAN | SUPERSEDE | CONFLICT_REQUIRES_REVIEW | REJECT_INVALID
    plan_path: Path | None
    errors: list[str]        # blocking errors that prevented import
    warnings: list[str]
    counters: dict[str, int] # all 20 required counters
```

**`rebuild_registry()` function:** Scans `plans/.claude/*.md`, reads each plan_identity block via `plan_identity.extract_plan_identity()`, reconstructs registry from `source.original_hash` fields. Plans without `source.original_hash` are registered under key `"legacy:{plan_id}"` with status LEGACY_UNKNOWN. This is the recovery path if the registry is deleted or corrupted.

**`_normalize_tc_table()` specifics:** Takes the list of TC entries found (from any of the 3 formats). If any entries exist but no table row (`| TC-... |`) exists in the text, inserts after the plan_identity block:
```
## Taskcard Status Summary

| Taskcard | Status |
|---|---|
| TC-X-001 | OPEN |
...
```
Does NOT delete original block/inline format entries — just adds the table so lifecycle_audit's TABLE pattern reliably finds them. Expected_taskcard_count is set to the count from this combined list.

**CLI:**
```bash
python tools/supervisor/plan_importer.py --source ~/.claude/plans/my-plan.md
python tools/supervisor/plan_importer.py --source ~/.claude/plans/my-plan.md --dry-run
python tools/supervisor/plan_importer.py --source plans/.claude/existing.md --supersede
python tools/supervisor/plan_importer.py --force --source plans/.claude/no-taskcards.md
python tools/supervisor/plan_importer.py --rebuild-registry
python tools/supervisor/plan_importer.py --migrate-legacy  # runs legacy migrator logic
```

Exit 0: success or DUPLICATE_NO_CHANGE. Exit 1: blocked (REJECT_INVALID, CONFLICT). Exit 3: warnings only.

**Reuse explicitly:**
- `plan_identity.extract_plan_identity(path)` — for reading existing blocks
- `lifecycle_audit._TC_TABLE_RE`, `_TC_BLOCK_RE`, `_TC_INLINE_RE` — import directly, do not reimplement
- `write_plan_lock` module — call directly or via subprocess

**Allowed paths:** `tools/supervisor/plan_importer.py`, `plans/.claude/`, `.local/supervisor/plan-registry.json`, `.local/supervisor/plan-conflicts.jsonl`

---

## TC-PIS-003 — lifecycle_audit.py Patch

**Objective:** 15-line targeted change to add `expected_taskcard_count` check. Closes Failure Mode 2.

**What to add** (after the existing taskcard parsing at ~line 554):

```python
# Check parsed count against import-time baseline
if plan_path:
    _pid_block = _plan_identity_mod.extract_plan_identity(Path(plan_path))
    _expected_count = (_pid_block or {}).get("expected_taskcard_count")
    if _expected_count is not None:
        _parsed_count = total_taskcards_parsed
        if _parsed_count < _expected_count:
            _findings.append({
                "finding_id": "TC_COUNT_BELOW_BASELINE",
                "severity": "WARN",  # WARN not BLOCK: authors add tasks post-import legitimately
                "message": (
                    f"Parsed {_parsed_count} taskcards but plan_identity.expected_taskcard_count "
                    f"is {_expected_count}. Possible format drift: check for block/inline "
                    f"taskcards not captured by the table regex."
                ),
                "parsed_count": _parsed_count,
                "expected_count": _expected_count,
            })
        # Also surface in audit result for observability
        result_metadata["expected_taskcard_count"] = _expected_count
        result_metadata["parsed_taskcard_count"] = _parsed_count
```

**Why WARN not BLOCK:** Plan authors legitimately add taskcards after import (expected_count becomes stale in the upward direction). The check targets FORMAT LOSS (count drops below baseline), not growth. If count rises above expected: no warning. If count drops below: WARN so the discrepancy is visible and can be diagnosed.

**Allowed paths:** `tools/supervisor/lifecycle_audit.py` (15-line addition only)

**Regression test:** Create a test plan with `expected_taskcard_count: 3` in plan_identity but only 2 TC entries in table format. Run lifecycle_audit. Assert `TC_COUNT_BELOW_BASELINE` appears in findings.

---

## TC-PIS-004 — Pilot Tests and Legacy Migrator

**Objective:** Prove all failure modes are fixed and all 20 counters reach 0. Reconcile legacy plans.

### Pilot Tests (`tests/plan_import/test_plan_importer.py`)

Ten behavioral contracts. Each defined as precondition → operation → required postconditions:

| Pilot | Precondition | Operation | Required Postconditions |
|---|---|---|---|
| P1: Well-structured | Source has plan_identity, TC table, headings. Registry empty. | `import_plan(source)` | disposition=NEW_PLAN; plan_identity in target with source.original_hash and expected_taskcard_count; registry entry created; all 20 counters=0 |
| P2: Prose-heavy, no plan_identity, block-format TC | Source lacks plan_identity; TC in block/heading format only | `import_plan(source)` | plan_identity added with expected_taskcard_count=N; TC table inserted; all counters=0 |
| P3: No taskcards | Source has plan_identity but 0 TC-* entries | `import_plan(source)` without --force | disposition=REJECT_INVALID; ACTIONABLE_PLAN_ITEMS_WITHOUT_TASKCARDS=1; nothing written to plans/.claude/ |
| P4: Existing target with execution state | Target exists with 5 CLOSED tasks. Source matches original import. | `import_plan(source)` (same source as P1) | disposition=DUPLICATE_NO_CHANGE; target file UNCHANGED (CLOSED tasks preserved); MATERIAL_SECOND_RUN_CHANGES=0 |
| P5: Same bytes | Source is byte-identical to P1 source | `import_plan(source)` after P1 | disposition=DUPLICATE_NO_CHANGE; zero writes; MATERIAL_SECOND_RUN_CHANGES=0 |
| P6: Mission conflict | P1 imported. New source has same mission_id, different plan_id. | `import_plan(conflicting_source)` | disposition=CONFLICT_REQUIRES_REVIEW; conflict record written to plan-conflicts.jsonl; no write to plans/.claude/; COMPETING_AUTHORITATIVE_PLANS=1 |
| P7: Invalid TC status | TC entries have status UNKNOWN_STATUS | `import_plan(source)` | disposition=REJECT_INVALID; STANDARDIZED_PLAN_BROKEN_REFERENCES≥1 |
| P8: Duplicate TC-ID | Same TC-ID appears twice | `import_plan(source)` | disposition=REJECT_INVALID; DUPLICATE_PLAN_ITEM_IDS≥1 |
| P9: Round-trip | Copy of a real plan from plans/.claude/ (parallel-foraging-fairy.md or similar) | `import_plan(source)` | parse_plan_taskcards() count ≥ expected_taskcard_count; plan_identity present; lifecycle_audit produces no TC_COUNT_BELOW_BASELINE finding |
| P10: Idempotency | Same source as P1 | Two calls to `import_plan()` | first=NEW_PLAN; second=DUPLICATE_NO_CHANGE; file hash identical after both calls; MATERIAL_SECOND_RUN_CHANGES=0 |

Critical: P4 is the most important test. It directly verifies that Failure Mode 1 is fixed — a second import of the same source does NOT overwrite execution state (closed tasks).

**All tests use `tmp_path` for registry isolation.** `TestAllCountersZero` asserts every counter == 0 for P1.

**Run:** `.venv/Scripts/pytest tests/plan_import/ -v`

### Legacy Migrator (`--migrate-legacy` flag in plan_importer.py)

Not a separate file. Implemented as a mode within `plan_importer.py`.

For each `plans/.claude/*.md`:
1. Compute source_hash from current content
2. Skip if source_hash already in registry
3. Try `_extract_plan_identity()` — read existing plan_identity block if any
4. Extract `plan_id`/`mission_id` from block or from filename stem as fallback
5. Check for mission_id conflict → record LEGACY_CONFLICT, skip activation
6. Run structural validation in legacy_mode (WARN-only for missing plan_identity, missing TC table)
7. Register with status LEGACY_REGISTERED (validation passed) or LEGACY_REGISTERED_WITH_FAILURES

**Honest scope:** Legacy plans do NOT get `expected_taskcard_count` added (source originals are gone; the current file content IS the source). They get a registry entry so V144 stops flagging them. Authors wanting full standardization can run `plan_importer.py --source plans/.claude/<name>.md --force` which re-imports the current file as source (updates plan_identity with expected_taskcard_count and source.original_hash pointing to itself).

**Expected output after `--migrate-legacy`:**
```
Registered: 75 LEGACY_REGISTERED, 4 LEGACY_REGISTERED_WITH_FAILURES, 2 LEGACY_CONFLICT_SKIPPED
LEGACY_IMPORTED_PLANS_NOT_RECONCILED = 0
```

---

## TC-PIS-005 — V144 Governance Validator and CLAUDE.md Update

**Objective:** Make future imports go through plan_importer.py. Block direct `cp` usage. Update Step 0.

### Governance Validator V144

Add to `tools/supervisor/governance_validators.py`:

```python
def validate_plan_import_provenance(repo_root: Path | None = None) -> list[dict]:
    """
    V144: Every .md in plans/.claude/ must have an entry in plan-registry.json.
    - Registry absent: WARN (migrator not yet run)
    - LEGACY_REGISTERED or LEGACY_REGISTERED_WITH_FAILURES: WARN (grandfathered)
    - Plan with no registry entry: FAIL (direct cp detected; DIRECT_UNSTANDARDIZED_PLAN_COPY_PATHS += 1)
    """
    _root = repo_root or Path(".")
    _registry_path = _root / ".local/supervisor/plan-registry.json"
    if not _registry_path.exists():
        return [{"validator": "V144", "severity": "WARN", "message": "plan-registry.json absent; run plan_importer.py --migrate-legacy"}]

    _registry = json.loads(_registry_path.read_text())
    _registered_paths = {e["plan_path"] for e in _registry.get("plans", {}).values()}

    results = []
    for plan_file in sorted((_root / "plans/.claude").glob("*.md")):
        rel = plan_file.relative_to(_root).as_posix()
        if rel not in _registered_paths:
            results.append({
                "validator": "V144",
                "severity": "FAIL",
                "message": f"Plan {rel} has no registry entry — likely added via direct cp. Run: python tools/supervisor/plan_importer.py --source {rel}",
                "file": rel,
            })
    return results
```

Update `governance_validator_runner.py`: `expected_count` 165 → 166.
Update `tests/supervisor/test_governance_validators.py`: assertion 165 → 166.

### CLAUDE.md Step 0 Update

Replace Step 0 migration instruction (the `cp` + `write_plan_lock` two-command sequence) with:

```
python tools/supervisor/plan_importer.py --source <external-plan-path>
```

The importer handles: source preservation, plan_identity augmentation (with expected_taskcard_count), TC table normalization, structural validation, registry update, and plan lock write in one atomic sequence. It is idempotent: running it twice on the same source produces DUPLICATE_NO_CHANGE on the second call and does NOT overwrite the plan file.

**If exit code is 1:** The plan failed structural validation. Read the blocking errors printed to stdout. Fix the source plan and re-run. Do not use `--force` unless you understand the specific error being bypassed.

**Allowed paths:** `tools/supervisor/governance_validators.py`, `tools/supervisor/governance_validator_runner.py`, `tests/supervisor/test_governance_validators.py`, `CLAUDE.md`

---

## Part 6: Tradeoffs, Risks, and Limits

**Tradeoff 1: expected_taskcard_count is WARN-only at audit time**

Plan authors add taskcards post-import. If the count rises, no warning fires. If the count drops (format loss), WARN fires. This is advisory — the audit does not block closure on a count mismatch. The risk: a format-loss case that produces a count drop below 1 (but above 0) will fire WARN and require human review but will not automatically prevent premature closure. Mitigation: the existing `all_taskcards_closed = (open_count == 0) and (total > 0)` check still prevents closure if any parseable task is open. The count mismatch WARN is an additional signal, not a replacement.

**Tradeoff 2: UPDATE_EXISTING_PLAN does not re-validate structure**

When a source is re-imported and the target already exists, the importer updates only the plan_identity source fields without re-running full validation. This avoids accidentally blocking a plan that's mid-execution. Risk: if the plan was manually corrupted post-import, the UPDATE path will not catch it. Mitigation: `validate_plan_readiness.py` still runs at execution time (Step 0b-validate in autonomous_cycle.py).

**Tradeoff 3: Advisory locking is not concurrency-safe for separate processes**

The registry uses `.tmp` + `os.replace()` for atomic file writes but has no cross-process lock. Two simultaneous `plan_importer.py` invocations targeting different plans could both read a stale registry snapshot and produce a race on the write. For a single-agent development tool on a developer workstation, this is acceptable. Do not deploy this as a shared service without adding explicit file locking.

**Tradeoff 4: Legacy plans are registered but not standardized**

The `--migrate-legacy` pass registers 81 existing plans with content-hash entries. It does NOT add `expected_taskcard_count` or `source.original_hash` to their plan_identity blocks (those plans may not HAVE plan_identity blocks). V144 will show WARN (not FAIL) for them. This is honest: they are grandfathered, not fully standardized. Full standardization of a legacy plan requires `plan_importer.py --source plans/.claude/<name>.md --force` which re-imports the current file as its own "source."

**Honest limits:**

- Semantic requirement extraction from prose is not achieved and is not attempted. Plans with requirements buried in prose paragraphs will not have those requirements surfaced as structured items. This must be addressed at plan-mode generation time.
- The `ACTIONABLE_PLAN_ITEMS_WITHOUT_TASKCARDS` counter is partially satisfied: the importer flags when `tc_count == 0`. It cannot detect "prose paragraph that describes a task but has no corresponding TC-* entry."
- Concurrent imports of two DIFFERENT plans in separate terminal windows have a narrow race window on the registry write. This is a known, documented limit.

---

## Part 7: Files and Regression Controls

### Files Created / Modified

**New files:**
- `tools/supervisor/plan_importer.py` (~320 LOC)
- `.supervisor/schemas/plan-identity-v2.schema.json`
- `tests/plan_import/test_plan_importer.py` (10 pilot test classes)
- `tests/plan_import/fixtures/` (10 fixture .md files)

**Modified files (targeted, minimal):**
- `tools/supervisor/lifecycle_audit.py` — 15 lines added (expected_taskcard_count check)
- `tools/supervisor/governance_validators.py` — V144 function added
- `tools/supervisor/governance_validator_runner.py` — expected_count 165 → 166
- `tests/supervisor/test_governance_validators.py` — expected_count assertion 165 → 166
- `CLAUDE.md` — Step 0: replace `cp` command with `plan_importer.py` invocation

### Regression Controls (one test per failure mode)

**FM1: Session-B overwrite regression** (`test_session_b_does_not_overwrite`)
```python
# Precondition: plan imported, 5 tasks marked CLOSED in target
# Operation: call import_plan() with same source again
# Assert: target file hash is IDENTICAL to pre-call hash
# Assert: CLOSED task statuses are preserved
# Assert: disposition == DUPLICATE_NO_CHANGE
```

**FM2: Partial parse regression** (`test_expected_count_catches_format_drift`)
```python
# Precondition: plan_identity has expected_taskcard_count=3; plan has only 2 TC rows in table
# Operation: run lifecycle_audit on the plan
# Assert: TC_COUNT_BELOW_BASELINE in findings
# Assert: audit does not return TERMINAL_CLOSED
```

**FM3: Mission conflict regression** (`test_mission_conflict_blocks_import`)
```python
# Precondition: plan A with mission_id FF-001 is ACTIVE in registry
# Operation: import_plan(plan_B_same_mission)
# Assert: disposition == CONFLICT_REQUIRES_REVIEW
# Assert: plan B is NOT in plans/.claude/
# Assert: registry["active_missions"]["FF-001"] still points to plan A
```

**V144 regression** (`test_v144_catches_direct_copy`)
```python
# Operation: copy a .md file directly into plans/.claude/ bypassing importer
# Assert: validate_plan_import_provenance() returns FAIL for that file
# Operation: run import_plan() on that file
# Assert: validate_plan_import_provenance() returns WARN (now registered as LEGACY)
```

### End-to-End Verification

```bash
# 1. First import
python tools/supervisor/plan_importer.py --source ~/.claude/plans/<new>.md
# Expected: exit 0, NEW_PLAN, plan_identity present in plans/.claude/<new>.md

# 2. Idempotency check (same source)
python tools/supervisor/plan_importer.py --source ~/.claude/plans/<new>.md
# Expected: exit 0, DUPLICATE_NO_CHANGE, target file unchanged

# 3. Legacy migration
python tools/supervisor/plan_importer.py --migrate-legacy
# Expected: LEGACY_IMPORTED_PLANS_NOT_RECONCILED = 0

# 4. Governance suite
python tools/supervisor/governance_validator_runner.py
# Expected: V144 passes (WARN for legacy plans, 0 FAILs), actual_count=166

# 5. Pilot test suite
.venv/Scripts/pytest tests/plan_import/ -v
# Expected: 10 pilots pass, FAILED_REQUIRED_PILOTS = 0

# 6. Counter assertion
python -c "
import sys, tempfile
from pathlib import Path
sys.path.insert(0, '.')
from tools.supervisor.plan_importer import import_plan
r = import_plan(
    Path('tests/plan_import/fixtures/pilot1_well_structured.md'),
    registry_path=Path(tempfile.mktemp(suffix='.json'))
)
failed = {k: v for k, v in r.counters.items() if v != 0}
if failed:
    print(f'FAIL: non-zero counters: {failed}', file=sys.stderr)
    sys.exit(1)
print('EXTERNAL_PLAN_INGESTION_STANDARDIZED_VALIDATED_AND_IDEMPOTENT')
"

# 7. Partial-parse protection
python tools/supervisor/lifecycle_audit.py \
    --mission-id FM2-TEST \
    --plan-path tests/plan_import/fixtures/format_drift.md
# Expected: TC_COUNT_BELOW_BASELINE in findings output
```
