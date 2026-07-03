# Lane Separation Governance — Machinery Design & Implementation
# sequential-twirling-sunrise — v5 (Forensics-Healed, 2026-07-03)

---

## PLAN LINEAGE

| Version | Date | Change |
|---------|------|--------|
| v1-v3 | 2026-07-03 | CI audit and remediation attempts |
| v4 | 2026-07-03 | Governance-only reframe: the CI job is irrelevant; the governance flaw is the subject |
| v5 | 2026-07-03 | PLAN FORENSICS surgical healing: 9 findings recorded and remediated (F-001..F-009) |

## FORENSIC FINDINGS (v5 surgical healing — all must be incorporated before execution)

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| F-001 | CRITICAL | `delegate_gap.py` writes to `gap-ledger.json` but actual schema is incompatible (`owning_lane` is integer 1/2/3; no `target_lane`, `discovered_by`, `plan_id`, `file` fields exist). Delegation data must go to a SEPARATE file: `reports/governance/delegation-ledger.json` | HEALED in Component 3, TC-LSG-005 |
| F-002 | CRITICAL | `fnmatch.fnmatch("src/net/csv/CsvDocument.cs", "src/**")` returns **False** — fnmatch does not implement `**` as multi-level wildcard. TC-LSG-002 acceptance test would silently pass wrong paths. Must use explicit `_glob_matches()` helper | HEALED in Component 2, TC-LSG-002 |
| F-003 | HIGH | TC-LSG-004 hook YAML missing `stages: [pre-commit]` — all existing hooks in `.pre-commit-config.yaml` require this field. Hook would not run without it | HEALED in TC-LSG-004 |
| F-004 | HIGH | No rollback procedure in any of the 8 taskcards — an implementation that breaks tests has no stated remediation path | HEALED: rollback added to each taskcard |
| F-005 | HIGH | No taskcard for upgrading scope guard from warn→block mode — mentioned in prose but untracked | HEALED: TC-LSG-009 added |
| F-006 | HIGH | No taskcard ownership field — no agent/role assigned to any taskcard | HEALED: Owner field added to each taskcard |
| F-007 | MEDIUM | `on_out_of_scope_discovery` in registry is not consumed by `scope_guard.py` — it is dead config unless explicitly read | HEALED: documented as agent-directive field, not scope_guard input |
| F-008 | MEDIUM | `registry/known-failure-ledger.yaml` in `delegate_gap.py` writes but NOT in `permitted_writes` for lanes other than lane-ci-audit. All lanes must be able to delegate. | HEALED: added to permitted_writes of all lanes |
| F-009 | LOW | Verification scenario says "set status=closed manually" but no mechanism defined | HEALED: Python one-liner added to verification section |

**Parent plan:** `plans/master-plan.md`
**User directive:** The CI job uncovered a governance flaw. Handle the flaw professionally. Do not treat this as a CI repair task.

---

## CONTEXT — THE GOVERNANCE FLAW

A CI audit plan executed and, upon discovering pre-existing failures in a different lane (architecture debt, missing product APIs), directly fixed those failures instead of delegating them. The agent had:

- No awareness of which files its lane is permitted to modify
- No protocol for handling out-of-scope discoveries
- No mechanism to hand off out-of-scope work to the supervisor
- No gate preventing it from retrying the main task before delegated work was complete

This is a structural gap in the supervision machinery. Plans can touch any file in the repository. There is no lane boundary enforcement at commit time, declaration time, or runtime. Scope violations go undetected until a human notices them.

**The flaw is not that the agent made a bad decision. The flaw is that the machinery gave the agent no basis to make the right decision.**

---

## DESIGN OVERVIEW

Four components are needed:

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. LANE SCOPE REGISTRY                                             │
│     registry/lane-scope-registry.yaml                               │
│     Machine-readable: per-lane permitted/forbidden writes,          │
│     on_out_of_scope_discovery protocol.                             │
├─────────────────────────────────────────────────────────────────────┤
│  2. SCOPE GUARD                                                      │
│     tools/supervisor/scope_guard.py                                  │
│     Reads registry → validates staged files → blocks forbidden       │
│     writes at commit time. Runs as pre-commit hook.                  │
│     Also runs at plan closeout before autonomous_cycle submission.   │
├─────────────────────────────────────────────────────────────────────┤
│  3. DELEGATION PROTOCOL                                              │
│     tools/supervisor/delegate_gap.py                                 │
│     When scope guard identifies an out-of-scope discovery:           │
│     - Writes to gap-ledger.json (supervisor pickup)                  │
│     - Writes to known-failure-ledger.yaml (CI logging)               │
│     - Writes delegation handoff file (wait gate input)               │
│     - Signals supervisor via autonomous_cycle                         │
│     Supervisor independently schedules the target lane sprint.       │
├─────────────────────────────────────────────────────────────────────┤
│  4. DELEGATION GATE                                                  │
│     tools/supervisor/delegation_gate.py                              │
│     Blocks any plan from proceeding past a declared wait point       │
│     until all delegated gaps from that plan are status=closed.       │
│     Plans declare: "do not cross this point until delegation done."  │
└─────────────────────────────────────────────────────────────────────┘
```

Additionally: plan locks must carry a `lane_id` so the scope guard knows which lane is active.

---

## COMPONENT 1 — LANE SCOPE REGISTRY

**File to create:** `registry/lane-scope-registry.yaml`

```yaml
# registry/lane-scope-registry.yaml
# Lane scope definitions. Enforced by scope_guard.py.
# Authoritative file — do not edit manually.

schema_version: "1.0"
last_updated: "2026-07-03"

lanes:

  - id: lane-ci-audit
    name: CI Configuration Audit
    description: >
      Repairs defects in CI workflow configuration files.
      All source, test, and governance state files are read-only.
    permitted_reads: ["**"]            # can read anything
    permitted_writes:
      - ".github/workflows/**"
      - ".gitlab-ci.yml"
      - ".pre-commit-config.yaml"
      - "pyproject.toml"              # dev/CI tooling deps only
      - "registry/known-failure-ledger.yaml"  # append: discovered failures
      - "reports/capability-layer/gap-ledger.json"  # append: delegations
      - ".local/ci-audit/**"          # delegation handoff state
      - ".local/evidences/**"         # sprint evidence
    forbidden_writes:
      - "src/**"
      - "tests/**"
      - "registry/source-structure-baseline.json"
      - "oracle/**"
      - "plans/master-plan.md"
      - "AGENTS.md"
      - "CLAUDE.md"
    on_out_of_scope_discovery:
      action: delegate
      never: fix_directly
      protocol: delegation_handoff_v1

  # F-008 FIX: All lanes include delegation write targets so any lane can invoke delegate_gap.py.
  # on_out_of_scope_discovery is an AGENT-DIRECTIVE FIELD — not consumed by scope_guard.py at
  # runtime. It tells the executing agent/plan what protocol to follow upon a reported violation.
  # scope_guard.py only reports violations; this field governs the agent's response.

  - id: lane-3-analytics-separation
    name: Python Analytics Separation
    description: Extracts analytics functions from monolithic source files.
    permitted_writes:
      - "src/python/**/{format}_analytics.py"
      - "src/python/**/__init__.py"
      - "tests/python/**"
      - "registry/source-structure-baseline.json"
      - "registry/known-failure-ledger.yaml"          # delegation: append only via delegate_gap.py
      - "reports/governance/delegation-ledger.json"   # delegation: append only via delegate_gap.py
      - ".local/evidences/**"
    forbidden_writes:
      - ".github/workflows/**"
      - "src/net/**"
    on_out_of_scope_discovery:
      action: delegate
      never: fix_directly
      protocol: delegation_handoff_v1

  - id: lane-5-dotnet-structure
    name: .NET Source Structure Healing
    description: Reduces oversized C# files to below baseline_loc_cap via partial-class extraction.
    permitted_writes:
      - "src/net/**/*.cs"
      - "tests/net/**/*.cs"
      - "registry/source-structure-baseline.json"
      - "registry/known-failure-ledger.yaml"          # delegation: append only via delegate_gap.py
      - "reports/governance/delegation-ledger.json"   # delegation: append only via delegate_gap.py
      - ".local/evidences/**"
    forbidden_writes:
      - "src/python/**"
      - ".github/workflows/**"
    on_out_of_scope_discovery:
      action: delegate
      never: fix_directly
      protocol: delegation_handoff_v1

  - id: lane-product-dotnet-api
    name: .NET Product API Deepening
    description: Implements new public API methods. REQUIRES add-dotnet-api skill.
    required_skill: add-dotnet-api
    requires_skill_transcript: true
    permitted_writes:
      - "src/net/{format}/**/*.cs"
      - "tests/net/{format}/**/*.cs"
      - "registry/format-registry.yaml"
      - "registry/known-failure-ledger.yaml"          # delegation: append only via delegate_gap.py
      - "reports/governance/delegation-ledger.json"   # delegation: append only via delegate_gap.py
      - ".local/evidences/**"
      - ".local/skill-receipts/**"
    forbidden_writes:
      - ".github/workflows/**"
      - "src/python/**"
    on_out_of_scope_discovery:
      action: delegate
      never: fix_directly
      protocol: delegation_handoff_v1

  - id: lane-product-python-api
    name: Python Product API Deepening
    description: Implements new public API methods. REQUIRES add-python-api skill.
    required_skill: add-python-api
    requires_skill_transcript: true
    permitted_writes:
      - "src/python/{format}/**/*.py"
      - "tests/python/{format}/**/*.py"
      - "registry/format-registry.yaml"
      - "registry/known-failure-ledger.yaml"          # delegation: append only via delegate_gap.py
      - "reports/governance/delegation-ledger.json"   # delegation: append only via delegate_gap.py
      - ".local/evidences/**"
      - ".local/skill-receipts/**"
    forbidden_writes:
      - ".github/workflows/**"
      - "src/net/**"
    on_out_of_scope_discovery:
      action: delegate
      never: fix_directly
      protocol: delegation_handoff_v1
```

---

## COMPONENT 2 — SCOPE GUARD

**File to create:** `tools/supervisor/scope_guard.py`

**Interface:**
```
python tools/supervisor/scope_guard.py \
  --lane <lane-id>            # explicit lane
  [--lane-from-lock]          # read lane from active-plan-lock.json
  [--changed-files f1 f2...]  # explicit file list
  [--from-git-staged]         # read from git diff --cached --name-only
  [--mode block|warn]         # block=exit 1 on violation; warn=always exit 0
  [--registry registry/lane-scope-registry.yaml]
```

**Glob matching — CRITICAL implementation note (F-002):**
`fnmatch` does NOT handle `**` as a multi-level wildcard. `fnmatch.fnmatch("src/net/csv/CsvDocument.cs", "src/**")` returns **False**. Use the following `_glob_matches()` helper instead:

```python
import fnmatch, os

def _glob_matches(path: str, pattern: str) -> bool:
    """Match path against a glob pattern supporting ** as multi-level wildcard."""
    path = path.replace('\\', '/')
    pattern = pattern.replace('\\', '/')
    if '**' not in pattern:
        return fnmatch.fnmatch(path, pattern)
    # Split on ** and validate prefix/suffix independently
    parts = pattern.split('**')
    prefix = parts[0].rstrip('/')
    suffix = parts[-1].lstrip('/')
    if prefix and not (path.startswith(prefix + '/') or path == prefix):
        return False
    if suffix and not (path.endswith('/' + suffix) or path == suffix):
        return False
    return True
```

**Behavior:**
1. Load `lane-scope-registry.yaml`
2. Find the lane entry matching `--lane` or `--lane-from-lock`
3. For each changed file: test against `permitted_writes` globs using `_glob_matches()`, then `forbidden_writes` globs
4. A file is PERMITTED if it matches any `permitted_writes` glob and no `forbidden_writes` glob
5. A file is FORBIDDEN if it matches any `forbidden_writes` glob (regardless of permitted_writes)
6. A file is UNRECOGNIZED if it matches no glob in either list → WARN only (never block)
7. For `requires_skill_transcript: true` lanes: additionally check `.local/skill-receipts/` for a receipt matching the changed format
8. In `block` mode: exit 1 if any FORBIDDEN files found; exit 0 if clean
9. In `warn` mode: always exit 0; print violations to stderr
10. `on_out_of_scope_discovery` in the registry is an **agent-directive field** — it tells the agent/plan what protocol to follow when a violation is reported. It is NOT read by scope_guard.py at runtime. scope_guard.py only reports; the agent decides what to do.

**Output format (machine-readable JSON to stdout):**
```json
{
  "lane": "lane-ci-audit",
  "verdict": "VIOLATION",
  "violations": [
    {
      "file": "src/net/csv/CsvDocument.cs",
      "rule": "src/**",
      "rule_type": "forbidden_writes",
      "action": "delegate or revert"
    }
  ],
  "permitted": ["github/workflows/ci.yml"],
  "unrecognized": []
}
```

**Tests required** (`tests/tools/test_scope_guard.py`):
- Clean commit within lane → exit 0, no violations
- Forbidden write → exit 1 in block mode, exit 0 in warn mode
- Missing lane ID → exit 2 (configuration error)
- No plan lock when using --lane-from-lock → defaults to warn mode, exit 0
- Skill transcript required but missing → violation reported
- Glob wildcard matching: `src/**` catches `src/net/csv/CsvDocument.cs`

---

## COMPONENT 3 — DELEGATION PROTOCOL

**File to create:** `tools/supervisor/delegate_gap.py`

This tool is called by a plan agent when scope_guard reports a violation or when a pre-existing failure is discovered that belongs to a different lane.

> **F-001 HEALED:** The original design wrote delegation data into `reports/capability-layer/gap-ledger.json`. That file has an incompatible schema: `owning_lane` is an integer (1/2/3), not a string lane ID, and fields like `target_lane`, `discovered_by`, `plan_id`, `file` do not exist. Delegation data MUST go to a separate store: `reports/governance/delegation-ledger.json`.

**Interface:**
```
python tools/supervisor/delegate_gap.py \
  --gap-id GAP-LANE5-001 \
  --target-lane lane-5-dotnet-structure \
  --file src/net/fods/FodsDocumentAccessor.cs \
  --description "Exceeds baseline_loc_cap by 650 LOC" \
  --severity P1 \
  --ci-job governance-check \           # optional: which CI job surfaced this
  --discovered-by lane-ci-audit \
  --plan-id sequential-twirling-sunrise \
  [--blocks-progression true]
```

**What it writes atomically (all three or none — use temp file + os.replace()):**

1. **`reports/governance/delegation-ledger.json`** — appends to `delegations[]` array (separate from product gap-ledger):
```json
{
  "schema_version": "1.0",
  "delegations": [
    {
      "gap_id": "GAP-LANE5-001",
      "target_lane": "lane-5-dotnet-structure",
      "file": "src/net/fods/FodsDocumentAccessor.cs",
      "description": "Exceeds baseline_loc_cap by 650 LOC",
      "severity": "P1",
      "discovered_by": "lane-ci-audit",
      "plan_id": "sequential-twirling-sunrise",
      "discovered_at": "2026-07-03T10:00:00Z",
      "status": "open",
      "do_not_fix_in": "lane-ci-audit"
    }
  ]
}
```

2. **`registry/known-failure-ledger.yaml`** — appends (CI visibility — all lanes may write here via delegate_gap.py):
```yaml
- gap_id: GAP-LANE5-001
  reason: "FodsDocumentAccessor.cs exceeds baseline_loc_cap by 650 LOC. Pre-existing architecture debt."
  owning_lane: lane-5-dotnet-structure
  discovered_by: lane-ci-audit
  discovered_at: 2026-07-03
  category: pre_existing_architecture_debt
  do_not_fix_in: lane-ci-audit
  status: open
```

3. **`.local/ci-audit/delegation-handoff-<plan_id>.yaml`** — creates/updates (plan-local wait state):
```yaml
plan_id: sequential-twirling-sunrise
delegations:
  - gap_id: GAP-LANE5-001
    target_lane: lane-5-dotnet-structure
    status: pending
overall_status: pending
```

**Supervisor pickup:** The supervisor reads `reports/governance/delegation-ledger.json` during `autonomous_cycle.py`. Delegation entries with `status: open` are converted to `next-work-items.json` entries assigned to `target_lane`. The supervisor schedules the lane sprint independently. When the lane sprint closes, it sets the delegation entry to `status: closed`.

**Supervisor does NOT need to be explicitly triggered** — it picks up open delegations on the next cycle naturally. The delegating plan just waits for the delegation to close.

---

## COMPONENT 4 — DELEGATION GATE

**File to create:** `tools/supervisor/delegation_gate.py`

A plan calls this before proceeding past any step that depends on delegated work being complete.

**Interface:**
```
python tools/supervisor/delegation_gate.py \
  --plan-id sequential-twirling-sunrise \
  [--gap-ids GAP-LANE5-001 GAP-LANE5-002 ...]  # if not provided: check all from plan
  [--ledger reports/governance/delegation-ledger.json]  # default path
```

**Behavior:**
1. Read `reports/governance/delegation-ledger.json` (NOT `gap-ledger.json` — separate file per F-001 fix)
2. Filter entries where `plan_id == <plan-id>` (or intersection with `--gap-ids`)
3. If any `status != closed`: exit 1, print pending gaps
4. If all `status == closed` (or no gaps registered): exit 0

**Exit codes:**
- 0 = GATE OPEN — all delegations resolved, proceed
- 1 = GATE CLOSED — delegations pending, wait
- 2 = NO DELEGATIONS FOUND — plan registered no gaps (open = proceed, warn)

**Usage in a plan taskcard:**
```
Before Step N: Run delegation_gate.py --plan-id <id>
If exit 1: STOP. Do not proceed. Supervisor has not completed delegated work yet.
If exit 0: Proceed to Step N.
```

This is the "wait for supervisor" primitive. No polling loop needed — just run before each gate point.

---

## COMPONENT 5 — PLAN LOCK LANE ID EXTENSION

**File to modify:** `tools/supervisor/write_plan_lock.py`

Plan files must declare their lane in a standard header field so `scope_guard.py --lane-from-lock` works.

**Plan file convention (add to all plan headers):**
```markdown
# Plan Title
# lane: lane-ci-audit
```
or as YAML front matter:
```yaml
---
lane_id: lane-ci-audit
plan_id: sequential-twirling-sunrise
---
```

**write_plan_lock.py change:**
- Parse `lane_id` from plan file header (regex: `^# lane:\s*(\S+)` or YAML front matter)
- Write `lane_id` to `.local/supervisor/active-plan-lock.json` alongside existing fields
- If no lane_id found: write `lane_id: unknown`; scope_guard defaults to warn mode

---

## TASKCARDS

| ID | Taskcard | Status | Priority | Depends On |
|----|----------|--------|----------|-----------|
| TC-LSG-001 | Create lane-scope-registry.yaml | CLOSED | CRITICAL | — |
| TC-LSG-002 | Implement scope_guard.py + tests | CLOSED | CRITICAL | TC-LSG-001 |
| TC-LSG-003 | Extend write_plan_lock.py with lane_id | CLOSED | HIGH | TC-LSG-001 |
| TC-LSG-004 | Add scope-guard pre-commit hook (warn mode) | CLOSED | HIGH | TC-LSG-002, TC-LSG-003 |
| TC-LSG-005 | Implement delegate_gap.py | CLOSED | HIGH | TC-LSG-001 |
| TC-LSG-006 | Implement delegation_gate.py | CLOSED | HIGH | TC-LSG-005 |
| TC-LSG-007 | Add scope_guard to plan closeout | CLOSED | MEDIUM | TC-LSG-002 |
| TC-LSG-008 | Write lane-separation-protocol.md | CLOSED | MEDIUM | TC-LSG-001..006 |
| TC-LSG-009 | Upgrade scope-guard hook from warn→block | backlog | MEDIUM | TC-LSG-004 (stable >=3 sprints) |

---

### TC-LSG-001 — Lane Scope Registry
**Owner:** governance-machinery-agent
**Objective:** Create `registry/lane-scope-registry.yaml` with scope definitions for all active lanes.
**Files:** `registry/lane-scope-registry.yaml` (new)
**Steps:**
1. Create the file with the schema from Component 1 above (use the healed version including F-008 fixes)
2. Initial entries: lane-ci-audit, lane-3-analytics-separation, lane-5-dotnet-structure, lane-product-dotnet-api, lane-product-python-api
3. Verify: `python -c "import yaml; d=yaml.safe_load(open('registry/lane-scope-registry.yaml')); assert len(d['lanes'])==5"`
4. Add remaining lanes from `plans/strategic/spec-to-feature-radical-correction-plan.md` in a subsequent pass
**Acceptance:** `python -c "import yaml; yaml.safe_load(open('registry/lane-scope-registry.yaml'))"` exits 0; all 5 initial lanes present; `delegation-ledger.json` and `known-failure-ledger.yaml` in permitted_writes of all 5 lanes
**Rollback:** `git rm registry/lane-scope-registry.yaml` — no other file modified

---

### TC-LSG-002 — Scope Guard Implementation
**Owner:** governance-machinery-agent
**Objective:** Implement `tools/supervisor/scope_guard.py` + `tests/tools/test_scope_guard.py`
**Files:** `tools/supervisor/scope_guard.py` (new), `tests/tools/test_scope_guard.py` (new)
**Steps:**
1. Implement scope_guard.py per the interface and behavior specified in Component 2
2. **CRITICAL (F-002):** Use `_glob_matches()` helper from Component 2 — NOT bare `fnmatch`. `fnmatch` returns False for `"src/net/csv/CsvDocument.cs"` against `"src/**"`. Verify this explicitly in tests.
3. Write tests covering all cases listed in Component 2 including the `**` wildcard case
4. Run tests: `.venv/Scripts/pytest tests/tools/test_scope_guard.py -v`
5. Verify acceptance command manually: `python tools/supervisor/scope_guard.py --lane lane-ci-audit --changed-files src/net/csv/CsvDocument.cs --mode block --registry registry/lane-scope-registry.yaml`
**Acceptance:**
- All tests pass
- `scope_guard.py --lane lane-ci-audit --changed-files src/net/csv/CsvDocument.cs --mode block` exits 1
- `scope_guard.py --lane lane-ci-audit --changed-files .github/workflows/ci.yml --mode block` exits 0
- Explicit test: `_glob_matches("src/net/csv/CsvDocument.cs", "src/**")` returns True (not False as fnmatch would)
**Rollback:** `git rm tools/supervisor/scope_guard.py tests/tools/test_scope_guard.py`

---

### TC-LSG-003 — Plan Lock Lane ID Extension
**Owner:** governance-machinery-agent
**Objective:** Extend `write_plan_lock.py` to parse and write `lane_id` from plan file headers
**Files:** `tools/supervisor/write_plan_lock.py` (modify)
**Steps:**
1. Add plan file parser: read first 20 lines, look for `# lane: <id>` (regex: `^# lane:\s*(\S+)`) or `lane_id: <id>` in YAML front matter
2. Write `lane_id` field to BOTH lock files (session-keyed lock AND `active-plan-lock.json`)
3. If not found: write `"lane_id": "unknown"`; scope_guard defaults to warn mode for unknown lanes
**Acceptance:**
- Plan file with `# lane: lane-ci-audit` header → `active-plan-lock.json` contains `"lane_id": "lane-ci-audit"`
- Plan file with no lane header → `active-plan-lock.json` contains `"lane_id": "unknown"`
**Rollback:** `git checkout tools/supervisor/write_plan_lock.py` — reverts to prior version; scope_guard falls back to warn mode (safe)

---

### TC-LSG-004 — Pre-Commit Hook Integration (warn mode)
**Owner:** governance-machinery-agent
**Objective:** Add scope-guard as a pre-commit hook in `warn` mode. Block mode is handled by TC-LSG-009 after stability.
**Files:** `.pre-commit-config.yaml` (modify)
**Steps:**
1. Add to the existing `- repo: local` block in `.pre-commit-config.yaml`:
   ```yaml
       - id: scope-guard
         name: Lane scope guard (warn mode — violations print to stderr, never block commit)
         language: system
         entry: python tools/supervisor/scope_guard.py --from-git-staged --lane-from-lock --mode warn
         pass_filenames: false
         always_run: false
         stages: [pre-commit]
   ```
   **CRITICAL (F-003):** `stages: [pre-commit]` is REQUIRED — all existing hooks have it. Without it the hook does not run. Also note: add this inside the existing `- repo: local` section (do not create a duplicate repo block).
2. Initial mode: `warn` (always exit 0, prints violations to stderr for awareness)
3. Upgrade to block is tracked in TC-LSG-009 — NOT in this taskcard
**Acceptance:**
- `pre-commit run scope-guard` runs without error (exit 0 in warn mode even with violations)
- When a `src/net/*.cs` file is staged under lane-ci-audit: stderr shows a scope warning
- `pre-commit run --all-files` does not fail due to scope-guard (warn mode)
**Rollback:** Remove the `scope-guard` hook entry from `.pre-commit-config.yaml`; `git checkout .pre-commit-config.yaml`

---

### TC-LSG-005 — Delegation Protocol CLI
**Owner:** governance-machinery-agent
**Objective:** Implement `tools/supervisor/delegate_gap.py`
**Files:** `tools/supervisor/delegate_gap.py` (new)
**Steps:**
1. Implement per Component 3 healed interface and behavior
2. **CRITICAL (F-001):** Write delegation data to `reports/governance/delegation-ledger.json` — NOT to `reports/capability-layer/gap-ledger.json`. The product gap-ledger has an incompatible schema.
3. Create `reports/governance/` directory if it does not exist
4. Initialize `delegation-ledger.json` with `{"schema_version": "1.0", "delegations": []}` if file does not exist
5. Must be atomic: use temp file + `os.replace()` (NOT `os.rename()` — Windows raises FileExistsError on existing target)
6. Read existing `delegation-ledger.json` and `known-failure-ledger.yaml` to avoid duplicate gap IDs (idempotency)
7. Validate `--target-lane` exists in `lane-scope-registry.yaml` before writing
**Acceptance:**
- Running the command creates/appends to `reports/governance/delegation-ledger.json` with correct schema
- Does NOT modify `reports/capability-layer/gap-ledger.json`
- Re-running with same gap-id is idempotent (no duplicate entry in delegation-ledger.json)
- Invalid target-lane exits 2 with descriptive error
- `os.replace()` used (not `os.rename()`) for Windows atomicity
**Rollback:** `rm reports/governance/delegation-ledger.json`; `git checkout tools/supervisor/delegate_gap.py`

---

### TC-LSG-006 — Delegation Gate
**Owner:** governance-machinery-agent
**Objective:** Implement `tools/supervisor/delegation_gate.py`
**Files:** `tools/supervisor/delegation_gate.py` (new)
**Steps:**
1. Implement per Component 4 healed interface
2. Read from `reports/governance/delegation-ledger.json` (NOT `gap-ledger.json` — see F-001)
3. If `delegation-ledger.json` does not exist: exit 2 (no delegations registered)
4. Exit 0 = gate open (all closed), exit 1 = gate blocked (pending delegations), exit 2 = no delegations
**Acceptance:**
- With no `delegation-ledger.json`: exits 2
- With an open delegation for plan-id: exits 1 with gap list printed to stdout
- After delegation status set to `closed` via Python one-liner: exits 0
- Verify with one-liner: `python -c "import json,pathlib; p=pathlib.Path('reports/governance/delegation-ledger.json'); d=json.loads(p.read_text()); [g.update({'status':'closed'}) for g in d['delegations'] if g['gap_id']=='GAP-TEST-001']; p.write_text(json.dumps(d,indent=2))"`
**Rollback:** `git rm tools/supervisor/delegation_gate.py`

---

### TC-LSG-007 — Scope Guard at Plan Closeout
**Owner:** governance-machinery-agent
**Objective:** Add scope_guard check to `tools/supervisor/sprint_executor_validate.py` so any plan closeout that includes forbidden-write files is flagged before the declaration reaches the supervisor
**Files:** `tools/supervisor/sprint_executor_validate.py` (modify)
**Steps:**
1. In the validation pipeline, after checking changed_files for schema validity (existing Phase sequence):
2. Add new Phase: import `scope_guard` module (or subprocess call), run against `declaration.changed_files`
3. Read `lane_id` from active plan lock (`active-plan-lock.json`) — if unknown or missing, skip with WARN
4. If violations found: add `WARN` items to validator output (NOT `FAIL` — closeout must never block per Supreme Directive)
5. Violations must appear in the evidence review output for human visibility
**Acceptance:**
- A declaration with `src/net/csv/CsvDocument.cs` in `changed_files` under `lane-ci-audit` → validator output contains a scope WARN for that file
- The validator still exits 0 on scope violations (WARN not FAIL)
- A declaration with no lane_id in lock → scope check skipped, WARN logged
**Rollback:** `git checkout tools/supervisor/sprint_executor_validate.py`

---

### TC-LSG-008 — Protocol Documentation
**Owner:** governance-machinery-agent
**Objective:** Write `docs/governance/lane-separation-protocol.md` as the canonical reference
**Files:** `docs/governance/lane-separation-protocol.md` (new)
**Content:**
1. The governance flaw this addresses (with the CI audit as worked example)
2. The four components and how they interact (include the F-001 warning: delegation-ledger ≠ gap-ledger)
3. The triage decision tree (in-scope vs out-of-scope discovery)
4. The 5-step delegation protocol with exact CLI commands
5. The delegation gate usage pattern including the Python one-liner for closing gaps (F-009 fix)
6. The scope guard escalation path (warn → block) — reference TC-LSG-009
7. How the supervisor naturally picks up delegated gaps via `reports/governance/delegation-ledger.json`
8. Lane scope registry format, `on_out_of_scope_discovery` as agent-directive field (not scope_guard input)
9. How to add new lanes
**Rollback:** `git rm docs/governance/lane-separation-protocol.md` — documentation only, no functional impact

---

### TC-LSG-009 — Upgrade Scope Guard Hook: warn→block
**Owner:** governance-machinery-agent
**Objective:** Upgrade the scope-guard pre-commit hook from warn mode to block mode after stability is confirmed
**Files:** `.pre-commit-config.yaml` (modify)
**Prerequisite:** TC-LSG-004 must have been running in warn mode for ≥3 autonomous sprints with zero false-positives (UNRECOGNIZED files that were erroneously flagged as FORBIDDEN)
**Steps:**
1. Confirm ≥3 sprint evidence files exist that show scope-guard ran in warn mode with no false FORBIDDEN hits
2. Change `--mode warn` to `--mode block` in the hook entry
3. Test: stage a file that IS in a forbidden path → confirm pre-commit blocks the commit
4. Test: stage a file that IS permitted → confirm pre-commit passes
**Acceptance:**
- `pre-commit run scope-guard` with a staged `src/net/*.cs` under lane-ci-audit → exit 1 (commit blocked)
- `pre-commit run scope-guard` with a staged `.github/workflows/ci.yml` under lane-ci-audit → exit 0
**Rollback:** Revert `--mode block` to `--mode warn` in `.pre-commit-config.yaml`

---

## SCOPE BOUNDARY OF THIS PLAN

```
MAY CREATE:
  registry/lane-scope-registry.yaml
  tools/supervisor/scope_guard.py
  tools/supervisor/delegate_gap.py
  tools/supervisor/delegation_gate.py
  tests/tools/test_scope_guard.py
  docs/governance/lane-separation-protocol.md
  reports/governance/delegation-ledger.json    ← NEW (F-001: separate from gap-ledger.json)
  .local/evidences/**

MAY MODIFY:
  tools/supervisor/write_plan_lock.py
  tools/supervisor/sprint_executor_validate.py
  .pre-commit-config.yaml
  registry/known-failure-ledger.yaml           ← append-only (delegation records)

MUST NOT TOUCH:
  src/**
  tests/python/**, tests/net/**  (except tests/tools/ — new governance tests)
  registry/source-structure-baseline.json
  reports/capability-layer/gap-ledger.json     ← product gap-ledger; incompatible schema
  oracle/**
  .github/workflows/**
  .gitlab-ci.yml
```

---

## VERIFICATION

After all taskcards complete, run the full scenario test:

```bash
# 1. Simulate a CI audit plan touching src/ (expect VIOLATION)
python tools/supervisor/scope_guard.py \
  --lane lane-ci-audit \
  --changed-files src/net/csv/CsvDocument.cs .github/workflows/ci.yml \
  --mode block \
  --registry registry/lane-scope-registry.yaml
# Expected: exit 1, violation for CsvDocument.cs, permitted for ci.yml

# 2. Verify ** glob matching works correctly (F-002 regression test)
python -c "
import sys; sys.path.insert(0, 'tools/supervisor')
from scope_guard import _glob_matches
assert _glob_matches('src/net/csv/CsvDocument.cs', 'src/**') == True, 'F-002: ** glob broken'
assert _glob_matches('.github/workflows/ci.yml', '.github/workflows/**') == True
assert _glob_matches('src/net/csv/CsvDocument.cs', 'tests/**') == False
print('PASS: glob matching correct')
"

# 3. Simulate delegation of a discovered gap
python tools/supervisor/delegate_gap.py \
  --gap-id GAP-TEST-001 \
  --target-lane lane-5-dotnet-structure \
  --file src/net/fods/FodsDocumentAccessor.cs \
  --description "Test gap" \
  --severity P2 \
  --discovered-by lane-ci-audit \
  --plan-id sequential-twirling-sunrise
# Expected: exit 0, gap written to reports/governance/delegation-ledger.json
# Verify: reports/capability-layer/gap-ledger.json UNCHANGED

python -c "
import json; d=json.load(open('reports/governance/delegation-ledger.json'))
assert any(g['gap_id']=='GAP-TEST-001' for g in d['delegations']), 'delegation not written'
orig=json.load(open('reports/capability-layer/gap-ledger.json'))
assert all('GAP-TEST-001' not in str(g) for g in orig.get('gaps',[])), 'F-001 violated: gap in product ledger'
print('PASS: delegation written to correct file, product ledger untouched')
"

# 4. Gate check while delegation is pending
python tools/supervisor/delegation_gate.py --plan-id sequential-twirling-sunrise
# Expected: exit 1, shows GAP-TEST-001 as pending

# 5. Simulate supervisor closing the gap (F-009 fix: Python one-liner replaces "manually set to closed")
python -c "
import json; from pathlib import Path
p = Path('reports/governance/delegation-ledger.json')
d = json.loads(p.read_text())
for g in d['delegations']:
    if g['gap_id'] == 'GAP-TEST-001':
        g['status'] = 'closed'
p.write_text(json.dumps(d, indent=2))
print('Gap GAP-TEST-001 closed')
"

# 6. Gate check after closing — expect GATE OPEN
python tools/supervisor/delegation_gate.py --plan-id sequential-twirling-sunrise
# Expected: exit 0, gate open
```

---

## EXECUTION READINESS

**VERDICT: READY FOR EXECUTION (v5 — post-forensic-healing)**

- All 9 taskcards are fully specified: files, interface, behavior, acceptance criteria, owner, rollback
- 9 forensic findings (F-001..F-009) recorded and healed in this version
- No user decisions required
- Scope boundary is explicit, delegation-ledger is separate from product gap-ledger (F-001 healed)
- Glob matching implementation specified explicitly with `_glob_matches()` (F-002 healed)
- Pre-commit hook format corrected with `stages: [pre-commit]` (F-003 healed)
- Rollback procedures on every taskcard (F-004 healed)
- warn→block upgrade tracked in TC-LSG-009 (F-005 healed)
- Owner field on every taskcard (F-006 healed)
- `on_out_of_scope_discovery` documented as agent-directive, not scope_guard input (F-007 healed)
- `known-failure-ledger.yaml` in permitted_writes of all lanes (F-008 healed)
- Gap closure verification uses Python one-liner (F-009 healed)
- No CI job monitoring, no CI retry, no push operations — pure governance machinery

**Execution order:** TC-LSG-001 → [TC-LSG-002, TC-LSG-003, TC-LSG-005, TC-LSG-006 in parallel] → TC-LSG-004 → TC-LSG-007 → TC-LSG-008 → TC-LSG-009 (deferred: after ≥3 stable sprints)


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-03T10:57:51.059394+00:00"
  locked_by: "af3d4a5638a5"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
