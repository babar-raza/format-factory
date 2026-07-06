# Rectification Plan: Deep Recon Gaps — Revised Against Current System State

authoritative_plan: plans/.claude/partitioned-chasing-puzzle.md
last_verified: 2026-07-06

---

## A. Current-State Reassessment

The previous version of this plan was written before independently verifying current HEAD. Several items have since been completed by the system's own sprint pipeline. The plan below reflects only work that remains genuinely necessary.

### What Was Verified During Reassessment

| Item | File / Tool | Finding |
|---|---|---|
| `generate_root_status.py` counting method | `tools/readme_sync/generate_root_status.py` lines 41-55 | **ALREADY FIXED** — now reads `expected_count` from runner, not grep |
| `load_selected_product_gaps` bug | `tools/supervisor/generate_supervisor_packet.py` lines 175-181 | **ALREADY FIXED** — has `isinstance(payload, dict)` guard |
| `.gitattributes` linguist rules | `.gitattributes` (repo root) | **ALREADY EXISTS** — has `reports/**`, `.local/**`, `*.jsonl`, oracle reports |
| 05-GAPS recon corrections | `docs/system-recon/.../05-GAPS-CONTRADICTIONS-AND-OPEN-QUESTIONS.md` | **ALREADY APPLIED** — ISSUE-LANG-002, ISSUE-DISC-002, ISSUE-DOC-001 all annotated with VERIFIED/INCORRECT headers |
| MEMORY.md validator count | `memory/MEMORY.md` line 86 | **CORRECT** — says "161 total; test asserts 161; expected_count=161 in runner" |
| README validator count | `README.md` line 7, 45, 205, 255, 270, 278 | **STALE** — says "101" in 6 places |
| README skill count | `README.md` line 46, 270 | **STALE** — says "120 registered" |
| Canonical validator count | `test_canonical_validator_count` line 1821 | **161** (not 129 as the plan's initial draft stated — system grew since initial analysis) |
| grep `def validate_*` count | All governance_validators*.py | **156** across 20 files (was 153/18 earlier — 2 new modules added) |
| 01-SYSTEM-OVERVIEW.md accuracy | User's highlighted file | **HAS ERRORS** — "No CI for .NET" in section 28 item 6; inconsistent validator counts (153 in L12 table, 161 in strengths/CLM) |

---

## B. Item-by-Item Status of Previous Plan

| Taskcard | Status | Evidence | Remaining |
|---|---|---|---|
| TC-RC1-001-01 (fix generate_root_status.py) | **DONE** | Lines 41-55 read from `expected_count` in runner | Nothing |
| TC-RC1-001-02 (update README counts) | **UNRESOLVED** | README still says 101, 120 in 6+ places | Full update needed: 101→161, 120→123, 11 modules→20 modules |
| TC-RC1-001-03 (add CI drift gate) | **UNRESOLVED** | No `readme-drift` job in ci.yml | Needs adding |
| TC-RC1-001-04 (update MEMORY.md) | **DONE** | Line 86 already says "161 total; test asserts 161" | Nothing |
| TC-RC1-001-05 (sync capabilities) | **OUT OF SCOPE** | Capability sync is a separate sprint-pipeline concern | Remove |
| TC-RC1-002 (verify sprint count) | **UNRESOLVED** | Not checked | Still needed |
| TC-RC2-001-01 (fix load_selected_product_gaps) | **DONE** | Lines 178-179 have isinstance guard | Nothing |
| TC-RC2-001-02 (audit all load_json loaders) | **UNRESOLVED** | Only the one site was fixed | Audit still needed |
| TC-RC3-001-01 (gitattributes linguist rules) | **DONE** | `.gitattributes` exists with comprehensive rules | Nothing |
| TC-RC3-001-02 (evidence cleanup in autonomous_cycle) | **UNRESOLVED** | Not yet added | Still needed |
| TC-RC3-002 (plan lock recovery docs) | **UNRESOLVED** | Not checked | Still needed |
| TC-RC4-001 (correct 05-GAPS recon doc) | **DONE** | Corrections already applied | Nothing |
| TC-MISC-001 (CSV namespace shadow docs) | **UNRESOLVED** | Not yet documented | Still needed |
| TC-MISC-002 (test count clarification) | **DONE** | README line 408 already has disclaimer | Nothing |

**New issue identified during reassessment:**
`01-SYSTEM-OVERVIEW.md` (the user's selected file) has uncorrected errors that need fixing as part of this work. Added as TC-NEW-001.

---

## C. Remaining Problems

### P-1: README Counts Are Stale (6 locations)

**Root cause:** `generate_root_status.py` can detect drift and now counts correctly (161), but it is only called non-blockingly from `autonomous_cycle.py`. No CI gate blocks merges when README diverges.

**Impact:** Every reader of README.md sees incorrect validator count (101 vs 161 — 60 validators off). Skill count also wrong (120 vs 123).

**Exact locations in README.md:**
- Line 7: "101 governance validators across 11 modules" — should be "161 governance validators across 20 modules"
- Line 45 (L12 row): "101 programmatic validators" — should be "161 programmatic validators"
- Line 46 (L13 row): "120 registered skill definitions" — should be "123 registered skill definitions"
- Line 205: "101 programmatic governance validators across 11 modules" — should be "161 ... across 20 modules"
- Line 255: "101 programmatic validators across 11 modules" — should be "161 ... across 20 modules"
- Line 270: "101 governance validators, grade work items" — should be "161"
- Line 278: "governance_validators*.py — 101 programmatic quality gates across 11 modules" — should be "161 ... across 20 modules"

### P-2: No CI Enforcement of README Drift

**Root cause:** `generate_root_status.py --mode drift-only` exits 1 on drift, but no CI job calls it.

**Impact:** Count drift will recur — already happened 3 times (101 → 127 → 129 → 161) with no enforcement loop.

### P-3: Remaining load_json → .get() Sites Without isinstance Guards

**Root cause:** The `load_selected_product_gaps` fix was one instance of a systemic pattern. Other loaders in `tools/supervisor/` may still call `.get()` on unvalidated payloads.

**Impact:** Any state file that becomes a bare list (instead of dict) will cause AttributeError in unguarded callers.

### P-4: Evidence Directories Accumulate Unboundedly

**Root cause:** `.local/evidences/` has 3,449 run_id directories with no cleanup mechanism. `.gitattributes` correctly marks `.local/**` as linguist-generated, but the directories themselves are not pruned.

**Impact:** 3,449 directories currently. Grows ~1 per sprint. No constraint.

### P-5: 01-SYSTEM-OVERVIEW.md Has Incorrect and Inconsistent Claims

**Root cause:** The document was written during a single-pass recon and not re-verified after the system changed.

**Issues:**
- Section 28 item 6: "No CI for .NET: GitHub Actions only runs Python lint/test" — **INCORRECT** (ci.yml has a full `dotnet-build` job)
- L12 table (section 8): "153 programmatic validators | 18 modules" — should be "161 | 20 modules"
- Section 19: Validator module breakdown table totals 153 — two new modules (`governance_validators_contract.py`, `governance_validators_oracle.py`) are missing; total should be 161
- Section 27 strengths: says "161 canonical validators" — correct, but contradicts section 8 and 19

**Impact:** Internal inconsistency undermines trust in the document. Incorrect "No CI for .NET" claim may mislead contributors.

### P-6: Sprint Count Claim Unverified

**Root cause:** README claims "840 autonomous sprint cycles" — not yet cross-checked against `maturity-trend.json`.

**Impact:** Low — likely accurate directionally, but unverified.

---

## D. Revised Plan — Only Necessary Work

### TC-A: Update README Counts (P-1)

**Status:** TODO
**Priority:** High — most visible stale information
**Files:** `README.md`

**Micro-steps:**

MS-A-01: Verify canonical count by running `python tools/readme_sync/generate_root_status.py --mode drift-only --json`. Expected: `validator_count: 161`, `drifted: true`, `drifted_fields: ["validator_count"]`.

MS-A-02: Update line 7 (intro paragraph):
- Old: `101 governance validators across 11 modules`
- New: `161 governance validators across 20 modules`

MS-A-03: Update line 45 (L12 layer table row):
- Old: `101 programmatic validators`
- New: `161 programmatic validators`

MS-A-04: Update line 46 (L13 layer table row):
- Old: `120 registered skill definitions`
- New: `123 registered skill definitions`

MS-A-05: Update line 205 (Quality Gates section):
- Old: `101 programmatic governance validators across 11 modules`
- New: `161 programmatic governance validators across 20 modules`

MS-A-06: Update line 255 (Machinery Features section):
- Old: `101 programmatic validators across 11 modules`
- New: `161 programmatic validators across 20 modules`

MS-A-07: Update line 270 (Pipeline description):
- Old: `101 governance validators`
- New: `161 governance validators`

MS-A-08: Update line 278 (Key files list):
- Old: `101 programmatic quality gates across 11 modules`
- New: `161 programmatic quality gates across 20 modules`

MS-A-09: Verify no stale counts remain: search for `101 governance`, `101 programmatic`, `120 registered` — should return 0 matches.

MS-A-10: Run drift detector to confirm: `python tools/readme_sync/generate_root_status.py --mode drift-only` — should exit 0.

**Acceptance:** `generate_root_status.py --mode drift-only` exits 0. All 6 stale count locations updated.

**Rollback:** Revert README.md edits to prior values.

---

### TC-B: Add CI Drift Gate (P-2)

**Status:** TODO
**Priority:** High — prevents P-1 from recurring
**File:** `.github/workflows/ci.yml`

**Add a new job after the existing `governance-check` job:**

```yaml
  readme-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Check README drift
        run: python tools/readme_sync/generate_root_status.py --mode drift-only
```

`generate_root_status.py` exits 1 on drift → CI fails. The tool reads from the runner's `expected_count` field, so it will always use the canonical count.

**Micro-steps:**

MS-B-01: Read `.github/workflows/ci.yml` to find the correct insertion point (after `governance-check` job, before `dotnet-build`).

MS-B-02: Insert the `readme-drift` job.

MS-B-03: Verify the tool would pass with the corrected README by running locally after TC-A completes.

**Acceptance:** CI file has the new job. `generate_root_status.py --mode drift-only` exits 0 (after TC-A).

**Dependency:** TC-A must complete first (so the CI gate doesn't fail immediately on the stale count).

**Rollback:** Remove the `readme-drift` job if it causes false failures.

---

### TC-C: Audit Remaining load_json → .get() Sites (P-3)

**Status:** TODO
**Priority:** Medium — prevents crash class but no current active crash
**Files:** `tools/supervisor/*.py`

**Micro-steps:**

MS-C-01: Search for all call sites that call `.get(` within 5 lines of `load_json(` or `json.loads(` across all `tools/supervisor/*.py` files.

MS-C-02: For each hit, check whether an `isinstance(*, dict)` guard precedes the `.get()` call. Record unguarded sites.

MS-C-03: For each unguarded site, add the guard following the established pattern:
```python
if not isinstance(payload, dict):
    return payload if isinstance(payload, list) else {}
```

MS-C-04: Do not change the return contract of any function. Guards should return the same type as the function's declared return type (list → `[]`, dict → `{}`).

**Acceptance:** All `load_json()` → `.get()` chains in `tools/supervisor/*.py` have `isinstance(payload, dict)` guards. Existing behavior for correctly-shaped files is unchanged.

**Scope restriction:** Only `tools/supervisor/*.py`. Do not touch evidence declaration pipeline, check_continuation.py (separate concern), or test files.

---

### TC-D: Add Evidence Directory Cleanup (P-4)

**Status:** TODO
**Priority:** Low-Medium
**File:** `tools/supervisor/autonomous_cycle.py`

**Add a best-effort cleanup step at Step 7f (after the existing Step 7e README drift check):**

```python
# Step 7f: Evidence directory cleanup (non-blocking, best-effort)
try:
    import time
    import shutil
    evidence_root = repo_root / ".local" / "evidences"
    if evidence_root.is_dir():
        cutoff = time.time() - (30 * 86400)  # 30 days
        pruned = 0
        for d in evidence_root.iterdir():
            if d.is_dir() and d.stat().st_mtime < cutoff:
                shutil.rmtree(d, ignore_errors=True)
                pruned += 1
        if pruned > 0:
            print(f"  Pruned {pruned} evidence dirs older than 30 days")
except Exception as _cleanup_err:
    print(f"  WARNING: evidence cleanup failed (non-blocking): {_cleanup_err}")
```

**Retention policy:** 30 days. Evidence older than 30 days is never re-inspected in normal operation. Can be regenerated from work products if needed.

**Micro-steps:**

MS-D-01: Read `autonomous_cycle.py` around line 1706-1715 (Step 7e) to locate the insertion point.

MS-D-02: Insert the Step 7f cleanup block after Step 7e.

MS-D-03: Confirm the step uses `ignore_errors=True` and is wrapped in a try/except (non-blocking requirement).

**Acceptance:** Step 7f exists and is non-blocking. Old evidence dirs (>30 days) are removed on next sprint cycle.

---

### TC-E: Correct 01-SYSTEM-OVERVIEW.md (P-5)

**Status:** TODO
**Priority:** Medium — document is the user's highlighted file
**File:** `docs/system-recon/FF-DEEP-RECON-20260705-052931/01-SYSTEM-OVERVIEW.md`

**Micro-steps:**

MS-E-01: Fix section 8 (L12 layer table row):
- Old: `| L12 | Governance Layer | ... | 153 programmatic validators | 18 modules |`
- New: `| L12 | Governance Layer | ... | 161 programmatic validators | 20 modules |`

MS-E-02: Fix section 19 (Governance Validators module breakdown table):
- Current total: 153 (missing `governance_validators_contract.py` and `governance_validators_oracle.py`)
- Add `governance_validators_contract.py` row: 27 validators (registry-sourced, TC-BF-005)
- Add `governance_validators_oracle.py` row: 1 validator (V143 oracle depth minimum)
- Update table total from 153 to 161
- Update module count from 18 to 20

MS-E-03: Add correction annotation to section 28 item 6:
- Current: "No CI for .NET: GitHub Actions only runs Python lint/test"
- Add `~~` strikethrough and correction note: `~~No CI for .NET: GitHub Actions only runs Python lint/test~~ **INCORRECT — ci.yml has a full `dotnet-build` job that runs `dotnet restore`, `dotnet build`, and `dotnet test` for all .NET projects**`

MS-E-04: Verify section 27 (strengths) and CLM-GOV-003 already say 161 — they do; no change needed there.

**Acceptance:** All 3 corrections applied. Document is internally consistent on validator count. Section 28 item 6 is annotated as incorrect.

---

### TC-F: Verify Sprint Count (P-6)

**Status:** TODO
**Priority:** Low
**File:** `reports/supervisor/maturity-trend.json` → `README.md` if correction needed

**Micro-steps:**

MS-F-01: Read `reports/supervisor/maturity-trend.json` and check the `sprint_count` field.

MS-F-02: Compare against README line 7 claim ("840 autonomous sprint cycles").

MS-F-03: If `sprint_count` from source ≤ 840: no change needed (README says "Over 840" which is not a precise claim). If dramatically different (>20% growth), update README line 7 to current count.

**Acceptance:** Sprint count either confirmed as plausible or corrected.

---

### TC-G: Document CSV Namespace Shadow

**Status:** TODO
**Priority:** Low
**Target:** `src/python/csv/` (add README.md or note in `__init__.py`)

**Micro-steps:**

MS-G-01: Check if `src/python/csv/README.md` exists.

MS-G-02: Create or add to existing file:
```
## Known Issue: Package Name Shadows Python stdlib csv

The package directory is named `csv`, which shadows Python's built-in `csv` module
in certain import configurations. This was established early in the project and
renaming it would break hundreds of existing imports, tests, and oracle cases.

Workaround: import specific submodules directly:
    from csv.csv_parser import parse_csv_strict
    from csv.models import CsvDocument

Do not rename without a major version bump and a coordinated import migration.
```

**Acceptance:** Documentation exists for the known issue.

---

## Execution Order

```
TC-A (README counts)
  → TC-B (CI drift gate)       [depends on TC-A so gate doesn't fail immediately]

TC-C (audit loaders)            [independent]
TC-D (evidence cleanup)         [independent]
TC-E (01-SYSTEM-OVERVIEW.md)    [independent]
TC-F (sprint count)             [independent, fast]
TC-G (CSV docs)                 [independent, fast]
```

**Parallel-safe after TC-A completes:** TC-B, TC-C, TC-D, TC-E, TC-F, TC-G

---

## Validation Matrix

| Taskcard | Validation | Expected |
|---|---|---|
| TC-A | `python tools/readme_sync/generate_root_status.py --mode drift-only` | Exit 0, no drift |
| TC-A | `grep -n "101 governance\|101 programmatic\|120 registered" README.md` | 0 matches |
| TC-B | CI passes on a test push | `readme-drift` job passes |
| TC-C | `grep -c "\.get(" tools/supervisor/generate_supervisor_packet.py` vs isinstance guards | All guarded |
| TC-D | Check `autonomous_cycle.py` around line 1706 for Step 7f | Step exists, wrapped in try/except |
| TC-E | `grep "153 programmatic\|18 modules\|No CI for .NET" docs/system-recon/.../01-SYSTEM-OVERVIEW.md` | 0 matches (either corrected or struck through) |
| TC-F | `maturity-trend.json sprint_count` vs README | Consistent |

## Negative Controls

| Control | What It Prevents |
|---|---|
| CI readme-drift gate (TC-B) | Future count drift persisting unnoticed after new validators added |
| isinstance guards (TC-C) | AttributeError crashes when any state file is a bare list |
| Evidence cleanup (TC-D) | Unbounded .local/evidences/ accumulation |

## Tradeoffs and Limits

1. **TC-B adds a CI job** (~5-10s) to catch drift that was previously catching up at ~60 validators per gap. Worth it.
2. **TC-C is an audit, not a schema system.** Full JSON Schema enforcement for 58 state files is disproportionate. Type guards on `.get()` calls prevent the crash class specifically.
3. **TC-D 30-day cutoff is generous.** Can be shortened after observing impact. Deliberately conservative for the first deployment.
4. **TC-E corrects an observation document, not product source.** The recon docs are historical records — corrections are annotations, not rewrites.
5. **Validator count changes faster than documentation** — the gap went from 101 to 161 in ~60 days. The CI gate (TC-B) is the structural fix; manual count updates (TC-A) are an immediate repair.
