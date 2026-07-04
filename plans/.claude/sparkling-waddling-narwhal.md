# Deep Assessment: Python Library Consumer Pass — format-factory

> **Status:** Empirically verified — all commands run against live environment.

---

## Assessment Scope

- **System:** 20 Python FOSS libraries (`src/python/`), consumer proof scripts (`examples/python/*/consumer_roundtrip.py`), installed packages (`.venv/Lib/site-packages/{fmt}/`), installed-workflow tests (`tests/python/*/test_r*_installed_workflow.py`)
- **Claim being assessed:** README.md table (lines 119–146) shows "Consumer Proof: PASS" for all 20 formats, defined as "a runnable script that loads, inspects, mutates, writes, and reloads the format using only the installed package API."
- **Evidence inspected:** Ran all 20 consumer_roundtrip.py scripts; SHA-256 compared all 19 non-csv format modules between site-packages and source; confirmed sys.path resolution per format; read conftest.py; read 5 consumer scripts; read build-local-packages.py; ran targeted test suite (2925 tests).
- **Missing evidence:** Last wheel build timestamp per format; whether any consumer proof output has ever been captured as dated evidence.

---

## Current-State Reconstruction

### Installation architecture (empirically confirmed)

All 20 formats have module directories in `.venv/Lib/site-packages/`:
```
.venv/Lib/site-packages/
  fods/        ← module dir (stale copy)
  fodt/        ← module dir (stale copy)
  odt/         ← module dir (stale copy)
  ... (all 20)
```

8 formats ALSO have PTH editable install files:
```
__editable__.format_factory_abw-0.1.0.dev0.pth  → src/python
__editable__.format_factory_fods_python-0.1.0.pth → (finder-based editable)
__editable__.format_factory_fodt_python-0.1.0.dev0.pth → src/python
__editable__.format_factory_gnumeric-0.1.0.dev0.pth → src/python
__editable__.format_factory_ndjson-0.1.0.dev0.pth → src/python
__editable__.format_factory_toml-0.1.0.pth → src/python
__editable__.format_factory_zst-0.1.0.dev0.pth → src/python
__editable__.format_factory_fodp-0.1.0.pth → src/python
__editable__.format_factory_dev-0.0.0.pth → src/  (adds ENTIRE src/)
```

**sys.path order in .venv Python (critical):**
```
C:\Python313\python313.zip
C:\Python313\DLLs
C:\Python313\Lib          ← stdlib (csv.py lives here)
C:\Python313
.venv
.venv\Lib\site-packages   ← format-factory module dirs HERE
src\python                ← added by PTH files
src                       ← added by __editable__.format_factory_dev PTH
```

**Import resolution (empirically confirmed):**
- 19/20 formats: import resolves to `.venv/Lib/site-packages/{fmt}/` (the stale copy)
- `csv`: import resolves to `C:\Python313\Lib\csv.py` (stdlib — namespace collision)
- The PTH editable markers are **defeated** by the co-existing module directories, which come first in sys.path

### Staleness audit (SHA-256, empirically confirmed)

**62 files across 19 formats differ between site-packages and source:**

| Format   | Stale | SP-Only (ghost) | Src-Only (missing) | Sample stale files |
|----------|-------|-----------------|--------------------|--------------------|
| abw      | 3     | 0               | 0                  | abw_codec, abw_workflow, word_document |
| dif      | 3     | 0               | 0                  | dif_parser, dif_stats, interchange_document |
| fodg     | 2     | 0               | 1                  | fodg_codec, models |
| fodp     | 3     | 0               | 0                  | fodp_codec, models, presentation_document |
| fods     | 6     | 2               | 0                  | cli, constants, fods_analytics |
| fodt     | 8     | 0               | 0                  | cli, constants, exporters |
| gnumeric | 4     | 1               | 0                  | cli, gnumeric_analytics, gnumeric_codec |
| ndjson   | 4     | 0               | 0                  | __init__, cli, ndjson_record_stats |
| ods      | 2     | 0               | 0                  | models, ods_stats |
| odt      | 2     | 0               | 0                  | models, odt_parser |
| pbm      | 5     | 0               | 0                  | __init__, bitmap_image, pbm_parser |
| pgm      | 4     | 0               | 0                  | __init__, grayscale_image, pgm_parser |
| ppm      | 4     | 0               | 0                  | __init__, color_image, ppm_parser |
| qoi      | 2     | 0               | 0                  | image_document, models |
| sylk     | 2     | 0               | 0                  | sylk_parser, sylk_workflow |
| toml     | 3     | 1               | 0                  | cli, models, toml_codec |
| tsv      | 2     | 0               | 0                  | tabular_document, tsv_parser |
| xcf      | 2     | 0               | 0                  | models, xcf_parser |
| zst      | 1     | 0               | 0                  | compression_metrics |
| **TOTAL**| **62**| **4**           | **1**              |                    |

**SP-only (ghost) files** = files deleted from source but still in installed package. Example: `fods/spreadsheet_document.py` (1035 lines, deleted after analytics extraction) and `fods/spreadsheet_model_document.py` (524 lines) — both still importable from the installed package.

**Src-only (missing)** = files in source never installed. Example: `fodg/` has 1 new source file with no corresponding site-packages entry.

### conftest.py behavior (empirically confirmed)

```python
# tests/python/conftest.py — explicit design intent:
"""Adds src/python/ to sys.path so that 'import fods' resolves to
src/python/fods/ (the product source) rather than any test directory."""

import csv as _stdlib_csv  # pre-import stdlib csv BEFORE src/python/ shadows it
sys.path.insert(0, _SRC_PYTHON)
sys.modules["csv"] = _stdlib_csv  # pin stdlib csv; FF csv is only accessible via workarounds
```

**ALL tests in `tests/python/` run against source, not installed packages.** This is the correct design for unit tests. It also reveals that the CSV package name would break any code that depends on stdlib csv in the same process.

### Test and consumer proof results (empirically confirmed)

- **Test suite:** 2925 passed, 8 skipped — all against source via conftest
- **Consumer roundtrip scripts:** 20/20 PASS — all against stale installed packages (except CSV, which uses repo-root sys.path insertion)
- **Two different code versions are being validated:** tests validate HEAD source; consumer proofs validate stale installed packages

---

## Symptoms

1. All 20 scripts print `CONSUMER_PROOF: PASS` today
2. All 20 module directories exist in site-packages
3. 62 of those installed files differ from current source
4. `import csv` resolves to stdlib, not to the FF CSV package, in all normal Python environments
5. Editable install PTH files are present but completely inert (shadowed by module directories)
6. Ghost files from deleted modules remain importable from installed packages
7. No timestamped execution output exists for any consumer roundtrip script
8. "Installed workflow" tests are a misnomer — they test source via conftest, not installed packages

---

## Root Causes

### RC-1: Sprint loop never rebuilds installed packages

**Evidence:** `packaging/python/build-local-packages.py` builds wheels to `.local/package-builds/` but is never called by the sprint closeout pipeline. The 62-file divergence is proof: source has evolved through many sprints, installed packages are frozen.

**First failing boundary:** Sprint closeout. The pipeline calls `autonomous-cycle` → governance validators → evidence declaration but has no "sync installed packages" step.

**Affected scope:** All 19 non-csv formats. Every source sprint widens the divergence.

**Why controls missed it:** MEMORY.md documents this ("Non-editable installs: Copy .py files to site-packages after adding new source files") but as a manual reminder, not an automated gate. The `/package-install-proof` skill exists but is `advisory_only: true`.

**Confidence:** HIGH — empirically confirmed with SHA-256 comparison.

---

### RC-2: Editable install intent is structurally defeated

**Evidence:** 8 formats have PTH editable markers intended to make source = installed. But those same formats also have module directories in site-packages. Python's sys.path puts site-packages before PTH-added paths. Import of `fods` resolves to `.venv/Lib/site-packages/fods/` (stale copy), ignoring the PTH file entirely.

**First failing boundary:** When the first non-editable wheel was installed for a format that already had a PTH editable install, the module dir shadowed the PTH.

**Affected scope:** All 8 PTH-editable formats (abw, fodp, fods, fodt, gnumeric, ndjson, toml, zst). For these, even the "editable install" mechanism does not work as intended.

**Why controls missed it:** There is no validator that checks whether an editable install is actually being used vs. shadowed by a module directory. The distinction is only visible by tracing import resolution.

**Confidence:** HIGH — confirmed by tracing `fods.__path__` to site-packages, not src.

---

### RC-3: Consumer proof tests a different code version than the test suite

**Evidence:** conftest inserts `src/python` first → tests test source. Consumer roundtrip scripts resolve to site-packages → they test stale installed code. The two systems have never been co-validated for consistency.

**First failing boundary:** There is no CI step or gate that runs both the test suite and consumer roundtrip scripts against the SAME code version.

**Affected scope:** All 20 formats. The divergence makes both signals independently unreliable as proof of the other.

**Why controls missed it:** The design choice to use conftest for source testing is correct and deliberate. The problem is that no one has established that the installed packages match the passing source tests. This gap is invisible unless you explicitly compare the two.

**Confidence:** HIGH — both codepaths confirmed empirically.

---

### RC-4: CSV package has an unfixable namespace collision under its current name

**Evidence:** Python stdlib `csv.py` is at `C:\Python313\Lib\csv.py`. Python searches stdlib before site-packages. `import csv` always resolves to stdlib for any code that doesn't perform explicit sys.path manipulation. The conftest documents and works around this with `sys.modules["csv"] = _stdlib_csv`. The CSV consumer roundtrip script documents this with a "NOTE: The Format Factory CSV package imports as 'csv', which shadows Python's stdlib csv module."

**First failing boundary:** Package naming at library creation time. The name `csv` was chosen to match the format but collides with the most widely-used stdlib module.

**Affected scope:** Any external consumer of the FF CSV package. All internal usage requires workarounds.

**Why controls missed it:** The workarounds are so embedded (conftest pins, consumer script workaround) that the tests and proofs all pass. The underlying usability defect is hidden.

**Confidence:** HIGH — stdlib path confirmed by tracing `csv.__file__`.

---

### RC-5: No execution evidence captured for consumer proof

**Evidence:** The obligation register (`all-format-obligation-register.yaml`) cites script file paths as evidence, not captured stdout. No `.local/evidences/consumer-proof-*.txt` files exist. Consumer proofs have no timestamp, no captured output, no dated proof that they ever ran and produced PASS output.

**First failing boundary:** The `/create-consumer-roundtrip` skill marks completion based on script file existence + content containing the string `CONSUMER_PROOF: PASS` — not based on script execution.

**Affected scope:** All 20 formats.

**Confidence:** HIGH — checked .local/evidences/ directory; no consumer proof output files exist.

---

## Structural Weaknesses

1. **No package sync in sprint lifecycle:** Source and installed packages are fundamentally different artifacts with no automated synchronization. Every source sprint silently widens the divergence.

2. **Dual-authority code state:** Two code versions coexist (source and installed) with no mechanism to enforce they match. Tests validate one; consumer proofs validate the other; no gate checks they are equivalent.

3. **Editable install shadowing pattern:** Having both PTH editable markers AND module directories for the same format is contradictory and results in the editable mechanism being silently defeated. Neither developers nor validators detect this state.

4. **Ghost file contamination:** Deleted source files remain in installed packages. A consumer using the installed package can import stale/deleted functionality that doesn't exist in source. This inverts the expected behavior (source is authoritative, installed should track it).

5. **"Installed workflow" tests don't test installed packages:** These tests run under conftest which routes to source. They test that the workflow function exists in source and works in source. They provide no guarantee about the installed package. The misnaming creates false confidence.

6. **Consumer proof scripts always succeed:** The scripts have no mechanism to fail based on staleness, ghost files, or version mismatch. They test functional behavior (load/write/verify) which happens to work even against the stale copy. There is no version check, no file inventory check, no staleness gate.

7. **MEMORY.md documents the manual sync requirement but doesn't enforce it:** The note "Non-editable installs: Copy .py files to site-packages after adding new source files" is a human instruction, not a machine check. It will be skipped under autonomous operation.

---

## What Should Be Preserved

- **All 20 source library implementations** — genuinely production-grade (46K LOC, real parsers, real analytics, round-trip tests). These should not change.
- **conftest.py routing to source for unit tests** — this is the correct design for a unit test suite. It ensures tests always run against current source, not against potentially stale installed packages.
- **The consumer_roundtrip.py load→inspect→mutate→write→reload pattern** — this is the right verification pattern. The scripts are correct as test programs.
- **packaging/python/build-local-packages.py** — this correctly builds wheels. It just needs to be called.
- **The test assertions** — 2925 tests verify real behavior. Don't change them.
- **Oracle validation (73/73 PASS)** — separate from consumer proof, correctly implemented, unaffected by this problem.

---

## What Must Be Redesigned

### 1. Package installation model: editable-only for development

**Current state:** 19 formats have stale module dir copies in site-packages. 8 of those also have PTH editable markers (defeated). The result is a chaotic mix with no predictable semantics.

**Target state:** All 20 formats use editable install only. Module directories removed from site-packages for formats that have PTH files. For formats without PTH files, either add PTH-based editable installs OR explicitly document as "must rebuild to sync."

**Why:** With purely editable installs, source = installed always. conftest route-to-source and import-from-site-packages become equivalent. Staleness is eliminated. Ghost files cannot accumulate.

### 2. Sprint closeout: add package sync gate

**Current state:** Sprint closeout calls autonomous-cycle, governance validators, declaration — but never touches installed packages.

**Target state:** Sprint closeout adds a package sync step: for any format whose source files changed during the sprint, either (a) reinstall via editable + rebuild, or (b) copy changed files to site-packages. This step should be best-effort (doesn't block the sprint) but must produce evidence.

### 3. Consumer proof: capture dated execution output

**Current state:** Consumer proof obligation is marked complete based on script file existence.

**Target state:** A `tools/consumer_proof_runner.py` script that:
- Runs all 20 `consumer_roundtrip.py` scripts
- Captures stdout + timestamp to `.local/evidences/consumer-proof-{fmt}-{date}.txt`
- Writes `.local/evidences/consumer-proof-manifest.json` with per-format state and timestamp
- Obligation register `evidence_paths` points to these captured outputs

### 4. CSV package: rename or document hard limitation

**Current state:** Package named `csv` collides with stdlib. Workarounds required in conftest, consumer script, and any consumer code. README doesn't disclose this.

**Target state (option A — rename):** Rename to `formatfactory_csv` or `ff_csv`. All imports in tests/examples updated. README updated. This is a breaking change but the correct long-term solution.

**Target state (option B — document):** Add explicit disclosure to README CSV row: "Note: package name `csv` shadows stdlib csv. Use `from csv.csv_parser import parse_csv` syntax — plain `import csv` gives stdlib." Update conftest comment into a visible warning.

### 5. Fix "installed_workflow" test misnaming

**Current state:** Tests named `test_r*_installed_workflow.py` actually test source via conftest.

**Target state:** Either rename to `test_r*_workflow.py` (removing the "installed" claim), OR create a separate pytest fixture/marker that strips conftest's sys.path injection and actually verifies import from site-packages. The latter would expose the staleness problem mechanically.

---

## Production-Grade Target Design

### Architecture

```
Source (src/python/{fmt}/)
       ↓  editable install (all formats)
site-packages/{fmt}/ ← same files via .pth symlink OR removed in favor of PTH
       ↓
conftest inserts src/python first
       ↓
pytest tests/python/       → validates SOURCE behavior
       ↓
sprint closeout: run consumer_proof_runner.py
       ↓
consumer_proof_runner.py   → runs all 20 roundtrip scripts
                           → resolves from site-packages (now == source via editable)
                           → captures stdout to .local/evidences/
       ↓
consumer-proof-manifest.json {fmt: pass, timestamp, version}
       ↓
README Consumer Proof table updated from manifest
```

### State model per format

```
EDITABLE_SYNCED    = PTH file present, no module directory, source = installed
STALE_COPY         = module directory present, source diverged (current state, 19 formats)
GHOST_FILES        = module directory has files not in source (fods, gnumeric, toml)
CSV_STDLIB_SHADOW  = import resolves to wrong module (1 format)
```

Target: all 20 at `EDITABLE_SYNCED`. STALE_COPY and GHOST_FILES must be eliminated.

### Failure handling

- Ghost file detection: governance validator checks for files in site-packages/{fmt}/ that are not in src/python/{fmt}/
- Stale detection: governance validator computes MD5 mismatch count; FAIL if count > 0 for non-editable installs
- Consumer proof failure: consumer_proof_runner.py exits non-zero if any script fails; evidence file captures error output

### Observability

- `consumer-proof-manifest.json`: per-format state, timestamp, mode (EDITABLE/COPY), pass/fail
- Governance validator V102: checks for ghost files and staleness in site-packages
- Sprint closeout log: records which formats had source changes and whether sync step ran

---

## Implementation Direction

### Phase 1 — Fix editable installs (highest impact, lowest risk) [1 sprint]

**What:** For the 8 formats that have BOTH PTH files AND module directories, delete the stale module directories. Python will then use the PTH editable install as intended.

**Files to modify:**
- Remove `.venv/Lib/site-packages/{fmt}/` dirs for: abw, fodp, fods, fodt, gnumeric, ndjson, toml, zst

**Verification:** After deletion, `import fods; fods.__path__` should resolve to `src/python/fods`, not `site-packages/fods`.

**Risk:** LOW. These 8 formats already have PTH editable markers. Removing the stale copies reveals the intended behavior.

### Phase 2 — Convert remaining 12 to editable installs [1-2 sprints]

**What:** For the 12 formats with module directories but no PTH files (dif, fodg, ods, odt, pbm, pgm, ppm, qoi, sylk, tsv, xcf + csv):
- Run `pip install -e packaging/python/{fmt}/` OR add manual PTH file to site-packages
- Remove stale module directory

**Verification:** All 20 formats resolve imports to `src/python/{fmt}/` not `site-packages/{fmt}/`.

### Phase 3 — Clean up ghost files [same as Phase 2 or follow-on]

**What:** Ghost files in site-packages (fods: 2, gnumeric: 1, toml: 1) are artifacts of earlier analytics extraction refactors. After Phase 1 removes the stale dirs, these ghost files go away automatically for the 8 PTH formats. After Phase 2, remaining formats lose their ghost files.

**No separate action needed if Phases 1-2 complete.**

### Phase 4 — Add consumer_proof_runner.py and capture evidence [1 sprint]

**Files to create:**
- `tools/consumer_proof_runner.py`: loops all 20 formats, runs `consumer_roundtrip.py`, captures stdout to `.local/evidences/consumer-proof-{fmt}.txt`, writes manifest

**Files to modify:**
- Sprint closeout in `autonomous_cycle.py`: add best-effort call to `consumer_proof_runner.py` after source changes
- Obligation register: update `evidence_paths` to reference captured stdout files

### Phase 5 — Add V102 governance validator [1 sprint]

**What:** Add governance validator that detects staleness and ghost files.

**Files to modify:**
- `tools/supervisor/governance_validators_ext2.py` (or a new `_ext3.py`): add `validate_site_packages_sync()`
  - For each format: check if site-packages has extra files not in src (ghost files → FAIL)
  - Check if any files in site-packages differ from src (staleness → WARN if > N files)
- `tools/supervisor/run_validators.py`: register new validator V102

### Phase 6 — CSV namespace decision [requires user decision]

This requires a decision: rename the package (breaking change, correct long-term fix) vs. add explicit disclosure to README (non-breaking, honest about the limitation).

**If rename (option A):**
- Rename `src/python/csv/` to `src/python/ff_csv/` or `src/python/formatfactory_csv/`
- Update all imports in tests, examples, packaging
- Update README package name

**If disclosure (option B):**
- Add warning to README CSV row
- Update `src/python/csv/README.md` if exists

### Phase 7 — Fix "installed_workflow" test naming/behavior [1 sprint, low priority]

Rename `test_r*_installed_workflow.py` to `test_r*_workflow.py` to stop claiming they test installed packages when they test source.

---

## Verification Strategy

### Proof chain after fix

```
REAL INPUT (samples/by-format/{fmt}/minimal.{ext})
→ OFFICIAL ENTRY POINT (.venv/Scripts/python examples/python/{fmt}/consumer_roundtrip.py)
→ SYSTEM PROCESSING (import from editable install = current source)
→ STATE ARTIFACT (.local/evidences/consumer-proof-{fmt}.txt: "CONSUMER_PROOF: PASS")
→ VALIDATOR (V102: no ghost files, no stale files)
→ DOWNSTREAM (README Consumer Proof table)
→ OBSERVED RESULT: 20/20 PASS against current source
```

### Key verification tests

1. **Editable install verification:** `python -c "import fods; assert 'src/python' in str(fods.__path__[0])"` — fails today, must pass after Phase 1
2. **Ghost file check:** `python tools/supervisor/governance_validators_ext2.py --format fods` — must report 0 ghost files after Phase 1
3. **Consumer proof capture:** `python tools/consumer_proof_runner.py` → all 20 `.local/evidences/consumer-proof-*.txt` files created
4. **Staleness gate:** After any source sprint, before marking consumer proof complete, V102 validator must show 0 diverged files for modified formats
5. **Test suite still passes:** `pytest tests/python/ -q` → 2925+ passed (should not regress)
6. **CSV stdlib not broken by install:** `python -c "import csv; csv.reader"` — must work after all phases (tests that stdlib csv is accessible)

### Negative controls

- Deliberately modify `src/python/fods/parser.py` without updating site-packages → V102 fires
- Confirm `import fods.__path__` points to source after Phase 1 (not site-packages copy)
- Confirm ghost files are gone after Phase 1 for fods

### Rerun consistency

After Phases 1-2: consumer proof and test suite run against the SAME code (source via editable install). Results become consistent across reruns because there is only one code identity.

---

## Tradeoffs and Risks

### Benefits
- Eliminates the dual-code-identity problem permanently
- Makes editable installs work as intended
- Removes 62 diverged files and 4 ghost files that could cause import surprises
- Consumer proof and tests agree because they test the same code

### Costs
- Phases 1-2 require removing module directories from site-packages — this is a destructive operation (directories deleted)
- Converting 12 formats from non-editable to editable install requires either `pip install -e` (needs pyproject.toml in each format's package dir) or manual PTH creation
- CSV rename (Phase 6 option A) is a breaking change for any existing code using `from csv.csv_parser import ...`

### Migration risks
- Phase 1 (remove 8 stale dirs): LOW. PTH files already exist. Python will find source via PTH after directory removal.
- Phase 2 (convert 12 to editable): MEDIUM. Requires valid pyproject.toml structure for editable installs. If any format's pyproject.toml is missing or malformed, that format needs manual PTH file creation instead.
- Phase 3 (ghost files): ZERO if Phase 1 completes for those formats.
- Phase 6 (CSV rename): HIGH. Every import `from csv.csv_parser import ...` in tests and examples needs updating (grep shows ~50+ occurrences).

### Likely limits
- Even with editable installs, the sprint loop doesn't call `consumer_proof_runner.py` unless Phase 4 adds it to autonomous-cycle. Consumer proof evidence remains uncaptured until Phase 4.
- CSV namespace collision cannot be fixed without Phase 6 — and Phase 6 requires a decision on rename vs. disclosure.
- The test suite tests source, not wheel artifacts. Even after all phases, we have no CI that builds a wheel from scratch and verifies it installs and imports correctly in a clean Python environment.

### Rejected alternatives
- **Keep stale copies, add explicit sync step:** Too fragile. Each sprint needs to identify which formats changed and sync them. High maintenance.
- **Remove conftest src/python insertion:** Would make all tests depend on installed packages. Breaks during development before reinstall. Wrong direction.
- **Mark consumer proof as "source-verified" in README:** Correct honesty but doesn't fix the underlying problem. Pushes the problem onto README readers.

---

## Final Assessment

**PRODUCTION_HARDENING_REQUIRED**

The source libraries are production-grade. The problem is entirely in the packaging management layer. Three structural failures must be addressed:

1. **Stale installed packages**: 62 files diverged. Consumer proofs test different code than the test suite. Ghost files from deleted modules remain importable. Fix: editable installs for all formats.

2. **No synchronization gate**: The sprint lifecycle has no step that synchronizes source with installed packages. Fix: add V102 governance validator + consumer_proof_runner.py to sprint closeout.

3. **CSV namespace collision**: `import csv` never reaches the FF CSV package without workarounds that normal consumers won't know to apply. Fix: rename or explicitly document. This is the only issue requiring a user decision (rename vs. disclosure).

Phases 1-4 can be executed without a user decision. Phase 6 (CSV) requires one. All phases are targeted at the packaging infrastructure — not the source libraries, not the tests.

---

## Taskcard Status Summary

| TC-ID | Status |
|-------|--------|
| TC-CPR-001 | CLOSED |
| TC-CPR-002 | CLOSED |
| TC-CPR-003 | CLOSED |
| TC-CPR-004 | CLOSED |
| TC-CPR-005 | CLOSED |
| TC-CPR-006 | CLOSED |
| TC-CPR-007 | CLOSED |
| TC-CPR-008 | CLOSED |

## Taskcard Status Table

| TC-ID      | Description                                                              | Status  |
|------------|--------------------------------------------------------------------------|---------|
| TC-CPR-001 | Delete stale module dirs for 8 editable-PTH formats; verify editable install activates | CLOSED |
| TC-CPR-002 | Convert 12 remaining formats to editable installs (PTH or pip install -e) | CLOSED |
| TC-CPR-003 | Add V137-V138 governance validators: ghost file detection + stale file detection + evidence existence | CLOSED |
| TC-CPR-004 | Create tools/consumer_proof_runner.py: run all 20 scripts, capture stdout evidence | CLOSED |
| TC-CPR-005 | Add consumer_proof_runner.py call to sprint closeout in autonomous_cycle.py (best-effort) | CLOSED |
| TC-CPR-006 | Update obligation register evidence_paths to captured stdout files | CLOSED |
| TC-CPR-007 | Fix "installed_workflow" test naming; rename to workflow tests | CLOSED |
| TC-CPR-008 | CSV namespace: README disclosure added (option B — no rename) | CLOSED |


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-04T13:17:57.104204+00:00"
  locked_by: "6ccb0fc24c11"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
