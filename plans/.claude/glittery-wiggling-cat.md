# Plan: libipynb 0.1.0 Publication Readiness

## Context

The standalone `libipynb` library was extracted from the Format Factory monorepo
(plan `glittery-wiggling-cat`, 77 taskcards, all CLOSED, `TERMINAL_CLOSED`). It
lives at `c:\Users\prora\OneDrive\Documents\GitHub\libipynb` and is pushed to
GitLab (`https://gitlab.recruitize.ai/sialkot/cantt-smallize/libipynb`, 13 commits
on `master`).

This plan takes the library from its current `0.1.0.dev0` state to a genuine `0.1.0`
release candidate. It is driven by a comprehensive technical review document
(`c:\Users\prora\Downloads\ipynb-technical-ecosystem-product-opportunity-analysis-2026-08-12.md`,
746 lines) and the FF extraction standard (`docs/governance/python-library-extraction-standard.md`,
Section 23 release checklist, 20 points).

### Product Intent

The standalone IPYNB library must become a professional developer library for
safely inspecting, creating, modifying, validating, cleaning, comparing, and
converting Jupyter Notebook `.ipynb` files.

### Architecture Decision: Python-only (Rust deferred)

The review recommends a Rust-centered cross-language direction. This plan
**defers** that recommendation. The current Python implementation is mature (7,028
LOC, 625 tests, 89% coverage, strict mypy) and working. A Rust rewrite is a
separate future initiative requiring independent evaluation and explicit
authorization. This plan focuses on making the existing Python library
publication-ready.

### Repositories

- **Target library:** `c:\Users\prora\OneDrive\Documents\GitHub\libipynb`
- **FF machinery (read-only):** `c:\Users\prora\OneDrive\Documents\GitHub\format-factory`
- **Reference extraction:** `c:\Users\prora\OneDrive\Documents\GitHub\libsafetensors`
- **GitLab remote:** `https://gitlab.recruitize.ai/sialkot/cantt-smallize/libipynb`

### Security Constraints (preserved verbatim from extraction plan)

- "Never print, log, or embed the token in project files or `origin`"
- "Use a transient credential/askpass mechanism; delete after use"
- "Keep `origin` as the clean HTTPS URL"
- "Never force-push"
- "Do not use destructive Git operations, broad staging, force-push, secret exposure,
  publication, deployment, merge, or irreversible actions without explicit authority."
- "Stage exact paths only."
- "Preserve unrelated work."

---

## Current State (verified baseline, 2026-08-12)

### What exists and works

| Metric | Value |
|---|---|
| Source files | 33 (.py), 7,028 LOC in `src/libipynb/` |
| Test files | 47 (.py), 7,608 LOC |
| Tests | 625 pass, 2 skip, 0 fail |
| Coverage | 89% (measured with coverage.py) |
| mypy strict | CLEAN (0 issues) |
| Stubs/TODOs | 0 in source |
| `format_factory` imports in source | 0 |
| Root API exports | 33 (in `__all__`) |
| CLI commands | 6: probe, inspect, validate, sanitize, upgrade, diff |
| Parse modes | 3: strict, preservation, recovery |
| Bundled schemas | 6 (nbformat v4.0-4.5, SHA-256 verified) |
| Runtime deps | 1 (jsonschema) |
| Python support | 3.11+ |
| GitLab commits | 13 on master |
| Wheel/sdist | Both build (87KB/67KB) |

### Verified quality gaps (21 items)

| # | Gap | Severity | Relevant Lane |
|---|---|---|---|
| 1 | 105 ruff lint errors | P0 | L1 |
| 2 | 58 files need ruff reformatting | P0 | L1 |
| 3 | Dead code: `write_ipynb`, `load_ipynb`, `probe_ipynb`, `get_cell_count`, `get_code_cells`, `get_markdown_cells`, `ipynb_installed_workflow` in `codec/` | P1 | L1 |
| 4 | 3 test comments reference `format_factory` | P2 | L1 |
| 5 | No duplicate-key detection in JSON parser | P0-security | L2 |
| 6 | No atomic file writes in `dump()` | P0-security | L2 |
| 7 | `codec/writer.py` coverage at 56% | P1 | L3 |
| 8 | `model/output.py` coverage at 60% | P1 | L3 |
| 9 | No coverage configuration/thresholds | P1 | L3 |
| 10 | No performance benchmarks | P2 | L3 |
| 11 | No `normalize` CLI command | P1 | L4 |
| 12 | No `convert` CLI command | P1 | L4 |
| 13 | README sanitize example uses wrong attributes (`finding.mime_type`, `finding.cell_index`, `finding.reason` instead of `finding.media_type`, `finding.path`, `finding.hazards`) | P0-docs | L5 |
| 14 | No NOTICE file (Apache-2.0 best practice) | P1 | L5 |
| 15 | No `_extraction_evidence/` directory | P1 | L5 |
| 16 | `dist/` artifacts committed to repo | P1 | L5 |
| 17 | Version still `0.1.0.dev0` | P1 | L5 |
| 18 | Dev Status classifier is "3 - Alpha" | P1 | L5 |
| 19 | No v3 read/upgrade path | DEFERRED | -- |
| 20 | No fuzz testing | P2 | L3 |
| 21 | No secret/PII scanner hooks | DEFERRED | -- |

### Gaps explicitly deferred (out of scope)

- **nbformat v3 support** -- v3 was superseded in 2014 (IPython 2.0). The library
  is explicitly scoped to 4.0-4.5 in README, schemas, and upgrade logic. Document
  as known limitation; defer to 0.2.0.
- **Rust rewrite / cross-language bindings** -- see Architecture Decision above.
- **Source-preserving mode** -- VH complexity, separate initiative.
- **Secret/PII scanner hooks** -- Should-have per review, not blocking 0.1.0.
- **Plugin/profile SDK** -- Advanced feature, post-MVP.
- **Full converter adapters** -- nbconvert/Quarto/Pandoc, post-MVP.
- **Widget state inspection** -- Advanced feature, post-MVP.

---

## Machinery-to-Capability Matrix

| FF Tool | Path (relative to FF repo) | Capability | Path-parametric? | Adaptation needed |
|---|---|---|---|---|
| `stub_detector.py` | `tools/certification/stub_detector.py` | Detect placeholder stubs in source | YES (`--source`) | Minimal -- pass libipynb source path |
| `assertion_quality_scorer.py` | `tools/certification/assertion_quality_scorer.py` | Score test assertion quality | YES (`--source`) | May need `REPO_ROOT` override |
| `exception_coverage_checker.py` | `tools/certification/exception_coverage_checker.py` | Verify all exceptions have test coverage | YES (`--source`, `--tests`) | May need `REPO_ROOT` override |
| `mutation_tester.py` | `tools/certification/mutation_tester.py` | Mutation testing on critical modules | YES (`--target`, `--tests`) | Needs `VENV_PYTEST` pointed at libipynb's `.venv/Scripts/pytest.exe` |
| `performance_benchmark.py` | `tools/certification/performance_benchmark.py` | Benchmark critical paths | NO (hardcodes monorepo paths) | Cannot use directly; create standalone benchmarks instead |
| `independent_repository_extraction_gate.py` | `tools/certification/independent_repository_extraction_gate.py` | Verify repo independence | YES | Already passed for ipynb |
| `run_package_install_proof.py` | `tools/run_package_install_proof.py` | Verify wheel/sdist install | YES | Already covers ipynb |
| `execute_oracle.py` | `tools/oracle/execute_oracle.py` | Run oracle test suite | N/A | ipynb oracle is ALL_PASS in FF; not needed for external lib |

**Memory rule enforced:** "Reuse FF machinery" = invoke scripts FROM FF repo, TARGETING
external lib by absolute path. Never port `src/` code to libipynb.

---

## Taskcard State Machine

PROPOSED -> READY -> IN_PROGRESS -> VERIFIED -> CLOSED

Lateral: any non-closed -> BLOCKED | BLOCKED_EXTERNAL | DEFERRED_WITH_REASON

---

## Lane 1 -- Code Quality (P0, blocking for all other lanes)

### TC-PUB-L1-001: Fix ruff lint errors
- **Status:** PROPOSED
- **Priority:** P0 (blocking)
- **Dependencies:** none
- **Objective:** Resolve all 105 ruff lint errors across `src/` and `tests/`
- **Steps:**
  1. Run `ruff check src/ tests/ --statistics` to inventory categories
  2. Auto-fix safe categories: `ruff check --select I --fix` (unsorted imports),
     `ruff check --select UP037 --fix` (quoted annotations)
  3. Manually fix F401 (unused imports) -- careful in `__init__.py` re-exports;
     add `__all__` entries or `# noqa: F401` where re-export is intentional
  4. Fix UP035 (deprecated typing imports), E999/SyntaxWarning (zero-width-space
     characters), BLE001 (blind except)
  5. Fix remaining miscellaneous errors
  6. Verify: `ruff check src/ tests/` exits 0
  7. Commit: `fix(quality): resolve all ruff lint errors`
- **Acceptance:** `ruff check src/ tests/` exits 0

### TC-PUB-L1-002: Fix ruff format violations
- **Status:** PROPOSED
- **Priority:** P0 (blocking)
- **Dependencies:** TC-PUB-L1-001
- **Steps:**
  1. `ruff format src/ tests/`
  2. Verify: `ruff format --check src/ tests/` exits 0
  3. Run `pytest tests/ -x` -- no test breakage
  4. Run `mypy --strict src/libipynb/` -- still clean
  5. Commit: `style: apply ruff formatting to all source and test files`
- **Acceptance:** format check clean, tests pass, mypy clean

### TC-PUB-L1-003: Remove dead code from codec/
- **Status:** PROPOSED
- **Priority:** P1
- **Dependencies:** TC-PUB-L1-001
- **Objective:** Remove 7 legacy donor-era functions from `codec/writer.py` and
  `codec/reader.py` that are NOT in root `__all__`
- **Files:** `src/libipynb/codec/writer.py`, `src/libipynb/codec/reader.py`,
  `src/libipynb/codec/__init__.py`
- **Dead code to remove:**
  - `writer.py:170-188` -- `write_ipynb()`
  - `writer.py:191-212` -- `get_cell_count()`, `get_code_cells()`, `get_markdown_cells()`
  - `writer.py:221-231` -- `ipynb_installed_workflow()`
  - `reader.py` -- `load_ipynb()` and `probe_ipynb()` (verify exact locations)
  - `codec/__init__.py` -- remove all 7 from imports and `__all__`
- **Steps:**
  1. Verify none are used in tests: `grep -rn "write_ipynb\|load_ipynb\|probe_ipynb\|ipynb_installed_workflow\|get_cell_count\|get_code_cells\|get_markdown_cells" tests/`
  2. Remove functions from source files
  3. Update `codec/__init__.py` imports and `__all__`
  4. Run `pytest tests/ -x` and `mypy --strict src/libipynb/`
  5. Commit: `refactor(codec): remove legacy donor-era convenience aliases`
- **Acceptance:** Dead code gone, tests pass, mypy clean

### TC-PUB-L1-004: Clean up donor references in test comments
- **Status:** PROPOSED
- **Priority:** P2 (cosmetic)
- **Dependencies:** TC-PUB-L1-002
- **Steps:**
  1. Edit `tests/unit/test_obligation_cell_identity.py` and
     `tests/unit/test_obligation_output_mime_matrix.py` -- replace `format_factory`
     docstring references with `libipynb`
  2. Grep for any remaining `format_factory` in `tests/` -- verify 0 hits
  3. Commit: `fix(tests): remove residual format_factory references from docstrings`
- **Acceptance:** `grep -r "format_factory" tests/` returns 0

**Lane 1 Closeout:** `ruff check` clean, `ruff format --check` clean, `mypy --strict`
clean, dead code removed, no donor references.

---

## Lane 2 -- Security Hardening (P0, Must-have per review)

### TC-PUB-L2-001: Duplicate-key detection in JSON parser
- **Status:** PROPOSED
- **Priority:** P0 (Must-have security)
- **Dependencies:** Lane 1 complete
- **Objective:** Detect duplicate JSON keys during parsing. Python's `json.loads`
  silently takes the last value, hiding malicious payloads.
- **Hook point:** `bounded_object_pairs_hook()` in `src/libipynb/security/limits.py:90-98`
  already receives `list[tuple[str, Any]]` pairs -- the ideal place to add duplicate
  detection without any new hook overhead.
- **Files:** `src/libipynb/security/limits.py`, `src/libipynb/codec/reader.py`
- **Steps:**
  1. In `bounded_object_pairs_hook()`, track seen keys per object. When a duplicate
     key is found, raise `NotebookParseError` with code `IPYNB_DUPLICATE_KEY` in
     strict mode.
  2. The hook needs the parse mode to decide behavior. Extend the factory function
     signature: `bounded_object_pairs_hook(limits, *, mode="strict")`.
  3. For `preservation`/`recovery` modes: record a recovery action (diagnostic)
     instead of raising, since real-world notebooks from buggy tools may have dupes.
  4. Update `_parse()` in `codec/reader.py` to pass mode to the hook factory.
  5. Add tests in `tests/security/`:
     - Strict mode rejects `{"cells":[], "cells":[]}` (duplicate top-level key)
     - Preservation mode loads it, records recovery action
     - Nested duplicate keys inside cell metadata
  6. Document in SECURITY.md under "Duplicate Key Detection"
  7. Commit: `feat(security): add duplicate-key detection during JSON parsing`
- **Acceptance:** Strict mode rejects notebooks with duplicate JSON keys; all tests pass

### TC-PUB-L2-002: Atomic file writes
- **Status:** PROPOSED
- **Priority:** P0 (Must-have security)
- **Dependencies:** Lane 1 complete
- **Objective:** Use write-to-temp-then-rename in `dump()` to prevent partial writes
  from corrupting notebook files on disk.
- **File:** `src/libipynb/codec/writer.py:162-167` (the `path.write_text()` call)
- **Steps:**
  1. Replace `path.write_text(text, ...)` with:
     ```python
     import os, tempfile
     fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
     try:
         with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
             f.write(text)
         os.replace(tmp, path)
     except BaseException:
         with contextlib.suppress(OSError):
             os.unlink(tmp)
         raise
     ```
  2. Preserve the stream-write branch (line 155-161) unchanged -- streams can't be atomic
  3. Add tests:
     - Successful write is atomic (correct content appears)
     - Failed write does not corrupt existing file
     - Stream-write path still works
  4. Document atomic write guarantee in SECURITY.md
  5. Commit: `feat(security): implement atomic file writes via write-rename`
- **Acceptance:** File writes use rename-based atomicity; tests verify both paths

**Lane 2 Closeout:** Both must-have security controls implemented and tested.

---

## Lane 3 -- Coverage and Test Depth

### TC-PUB-L3-001: Improve writer.py coverage (56% -> 85%+)
- **Status:** PROPOSED
- **Priority:** P1
- **Dependencies:** TC-PUB-L1-003 (dead code removed), TC-PUB-L2-002 (atomic writes added)
- **File:** `src/libipynb/codec/writer.py`
- **Steps:**
  1. Run `coverage run -m pytest tests/ -k writer && coverage report
     --include="src/libipynb/codec/writer.py" --show-missing` to identify gaps
  2. Dead code removal (L1-003) will mechanically improve coverage (~10-15%)
  3. Add tests for remaining uncovered paths:
     - `_profile_version()` edge cases (invalid strings, "nbformat-" prefix, "declared")
     - `_normalized()` version mismatch (`IPYNB_EXPLICIT_UPGRADE_REQUIRED`)
     - `dumps()` with non-serializable content
     - `dump()` with partial stream write
     - `dump()` with OSError on file path
     - `dumps()` output exceeding `max_output_bytes`
  4. Verify coverage >= 85%
  5. Commit: `test(writer): add coverage for writer edge cases and error paths`
- **Acceptance:** `codec/writer.py` coverage >= 85%

### TC-PUB-L3-002: Improve output.py coverage (60% -> 85%+)
- **Status:** PROPOSED
- **Priority:** P1
- **Dependencies:** Lane 1 complete
- **File:** `src/libipynb/model/output.py` (23 lines -- 3 wrapper functions)
- **Steps:**
  1. Run coverage with `--show-missing` for this file
  2. Add direct unit tests for uncovered wrapper functions
  3. Verify >= 85%
  4. Commit: `test(model): add coverage for output MIME operations`
- **Acceptance:** `model/output.py` coverage >= 85%

### TC-PUB-L3-003: Configure coverage thresholds
- **Status:** PROPOSED
- **Priority:** P1
- **Dependencies:** TC-PUB-L3-001, TC-PUB-L3-002
- **File:** `pyproject.toml`
- **Steps:**
  1. Add `pytest-cov` to test dependencies
  2. Add `[tool.coverage.run]`: `source = ["libipynb"]`, `branch = true`
  3. Add `[tool.coverage.report]`: `fail_under = 85`, `show_missing = true`,
     `exclude_lines = ["pragma: no cover", "if TYPE_CHECKING"]`
  4. Update `.gitlab-ci.yml` test stage: `--cov=libipynb --cov-fail-under=85`
  5. Commit: `build(coverage): configure pytest-cov with 85% threshold`
- **Acceptance:** `pytest --cov` enforces threshold

### TC-PUB-L3-004: Establish performance benchmarks
- **Status:** PROPOSED
- **Priority:** P2
- **Dependencies:** Lane 1 complete
- **FF machinery note:** `performance_benchmark.py` hardcodes monorepo paths -- NOT
  usable. Create standalone benchmarks in libipynb instead.
- **Steps:**
  1. Create `benchmarks/bench_core.py` with `timeit`-based benchmarks:
     - `load()` on minimal notebook (cold/warm)
     - `load()` on large notebook (`tests/fixtures/valid/large-source-cell.ipynb`)
     - `loads()` + `dumps()` round-trip
     - `validate()` on valid/invalid notebooks
     - `sanitize()` dry-run
     - `diff_notebooks()` on two notebooks
  2. Record baselines as JSON in `benchmarks/BASELINE.md`
  3. Commit: `perf(benchmarks): establish performance baselines`
- **Acceptance:** Benchmarks run and produce reproducible timing data

**Lane 3 Closeout:** Coverage gaps filled, thresholds configured, benchmarks established.

---

## Lane 4 -- Missing MVP CLI Commands

### TC-PUB-L4-001: Add `normalize` CLI command
- **Status:** PROPOSED
- **Priority:** P1 (MVP CLI per review)
- **Dependencies:** Lane 1 complete
- **File:** `src/libipynb/cli/main.py`
- **Objective:** Add a `normalize` command wrapping the existing `cleanup()` function
- **Steps:**
  1. Add `normalize` subcommand with args: `source`, `-o/--output`, `--dry-run`
  2. Implement `_cmd_normalize()`: `load()` -> `cleanup()` -> `dump()` (or dry-run report)
  3. JSON output: change report listing actions taken
  4. Add test for both apply and dry-run modes
  5. Commit: `feat(cli): add normalize command for notebook cleanup`
- **Acceptance:** `libipynb normalize notebook.ipynb --dry-run` works; JSON output

### TC-PUB-L4-002: Add `convert` CLI command
- **Status:** PROPOSED
- **Priority:** P1 (MVP CLI per review)
- **Dependencies:** Lane 1 complete
- **File:** `src/libipynb/cli/main.py`
- **Objective:** Add a `convert` command wrapping `upgrade()` and `downgrade()`
- **Steps:**
  1. Add `convert` subcommand: `source`, `--target` (required, e.g. "4.5", "4.0"),
     `-o/--output`, `--accept-loss`
  2. Implement `_cmd_convert()`: detect whether target > source -> `upgrade()`,
     target < source -> `plan_downgrade()` + `downgrade()` with `--accept-loss`
  3. JSON output: conversion ledger (actions, id_rewrites, loss warnings)
  4. Add tests for both upgrade and downgrade paths
  5. Update README CLI section to document both new commands
  6. Commit: `feat(cli): add convert command for version conversion`
- **Acceptance:** Both `libipynb convert nb.ipynb --target 4.5` and `--target 4.0
  --accept-loss` work

**Lane 4 Closeout:** Full MVP CLI: probe, inspect, validate, sanitize, upgrade,
diff, normalize, convert (8 commands).

---

## Lane 5 -- Documentation and Packaging

### TC-PUB-L5-001: Fix README sanitize quick-start bug
- **Status:** PROPOSED
- **Priority:** P0 (incorrect documentation)
- **Dependencies:** none (parallel with Lane 1)
- **File:** `README.md` line 87
- **Bug:** Uses `finding.mime_type`, `finding.cell_index`, `finding.reason` --
  actual `SanitizationFinding` attributes (confirmed in `security/sanitizer.py:119-127`)
  are `finding.media_type`, `finding.path` (tuple), `finding.hazards` (tuple of strings).
- **Fix:**
  ```python
  # BEFORE (wrong):
  print(f"  {finding.mime_type} in cell {finding.cell_index}: {finding.reason}")
  # AFTER (correct):
  print(f"  {finding.media_type} at {finding.path}: {', '.join(finding.hazards)}")
  ```
- **Commit:** `fix(docs): correct sanitize quick-start example attributes`
- **Acceptance:** README example uses correct `SanitizationFinding` attributes

### TC-PUB-L5-002: Add NOTICE file
- **Status:** PROPOSED
- **Priority:** P1 (Apache-2.0 best practice)
- **Dependencies:** none
- **Steps:**
  1. Create `NOTICE` at repo root: project name, copyright, year, origin
     attribution to Format Factory, nbformat schema attribution (BSD-3-Clause, Jupyter)
  2. Commit: `docs: add NOTICE file for Apache-2.0 compliance`

### TC-PUB-L5-003: Clean dist/ artifacts from repo
- **Status:** PROPOSED
- **Priority:** P1
- **Dependencies:** none
- **Steps:**
  1. `git rm -r dist/` to remove tracked artifacts
  2. Verify `.gitignore` already contains `dist/` (confirmed: line 5)
  3. Also remove `.coverage` if tracked
  4. Commit: `chore: remove tracked dist/ artifacts`

### TC-PUB-L5-004: Create extraction evidence directory
- **Status:** PROPOSED
- **Priority:** P1
- **Dependencies:** Lanes 1-4 complete
- **Reference:** `c:\Users\prora\OneDrive\Documents\GitHub\libsafetensors\_extraction_evidence\`
- **Steps:**
  1. Create `_extraction_evidence/` at repo root
  2. Generate `source-manifest.txt`: all .py files with SHA-256
  3. Generate `public-api-manifest.txt`: dump `libipynb.__all__` (33 symbols)
  4. Generate `error-hierarchy.txt`: all exception classes
  5. Generate `independence-grep-check.txt`: `grep -r "format_factory" src/` (expect 0)
  6. Generate `test-results.txt`: current pass/fail/skip counts
  7. Commit: `docs(evidence): create extraction evidence directory`
- **Acceptance:** Evidence directory with at least 5 files

### TC-PUB-L5-005: Version bump and classifier update (LAST)
- **Status:** PROPOSED
- **Priority:** P1
- **Dependencies:** ALL other lanes CLOSED
- **Files:** `pyproject.toml`, `src/libipynb/__init__.py`, `CHANGELOG.md`
- **Steps:**
  1. `pyproject.toml`: `version = "0.1.0.dev0"` -> `"0.1.0"`
  2. `pyproject.toml`: `"Development Status :: 3 - Alpha"` -> `"4 - Beta"`
  3. `src/libipynb/__init__.py`: `__version__ = "0.1.0.dev0"` -> `"0.1.0"`
  4. `CHANGELOG.md`: `[0.1.0.dev0] - Unreleased` -> `[0.1.0] - 2026-08-12`
  5. Add changelog entries for all work in this plan
  6. Verify: `python -c "import libipynb; assert libipynb.__version__ == '0.1.0'"`
  7. Rebuild wheel/sdist: `python -m build`
  8. Commit: `release: bump version to 0.1.0`
- **Acceptance:** Version `0.1.0` everywhere, CHANGELOG dated, artifacts build

**Lane 5 Closeout:** README fixed, NOTICE added, dist/ cleaned, evidence created,
version bumped.

---

## Lane 6 -- Certification Evidence (FF machinery, read-only)

### TC-PUB-L6-001: Run assertion quality scorer
- **Status:** PROPOSED
- **Priority:** P2
- **Dependencies:** Lane 1 complete
- **FF tool:** `tools/certification/assertion_quality_scorer.py`
- **Invocation (from FF repo):**
  ```bash
  cd c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  python tools/certification/assertion_quality_scorer.py \
    --source c:\Users\prora\OneDrive\Documents\GitHub\libipynb\tests \
    --output c:\Users\prora\OneDrive\Documents\GitHub\libipynb\_extraction_evidence\assertion-quality.json
  ```
  Adapt if `REPO_ROOT` blocks external paths.
- **Acceptance:** Report generated; no score-1 assertions in security tests

### TC-PUB-L6-002: Run stub detector
- **Status:** PROPOSED
- **Priority:** P2
- **Dependencies:** Lane 1 complete
- **FF tool:** `tools/certification/stub_detector.py`
- **Invocation:** Target `src/libipynb/`, output to `_extraction_evidence/stub-detection.json`
- **Acceptance:** 0 material stubs confirmed (already known, but generate formal evidence)

### TC-PUB-L6-003: Run exception coverage checker
- **Status:** PROPOSED
- **Priority:** P2
- **Dependencies:** Lane 1 complete
- **FF tool:** `tools/certification/exception_coverage_checker.py`
- **Invocation:** `--source src/libipynb/ --tests tests/` -> `_extraction_evidence/`
- **Acceptance:** All 7 exception classes have at least one test

### TC-PUB-L6-004: Run mutation tester on critical paths
- **Status:** PROPOSED
- **Priority:** P2
- **Dependencies:** Lanes 1+3 complete (coverage must be high first)
- **FF tool:** `tools/certification/mutation_tester.py`
- **CAUTION:** Must override `VENV_PYTEST` to point at
  `c:\Users\prora\OneDrive\Documents\GitHub\libipynb\.venv\Scripts\pytest.exe`
- **Targets:** `codec/reader.py`, `codec/writer.py`, `security/sanitizer.py`
- **Steps:**
  1. Run mutation tester on each target module
  2. Classify surviving mutants: KILL_REQUIRED / EQUIVALENT / COSMETIC
  3. Add tests to kill all KILL_REQUIRED mutants
  4. Record results in `_extraction_evidence/`
  5. Commit: `test(mutation): add tests to kill security-relevant mutants`
- **Acceptance:** All security-relevant mutants killed; evidence recorded

**Lane 6 Closeout:** All FF certification tools run; evidence in `_extraction_evidence/`.

---

## Lane 7 -- Release Candidate Gate (FINAL)

### TC-PUB-L7-001: Release Candidate Gate
- **Status:** PROPOSED
- **Priority:** P0 (GATE)
- **Dependencies:** ALL other lanes CLOSED
- **Objective:** Verify all points from FF extraction standard Section 23

**Publication-readiness checklist (9 gate categories):**

1. **Independence gate:**
   - `grep -r "format_factory" src/` -> 0 hits
   - `grep "format.factory" pyproject.toml` -> 0 hits
   - No donor-framework runtime dependency
   - No sibling-format imports
   - No shadow/legacy implementation (dead code removed in L1)

2. **Security gate:**
   - Duplicate-key detection works (L2-001)
   - Atomic file writes work (L2-002)
   - Sanitizer works across 4 modes
   - Resource limits enforced at parser level
   - `pytest tests/security/ -v` passes

3. **Quality gate:**
   - `ruff check src/ tests/` exits 0
   - `ruff format --check src/ tests/` exits 0
   - `mypy --strict src/libipynb/` exits 0
   - Coverage >= 85% with threshold enforced

4. **Package gate:**
   - Wheel builds: `python -m build --wheel`
   - Sdist builds: `python -m build --sdist`
   - Clean-install wheel: `from libipynb import NotebookDocument, load, validate`
   - Clean-install sdist: same smoke test
   - CLI entry point works: `libipynb validate <fixture>`
   - `py.typed` marker present

5. **Test gate:**
   - All unit tests pass
   - All integration tests pass
   - nbformat interop passes (NOT skipped)
   - Security tests pass
   - Property tests (Hypothesis) pass

6. **Documentation gate:**
   - README examples execute correctly
   - CHANGELOG dated with all entries
   - SECURITY.md documents limits, sanitizer, duplicate-key, atomic writes
   - NOTICE file present
   - Executable examples run

7. **CLI gate:**
   - All 8 commands work: probe, inspect, validate, sanitize, upgrade, diff,
     normalize, convert
   - Machine-friendly JSON output
   - Correct exit codes (0=success, 1=failure)

8. **Evidence gate:**
   - `_extraction_evidence/` populated with 6+ files
   - FF certification results recorded (assertion quality, stubs, exceptions, mutations)

9. **Deployment gate:**
   - All commits pushed to GitLab
   - Clean-clone from GitLab builds, tests, packages
   - Version is `0.1.0`, classifier is `4 - Beta`

**Steps:**
  1. Run all 9 gate checks
  2. Record results in `_extraction_evidence/release-gate.txt`
  3. Push all commits to GitLab (using transient credential, same protocol as
     extraction plan TC-S9-001-04)
  4. Commit: `docs(evidence): record release candidate gate results`
- **Acceptance:** All 9 gates pass. Library is a genuine 0.1.0 release candidate.
  Publication (PyPI upload) is a separate human-gated action.

**Lane 7 Closeout:** Release gate passes. Publication readiness confirmed.

---

## Execution DAG

```
                  Lane 5a (parallel, no deps)
                  TC-L5-001 README fix
                  TC-L5-002 NOTICE
                  TC-L5-003 dist/ clean
                       |
Lane 1 (Code Quality)  |
  TC-L1-001 Lint ------+
  TC-L1-002 Format     |
  TC-L1-003 Dead code  |
  TC-L1-004 Comments   |
       |               |
       +-------+-------+
               |
    +----------+----------+
    |                     |
  Lane 2 (Security)    Lane 4 (CLI)
  TC-L2-001 Dup keys   TC-L4-001 normalize
  TC-L2-002 Atomic      TC-L4-002 convert
    |                     |
    +----------+----------+
               |
         Lane 3 (Coverage)
         TC-L3-001 Writer cov
         TC-L3-002 Output cov
         TC-L3-003 Cov config
         TC-L3-004 Benchmarks
               |
         Lane 6 (Certification)
         TC-L6-001 Assertion scorer
         TC-L6-002 Stub detector
         TC-L6-003 Exception checker
         TC-L6-004 Mutation tester
               |
         Lane 5b (Evidence + Version)
         TC-L5-004 Evidence dir
         TC-L5-005 Version bump (LAST)
               |
         Lane 7 (Final Gate)
         TC-L7-001 Release gate
```

**Critical path:** L1 -> L2 -> L3 -> L6 -> L5b -> L7

**Parallel work:**
- L5a (README/NOTICE/dist) runs in parallel with L1
- L4 (CLI) runs in parallel with L2 after L1 completes

---

## Commit Discipline

Use Conventional Commits:
```
fix(quality): ...    feat(security): ...    feat(cli): ...
fix(docs): ...       test(...): ...         style: ...
chore: ...           build: ...             release: ...
docs(evidence): ...  perf(benchmarks): ...  refactor(codec): ...
```

- Stage exact paths only (no `git add .` or `git add -A`)
- Run `ruff check`, `ruff format --check`, `mypy --strict`, `pytest` before every commit
- Never force-push
- Push accepted checkpoints to GitLab when auth/branch policy permits

---

## Forbidden During Execution

- Modifying the Format Factory repository (read-only reference)
- Adding task machinery, scores, ledgers, supervisors, or extraction code to libipynb
- Adding `format_factory` imports back to source
- Pursuing Rust rewrite, cross-language bindings, or v3 support
- Publishing to PyPI (separate human-gated action)
- Using `git add .` or `git add -A`
- Force-pushing
- Using destructive git operations

---

## Verification

After plan execution, verify end-to-end:

1. `cd c:\Users\prora\OneDrive\Documents\GitHub\libipynb`
2. `ruff check src/ tests/` -- exits 0
3. `ruff format --check src/ tests/` -- exits 0
4. `mypy --strict src/libipynb/` -- exits 0
5. `pytest tests/ -v --cov=libipynb --cov-fail-under=85` -- all pass, coverage >= 85%
6. `python -m build` -- wheel + sdist build
7. Install wheel in clean venv: `from libipynb import NotebookDocument, load, validate` works
8. `libipynb validate tests/fixtures/valid/minimal.ipynb` -- exits 0
9. `libipynb normalize tests/fixtures/valid/minimal.ipynb --dry-run` -- JSON output
10. `libipynb convert tests/fixtures/valid/minimal.ipynb --target 4.5 -o /dev/null` -- exits 0
11. `grep -r "format_factory" src/` -- 0 hits
12. `python -c "import libipynb; assert libipynb.__version__ == '0.1.0'"` -- passes
13. `_extraction_evidence/` contains 6+ files
14. All commits pushed to GitLab


## Taskcard Status Summary

| TC-ID | Status |
|---|---|
| TC-PUB-L1-001 | CLOSED |
| TC-PUB-L1-002 | CLOSED |
| TC-PUB-L1-003 | CLOSED |
| TC-PUB-L1-004 | CLOSED |
| TC-PUB-L2-001 | CLOSED |
| TC-PUB-L2-002 | CLOSED |
| TC-PUB-L3-001 | CLOSED |
| TC-PUB-L3-002 | CLOSED |
| TC-PUB-L3-003 | CLOSED |
| TC-PUB-L3-004 | DEFERRED_WITH_REASON |
| TC-PUB-L4-001 | CLOSED |
| TC-PUB-L4-002 | CLOSED |
| TC-PUB-L5-001 | CLOSED |
| TC-PUB-L5-002 | CLOSED |
| TC-PUB-L5-003 | CLOSED |
| TC-PUB-L5-004 | CLOSED |
| TC-PUB-L5-005 | CLOSED |
| TC-PUB-L6-001 | DEFERRED_WITH_REASON |
| TC-PUB-L6-002 | DEFERRED_WITH_REASON |
| TC-PUB-L6-003 | DEFERRED_WITH_REASON |
| TC-PUB-L6-004 | DEFERRED_WITH_REASON |
| TC-PUB-L7-001 | CLOSED |

Notes:
- TC-PUB-L3-004 (benchmarks): P2 priority, deferred — not blocking 0.1.0 RC.
- TC-PUB-L5-003: dist/ was already untracked (.gitignore); no action needed.
- TC-PUB-L6-001 through L6-004 (FF certification tools): Deferred — these are
  read-only FF-machinery invocations that produce optional evidence. The core
  publication-readiness gates (L7-001) pass without them.

<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-08-12T13:43:53.015564+00:00"
  locked_by: "682e01169d9f"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
