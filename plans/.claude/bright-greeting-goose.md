# Plan: Maintenance Obligation Register — Durable Cross-Session Deferred Work Tracking

## Context

TC-BF-004's observation window (run `check_tombstone_records.py` on 2026-08-05) was not
tracked after bright-greeting-goose closed. A human caught it. This is a systemic failure,
not a one-off omission.

---

## Symptom vs Root Cause vs Structural Weakness

### Visible symptom
A scheduled monitoring task was not in any ledger after plan closure.

### What the first-pass plan got wrong
It proposed writing deferred items to `gap-ledger-pinned.json` alongside the capability
gap ledger. That approach fails on contact with production:

- `capability_map_generator.py` regenerates `gap-ledger.json` **every autonomous cycle**.
  Entries with `status: open` that are not derived from POC targets are silently discarded.
  Only `closed`, `DEFERRED_BY_DESIGN`, and `supplemental: true` entries survive.
- `capability_feature_compiler.py` validates every open gap against spec qnames.
  Maintenance items have no qnames → they fail QName validation and are rejected.
- The capability gap pipeline is purpose-built for product feature gaps. Injecting
  operational obligations into it pollutes sprint scoring, work-item selection,
  and governance validator counts.

The gap ledger is the wrong destination. This plan does not use it.

### Root causes (three independent failures)

**R1 — No canonical authoring format for deferred items.**
Across 73 closed plans, 21+ different status vocabularies are used: `DEFERRED`,
`DEFERRED_WITH_REASON`, `DEFERRED_BY_DESIGN`, `DEFERRED_NOT_FAILED`, `not_attempted`,
`VALID_DEFERRED`, `EXCLUDED`, `CHILDREN_IN_PROGRESS` with prose explanation. An extractor
that works on one plan fails on another. Prose extraction is non-deterministic across reruns.

**R2 — Plan closure produces a write-only artifact.**
`terminal_closure_record.json` captures `all_taskcards_closed`, `audit_verdict`, and
`closure_contract` — but omits `open_gaps`, `findings`, and `rework_items` from the
lifecycle audit output. No code in the supervisor pipeline reads
`.local/evidences/plan-closures/` after a plan closes. `check_continuation.py` explicitly
skips TERMINAL_CLOSED locks. `session-resume.md` and `next-sprint.md` are generated fresh
with zero awareness of closed-plan obligations. Closed plans are write-only.

**R3 — No lifecycle ownership for deferred obligations.**
Even items that do make it into prose have no: status progression, due-date surfacing,
overdue detection, or escalation. Prior attempts existed (`.local/r52-metadata/deferred-work-r53.txt`,
`.local/r53-metadata/deferred-work-r54.txt`) and were abandoned — no retrieval mechanism
was ever connected to the write path.

### Structural weakness
The session boundary is opaque to obligation inheritance. When a plan closes, the
supervisor pipeline has no step that asks "what did this plan defer?" and routes the answer
into any future-session artifact that gets read.

---

## What Must Be Preserved

- `gap-ledger.json` and its regeneration pipeline — untouched
- `capability_feature_compiler.py` — untouched
- `write_plan_lock.py` and `lifecycle_audit.py` — extended only, not modified in their
  core logic
- All existing plan closure machinery and terminal_closure_record.json schema (add fields,
  never remove)
- The canonical gap→work-item→declaration→grade→close pipeline for product work

---

## Solution: Maintenance Obligation Register (MOR)

A dedicated register for operational obligations that: survives autonomous cycle reruns,
has a governed lifecycle, surfaces in future sessions when due, and is never mixed with
product capability tracking.

### Why a separate register, not the gap ledger

Maintenance obligations and capability gaps have different consumers, different schemas,
different lifecycle transitions, and different expiry semantics. Mixing them produces
false positives in governance validators, misleads sprint scoring, and creates items the
capability compiler cannot process. Separation is not over-engineering; it is the correct
architectural boundary.

---

## Component Design

### C1 — Canonical deferred-item declaration format (plan authoring contract)

Every plan that defers work beyond its scope MUST include a `## Deferred Work Register`
section with machine-parseable YAML blocks. This is the extraction contract — the extractor
reads only this block, not prose.

```markdown
## Deferred Work Register

\`\`\`yaml
deferred_item:
  obligation_id: MO-BGG-001
  source_taskcard: TC-BF-004
  type: observation_window        # observation_window | scheduled_maintenance
                                  # | follow_up | valid_deferred
  action: "run check_tombstone_records.py; classify external_host_loop.py as FIRED or CONFIRMED_DEAD"
  scheduled_date: "2026-08-05"   # ISO date; omit if no fixed date
  owner: governance               # governance | maintenance | product
  reason: "30-day observation window from tombstone_date 2026-07-06"
\`\`\`
```

This block belongs in the plan before closure. Retroactive extraction from prose is
explicitly not supported — it cannot be made reliable.

**Implication:** Plans authored without this block produce zero MOR entries at closure.
This is correct behavior. Prose-only deferrals are not tracked. Authors must opt in.

---

### C2 — New tool: `tools/supervisor/maintenance_obligation_register.py`

**Core functions:**

```python
def extract_from_plan(plan_path: Path) -> list[dict]:
    """
    Parse ## Deferred Work Register sections for deferred_item: YAML blocks.
    Returns list of raw dicts. Empty list if section absent or no blocks found.
    Does NOT parse prose. Fails loudly on malformed YAML (not silently skipped).
    """

def register_obligations(
    obligations: list[dict],
    source_plan: str,
    source_plan_hash: str,
    register_path: Path,
) -> tuple[int, int]:
    """
    Idempotent write to MOR. Deduplicates by obligation_id.
    Returns (newly_added, already_existed).
    Never overwrites a completed obligation.
    """

def surface_due_obligations(
    register_path: Path,
    lookahead_days: int = 14,
) -> list[dict]:
    """
    Return open obligations with scheduled_date within lookahead_days,
    plus all open obligations with no scheduled_date (always surface).
    Returns empty list if register absent.
    """

def mark_completed(
    obligation_id: str,
    evidence: str,
    register_path: Path,
) -> bool:
    """
    Transition obligation to status: completed. Idempotent.
    Returns False if obligation not found (not an error).
    """
```

**MOR schema (`reports/supervisor/maintenance-obligations.json`):**
```json
{
  "schema_version": "1.0",
  "last_updated": "<ISO>",
  "obligations": [
    {
      "obligation_id": "MO-BGG-001",
      "type": "observation_window",
      "action": "run check_tombstone_records.py ...",
      "scheduled_date": "2026-08-05",
      "owner": "governance",
      "reason": "30-day observation window from tombstone_date 2026-07-06",
      "source_plan": "plans/.claude/bright-greeting-goose.md",
      "source_plan_hash": "314f0d31...",
      "source_taskcard": "TC-BF-004",
      "status": "open",
      "created_at": "2026-07-07T...",
      "completed_at": null,
      "completion_evidence": null
    }
  ]
}
```

This file is **never written by** `capability_map_generator.py`.
It survives all autonomous cycle reruns.

---

### C3 — Write path: hook in `write_plan_lock.py`

**Location:** After `_write_terminal_closure_record()` (~line 337), inside
`status == "TERMINAL_CLOSED"` branch.

```python
# TC-MOR-001: extract and register deferred obligations at plan closure
try:
    from maintenance_obligation_register import extract_from_plan, register_obligations
    obligations = extract_from_plan(Path(plan_path))
    if obligations:
        mor_path = repo_root / "reports" / "supervisor" / "maintenance-obligations.json"
        added, existed = register_obligations(
            obligations, plan_path, plan_hash, mor_path
        )
        print(f"[write_plan_lock] TC-MOR-001: {added} obligation(s) registered, "
              f"{existed} already existed")
except Exception as exc:
    print(f"[write_plan_lock] TC-MOR-001: MOR extraction failed (non-blocking): {exc}",
          file=sys.stderr)
```

**Non-blocking contract:** Extraction failure MUST NOT prevent TERMINAL_CLOSED from
being written. The `except` catches all exceptions and logs to stderr only.

**Also extend terminal_closure_record.json schema** (additive only):
```python
record["deferred_obligations"] = [o["obligation_id"] for o in obligations]
```

---

### C4 — Read path: session-resume.md surfacing

**Location:** In the supervisor packet generator that produces `session-resume.md`
(or as a standalone step in `autonomous_cycle.py` after generating the packet).

```python
from maintenance_obligation_register import surface_due_obligations
due = surface_due_obligations(
    repo_root / "reports" / "supervisor" / "maintenance-obligations.json",
    lookahead_days=14,
)
if due:
    # Inject into session-resume.md under new section:
    # ## Maintenance Obligations Due
    # | obligation_id | type | scheduled_date | action | owner |
```

This is the critical read path. Without it, the write path produces a write-only artifact
(the same failure as terminal_closure_record.json). Both paths must exist for the system
to work.

---

### C5 — Governance validator: overdue obligations

New validator (V162 or next available) in `governance_validators_ext4.py`:

```python
def validate_maintenance_obligations_current(declaration: dict, repo_root: Path = None) -> dict:
    """V162: Warn when open MOR obligations are past their scheduled_date."""
```

Verdict: WARNING (not GOV_BLOCK) — overdue maintenance does not block sprint work,
but must be visible. `blocks_sprint: False`.

---

### C6 — Control index ingestor

New file: `tools/supervisor/control_index/ingestors/maintenance_obligation_ingestor.py`

New SQLite table: `maintenance_obligations`
Indexed columns: `obligation_id`, `type`, `status`, `scheduled_date`, `owner`, `source_plan`

Query: `python -m tools.supervisor.control_index.query obligations --filter "status=open"`

---

### C7 — Immediate backfill

Add `## Deferred Work Register` section to `plans/.claude/bright-greeting-goose.md`
with the TC-BF-004 observation window entry. Then run the extractor to write to MOR.

This is the retroactive registration for the item that triggered this work.

---

## Files to Create or Modify

| File | Change | Rationale |
|---|---|---|
| `tools/supervisor/maintenance_obligation_register.py` | **New** | Core tool — extract, register, surface, complete |
| `reports/supervisor/maintenance-obligations.json` | **New** | MOR — never overwritten by autonomous cycle |
| `tools/supervisor/write_plan_lock.py` | **Modify** | Add TC-MOR-001 hook (~line 337); extend closure record schema |
| Supervisor packet generator / `session-resume.md` template | **Modify** | Inject due obligations section |
| `tools/supervisor/governance_validators_ext4.py` | **Modify** | Add V162 overdue-obligations validator |
| `tools/supervisor/control_index/ingestors/maintenance_obligation_ingestor.py` | **New** | Control index ingestion |
| `plans/.claude/bright-greeting-goose.md` | **Modify** | Add `## Deferred Work Register` with TC-BF-004 entry |
| `tests/supervisor/test_maintenance_obligation_register.py` | **New** | Unit + integration tests |

**Explicitly NOT modified:**
- `gap-ledger.json` or any file in `reports/capability-layer/`
- `capability_map_generator.py`
- `capability_feature_compiler.py`
- `lifecycle_audit.py` core logic (only terminal_closure_record.json schema is extended)

---

## Execution Order

1. `maintenance_obligation_register.py` — core tool (all other components depend on this)
2. Add `## Deferred Work Register` to bright-greeting-goose.md; run extractor → verify MOR populated
3. Hook `write_plan_lock.py` (TC-MOR-001); extend closure record schema
4. Locate and update session-resume.md generation to surface due obligations
5. Add V162 governance validator
6. Add control index ingestor
7. Write tests

---

## Validation Steps

```bash
# 1. Unit test the extractor on bright-greeting-goose.md
python tools/supervisor/maintenance_obligation_register.py \
  extract --plan-path plans/.claude/bright-greeting-goose.md

# 2. Verify MOR populated (expect MO-BGG-001, scheduled_date 2026-08-05)
python -c "
import json
data = json.load(open('reports/supervisor/maintenance-obligations.json'))
print(len(data['obligations']), 'obligations')
for o in data['obligations']:
    print(o['obligation_id'], o['status'], o.get('scheduled_date'))
"

# 3. Re-run write_plan_lock --terminal — verify idempotency (0 newly added, 1 existed)
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/bright-greeting-goose.md --terminal
# Expect: "TC-MOR-001: 0 obligation(s) registered, 1 already existed"

# 4. Verify MOR survives autonomous cycle (gap ledger regeneration)
python tools/supervisor/autonomous_cycle.py \
  --declaration .local/evidences/test-decl.yaml --dry-run
python -c "
import json
data = json.load(open('reports/supervisor/maintenance-obligations.json'))
assert any(o['obligation_id'] == 'MO-BGG-001' for o in data['obligations']), 'WIPED'
print('MOR survived regen — OK')
"

# 5. Test due-surfacing with synthetic overdue entry
python tools/supervisor/maintenance_obligation_register.py \
  surface --lookahead-days 14

# 6. Run tests
.venv/Scripts/pytest tests/supervisor/test_maintenance_obligation_register.py -v

# 7. Verify V162 validator fires on overdue obligation
python -c "
import sys; sys.path.insert(0,'tools/supervisor')
from governance_validators_ext4 import validate_maintenance_obligations_current
from pathlib import Path
decl = {'sprint_id': 'test', 'planned_work_items': []}
result = validate_maintenance_obligations_current(decl, repo_root=Path('.'))
print('V162:', result.get('verdict'), '|', result.get('summary'))
"
```

---

## Regression Controls

1. **V162 must not fire as GOV_BLOCK** — only WARNING. Test that `blocks_sprint: False`.
2. **MOR idempotency** — running write_plan_lock --terminal twice must not duplicate entries.
3. **MOR survives regen** — the survival test in step 4 above is a required regression test.
4. **Non-blocking closure** — if `maintenance_obligation_register.py` raises any exception,
   TERMINAL_CLOSED must still be written. Test by passing a corrupted plan path.
5. **Governance test count** — if V162 is added to the runner, expected_count in
   `governance_validator_runner.py` and `test_governance_validators.py` must be updated.
   Currently 161; will become 162. Both must be updated atomically.

---

## Tradeoffs and Honest Limits

**Gap ledger destination (why rejected):**
The user's original request said "gap ledger." The audit shows this cannot work reliably:
open entries are wiped on every cycle regen, and the capability compiler rejects items
without qnames. The MOR is a separate register that correctly separates concerns.
If the gap ledger is later refactored to support persistent manual entries, MOR entries
could be mirrored there — but that is not this plan's scope.

**Plan authoring compliance burden:**
The `## Deferred Work Register` format only works for plans authored after this change.
All 73 existing closed plans have deferred items in prose that cannot be reliably extracted.
The backfill for bright-greeting-goose.md is manual. This is the honest limit: there is
no retroactive fix for existing prose-only deferrals. The system improves going forward.

**Prose extraction was explicitly rejected:**
Extracting from arbitrary prose (e.g., "expires 2026-08-05") is non-deterministic, fails
differently on every plan, and cannot be made reliable without training data. The
canonical YAML block is the only defensible approach for production use.

**Prior attempts failed for the same reason:**
`.local/r52-metadata/deferred-work-r53.txt` et al. were write-only artifacts with no
read path connected. This plan's C4 (read path into session-resume.md) is what makes
the MOR different from those abandoned files. If C4 is skipped, the MOR becomes the
same write-only failure. C4 is not optional.

**Due-date surfacing is advisory, not enforced:**
The MOR surfaces obligations as context in session-resume.md. It does not block sprint
execution if an obligation is overdue. The V162 validator fires a WARNING only. This
is intentional: maintenance tasks should not stop product work. The tradeoff is that
overdue obligations can be silently ignored by an agent under time pressure. A future
hardening could add a `must_acknowledge: true` field that triggers a softer gate.

**Control index (C6) is lower priority:**
The control index is useful for querying but not required for correctness. C1-C5 deliver
the functional requirement. C6 can be deferred if implementation time is constrained.
This is the only component that is explicitly optional.

---

## Deferred Work Register

```yaml
deferred_item:
  obligation_id: MO-BGG-001
  source_taskcard: TC-BF-004
  type: observation_window
  action: "run check_tombstone_records.py in tools/supervisor/; classify external_host_loop.py as FIRED or CONFIRMED_DEAD; update COMPONENT-REGISTER.yaml entry tombstone_status field"
  scheduled_date: "2026-08-05"
  owner: governance
  reason: "30-day observation window from tombstone_date 2026-07-06; checks whether suspected ghost file was invoked in production within the window"
```


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-08T09:18:58.204002+00:00"
  locked_by: "6aa05023e6ac"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
