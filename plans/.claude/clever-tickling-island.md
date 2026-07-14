# Canary Control — Production-Grade Design
**Mission:** `clever-tickling-island`
**Revision:** 3 (micro-taskcardized — supersedes revision 2)
**Plan authority:** This file is the sole execution authority.
**Supporting artifacts:** Produced during execution at `reports/canary/taskcardization/` — see §Execution Artifacts.

---

## Preflight Record

```
repository:   c:\Users\prora\OneDrive\Documents\GitHub\format-factory
branch:       main
HEAD:         af879e55
active plan:  C:\Users\prora\.claude\plans\clever-tickling-island.md
plan title:   Canary Control — Production-Grade Design
plan format:  markdown with embedded taskcard execution layer
major sections: 14 (diagnostic, preservation, redesign, design, impl, validation, tests, regression,
                   tradeoffs, deferred, requirement registry, execution control, state machine,
                   evidence contract, handoff)
existing tasks before this revision: 0 (plan had actionable prose, no taskcards)
duplicate plan risk: NONE (single plan file, no competing versions found)
expected_count in governance_validator_runner.py: 167 (V149 added 2026-07-09; plan previously
                                                         cited 165 — corrected in §Regression Controls)
governance_validator_runner.py role: LIBRARY (not CLI) — called by autonomous_cycle.py
tools/canary/ directory: DOES NOT EXIST — must be created
tests/canary/ directory: DOES NOT EXIST — must be created
.supervisor/validator-shadow-registry.yaml: DOES NOT EXIST — must be created
```

---

## Diagnostic: Symptoms, Root Causes, and Structural Weaknesses

### What the first analysis got wrong

The first plan proposed a 7-table SQLite state machine with its own lifecycle, 12 pilots, and a vertical slice around oracle D0→D1 promotion. All of this was based on a surface reading of the prompt rather than a close reading of how the system actually executes.

After reading the key files in detail, the situation is materially different.

---

### What does NOT need canary control

**Oracle D0→D1 promotion is already naturally per-format isolated.**
Each format has its own `oracle/formats/{format_id}/oracle-package.yaml`. Adding `expected_model_properties` to FODS's file does not touch any other format. `execute_oracle.py --format fods` runs only FODS cases and writes only to `.local/oracle/fods/`. There is no "portfolio-wide oracle execution" problem to solve. Re-running after a change produces the same outcome (PASS/FAIL, depth level) because oracle output is deterministic given unchanged product code. The waves described in `oracle-backfill-wave6.md` are scheduling descriptions, not a correctness problem.

**Gap ledger compilation is deterministic and already filter-capable.**
`capability_feature_compiler.py` is a pure function over `gap-ledger.json`. Same input → identical output. It already supports `--format-filter`. The problem is not unstable output; the problem is that work selection is not cohort-aware. But this is a scheduling problem, not a correctness problem. A canary does not fix it.

**Per-format gate execution is already isolated.**
`gate_executor.py` is called per format and writes per-format phase locks to `.local/supervisor/phase-locks/{format_id}.json`. Each format gates independently.

**Most other operations are already naturally scoped.** SAL ingestion is per-format. QName migrations have `validate_migration_safe.py` and `qname_migration_planner.py` as pre-flight controls. The conveyor matrix already assigns formats to cohorts A/B/C/D.

---

### What actually breaks consistency and is genuinely dangerous

**1. Governance validator blocking promotion has a portfolio-wide blast radius with no staged path.** `[REQ-DIAG-001]`

The 165 validators are code — a change to `blocks_sprint = True` in any validator immediately makes every sprint for every format subject to that rule. There is no mechanism to test a new blocking rule against FODS declarations for 3 sprints before applying it to all 20 formats. The history is visible in `failure-memory.json`: FM-0004 (164 occurrences) and FM-0005 (129 occurrences) show that validator-level blocking failures recur and are resolved by adding grace-aware exemptions, not by staged promotion. The exemptions accumulate and become hard to reason about.

**This is the largest real blast-radius problem in the system.** A single `blocks_sprint` flip blocks the autonomous loop for every format until the root cause is fixed.

**2. LLM grader provider switches have no shadow comparison.** `[REQ-DIAG-002]`

`grade_declared_work.py` calls one LLM provider per work item. The grade cache uses a 7-day TTL keyed by evidence content fingerprint. If the provider is switched (e.g., from GPT_OSS to a new model), all cached grades are immediately stale by provider, but the cache key doesn't include the provider. New grades come from a different model, and there is no record of how the new model's verdicts compare to the old model's verdicts on the same evidence. A model switch that causes ACCEPTED → REWORK on 30% of previously passing items will silently re-trigger rework items, and the failure won't be traceable to the provider change.

**3. Gap ledger priority recompilation changes work-selection order for all formats simultaneously.** `[REQ-DIAG-003]`

When the scoring function in `capability_feature_compiler.py` changes (e.g., the starvation penalty, the priority floor, or the deepening lane classification), work selection changes portfolio-wide for the next sprint. There is no way to say "show me what work-item ordering would change under this new algorithm before committing to it." The gap ledger is 33MB with 1277 gaps. Bugs in the scoring function are invisible until work starts going to wrong formats.

---

### Structural weaknesses (distinct from symptoms)

**Sprint is too coarse as a rollback unit.** A sprint can bundle work across FODS, CSV, ODS. When V13 (monolith detection) blocks the sprint, all of it is treated as rework regardless of which format triggered the violation. This makes the blast radius of a single validation failure extend across unrelated work. `[REQ-STRUC-001]`

**The SQLite control index is a read-only shadow.** It was designed not to own state. Any canary system that puts decision state in SQLite is working against the grain of the architecture. Files are authoritative; SQLite tracks them. This is the right model, but it means canary state (which IS decision state) needs careful placement: it either lives in YAML/JSON files (file-authoritative) with SQLite tracking it, or it is transient and not durable. `[REQ-STRUC-002]`

**Validator grace-aware exemptions are a workaround, not a solution.** FM-0004 and FM-0005 were resolved by adding exemptions for TEST items instead of fixing the root cause. These exemptions accumulate and make the validator behavior harder to predict. The real fix is a mechanism for running validators in a non-blocking shadow mode before promoting them to blocking. `[REQ-STRUC-003]`

**The existing wave/batch plans (markdown) are not machine-enforceable.** `oracle-backfill-wave6.md` defines batch cohorts but nothing in code checks that execution respects batch boundaries. A sprint can execute oracle for any format regardless of wave assignment. This is a governance gap but not a canary problem — it is a discipline problem solved by scheduling controls, not a parallel execution problem. `[REQ-STRUC-004]`

---

## What Must Be Preserved

- **File authority model.** JSON/YAML files are ground truth. SQLite is a shadow index. This must not change. `[REQ-PRES-001]`
- **Sprint lifecycle.** Continuation signal, plan locks, evidence declaration, and grading pipeline work correctly and have been tested at scale (~3199 sprints indexed). `[REQ-PRES-002]`
- **Oracle per-format isolation.** Already correct. Do not add complexity. `[REQ-PRES-003]`
- **165 validators as the correctness gate.** The validators are the real quality layer. Canary should extend their reach, not weaken them. Validator count is 167 as of 2026-07-09 (V149 added). `[REQ-PRES-004]`
- **Grade cache (7-day TTL, evidence-content keyed).** Well-designed. The problem is not the cache; it is the missing shadow comparison for provider switches. `[REQ-PRES-005]`
- **Phase locks and authority gate validation.** Per-format, well-isolated, already correct. `[REQ-PRES-006]`
- **`execute_oracle.py` as-is.** 1428 LOC, mature, all 20 formats verified. Do not modify it. `[REQ-PRES-007]`

---

## What Must Be Redesigned

**Only three things genuinely require canary control:** `[REQ-RDSGN-001, REQ-RDSGN-002, REQ-RDSGN-003]`

1. **Governance validator blocking scope** — needs per-format-scope shadow mode before global promotion
2. **LLM grader provider/model switches** — needs shadow comparison against stable provider on same evidence
3. **Gap compilation priority algorithm changes** — needs dry-run comparison before committing new scoring

Everything else is either already isolated, already gated, or not a canary problem.

---

## Proposed Design

### Core principle

Canary in this system means: **a global-scope change runs in shadow observation mode for a bounded scope before it becomes authoritative.** It does NOT mean a parallel execution framework. It does NOT mean a new lifecycle alongside the existing sprint loop. It extends the existing sprint loop with a shadow observation layer.

The three components are:
1. A **validator shadow registry** — YAML config file; `governance_validator_runner.py` reads it to determine per-validator, per-format scope
2. A **grader shadow log** — `grade_declared_work.py` optionally runs a second provider call and logs the comparison
3. A **compilation diff tool** — pure function comparing old vs new gap compilation output before writing

SQLite owns exactly **two new tables**: `validator_shadow_observations` and `grader_shadow_observations`. These are write-once observation logs, not control state. Files (the shadow registry YAML and grader config) remain authoritative.

### Design clarification: format_scope in V1

V1 shadow registry supports only `format_scope: ["*"]` (all formats in shadow mode for that validator). Per-format scoping (e.g., `["fods", "csv"]`) would require extracting the primary format from the declaration's work items — feasible but adds complexity. V1 uses wildcard scope only; per-format scope is a V2 extension listed in Deferred Work.

---

### Component 1: Validator Shadow Registry

**File:** `.supervisor/validator-shadow-registry.yaml` (does not yet exist; initial state is empty list)

```yaml
# Governs per-validator enforcement scope.
# Modes: advisory (never blocks), shadow (runs but logs to shadow, does not block),
#        blocking (full enforcement — the normal mode).
# When no entry exists for a validator, defaults to 'blocking'.
# format_scope: ["*"] means all formats in that mode (V1 only supports ["*"]).
# shadow_promotion_threshold: int — min observed sprints before promotion is safe.
validator_shadow_entries: []
```

**Modified file:** `tools/supervisor/governance_validator_runner.py`

`governance_validator_runner.py` is a **library**, not a CLI. It exposes:
```python
def run_all_governance_validators(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict
```
The function returns a dict with key `"blocks_sprint": bool` (line ~800:
`blocks_sprint = any(r.get("blocks_sprint") for r in results if r["result"] == "FAIL")`).

Changes (surgical, ~40 LOC, insert before line 800 aggregation):
- Add constant: `SHADOW_REGISTRY_PATH` pointing to `.supervisor/validator-shadow-registry.yaml`
- Add helper: `_load_shadow_registry() -> dict` — loads YAML, returns `{}` if file missing or parse error (fail-safe)
- Add helper: `_write_shadow_log_entry(entry: dict) -> None` — appends JSON line to `.local/supervisor/validator-shadow-log.jsonl`
- In `run_all_governance_validators()`: load registry once at function entry
- After each validator result is appended to `results`: check if `validator_id` is in shadow registry
- If shadow match: neutralize by setting `result["blocks_sprint"] = False` on that result dict entry; write shadow log entry; accumulate into `shadow_suppressions` list
- Add `"shadow_suppressions": shadow_suppressions` to return dict (observability only)
- The existing `blocks_sprint = any(...)` aggregation at ~line 800 then naturally sees `False` for shadow validators

Shadow log entry format:
```json
{"ts": "ISO8601", "sprint_id": "...", "validator_id": "...", "result": "FAIL",
 "would_have_blocked": true, "finding_count": 2, "mode": "shadow"}
```

**Promotion path:**
```bash
python tools/canary/validator_promotion.py shadow \
  --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM --threshold 5
python tools/canary/validator_promotion.py status \
  --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
# Output: "5/5 sprints observed. 3/5 would have blocked. Threshold: 5. Safe to promote."
python tools/canary/validator_promotion.py promote \
  --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
python tools/canary/validator_promotion.py demote \
  --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
```

**Why this is the right design:**
- The file (`.supervisor/validator-shadow-registry.yaml`) is authoritative. SQLite tracks it.
- The sprint lifecycle is unchanged. Shadow observations are a side effect, not a control.
- A validator in shadow mode still runs — its output is visible in the shadow log. The only difference is it doesn't block the sprint.
- Promotion is explicit and auditable (edit + commit of the registry file).
- Rollback is trivial: edit the registry file back.
- This directly fixes FM-0004 and FM-0005: instead of adding grace-aware exemptions after the fact, you can shadow-test a new blocking rule before it fires.

---

### Component 2: Grader Shadow Mode

**Modified file:** `tools/supervisor/grade_declared_work.py`

Current CLI args (line ~1108): `--inspection`, `--declaration`, `--output-dir`
Current LLM client construction: lines 302–314
Current cache path (line 40): `.local/supervisor/grade-cache.json`

Changes (~60 LOC):
- New CLI flag at line 1108: `--shadow-provider <provider_id>` (reads from `tools/llm/endpoints.yaml`; optional, default `""`)
- New flag: `--sprint-id <id>` (passed for shadow log correlation; optional)
- Pass `shadow_provider` and `sprint_id` through `grade_all()` signature to grading loop
- When `shadow_provider` is non-empty: after grading each work item with stable provider, construct second LLM client for shadow provider and grade same item
- Shadow grade NEVER affects sprint verdict — only stable grade does
- Write comparison to `.local/supervisor/grader-shadow-log.jsonl`:
  ```json
  {"ts": "ISO8601", "item_id": "...", "sprint_id": "...", "stable_provider": "gpt-4o",
   "stable_grade": "ACCEPTED_VERIFIED", "shadow_provider": "claude-3-5-sonnet",
   "shadow_grade": "ACCEPTED_VERIFIED", "agreement": true}
  ```
- If shadow provider call fails (timeout, network, auth): log failure as `{"agreement": null, "error": "..."}`, continue with stable grade (non-blocking)
- Shadow cache key: `{item_id}:{evidence_hash}:shadow:{provider_id}` stored in `.local/supervisor/grader-shadow-cache.json`

**Why not cache-keyed by provider:** The existing cache key is `{item_id}:{evidence_hash}`. The shadow cache uses `{item_id}:{evidence_hash}:shadow:{provider_id}`. This prevents cross-contamination while sharing the evidence fingerprinting logic.

**Promotion decision tool:**
```bash
python tools/canary/grader_promotion.py summary --shadow-provider claude-3-5-sonnet
# Output: Observations: 47 items; Agreement rate: 91.5% (43/47);
#         Stable→Shadow upgrades (REWORK→ACCEPTED): 3;
#         Stable→Shadow downgrades (ACCEPTED→REWORK): 4;
#         Recommendation: HOLD (4 downgrades require review)
```

**Why this matters:** The grade cache's 7-day TTL means a silent provider switch would cause stale cached grades to expire and be replaced by the new provider's grades, with no visibility into whether the new provider agrees with the old one. The shadow log makes the disagreement visible before it becomes the authoritative source.

---

### Component 3: Compilation Diff Tool

**New file:** `tools/canary/compilation_diff.py`

This is a pure comparison tool. It does not modify any state.

```bash
python tools/canary/compilation_diff.py \
  --ledger reports/capability-layer/gap-ledger.json \
  --output reports/canary/compilation-diff-YYYYMMDD.yaml
# With candidate module (when testing a modified compiler):
python tools/canary/compilation_diff.py \
  --ledger reports/capability-layer/gap-ledger.json \
  --candidate-module tools.supervisor.capability_feature_compiler_candidate \
  --output reports/canary/compilation-diff-YYYYMMDD.yaml
```

Default behavior (no `--candidate-module`): runs the current compiler twice on the same ledger and verifies stable output (idempotency check). With `--candidate-module`: imports candidate module, runs both, diffs outputs.

Output format:
```yaml
comparison_date: "2026-07-10"
stable_module: "tools.supervisor.capability_feature_compiler"
candidate_module: "tools.supervisor.capability_feature_compiler_candidate"
total_stable_items: 20
total_candidate_items: 20
priority_changes:
  - gap_id: GAP-FODS-001
    stable_rank: 3
    candidate_rank: 1
    reason: "Starvation penalty changed"
format_coverage_changes:
  - format: abw
    stable_in_top_20: false
    candidate_in_top_20: true
new_items_surfaced: []
items_dropped: []
recommendation: "REVIEW before deploying — 3 formats change coverage in top-20"
```

---

### SQLite: Exactly Two New Tables

**File:** `tools/supervisor/control_index/migrations/v3_canary_shadow_log.sql`

Migration notes:
- `tools/supervisor/control_index/__init__.py` defines `SCHEMA_VERSION` — increment from 2 to 3
- `db.py` loads schema from `schema.sql` via `_SCHEMA_SQL = (Path(__file__).parent / "schema.sql").read_text()`
- `ensure_db()` at line 80 calls `init_db()` when `get_schema_version() < SCHEMA_VERSION`
- Migration approach: add new tables to `schema.sql` using `CREATE TABLE IF NOT EXISTS` so re-running is safe; increment `SCHEMA_VERSION` in `__init__.py`

```sql
-- v3: Canary shadow observation log tables
-- Validator shadow observations (append-only)
CREATE TABLE IF NOT EXISTS validator_shadow_observations (
    obs_id TEXT PRIMARY KEY,          -- "{sprint_id}:{validator_id}"
    sprint_id TEXT NOT NULL,
    validator_id TEXT NOT NULL,
    format TEXT,                      -- NULL = format-agnostic (V1: always NULL for wildcard)
    result TEXT NOT NULL,             -- PASS, FAIL, WARN
    would_have_blocked BOOLEAN NOT NULL,
    finding_count INTEGER NOT NULL DEFAULT 0,
    observed_at TEXT NOT NULL,
    FOREIGN KEY (sprint_id) REFERENCES sprints(sprint_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS idx_vso_validator
    ON validator_shadow_observations(validator_id, format);
CREATE INDEX IF NOT EXISTS idx_vso_sprint
    ON validator_shadow_observations(sprint_id);

-- Grader shadow comparisons (append-only)
CREATE TABLE IF NOT EXISTS grader_shadow_observations (
    obs_id TEXT PRIMARY KEY,          -- "{sprint_id}:{item_id}:{shadow_provider}"
    sprint_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    stable_provider TEXT NOT NULL,
    stable_grade TEXT NOT NULL,
    shadow_provider TEXT NOT NULL,
    shadow_grade TEXT,                -- NULL if shadow call failed
    agreement BOOLEAN,                -- NULL if shadow call failed
    error TEXT,                       -- error message if shadow call failed
    observed_at TEXT NOT NULL,
    FOREIGN KEY (sprint_id) REFERENCES sprints(sprint_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS idx_gso_shadow_provider
    ON grader_shadow_observations(shadow_provider, agreement);
CREATE INDEX IF NOT EXISTS idx_gso_sprint
    ON grader_shadow_observations(sprint_id);
```

Note: FK constraint uses `DEFERRABLE INITIALLY DEFERRED` because shadow log entries may be written before the sprint is indexed into the `sprints` table (the ingestor runs on next sync).

**What SQLite does NOT own:**
- The shadow registry configuration (that is `.supervisor/validator-shadow-registry.yaml`)
- The grader provider configuration (that is `tools/llm/endpoints.yaml`)
- Any decision about promotion (that is the promotion CLI tools)
- Sprint lifecycle state (that remains in existing tables)

**What SQLite DOES own:**
- Queryable history of shadow observations, enabling:
  ```
  python -m tools.supervisor.control_index.query shadow-status \
    --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
  # Shows: observed 7 sprints, would-have-blocked 2, threshold: 5, progress: 40%
  ```

---

### Control Index Integration

**New ingestor:** `tools/supervisor/control_index/ingestors/canary_shadow_ingestor.py`

Pattern (same as existing ingestors):
```python
from . import BaseIngestor
from ..sync import register_ingestor

@register_ingestor
class CanaryShadowIngestor(BaseIngestor):
    entity_type = "canary_shadow"
    source_paths = [
        ".local/supervisor/validator-shadow-log.jsonl",
        ".local/supervisor/grader-shadow-log.jsonl",
    ]
    # ingest_records() reads JSONL lines, inserts into both tables
```

Registration: add `from .ingestors import canary_shadow_ingestor  # noqa: F401, E402` after line 99 in `sync.py`. The `@register_ingestor` decorator auto-registers.

**New query:** extend `tools/supervisor/control_index/query.py` (or equivalent query CLI) to support:
```bash
python -m tools.supervisor.control_index.query shadow-status
python -m tools.supervisor.control_index.query shadow-status --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
```

---

### Discovery Reports (required by mission prompt)

Produced during TC-INV-001. Written once; not living documents.

| Report | Path | Content |
|--------|------|---------|
| State system inventory | `reports/canary/state-system-inventory.yaml` | 21 systems, each with canary_relevance |
| Opportunity map | `reports/canary/canary-opportunity-map.yaml` | 14+ candidates with dispositions |
| Risk register | `reports/canary/canary-risk-register.yaml` | R1-R4 and mitigations |
| Architecture decision | `reports/canary/canary-architecture-decision.yaml` | Full decision record |
| Benefit assessment | `reports/canary/canary-benefit-assessment.yaml` | Written after pilots pass (TC-CLOSE-001) |

Key dispositions (embedded in opportunity map):
- Validator promotion: `ADOPT` | LLM grader switch: `ADOPT` | Compilation priority: `ADOPT`
- Oracle D0→D1: `EXISTING_GATE_SUFFICIENT` | SAL ingestion: `EXISTING_GATE_SUFFICIENT`
- Parser/writer changes: `NOT_SUITABLE` (requires versioned package isolation)
- Package/release: `EXISTING_GATE_SUFFICIENT` | Regeneration: `FEATURE_FLAG_SUFFICIENT`
- Schema migrations: `TRANSACTIONAL_MIGRATION_BETTER` | Cross-language parity: `PILOT_ONLY`
- QName migrations: `EXISTING_GATE_SUFFICIENT` | Task selection: `NOT_SUITABLE`
- Localization: `DEFER_WITH_REASON` (pipeline doesn't exist) | Orchestration: `FEATURE_FLAG_SUFFICIENT`

---

## Implementation Files and Changes

### New files
```
tools/canary/__init__.py                        — package init, version string
tools/canary/validator_promotion.py             — shadow/status/promote/demote CLI
tools/canary/grader_promotion.py                — shadow summary + recommendation CLI
tools/canary/compilation_diff.py                — pure gap compilation comparison tool
tools/supervisor/control_index/migrations/
    v3_canary_shadow_log.sql                    — DDL for 2 new SQLite tables
tools/supervisor/control_index/ingestors/
    canary_shadow_ingestor.py                   — ingests shadow JSONL into SQLite
tests/canary/__init__.py                        — empty test package init
tests/canary/test_validator_shadow.py           — 8 test functions
tests/canary/test_grader_shadow.py              — 5 test functions
tests/canary/test_schema_migration.py           — 4 test functions
tests/canary/test_compilation_diff.py           — 4 test functions
```

### Modified files (surgical)
```
.supervisor/validator-shadow-registry.yaml              [CREATE — empty initial state]
tools/supervisor/governance_validator_runner.py         [+~40 LOC: shadow registry load + routing]
tools/supervisor/grade_declared_work.py                 [+~60 LOC: shadow provider flag + log writer]
tools/supervisor/control_index/__init__.py              [SCHEMA_VERSION: 2 → 3]
tools/supervisor/control_index/schema.sql               [append v3 DDL block]
tools/supervisor/control_index/sync.py                  [+1 import: canary_shadow_ingestor]
tools/supervisor/control_index/db.py                    [no change needed — ensure_db() already handles]
```

### New runtime files (gitignored, produced during operation)
```
.local/supervisor/validator-shadow-log.jsonl            — validator shadow observations
.local/supervisor/grader-shadow-log.jsonl               — grader shadow comparisons
.local/supervisor/grader-shadow-cache.json              — shadow grader grade cache
```

---

## Requirement Registry

| ID | Statement | Priority |
|----|-----------|----------|
| REQ-DIAG-001 | Validator blocking promotion must have a shadow observation period before becoming portfolio-wide | CRITICAL |
| REQ-DIAG-002 | LLM grader provider switches must have shadow comparison log before the switch is authoritative | HIGH |
| REQ-DIAG-003 | Gap compilation algorithm changes must have a dry-run diff before commit | MEDIUM |
| REQ-PRES-001 | File authority model must not change: JSON/YAML are ground truth, SQLite is shadow | CRITICAL |
| REQ-PRES-002 | Sprint lifecycle (continuation signal, plan locks, evidence, grading) must not regress | CRITICAL |
| REQ-PRES-003 | Oracle per-format isolation must not be disturbed | HIGH |
| REQ-PRES-004 | Validator count (currently 167) must not decrease | HIGH |
| REQ-PRES-005 | Grade cache (7-day TTL, evidence-keyed) must not be modified | HIGH |
| REQ-PRES-006 | Phase locks and authority gate validation must not be disturbed | HIGH |
| REQ-PRES-007 | execute_oracle.py must not be modified | HIGH |
| REQ-RDSGN-001 | governance_validator_runner.py must support per-validator shadow mode | CRITICAL |
| REQ-RDSGN-002 | grade_declared_work.py must support shadow provider grading | HIGH |
| REQ-RDSGN-003 | A compilation diff tool must exist for pre-commit scoring algorithm review | MEDIUM |
| REQ-IMPL-001 | .supervisor/validator-shadow-registry.yaml: shadow config file, YAML authority | CRITICAL |
| REQ-IMPL-002 | validator-shadow-log.jsonl: append-only shadow observation log | CRITICAL |
| REQ-IMPL-003 | validator_promotion.py: CLI for shadow/status/promote/demote lifecycle | HIGH |
| REQ-IMPL-004 | grader-shadow-log.jsonl: append-only grader comparison log | HIGH |
| REQ-IMPL-005 | grader_promotion.py: CLI for shadow summary and recommendation | HIGH |
| REQ-IMPL-006 | compilation_diff.py: pure diff, no state mutation | MEDIUM |
| REQ-IMPL-007 | v3_canary_shadow_log.sql: two new SQLite tables with indexes | HIGH |
| REQ-IMPL-008 | canary_shadow_ingestor.py: ingests JSONL logs into SQLite | HIGH |
| REQ-IMPL-009 | shadow-status query: queryable via control index CLI | MEDIUM |
| REQ-TEST-001 | test_validator_shadow.py: 8 tests covering shadow registry round-trips | HIGH |
| REQ-TEST-002 | test_grader_shadow.py: 5 tests covering shadow grading isolation | HIGH |
| REQ-TEST-003 | test_schema_migration.py: 4 tests covering v3 migration | HIGH |
| REQ-TEST-004 | test_compilation_diff.py: 4 tests covering pure diff properties | MEDIUM |
| REQ-REGR-001 | Governance validator count (167) must remain unchanged after shadow routing | CRITICAL |
| REQ-REGR-002 | Default blocking behavior unchanged when registry is empty | CRITICAL |
| REQ-REGR-003 | Sprint verdict unchanged when no shadow provider is configured | HIGH |
| REQ-REGR-004 | Control index row counts must not decrease after new ingestor added | HIGH |

---

## Execution Control Layer

### Execution order (dependency DAG summary)

```
TC-INV-001 ──────────────────────────────────────────────────────► (parallel-safe with all)
TC-SCHEMA-001 ─────────────────────────────────────────────────────► (prerequisite for TC-TEST-003)
TC-REGISTRY-001 ───► TC-VALCLI-001 ────────────────────────────────► (prerequisite for TC-TEST-001)
TC-GRADER-001 ─────────────────────────────────────────────────────► (prerequisite for TC-TEST-002)
TC-DIFF-001 ───────────────────────────────────────────────────────► (prerequisite for TC-TEST-004)
TC-INIT-001 ──────► (prerequisite for TC-REGISTRY-001, TC-GRADER-001, TC-DIFF-001)
TC-TEST-001 ────────────────────────────────────────────────────────► (after TC-REGISTRY-001, TC-VALCLI-001)
TC-TEST-002 ────────────────────────────────────────────────────────► (after TC-GRADER-001, TC-DIFF-001)
TC-TEST-003 ────────────────────────────────────────────────────────► (after TC-SCHEMA-001)
TC-TEST-004 ────────────────────────────────────────────────────────► (after TC-DIFF-001)
TC-CLOSE-001 ───────────────────────────────────────────────────────► (after ALL above)
```

Parallel-safe: TC-INV-001 can run at any time. TC-SCHEMA-001 and TC-INIT-001 can run in parallel. TC-REGISTRY-001 and TC-GRADER-001 and TC-DIFF-001 can run in parallel after TC-INIT-001.

File ownership locks:
- `tools/supervisor/governance_validator_runner.py`: TC-REGISTRY-001 ONLY
- `tools/supervisor/grade_declared_work.py`: TC-GRADER-001 ONLY
- `tools/supervisor/control_index/__init__.py`: TC-SCHEMA-001 ONLY
- `tools/supervisor/control_index/schema.sql`: TC-SCHEMA-001 ONLY
- `tools/supervisor/control_index/sync.py`: TC-SCHEMA-001 ONLY (one-line change)

---

### TC-INV-001: Produce Required Discovery Reports
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-DIAG-001/002/003, mission prompt §2/§4/§10/§11
Objective: Produce the 4 required discovery report YAMLs that document the
           state-system inventory, opportunity dispositions, risk register,
           and architecture decision for the record.
Scope:
  Allowed files: reports/canary/*.yaml (create or overwrite)
  Forbidden:     src/*, tools/*, tests/*, .supervisor/*
Outputs:
  - reports/canary/state-system-inventory.yaml
  - reports/canary/canary-opportunity-map.yaml
  - reports/canary/canary-risk-register.yaml
  - reports/canary/canary-architecture-decision.yaml
Dependencies: none
Children:
  - TC-INV-001-01: state-system-inventory.yaml
  - TC-INV-001-02: canary-opportunity-map.yaml
  - TC-INV-001-03: canary-risk-register.yaml + canary-architecture-decision.yaml
Parent acceptance: all 4 files exist, are valid YAML, contain required fields
Evidence: ls reports/canary/*.yaml; python -c "import yaml; yaml.safe_load(open(f))"
Closeout: all 3 children CLOSED, YAML parse succeeds for all 4 files
```

#### TC-INV-001-01: Write state-system-inventory.yaml
```
Type:     CHILD
Parent:   TC-INV-001
Status:   TODO
Source:   REQ-DIAG-001/002/003, exploration findings (21 systems identified)
Purpose:  Provide machine-readable inventory of all 21 state systems with
          canary_relevance ratings to justify the 3-candidate scope.
Scope:
  Allowed: reports/canary/state-system-inventory.yaml (create)
  Forbidden: all other files
Inputs:   Exploration findings from Explore agents (already in plan context)
Expected output:
  YAML with 21 entries. Each entry must have:
    system_id, purpose, owner, authority, stores, producers, consumers,
    state_model, transitions, concurrency, recovery, failure_history,
    broad_change_risk, current_controls, canary_relevance, findings
  canary_relevance values used: not_applicable (15), monitor_only (4),
    shadow_enforcement_needed (2: validator_enforcement, grader_selection)
Evidence: file exists, yaml.safe_load succeeds, len(entries) == 21
Next valid task: TC-INV-001-02
Rollback: delete file (no system state affected)
```

Micro-steps:
- MS-INV-001-01-01 [PENDING]: Create `reports/canary/` directory if not exists. Command: `python -c "from pathlib import Path; Path('reports/canary').mkdir(exist_ok=True)"`
- MS-INV-001-01-02 [PENDING]: Write `reports/canary/state-system-inventory.yaml` with all 21 system entries derived from exploration findings. Each entry uses exact field schema above. Systems: continuation_signal, plan_locks, evidence_declarations, oracle_verdicts, gap_ledger, control_index_sqlite, governance_validators, failure_memory, continuation_ledger, format_registry, phase_locks, checkpoint_manager, action_queue, orchestrator_state, sal_facts, qname_registry, capability_registry, source_baseline, grade_cache, mission_locks_sqlite, conveyor_matrix.
- MS-INV-001-01-03 [PENDING]: Verify YAML parses: `python -c "import yaml; data=yaml.safe_load(open('reports/canary/state-system-inventory.yaml')); assert len(data['state_systems']) == 21"`. Record pass/fail.
- MS-INV-001-01-04 [PENDING]: Capture evidence: record file path and entry count in child taskcard status.

#### TC-INV-001-02: Write canary-opportunity-map.yaml
```
Type:     CHILD
Parent:   TC-INV-001
Status:   TODO
Source:   REQ-DIAG-001/002/003, mission prompt §4, 14 prompt-suggested candidates
Purpose:  Document all 14+ canary candidates with disposition and justification.
          Serves as the authoritative record of what was considered and why.
Scope:
  Allowed: reports/canary/canary-opportunity-map.yaml (create)
  Forbidden: all other files
Inputs:   Dispositions from §Discovery Reports in this plan
Expected output:
  YAML with 14+ candidate entries. Each must have:
    candidate_id, discovered_from, workflow, current_rollout_model,
    stable_path, candidate_path, subject_unit, blast_radius,
    failure_modes, existing_controls, comparison_possible,
    rollback_possible, recommendation, evidence
  Adopted candidates: validator_promotion, llm_grader_switch, compilation_priority
  EXISTING_GATE_SUFFICIENT: oracle_d0_d1, sal_ingestion, package_release,
    qname_migrations, per_format_gate_execution
  NOT_SUITABLE: parser_writer_changes, task_selection_queue
  FEATURE_FLAG_SUFFICIENT: portfolio_regeneration, orchestration_changes
  TRANSACTIONAL_MIGRATION_BETTER: schema_migrations
  DEFER_WITH_REASON: content_localization
  PILOT_ONLY: cross_language_parity
Evidence: file exists, yaml.safe_load succeeds,
          CANARY_CANDIDATES_WITHOUT_DISPOSITION = 0 (all 14+ have recommendation field)
Next valid task: TC-INV-001-03
```

Micro-steps:
- MS-INV-001-02-01 [PENDING]: Write `reports/canary/canary-opportunity-map.yaml` with all 14 prompt-suggested candidates + any agent-discovered candidates from exploration. Total must be ≥ 14.
- MS-INV-001-02-02 [PENDING]: Verify: `python -c "import yaml; d=yaml.safe_load(open('reports/canary/canary-opportunity-map.yaml')); assert all('recommendation' in c for c in d['candidates'])"`. Record pass/fail.

#### TC-INV-001-03: Write risk register and architecture decision
```
Type:     CHILD
Parent:   TC-INV-001
Status:   TODO
Source:   REQ-DIAG-001/002/003, §Discovery Reports
Purpose:  Record architectural decisions and risks with mitigations.
Scope:
  Allowed: reports/canary/canary-risk-register.yaml,
           reports/canary/canary-architecture-decision.yaml (create)
  Forbidden: all other files
Expected output:
  canary-risk-register.yaml: 4+ risks R1-R4 each with:
    risk_id, description, severity, probability, prevention, detection,
    recovery, owner, test, pilot
  canary-architecture-decision.yaml: includes adopted/rejected candidates,
    selected vertical slice, SQLite design, authority boundaries, metrics,
    promotion/rollback, migration order, expected benefits and costs
Evidence: both files exist, yaml.safe_load succeeds for both,
          HIGH_RISKS_WITHOUT_MITIGATION = 0
```

Micro-steps:
- MS-INV-001-03-01 [PENDING]: Write `reports/canary/canary-risk-register.yaml`. Include R1 (shadow becomes permanent), R2 (shadow log unbounded growth), R3 (shadow provider latency), R4 (registry-code inconsistency). Each must have all required fields.
- MS-INV-001-03-02 [PENDING]: Write `reports/canary/canary-architecture-decision.yaml`. Reference all adopted/rejected candidates from TC-INV-001-02. Include authority boundary table (RETAIN_AS_AUTHORITY / CANARY_OWNS / COORDINATED_BY_CANARY). Reference REQ-* IDs.
- MS-INV-001-03-03 [PENDING]: Verify both files parse: `python -c "import yaml; [yaml.safe_load(open(f)) for f in ['reports/canary/canary-risk-register.yaml','reports/canary/canary-architecture-decision.yaml']]"`.

---

### TC-INIT-001: Initialize tools/canary Package
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-IMPL-003/005/006
Objective: Create the tools/canary/ Python package directory with __init__.py.
           This is a prerequisite for all canary CLI tools.
Scope:
  Allowed: tools/canary/__init__.py (create)
  Forbidden: all other files
Dependencies: none
Children:
  - TC-INIT-001-01: Create tools/canary/__init__.py
Parent acceptance: `import tools.canary` succeeds from repo root
Closeout: child CLOSED, import succeeds
```

#### TC-INIT-001-01: Create tools/canary/__init__.py
```
Type:     CHILD
Parent:   TC-INIT-001
Status:   TODO
Purpose:  Make tools/canary a Python package so CLI tools can be imported.
Scope:
  Allowed: tools/canary/__init__.py (create)
  Forbidden: all other files
Expected output:
  Minimal __init__.py with version string and __all__:
    __version__ = "1.0.0"
    __all__ = ["validator_promotion", "grader_promotion", "compilation_diff"]
Evidence: file exists, `python -c "import sys; sys.path.insert(0,'tools'); import canary"` succeeds
Next valid task: TC-REGISTRY-001-01 (validator_promotion.py)
```

Micro-steps:
- MS-INIT-001-01-01 [PENDING]: Verify `tools/canary/` directory does not exist: `python -c "from pathlib import Path; print(Path('tools/canary').exists())"` — expect False.
- MS-INIT-001-01-02 [PENDING]: Create `tools/canary/__init__.py` with `__version__ = "1.0.0"` and `__all__` list.
- MS-INIT-001-01-03 [PENDING]: Verify import: `python -c "import sys; sys.path.insert(0,'tools'); import canary; print(canary.__version__)"` — expect `1.0.0`.

---

### TC-SCHEMA-001: SQLite v3 Migration — Canary Shadow Tables
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-IMPL-007/008/009
Objective: Extend the existing control-index.db with two new tables for canary
           shadow observations, without breaking existing schema or tests.
Scope:
  Allowed files:
    tools/supervisor/control_index/__init__.py
    tools/supervisor/control_index/schema.sql
    tools/supervisor/control_index/sync.py
    tools/supervisor/control_index/ingestors/canary_shadow_ingestor.py (create)
    tools/supervisor/control_index/migrations/v3_canary_shadow_log.sql (create)
  Forbidden: all other control_index files, all other tools/ files
Preserved behavior:
  - All 16 existing ingestors continue to function
  - Existing table row counts do not decrease
  - schema_meta.schema_version was 2, becomes 3
  - test_control_index_sync.py must still pass
Dependencies: none
Children:
  - TC-SCHEMA-001-01: Write v3 SQL migration file
  - TC-SCHEMA-001-02: Increment SCHEMA_VERSION and append DDL to schema.sql
  - TC-SCHEMA-001-03: Create canary_shadow_ingestor.py
  - TC-SCHEMA-001-04: Register ingestor in sync.py
Parent acceptance criteria:
  - `python -m tools.supervisor.control_index status` shows schema_version = 3
  - `validator_shadow_observations` and `grader_shadow_observations` tables exist
  - test_control_index_sync.py passes
Evidence:
  - control_index status output showing version 3
  - pytest test_control_index_sync.py output
Closeout: all 4 children CLOSED, parent acceptance criteria met
```

#### TC-SCHEMA-001-01: Write v3 SQL migration file
```
Type:     CHILD
Parent:   TC-SCHEMA-001
Status:   TODO
Source:   REQ-IMPL-007
Purpose:  Produce the canonical DDL for the two new canary shadow tables.
          This file serves as documentation and as the source for schema.sql.
Scope:
  Allowed: tools/supervisor/control_index/migrations/v3_canary_shadow_log.sql (create)
           (create tools/supervisor/control_index/migrations/ directory if needed)
  Forbidden: schema.sql, __init__.py, sync.py, db.py
Inputs:   DDL specification from §SQLite: Exactly Two New Tables in this plan
Expected output:
  SQL file containing exactly:
    CREATE TABLE IF NOT EXISTS validator_shadow_observations (...)
    CREATE INDEX IF NOT EXISTS idx_vso_validator ON ...
    CREATE INDEX IF NOT EXISTS idx_vso_sprint ON ...
    CREATE TABLE IF NOT EXISTS grader_shadow_observations (...)
    CREATE INDEX IF NOT EXISTS idx_gso_shadow_provider ON ...
    CREATE INDEX IF NOT EXISTS idx_gso_sprint ON ...
    (DEFERRABLE FK constraint, nullable shadow_grade and agreement columns)
Evidence: file exists, sqlite3 can parse it:
  python -c "import sqlite3; c=sqlite3.connect(':memory:');
    c.executescript(open('tools/supervisor/control_index/migrations/v3_canary_shadow_log.sql').read())"
Next valid task: TC-SCHEMA-001-02
```

Micro-steps:
- MS-SCHEMA-001-01-01 [PENDING]: Create `tools/supervisor/control_index/migrations/` directory: `python -c "from pathlib import Path; Path('tools/supervisor/control_index/migrations').mkdir(exist_ok=True)"`
- MS-SCHEMA-001-01-02 [PENDING]: Write `tools/supervisor/control_index/migrations/v3_canary_shadow_log.sql` with both CREATE TABLE statements and 4 indexes as specified in §SQLite above. Include DEFERRABLE FK constraints. Use nullable `shadow_grade`, `agreement`, `error` columns in grader table (to handle failed shadow calls gracefully).
- MS-SCHEMA-001-01-03 [PENDING]: Parse-test the SQL: `python -c "import sqlite3; c=sqlite3.connect(':memory:'); c.executescript(open('tools/supervisor/control_index/migrations/v3_canary_shadow_log.sql').read()); print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")])"` — expect both table names in output.
- MS-SCHEMA-001-01-04 [PENDING]: Record: file path, line count, table count (2), index count (4).

#### TC-SCHEMA-001-02: Increment SCHEMA_VERSION and extend schema.sql
```
Type:     CHILD
Parent:   TC-SCHEMA-001
Status:   TODO
Source:   REQ-IMPL-007
Purpose:  Trigger automatic v3 migration by bumping SCHEMA_VERSION and appending
          the new DDL to schema.sql so init_db() picks it up on next call to ensure_db().
Scope:
  Allowed:
    tools/supervisor/control_index/__init__.py  (SCHEMA_VERSION: 2 → 3)
    tools/supervisor/control_index/schema.sql   (append v3 DDL block)
  Forbidden: db.py (ensure_db() already handles version comparison correctly)
Preconditions: TC-SCHEMA-001-01 CLOSED (v3 SQL file exists as source)
Inputs:
  - Current SCHEMA_VERSION in __init__.py (read first to confirm it is 2)
  - DDL from v3_canary_shadow_log.sql
Expected output:
  __init__.py: SCHEMA_VERSION = 3
  schema.sql: original content + v3 DDL appended with comment header
              "-- v3: canary shadow observation tables"
Evidence:
  - grep "SCHEMA_VERSION = 3" tools/supervisor/control_index/__init__.py → found
  - grep "validator_shadow_observations" tools/supervisor/control_index/schema.sql → found
Next valid task: TC-SCHEMA-001-03
```

Micro-steps:
- MS-SCHEMA-001-02-01 [PENDING]: Read `tools/supervisor/control_index/__init__.py`. Confirm current `SCHEMA_VERSION` value (expect 2). Record actual value.
- MS-SCHEMA-001-02-02 [PENDING]: Read `tools/supervisor/control_index/schema.sql`. Confirm it does NOT already contain `validator_shadow_observations`. Record last line number.
- MS-SCHEMA-001-02-03 [PENDING]: Edit `tools/supervisor/control_index/__init__.py`: change `SCHEMA_VERSION = 2` to `SCHEMA_VERSION = 3`. Verify with grep.
- MS-SCHEMA-001-02-04 [PENDING]: Append to `tools/supervisor/control_index/schema.sql`: add comment header `-- v3: canary shadow observation tables` followed by full DDL from v3_canary_shadow_log.sql. Use `CREATE TABLE IF NOT EXISTS` (already in DDL, so safe to append).
- MS-SCHEMA-001-02-05 [PENDING]: Run migration: `python -m tools.supervisor.control_index init`. Expect success (no error).
- MS-SCHEMA-001-02-06 [PENDING]: Verify schema version: `python -m tools.supervisor.control_index status`. Expect `schema_version: 3` in output.
- MS-SCHEMA-001-02-07 [PENDING]: Verify tables exist: `python -c "from tools.supervisor.control_index.db import get_connection; from tools.supervisor.control_index import DEFAULT_DB_PATH; c=get_connection(DEFAULT_DB_PATH); print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%shadow%'\")])"` — expect both table names.

#### TC-SCHEMA-001-03: Create canary_shadow_ingestor.py
```
Type:     CHILD
Parent:   TC-SCHEMA-001
Status:   TODO
Source:   REQ-IMPL-008
Purpose:  Ingest validator-shadow-log.jsonl and grader-shadow-log.jsonl into
          the two new SQLite tables. Follows existing ingestor pattern exactly.
Scope:
  Allowed: tools/supervisor/control_index/ingestors/canary_shadow_ingestor.py (create)
  Forbidden: all other ingestor files, schema.sql, db.py
Preconditions: TC-SCHEMA-001-02 CLOSED (tables exist)
Inputs:
  - Existing ingestor pattern (gap_ingestor.py as reference):
    @register_ingestor, BaseIngestor, entity_type, source_paths, ingest_records()
  - Source files: .local/supervisor/validator-shadow-log.jsonl,
                  .local/supervisor/grader-shadow-log.jsonl
Expected output:
  canary_shadow_ingestor.py with:
    - @register_ingestor decorator
    - entity_type = "canary_shadow"
    - source_paths = [".local/supervisor/validator-shadow-log.jsonl",
                      ".local/supervisor/grader-shadow-log.jsonl"]
    - ingest_records(): reads JSONL lines, inserts into validator_shadow_observations
      and grader_shadow_observations based on source_path
    - delete_existing(): deletes rows for given source_file path
    - Handles missing files gracefully (returns 0 if file doesn't exist yet)
Evidence:
  - file exists with @register_ingestor decorator
  - python -c "from tools.supervisor.control_index.ingestors import canary_shadow_ingestor" succeeds
Next valid task: TC-SCHEMA-001-04
```

Micro-steps:
- MS-SCHEMA-001-03-01 [PENDING]: Read `tools/supervisor/control_index/ingestors/gap_ingestor.py` as pattern reference. Note: BaseIngestor import path, register_ingestor import, entity_type, source_paths, ingest_records signature.
- MS-SCHEMA-001-03-02 [PENDING]: Write `tools/supervisor/control_index/ingestors/canary_shadow_ingestor.py`. Structure: import BaseIngestor from `. import BaseIngestor`; import register_ingestor from `..sync`; decorate class with `@register_ingestor`; set `entity_type = "canary_shadow"`; set `source_paths` to both JSONL file paths; implement `delete_existing()` to delete from both tables by source_file; implement `ingest_records()` to route validator log lines to `validator_shadow_observations` and grader log lines to `grader_shadow_observations`; handle missing file gracefully.
- MS-SCHEMA-001-03-03 [PENDING]: Verify import: `python -c "import sys; sys.path.insert(0,'tools/supervisor'); from control_index.ingestors import canary_shadow_ingestor; print('OK')"` — expect OK.
- MS-SCHEMA-001-03-04 [PENDING]: Verify ingestor count: `python -c "import sys; sys.path.insert(0,'tools/supervisor'); from control_index.sync import ALL_INGESTORS; print(len(ALL_INGESTORS))"` — expect N+1 where N is count before this change (currently 16, so expect 16 after import before TC-SCHEMA-001-04 adds the import).

#### TC-SCHEMA-001-04: Register ingestor in sync.py
```
Type:     CHILD
Parent:   TC-SCHEMA-001
Status:   TODO
Source:   REQ-IMPL-008
Purpose:  Add the import that triggers the @register_ingestor decorator,
          making canary_shadow_ingestor auto-register into ALL_INGESTORS.
Scope:
  Allowed: tools/supervisor/control_index/sync.py (one-line insertion only)
  Forbidden: all other files
Preconditions: TC-SCHEMA-001-03 CLOSED (ingestor file exists)
Expected output:
  One new import line after the last existing ingestor import (~line 99):
    from .ingestors import canary_shadow_ingestor  # noqa: F401, E402
Evidence:
  - grep "canary_shadow_ingestor" tools/supervisor/control_index/sync.py → found
  - python -m tools.supervisor.control_index.sync produces no import error
  - ALL_INGESTORS length increased by 1 (from 16 to 17)
Next valid task: TC-REGISTRY-001-01 (can now run TC-REGISTRY-001 in parallel)
```

Micro-steps:
- MS-SCHEMA-001-04-01 [PENDING]: Read `tools/supervisor/control_index/sync.py` lines 75-110. Confirm current ingestor import list ends at line ~99 with `# noqa: F401, E402` pattern. Record exact line number of last ingestor import.
- MS-SCHEMA-001-04-02 [PENDING]: Insert one line after the last ingestor import: `from .ingestors import canary_shadow_ingestor  # noqa: F401, E402`
- MS-SCHEMA-001-04-03 [PENDING]: Verify: `python -c "import sys; sys.path.insert(0,'tools/supervisor'); from control_index.sync import ALL_INGESTORS; print(len(ALL_INGESTORS))"` — expect 17.
- MS-SCHEMA-001-04-04 [PENDING]: Run full sync to confirm no regression: `python -m tools.supervisor.control_index sync`. Expect no errors. Record output.

---

### TC-REGISTRY-001: Validator Shadow System
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-IMPL-001/002, REQ-RDSGN-001
Objective: Build the complete validator shadow mechanism: config file + shadow
           routing in governance_validator_runner.py + shadow log writer.
           This is the highest-priority implementation deliverable.
Scope:
  Allowed files:
    .supervisor/validator-shadow-registry.yaml (create)
    tools/supervisor/governance_validator_runner.py (surgical addition only)
  Forbidden:
    All other governance_validators_*.py files
    Any other tools/supervisor/*.py file
    Do NOT modify blocks_sprint in any existing validator
Preserved behavior:
  - All 167 validators continue to execute
  - Validators NOT in shadow registry continue to block on FAIL exactly as before
  - run_all_governance_validators() return dict structure unchanged (new key added)
Dependencies: TC-INIT-001 (tools/canary package exists)
Children:
  - TC-REGISTRY-001-01: Create .supervisor/validator-shadow-registry.yaml
  - TC-REGISTRY-001-02: Add shadow registry loader to governance_validator_runner.py
  - TC-REGISTRY-001-03: Add shadow routing (neutralize blocks_sprint for shadow validators)
  - TC-REGISTRY-001-04: Add shadow log writer
Parent acceptance criteria:
  - .venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v PASSES (all 167)
  - Empty registry → behavior identical to pre-change (regression: REQ-REGR-001/002)
  - V_VALIDATE_ORACLE_DEPTH_MINIMUM added to shadow mode → sprint not blocked, log written
Evidence:
  - pytest output showing 167 validators pass
  - .local/supervisor/validator-shadow-log.jsonl entry for V143 observation
Closeout: all 4 children CLOSED, both acceptance checks pass
```

#### TC-REGISTRY-001-01: Create .supervisor/validator-shadow-registry.yaml
```
Type:     CHILD
Parent:   TC-REGISTRY-001
Status:   TODO
Source:   REQ-IMPL-001
Purpose:  Create the YAML config file that serves as the authority for which
          validators are in shadow mode. Initial state: empty (no validators
          in shadow — preserves all existing behavior by default).
Scope:
  Allowed: .supervisor/validator-shadow-registry.yaml (create)
  Forbidden: .supervisor/config.yaml, .supervisor/policies.yaml, all other files
Expected output:
  YAML file with:
    validator_shadow_entries: []  # empty: all validators blocking by default
Evidence:
  - file exists at .supervisor/validator-shadow-registry.yaml
  - python -c "import yaml; d=yaml.safe_load(open('.supervisor/validator-shadow-registry.yaml'));
      assert d['validator_shadow_entries'] == [], d"
Next valid task: TC-REGISTRY-001-02
Rollback: delete the file (restores pre-change state)
```

Micro-steps:
- MS-REGISTRY-001-01-01 [PENDING]: Confirm `.supervisor/` directory exists and `validator-shadow-registry.yaml` does not already exist.
- MS-REGISTRY-001-01-02 [PENDING]: Write `.supervisor/validator-shadow-registry.yaml` with content: header comment block explaining modes (advisory/shadow/blocking), `validator_shadow_entries: []`.
- MS-REGISTRY-001-01-03 [PENDING]: Verify: `python -c "import yaml; d=yaml.safe_load(open('.supervisor/validator-shadow-registry.yaml')); assert 'validator_shadow_entries' in d and isinstance(d['validator_shadow_entries'], list)"`. Record pass.

#### TC-REGISTRY-001-02: Add shadow registry loader to governance_validator_runner.py
```
Type:     CHILD
Parent:   TC-REGISTRY-001
Status:   TODO
Source:   REQ-RDSGN-001
Purpose:  Add a fail-safe registry loader so the runner knows which validators
          are in shadow mode without crashing if the file is missing.
Scope:
  Allowed: tools/supervisor/governance_validator_runner.py (additions only, no removals)
  Forbidden: any governance_validators_*.py file
Preconditions: TC-REGISTRY-001-01 CLOSED
Inputs:
  - Current imports section (lines ~1-60 of governance_validator_runner.py)
  - Current function signature: run_all_governance_validators(declaration, repo_root)
Expected output:
  3 additions to governance_validator_runner.py:
  1. Near top imports: import yaml (if not already imported)
  2. Module-level constant:
       SHADOW_REGISTRY_PATH = (
           Path(__file__).resolve().parent.parent.parent
           / ".supervisor" / "validator-shadow-registry.yaml"
       )
  3. New helper function (before run_all_governance_validators):
       def _load_shadow_registry() -> dict:
           """Return {validator_id: entry} from registry. Returns {} on any error."""
           try:
               if not SHADOW_REGISTRY_PATH.exists():
                   return {}
               data = yaml.safe_load(SHADOW_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
               entries = data.get("validator_shadow_entries", [])
               return {e["validator_id"]: e for e in entries if "validator_id" in e}
           except Exception:
               return {}  # fail-safe: treat missing/invalid registry as empty
Evidence:
  - grep "SHADOW_REGISTRY_PATH" tools/supervisor/governance_validator_runner.py → found
  - grep "_load_shadow_registry" tools/supervisor/governance_validator_runner.py → found
  - python -c "import sys; sys.path.insert(0,'tools/supervisor');
      from governance_validator_runner import _load_shadow_registry;
      r = _load_shadow_registry(); print(type(r), len(r))"  → dict, 0
Next valid task: TC-REGISTRY-001-03
```

Micro-steps:
- MS-REGISTRY-001-02-01 [PENDING]: Read lines 1-70 of `tools/supervisor/governance_validator_runner.py`. Confirm `yaml` is or is not imported. Record line numbers of: existing imports, last import line, start of `run_all_governance_validators` function.
- MS-REGISTRY-001-02-02 [PENDING]: If `yaml` not imported: add `import yaml` near the existing `from pathlib import Path` import.
- MS-REGISTRY-001-02-03 [PENDING]: Add `SHADOW_REGISTRY_PATH` constant after imports block (before first function definition).
- MS-REGISTRY-001-02-04 [PENDING]: Add `_load_shadow_registry()` function just before `run_all_governance_validators`. Function body: try/except block, returns dict keyed by validator_id. Handles missing file, invalid YAML, and missing validator_id field gracefully.
- MS-REGISTRY-001-02-05 [PENDING]: Verify import works: `python -c "import sys; sys.path.insert(0,'tools/supervisor'); from governance_validator_runner import _load_shadow_registry; assert _load_shadow_registry() == {}"`. Record pass.

#### TC-REGISTRY-001-03: Add shadow routing in validator result loop
```
Type:     CHILD
Parent:   TC-REGISTRY-001
Status:   TODO
Source:   REQ-RDSGN-001, REQ-REGR-001
Purpose:  After each validator's result is appended to the results list,
          check if it is in shadow mode. If so, neutralize its blocks_sprint
          flag so the final aggregation at line ~800 sees False.
          This is the core behavioral change of the entire plan.
Scope:
  Allowed: tools/supervisor/governance_validator_runner.py (additions only)
  Forbidden: modifying blocks_sprint in any validator definition file
Preconditions: TC-REGISTRY-001-02 CLOSED
Critical constraint:
  The validator MUST still run and its result MUST still appear in
  run_all_governance_validators()["validators"] list.
  ONLY its blocks_sprint field is neutralized in the result dict.
  The original would_have_blocked value is preserved in shadow_suppressions.
Expected output:
  In run_all_governance_validators():
  1. At function entry: shadow_registry = _load_shadow_registry()
                         shadow_suppressions = []
  2. After each validator result is appended to results:
       result = results[-1]  # the just-appended result
       vid = result.get("validator") or result.get("validator_id", "")
       if vid in shadow_registry and result["result"] == "FAIL" and result.get("blocks_sprint"):
           shadow_entry = shadow_registry[vid]
           shadow_suppressions.append({
               "validator_id": vid,
               "original_result": result["result"],
               "would_have_blocked": True,
               "finding_count": len(result.get("items", result.get("violations", []))),
               "registry_entry": shadow_entry,
           })
           result["blocks_sprint"] = False  # neutralize for aggregation
  3. In return dict: add "shadow_suppressions": shadow_suppressions
Evidence:
  - With empty registry: run_all_governance_validators() output is bit-for-bit identical to
    pre-change output for same declaration (test via test_shadow_registry_loads_empty)
  - With V143 in shadow: V143 FAIL does NOT set blocks_sprint=True in return dict
  - shadow_suppressions list is populated with correct entry
Next valid task: TC-REGISTRY-001-04
```

Micro-steps:
- MS-REGISTRY-001-03-01 [PENDING]: Read `tools/supervisor/governance_validator_runner.py` lines 195-215 (start of `run_all_governance_validators`) and lines 790-815 (blocks_sprint aggregation). Identify exact location where: (a) function body begins, (b) first validator result appended to results list, (c) `blocks_sprint = any(...)` line.
- MS-REGISTRY-001-03-02 [PENDING]: Insert `shadow_registry = _load_shadow_registry()` and `shadow_suppressions = []` at function start (after declaration/repo_root locals, before validator calls).
- MS-REGISTRY-001-03-03 [PENDING]: Identify the pattern used to append validator results to `results`. It may be direct appends or a loop. Insert the shadow-routing block immediately after each append point — or, if all validators append via a common pattern, insert a single post-processing check after all validators run (before line ~800 aggregation). Use the post-processing approach if inserting at each call site would require more than 10 insertion points.
- MS-REGISTRY-001-03-04 [PENDING]: Add `"shadow_suppressions": shadow_suppressions` to the return dict near the end of the function.
- MS-REGISTRY-001-03-05 [PENDING]: Run smoke test with empty registry: `python -c "import sys; sys.path.insert(0,'tools/supervisor'); from governance_validator_runner import run_all_governance_validators; r = run_all_governance_validators({}); print('shadow_suppressions:', r.get('shadow_suppressions')); print('blocks_sprint:', r['blocks_sprint'])"`. Expect shadow_suppressions = [], blocks_sprint = False (no declaration = nothing to block).

#### TC-REGISTRY-001-04: Add shadow log writer
```
Type:     CHILD
Parent:   TC-REGISTRY-001
Status:   TODO
Source:   REQ-IMPL-002
Purpose:  Write each shadow suppression to .local/supervisor/validator-shadow-log.jsonl
          as an append-only observation record.
Scope:
  Allowed: tools/supervisor/governance_validator_runner.py (additions only)
  Forbidden: all other files
Preconditions: TC-REGISTRY-001-03 CLOSED
Expected output:
  New helper function _write_shadow_log_entry(entry: dict) -> None:
    - Writes JSON line to SHADOW_LOG_PATH = REPO_ROOT / ".local/supervisor/validator-shadow-log.jsonl"
    - Creates parent directory if needed
    - Appends (mode="a"), never overwrites
    - Wraps in try/except — log write failure is non-fatal (sprint continues)
  Entry structure:
    {"ts": ISO8601, "validator_id": str, "result": str,
     "would_have_blocked": bool, "finding_count": int, "mode": "shadow"}
  Call site: after shadow suppression recorded in shadow_suppressions list,
             call _write_shadow_log_entry(...)
Evidence:
  - After running governance validators with V143 in shadow mode and a failing V143 check:
    .local/supervisor/validator-shadow-log.jsonl contains ≥1 line
  - Each line is valid JSON with required fields
  - Log write failure (e.g., read-only filesystem) does NOT raise exception in caller
Next valid task: TC-VALCLI-001-01
Rollback: remove _write_shadow_log_entry function and call sites; delete log file
```

Micro-steps:
- MS-REGISTRY-001-04-01 [PENDING]: Add `SHADOW_LOG_PATH` constant to `governance_validator_runner.py`: `SHADOW_LOG_PATH = Path(__file__).resolve().parent.parent.parent / ".local" / "supervisor" / "validator-shadow-log.jsonl"`
- MS-REGISTRY-001-04-02 [PENDING]: Add `import json` to imports if not already present (check first).
- MS-REGISTRY-001-04-03 [PENDING]: Write `_write_shadow_log_entry(entry: dict) -> None` helper. Body: `try: SHADOW_LOG_PATH.parent.mkdir(parents=True, exist_ok=True); SHADOW_LOG_PATH.open("a", encoding="utf-8").write(json.dumps(entry) + "\n"); except Exception: pass`
- MS-REGISTRY-001-04-04 [PENDING]: Add call to `_write_shadow_log_entry(...)` inside the shadow suppression block (from TC-REGISTRY-001-03). Pass: `{"ts": datetime.now(timezone.utc).isoformat(), "validator_id": vid, "result": result["result"], "would_have_blocked": True, "finding_count": shadow_suppressions[-1]["finding_count"], "mode": "shadow"}`. Add datetime import if needed.
- MS-REGISTRY-001-04-05 [PENDING]: Test log write: run governance validators with V143 in registry (temporarily add to `.supervisor/validator-shadow-registry.yaml`), then check: `python -c "import json; lines=[json.loads(l) for l in open('.local/supervisor/validator-shadow-log.jsonl')]; print(len(lines), 'entries')"`.
- MS-REGISTRY-001-04-06 [PENDING]: Run full governance validator test: `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v`. Expect all 167 pass. Capture output as evidence.

---

### TC-VALCLI-001: Validator Promotion CLI
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-IMPL-003
Objective: Create tools/canary/validator_promotion.py with 4 sub-commands:
           shadow (add to registry), status (observation count), promote
           (set mode: blocking), demote (set mode: shadow or advisory).
Scope:
  Allowed: tools/canary/validator_promotion.py (create)
  Forbidden: .supervisor/validator-shadow-registry.yaml (CLI edits it at runtime, not now)
Dependencies: TC-INIT-001 (package exists), TC-REGISTRY-001 (registry file exists)
Children:
  - TC-VALCLI-001-01: Create validator_promotion.py with all 4 sub-commands
Parent acceptance criteria:
  - python tools/canary/validator_promotion.py shadow --validator V_TEST --threshold 3
    → adds entry to registry YAML
  - python tools/canary/validator_promotion.py status --validator V_TEST
    → reads shadow log, prints count/rate/threshold progress
  - python tools/canary/validator_promotion.py promote --validator V_TEST
    → sets mode: blocking in registry
  - python tools/canary/validator_promotion.py demote --validator V_TEST
    → sets mode: shadow in registry
  - Idempotent promote (already blocking): exit 0, prints "already blocking"
Closeout: child CLOSED, all 4 sub-commands work as specified
```

#### TC-VALCLI-001-01: Create tools/canary/validator_promotion.py
```
Type:     CHILD
Parent:   TC-VALCLI-001
Status:   TODO
Source:   REQ-IMPL-003
Purpose:  CLI entry point for validator shadow lifecycle management.
Scope:
  Allowed: tools/canary/validator_promotion.py (create)
  Forbidden: .supervisor/ directory (runtime edits only)
Expected output:
  CLI with argparse sub-commands:
    shadow --validator <id> [--formats "*"] [--threshold N] [--notes TEXT]
    status --validator <id>
    promote --validator <id>
    demote --validator <id> [--to shadow|advisory]
  All sub-commands read/write .supervisor/validator-shadow-registry.yaml
  status also reads .local/supervisor/validator-shadow-log.jsonl
  All file edits use atomic write (write tmp, rename) or yaml.dump to file
  Exit codes: 0 success, 1 error (e.g., validator not found in registry for promote)
Evidence:
  - python tools/canary/validator_promotion.py shadow --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
      --threshold 5 → exit 0, registry updated
  - python tools/canary/validator_promotion.py status --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
      → prints observation count
  - python tools/canary/validator_promotion.py promote --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
      → registry entry mode changed to "blocking"
  - python tools/canary/validator_promotion.py promote (again) → exit 0, "already blocking"
  - python tools/canary/validator_promotion.py demote --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM
      → mode back to "shadow"
Next valid task: TC-TEST-001-01
```

Micro-steps:
- MS-VALCLI-001-01-01 [PENDING]: Write `tools/canary/validator_promotion.py`. Structure: imports (argparse, yaml, json, pathlib, datetime); `REGISTRY_PATH` and `SHADOW_LOG_PATH` constants; `load_registry()` and `save_registry()` helpers (save uses tmp-rename pattern); `cmd_shadow()`, `cmd_status()`, `cmd_promote()`, `cmd_demote()` sub-command functions; `main()` with argparse; `if __name__ == "__main__": sys.exit(main())`.
- MS-VALCLI-001-01-02 [PENDING]: Implement `cmd_shadow()`: loads registry, finds existing entry by validator_id or creates new one, sets mode="shadow", format_scope=["*"], shadow_since=today, shadow_promotion_threshold=threshold, saves registry.
- MS-VALCLI-001-01-03 [PENDING]: Implement `cmd_status()`: loads registry to get threshold, reads validator-shadow-log.jsonl, filters by validator_id, counts total observations and would-have-blocked count, prints summary with threshold progress percentage.
- MS-VALCLI-001-01-04 [PENDING]: Implement `cmd_promote()`: loads registry, finds entry, if already "blocking" prints message and exits 0 (idempotent), else sets mode="blocking" and saves.
- MS-VALCLI-001-01-05 [PENDING]: Implement `cmd_demote()`: loads registry, finds entry, sets mode to --to value (default "shadow"), saves.
- MS-VALCLI-001-01-06 [PENDING]: Test all 4 sub-commands against `.supervisor/validator-shadow-registry.yaml` using `V_VALIDATE_ORACLE_DEPTH_MINIMUM` as test validator. Verify file contents after each command.

---

### TC-GRADER-001: Grader Shadow Integration
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-IMPL-004/005, REQ-RDSGN-002
Objective: Add optional shadow grading to grade_declared_work.py and create
           the grader_promotion.py summary CLI.
Scope:
  Allowed files:
    tools/supervisor/grade_declared_work.py (surgical addition, ~60 LOC)
    tools/canary/grader_promotion.py (create)
  Forbidden:
    Any change to grade_declared_work.py that alters sprint verdict logic
    Any change to the stable grading path
    Any change to grade cache keying for stable grades
Preserved behavior:
  - Sprint verdict (ACCEPTED/REWORK) when --shadow-provider not set:
    bit-for-bit identical to pre-change behavior (REQ-REGR-003)
  - Grade cache for stable provider: unchanged key format, unchanged TTL
Dependencies: TC-INIT-001 (tools/canary package exists)
Children:
  - TC-GRADER-001-01: Add --shadow-provider to grade_declared_work.py
  - TC-GRADER-001-02: Add shadow grading call and log writer
  - TC-GRADER-001-03: Create tools/canary/grader_promotion.py
Parent acceptance criteria:
  - grade_declared_work.py without --shadow-provider: output identical to pre-change
  - grade_declared_work.py --shadow-provider <id>: shadow log populated, verdict unchanged
  - grader_promotion.py summary produces recommendation
Closeout: all 3 children CLOSED, parent acceptance criteria met
```

#### TC-GRADER-001-01: Add --shadow-provider CLI flag
```
Type:     CHILD
Parent:   TC-GRADER-001
Status:   TODO
Source:   REQ-RDSGN-002
Purpose:  Extend the argparse CLI of grade_declared_work.py with optional
          --shadow-provider and --sprint-id flags without changing any existing arg.
Scope:
  Allowed: tools/supervisor/grade_declared_work.py (additions only)
  Forbidden: changing existing CLI args, changing grade_all() output structure
Preconditions: TC-INIT-001 CLOSED
Inputs:
  - Current main() at line 1103, current args: --inspection, --declaration, --output-dir
  - grade_all() signature: grade_all(inspection: dict, declaration: dict) → dict
Expected output:
  Add to argparse parser (before args = parser.parse_args()):
    parser.add_argument("--shadow-provider", type=str, default="",
                        help="Shadow LLM endpoint ID for provider comparison grading")
    parser.add_argument("--sprint-id", type=str, default="",
                        help="Sprint ID for shadow log correlation")
  Pass args.shadow_provider and args.sprint_id to grade_all() (update signature)
  grade_all signature becomes: grade_all(inspection, declaration, shadow_provider="", sprint_id="")
Evidence:
  - python tools/supervisor/grade_declared_work.py --help includes --shadow-provider
  - Running without --shadow-provider: exit code identical to pre-change
Next valid task: TC-GRADER-001-02
```

Micro-steps:
- MS-GRADER-001-01-01 [PENDING]: Read `tools/supervisor/grade_declared_work.py` lines 1100-1127 (main function). Record exact line of `parser.parse_args()` and `grade_all()` call.
- MS-GRADER-001-01-02 [PENDING]: Read `grade_all()` function signature at line ~648. Record current parameter list.
- MS-GRADER-001-01-03 [PENDING]: Add two argparse lines before `args = parser.parse_args()`. Use exact flag names: `--shadow-provider` and `--sprint-id`, both optional with `default=""`.
- MS-GRADER-001-01-04 [PENDING]: Update `grade_all()` signature to accept `shadow_provider: str = ""` and `sprint_id: str = ""` as keyword arguments.
- MS-GRADER-001-01-05 [PENDING]: Update the call site `review = grade_all(inspection, declaration)` to `review = grade_all(inspection, declaration, shadow_provider=args.shadow_provider, sprint_id=args.sprint_id)`.
- MS-GRADER-001-01-06 [PENDING]: Verify help: `python tools/supervisor/grade_declared_work.py --help | grep shadow-provider` → found.
- MS-GRADER-001-01-07 [PENDING]: Confirm no regression: run existing `grade_declared_work.py` test if one exists (check `tests/supervisor/` for relevant test file), or record that output without `--shadow-provider` is unchanged.

#### TC-GRADER-001-02: Add shadow grading call and log writer
```
Type:     CHILD
Parent:   TC-GRADER-001
Status:   TODO
Source:   REQ-IMPL-004, REQ-RDSGN-002
Purpose:  Inside grade_all(), after grading each work item with the stable
          provider, optionally call shadow provider and log comparison.
          Shadow grade never affects sprint verdict.
Scope:
  Allowed: tools/supervisor/grade_declared_work.py (additions only in grade_all and helpers)
  Forbidden: any change that affects sprint verdict when shadow_provider is empty
Preconditions: TC-GRADER-001-01 CLOSED
Inputs:
  - LLM client construction pattern at lines ~298-314
  - Grade cache pattern at lines ~40, ~80-110
  - Per-item grading loop (identify exact location in grade_all)
Expected output:
  New helper: _grade_item_shadow(item, inspection_item, shadow_provider, sprint_id) -> None
    - Constructs second LLM client for shadow_provider endpoint
    - Calls same grading logic as stable path (reuse _grade_item if extractable)
    - Writes to GRADER_SHADOW_LOG_PATH (.local/supervisor/grader-shadow-log.jsonl)
    - Writes to shadow cache (.local/supervisor/grader-shadow-cache.json)
    - All failures: catch Exception, log {"error": str(e), "agreement": null}, return
    - Never raises; never affects review dict
  Call site in grade_all: after stable grade stored, if shadow_provider:
    _grade_item_shadow(item, inspection_item, shadow_provider, sprint_id)
Evidence:
  - With --shadow-provider set: grader-shadow-log.jsonl populated with correct fields
  - With --shadow-provider absent: grader-shadow-log.jsonl NOT written to
  - Sprint verdict identical with and without --shadow-provider on same declaration
Next valid task: TC-GRADER-001-03
```

Micro-steps:
- MS-GRADER-001-02-01 [PENDING]: Read `tools/supervisor/grade_declared_work.py` lines 640-730 (grade_all and per-item grading). Identify: the per-item loop structure, where stable grade result is stored, the LLM client construction code that can be reused.
- MS-GRADER-001-02-02 [PENDING]: Add `GRADER_SHADOW_LOG_PATH` constant to module.
- MS-GRADER-001-02-03 [PENDING]: Write `_write_grader_shadow_entry(entry: dict) -> None` — appends JSON line to `GRADER_SHADOW_LOG_PATH`, non-fatal on failure.
- MS-GRADER-001-02-04 [PENDING]: Write `_grade_item_shadow(item_id, evidence_hash, shadow_provider, sprint_id, stable_grade) -> None`. Body: look up shadow cache first (key: `f"{item_id}:{evidence_hash}:shadow:{shadow_provider}"`); if cache hit, use cached grade; else call shadow provider LLM; write to shadow cache; call `_write_grader_shadow_entry({...})`. Entire body in try/except.
- MS-GRADER-001-02-05 [PENDING]: Add call to `_grade_item_shadow()` in the per-item grading loop: after stable grade is stored, check `if shadow_provider:` and call with correct args.
- MS-GRADER-001-02-06 [PENDING]: Test isolation: run grader without `--shadow-provider` on a test declaration (use existing evidence fixture if available). Verify `grader-shadow-log.jsonl` not written. Record evidence.
- MS-GRADER-001-02-07 [PENDING]: If shadow provider credentials are available: run with `--shadow-provider` and verify `grader-shadow-log.jsonl` populated. If credentials unavailable: create a mock test in TC-TEST-002 that patches the LLM call.

#### TC-GRADER-001-03: Create tools/canary/grader_promotion.py
```
Type:     CHILD
Parent:   TC-GRADER-001
Status:   TODO
Source:   REQ-IMPL-005
Purpose:  CLI for reviewing shadow grading observations and getting a
          data-driven recommendation on whether the shadow provider is
          safe to promote as the primary provider.
Scope:
  Allowed: tools/canary/grader_promotion.py (create)
  Forbidden: grade_declared_work.py, shadow log files (read-only)
Expected output:
  CLI: python tools/canary/grader_promotion.py summary --shadow-provider <id>
  Reads grader-shadow-log.jsonl, filters by shadow_provider.
  Prints:
    Observations: N items
    Agreement rate: X% (n/N)
    Stable→Shadow upgrades (REWORK→ACCEPTED): n_upgrades
    Stable→Shadow downgrades (ACCEPTED→REWORK): n_downgrades
    Failed shadow calls: n_failed
    Recommendation: PROMOTE | HOLD | INSUFFICIENT_DATA
  Recommendation logic:
    INSUFFICIENT_DATA if N < 10
    HOLD if n_downgrades > 0 (any downgrade warrants review)
    PROMOTE if n_downgrades == 0 and agreement_rate >= 0.90 and N >= 10
Evidence:
  - python tools/canary/grader_promotion.py summary --shadow-provider test → prints expected fields
  - With seeded log data: recommendations match expected logic
Next valid task: TC-TEST-002
```

Micro-steps:
- MS-GRADER-001-03-01 [PENDING]: Write `tools/canary/grader_promotion.py`. Structure: imports (argparse, json, pathlib, collections); `GRADER_SHADOW_LOG_PATH` constant; `load_observations(shadow_provider)` reads JSONL and filters; `compute_summary(observations)` returns dict with agreement rate, upgrade/downgrade counts; `recommend(summary)` applies recommendation logic; `cmd_summary(args)` formats and prints; `main()` with argparse; entry point.
- MS-GRADER-001-03-02 [PENDING]: Test with seed data: create a temp JSONL file with 15 fake entries (12 agree, 3 disagree, 2 downgrades). Run `summary` command. Verify: Agreement rate = 12/15 = 80%, Recommendation = HOLD (downgrades present).
- MS-GRADER-001-03-03 [PENDING]: Test INSUFFICIENT_DATA path: run with empty log or N < 10. Verify: prints INSUFFICIENT_DATA.

---

### TC-DIFF-001: Compilation Diff Tool
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-IMPL-006, REQ-RDSGN-003
Objective: Create tools/canary/compilation_diff.py — a pure comparison tool
           that diffs gap compilation output before/after scoring algorithm
           changes. No state mutation. No dependencies on other canary tools.
Scope:
  Allowed: tools/canary/compilation_diff.py (create)
  Forbidden: capability_feature_compiler.py, gap-ledger.json
Dependencies: TC-INIT-001 (package exists)
Children:
  - TC-DIFF-001-01: Create compilation_diff.py
Parent acceptance criteria:
  - Running diff twice on same ledger with same module produces empty change lists
  - Running diff with modified scoring function detects priority changes
Closeout: child CLOSED, both acceptance criteria met
```

#### TC-DIFF-001-01: Create tools/canary/compilation_diff.py
```
Type:     CHILD
Parent:   TC-DIFF-001
Status:   TODO
Source:   REQ-IMPL-006
Purpose:  Pure function that imports stable and candidate compiler modules,
          runs both on the same gap ledger, and diffs the outputs.
Scope:
  Allowed: tools/canary/compilation_diff.py (create)
  Forbidden: all other files
Expected output:
  CLI:
    python tools/canary/compilation_diff.py \
      --ledger reports/capability-layer/gap-ledger.json \
      [--candidate-module tools.supervisor.capability_feature_compiler_candidate] \
      --output reports/canary/compilation-diff-YYYYMMDD.yaml
  Default (no --candidate-module): stable vs stable (idempotency check, expects empty diff)
  With --candidate-module: stable vs candidate
  Output YAML fields: comparison_date, stable_module, candidate_module,
    total_stable_items, total_candidate_items, priority_changes (list),
    format_coverage_changes (list), new_items_surfaced (list), items_dropped (list),
    recommendation (str: SAFE_TO_DEPLOY | REVIEW_REQUIRED | HOLD)
  recommendation logic:
    SAFE_TO_DEPLOY if len(priority_changes)==0 and len(format_coverage_changes)==0
    REVIEW_REQUIRED if len(priority_changes) > 0 or len(format_coverage_changes) > 0
    HOLD if len(items_dropped) > 0 (loss of coverage is serious)
Evidence:
  - python tools/canary/compilation_diff.py --ledger ... --output /tmp/test.yaml → exit 0
  - Output YAML has all required fields
  - Running twice produces identical output (pure function)
  - With identical modules: priority_changes = [], format_coverage_changes = []
Next valid task: TC-TEST-001 (tests can now be written)
```

Micro-steps:
- MS-DIFF-001-01-01 [PENDING]: Read `tools/supervisor/capability_feature_compiler.py` lines 1-50 and 240-280 to understand: how `compile_gaps()` is called, what the output structure is, and whether the module can be imported and called without side effects.
- MS-DIFF-001-01-02 [PENDING]: Write `tools/canary/compilation_diff.py`. Structure: imports (argparse, importlib, json, yaml, pathlib, datetime); `load_compiler(module_path)` uses importlib.import_module; `run_compiler(compiler_module, ledger_path)` calls `compiler_module.compile_gaps()` or equivalent; `diff_outputs(stable, candidate)` computes priority_changes and format_coverage_changes; `write_output(diff, output_path)` writes YAML; `main()` with argparse; entry point.
- MS-DIFF-001-01-03 [PENDING]: Test idempotency: `python tools/canary/compilation_diff.py --ledger reports/capability-layer/gap-ledger.json --output /tmp/diff-test.yaml`. Check: priority_changes is empty list (or has exactly the changes expected), recommendation is SAFE_TO_DEPLOY. Record output.
- MS-DIFF-001-01-04 [PENDING]: Test that second run produces identical output: compare output files byte-for-byte (excluding comparison_date field). Record pass.

---

### TC-TEST-001: Validator Shadow Test Suite
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-TEST-001/003
Objective: Create tests/canary/test_validator_shadow.py (8 tests) and
           tests/canary/test_schema_migration.py (4 tests).
Scope:
  Allowed:
    tests/canary/__init__.py (create)
    tests/canary/test_validator_shadow.py (create)
    tests/canary/test_schema_migration.py (create)
  Forbidden: modifying any existing test files
Dependencies:
  TC-REGISTRY-001 CLOSED (shadow system exists)
  TC-VALCLI-001 CLOSED (promotion CLI exists)
  TC-SCHEMA-001 CLOSED (migration exists)
Children:
  - TC-TEST-001-01: Create tests/canary/__init__.py and test_validator_shadow.py
  - TC-TEST-001-02: Create tests/canary/test_schema_migration.py
Parent acceptance criteria:
  .venv/Scripts/pytest tests/canary/test_validator_shadow.py -v → 8 PASS
  .venv/Scripts/pytest tests/canary/test_schema_migration.py -v → 4 PASS
Closeout: both children CLOSED, all 12 tests pass
```

#### TC-TEST-001-01: Create test_validator_shadow.py
```
Type:     CHILD
Parent:   TC-TEST-001
Status:   TODO
Source:   REQ-TEST-001, REQ-REGR-001/002
Purpose:  8 focused tests covering the shadow registry round-trip, routing,
          isolation, and promotion lifecycle.
Scope:
  Allowed: tests/canary/__init__.py (create), tests/canary/test_validator_shadow.py (create)
  Forbidden: modifying governance_validator_runner.py in tests (use tmp_path fixtures)
```

Micro-steps:
- MS-TEST-001-01-01 [PENDING]: Create `tests/canary/__init__.py` (empty).
- MS-TEST-001-01-02 [PENDING]: Write `tests/canary/test_validator_shadow.py` with 8 test functions:
  1. `test_shadow_registry_loads_empty` — point `_load_shadow_registry` at tmp empty file; verify returns `{}`
  2. `test_shadow_registry_missing_file` — point at non-existent path; verify returns `{}` (fail-safe)
  3. `test_shadow_registry_loads_entry` — write tmp registry with one entry; verify dict has one key
  4. `test_shadow_routing_neutralizes_blocks_sprint` — mock a FAIL result with `blocks_sprint=True`; inject into shadow registry; call routing code; verify `blocks_sprint=False` in result
  5. `test_shadow_routing_preserves_pass_result` — PASS result with registry entry; verify PASS result untouched
  6. `test_shadow_routing_non_shadow_validator_still_blocks` — validator NOT in registry; FAIL with `blocks_sprint=True`; verify result `blocks_sprint=True` unchanged
  7. `test_shadow_log_written` — mock `_write_shadow_log_entry`; trigger shadow suppression; verify mock called with correct fields
  8. `test_promote_command_changes_mode` — run `validator_promotion.py promote` on tmp registry; verify mode changed to "blocking" in YAML
- MS-TEST-001-01-03 [PENDING]: Run: `.venv/Scripts/pytest tests/canary/test_validator_shadow.py -v`. All 8 must pass. Record output as evidence.

#### TC-TEST-001-02: Create test_schema_migration.py
```
Type:     CHILD
Parent:   TC-TEST-001
Status:   TODO
Source:   REQ-TEST-003, REQ-REGR-004
Purpose:  4 tests for v3 migration correctness and idempotency.
```

Micro-steps:
- MS-TEST-001-02-01 [PENDING]: Write `tests/canary/test_schema_migration.py` with 4 test functions:
  1. `test_v3_migration_creates_both_tables` — call `init_db(tmp_db)`, query `sqlite_master`, verify both `validator_shadow_observations` and `grader_shadow_observations` tables exist
  2. `test_v3_migration_idempotent` — call `init_db(tmp_db)` twice; verify no error and tables still exist
  3. `test_v3_schema_version_is_3` — after init_db, call `get_schema_version(tmp_db)`; verify equals 3
  4. `test_v3_table_insert_and_query` — insert one row into each table, query back, verify all fields round-trip correctly; include test of nullable columns (shadow_grade=None for failed shadow call)
- MS-TEST-001-02-02 [PENDING]: Run: `.venv/Scripts/pytest tests/canary/test_schema_migration.py -v`. All 4 must pass. Record output.

---

### TC-TEST-002: Grader and Compilation Diff Test Suite
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-TEST-002/004
Objective: Create tests/canary/test_grader_shadow.py (5 tests) and
           tests/canary/test_compilation_diff.py (4 tests).
Dependencies:
  TC-GRADER-001 CLOSED
  TC-DIFF-001 CLOSED
Children:
  - TC-TEST-002-01: Create test_grader_shadow.py
  - TC-TEST-002-02: Create test_compilation_diff.py
Parent acceptance criteria:
  .venv/Scripts/pytest tests/canary/test_grader_shadow.py -v → 5 PASS
  .venv/Scripts/pytest tests/canary/test_compilation_diff.py -v → 4 PASS
Closeout: both children CLOSED, all 9 tests pass
```

#### TC-TEST-002-01: Create test_grader_shadow.py
```
Type:     CHILD
Parent:   TC-TEST-002
Status:   TODO
Source:   REQ-TEST-002, REQ-REGR-003
```

Micro-steps:
- MS-TEST-002-01-01 [PENDING]: Write `tests/canary/test_grader_shadow.py` with 5 test functions:
  1. `test_shadow_grade_does_not_affect_sprint_verdict` — mock shadow provider call to return "REWORK_REQUIRED"; run grading with stable provider returning "ACCEPTED_VERIFIED"; verify sprint verdict is "ACCEPTED_VERIFIED" (shadow has no influence)
  2. `test_shadow_grade_logs_comparison` — mock both providers; run grade with shadow; verify grader-shadow-log.jsonl populated with correct fields (item_id, stable_grade, shadow_grade, agreement bool)
  3. `test_shadow_provider_failure_is_non_blocking` — mock shadow provider to raise ConnectionError; run grading; verify sprint verdict unaffected, log entry has error field, no exception propagated
  4. `test_shadow_cache_uses_different_namespace` — set up shadow cache with known entry; verify its key includes `:shadow:{provider}` suffix; verify stable cache not contaminated
  5. `test_grader_promotion_summary_correct` — write seeded grader-shadow-log.jsonl with 10 agree + 2 disagree + 1 downgrade; run grader_promotion.py summary; verify: Agreement rate = 10/13, n_downgrades = 1, Recommendation = HOLD
- MS-TEST-002-01-02 [PENDING]: Run: `.venv/Scripts/pytest tests/canary/test_grader_shadow.py -v`. All 5 must pass.

#### TC-TEST-002-02: Create test_compilation_diff.py
```
Type:     CHILD
Parent:   TC-TEST-002
Status:   TODO
Source:   REQ-TEST-004
```

Micro-steps:
- MS-TEST-002-02-01 [PENDING]: Write `tests/canary/test_compilation_diff.py` with 4 test functions:
  1. `test_diff_identical_runs_produces_empty_changes` — run stable vs stable on a small synthetic gap ledger (5 gaps); verify priority_changes=[], format_coverage_changes=[]
  2. `test_diff_detects_priority_reordering` — create two mock compiler functions with different scoring; verify priority_changes contains the reordered gap
  3. `test_diff_detects_format_entering_coverage` — candidate includes an extra format in top-N; verify format_coverage_changes contains it
  4. `test_diff_is_pure_no_state_mutation` — run diff twice on same inputs; verify: (a) output YAML is byte-for-byte identical (modulo comparison_date), (b) gap-ledger.json unchanged (check sha256 before and after)
- MS-TEST-002-02-02 [PENDING]: Run: `.venv/Scripts/pytest tests/canary/test_compilation_diff.py -v`. All 4 must pass.

---

### TC-CLOSE-001: Integration Validation and Closeout
```
Type:     PARENT
Status:   PROPOSED
Owner:    execution agent
Source:   REQ-REGR-001/002/003/004, mission prompt §15
Objective: Run all validation steps, regression controls, and produce the
           final benefit assessment YAML. Prove idempotency.
Dependencies: ALL other parent taskcards CLOSED
Children:
  - TC-CLOSE-001-01: Schema and ingestor validation (Step 1)
  - TC-CLOSE-001-02: Validator shadow round-trip (Steps 2–3)
  - TC-CLOSE-001-03: Grader shadow validation (Step 4)
  - TC-CLOSE-001-04: Compilation diff validation (Step 5)
  - TC-CLOSE-001-05: Full test suite + regression controls (Step 6)
  - TC-CLOSE-001-06: Second-run idempotency proof (Step 7)
  - TC-CLOSE-001-07: Produce canary-benefit-assessment.yaml
Parent acceptance criteria:
  All 7 children CLOSED.
  reports/canary/canary-benefit-assessment.yaml exists.
  Final verdict: CANARY_CONTROL_INTEGRATED_PILOT_PROVEN_AND_IDEMPOTENT
Closeout: all 7 children CLOSED, final verdict written to architecture-decision YAML
```

#### TC-CLOSE-001-01: Schema migration end-to-end validation
```
Status: TODO
Purpose: Validate the SQLite v3 migration from scratch and confirm queryability.
```
Micro-steps:
- MS-CLOSE-001-01-01 [PENDING]: Run `python -m tools.supervisor.control_index init`. Expect exit 0.
- MS-CLOSE-001-01-02 [PENDING]: Run `python -m tools.supervisor.control_index status`. Verify output contains `schema_version: 3` and lists both new tables.
- MS-CLOSE-001-01-03 [PENDING]: Run `python -m tools.supervisor.control_index.query shadow-status`. Verify command runs without error (may show 0 observations — acceptable).
- MS-CLOSE-001-01-04 [PENDING]: Run full sync: `python -m tools.supervisor.control_index sync`. Expect exit 0, no ingestor errors, `canary_shadow` entity type listed in sync report. Record sync report.

#### TC-CLOSE-001-02: Validator shadow round-trip
```
Status: TODO
Purpose: Validate the complete shadow promotion lifecycle end-to-end.
```
Micro-steps:
- MS-CLOSE-001-02-01 [PENDING]: Add V143 to shadow mode: `python tools/canary/validator_promotion.py shadow --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM --threshold 5`. Verify `.supervisor/validator-shadow-registry.yaml` now contains the entry.
- MS-CLOSE-001-02-02 [PENDING]: Run governance validators: `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v`. Expect all 167 pass. Confirm V_VALIDATE_ORACLE_DEPTH_MINIMUM result is in output (runs but does not block).
- MS-CLOSE-001-02-03 [PENDING]: Check shadow log was written: `python -c "import json; lines=[json.loads(l) for l in open('.local/supervisor/validator-shadow-log.jsonl') if 'ORACLE_DEPTH' in l]; print(len(lines), 'V143 entries')"`. Expect ≥ 0 entries (may be 0 if no D0-only formats in current test declarations — acceptable; log write mechanism is verified in unit tests).
- MS-CLOSE-001-02-04 [PENDING]: Check observation status: `python tools/canary/validator_promotion.py status --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM`. Record output.
- MS-CLOSE-001-02-05 [PENDING]: Promote: `python tools/canary/validator_promotion.py promote --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM`. Verify registry entry mode = "blocking".
- MS-CLOSE-001-02-06 [PENDING]: Idempotent promote: run promote again. Verify exit 0 and "already blocking" message.
- MS-CLOSE-001-02-07 [PENDING]: Demote: `python tools/canary/validator_promotion.py demote --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM`. Verify mode = "shadow".
- MS-CLOSE-001-02-08 [PENDING]: Reset: remove V143 from registry (set `validator_shadow_entries: []`) to restore initial empty state.

#### TC-CLOSE-001-03: Grader shadow validation
```
Status: TODO
Purpose: Validate shadow grading flag exists and shadow log isolation works.
```
Micro-steps:
- MS-CLOSE-001-03-01 [PENDING]: Verify `--shadow-provider` flag is available: `python tools/supervisor/grade_declared_work.py --help | grep shadow-provider`. Expect found.
- MS-CLOSE-001-03-02 [PENDING]: If a shadow provider is configured in `tools/llm/endpoints.yaml`: run `python tools/supervisor/grade_declared_work.py --inspection <latest_inspection.json> --declaration <latest_declaration.yaml> --output-dir /tmp/grade-test --shadow-provider <provider>`. Verify sprint verdict unchanged; verify `grader-shadow-log.jsonl` populated.
- MS-CLOSE-001-03-03 [PENDING]: If no shadow provider configured: verify that running without `--shadow-provider` produces identical output to pre-change (compare output-dir structure and verdict). Record as evidence.
- MS-CLOSE-001-03-04 [PENDING]: Run `python tools/canary/grader_promotion.py summary --shadow-provider <provider>`. Verify command runs (may show INSUFFICIENT_DATA if < 10 observations — acceptable).

#### TC-CLOSE-001-04: Compilation diff validation
```
Status: TODO
Purpose: Validate the diff tool is pure and produces correct output.
```
Micro-steps:
- MS-CLOSE-001-04-01 [PENDING]: Run: `python tools/canary/compilation_diff.py --ledger reports/capability-layer/gap-ledger.json --output /tmp/diff-validation.yaml`. Expect exit 0.
- MS-CLOSE-001-04-02 [PENDING]: Verify output YAML: `python -c "import yaml; d=yaml.safe_load(open('/tmp/diff-validation.yaml')); print(d.keys()); assert 'priority_changes' in d; assert 'recommendation' in d"`. Expect all required fields present.
- MS-CLOSE-001-04-03 [PENDING]: Verify idempotency: run again, compare: `python tools/canary/compilation_diff.py --ledger reports/capability-layer/gap-ledger.json --output /tmp/diff-validation-2.yaml`. Compare priority_changes and format_coverage_changes between runs (ignore comparison_date field). Expect identical.
- MS-CLOSE-001-04-04 [PENDING]: Verify gap ledger not mutated: `python -c "import hashlib; print(hashlib.sha256(open('reports/capability-layer/gap-ledger.json','rb').read()).hexdigest())"` before and after. Expect identical hash.

#### TC-CLOSE-001-05: Full test suite and regression controls
```
Status: TODO
Purpose: All 21 new canary tests pass; all 167 governance validator tests pass;
         control index sync tests pass.
```
Micro-steps:
- MS-CLOSE-001-05-01 [PENDING]: Run all canary tests: `.venv/Scripts/pytest tests/canary/ -v`. Expect 21 PASS (8 + 5 + 4 + 4), 0 FAIL. Record output.
- MS-CLOSE-001-05-02 [PENDING]: Run governance validator regression: `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v`. Expect 167 validators confirmed (expected_count=167 assertion passes). Record output.
- MS-CLOSE-001-05-03 [PENDING]: Run control index sync tests: `.venv/Scripts/pytest tests/supervisor/test_control_index_sync.py -v`. Expect no regression — existing entity type counts unchanged or increased. Record output.
- MS-CLOSE-001-05-04 [PENDING]: Verify regression control REQ-REGR-002: confirm empty registry → no change to validator behavior. Run: `python -c "import sys; sys.path.insert(0,'tools/supervisor'); from governance_validator_runner import run_all_governance_validators; r=run_all_governance_validators({}); assert r.get('shadow_suppressions') == []"`. Expect pass.

#### TC-CLOSE-001-06: Second-run idempotency proof
```
Status: TODO
Purpose: Prove that running all implementation commands a second time
         produces no state mutations and no errors.
```
Micro-steps:
- MS-CLOSE-001-06-01 [PENDING]: Re-run `python -m tools.supervisor.control_index init`. Expect exit 0. Verify schema_version still 3 (no re-migration side effects).
- MS-CLOSE-001-06-02 [PENDING]: Re-run governance validator test. Expect same result as first run (still 167 pass).
- MS-CLOSE-001-06-03 [PENDING]: Re-run `python tools/canary/validator_promotion.py promote --validator V_VALIDATE_ORACLE_DEPTH_MINIMUM` (when already blocking). Expect "already blocking", exit 0.
- MS-CLOSE-001-06-04 [PENDING]: Re-run compilation diff: produce second output file. Compare priority_changes with first output. Expect identical list.
- MS-CLOSE-001-06-05 [PENDING]: Record: "MATERIAL_SECOND_RUN_CHANGES = 0" as explicit statement in closeout evidence.

#### TC-CLOSE-001-07: Produce canary-benefit-assessment.yaml
```
Status: TODO
Purpose: Record measured overhead, operational benefits, and costs.
         This is evidence of what the canary system actually costs to operate.
```
Micro-steps:
- MS-CLOSE-001-07-01 [PENDING]: Measure: time to run governance validators with empty registry vs with one shadow entry. Record millisecond overhead.
- MS-CLOSE-001-07-02 [PENDING]: Measure: new SQLite row counts from ingestor (validator_shadow_observations + grader_shadow_observations). Record storage overhead per sprint.
- MS-CLOSE-001-07-03 [PENDING]: Write `reports/canary/canary-benefit-assessment.yaml` with fields: `new_lines_of_code`, `new_files_created`, `existing_files_modified`, `validator_shadow_overhead_ms`, `grader_shadow_overhead_per_item_ms` (estimate or measured), `sqlite_rows_per_sprint`, `rollback_complexity`, `operational_model`, `recommendation`, `final_verdict: CANARY_CONTROL_INTEGRATED_PILOT_PROVEN_AND_IDEMPOTENT`.
- MS-CLOSE-001-07-04 [PENDING]: Update `reports/canary/canary-architecture-decision.yaml` to add `final_verdict` field matching benefit assessment.

---

## Taskcard State Machine

### Legal transitions — Parent
```
PROPOSED → READY              (guard: all prerequisite children have been identified)
READY → IN_PROGRESS           (guard: first child taskcard set to IN_PROGRESS)
IN_PROGRESS → CHILDREN_IN_PROGRESS (guard: at least one child IN_PROGRESS)
CHILDREN_IN_PROGRESS → INTEGRATION_PENDING (guard: all children CLOSED)
INTEGRATION_PENDING → VERIFIED (guard: parent acceptance criteria checked)
VERIFIED → SCORED             (guard: quality dimensions rated)
SCORED → CLOSED               (guard: all scores ≥ 4/5)
SCORED → REROUTED             (guard: any score < 4/5)
REROUTED → IN_PROGRESS        (guard: rework plan defined)
any → BLOCKED                 (guard: dependency blocked)
BLOCKED → READY               (guard: dependency resolved)
```

### Legal transitions — Child
```
TODO → READY                  (guard: parent IN_PROGRESS, preconditions met)
READY → IN_PROGRESS           (guard: first micro-step set ACTIVE)
IN_PROGRESS → IMPLEMENTED     (guard: all micro-steps COMPLETE)
IMPLEMENTED → VERIFIED        (guard: acceptance checks run and pass)
VERIFIED → SCORED             (guard: quality gates assessed)
SCORED → CLOSED               (guard: all required gates ≥ 4/5)
SCORED → REROUTED             (guard: any required gate < 4/5)
REROUTED → IN_PROGRESS        (guard: failing micro-steps reset to PENDING)
any → BLOCKED                 (guard: blocking dependency unresolved)
```

### Blocked invalid transitions
```
TODO → CLOSED                 BLOCKED
READY → CLOSED                BLOCKED
IMPLEMENTED → CLOSED          BLOCKED (must verify first)
parent CLOSED with child TODO BLOCKED
parent CLOSED with child BLOCKED BLOCKED
REROUTED → CLOSED without rework BLOCKED
```

### Quality gate minimum (all children)
```
requirement_correctness:    ≥ 4/5
implementation_correctness: ≥ 4/5
scope_discipline:           ≥ 4/5
validation_strength:        ≥ 4/5
evidence_completeness:      ≥ 4/5
regression_safety:          ≥ 4/5
```

If any gate < 4/5: mark child REROUTED, identify failing micro-step, reset to PENDING, re-execute.

---

## Validation Matrix

| Check | Command | Expected | Mandatory | TC |
|-------|---------|----------|-----------|-----|
| Schema version = 3 | `python -m tools.supervisor.control_index status` | `schema_version: 3` | YES | TC-SCHEMA-001 |
| Both shadow tables exist | See MS-SCHEMA-001-02-07 | table names in output | YES | TC-SCHEMA-001 |
| Shadow ingestor registered | `ALL_INGESTORS length == 17` | 17 | YES | TC-SCHEMA-001 |
| Registry loads empty | `_load_shadow_registry() == {}` | `{}` | YES | TC-REGISTRY-001 |
| Shadow routing neutralizes | See test 4 in TC-TEST-001-01 | blocks_sprint=False | YES | TC-REGISTRY-001 |
| Non-shadow validator still blocks | See test 6 in TC-TEST-001-01 | blocks_sprint=True | YES | TC-REGISTRY-001 |
| Shadow log written on FAIL | See test 7 in TC-TEST-001-01 | log entry exists | YES | TC-REGISTRY-001 |
| Governance validators: 167 pass | `.venv/Scripts/pytest test_governance_validators.py` | 167 PASS | YES | TC-CLOSE-001 |
| Promote changes mode | See MS-VALCLI-001-01-06 | mode: blocking | YES | TC-VALCLI-001 |
| Promote idempotent | Run promote twice | exit 0 both times | YES | TC-VALCLI-001 |
| Grader flag present | `grade_declared_work.py --help | grep shadow` | found | YES | TC-GRADER-001 |
| Shadow grade no verdict effect | See test 1 in TC-TEST-002-01 | verdict unchanged | YES | TC-GRADER-001 |
| Shadow failure non-blocking | See test 3 in TC-TEST-002-01 | no exception | YES | TC-GRADER-001 |
| Diff pure (no mutation) | See test 4 in TC-TEST-002-02 | same sha256 | YES | TC-DIFF-001 |
| Diff idempotent | Run diff twice, compare output | identical | YES | TC-DIFF-001 |
| All canary tests pass | `.venv/Scripts/pytest tests/canary/ -v` | 21 PASS | YES | TC-CLOSE-001 |
| Control index sync no regression | `.venv/Scripts/pytest test_control_index_sync.py` | existing counts ≥ pre-change | YES | TC-CLOSE-001 |
| Second run idempotent | Re-run all commands | no mutations | YES | TC-CLOSE-001 |

**Negative controls (things that must NOT happen):**

| Negative check | Mechanism | TC |
|----------------|-----------|-----|
| Shadow grade must NOT change sprint verdict | test 1 in TC-TEST-002-01 | TC-GRADER-001 |
| Shadow log write failure must NOT propagate | test 3 in TC-TEST-002-01 | TC-GRADER-001 |
| Missing registry file must NOT crash runner | test 2 in TC-TEST-001-01 | TC-REGISTRY-001 |
| Validator count must NOT decrease | test_governance_validators.py expected_count=167 | TC-CLOSE-001 |
| Gap ledger must NOT be mutated by diff tool | sha256 check in MS-CLOSE-001-04-04 | TC-DIFF-001 |
| Non-shadow FAIL must NOT be suppressed | test 6 in TC-TEST-001-01 | TC-REGISTRY-001 |

---

## Evidence Contract

Every child taskcard produces at least one evidence record. Evidence is not a file path — evidence is verified output content.

### Evidence obligations per taskcard group

```
TC-INV-001:     4 YAML files parsed cleanly; entry count assertions pass
TC-INIT-001:    import check output
TC-SCHEMA-001:  schema_version=3 output; both table names in sqlite_master; sync output
TC-REGISTRY-001: governance validator test output (167 pass); shadow log entry
TC-VALCLI-001:  registry file content after each command; help output
TC-GRADER-001:  help output with --shadow-provider; grader-shadow-log.jsonl entry or isolation proof
TC-DIFF-001:    diff output YAML; sha256 of gap-ledger before/after
TC-TEST-001:    pytest output: 12 pass (8 + 4)
TC-TEST-002:    pytest output: 9 pass (5 + 4)
TC-CLOSE-001:   full pytest run output; idempotency comparison; benefit-assessment.yaml
```

### Evidence structure (produced during TC-CLOSE-001)
```
.local/evidences/canary-001/
  evidence-declaration.yaml     — formal sprint declaration
  validator-shadow-test-run.txt — test_governance_validators.py output
  canary-test-run.txt           — tests/canary/ output
  schema-status.txt             — control_index status output
  shadow-log-sample.jsonl       — first 5 entries from validator-shadow-log.jsonl
  diff-baseline.yaml            — compilation_diff.py baseline output
  idempotency-comparison.txt    — second-run diff output
  benefit-assessment-ref.yaml   — reference to reports/canary/canary-benefit-assessment.yaml
```

---

## Regression Controls

**Governance validator count must remain 167:**
`tests/supervisor/test_governance_validators.py` asserts `expected_count = 167` (V149 added 2026-07-09; the plan previously cited 165 — this was a stale reference, now corrected). Any shadow-mode routing must NOT remove validators from the runner; it only redirects their blocking output. This test is the primary regression gate.

**Default blocking behavior unchanged when registry is empty:**
`test_shadow_registry_loads_empty` (TC-TEST-001-01 test 1) and `test_shadow_registry_missing_file` (test 2) are the regression controls. If registry is empty or missing, all validators run in blocking mode as before. No behavioral change.

**Evidence declaration grading verdict unchanged when no shadow provider configured:**
`test_shadow_grade_does_not_affect_sprint_verdict` (TC-TEST-002-01 test 1) is the regression control. `grade_declared_work.py` without `--shadow-provider` must produce identical output to the pre-change version.

**Control index row count must not decrease:**
Existing `test_control_index_sync.py` verifies ingestor entity types. Adding `canary_shadow` ingestor must not reduce counts for `format`, `capability`, `skill`, `layer`, `failure`, `plan_lock`, `source_violation`, `gap`, `qname`, `sprint`, or `event`.

---

## Tradeoffs and Limits — Honest Assessment

**What this design achieves:**
- Safe staged promotion path for the two highest-risk global-scope changes (validator blocking, grader provider)
- No new lifecycle; canary is an observation layer on the existing sprint loop
- Minimal new code (~115 LOC in existing files, ~250 LOC in new files)
- File authority model preserved; SQLite stays read-side
- Rollback is trivial (edit YAML config file)

**What this design does not achieve:**
- Automatic rollback when observations go bad — promotion and demotion are explicit CLI operations, not automated
- Shadow comparison for oracle depth promotion — this is not needed because oracle execution is already per-format isolated
- Canary for product code changes (parser/writer rewrites) — this requires versioned Python packages that can coexist in the same venv, which is architecturally out of scope
- Cohort-aware work selection — the compilation diff tool shows impact before algorithm changes, but the gap ledger prioritization is still portfolio-wide after any commit
- The "wave" problem — oracle wave assignment (wave6.md) is a scheduling discipline issue. Canary cannot enforce scheduling discipline; only per-format execution controls can, and those already exist in oracle executor's `--format` flag

**Risks that remain after this design:**
- A validator promoted from shadow to blocking may still trigger widespread sprint failures if the finding rate was under-represented in the shadow observation set (e.g., only 3 formats tested in shadow, 17 others have the violation too). Mitigation: the shadow registry should specify `format_scope` explicitly, not `["*"]` when unknown. V2 per-format scope is a future extension.
- The grader shadow call adds API cost and latency. If the shadow provider is unavailable, the sprint continues normally, but if cost controls are strict this needs a budget gate.
- The compilation diff tool is only useful if someone runs it before committing scoring algorithm changes. There is no automated enforcement of this discipline. It is a tool, not a gate.

**Where evidence is weak:**
- It is not yet known whether grader shadow disagreement rates are high enough to justify the API cost. Measure over 10 sprints before deciding whether shadow grading is worth keeping.
- The validator shadow threshold of 5 sprints is a heuristic. The right threshold depends on sprint cadence and typical finding rate. It may need tuning.

**The limit of canary control in this architecture:**
Canary control is most valuable when you can run both stable and candidate on the same inputs and compare outputs. In this system, most operations are already per-format isolated (oracle, gate execution, phase locks). The remaining portfolio-wide operations (validator blocking, grader, compilation) are the right targets. Attempting to extend canary further would add complexity without proportional safety benefit.

---

## What Deferred Work Looks Like (explicit scope boundary)

NOT part of this plan:

- **Per-format scope in shadow registry (V2):** `format_scope: ["fods", "csv"]` instead of `["*"]`. Requires extracting primary format from declaration work items.
- **Format-cohort aware work selection:** Extending `product_task_selector.py` to respect wave assignment. Requires `canary_cohort` field in `continuation-signal.json`.
- **Versioned product package canary:** Running old and new FODS parser side-by-side. Requires Docker isolation or PEP 517 editable installs.
- **Cross-language parity shadow:** Extending `cross_platform_parity_runner.py` beyond CSV.
- **Automated promotion from shadow to blocking:** Triggered by `check_continuation.py` when observation threshold is met. Adds automation but adds a new failure mode. Defer until manual promotion cycle is proven.
- **Compilation diff enforcement gate:** Making it a required pre-commit check. Currently it is a tool only.

---

## Execution Handoff

The execution agent receiving this plan must:

1. **Start by reading this plan file in full** before touching any files.
2. **Execute TC-INV-001 first** (discovery reports — no file system risk, parallel-safe).
3. **Execute TC-INIT-001** to create the `tools/canary/` package.
4. **Then run TC-SCHEMA-001 and TC-REGISTRY-001 in parallel** (different file ownership).
5. **Then run TC-GRADER-001 and TC-DIFF-001 in parallel** (different file ownership).
6. **Then run TC-VALCLI-001** (depends on TC-REGISTRY-001).
7. **Then run TC-TEST-001 and TC-TEST-002 in parallel** (after their respective dependencies close).
8. **Finally run TC-CLOSE-001** (all other parents must be CLOSED).

For each micro-step:
- Confirm the preconditions are met before starting
- Execute exactly the action specified — no broader scope
- Capture the evidence output immediately
- Update the micro-step status to COMPLETE or FAILED
- If FAILED: mark the child taskcard BLOCKED, record failure reason, do NOT proceed to next micro-step in the same child
- After all micro-steps COMPLETE: run acceptance checks and mark child VERIFIED
- After all children VERIFIED: run parent integration checks and mark parent INTEGRATION_PENDING → VERIFIED → SCORED → CLOSED

**Stop conditions (legitimate):**
- Any test that cannot be made to pass after one repair attempt → mark child REROUTED, surface failure to user
- Any governance validator count drop below 167 → STOP, do not proceed
- Any change to stable grade verdict without `--shadow-provider` → STOP, revert changes to `grade_declared_work.py`

**The execution agent must NOT:**
- Combine work from two different children in one step
- Mark a parent CLOSED before all children are CLOSED
- Skip the acceptance checks at the end of each child
- Treat test existence as test passing (tests must be run and output captured)
- Modify any file not listed in the Scope field of the child taskcard

---

## Execution Artifacts (produced during execution, not during planning)

All supporting analysis artifacts required by the meta-taskcardization prompt are produced during execution and stored at:

```
reports/canary/taskcardization/
  taskcardization-preflight.md          (authority: this plan file)
  section-processing-ledger.yaml        (authority: this plan file)
  plan-part-deep-analysis.yaml          (authority: this plan file)
  actionable-item-extraction-log.yaml   (authority: this plan file)
  solution-options-analysis.md          (authority: this plan file)
  normalized-requirements-inventory.yaml (authority: REQ-* registry in this plan)
  execution-dag.yaml                    (authority: §Execution Control Layer)
  taskcard-dependency-matrix.csv        (authority: §Execution Control Layer)
  file-ownership-and-locks.yaml         (authority: Scope fields in each child)
  validation-command-matrix.yaml        (authority: §Validation Matrix)
  evidence-obligation-matrix.csv        (authority: §Evidence Contract)
  taskcard-state-machine.yaml           (authority: §Taskcard State Machine)
  idempotency-check.md                  (authority: TC-CLOSE-001-06)
  execution-readiness-verdict.md        (produced as part of TC-CLOSE-001)
```

All artifacts reference:
```yaml
authoritative_plan: C:\Users\prora\.claude\plans\clever-tickling-island.md
artifact_role: analysis_or_evidence_only
execution_authority: false
```

---

## Summary

The system has extensive existing controls (167 validators, per-format oracle, phase locks, authority gates, plan locks, continuation isolation). Most operations that look like canary candidates are already naturally isolated at the format or sprint level.

The two genuine canary problems are: (1) governance validator promotions apply portfolio-wide with no staged test, and (2) LLM grader provider switches have no shadow comparison period. Both are solved here by adding shadow observation layers to existing execution paths, backed by two SQLite tables and two new CLI tools.

The compilation diff tool addresses the third problem (priority algorithm changes) as a pure comparison utility without a state machine.

**Implementation scope:** ~115 LOC added to existing files, ~250 LOC in new files, 1 YAML config, 1 SQL migration, 1 ingestor, 4 test files.

**Taskcards:** 9 parents, 31 children, ~105 micro-steps.

---

## Audit Taskcard Status (lifecycle_audit.py format)

| TC-ID | Status |
|---|---|
| TC-INV-001 | CLOSED |
| TC-INIT-001 | CLOSED |
| TC-SCHEMA-001 | CLOSED |
| TC-REGISTRY-001 | CLOSED |
| TC-VALCLI-001 | CLOSED |
| TC-GRADER-001 | CLOSED |
| TC-DIFF-001 | CLOSED |
| TC-TEST-001 | CLOSED |
| TC-TEST-002 | CLOSED |
| TC-CLOSE-001 | CLOSED |

**Final verdict target:** `CANARY_CONTROL_INTEGRATED_PILOT_PROVEN_AND_IDEMPOTENT`


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-13T14:34:28.776139+00:00"
  locked_by: "c0d42e113626"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
