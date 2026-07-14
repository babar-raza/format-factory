# Portfolio Recon-and-Healing — Production-Grade Execution Plan

**Plan ID:** fizzy-imagining-hinton
**Mission:** PORTFOLIO-RECON-HEAL-20260627
**Authoritative Source Plan:** `plans/healing/portfolio-product-machinery-recon-and-healing-plan.md`
**Type:** machinery_hardening
**Status:** ACTIVE

---

## Diagnostic Summary — Why a Deeper Pass Was Needed

The original plan and initial plan draft had multiple structural failures that would reproduce false progress on re-run:

### Symptom → Root Cause Map

| Symptom | Root Cause |
|---|---|
| TC-W0-001 marked DONE with `TODO_GIT_REV` in receipt | Done-check was `grep "overclaim"` — trivially passes if word exists anywhere in file; proves nothing about runtime behavior |
| TC-W2-* targets 9 formats for "analytics extraction" | Source files named `text_document.py`, `bitmap_image.py`, etc. are ALREADY pure analytics modules; extraction already happened in prior sprints |
| TC-W2-001 targets `fods/spreadsheet_document.py` | File does not exist; FODS analytics are in different files; plan assumption is 2+ weeks stale |
| TC-W2-008 targets `sylk/spreadsheet_document.py` | File does not exist; SYLK already has `sylk_analytics.py` |
| TC-W3-* targets "monolith healing" | ABW/DIF/NDJSON/XCF already appear to be analytics files; ZST's `zst_codec.py` is the PRIMARY CODEC, not analytics, making LOC reduction by extraction architecturally risky |
| TC-W0-002 says "skip gaps failed in last 2 attempts within 48h" | `failure_memory.py` exists; `autonomous_task_generator.py` already integrates it; actual threshold is `occurrence_count >= 3` (ESCALATION_THRESHOLD), not 2; time window is sprint-count, not 48h |
| TC-W6-001 says consolidate `tools/supervisor/sprint_writers/` | Directory does not exist; sprint writer scripts are scattered across 234 files in `tools/supervisor/` |
| TC-W7-002 says "expand to ≥5 security test files" | 30 security/fuzz test files already exist across 18 formats; done-check would trivially pass immediately |
| TC-W5-001 says "verify all open gaps" | Only 16 gaps are open (gap ledger: 1495 total, 1447 closed); scope is far smaller than plan implies |
| Overclaim detector (TC-W0-001) | Wired in code but only executes when `reports/capability-layer/proof-graph/` or `proof-graph.json` exists; silently skipped in most runs; TC-W0-001 "done" does not mean it actually detects anything |

### What Must Be Preserved

- The overclaim detection code in `autonomous_cycle.py` (lines 1442-1497) — valid infrastructure; needs conditional activation verified
- The manual evidence-path overclaim check in `autonomous_cycle.py` (lines 1130-1141) — this runs unconditionally; is the more reliable of the two mechanisms
- `failure_memory.py` and its integration in `autonomous_task_generator.py` — already operational
- The gap ledger (1495 entries, 16 open, 1447 closed) — mostly complete
- All 30 existing security/fuzz test files across 18 formats
- TC-W4-* writers — none of the 4 exist; all need creation
- TC-W0-003 .NET test fixes — real stubs confirmed in tests/net/fodt/ and tests/net/zst/
- TC-W1-003 lane-ownership.yaml — doesn't exist; valid new work
- TC-W1-004 package-install verification script — doesn't exist; valid new work

### What Must Be Redesigned

- TC-W0-001 done-check: needs behavioral proof that overclaim detection produces output
- TC-W0-002: needs reconciliation with actual implementation (not a new feature)
- TC-W2-* and TC-W3-*: need pre-flight verification before any implementation
- Done-checks throughout: must verify behavior, not file existence or keyword presence
- Receipt protocol: must capture actual git revisions (no `TODO_GIT_REV` allowed)
- TC-W6-001: must target the actual script location, not a non-existent directory
- TC-W7-002: must verify scope before starting (may already be complete)

---

## Execution Protocol (Non-Negotiable)

Before marking any task DONE:
1. The done-check must verify **behavior**, not just file existence or keyword presence
2. The receipt MUST contain actual git revision (`git rev-parse HEAD`) — no `TODO_GIT_REV`
3. For Python changes: run `.venv/Scripts/pytest tests/python/{fmt}/ -x` (not `python -m pytest`)
4. For .NET changes: use actual `.csproj` file path, not a directory
5. For "already complete" findings: write receipt with verdict `ALREADY_COMPLETE_VERIFIED` and evidence

State files to maintain:
- `.local/plan-execution/portfolio-recon-heal/state.yaml`
- `.local/plan-execution/portfolio-recon-heal/current-task.yaml`
- `.local/plan-execution/portfolio-recon-heal/checkpoint.md`
- `.local/plan-execution/portfolio-recon-heal/execution-ledger.jsonl`
- `.local/plan-execution/portfolio-recon-heal/receipts/<task-id>.yaml`

---

## Step 0 — Session Startup (Every Session)

```bash
# Copy plan to in-repo location (if not already done)
cp "C:/Users/prora/.claude/plans/fizzy-imagining-hinton.md" plans/.claude/fizzy-imagining-hinton.md

# Write plan lock
python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/fizzy-imagining-hinton.md

# Reconstruct state from: state.yaml → current-task.yaml → checkpoint.md → active taskcard
```

---

## WAVE 0 — Critical Machinery (P0)

### TC-W0-001 — Verify Overclaim Detector Is Actually Operational

**Source plan status:** DONE — but receipt has `TODO_GIT_REV` placeholders and done-check was a trivial grep.

**Required re-verification steps:**
1. Check whether `reports/capability-layer/proof-graph/` or `reports/capability-layer/proof-graph.json` exists
2. If proof-graph is absent: the detector is silently skipped in every autonomous run — the DONE claim is technically true for the code being present but misleading about actual runtime behavior
3. Run: `python -c "from tools.requirements_authority.overclaim_detector import OverclaimDetector; print('importable')"` — must succeed
4. Verify the manual evidence-path check (lines 1130-1141) runs unconditionally by reading those lines
5. Document: whether the proof-graph-dependent detector is operational or a dead path

**Done-check:**
- `python -c "from tools.requirements_authority.overclaim_detector import OverclaimDetector; print('OK')"` — must not crash
- Confirm the manual evidence check (lines 1130-1141 of `autonomous_cycle.py`) runs without a proof-graph dependency
- Write receipt with actual `git rev-parse HEAD` (not TODO placeholder)
- If proof-graph does NOT exist and the sophisticated detector is dead: add a finding to `reports/overclaim-status.json` documenting the gap and mark task DONE_WITH_KNOWN_LIMITATION

**Receipt must contain:**
- `repository_revision_before`: actual output of `git rev-parse HEAD` before any changes
- `repository_revision_after`: actual output of `git rev-parse HEAD` after changes
- `overclaim_detector_proof_graph_exists`: true or false
- `manual_evidence_check_unconditional`: true or false

---

### TC-W0-002 — Reconcile Failure-Memory Against Plan Description

**What the plan says:** "Skip gaps that failed in last 2 attempts within 48h"
**What the code does:** `failure_memory.py` → `load_excluded_gap_ids()` excludes gaps with `occurrence_count >= 3` (ESCALATION_THRESHOLD=3); time window is sprint-count, not wall-clock 48h

**Steps:**
1. Read `tools/supervisor/autonomous_task_generator.py` lines 1619-1629 — confirm failure exclusion is called at gap selection time
2. Read `tools/supervisor/failure_memory.py` method `load_excluded_gap_ids()` — confirm threshold and window
3. Test the integration: `python -c "import sys; sys.path.insert(0, 'tools/supervisor'); from failure_memory import FailureMemory; fm = FailureMemory('.'); print(fm.load_excluded_gap_ids())"` — must not crash
4. Check if `record_failure()` accepts a `gap_id` keyword argument — it must for the exclusion to work
5. If `gap_id` is NOT in `record_failure()` signature: this is the schema mismatch — add it as optional kwarg

**Done-check (behavioral, not grep):**
- Import succeeds: `from failure_memory import FailureMemory`
- Import `autonomous_task_generator` finds and calls `load_excluded_gap_ids()` (grep for the call site)
- Run `python tools/supervisor/autonomous_task_generator.py --help` — no crash
- Write a reconciliation note in the receipt describing: actual threshold (3, not 2), actual window (sprint-count, not 48h), gap_id schema mismatch status
- If integration is already complete and correct: mark `ALREADY_COMPLETE_VERIFIED`

---

### TC-W0-003 — Fix Weak Assert.True(true) in .NET Tests

**Confirmed stubs (from inspection):**
- `tests/net/fodt/` — multiple tests with `Assert.True(true)` in else-branch of conditional checks
- `tests/net/zst/` — properties `MagicValid`, `IsHighlyCompressed`, `IsMinimalFrame` read but not asserted on actual value

**Steps:**
1. Run: `grep -rn "Assert.True(true)" tests/net/fodt/ tests/net/zst/` — collect all locations
2. For each instance, read the full test method body
3. Determine what value the test is actually reading and what its valid range/expected value is:
   - For bool properties: assert `Assert.True(result)` or `Assert.False(result)` based on fixture construction
   - For conditional branches: assert the actual alternative condition, e.g., `Assert.True(doc.GetSectionCount() > 0)`
   - For property-accessibility tests: assert `Assert.IsType<bool>(doc.IsHighlyCompressed)` or the actual expected value
4. Build and test:
   ```
   dotnet build tests/net/fodt/FormatFactory.Fodt.Tests.csproj
   dotnet build tests/net/zst/FormatFactory.Zst.Tests.csproj
   dotnet test tests/net/fodt/FormatFactory.Fodt.Tests.csproj
   dotnet test tests/net/zst/FormatFactory.Zst.Tests.csproj
   ```

**Done-check (behavioral):**
- `grep -rn "Assert.True(true)" tests/net/fodt/ tests/net/zst/` returns 0 results
- `dotnet test` passes for both projects
- At least one replaced assertion tests an actual value, not just absence of exception

**Hardening note:** Do NOT replace `Assert.True(true)` with `Assert.NotNull(result)` if `result` is always non-null by construction — that would be equally meaningless. Read what the test loads and assert on the actual property value returned.

---

## WAVE 1 — Governance and Registration (P1)

### TC-W1-001 — Sync Missing Command-Registry Entries

**Known state:** One gap found — `found-issue-ownership` is missing from `command-registry.yaml` per parity-report.yaml.

**Steps:**
1. Read `.governance/capabilities/parity-report.yaml` — find all `command_in_registry: false` entries
2. For each: add the missing entry to `command-registry.yaml` with correct command metadata
3. Run: `python tools/capability_sync/run_sync.py` to regenerate parity report
4. Verify: `grep "command_in_registry: false" .governance/capabilities/parity-report.yaml` returns 0 results

**Done-check (behavioral):**
- parity-report.yaml shows 0 entries with `command_in_registry: false` after sync
- `python tools/capability_sync/run_sync.py` exits 0

---

### TC-W1-002 — Validate Source-Structure-Baseline.json Accuracy

**Hardening note:** The plan says "document in a comment block at top of the JSON file." Standard JSON does not support comments. Use a `_audit_notes` top-level key instead.

**Steps:**
1. Read `registry/source-structure-baseline.json` — get all entries in `known_violations`
2. For each entry, measure actual LOC: `wc -l <file>` (or equivalent on Windows)
3. Update `loc` field to actual current value — do NOT change `baseline_loc_cap` (write-once)
4. For any entry where `baseline_loc_cap > 5 * current_loc`: add to `_audit_notes` top-level key
5. Format: `{ "_audit_notes": { "oversized_caps": [ { "path": "...", "cap": N, "actual_loc": M, "ratio": R } ] }, "known_violations": {...} }`

**Done-check (behavioral):**
- `python -c "import json; data = json.load(open('registry/source-structure-baseline.json')); print('valid JSON, entries:', len(data['known_violations']))"` — no crash
- At least one `loc` value updated from its prior value (or confirmed accurate)
- `_audit_notes` key exists if any oversized caps found

---

### TC-W1-003 — Add lane-ownership.yaml

**Confirmed:** File does not exist. Valid new work.

**Steps:**
1. Verify actual top-level directories match the prescribed paths by running `ls src/python/ src/net/ tests/python/ tests/net/ tools/ .governance/ registry/`
2. Create `registry/lane-ownership.yaml`:
```yaml
# Lane ownership registry — maps path prefixes to governance owners
# Used by governance validators for lane attribution
lanes:
  python_product:
    paths: ["src/python/"]
    owner: "product"
    description: "Python FOSS format implementations"
  dotnet_product:
    paths: ["src/net/"]
    owner: "product"
    description: ".NET commercial format implementations"
  tests_python:
    paths: ["tests/python/"]
    owner: "testing"
    description: "Python format test suites"
  tests_dotnet:
    paths: ["tests/net/"]
    owner: "testing"
    description: ".NET format test suites"
  tools:
    paths: ["tools/"]
    owner: "machinery"
    description: "Supervisor, governance, and automation tooling"
  governance:
    paths: [".governance/", "registry/"]
    owner: "governance"
    description: "Capability registry, validators, and governance artifacts"
```

**Done-check:**
- `python -c "import yaml; d = yaml.safe_load(open('registry/lane-ownership.yaml')); print('lanes:', list(d['lanes'].keys()))"` — no crash, prints lane names

---

### TC-W1-004 — Package-Install Verification Script

**Hardening note:** Format IDs do not always equal importable module names. Some packages may install under different names. Verify actual install names from site-packages first.

**Steps:**
1. Check `.venv/Lib/site-packages/` to confirm actual installed package names for the 20 formats
2. For formats where package name differs from format ID, map accordingly
3. Create `tools/verify_package_installs.py`:
   - Accept optional `--venv` path argument (default: `.venv`)
   - For each of 20 format IDs: attempt `importlib.import_module(fmt)` using the venv's Python
   - Print PASS/FAIL per format
   - Print summary: `N/20 packages importable`
   - Exit code 0 if all pass, 1 if any fail
4. Run: `.venv/Scripts/python tools/verify_package_installs.py`

**Done-check (behavioral):**
- Script runs without crash: `.venv/Scripts/python tools/verify_package_installs.py`
- Prints `N/20 packages importable` where N is verified count
- At least one format actually imports successfully (not just that the script completes)

---

## WAVE 2 — Analytics Separation (P2, requires TC-W0-001 DONE)

### PRE-FLIGHT REQUIRED: Verify Analytics Separation State

**Before executing any TC-W2-* task, execute this verification sprint first:**

Run a state assessment for all 9 targets. For each format:
1. Check if the source file named in the plan actually exists
2. Check if an analytics file already exists
3. If the source file is already a pure analytics module (all functions are stats/metrics, file imports from a parser, no parsing/serialization logic): mark the task `ALREADY_COMPLETE_VERIFIED`
4. Only proceed with extraction if a genuine mixed-concern monolith is found

**Confirmed findings from pre-flight inspection:**
- `src/python/fodt/text_document.py` — already pure analytics, imports `parse_fodt_strict()`; TC-W2-002 is ALREADY_COMPLETE_VERIFIED
- `src/python/odt/text_document.py` — already pure analytics, imports from `odt_parser`; TC-W2-003 is ALREADY_COMPLETE_VERIFIED
- `src/python/fodp/presentation_document.py` — already pure analytics, 90+ functions; TC-W2-004 is ALREADY_COMPLETE_VERIFIED
- `src/python/pbm/bitmap_image.py` — already pure analytics; TC-W2-005 is ALREADY_COMPLETE_VERIFIED
- `src/python/pgm/grayscale_image.py` — already pure analytics; TC-W2-006 is ALREADY_COMPLETE_VERIFIED
- `src/python/qoi/image_document.py` — already pure analytics; TC-W2-007 is ALREADY_COMPLETE_VERIFIED
- `src/python/tsv/tabular_document.py` — already pure analytics (852 LOC, 75+ functions); TC-W2-009 requires a separate LOC check since it's 852 LOC
- `src/python/fods/spreadsheet_document.py` — FILE DOES NOT EXIST; TC-W2-001 must discover what FODS analytics structure actually is before executing
- `src/python/sylk/spreadsheet_document.py` — FILE DOES NOT EXIST; SYLK already has `sylk_analytics.py`; TC-W2-008 is ALREADY_COMPLETE_VERIFIED

**Execution order:**
1. For each "ALREADY_COMPLETE_VERIFIED" task: read the analytics file, confirm it has ≥1 function, run format tests, write receipt with verdict `ALREADY_COMPLETE_VERIFIED`, update plan status to DONE
2. For `fods` (TC-W2-001): inspect `src/python/fods/` directory to find actual analytics file structure, then either verify it's complete or create/move as needed
3. Update plan status for each

---

### TC-W2-001 — Analytics Separation: fods (NEEDS DISCOVERY)

**Steps:**
1. List all files in `src/python/fods/` to understand current structure
2. Find analytics functions — any file containing functions named `fods_*_count`, `fods_*_stats`, `fods_*_summary`
3. Determine: is there already a `fods_analytics.py` or equivalent? If yes → `ALREADY_COMPLETE_VERIFIED`
4. If not: identify the monolith file and apply extraction per TC-W2-002 pattern
5. Run: `.venv/Scripts/pytest tests/python/fods/ -x` — must pass

**Done-check:** A file named `*analytics*.py` exists in `src/python/fods/` with ≥1 function. Tests pass.

---

### TC-W2-002 through TC-W2-009 (except TC-W2-001)

Based on pre-flight inspection findings:
- TC-W2-002, TC-W2-003, TC-W2-004, TC-W2-005, TC-W2-006, TC-W2-007: Likely `ALREADY_COMPLETE_VERIFIED`
- TC-W2-008 (sylk): `sylk_analytics.py` already exists — verify ≥1 function and tests pass → `ALREADY_COMPLETE_VERIFIED`
- TC-W2-009 (tsv): `tabular_document.py` is 852 LOC (slightly above the 800 LOC threshold in TC-W3-*) — verify analytics separation completeness and tests pass

**For each: write a receipt with the correct verdict and run format tests. Update source plan status.**

---

## WAVE 3 — Monolith Healing (P2, requires any TC-W2-* DONE)

### PRE-FLIGHT REQUIRED: Verify Current LOC of Monolith Targets

Before any TC-W3-* work, measure actual current LOC:

```bash
# Run actual line counts (Windows equivalent):
for fmt in abw dif ndjson zst xcf; do echo "$fmt:"; wc -l src/python/$fmt/*.py 2>/dev/null; done
```

**Plan assumptions to verify:**
- `abw/word_document.py`: plan claims 1027 LOC — verify current state
- `dif/interchange_document.py`: plan claims 995 LOC — verify
- `ndjson/json_stream.py`: plan claims 927 LOC — verify
- `zst/zst_codec.py`: plan claims 931 LOC — CRITICAL: this is the primary codec, not analytics
- `xcf/xcf_image_metrics.py`: plan claims 899 LOC — this IS a metrics file already

**Risk assessment for TC-W3-004 (zst/zst_codec.py):**
The file contains `class ZstException` and is the primary compression codec. Extracting "analytics" from the primary codec is architecturally risky. If current LOC is already ≤800 or if the file is core domain, this task should be re-scoped to EITHER:
- Extract only clearly non-core analytics functions (if any exist), OR
- Mark as INVALIDATED if the file is already ≤800 LOC or has no analytics functions

**Execution rule per task:**
1. Measure actual current LOC
2. If file is already ≤800 LOC: mark `ALREADY_COMPLETE_VERIFIED`
3. If file is >800 LOC and is a pure analytics file: extract further analytics to new `{fmt}_analytics.py`
4. If file is >800 LOC and is core domain (parsing/codec/serialization): do NOT extract — mark as `TASK_INVALIDATED_BY_REPOSITORY_TRUTH` with explanation
5. For each extraction: run format tests and verify LOC reduction

**Done-check per task:**
- Actual LOC measurement (not plan estimate) proves ≤800, OR
- Task is verifiably invalidated with documented reason

---

## WAVE 4 — New Writers (P3)

**Confirmed:** All 4 writer files do not exist. All 4 are valid new work.

### TC-W4-001 — TSV Writer (requires TC-W2-009 DONE)

**Steps:**
1. Read `src/python/csv/csv_writer.py` as reference implementation
2. Read `src/python/tsv/__init__.py` to understand current exports
3. Create `src/python/tsv/tsv_writer.py`:
   - Function: `write_tsv(rows: list[list[str]], path: str, headers: list[str] | None = None) -> None`
   - Use `\t` separator; newline `\r\n` or `\n` (match CSV reference)
   - No quoting complications (TSV convention: tabs in values are illegal; document this)
4. Add `write_tsv` to `src/python/tsv/__init__.py`
5. If non-editable install: copy `tsv_writer.py` to `.venv/Lib/site-packages/tsv/`
6. Add roundtrip test in `tests/python/tsv/test_tsv_writer.py`:
   - Write rows with known values → read back → assert semantic equality (not just file existence)
7. Run: `.venv/Scripts/pytest tests/python/tsv/ -x`

**Done-check (behavioral):**
- `.venv/Scripts/python -c "from tsv.tsv_writer import write_tsv; print('OK')"` — no crash
- Roundtrip test passes and asserts actual row/value equality

---

### TC-W4-002 — NDJSON Writer (requires TC-W3-003 DONE)

**Steps:**
1. Read `src/python/ndjson/__init__.py` and `src/python/ndjson/json_stream.py` (or current main module)
2. Create `src/python/ndjson/ndjson_writer.py`:
   - Function: `write_ndjson(records: list[dict], path: str) -> None`
   - Each record → `json.dumps(record)` + `\n`
   - Validate each record is JSON-serializable; raise `TypeError` with context on failure
3. Add to `__init__.py`; sync to site-packages if non-editable
4. Roundtrip test: write known dicts → parse back → assert equality

**Done-check (behavioral):**
- `.venv/Scripts/python -c "from ndjson.ndjson_writer import write_ndjson; print('OK')"` — no crash
- Roundtrip test verifies dict equality after write+read cycle

---

### TC-W4-003 — TOML Writer (requires TC-W2-009 DONE)

**Steps:**
1. Read `src/python/toml/__init__.py` to understand current read API
2. Check: is `tomli-w` or similar already in `.venv`? If yes, use it. If no, implement minimal writer.
3. Create `src/python/toml/toml_writer.py`:
   - Function: `write_toml(data: dict, path: str) -> None`
   - Supported types: `str`, `int`, `float`, `bool`, `datetime`, `list` (of supported types), `dict` (nested tables)
   - Explicitly raise `TypeError` with message for unsupported types (sets, tuples of mixed types, custom objects)
   - Do not silently emit invalid TOML
4. Roundtrip test with known dict (strings, ints, nested tables) — read back and verify

**Done-check (behavioral):**
- `.venv/Scripts/python -c "from toml.toml_writer import write_toml; print('OK')"` — no crash
- Roundtrip test verifies dict equality after write+read
- Test that passing an unsupported type raises `TypeError` (not silent failure)

---

### TC-W4-004 — SYLK Writer (requires TC-W2-008 DONE)

**Steps:**
1. Read SYLK spec: `ID;P` header, `C;X{col};Y{row};K{value}` cell records, `E` terminator
2. Read `src/python/sylk/sylk_analytics.py` and parser to understand model structure
3. Create `src/python/sylk/sylk_writer.py`:
   - Accept the model structure returned by the parser
   - Emit valid SYLK text
4. Roundtrip test: parse sample → write → parse output → compare cell values

**Done-check (behavioral):**
- `.venv/Scripts/python -c "from sylk.sylk_writer import write_sylk; print('OK')"` — no crash
- Roundtrip test verifies cell value equality (not just file existence)

---

## WAVE 5 — Gap Ledger Verification (P2, requires TC-W1-001 DONE)

**Confirmed scope:** 16 open gaps (not hundreds). 1447 closed gaps.

### TC-W5-001 — Verify Open Gaps Against Source Truth

**Steps:**
1. Read `reports/capability-layer/gap-ledger.json` — extract the 16 open gaps
2. For each open gap: read the `description` field; search the described source file/function to verify deficiency still exists
3. If deficiency is fixed: update gap status to `closed` with evidence notes
4. If deficiency still exists: leave as open, add verification timestamp
5. Write updated ledger

**Done-check:** All 16 open gaps verified against source; any fixed gaps have evidence in ledger. Report the count in receipt.

---

### TC-W5-002 — Spot-Check Closed Gaps

**Steps:**
1. Extract closed gap IDs: count actual number (expected ~1447)
2. Take deterministic 10% sample (every 10th entry by index)
3. For each sampled gap: find the described deficiency and verify the fix exists in current source
4. Reopen any falsely-closed gaps (with evidence)
5. Write `reports/gap-spot-check-results.json` with per-gap PASS/FAIL

**Done-check:** `reports/gap-spot-check-results.json` exists with exactly `ceil(actual_closed_count / 10)` entries and PASS/FAIL per entry.

**Tradeoff note:** This is genuine sampling work. At 1447 closed gaps, a 10% sample is ~145 gaps. If each takes 1-2 minutes of source inspection, this is the largest single-session task. If context runs short, close the task on partial sample (document how many were checked) and continue in next session from the checkpoint.

---

### TC-W5-003 — Normalize Format Name Casing

**Steps:**
1. Run: `grep -rn "FODS\|FODT\|SYLK\|NDJSON\|GNUMERIC" registry/ reports/ .governance/ --include="*.yaml" --include="*.json" --include="*.md"` — exclude `.cs` files
2. For each occurrence: determine if it's in prose heading (keep uppercase) or data field (lowercase)
3. Fix data field occurrences

**Done-check:** `grep -rn "FODS\|FODT\|SYLK" registry/ .governance/ --include="*.yaml"` returns only intentional uppercase entries.

---

### TC-W5-004 — Register Unledgered Gaps

**Steps:**
1. Collect deficiencies found during TC-W5-001/002 that lack gap-ledger entries
2. For each: add a properly structured gap entry with `gap_id`, `description`, `status: open`, `format`, evidence path

**Done-check:** Any deficiencies found during W5-001/002 have corresponding gap-ledger entries.

---

## WAVE 6 — Machinery Consolidation (P4)

### TC-W6-001 — Identify and Consolidate Sprint Writer Duplication

**Critical correction:** `tools/supervisor/sprint_writers/` does NOT exist. Sprint writer logic is distributed across 234 files in `tools/supervisor/`. This task must be re-scoped.

**Revised steps:**
1. Find files in `tools/supervisor/` with names matching `sprint_writer*`, `write_sprint*`, `build_*_package*`, or similar sprint-evidence writing patterns
2. Read 2-3 of them to identify shared write patterns (evidence declaration writing, YAML output, etc.)
3. If a common base class or utility is missing: extract shared code into `tools/supervisor/sprint_writer_base.py`
4. Measure LOC reduction (target: ≥20% reduction in total LOC of the identified set)

**Hardening note:** If the 234 supervisor scripts have no clear "sprint writer" cohort, this task may reduce to identifying the 5-10 scripts that write evidence/declarations and extracting their shared logic. Do not attempt to consolidate all 234 scripts.

**Done-check:** Identified sprint-writer files have LOC reduced by ≥20% through shared utility extraction. Or: document that no meaningful consolidation target exists and mark `TASK_INVALIDATED_BY_REPOSITORY_TRUTH`.

---

### TC-W6-002 — Classify Unused Tool Scripts

**Scale note:** 234 Python files in `tools/supervisor/`. Full manual classification is infeasible in one session.

**Revised steps:**
1. Build an automated script to classify usage: for each `.py` file in `tools/supervisor/`, search for its basename in `CLAUDE.md`, `.supervisor/skill-registry.yaml`, governance validators, and pipeline imports
2. Produce `reports/unused-tools-audit.json` with classification `active|likely_unused|archive_candidate` and the reference that proves it active (or absence of references)
3. Do not manually inspect each file — use grep-based reference detection

**Done-check:** `reports/unused-tools-audit.json` exists with classification for every `.py` file in `tools/supervisor/` (≥200 entries expected).

---

### TC-W6-003 — Document Machinery:Product Ratio

**Steps:**
1. Count LOC: product = `src/python/` + `src/net/` all `.py` and `.cs` files
2. Count LOC: machinery = `tools/` all `.py` files + `.governance/` all files + `reports/` all `.md` and `.yaml` files
3. Calculate ratio: machinery_loc / product_loc
4. Write `reports/machinery-product-ratio.json` with counts and ratio

**Done-check:** File exists; ratio is documented with component breakdown.

**Target:** < 2.0:1 (may not be achievable without significant machinery reduction — document honestly)

---

## WAVE 7 — Test Architecture (P4)

### TC-W7-001 — Test-Coverage Index (requires any TC-W3-* DONE)

**Steps:**
1. List all `tests/net/fods/FodsR*.cs` and `tests/python/*/test_r*.py` files
2. For each: extract test class name and map to feature via filename pattern (e.g., `FodtR292GetSectionNameDedicatedTests` → feature: `GetSectionName`)
3. Write `registry/test-coverage-index.yaml` with ≥50 entries

**Done-check:** File exists; `python -c "import yaml; d=yaml.safe_load(open('registry/test-coverage-index.yaml')); print(len(d['tests']))"` prints ≥50.

---

### TC-W7-002 — Security Test Suite

**IMPORTANT PRE-FLIGHT CHECK:** 30 security/fuzz test files already exist across 18 formats. The original done-check (`find tests/ -name "*security*" | wc -l >= 5`) would TRIVIALLY PASS without any work.

**Revised approach:**
1. Audit the 30 existing security test files — what attacks/scenarios do they cover?
2. Identify gaps: which attack categories are NOT covered? (path traversal, zip bombs, XML entity expansion, integer overflow in dimensions, etc.)
3. Add tests ONLY for genuinely missing attack categories — do not add tests that duplicate existing ones
4. Target: add ≥3 new security test files for attack categories not currently covered

**Done-check:** A list of 3 new security test files, each targeting a specific attack category, each with ≥2 test functions that use disposable temporary fixtures and make real assertions.

---

### TC-W7-003 — Performance Benchmark Suite (no dependency)

**Steps:**
1. Create `tests/benchmarks/` directory
2. For each of fods, fodt, csv, ndjson, zst:
   - Find or create a sample file of ≥10KB
   - Write `tests/benchmarks/bench_{fmt}.py` using `timeit` or `time.perf_counter`
   - 10 warmup runs, then 50 measured runs; report mean and stddev
   - Record: Python version, file size, machine specs (via `platform.processor()`)
3. Do NOT set hard performance thresholds — record baseline for comparison only

**Done-check:** `ls tests/benchmarks/bench_*.py | wc -l` ≥ 5; each script runs without error and prints mean/stddev.

**Tradeoff:** Without stable baselines, benchmarks are observation only. First-run numbers will define the baseline for future regression detection.

---

### TC-W7-004 — Audit Overlapping R-Series Tests (requires TC-W7-001)

**Steps:**
1. Use `registry/test-coverage-index.yaml` to find features with >3 test files
2. For each cluster: read the test files to classify as redundant vs. complementary
3. Write `reports/test-overlap-audit.json` with overlap analysis — audit only, no deletion

**Done-check:** Report exists with overlap analysis. At least one cluster identified (or documented that no clusters with >3 files exist).

---

## Plan Closure

After all taskcards are DONE, ALREADY_COMPLETE_VERIFIED, or TASK_INVALIDATED_BY_REPOSITORY_TRUTH:

1. Run lifecycle audit:
```bash
python tools/supervisor/lifecycle_audit.py \
  --mission-id PORTFOLIO-RECON-HEAL-20260627 \
  --sprint-id TC-W7-004
```

2. Close the plan:
```bash
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/fizzy-imagining-hinton.md \
  --terminal --audit-gate
```

If `ITERATION_REQUIRED`: read `.local/supervisor/lifecycle-audit-results.json`, add new taskcards, execute them.
If `TERMINAL_CLOSED`: **STOP**. Report completion. Do NOT call `check_continuation.py` or read `next-sprint.md`.

---

## Tradeoffs, Risks, and Honest Limitations

| Area | Risk | Mitigation |
|---|---|---|
| TC-W0-001 re-verification | Overclaim detector may be permanently dead (no proof-graph) | Document as known limitation; confirm manual evidence check works instead |
| TC-W2-* obsolescence | 7 of 9 tasks may be already done | Pre-flight verification sprint; write `ALREADY_COMPLETE_VERIFIED` receipts |
| TC-W3-004 (zst_codec.py) | Primary codec — analytics extraction may break compression | Measure LOC first; if already ≤800, invalidate task; if >800, inspect for safe extraction points only |
| TC-W5-002 sampling | 145 gap verifications is significant work | Time-bound at 60 min; document partial completion in checkpoint; resume in next session |
| TC-W6-001 path mismatch | `sprint_writers/` directory doesn't exist | Re-scope to identify actual sprint-writer scripts before consolidating |
| TC-W7-002 security tests | 30 files already exist; naive done-check would pass trivially | Pre-flight count of existing files; add only genuinely missing attack categories |
| Receipt `TODO_GIT_REV` pattern | Receipts look complete but are actually synthetic | Mandatory: every receipt must contain actual `git rev-parse HEAD` output |
| Per-session context exhaustion | 36 taskcards cannot all complete in one session | State files and checkpoint are authoritative; next session resumes from checkpoint exactly |

## Regression Controls

- Before any Wave 2/3 extraction: run format tests to establish baseline pass count; re-run after
- Before any Wave 4 writer: run `from {fmt} import *` to confirm no import errors in current state
- After any Wave 6 consolidation: run full governance validator suite (165 validators) to detect regressions
- After TC-W0-003 .NET test fixes: both `dotnet test` projects must produce zero failures (not just zero new failures)
