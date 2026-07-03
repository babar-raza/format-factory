# Lane Separation Protocol

**Status:** Active
**Plan:** sequential-twirling-sunrise (TC-LSG-008)
**Enforced by:** `tools/supervisor/scope_guard.py`

---

## Why This Protocol Exists

A CI audit plan discovered pre-existing architecture failures (oversized C# files) and product
API gaps during CI job analysis. Instead of delegating those findings to the appropriate lanes,
the plan fixed them directly — touching `src/net/csv/CsvDocument.cs` with new analytics API
methods. This violated lane boundaries and contaminated the CI audit sprint with unrelated
product work.

The root cause was not a bad agent decision. The root cause was that the machinery gave the
agent no basis to make the right decision:

- No registry declaring which files each lane may touch
- No runtime enforcement at commit time
- No delegation protocol for out-of-scope discoveries
- No gate preventing the plan from retrying its main task before delegated work completed

This protocol installs all four missing mechanisms.

---

## The Four Components

```
+------------------------------------------------------------------+
|  1. LANE SCOPE REGISTRY                                          |
|     registry/lane-scope-registry.yaml                            |
|     Per-lane permitted_writes / forbidden_writes.                |
|     on_out_of_scope_discovery = agent directive field.           |
+------------------------------------------------------------------+
|  2. SCOPE GUARD                                                  |
|     tools/supervisor/scope_guard.py                              |
|     Reads registry -> validates files -> reports violations.     |
|     Runs as pre-commit hook (warn mode initially).               |
|     Also runs at plan closeout (Phase 13 of validator).          |
+------------------------------------------------------------------+
|  3. DELEGATION PROTOCOL                                          |
|     tools/supervisor/delegate_gap.py                             |
|     When scope_guard reports a violation or an out-of-scope      |
|     discovery is made: write to delegation-ledger.json +         |
|     known-failure-ledger.yaml + delegation-handoff file.         |
|     Supervisor picks up open delegations on next cycle.          |
+------------------------------------------------------------------+
|  4. DELEGATION GATE                                              |
|     tools/supervisor/delegation_gate.py                          |
|     Blocks plan from proceeding past a declared wait point       |
|     until all delegated gaps are status=closed.                  |
+------------------------------------------------------------------+
```

**IMPORTANT: delegation-ledger.json != gap-ledger.json**

`reports/governance/delegation-ledger.json` is the delegation store.
`reports/capability-layer/gap-ledger.json` is the product capability gap store.
These are SEPARATE files with incompatible schemas. `delegate_gap.py` writes to the
governance ledger only. Do not confuse them.

---

## Lane Scope Registry

File: `registry/lane-scope-registry.yaml`

Each lane entry defines:

```yaml
- id: lane-ci-audit
  name: CI Configuration Audit
  permitted_writes:
    - ".github/workflows/**"
    - "registry/known-failure-ledger.yaml"
    - "reports/governance/delegation-ledger.json"
    # ...
  forbidden_writes:
    - "src/**"
    - "tests/**"
    # ...
  on_out_of_scope_discovery:
    action: delegate       # AGENT DIRECTIVE - not consumed by scope_guard.py
    never: fix_directly
    protocol: delegation_handoff_v1
```

**`on_out_of_scope_discovery` is an agent-directive field** — it tells the executing
agent/plan what to do when a scope violation is reported. It is NOT read by
`scope_guard.py` at runtime. The scope guard only reports; the agent decides.

**All lanes include `delegation-ledger.json` and `known-failure-ledger.yaml` in
`permitted_writes`** so that `delegate_gap.py` can be called from any lane.

---

## In-Scope vs Out-of-Scope Discovery Triage

```
Agent discovers a failure during sprint work
            |
            v
Is the failure in my lane's permitted_writes?
            |
     YES    |    NO
     |      |    |
     v      |    v
Fix it.     |  Run scope_guard.py --mode block
            |  (or check forbidden_writes manually)
            |            |
            |            v
            |  scope_guard reports VIOLATION
            |            |
            |            v
            |  Call delegate_gap.py with target-lane
            |            |
            |            v
            |  Check delegation_gate.py before retrying main task
            |            |
            |  If GATE CLOSED: STOP, do not proceed
            |  If GATE OPEN: proceed to next step
```

---

## 5-Step Delegation Protocol

When you discover an out-of-scope failure:

**Step 1: Run scope_guard to confirm violation**
```bash
python tools/supervisor/scope_guard.py \
  --lane lane-ci-audit \
  --changed-files src/net/csv/CsvDocument.cs \
  --mode block \
  --registry registry/lane-scope-registry.yaml
# exit 1 = violation confirmed
```

**Step 2: Register the delegation**
```bash
python tools/supervisor/delegate_gap.py \
  --gap-id GAP-LANE5-001 \
  --target-lane lane-5-dotnet-structure \
  --file src/net/fods/FodsDocumentAccessor.cs \
  --description "Exceeds baseline_loc_cap by 650 LOC. Pre-existing architecture debt." \
  --severity P1 \
  --discovered-by lane-ci-audit \
  --plan-id my-plan-id
# Writes to: reports/governance/delegation-ledger.json
#            registry/known-failure-ledger.yaml
#            .local/ci-audit/delegation-handoff-my-plan-id.yaml
```

**Step 3: Do NOT fix the issue yourself.** Revert any changes to the out-of-scope file
if already made. Log the known-failure-ledger entry as the formal record.

**Step 4: Supervisor picks up the delegation on the next autonomous cycle.**
No explicit trigger needed — `autonomous_cycle.py` reads `delegation-ledger.json` and
converts open delegations to `next-work-items.json` entries for `target_lane`.

**Step 5: Check gate before retrying your main task**
```bash
python tools/supervisor/delegation_gate.py --plan-id my-plan-id
# exit 0 = GATE OPEN  (delegation resolved, proceed)
# exit 1 = GATE CLOSED (wait - supervisor still working)
# exit 2 = no delegations registered (proceed)
```

---

## Closing a Delegation (for Testing/Simulation)

When the target lane sprint completes, it updates the delegation status. For testing,
use this Python one-liner:

```python
import json
from pathlib import Path
p = Path('reports/governance/delegation-ledger.json')
d = json.loads(p.read_text())
for g in d['delegations']:
    if g['gap_id'] == 'GAP-LANE5-001':
        g['status'] = 'closed'
p.write_text(json.dumps(d, indent=2))
```

---

## Scope Guard Pre-Commit Hook

The hook runs in `warn` mode initially (TC-LSG-004). Violations are printed to stderr
but never block commits. This provides visibility without disrupting existing workflows.

```yaml
# In .pre-commit-config.yaml (under existing - repo: local block)
- id: scope-guard
  name: Lane scope guard (warn mode)
  language: system
  entry: python tools/supervisor/scope_guard.py --from-git-staged --lane-from-lock --mode warn
  pass_filenames: false
  always_run: false
  stages: [pre-commit]
```

**Escalation path (warn -> block):**
After >= 3 sprints running in warn mode with zero false-positives, upgrade to block mode
via TC-LSG-009. Change `--mode warn` to `--mode block` in the hook entry.

---

## Scope Guard at Plan Closeout

`sprint_executor_validate.py` Phase 13 runs the scope guard against `changed_files` in
the evidence declaration. Violations appear as `scope_warnings` in the validator output
(WARN only, never FAIL — closeout must not block per Supreme Directive).

The `lane_id` is read from `active-plan-lock.json` (written by `write_plan_lock.py`
via the TC-LSG-003 extension). If `lane_id` is `unknown`, the scope check is skipped.

---

## How Plans Declare Their Lane

Add to the plan file header:

```markdown
# My Plan Name
# lane: lane-ci-audit
```

`write_plan_lock.py` parses this and writes `lane_id` to both lock files.
`scope_guard.py --lane-from-lock` reads it back.

---

## How to Add New Lanes

1. Add a new entry to `registry/lane-scope-registry.yaml`
2. Define `permitted_writes`, `forbidden_writes`, `on_out_of_scope_discovery`
3. Always include these in `permitted_writes` (allows delegation from any lane):
   - `"registry/known-failure-ledger.yaml"`
   - `"reports/governance/delegation-ledger.json"`
4. Add `"# lane: <new-lane-id>"` to the plan file header for plans in that lane
5. Validate: `python -c "import yaml; yaml.safe_load(open('registry/lane-scope-registry.yaml'))"`

---

## Files Created by This Protocol

| File | Purpose |
|------|---------|
| `registry/lane-scope-registry.yaml` | Lane boundary definitions |
| `tools/supervisor/scope_guard.py` | File boundary enforcer |
| `tools/supervisor/delegate_gap.py` | Cross-lane delegation CLI |
| `tools/supervisor/delegation_gate.py` | Wait-for-supervisor gate |
| `reports/governance/delegation-ledger.json` | Delegation state (separate from product gap-ledger) |
| `tests/tools/test_scope_guard.py` | 23-test suite for scope_guard |

## Files Modified by This Protocol

| File | Change |
|------|--------|
| `tools/supervisor/write_plan_lock.py` | Added `lane_id` field parsing + writing |
| `tools/supervisor/sprint_executor_validate.py` | Added Phase 13 scope guard check |
| `.pre-commit-config.yaml` | Added `scope-guard` hook (warn mode) |
