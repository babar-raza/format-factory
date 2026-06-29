# Portfolio Product and Machinery Healing Plan

**Mission ID:** PORTFOLIO-RECON-HEAL-20260627
**Type:** machinery_hardening
**Status:** ACTIVE

## How to Execute This Plan

1. Find the first taskcard with `status: PENDING` below.
2. Execute ONLY that taskcard. Each is self-contained.
3. After completing it, change its status to `DONE`.
4. Move to the next `PENDING` taskcard. Stop when all are `DONE`.

Dependencies are marked with `requires:`. Skip a task if its dependency is not `DONE` yet — move to the next `PENDING` task without a blocking dependency.

---

## TC-W0-001 — Wire overclaim detector into autonomous cycle
- **status:** DONE
- **completed:** 2026-06-27T23:05:10+05:00
- **receipt:** .local/plan-execution/portfolio-recon-heal/receipt_TCW0-001.yaml
- **verified revision:** TODO_GIT_REV_AFTER
- **priority:** P0
- **requires:** none
- **target file:** `tools/supervisor/autonomous_cycle.py`
- **what:** After the post-sprint grading block, add a call to detect overclaims. An overclaim is when a work item is graded PASS but evidence does not support it.
- **steps:**
  1. Read `tools/supervisor/autonomous_cycle.py` — find the post-sprint grading section
  2. Add an overclaim detection pass that compares declared evidence paths against actual file existence and content
  3. Log any overclaims to `reports/supervisor/overclaim-detections.json`
- **done-check:** Run `python tools/supervisor/autonomous_cycle.py --help` (no crash). Grep for "overclaim" in the file — must exist.

---

## TC-W0-002 — Activate failure-memory learning loop
- **status:** PENDING
- **priority:** P0
- **requires:** none
- **target file:** `tools/supervisor/autonomous_task_generator.py`
- **what:** Read `failure-memory.json` (if exists) when selecting next gaps. Skip gaps that failed in the last 2 attempts.
- **steps:**
  1. Read `tools/supervisor/autonomous_task_generator.py` — find the gap selection logic
  2. At the top of gap selection, load `.local/supervisor/failure-memory.json` (default: empty list)
  3. Filter out gaps whose `gap_id` appears in failure-memory with `attempts >= 2` and `last_attempt` within 48h
  4. If no file exists, proceed normally (no error)
- **done-check:** Grep for `failure-memory` in the file — must exist. `python -c "from tools.supervisor.autonomous_task_generator import *"` — no crash.

---

## TC-W0-003 — Fix weak Assert.True(true) in .NET tests
- **status:** PENDING
- **priority:** P0
- **requires:** none
- **target files:** `tests/net/fodt/FodtR292*.cs` through `FodtR314*.cs` (12 files), `tests/net/zst/` (6 files with `Assert.True(true)`)
- **what:** Replace `Assert.True(true)` with meaningful assertions that test actual values.
- **steps:**
  1. Run: `grep -rn "Assert.True(true)" tests/net/fodt/ tests/net/zst/` to find all instances
  2. For each file, read the test to understand what it does
  3. Replace `Assert.True(true)` with an assertion on the actual result (e.g., `Assert.NotNull(result)`, `Assert.Equal(expected, actual)`, `Assert.Contains(...)`)
  4. Build: `dotnet build tests/net/fodt/ tests/net/zst/` — must compile
- **done-check:** `grep -rn "Assert.True(true)" tests/net/fodt/ tests/net/zst/` returns 0 results.

---

## TC-W1-001 — Sync missing command-registry entries
- **status:** PENDING
- **priority:** P1
- **requires:** none
- **what:** Ensure all skills in `skill-registry.yaml` have matching entries in `.governance/capabilities/registry.yaml`.
- **steps:**
  1. Run: `/sync-capabilities` (or `python tools/capability_sync/run_sync.py`)
  2. Check output for "missing" or "added" entries
  3. Verify: `grep "command_in_registry: false" .governance/capabilities/parity-report.yaml` — must return 0 results
- **done-check:** `parity-report.yaml` has 0 entries with `command_in_registry: false`.

---

## TC-W1-002 — Validate source-structure-baseline.json accuracy
- **status:** PENDING
- **priority:** P1
- **requires:** none
- **target file:** `registry/source-structure-baseline.json`
- **what:** Verify `loc` and `functions` counts match actual file contents. Flag caps that are wildly wrong.
- **steps:**
  1. Read `registry/source-structure-baseline.json`
  2. For each entry in `known_violations`, count actual LOC and functions: `wc -l <file>` and count `def ` lines
  3. Update `loc` and `functions` to actual values (do NOT change `baseline_loc_cap` or `baseline_functions_cap` — those are write-once)
  4. Document any entry where `baseline_loc_cap` is >5x actual LOC in a comment block at the top of the file
- **done-check:** `loc` values in the file match actual line counts (within ±5 lines).

---

## TC-W1-003 — Add lane-ownership.yaml
- **status:** PENDING
- **priority:** P1
- **requires:** none
- **target file:** `registry/lane-ownership.yaml` (create new)
- **what:** Map source directories to lane owners for governance validation.
- **steps:**
  1. Create `registry/lane-ownership.yaml` with this structure:
     ```yaml
     lanes:
       python_product: { paths: ["src/python/"], owner: "product" }
       dotnet_product: { paths: ["src/net/"], owner: "product" }
       tests_python: { paths: ["tests/python/"], owner: "testing" }
       tests_dotnet: { paths: ["tests/net/"], owner: "testing" }
       tools: { paths: ["tools/"], owner: "machinery" }
       governance: { paths: [".governance/", "registry/"], owner: "governance" }
     ```
  2. Populate paths by scanning the repo's top-level directories
- **done-check:** File exists and is valid YAML. `python -c "import yaml; yaml.safe_load(open('registry/lane-ownership.yaml'))"` — no error.

---

## TC-W1-004 — Package-install verification script
- **status:** PENDING
- **priority:** P1
- **requires:** none
- **target file:** `tools/verify_package_installs.py` (create new)
- **what:** Script that verifies all 20 Python format packages can be imported.
- **steps:**
  1. Create script that iterates over: `abw csv dif fodg fodp fods fodt gnumeric ndjson ods odt pbm pgm ppm qoi sylk toml tsv xcf zst`
  2. For each, attempt `importlib.import_module(fmt)` and report pass/fail
  3. Print summary: `N/20 packages importable`
- **done-check:** `python tools/verify_package_installs.py` runs without crash and prints summary.

---

## TC-W2-001 — Analytics separation: fods
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/fods/spreadsheet_document.py`
- **target:** `src/python/fods/fods_analytics.py` (create new)
- **what:** Move all analytics/statistics functions from the source file into a separate analytics module.
- **steps:**
  1. Read the source file. Identify functions that compute statistics, aggregates, or metrics (names containing `stats`, `count`, `summary`, `analytics`, `aggregate`, `metric`)
  2. Move those functions to the new `fods_analytics.py` file
  3. Add imports in the source file to re-export from analytics (backward compat)
  4. Update `src/python/fods/__init__.py` to export from analytics module
  5. Run: `.venv/Scripts/pytest tests/python/fods/ -x` — all tests pass
- **done-check:** `fods_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W2-002 — Analytics separation: fodt
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/fodt/text_document.py`
- **target:** `src/python/fodt/fodt_analytics.py` (create new)
- **steps:** Same pattern as TC-W2-001 but for fodt.
- **done-check:** `fodt_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W2-003 — Analytics separation: odt
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/odt/text_document.py`
- **target:** `src/python/odt/odt_analytics.py` (create new)
- **steps:** Same pattern as TC-W2-001 but for odt.
- **done-check:** `odt_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W2-004 — Analytics separation: fodp
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/fodp/presentation_document.py`
- **target:** `src/python/fodp/fodp_analytics.py` (create new)
- **steps:** Same pattern as TC-W2-001 but for fodp.
- **done-check:** `fodp_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W2-005 — Analytics separation: pbm
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/pbm/bitmap_image.py`
- **target:** `src/python/pbm/pbm_analytics.py` (create new)
- **steps:** Same pattern as TC-W2-001 but for pbm.
- **done-check:** `pbm_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W2-006 — Analytics separation: pgm
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/pgm/grayscale_image.py`
- **target:** `src/python/pgm/pgm_analytics.py` (create new)
- **steps:** Same pattern as TC-W2-001 but for pgm.
- **done-check:** `pgm_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W2-007 — Analytics separation: qoi
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/qoi/image_document.py`
- **target:** `src/python/qoi/qoi_analytics.py` (create new)
- **steps:** Same pattern as TC-W2-001 but for qoi.
- **done-check:** `qoi_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W2-008 — Analytics separation: sylk
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/sylk/spreadsheet_document.py`
- **target:** `src/python/sylk/sylk_analytics.py` (create new)
- **steps:** Same pattern as TC-W2-001 but for sylk.
- **done-check:** `sylk_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W2-009 — Analytics separation: tsv
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W0-001
- **source:** `src/python/tsv/tabular_document.py`
- **target:** `src/python/tsv/tsv_analytics.py` (create new)
- **steps:** Same pattern as TC-W2-001 but for tsv.
- **done-check:** `tsv_analytics.py` exists with ≥1 function. Tests pass.

---

## TC-W3-001 — Monolith healing: abw/word_document.py
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W2-001 through TC-W2-009 (any)
- **source:** `src/python/abw/word_document.py` (1027 LOC, 98 fn)
- **target:** `src/python/abw/abw_analytics.py` (create new)
- **what:** Extract stats/analytics functions to get source file under 800 LOC.
- **steps:**
  1. Read source. Identify analytics/stats functions (≥20 functions expected)
  2. Move them to `abw_analytics.py`
  3. Re-export from source for backward compat
  4. Verify: `wc -l src/python/abw/word_document.py` — must be ≤800
  5. Run: `.venv/Scripts/pytest tests/python/abw/ -x` — all tests pass
- **done-check:** `word_document.py` ≤ 800 LOC. `abw_analytics.py` exists. Tests pass.

---

## TC-W3-002 — Monolith healing: dif/interchange_document.py
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W2-001 through TC-W2-009 (any)
- **source:** `src/python/dif/interchange_document.py` (995 LOC, 65 fn)
- **target:** `src/python/dif/dif_analytics.py` (create new)
- **what:** Same pattern as TC-W3-001 but for dif.
- **done-check:** `interchange_document.py` ≤ 800 LOC. Tests pass.

---

## TC-W3-003 — Monolith healing: ndjson/json_stream.py
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W2-001 through TC-W2-009 (any)
- **source:** `src/python/ndjson/json_stream.py` (927 LOC, 69 fn)
- **target:** `src/python/ndjson/ndjson_analytics.py` (create new)
- **what:** Same pattern as TC-W3-001 but for ndjson.
- **done-check:** `json_stream.py` ≤ 800 LOC. Tests pass.

---

## TC-W3-004 — Monolith healing: zst/zst_codec.py
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W2-001 through TC-W2-009 (any)
- **source:** `src/python/zst/zst_codec.py` (931 LOC, 22 fn)
- **target:** `src/python/zst/zst_compression_analytics.py` (create new)
- **what:** Same pattern as TC-W3-001 but for zst.
- **done-check:** `zst_codec.py` ≤ 800 LOC. Tests pass.

---

## TC-W3-005 — Monolith healing: xcf/xcf_image_metrics.py
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W2-001 through TC-W2-009 (any)
- **source:** `src/python/xcf/xcf_image_metrics.py` (899 LOC, 104 fn)
- **target:** `src/python/xcf/xcf_analytics.py` (create new)
- **what:** Split metrics (keep) from analytics (extract). Same pattern as TC-W3-001.
- **done-check:** `xcf_image_metrics.py` ≤ 800 LOC. Tests pass.

---

## TC-W4-001 — Writer: tsv
- **status:** PENDING
- **priority:** P3
- **requires:** TC-W2-009
- **reference:** `src/python/csv/csv_writer.py` (model this after it)
- **target:** `src/python/tsv/tsv_writer.py` (create new)
- **what:** Write a TSV writer that takes rows as `list[list[str]]` + `headers` kwarg, outputs tab-separated text.
- **steps:**
  1. Read `src/python/csv/csv_writer.py` as reference
  2. Create `tsv_writer.py` — same API but use `\t` separator instead of `,`
  3. Add `write_tsv` to `src/python/tsv/__init__.py` exports
  4. Add a roundtrip test in `tests/python/tsv/`
- **done-check:** `from tsv.tsv_writer import write_tsv` works. Roundtrip test passes.

---

## TC-W4-002 — Writer: ndjson
- **status:** PENDING
- **priority:** P3
- **requires:** TC-W3-003
- **target:** `src/python/ndjson/ndjson_writer.py` (create new)
- **what:** Serialize list of dicts back to NDJSON (one JSON object per line).
- **steps:**
  1. Create writer: `def write_ndjson(records: list[dict], path: str)` — writes one `json.dumps(r)` per line
  2. Export from `__init__.py`
  3. Add roundtrip test
- **done-check:** `from ndjson.ndjson_writer import write_ndjson` works. Test passes.

---

## TC-W4-003 — Writer: toml
- **status:** PENDING
- **priority:** P3
- **requires:** TC-W2-009
- **target:** `src/python/toml/toml_writer.py` (create new)
- **what:** Serialize dict back to TOML format.
- **steps:**
  1. Use Python 3.11+ `tomllib` for reading, implement simple TOML writer for dicts
  2. Export from `__init__.py`
  3. Add roundtrip test
- **done-check:** `from toml.toml_writer import write_toml` works. Test passes.

---

## TC-W4-004 — Writer: sylk
- **status:** PENDING
- **priority:** P3
- **requires:** TC-W2-008
- **target:** `src/python/sylk/sylk_writer.py` (create new)
- **what:** Serialize spreadsheet model back to SYLK format.
- **steps:**
  1. Read SYLK format spec (ID;P header, C;X;Y;K records)
  2. Create writer function
  3. Export from `__init__.py`
  4. Add roundtrip test
- **done-check:** `from sylk.sylk_writer import write_sylk` works. Test passes.

---

## TC-W5-001 — Verify open gaps against source truth
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W1-001
- **target file:** `reports/capability-layer/gap-ledger.json`
- **what:** Check all gaps with `status: open` — verify the gap still exists in source code.
- **steps:**
  1. Read `reports/capability-layer/gap-ledger.json`
  2. For each open gap, check if the described deficiency still exists
  3. Close gaps that are already fixed. Keep gaps that are real.
  4. Write updated ledger
- **done-check:** Every open gap in the ledger corresponds to a real, verifiable deficiency.

---

## TC-W5-002 — Spot-check closed gaps
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W5-001
- **target file:** `reports/capability-layer/gap-ledger.json`
- **what:** Sample 125 closed gaps (10% of ~1245). Verify each was actually fixed.
- **steps:**
  1. Extract all closed gap IDs. Take every 10th one (deterministic sample).
  2. For each, verify the fix exists in source
  3. Reopen any that were falsely closed
- **done-check:** Report written to `reports/gap-spot-check-results.json` with pass/fail per sample.

---

## TC-W5-003 — Normalize format name casing
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W5-001
- **what:** Fix inconsistent casing: `FODS` vs `fods` vs `Fods` throughout registries and reports.
- **steps:**
  1. Grep for mixed casing in `registry/`, `reports/`, `.governance/`
  2. Standardize to lowercase (`fods`, `fodt`, etc.) in data files
  3. Keep uppercase only in prose headings and .NET namespaces
- **done-check:** `grep -rn "FODS\|Fods" registry/ reports/ .governance/ | grep -v ".cs"` — returns only intentional prose uses.

---

## TC-W5-004 — Register unledgered gaps
- **status:** PENDING
- **priority:** P2
- **requires:** TC-W5-001
- **what:** Any deficiencies found during TC-W5-001/002 that have no gap entry — add them.
- **done-check:** All known deficiencies have gap-ledger entries.

---

## TC-W6-001 — Consolidate evidence sprint_writers
- **status:** PENDING
- **priority:** P4
- **requires:** TC-W1-001
- **what:** Reduce duplication in `tools/supervisor/sprint_writers/` (run046-050 are ~15K LOC total with heavy repetition).
- **steps:**
  1. Read 3-4 sprint_writer files. Identify common patterns.
  2. Extract shared logic into a base module
  3. Reduce total LOC by ≥30%
- **done-check:** Total LOC of `tools/supervisor/sprint_writers/` reduced by ≥30%.

---

## TC-W6-002 — Classify unused tool scripts
- **status:** PENDING
- **priority:** P4
- **requires:** TC-W1-001
- **what:** Identify tool scripts in `tools/` not referenced by any skill, validator, or pipeline.
- **steps:**
  1. List all `.py` files in `tools/`
  2. Grep for each filename across skills, CLAUDE.md, validators, and pipeline scripts
  3. Write `reports/unused-tools-audit.json` with classification: `active`, `likely_unused`, `archive_candidate`
- **done-check:** Report file exists with classification for every tool script.

---

## TC-W6-003 — Document machinery:product ratio
- **status:** PENDING
- **priority:** P4
- **requires:** TC-W6-001, TC-W6-002
- **what:** Calculate final machinery:product LOC ratio and document trend.
- **steps:**
  1. Count LOC in `src/python/` + `src/net/` (product)
  2. Count LOC in `tools/` + `.governance/` + `reports/` (machinery)
  3. Write ratio to `reports/machinery-product-ratio.json`
- **done-check:** Ratio file exists. Ratio is documented (target: <2.0:1).

---

## TC-W7-001 — Test-coverage index
- **status:** PENDING
- **priority:** P4
- **requires:** TC-W3-001 through TC-W3-005 (any)
- **target:** `registry/test-coverage-index.yaml` (create new)
- **what:** Map each R-series test file to the product feature(s) it covers.
- **steps:**
  1. List all `tests/net/fods/FodsR*.cs` and `tests/python/*/test_r*.py` files
  2. For each, extract the test class name and map to feature (from filename pattern)
  3. Write YAML index
- **done-check:** File exists and is valid YAML with ≥50 entries.

---

## TC-W7-002 — Security test suite
- **status:** PENDING
- **priority:** P4
- **requires:** none
- **what:** Expand security tests beyond current 2 files.
- **steps:**
  1. Find existing security tests: `grep -rn "security\|injection\|malicious\|fuzz" tests/`
  2. Add tests for: malformed input handling, path traversal in file operations, oversized input
  3. Target: ≥5 security-focused test files
- **done-check:** `find tests/ -name "*security*" -o -name "*fuzz*" | wc -l` ≥ 5.

---

## TC-W7-003 — Performance benchmark suite
- **status:** PENDING
- **priority:** P4
- **requires:** none
- **target:** `tests/benchmarks/` (create new directory)
- **what:** Add basic perf benchmarks for the 5 most-used formats.
- **steps:**
  1. Create `tests/benchmarks/` directory
  2. Add benchmark scripts for fods, fodt, csv, ndjson, zst
  3. Each benchmark: load a sample file 100 times, report avg time
- **done-check:** `ls tests/benchmarks/*.py | wc -l` ≥ 5. Each runs without error.

---

## TC-W7-004 — Audit overlapping R-series tests
- **status:** PENDING
- **priority:** P4
- **requires:** TC-W7-001
- **what:** Identify R-series test files that test the same feature. Audit only — no deletion.
- **steps:**
  1. Using `registry/test-coverage-index.yaml` from TC-W7-001, find features with >3 test files
  2. For each cluster, note which tests are redundant vs. complementary
  3. Write report to `reports/test-overlap-audit.json`
- **done-check:** Report exists with overlap analysis.

---

## Completion Checklist

All tasks are DONE when these are true:
- [ ] Overclaim detector wired (TC-W0-001)
- [ ] Failure-memory active (TC-W0-002)
- [ ] 0 weak `Assert.True(true)` in .NET tests (TC-W0-003)
- [ ] 0 missing command-registry entries (TC-W1-001)
- [ ] Baseline JSON has accurate LOC counts (TC-W1-002)
- [ ] Lane-ownership.yaml exists (TC-W1-003)
- [ ] Package-install script works for 20/20 formats (TC-W1-004)
- [ ] 9 analytics separations complete (TC-W2-*)
- [ ] 5 monoliths healed to ≤800 LOC (TC-W3-*)
- [ ] 4 writers added (TC-W4-*)
- [ ] Gap ledger verified and normalized (TC-W5-*)
- [ ] Machinery consolidated and ratio documented (TC-W6-*)
- [ ] Test architecture enhanced (TC-W7-*)
